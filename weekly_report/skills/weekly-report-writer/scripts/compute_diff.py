"""Compute cross-week diff between two manifests.

Output schema mirrors spec §7. Pure function, no I/O.
"""
from __future__ import annotations
import re

_VER_KEY_RE = re.compile(r"v(\d+)([a-z]?)", re.IGNORECASE)


def _version_sort_key(v: str) -> tuple[int, str]:
    m = _VER_KEY_RE.fullmatch(v) if v else None
    if not m:
        return (0, v or "")
    return (int(m.group(1)), m.group(2).lower())


def _index(files: list[dict]) -> dict[str, dict]:
    return {f["path"]: f for f in files}


def _diff_bucket(last_files, this_files):
    last_by = _index(last_files)
    this_by = _index(this_files)
    added = sorted(set(this_by) - set(last_by))
    deleted = sorted(set(last_by) - set(this_by))
    modified = []
    for p in sorted(set(last_by) & set(this_by)):
        last = last_by[p]
        this = this_by[p]
        if last.get("sha1") and this.get("sha1"):
            if last["sha1"] != this["sha1"]:
                modified.append(p)
        elif last.get("mtime") != this.get("mtime") or last.get("size") != this.get("size"):
            modified.append(p)
    return added, modified, deleted


def _diff_version_chains(last_chains: dict, this_chains: dict) -> list[dict]:
    out = []
    for fam, this_ch in this_chains.items():
        last_ch = last_chains.get(fam)
        last_versions = list(last_ch["versions"]) if last_ch else []
        this_versions = list(this_ch["versions"])
        last_max = max(last_versions, key=_version_sort_key) if last_versions else None
        this_max = max(this_versions, key=_version_sort_key)
        if last_max != this_max:
            out.append({
                "family": fam,
                "from": last_max,
                "to": this_max,
                "diff_summary": "",
            })
    # Detect deleted families
    for fam in last_chains:
        if fam not in this_chains:
            out.append({
                "family": fam,
                "from": max(last_chains[fam]["versions"], key=_version_sort_key),
                "to": None,
                "diff_summary": "family removed",
            })
    return out


def compute_diff(last_manifest: dict, this_manifest: dict) -> dict:
    out = {
        "this_week": this_manifest.get("week_id", "this"),
        "last_week": last_manifest.get("week_id", "last"),
    }
    last_b = last_manifest["buckets"]
    this_b = this_manifest["buckets"]

    # Code bucket has special treatment (version chains)
    added, modified, deleted = _diff_bucket(
        last_b["code"]["files"], this_b["code"]["files"])
    chain_advanced = _diff_version_chains(
        last_b["code"].get("version_chains", {}),
        this_b["code"].get("version_chains", {}),
    )
    out["code"] = {
        "version_chains_advanced": chain_advanced,
        "added_loose_files": added,
        "non_versioned_modified": modified,
        "deleted_files": deleted,
    }

    # Other buckets — generic diff
    for bk in ("experiment_data", "paper", "reading", "theory", "figures",
               "checkpoint_signal", "uncategorized"):
        last_files = last_b.get(bk, {}).get("files", [])
        this_files = this_b.get(bk, {}).get("files", [])
        a, m, d = _diff_bucket(last_files, this_files)
        out[bk] = {"added": a, "modified": m, "deleted": d}

    return out
