"""ThreadPool-based project scanner producing a manifest.json structure.

Spec: §6 Scanner. Single-source-of-truth for what a "weekly snapshot" contains.
Concurrency: ThreadPool over distinct bucket roots (max_workers configurable).
"""
from __future__ import annotations
import datetime as _dt
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from scripts.bucket_classifier import BUCKETS, BucketClassifier
from scripts.file_metadata import FileRecord, inspect_file
from scripts.ignore_rules import IgnoreMatcher
from scripts.parse_filename import parse_filename

SCANNER_VERSION = "1.0"

# Natural sort key for version strings like "v25", "v5b", "v100".
_VER_KEY_RE = re.compile(r"v(\d+)([a-z]?)", re.IGNORECASE)


def _version_sort_key(v: str) -> tuple[int, str]:
    m = _VER_KEY_RE.fullmatch(v) if v else None
    if not m:
        return (0, v or "")
    return (int(m.group(1)), m.group(2).lower())


@dataclass
class ScanConfig:
    project_root: Path
    buckets: Mapping[str, Mapping]
    global_ignores: Sequence[str]
    project_ignores: Sequence[str]
    metadata_only_size_mb: int = 10
    max_workers: int = 8


def _walk_root(root_abs: Path, ignore: IgnoreMatcher, project_root: Path):
    """Yield (rel_path_str, abs_path) for each non-ignored file under root_abs."""
    for sub in root_abs.rglob("*"):
        if sub.is_dir():
            continue
        if ignore.is_symlink(sub):
            continue
        try:
            rel = sub.relative_to(project_root)
        except ValueError:
            continue
        rel_s = str(rel).replace("\\", "/")
        if ignore.is_ignored(Path(rel_s)):
            continue
        yield rel_s, sub


def scan_project(cfg: ScanConfig) -> dict:
    classifier = BucketClassifier(cfg.buckets)
    ignore = IgnoreMatcher(
        global_globs=list(cfg.global_ignores),
        project_globs=list(cfg.project_ignores),
        skip_symlinks=True,
    )

    # Distinct root abs paths to walk in parallel.
    # Patterns containing "**" or empty fall back to walking project_root.
    roots: set[Path] = set()
    for cfg_b in cfg.buckets.values():
        for r in cfg_b.get("roots", []):
            if not r or "**" in r:
                roots.add(cfg.project_root)
            else:
                p = cfg.project_root / r
                if p.exists():
                    roots.add(p)
    if not roots:
        roots = {cfg.project_root}

    files_by_bucket: dict[str, list[FileRecord]] = {b: [] for b in BUCKETS}
    anomalies: list[str] = []

    def _process_root(root_abs: Path):
        local: dict[str, list[FileRecord]] = {b: [] for b in BUCKETS}
        local_anomalies: list[str] = []
        for rel_s, abs_p in _walk_root(root_abs, ignore, cfg.project_root):
            bucket = classifier.classify(rel_s)
            rec = inspect_file(abs_p, cfg.metadata_only_size_mb, rel_path=rel_s)
            if rec is None:
                continue
            local[bucket].append(rec)
            if bucket == "code":
                p = parse_filename(abs_p.stem)
                if p.is_anomaly:
                    local_anomalies.append(f"{rel_s}: {','.join(p.anomaly_reasons)}")
        return local, local_anomalies

    with ThreadPoolExecutor(max_workers=cfg.max_workers) as ex:
        for local, local_anom in ex.map(_process_root, sorted(roots)):
            for b, recs in local.items():
                files_by_bucket[b].extend(recs)
            anomalies.extend(local_anom)

    # De-duplicate (a file under nested roots could be visited twice)
    seen: set[str] = set()
    for b in files_by_bucket:
        unique = []
        for r in files_by_bucket[b]:
            if r.path in seen:
                continue
            seen.add(r.path)
            unique.append(r)
        files_by_bucket[b] = unique

    # Build version_chains for code bucket.
    # Track all (version, path) per family, then pick latest_path deterministically
    # by max(version) using natural sort key — independent of filesystem traversal order.
    chain_entries: dict[str, dict[str, str]] = {}     # family -> {version: path}
    for r in files_by_bucket["code"]:
        stem = Path(r.path).stem
        p = parse_filename(stem)
        if p.version is None:
            continue
        chain_entries.setdefault(p.family_key, {})[p.version] = r.path

    version_chains: dict[str, dict] = {}
    for family, ver_to_path in chain_entries.items():
        sorted_versions = sorted(ver_to_path.keys(), key=_version_sort_key)
        latest_version = sorted_versions[-1]
        version_chains[family] = {
            "versions": sorted_versions,
            "latest_path": ver_to_path[latest_version],
        }

    manifest = {
        "schema_version": "2.0",
        "scanner_version": SCANNER_VERSION,
        "scanned_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "project_root": str(cfg.project_root),
        "project_name": Path(cfg.project_root).name,
        "buckets": {
            b: {
                "files": [r.__dict__ for r in files_by_bucket[b]],
                **({"version_chains": version_chains} if b == "code" else {}),
            }
            for b in BUCKETS
        },
        "anomalies": sorted(set(anomalies)),
    }
    return manifest
