# Weekly-Report-Writer Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个面向博士生的全自动周报生成 skill，扫描工程目录、对比上周快照、半自动归并版本链与指标、L3 质询补语义、输出 PhD 风格周报 markdown。

**Architecture:** 4 层流水线（Scanner → Differ → Interview → Writer）+ per-project 配置 + 多 bucket（code/data/paper/reading/theory/figures/checkpoint_signal）+ 增量学习的 metric_vocab。Scanner/Differ/Metric 用确定性 Python 脚本，ThreadPool 并发；Interview/Writer 用 LLM + 模板。

**Tech Stack:** Python 3.10+ 标准库（pathlib / hashlib / re / json / tomllib / concurrent.futures）+ markdown 输出 + 可选 imagehash（pHash 配图去重）。无外部服务依赖。

**Spec:** [docs/superpowers/specs/2026-05-04-weekly-report-writer-design.md](../specs/2026-05-04-weekly-report-writer-design.md)

**Repo State:** `D:\code\github_skill\weekly_report\` 不在 git 仓库下。Plan 中 commit 步骤以"可选"标注，建议先 `git init` 再开始。

**Test Project:** `D:\code\radar_target_recognition`（45GB / 331 .py / 71315 数据文件 / 4 论文 doc）作为 e2e 测试目标。**RED LINE：测试过程禁止任何写操作落到该目录之外（仅允许写到 `<project>/.weekly_report/` 与 `D:\code\reports\`）**。

---

## Phase 0: Repo Setup

### Task 0: Git init + baseline commit (optional)

**Files:**
- Create: `D:\code\github_skill\.git` (via init)
- Create: `D:\code\github_skill\.gitignore`

- [ ] **Step 1: Init repo and add gitignore**

```bash
cd D:/code/github_skill
git init
cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
.coverage
htmlcov/
*.swp
.DS_Store
EOF
```

- [ ] **Step 2: Initial commit**

```bash
git add weekly_report/SKILL.md weekly_report/docs/ weekly_report/references/ weekly_report/assets/ .gitignore
git commit -m "chore: import existing weekly_report skill draft + design spec"
```

---

## Phase 1: Foundation — Filename Parser & Path Guard

### Task 1: Set up package layout for scripts

**Files:**
- Create: `weekly_report/scripts/__init__.py`
- Create: `weekly_report/scripts/tests/__init__.py`
- Create: `weekly_report/scripts/tests/conftest.py`

- [ ] **Step 1: Create empty __init__.py files**

Create empty file `weekly_report/scripts/__init__.py`.
Create empty file `weekly_report/scripts/tests/__init__.py`.

- [ ] **Step 2: Create conftest.py with shared fixtures**

```python
# weekly_report/scripts/tests/conftest.py
"""Shared pytest fixtures for weekly_report scripts tests."""
import json
import shutil
from pathlib import Path
import pytest


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """A throwaway project root with realistic shape."""
    root = tmp_path / "fake_project"
    (root / "Forecasting").mkdir(parents=True)
    (root / "Forecasting" / "output").mkdir()
    (root / "Forecasting" / "checkpoint").mkdir()
    (root / "paper_writing").mkdir()
    (root / "research-wiki").mkdir()
    (root / "raw_data").mkdir()
    return root


@pytest.fixture
def tmp_weekly_report_dir(tmp_project: Path) -> Path:
    """The .weekly_report state dir inside fake_project."""
    d = tmp_project / ".weekly_report"
    d.mkdir()
    return d
```

- [ ] **Step 3: Verify pytest can collect**

```bash
cd D:/code/github_skill/weekly_report
python -m pytest scripts/tests -v --collect-only
```

Expected: pytest reports 0 tests collected, no import errors.

- [ ] **Step 4: Commit (optional)**

```bash
git add weekly_report/scripts/
git commit -m "test: scaffold scripts package + shared fixtures"
```

---

### Task 2: parse_filename — version chain heuristic

**Spec ref:** §7 Differ 规则 / 版本链识别启发式

**Files:**
- Create: `weekly_report/scripts/parse_filename.py`
- Create: `weekly_report/scripts/tests/test_parse_filename.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_parse_filename.py
"""Tests for parse_filename heuristic."""
import pytest
from scripts.parse_filename import parse_filename, ParsedName


@pytest.mark.parametrize("stem,family,version,status", [
    ("rcs_stacking_v26",        "rcs_stacking",         "v26", None),
    ("rcs_fusion_v25",          "rcs_fusion",           "v25", None),
    ("train_v17_contrastive",   "train_contrastive",    "v17", None),
    ("train_v17_fixed",         "train",                "v17", "fixed"),
    ("train_v19_mstcn_contrastive", "train_mstcn_contrastive", "v19", None),
    ("adaptive_fusion_v5b",     "adaptive_fusion",      "v5b", None),
    ("data_loader_complex_v2",  "data_loader_complex",  "v2",  None),
    ("data_loader_new",         "data_loader",          None,  "new"),
    ("inference_v20_v2",        "inference",            "v20", None),  # _v2 as semantic
    ("compare_v17_v19",         "compare",              "v17", None),  # comparison script
    ("plain_module",            "plain_module",         None,  None),
])
def test_parse_filename_basic(stem, family, version, status):
    result = parse_filename(stem)
    assert result.family_key == family
    assert result.version == version
    assert result.status == status


def test_parse_filename_double_final_anomaly():
    """Final_inference_final.py → flagged as anomaly."""
    result = parse_filename("Final_inference_final")
    assert result.is_anomaly
    assert "double_status_marker" in result.anomaly_reasons


def test_parse_filename_v20v2_typo():
    """analyze_errors_v20v2 → flagged as suspected typo."""
    result = parse_filename("analyze_errors_v20v2")
    assert result.is_anomaly
    assert "suspected_version_typo" in result.anomaly_reasons


def test_parse_filename_returns_dataclass():
    """Return type must be ParsedName dataclass for downstream use."""
    result = parse_filename("rcs_stacking_v26")
    assert isinstance(result, ParsedName)
    assert hasattr(result, "raw_stem")
    assert result.raw_stem == "rcs_stacking_v26"
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
cd D:/code/github_skill/weekly_report
python -m pytest scripts/tests/test_parse_filename.py -v
```

Expected: ImportError or all tests FAIL.

- [ ] **Step 3: Implement parse_filename**

```python
# weekly_report/scripts/parse_filename.py
"""Heuristic filename parser for PhD code repos.

Extracts (family_key, version_token, status_suffix) from file stems
to enable version-chain identification across weekly snapshots.
See spec §7 for the full algorithm.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional

STATUS_SUFFIXES = frozenset({
    "final", "fixed", "correct", "new", "legacy", "old", "bak",
})

VERSION_TOKEN_RE = re.compile(r"_v(\d+)([a-z])?(?:_(.+?))?$")
DOUBLE_STATUS_RE = re.compile(r"(?i)^(?P<head>.+?)_(?P<s1>final|fixed|correct)_.*_(?P=s1)$")
SUSPECTED_TYPO_RE = re.compile(r"_v\d+v\d+$")


@dataclass
class ParsedName:
    raw_stem: str
    family_key: str
    version: Optional[str] = None
    status: Optional[str] = None
    is_anomaly: bool = False
    anomaly_reasons: list[str] = field(default_factory=list)


def parse_filename(stem: str) -> ParsedName:
    """Parse a file stem (no extension) into family/version/status."""
    anomalies: list[str] = []

    if SUSPECTED_TYPO_RE.search(stem):
        anomalies.append("suspected_version_typo")

    if DOUBLE_STATUS_RE.search(stem):
        anomalies.append("double_status_marker")

    m = VERSION_TOKEN_RE.search(stem)
    version: Optional[str] = None
    semantic_suffix: Optional[str] = None
    status: Optional[str] = None

    if m:
        version = f"v{m.group(1)}{m.group(2) or ''}"
        semantic_suffix = m.group(3)
        if semantic_suffix and semantic_suffix.lower() in STATUS_SUFFIXES:
            status = semantic_suffix.lower()
            semantic_suffix = None
        base = stem[: m.start()]
    else:
        base = stem
        # Standalone status suffix: data_loader_new
        for s in STATUS_SUFFIXES:
            if base.lower().endswith(f"_{s}"):
                status = s
                base = base[: -(len(s) + 1)]
                break

    family_key = f"{base}_{semantic_suffix}" if semantic_suffix else base

    return ParsedName(
        raw_stem=stem,
        family_key=family_key,
        version=version,
        status=status,
        is_anomaly=bool(anomalies),
        anomaly_reasons=anomalies,
    )
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_parse_filename.py -v
```

Expected: all 13 parametrized + 3 named tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/parse_filename.py weekly_report/scripts/tests/test_parse_filename.py
git commit -m "feat(parse_filename): heuristic family_key/version/status extractor"
```

---

### Task 3: path_guard — write whitelist enforcer (RED LINE)

**Spec ref:** §1 红线工程化保障

**Files:**
- Create: `weekly_report/scripts/path_guard.py`
- Create: `weekly_report/scripts/tests/test_path_guard.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_path_guard.py
"""Tests for path_guard - enforces write whitelist."""
import pytest
from pathlib import Path
from scripts.path_guard import (
    is_write_allowed,
    assert_write_allowed,
    PathGuardError,
)


def test_allow_write_inside_weekly_report(tmp_project: Path):
    target = tmp_project / ".weekly_report" / "manifest.json"
    assert is_write_allowed(target, project_root=tmp_project) is True


def test_allow_write_under_reports_aggregate(tmp_path: Path):
    # Simulate D:\code\reports\ aggregate dir
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    target = reports_dir / "2026" / "05" / "report.md"
    assert is_write_allowed(target, project_root=None,
                            reports_root=reports_dir) is True


def test_deny_write_to_user_code(tmp_project: Path):
    target = tmp_project / "Forecasting" / "stolen_change.py"
    assert is_write_allowed(target, project_root=tmp_project) is False


def test_deny_write_to_paper_dir(tmp_project: Path):
    target = tmp_project / "paper_writing" / "draft.tex"
    assert is_write_allowed(target, project_root=tmp_project) is False


def test_assert_raises_on_violation(tmp_project: Path):
    target = tmp_project / "Forecasting" / "evil.py"
    with pytest.raises(PathGuardError, match="not in write whitelist"):
        assert_write_allowed(target, project_root=tmp_project)


def test_relative_path_resolved_against_project(tmp_project: Path):
    """Relative paths must be resolved against project_root before check."""
    # Construct a relative path that would escape via ..
    target = tmp_project / ".weekly_report" / ".." / "Forecasting" / "x.py"
    assert is_write_allowed(target, project_root=tmp_project) is False
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_path_guard.py -v
```

Expected: ImportError; all FAIL.

- [ ] **Step 3: Implement path_guard**

```python
# weekly_report/scripts/path_guard.py
"""Path write guard. Hard rule: skill MUST NOT modify user code.

Whitelisted write locations:
  - <project_root>/.weekly_report/**
  - <reports_root>/**           (cross-project aggregate, e.g. D:\\code\\reports\\)

Any other write attempt raises PathGuardError. Use assert_write_allowed()
before any open(..., 'w') / 'wb' / Path.write_text() / write_bytes() / mkdir
within scripts that synthesize output files.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional


class PathGuardError(RuntimeError):
    """Raised when a script tries to write outside the whitelist."""


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_write_allowed(
    target: Path,
    project_root: Optional[Path] = None,
    reports_root: Optional[Path] = None,
) -> bool:
    """Return True iff target is inside one of the whitelisted roots."""
    target = Path(target)
    if project_root is not None:
        weekly_report = Path(project_root) / ".weekly_report"
        if _is_within(target, weekly_report):
            return True
    if reports_root is not None:
        if _is_within(target, Path(reports_root)):
            return True
    return False


def assert_write_allowed(
    target: Path,
    project_root: Optional[Path] = None,
    reports_root: Optional[Path] = None,
) -> None:
    if not is_write_allowed(target, project_root, reports_root):
        raise PathGuardError(
            f"Write target {target} not in write whitelist "
            f"(project_root={project_root}, reports_root={reports_root})"
        )
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_path_guard.py -v
```

Expected: 6 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/path_guard.py weekly_report/scripts/tests/test_path_guard.py
git commit -m "feat(path_guard): enforce write whitelist as hard red-line"
```

---

## Phase 2: Scanner

### Task 4: ignore_rules helper

**Spec ref:** §6 Scanner 规则 / 文件级处理决策树

**Files:**
- Create: `weekly_report/scripts/ignore_rules.py`
- Create: `weekly_report/scripts/tests/test_ignore_rules.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_ignore_rules.py
import pytest
from pathlib import Path
from scripts.ignore_rules import IgnoreMatcher

GLOBAL_IGNORES = [
    "__pycache__/**", "*.pyc", ".pytest_cache/**",
    "dist/**", "build_tmp/**",
    "*~", "*_tmp.*", "*_temp.*",
    ".weekly_report/**",
]


@pytest.mark.parametrize("rel,expected", [
    ("Forecasting/__pycache__/x.pyc", True),
    ("Forecasting/train.py",          False),
    ("dist/wheel.whl",                True),
    ("Forecasting/build_tmp/x.txt",   True),
    ("a_tmp.py",                      True),
    ("a_temp.json",                   True),
    ("legacy_keep.py",                False),
    (".weekly_report/2026/05/x.md",   True),
    ("notes~",                        True),
])
def test_global_ignore_matches(rel, expected):
    m = IgnoreMatcher(global_globs=GLOBAL_IGNORES)
    assert m.is_ignored(Path(rel)) is expected


def test_project_ignore_layered_on_top():
    m = IgnoreMatcher(
        global_globs=GLOBAL_IGNORES,
        project_globs=["raw_data/**", "*.mat"],
    )
    assert m.is_ignored(Path("raw_data/sample.mat")) is True
    assert m.is_ignored(Path("Forecasting/x.py"))    is False


def test_symlink_skip(tmp_project: Path):
    """Symlinks are also ignored as policy."""
    m = IgnoreMatcher(global_globs=[], skip_symlinks=True)
    target = tmp_project / "real.py"
    target.write_text("x")
    link = tmp_project / "link.py"
    try:
        link.symlink_to(target)
        assert m.is_symlink(link) is True
    except (OSError, NotImplementedError):
        pytest.skip("symlink not permitted on this platform")
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_ignore_rules.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement IgnoreMatcher**

```python
# weekly_report/scripts/ignore_rules.py
"""Glob-based ignore matcher with global + project layered rules."""
from __future__ import annotations
import fnmatch
from pathlib import Path
from typing import Iterable, Optional


class IgnoreMatcher:
    def __init__(
        self,
        global_globs: Optional[Iterable[str]] = None,
        project_globs: Optional[Iterable[str]] = None,
        skip_symlinks: bool = True,
    ) -> None:
        self._globs: list[str] = []
        if global_globs:
            self._globs.extend(global_globs)
        if project_globs:
            self._globs.extend(project_globs)
        self._skip_symlinks = skip_symlinks

    def is_ignored(self, rel_path: Path) -> bool:
        s = str(rel_path).replace("\\", "/")
        for g in self._globs:
            # Support both "dir/**" prefix matches and plain glob
            if "**" in g:
                head = g.replace("/**", "")
                if s == head or s.startswith(head + "/"):
                    return True
            if fnmatch.fnmatch(s, g):
                return True
            # Also match basename for top-level patterns like "*_tmp.*"
            if fnmatch.fnmatch(rel_path.name, g):
                return True
        return False

    def is_symlink(self, abs_path: Path) -> bool:
        if not self._skip_symlinks:
            return False
        try:
            return abs_path.is_symlink()
        except OSError:
            return False
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_ignore_rules.py -v
```

Expected: 11 tests PASS (1 may skip on Windows non-admin).

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/ignore_rules.py weekly_report/scripts/tests/test_ignore_rules.py
git commit -m "feat(ignore_rules): glob-based ignore matcher with layered rules"
```

---

### Task 5: file_metadata — single-file inspect

**Spec ref:** §6 各 bucket 特殊处理

**Files:**
- Create: `weekly_report/scripts/file_metadata.py`
- Create: `weekly_report/scripts/tests/test_file_metadata.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_file_metadata.py
from pathlib import Path
from scripts.file_metadata import inspect_file, FileRecord


def test_inspect_small_file_includes_sha1(tmp_path: Path):
    f = tmp_path / "small.py"
    f.write_text("print(1)\n")
    rec = inspect_file(f, metadata_only_size_mb=10)
    assert isinstance(rec, FileRecord)
    assert rec.size > 0
    assert rec.sha1 is not None and len(rec.sha1) == 40
    assert rec.mtime > 0


def test_inspect_large_file_skips_sha1(tmp_path: Path):
    f = tmp_path / "big.bin"
    f.write_bytes(b"x" * (11 * 1024 * 1024))   # 11 MB
    rec = inspect_file(f, metadata_only_size_mb=10)
    assert rec.size == 11 * 1024 * 1024
    assert rec.sha1 is None


def test_inspect_missing_returns_none(tmp_path: Path):
    f = tmp_path / "ghost.py"
    rec = inspect_file(f, metadata_only_size_mb=10)
    assert rec is None
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_file_metadata.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement inspect_file**

```python
# weekly_report/scripts/file_metadata.py
"""Inspect a single file: size, mtime, sha1 (only if small enough)."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileRecord:
    path: str            # relative-to-project, posix style
    size: int
    mtime: float
    sha1: Optional[str]  # None if metadata-only


def _sha1_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha1()
    with p.open("rb") as fh:
        while True:
            data = fh.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def inspect_file(
    abs_path: Path,
    metadata_only_size_mb: int,
    rel_path: Optional[str] = None,
) -> Optional[FileRecord]:
    if not abs_path.exists() or not abs_path.is_file():
        return None
    st = abs_path.stat()
    size = st.st_size
    sha1 = None
    if size <= metadata_only_size_mb * 1024 * 1024:
        sha1 = _sha1_of(abs_path)
    return FileRecord(
        path=rel_path or str(abs_path).replace("\\", "/"),
        size=size,
        mtime=st.st_mtime,
        sha1=sha1,
    )
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_file_metadata.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/file_metadata.py weekly_report/scripts/tests/test_file_metadata.py
git commit -m "feat(file_metadata): single-file inspector with size-conditional sha1"
```

---

### Task 6: bucket_classifier — assign file to bucket

**Spec ref:** §4 buckets.* / §6 Scanner

**Files:**
- Create: `weekly_report/scripts/bucket_classifier.py`
- Create: `weekly_report/scripts/tests/test_bucket_classifier.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_bucket_classifier.py
import pytest
from scripts.bucket_classifier import BucketClassifier, BUCKETS

CONFIG = {
    "code":            {"roots": ["Forecasting", "hardware"], "exts": [".py"]},
    "experiment_data": {"roots": ["Forecasting/output"],      "exts": [".json"]},
    "paper":           {"roots": ["paper_writing"],            "exts": [".tex", ".md"]},
    "reading":         {"roots": ["research-wiki"],            "exts": [".md", ".pdf"]},
    "theory":          {"roots": ["theory"],                   "exts": [".md", ".tex"]},
    "figures":         {"roots": ["**/ppt_figures"],           "exts": [".png", ".svg"]},
    "checkpoint_signal":{"roots": ["**/checkpoint"],           "exts": [".pt", ".pth", ".ckpt"]},
}


@pytest.mark.parametrize("rel,bucket", [
    ("Forecasting/train.py",                       "code"),
    ("Forecasting/output/inference.json",          "experiment_data"),
    ("paper_writing/chapter3.tex",                 "paper"),
    ("research-wiki/notes.md",                     "reading"),
    ("theory/derivation.md",                       "theory"),
    ("Forecasting/ppt_figures/fig1.png",           "figures"),
    ("Forecasting/checkpoint/best_acc_0.94.pt",    "checkpoint_signal"),
    ("misc/random.txt",                            "uncategorized"),
])
def test_classify(rel, bucket):
    c = BucketClassifier(CONFIG)
    assert c.classify(rel) == bucket


def test_buckets_constant_matches_config():
    """All buckets enumerated in BUCKETS must be supported."""
    expected = {"code","experiment_data","paper","reading","theory","figures","checkpoint_signal","uncategorized"}
    assert set(BUCKETS) == expected
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_bucket_classifier.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement BucketClassifier**

```python
# weekly_report/scripts/bucket_classifier.py
"""Classify a file path into one of the buckets defined by project.toml."""
from __future__ import annotations
import fnmatch
from pathlib import PurePosixPath
from typing import Mapping

BUCKETS = (
    "code", "experiment_data", "paper", "reading",
    "theory", "figures", "checkpoint_signal", "uncategorized",
)


class BucketClassifier:
    def __init__(self, config: Mapping[str, Mapping]) -> None:
        # config[bucket_name] = {"roots": [...], "exts": [...]}
        self._cfg = config

    @staticmethod
    def _matches_root(rel: str, root: str) -> bool:
        rel = rel.replace("\\", "/")
        if "**" in root:
            # "**/ppt_figures" matches any depth
            tail = root.replace("**/", "").rstrip("/")
            parts = rel.split("/")
            for i, _ in enumerate(parts):
                if "/".join(parts[i:i+1]) == tail:
                    return True
                if rel.startswith("/".join(parts[: i + 1]) + "/" + tail + "/"):
                    return True
            return tail in parts
        # plain prefix
        return rel == root or rel.startswith(root.rstrip("/") + "/")

    def classify(self, rel_path: str) -> str:
        rel = rel_path.replace("\\", "/")
        ext = "." + rel.rsplit(".", 1)[-1].lower() if "." in rel else ""
        # Order matters: experiment_data before code (sub-prefix relationship)
        order = ("checkpoint_signal", "experiment_data", "figures", "theory",
                 "paper", "reading", "code")
        for name in order:
            cfg = self._cfg.get(name)
            if not cfg:
                continue
            roots = cfg.get("roots", [])
            exts = [e.lower() for e in cfg.get("exts", [])]
            if exts and ext not in exts:
                continue
            for r in roots:
                if self._matches_root(rel, r):
                    return name
        return "uncategorized"
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_bucket_classifier.py -v
```

Expected: all 9 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/bucket_classifier.py weekly_report/scripts/tests/test_bucket_classifier.py
git commit -m "feat(bucket_classifier): assign rel paths to buckets per config"
```

---

### Task 7: scan_project — ThreadPool walker integrating Tasks 2/4/5/6

**Spec ref:** §6 并发模型 / §5 manifest schema

**Files:**
- Create: `weekly_report/scripts/scan_project.py`
- Create: `weekly_report/scripts/tests/test_scan_project.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_scan_project.py
import json
from pathlib import Path
from scripts.scan_project import scan_project, ScanConfig


def _make_realistic_tree(root: Path):
    (root / "Forecasting").mkdir(parents=True)
    (root / "Forecasting" / "rcs_stacking_v25.py").write_text("# v25\n")
    (root / "Forecasting" / "rcs_stacking_v26.py").write_text("# v26\n")
    (root / "Forecasting" / "__pycache__").mkdir()
    (root / "Forecasting" / "__pycache__" / "x.pyc").write_text("garbage")
    (root / "Forecasting" / "output").mkdir()
    (root / "Forecasting" / "output" / "result.json").write_text(
        '{"track_acc": 0.94, "seed": 42}'
    )
    (root / "paper_writing").mkdir()
    (root / "paper_writing" / "chapter3.md").write_text("# 3 method\n")
    (root / "raw_data").mkdir()
    (root / "raw_data" / "huge.mat").write_bytes(b"x" * 1024)
    (root / "_tmp.py").write_text("scrap")


def test_scan_basic_buckets(tmp_path: Path):
    proj = tmp_path / "proj"
    _make_realistic_tree(proj)

    cfg = ScanConfig(
        project_root=proj,
        buckets={
            "code":            {"roots": ["Forecasting"],         "exts": [".py"]},
            "experiment_data": {"roots": ["Forecasting/output"],  "exts": [".json"]},
            "paper":           {"roots": ["paper_writing"],       "exts": [".md"]},
            "reading":         {"roots": [], "exts": []},
            "theory":          {"roots": [], "exts": []},
            "figures":         {"roots": [], "exts": []},
            "checkpoint_signal":{"roots":[], "exts": []},
        },
        global_ignores=["__pycache__/**", "*_tmp.*"],
        project_ignores=["raw_data/**"],
        metadata_only_size_mb=10,
        max_workers=4,
    )
    manifest = scan_project(cfg)

    code_paths = [f["path"] for f in manifest["buckets"]["code"]["files"]]
    assert "Forecasting/rcs_stacking_v25.py" in code_paths
    assert "Forecasting/rcs_stacking_v26.py" in code_paths

    exp_paths = [f["path"] for f in manifest["buckets"]["experiment_data"]["files"]]
    assert exp_paths == ["Forecasting/output/result.json"]

    paper_paths = [f["path"] for f in manifest["buckets"]["paper"]["files"]]
    assert paper_paths == ["paper_writing/chapter3.md"]

    # ignored
    all_paths = []
    for b in manifest["buckets"].values():
        all_paths.extend(f["path"] for f in b.get("files", []))
    assert not any("__pycache__" in p for p in all_paths)
    assert not any("raw_data" in p for p in all_paths)
    assert "_tmp.py" not in all_paths


def test_scan_extracts_version_chains(tmp_path: Path):
    proj = tmp_path / "proj"
    _make_realistic_tree(proj)
    cfg = ScanConfig(
        project_root=proj,
        buckets={"code": {"roots": ["Forecasting"], "exts": [".py"]},
                 "experiment_data": {"roots": [], "exts": []},
                 "paper": {"roots": [], "exts": []},
                 "reading": {"roots": [], "exts": []},
                 "theory": {"roots": [], "exts": []},
                 "figures": {"roots": [], "exts": []},
                 "checkpoint_signal": {"roots": [], "exts": []}},
        global_ignores=["__pycache__/**", "*_tmp.*"],
        project_ignores=[],
        metadata_only_size_mb=10,
        max_workers=2,
    )
    manifest = scan_project(cfg)
    chains = manifest["buckets"]["code"]["version_chains"]
    assert "rcs_stacking" in chains
    assert sorted(chains["rcs_stacking"]["versions"]) == ["v25", "v26"]


def test_scan_sets_metadata_fields(tmp_path: Path):
    proj = tmp_path / "proj"
    _make_realistic_tree(proj)
    cfg = ScanConfig(
        project_root=proj,
        buckets={"code": {"roots": ["Forecasting"], "exts": [".py"]},
                 "experiment_data": {"roots": [], "exts": []},
                 "paper": {"roots": [], "exts": []},
                 "reading": {"roots": [], "exts": []},
                 "theory": {"roots": [], "exts": []},
                 "figures": {"roots": [], "exts": []},
                 "checkpoint_signal": {"roots": [], "exts": []}},
        global_ignores=[],
        project_ignores=[],
        metadata_only_size_mb=10,
        max_workers=2,
    )
    manifest = scan_project(cfg)
    assert manifest["schema_version"] == "2.0"
    assert manifest["project_root"].endswith("proj")
    assert "scanned_at" in manifest
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_scan_project.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement scan_project**

```python
# weekly_report/scripts/scan_project.py
"""ThreadPool-based project scanner producing a manifest.json structure.

Spec: §6 Scanner. Single-source-of-truth for what a "weekly snapshot" contains.
"""
from __future__ import annotations
import datetime as _dt
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from scripts.bucket_classifier import BUCKETS, BucketClassifier
from scripts.file_metadata import FileRecord, inspect_file
from scripts.ignore_rules import IgnoreMatcher
from scripts.parse_filename import parse_filename


@dataclass
class ScanConfig:
    project_root: Path
    buckets: Mapping[str, Mapping]   # see test for shape
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
        rel = sub.relative_to(project_root)
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

    # Collect distinct root abs paths to walk in parallel
    roots: set[Path] = set()
    for cfg_b in cfg.buckets.values():
        for r in cfg_b.get("roots", []):
            # "**/x" patterns: fall back to walking project_root
            if "**" in r or r == "":
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
            # filename anomaly flag (code bucket only)
            if bucket == "code":
                stem = abs_p.stem
                p = parse_filename(stem)
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

    # Build version_chains for code bucket
    version_chains: dict[str, dict] = {}
    for r in files_by_bucket["code"]:
        stem = Path(r.path).stem
        p = parse_filename(stem)
        if p.version is None:
            continue
        ch = version_chains.setdefault(p.family_key, {"versions": []})
        if p.version not in ch["versions"]:
            ch["versions"].append(p.version)
        ch["latest_path"] = r.path

    manifest = {
        "schema_version": "2.0",
        "scanned_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "project_root": str(cfg.project_root),
        "buckets": {
            b: {
                "files": [r.__dict__ for r in files_by_bucket[b]],
                **({"version_chains": version_chains} if b == "code" else {}),
            }
            for b in BUCKETS
        },
        "anomalies": sorted(anomalies),
    }
    return manifest
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_scan_project.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/scan_project.py weekly_report/scripts/tests/test_scan_project.py
git commit -m "feat(scan_project): ThreadPool walker producing manifest structure"
```

---

## Phase 3: Metric Extraction

### Task 8: extract_metrics — JSON top-level numeric scanner

**Spec ref:** §8 Metric 抽取

**Files:**
- Create: `weekly_report/scripts/extract_metrics.py`
- Create: `weekly_report/scripts/tests/test_extract_metrics.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_extract_metrics.py
import pytest
from scripts.extract_metrics import (
    classify_key, extract_metrics_from_json, aggregate_by_seed,
    HINT_TOKENS_DEFAULT, CONFIG_HINT_DEFAULT, STAT_SUFFIX,
)


@pytest.mark.parametrize("k,expected", [
    ("track_acc",        "metric"),
    ("seg_acc",          "metric"),
    ("val_loss",         "metric"),
    ("f1_score",         "metric"),
    ("seed",             "config"),
    ("backbone",         "config"),
    ("n_train_tracks",   "config"),
    ("n_params",         "config"),
    ("track_acc_mean",   "metric"),   # via stat suffix stripping
    ("track_acc_std",    "metric"),
    ("nonsense_xyz",     "unknown"),
])
def test_classify_key_default_vocab(k, expected):
    cat = classify_key(k, hint_tokens=HINT_TOKENS_DEFAULT,
                       config_hints=CONFIG_HINT_DEFAULT,
                       stat_suffixes=STAT_SUFFIX,
                       known_metrics=set(), known_configs=set(),
                       ignored=set())
    assert cat == expected


def test_classify_known_overrides_hint():
    cat = classify_key("nonsense_xyz",
                       hint_tokens=HINT_TOKENS_DEFAULT,
                       config_hints=CONFIG_HINT_DEFAULT,
                       stat_suffixes=STAT_SUFFIX,
                       known_metrics={"nonsense_xyz"},
                       known_configs=set(),
                       ignored=set())
    assert cat == "metric"


def test_extract_from_json_dict():
    obj = {"track_acc": 0.94, "seed": 42, "backbone": "resnet34",
           "n_seeds": 8, "loss": 0.21, "label": "rcs"}
    out = extract_metrics_from_json(obj,
                                    known_metrics=set(),
                                    known_configs=set(),
                                    ignored=set())
    assert out["metrics"] == {"track_acc": 0.94, "loss": 0.21}
    assert out["config"]  == {"seed": 42, "n_seeds": 8, "backbone": "resnet34"}
    assert out["unknown_numeric"] == {}
    # non-numeric/non-config string ignored
    assert "label" not in out["metrics"] and "label" not in out["config"]


def test_aggregate_by_seed_mean_std():
    runs = [
        {"track_acc": 0.92, "seed": 1},
        {"track_acc": 0.93, "seed": 2},
        {"track_acc": 0.95, "seed": 3},
    ]
    agg = aggregate_by_seed(runs, metric_keys=["track_acc"])
    assert pytest.approx(agg["track_acc"]["mean"], abs=1e-6) == (0.92+0.93+0.95)/3
    assert agg["track_acc"]["n_seeds"] == 3
    assert agg["track_acc"]["std"] > 0
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_extract_metrics.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement extract_metrics**

```python
# weekly_report/scripts/extract_metrics.py
"""Heuristic JSON metric/config classifier + multi-seed aggregator.

Categories: metric / config / unknown / ignored.
Layered: hint tokens → known sets (from metric_vocab) → unknown bucket.
"""
from __future__ import annotations
import math
import statistics
from typing import Iterable, Mapping

HINT_TOKENS_DEFAULT = (
    "acc", "accuracy", "loss", "f1", "auc", "error", "err",
    "iou", "map", "recall", "precision",
    "mae", "rmse", "psnr", "ssim",
    "bleu", "rouge", "perplexity", "rate", "score",
)
CONFIG_HINT_DEFAULT = (
    "seed", "backbone", "lr", "epoch", "batch", "ratio", "pretrain",
    "n_params", "mode", "n_train", "n_val", "n_test", "rcs_mode",
)
STAT_SUFFIX = ("_mean", "_std", "_ci", "_ci_95", "_min", "_max", "_median")


def _strip_stat_suffix(k: str, suffixes: Iterable[str]) -> str:
    lk = k.lower()
    for s in suffixes:
        if lk.endswith(s):
            return k[: -len(s)]
    return k


def classify_key(
    key: str,
    *,
    hint_tokens: Iterable[str],
    config_hints: Iterable[str],
    stat_suffixes: Iterable[str],
    known_metrics: set[str],
    known_configs: set[str],
    ignored: set[str],
) -> str:
    """Return one of: 'metric' / 'config' / 'unknown' / 'ignored'."""
    if key in ignored:
        return "ignored"
    if key in known_metrics:
        return "metric"
    if key in known_configs:
        return "config"
    base = _strip_stat_suffix(key, stat_suffixes).lower()
    for h in hint_tokens:
        if h in base:
            return "metric"
    for c in config_hints:
        if c in key.lower():
            return "config"
    return "unknown"


def extract_metrics_from_json(
    obj: Mapping,
    *,
    known_metrics: set[str],
    known_configs: set[str],
    ignored: set[str],
    hint_tokens: Iterable[str] = HINT_TOKENS_DEFAULT,
    config_hints: Iterable[str] = CONFIG_HINT_DEFAULT,
    stat_suffixes: Iterable[str] = STAT_SUFFIX,
) -> dict[str, dict]:
    metrics: dict[str, float] = {}
    config: dict[str, object] = {}
    unknown_numeric: dict[str, float] = {}

    for k, v in obj.items():
        cat = classify_key(
            k,
            hint_tokens=hint_tokens, config_hints=config_hints,
            stat_suffixes=stat_suffixes,
            known_metrics=known_metrics, known_configs=known_configs,
            ignored=ignored,
        )
        if cat == "metric" and isinstance(v, (int, float)):
            metrics[k] = float(v)
        elif cat == "config":
            config[k] = v
        elif cat == "unknown" and isinstance(v, (int, float)):
            unknown_numeric[k] = float(v)
        # else: ignored / non-numeric metric / non-config string
    return {"metrics": metrics, "config": config, "unknown_numeric": unknown_numeric}


def aggregate_by_seed(runs: list[dict], metric_keys: list[str]) -> dict[str, dict]:
    """Aggregate metrics across seeds. Each run dict must contain the metric keys."""
    out: dict[str, dict] = {}
    for mk in metric_keys:
        values = [float(r[mk]) for r in runs if mk in r]
        if not values:
            continue
        mean = statistics.fmean(values)
        std = statistics.pstdev(values) if len(values) > 1 else 0.0
        out[mk] = {
            "mean": mean,
            "std": std,
            "n_seeds": len(values),
            "min": min(values),
            "max": max(values),
        }
    return out
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_extract_metrics.py -v
```

Expected: all PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/extract_metrics.py weekly_report/scripts/tests/test_extract_metrics.py
git commit -m "feat(extract_metrics): heuristic classifier + multi-seed aggregator"
```

---

### Task 9: metric_vocab IO + new-key flow

**Spec ref:** §8 metric_vocab.json schema / 新指标谨慎处理流

**Files:**
- Create: `weekly_report/scripts/metric_vocab.py`
- Create: `weekly_report/scripts/tests/test_metric_vocab.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_metric_vocab.py
import json
from pathlib import Path
from scripts.metric_vocab import load_metric_vocab, save_metric_vocab, MetricVocab


def test_load_missing_returns_empty(tmp_path: Path):
    v = load_metric_vocab(tmp_path / "nope.json", project_name="proj")
    assert v.metrics == {}
    assert v.config_keys == {}
    assert v.ignored_keys == set()
    assert v.project_name == "proj"


def test_round_trip(tmp_path: Path):
    v = MetricVocab(project_name="proj",
                    metrics={"track_acc": {"category":"metric","direction":"higher_better"}},
                    config_keys={"seed": {"category":"config"}},
                    ignored_keys={"junk"})
    fp = tmp_path / "vocab.json"
    save_metric_vocab(fp, v)
    loaded = load_metric_vocab(fp, project_name="proj")
    assert loaded.metrics == v.metrics
    assert loaded.config_keys == v.config_keys
    assert loaded.ignored_keys == v.ignored_keys


def test_save_writes_schema_version(tmp_path: Path):
    v = MetricVocab(project_name="p")
    fp = tmp_path / "vocab.json"
    save_metric_vocab(fp, v)
    obj = json.loads(fp.read_text())
    assert obj["schema_version"] == "1.0"
    assert obj["project_name"] == "p"
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_metric_vocab.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement metric_vocab IO**

```python
# weekly_report/scripts/metric_vocab.py
"""Read/write per-project metric_vocab.json (incremental learning)."""
from __future__ import annotations
import datetime as _dt
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class MetricVocab:
    project_name: str
    metrics: dict[str, dict] = field(default_factory=dict)
    config_keys: dict[str, dict] = field(default_factory=dict)
    ignored_keys: set[str] = field(default_factory=set)
    last_updated: Optional[str] = None


def load_metric_vocab(path: Path, *, project_name: str) -> MetricVocab:
    if not path.exists():
        return MetricVocab(project_name=project_name)
    obj = json.loads(path.read_text(encoding="utf-8"))
    return MetricVocab(
        project_name=obj.get("project_name", project_name),
        metrics=obj.get("metrics", {}),
        config_keys=obj.get("config_keys", {}),
        ignored_keys=set(obj.get("ignored_keys", [])),
        last_updated=obj.get("last_updated"),
    )


def save_metric_vocab(path: Path, vocab: MetricVocab) -> None:
    obj = {
        "schema_version": "1.0",
        "project_name": vocab.project_name,
        "last_updated": _dt.date.today().isoformat(),
        "metrics": vocab.metrics,
        "config_keys": vocab.config_keys,
        "stat_aggregates": ["_mean","_std","_ci","_ci_95","_min","_max","_median"],
        "ignored_keys": sorted(vocab.ignored_keys),
    }
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_metric_vocab.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/metric_vocab.py weekly_report/scripts/tests/test_metric_vocab.py
git commit -m "feat(metric_vocab): per-project vocab IO with incremental schema"
```

---

## Phase 4: Theory & Figures Extractors

### Task 10: theory_extractor — math block scanner

**Spec ref:** §6 theory bucket / §7 theory diff

**Files:**
- Create: `weekly_report/scripts/theory_extractor.py`
- Create: `weekly_report/scripts/tests/test_theory_extractor.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_theory_extractor.py
from pathlib import Path
from scripts.theory_extractor import extract_math_blocks


SAMPLE = r"""# Title
Some prose.

$$|mean(exp(j\phi))|$$

More prose with inline math \(a+b\) here.

\begin{equation}
\sum abs(RD)
\end{equation}
"""


def test_extract_three_kinds(tmp_path: Path):
    f = tmp_path / "theory.md"
    f.write_text(SAMPLE, encoding="utf-8")
    blocks = extract_math_blocks(f)
    kinds = sorted(b.kind for b in blocks)
    assert kinds == ["display_dollar", "equation_env", "inline_paren"]


def test_extract_returns_section_when_present(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("## 2.1 PhaseAmp\n\n$$x=y$$\n", encoding="utf-8")
    blocks = extract_math_blocks(f)
    assert blocks[0].section == "2.1 PhaseAmp"


def test_extract_skips_code_fences(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("```\n$$ignore$$\n```\n\n$$keep$$\n", encoding="utf-8")
    blocks = extract_math_blocks(f)
    assert len(blocks) == 1
    assert "keep" in blocks[0].body
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_theory_extractor.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement theory_extractor**

```python
# weekly_report/scripts/theory_extractor.py
"""Extract math blocks from .md/.tex files for the theory bucket diff.

Recognized:
  - $$...$$         (display_dollar)
  - \\(...\\)       (inline_paren)
  - \\begin{equation}...\\end{equation}  (equation_env)
Skips fenced code blocks (``` ... ```).
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path

DOLLAR_RE   = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
INLINE_RE   = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
EQUATION_RE = re.compile(r"\\begin\{equation\}(.+?)\\end\{equation\}", re.DOTALL)
HEADING_RE  = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


@dataclass
class MathBlock:
    file: str
    kind: str       # display_dollar / inline_paren / equation_env
    body: str
    section: str | None
    span: tuple[int, int]


def _strip_code_fences(text: str) -> str:
    # Replace fenced code blocks with whitespace of equal length so spans stay valid.
    fence = re.compile(r"```.*?```", re.DOTALL)
    return fence.sub(lambda m: " " * (m.end() - m.start()), text)


def _section_for(text: str, pos: int) -> str | None:
    last = None
    for m in HEADING_RE.finditer(text):
        if m.start() > pos:
            break
        last = m.group(2).strip()
    return last


def extract_math_blocks(path: Path) -> list[MathBlock]:
    raw = path.read_text(encoding="utf-8")
    cleaned = _strip_code_fences(raw)
    out: list[MathBlock] = []
    for kind, regex in (
        ("display_dollar", DOLLAR_RE),
        ("inline_paren",   INLINE_RE),
        ("equation_env",   EQUATION_RE),
    ):
        for m in regex.finditer(cleaned):
            section = _section_for(raw, m.start())
            out.append(MathBlock(
                file=str(path),
                kind=kind,
                body=m.group(1).strip(),
                section=section,
                span=(m.start(), m.end()),
            ))
    return out
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_theory_extractor.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/theory_extractor.py weekly_report/scripts/tests/test_theory_extractor.py
git commit -m "feat(theory_extractor): math block scanner ($$/inline/equation env)"
```

---

### Task 11: figure_picker — choose figures for the report

**Spec ref:** §4 buckets.figures / §5 manifest figures.candidates

**Files:**
- Create: `weekly_report/scripts/figure_picker.py`
- Create: `weekly_report/scripts/tests/test_figure_picker.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_figure_picker.py
from pathlib import Path
from scripts.figure_picker import pick_figures


def test_picks_newest_first(tmp_path: Path):
    cands = [
        {"path": "fig_old.png", "mtime": 1.0, "size": 100},
        {"path": "fig_mid.png", "mtime": 2.0, "size": 100},
        {"path": "fig_new.png", "mtime": 3.0, "size": 100},
    ]
    sel = pick_figures(cands, strategy="newest_3", max_per_report=2,
                       max_size_mb=10, active_window_days=None)
    paths = [s["path"] for s in sel]
    assert paths == ["fig_new.png", "fig_mid.png"]


def test_filters_oversize(tmp_path: Path):
    cands = [
        {"path": "fig_huge.png", "mtime": 1.0, "size": 11 * 1024 * 1024},
        {"path": "fig_ok.png",   "mtime": 2.0, "size": 1024},
    ]
    sel = pick_figures(cands, strategy="newest_3", max_per_report=5,
                       max_size_mb=10, active_window_days=None)
    paths = [s["path"] for s in sel]
    assert paths == ["fig_ok.png"]


def test_active_window_filters_old_figs(tmp_path: Path):
    import time
    now = time.time()
    cands = [
        {"path": "old.png",  "mtime": now - 30 * 86400, "size": 100},
        {"path": "new.png",  "mtime": now - 1  * 86400, "size": 100},
    ]
    sel = pick_figures(cands, strategy="newest_3", max_per_report=5,
                       max_size_mb=10, active_window_days=7)
    paths = [s["path"] for s in sel]
    assert paths == ["new.png"]
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_figure_picker.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement figure_picker**

```python
# weekly_report/scripts/figure_picker.py
"""Pick figure candidates to embed in a weekly report.

Strategy options:
  - "newest_3": pick the N most recently modified figures within the active window.
  - "by_family": (future) pick one per family_key; not used yet.
  - "all": take everything that fits the limits (cap by max_per_report).
"""
from __future__ import annotations
import time
from typing import Optional


def pick_figures(
    candidates: list[dict],
    *,
    strategy: str = "newest_3",
    max_per_report: int = 5,
    max_size_mb: float = 5.0,
    active_window_days: Optional[int] = None,
) -> list[dict]:
    cutoff = None
    if active_window_days is not None:
        cutoff = time.time() - active_window_days * 86400
    pool = []
    for c in candidates:
        if c.get("size", 0) > max_size_mb * 1024 * 1024:
            continue
        if cutoff is not None and c.get("mtime", 0) < cutoff:
            continue
        pool.append(c)
    pool.sort(key=lambda c: c.get("mtime", 0), reverse=True)
    return pool[:max_per_report]
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_figure_picker.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/figure_picker.py weekly_report/scripts/tests/test_figure_picker.py
git commit -m "feat(figure_picker): newest-N strategy with size+window filters"
```

---

## Phase 5: Diff Engine

### Task 12: compute_diff — manifest cross-week diff

**Spec ref:** §7 Differ 规则

**Files:**
- Create: `weekly_report/scripts/compute_diff.py`
- Create: `weekly_report/scripts/tests/test_compute_diff.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_compute_diff.py
from scripts.compute_diff import compute_diff


def _mk_manifest(week, files, version_chains=None):
    return {
        "week_id": week,
        "buckets": {
            "code": {
                "files": [{"path": p, "sha1": h, "mtime": 1.0, "size": 1}
                          for (p, h) in files],
                "version_chains": version_chains or {},
            },
            "experiment_data": {"files": []},
            "paper": {"files": []},
            "reading": {"files": []},
            "theory": {"files": []},
            "figures": {"files": []},
            "checkpoint_signal": {"files": []},
        },
    }


def test_added_modified_deleted_basic():
    last = _mk_manifest("W17", [("a.py","h1"), ("b.py","h2")])
    this = _mk_manifest("W18", [("a.py","h1"), ("b.py","h2_NEW"), ("c.py","h3")])
    d = compute_diff(last, this)
    code = d["code"]
    assert code["added_loose_files"] == ["c.py"]
    assert code["non_versioned_modified"] == ["b.py"]
    assert code["deleted_files"] == []


def test_version_chain_advanced():
    last = _mk_manifest("W17",
        [("rcs_stacking_v25.py","h1")],
        version_chains={"rcs_stacking": {"versions":["v25"], "latest_path":"rcs_stacking_v25.py"}})
    this = _mk_manifest("W18",
        [("rcs_stacking_v25.py","h1"), ("rcs_stacking_v26.py","h2")],
        version_chains={"rcs_stacking": {"versions":["v25","v26"], "latest_path":"rcs_stacking_v26.py"}})
    d = compute_diff(last, this)
    advanced = d["code"]["version_chains_advanced"]
    assert len(advanced) == 1
    assert advanced[0]["family"] == "rcs_stacking"
    assert advanced[0]["from"] == "v25"
    assert advanced[0]["to"]   == "v26"
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_compute_diff.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement compute_diff**

```python
# weekly_report/scripts/compute_diff.py
"""Compute cross-week diff between two manifests.

Output schema mirrors spec §7.
"""
from __future__ import annotations


def _index(files: list[dict]) -> dict[str, dict]:
    return {f["path"]: f for f in files}


def _diff_bucket(last_files, this_files):
    last_by = _index(last_files)
    this_by = _index(this_files)
    added = sorted(set(this_by) - set(last_by))
    deleted = sorted(set(last_by) - set(this_by))
    modified = []
    for p in sorted(set(last_by) & set(this_by)):
        if last_by[p].get("sha1") and this_by[p].get("sha1"):
            if last_by[p]["sha1"] != this_by[p]["sha1"]:
                modified.append(p)
        elif last_by[p].get("mtime") != this_by[p].get("mtime"):
            modified.append(p)
    return added, modified, deleted


def _diff_version_chains(last_chains, this_chains):
    out = []
    for fam, this_ch in this_chains.items():
        last_ch = last_chains.get(fam)
        last_versions = list(last_ch["versions"]) if last_ch else []
        this_versions = list(this_ch["versions"])
        # advanced if max version differs
        last_max = max(last_versions) if last_versions else None
        this_max = max(this_versions)
        if last_max != this_max:
            out.append({
                "family": fam,
                "from": last_max,
                "to": this_max,
                "diff_summary": "",   # filled by Writer/LLM stage
            })
    return out


def compute_diff(last_manifest: dict, this_manifest: dict) -> dict:
    out = {
        "this_week": this_manifest.get("week_id", "this"),
        "last_week": last_manifest.get("week_id", "last"),
    }
    last_b = last_manifest["buckets"]
    this_b = this_manifest["buckets"]

    # Code
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
    for bk in ("experiment_data", "paper", "reading", "theory", "figures", "checkpoint_signal"):
        a, m, d = _diff_bucket(
            last_b[bk]["files"], this_b[bk]["files"])
        out[bk] = {"added": a, "modified": m, "deleted": d}

    return out
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_compute_diff.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/compute_diff.py weekly_report/scripts/tests/test_compute_diff.py
git commit -m "feat(compute_diff): manifest cross-week diff with version-chain advancement"
```

---

## Phase 6: Init Mode

### Task 13: init_project — auto-detect bucket roots + scaffold project.toml

**Spec ref:** §11 第一周 baseline 模式 / 流程 step 1

**Files:**
- Create: `weekly_report/scripts/init_project.py`
- Create: `weekly_report/scripts/tests/test_init_project.py`
- Create: `weekly_report/assets/default-project.toml`

- [ ] **Step 1: Write the default project.toml template**

```toml
# weekly_report/assets/default-project.toml
[project]
name = ""              # auto-detected from directory name
display_name = ""
short_name = ""
domain = ""
advisor = ""
phd_year = 1

[buckets.code]
roots = []
ignore = ["__pycache__", "dist", "build_tmp", ".pytest_cache"]
include_extensions = [".py", ".cpp", ".h", ".cu"]
content_diff_size_kb = 200
sha1_for_content_diff = true

[buckets.experiment_data]
roots = []
ignore = ["raw_data/**", "dataset/**", "*.mat", "*.npy", "*.h5"]
include_extensions = [".json", ".csv", ".tsv"]
extract_metrics = true

[buckets.paper]
roots = []
ignore = [".aux", ".log", ".out", ".synctex.gz", "*.bak"]
include_extensions = [".tex", ".md", ".docx"]
section_diff = true

[buckets.reading]
roots = []
include_extensions = [".md", ".pdf"]

[buckets.theory]
roots = []
include_extensions = [".md", ".tex", ".ipynb"]
detect_math_in_paper = true
section_diff = true

[buckets.figures]
roots = []
include_extensions = [".png", ".jpg", ".jpeg", ".svg", ".pdf"]
sample_strategy = "newest_3"
max_per_report = 5
max_size_mb = 5

[checkpoint_signal]
enabled = true
roots = []
filename_patterns = [
  '_acc_(?P<acc>[\d.]+)',
  '_epoch_?(?P<epoch>\d+)',
  '_seed_?(?P<seed>\d+)',
  '_loss_(?P<loss>[\d.]+)',
]
ignore_content = true

[metrics]
hint_tokens_extra = []
config_keys_extra = []
multi_seed_aggregate = true
ci_field = "ci_95"

[scanner]
exclude_globs_global = [
  "__pycache__/**", "*.pyc", ".pytest_cache/**",
  "dist/**", "build/**", "build_tmp/**",
  ".idea/**", ".vscode/**",
  "*~", "*_tmp.*", "*_temp.*",
  ".weekly_report/**",
]
follow_symlinks = false
include_hidden = false
metadata_only_size_mb = 10
```

- [ ] **Step 2: Write failing tests**

```python
# weekly_report/scripts/tests/test_init_project.py
from pathlib import Path
import tomllib
from scripts.init_project import detect_buckets, build_project_toml


def test_detect_buckets_from_directory_shape(tmp_path: Path):
    (tmp_path / "Forecasting").mkdir()
    (tmp_path / "Forecasting" / "x.py").write_text("")
    (tmp_path / "Forecasting" / "output").mkdir()
    (tmp_path / "Forecasting" / "output" / "r.json").write_text("{}")
    (tmp_path / "paper_writing").mkdir()
    (tmp_path / "paper_writing" / "ch.md").write_text("# x")
    (tmp_path / "research-wiki").mkdir()
    (tmp_path / "research-wiki" / "n.md").write_text("# x")
    detected = detect_buckets(tmp_path)
    assert "Forecasting" in detected["code"]
    assert any("output" in r for r in detected["experiment_data"])
    assert "paper_writing" in detected["paper"]
    assert "research-wiki" in detected["reading"]


def test_build_project_toml_serializable(tmp_path: Path):
    text = build_project_toml(
        project_root=tmp_path,
        project_name="proj",
        display_name="My PhD Project",
        short_name="proj",
        detected={"code": ["Forecasting"], "experiment_data": ["Forecasting/output"],
                  "paper": [], "reading": [], "theory": [], "figures": [],
                  "checkpoint_signal": []},
    )
    obj = tomllib.loads(text)
    assert obj["project"]["name"] == "proj"
    assert obj["buckets"]["code"]["roots"] == ["Forecasting"]
```

- [ ] **Step 3: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_init_project.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 4: Implement init_project**

```python
# weekly_report/scripts/init_project.py
"""Init mode: auto-detect bucket roots and scaffold project.toml."""
from __future__ import annotations
from pathlib import Path

# Heuristic patterns for each bucket — subdir name keywords
NAME_HINTS = {
    "code":            ("forecasting", "code", "src", "hardware", "preprocess",
                        "fusion", "training", "models"),
    "experiment_data": ("output", "results", "experiments", "logs"),
    "paper":           ("paper_writing", "paper", "manuscript", "thesis"),
    "reading":         ("research-wiki", "reading", "papers_collected", "notes"),
    "theory":          ("theory", "derivations", "math", "notes_math"),
    "figures":         ("figures", "figs", "ppt_figures", "imgs", "plots"),
    "checkpoint_signal":("checkpoint", "checkpoints", "weights"),
}


def detect_buckets(project_root: Path) -> dict[str, list[str]]:
    detected: dict[str, list[str]] = {b: [] for b in NAME_HINTS}
    for sub in project_root.iterdir():
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        n = sub.name.lower()
        for bucket, hints in NAME_HINTS.items():
            if any(h in n for h in hints):
                detected[bucket].append(sub.name)
                break
    # second pass: nested checkpoint/output dirs
    for top in project_root.iterdir():
        if not top.is_dir() or top.name.startswith("."):
            continue
        for sub in top.iterdir():
            if not sub.is_dir():
                continue
            n = sub.name.lower()
            for bucket in ("experiment_data", "checkpoint_signal", "figures"):
                hints = NAME_HINTS[bucket]
                if any(h in n for h in hints):
                    rel = f"{top.name}/{sub.name}"
                    if rel not in detected[bucket]:
                        detected[bucket].append(rel)
    return detected


def build_project_toml(
    *,
    project_root: Path,
    project_name: str,
    display_name: str,
    short_name: str,
    detected: dict[str, list[str]],
) -> str:
    """Render a project.toml string from detected info. We hand-build to keep
    deterministic ordering and inline comments without an extra TOML dep."""
    def _toml_list(xs):
        return "[" + ", ".join(f'"{x}"' for x in xs) + "]"

    return f"""# Auto-generated by weekly-report-writer init at first run.
# Edit roots / ignore freely; re-run skill to pick up changes.

[project]
name = "{project_name}"
display_name = "{display_name}"
short_name = "{short_name}"
domain = ""
advisor = ""
phd_year = 1

[buckets.code]
roots = {_toml_list(detected.get('code', []))}
ignore = ["__pycache__", "dist", "build_tmp", ".pytest_cache"]
include_extensions = [".py", ".cpp", ".h", ".cu"]
content_diff_size_kb = 200
sha1_for_content_diff = true

[buckets.experiment_data]
roots = {_toml_list(detected.get('experiment_data', []))}
ignore = ["raw_data/**", "dataset/**", "*.mat", "*.npy", "*.h5"]
include_extensions = [".json", ".csv", ".tsv"]
extract_metrics = true

[buckets.paper]
roots = {_toml_list(detected.get('paper', []))}
ignore = [".aux", ".log", ".out", ".synctex.gz", "*.bak"]
include_extensions = [".tex", ".md", ".docx"]
section_diff = true

[buckets.reading]
roots = {_toml_list(detected.get('reading', []))}
include_extensions = [".md", ".pdf"]

[buckets.theory]
roots = {_toml_list(detected.get('theory', []))}
include_extensions = [".md", ".tex", ".ipynb"]
detect_math_in_paper = true
section_diff = true

[buckets.figures]
roots = {_toml_list(detected.get('figures', []))}
include_extensions = [".png", ".jpg", ".jpeg", ".svg", ".pdf"]
sample_strategy = "newest_3"
max_per_report = 5
max_size_mb = 5

[checkpoint_signal]
enabled = true
roots = {_toml_list(detected.get('checkpoint_signal', []))}
filename_patterns = [
  '_acc_(?P<acc>[\\d.]+)',
  '_epoch_?(?P<epoch>\\d+)',
  '_seed_?(?P<seed>\\d+)',
  '_loss_(?P<loss>[\\d.]+)',
]
ignore_content = true

[metrics]
hint_tokens_extra = []
config_keys_extra = []
multi_seed_aggregate = true
ci_field = "ci_95"

[scanner]
exclude_globs_global = [
  "__pycache__/**", "*.pyc", ".pytest_cache/**",
  "dist/**", "build/**", "build_tmp/**",
  ".idea/**", ".vscode/**",
  "*~", "*_tmp.*", "*_temp.*",
  ".weekly_report/**",
]
follow_symlinks = false
include_hidden = false
metadata_only_size_mb = 10
"""
```

- [ ] **Step 5: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_init_project.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 6: Commit (optional)**

```bash
git add weekly_report/scripts/init_project.py weekly_report/scripts/tests/test_init_project.py weekly_report/assets/default-project.toml
git commit -m "feat(init_project): bucket-root auto-detection + project.toml scaffold"
```

---

## Phase 7: Interview

### Task 14: interview_generator — produce interview.md

**Spec ref:** §9 Interview

**Files:**
- Create: `weekly_report/scripts/interview_generator.py`
- Create: `weekly_report/scripts/tests/test_interview_generator.py`
- Create: `weekly_report/assets/interview-template.md`

- [ ] **Step 1: Write the interview template skeleton**

```markdown
<!-- weekly_report/assets/interview-template.md -->
# 周报质询问卷 · {week_id} · {project_name}

## 元数据（自动生成，不要改）
- generated_at: {generated_at}
- diff_signature: {diff_signature}

{sections}

---
*Filled questionnaire is parsed by parse_interview.py.*
*H1 anchors (## ① ② ...) MUST stay; H2 sub-sections may be edited.*
```

- [ ] **Step 2: Write failing tests**

```python
# weekly_report/scripts/tests/test_interview_generator.py
from scripts.interview_generator import generate_interview


def test_generate_with_chain_advanced():
    diff = {
        "code": {
            "version_chains_advanced": [{"family":"rcs_stacking","from":"v25","to":"v26","diff_summary":""}],
            "non_versioned_modified": [], "added_loose_files": [], "deleted_files": [],
        },
        "experiment_data": {"added": [], "modified": [], "deleted": []},
        "paper":           {"added": [], "modified": ["paper_writing/ch3.md"], "deleted": []},
        "reading": {"added": [], "modified": [], "deleted": []},
        "theory":  {"added": [], "modified": [], "deleted": []},
        "figures": {"added": [], "modified": [], "deleted": []},
        "checkpoint_signal": {"added": [], "modified": [], "deleted": []},
    }
    md = generate_interview(
        week_id="2026-W18",
        project_name="radar",
        diff=diff,
        new_unknown_metrics=[],
        figure_candidates=[],
        theory_blocks_added=[],
    )
    assert "## ① 实验链进展" in md
    assert "rcs_stacking" in md
    assert "v25" in md and "v26" in md
    assert "## ③ 论文推进" in md
    assert "ch3.md" in md


def test_generate_with_new_unknown_metrics():
    diff = {"code": {"version_chains_advanced": [], "non_versioned_modified": [], "added_loose_files": [], "deleted_files": []},
            "experiment_data":{"added":[],"modified":[],"deleted":[]},
            "paper":{"added":[],"modified":[],"deleted":[]},
            "reading":{"added":[],"modified":[],"deleted":[]},
            "theory":{"added":[],"modified":[],"deleted":[]},
            "figures":{"added":[],"modified":[],"deleted":[]},
            "checkpoint_signal":{"added":[],"modified":[],"deleted":[]}}
    md = generate_interview(
        week_id="W18", project_name="p", diff=diff,
        new_unknown_metrics=[{"key":"weird_score","sample_file":"r.json"}],
        figure_candidates=[], theory_blocks_added=[],
    )
    assert "## ⑥ 本周发现新指标" in md
    assert "weird_score" in md
```

- [ ] **Step 3: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_interview_generator.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 4: Implement interview_generator**

```python
# weekly_report/scripts/interview_generator.py
"""Generate interview.md from manifest + diff data."""
from __future__ import annotations
import datetime as _dt
import hashlib
import json


def _diff_signature(diff: dict) -> str:
    return hashlib.sha1(json.dumps(diff, sort_keys=True).encode()).hexdigest()[:12]


def _section_chain_advanced(diff: dict) -> str:
    advanced = diff["code"]["version_chains_advanced"]
    if not advanced:
        return "（本周无版本链推进。如有遗漏请人工补充。）"
    out = []
    for c in advanced:
        out.append(
            f"### {c['family']} 链：{c['from']} → {c['to']}\n"
            f"**自动 diff 摘要**：（待填，由 LLM/手动补）\n"
            f"**请填**：\n"
            f"- {c['to']} 相对 {c['from']} 的核心改动：______\n"
            f"- 改动动机 / 解决的问题：______\n"
            f"- 是否达到预期：______\n"
        )
    return "\n".join(out)


def _section_paper(diff: dict) -> str:
    mods = diff["paper"]["modified"] + diff["paper"]["added"]
    if not mods:
        return "（本周论文文件无变化。）"
    body = []
    for f in mods:
        body.append(
            f"### {f}\n"
            f"**章节变动**：（章节级 diff 暂留待 LLM 阶段补全）\n"
            f"**请填**：\n"
            f"- 推进到：[ ] 初稿完成 [ ] 评审中 [ ] 待确认 [ ] 其他：____\n"
            f"- 预计完成时间：______\n"
        )
    return "\n".join(body)


def _section_unknown_metrics(metrics: list[dict]) -> str:
    if not metrics:
        return "（本周未发现新指标。）"
    out = []
    for m in metrics:
        out.append(
            f"### `{m['key']}`\n"
            f"- 出现位置：{m.get('sample_file','?')}\n"
            f"- 自动猜测：metric / 待确认\n"
            f"- [ ] 是指标，方向 higher_better\n"
            f"- [ ] 是指标，方向 lower_better\n"
            f"- [ ] 是配置（不参与对比）\n"
            f"- [ ] 忽略\n"
        )
    return "\n".join(out)


def _section_theory(blocks: list[dict]) -> str:
    if not blocks:
        return "（本周无新增公式块。如本周有理论推导，请手动补一段。）"
    out = []
    for b in blocks:
        out.append(
            f"### {b.get('file','?')} 第 {b.get('section','?')} 节\n"
            f"**自动检测的新公式**：\n- `{b.get('body','')[:80]}`\n"
            f"**请填**：\n"
            f"- 物理含义 / 数学动机：______\n"
            f"- 是否计划写进论文，哪一节：______\n"
            f"- 是否需要进一步推导 / 验证：______\n"
        )
    return "\n".join(out)


def _section_figures(cands: list[dict]) -> str:
    if not cands:
        return "（本周无候选配图。）"
    body = ["skill 已根据 mtime + family link 选出候选图，请勾选要嵌入周报的图（标题如有不准请改）："]
    for c in cands:
        body.append(f"- [ ] {c['path']} (caption: {c.get('caption_draft','')})")
    return "\n".join(body)


def generate_interview(
    *,
    week_id: str,
    project_name: str,
    diff: dict,
    new_unknown_metrics: list[dict],
    figure_candidates: list[dict],
    theory_blocks_added: list[dict],
) -> str:
    sig = _diff_signature(diff)
    sections = [
        ("① 实验链进展（必填）",   _section_chain_advanced(diff)),
        ("② 实验指标突变（必填）", "（指标突变检测见 manifest.metric_aggregates，请基于本节自动填表后审一遍）"),
        ("③ 论文推进（必填）",     _section_paper(diff)),
        ("④ 阅读 / 思考类（选填）","（系统不一定能从 mtime 看到，请你简述本周读了什么、有何启发）\n**请填**：______"),
        ("⑤ 给老师的 ask（选填）", "**请填**：\n- 需要的实验器材 / 数据：______\n- 需要老师确认的方向：______\n- 需要的计算资源：______"),
        ("⑥ 本周发现新指标（必处理）", _section_unknown_metrics(new_unknown_metrics)),
        ("⑦ 理论 / 公式推导（必填如有变化）", _section_theory(theory_blocks_added)),
        ("⑧ 配图建议（半自动）", _section_figures(figure_candidates)),
        ("⑨ 风险与阻塞（选填）", "**请填**：______"),
    ]
    section_md = "\n\n".join(f"## {h}\n\n{body}" for h, body in sections)
    return (
        f"# 周报质询问卷 · {week_id} · {project_name}\n\n"
        f"## 元数据（自动生成，不要改）\n"
        f"- generated_at: {_dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"- diff_signature: {sig}\n\n"
        f"{section_md}\n\n"
        f"---\n"
        f"*Filled questionnaire is parsed by parse_interview.py.*\n"
        f"*H1 anchors (## ① ② ...) MUST stay; H2 sub-sections may be edited.*\n"
    )
```

- [ ] **Step 5: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_interview_generator.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 6: Commit (optional)**

```bash
git add weekly_report/scripts/interview_generator.py weekly_report/scripts/tests/test_interview_generator.py weekly_report/assets/interview-template.md
git commit -m "feat(interview_generator): produce L3 questionnaire from diff"
```

---

### Task 15: parse_interview — H1-strict / H2-loose parser

**Spec ref:** §9 Interview.md 解析容错

**Files:**
- Create: `weekly_report/scripts/parse_interview.py`
- Create: `weekly_report/scripts/tests/test_parse_interview.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_parse_interview.py
from scripts.parse_interview import parse_interview


SAMPLE = """# 周报质询问卷 · 2026-W18 · radar

## 元数据
- generated_at: 2026-05-04T10:00
- diff_signature: deadbeef

## ① 实验链进展（必填）
### rcs_stacking 链：v25 → v26
**请填**：
- v26 相对 v25 的核心改动：换了 stacking 头从 LR 改 GBM
- 改动动机：解决 v25 的 underfit
- 是否达到预期：是

## ② 实验指标突变（必填）
（无）

## ⑥ 本周发现新指标
### `weird_score`
- [x] 是指标，方向 higher_better
- [ ] 是配置
"""


def test_parse_collects_sections():
    out = parse_interview(SAMPLE)
    assert "①" in out["sections"]
    assert "v25" in out["sections"]["①"]["raw"]
    assert "deadbeef" == out["meta"]["diff_signature"]


def test_parse_extracts_请填_text_blocks():
    out = parse_interview(SAMPLE)
    text = out["sections"]["①"]["fill_in"]
    assert "stacking 头" in text
    assert "underfit" in text


def test_parse_extracts_checkboxes():
    out = parse_interview(SAMPLE)
    boxes = out["sections"]["⑥"]["checkboxes"]
    matched = [(b["text"], b["checked"]) for b in boxes]
    assert ("是指标，方向 higher_better", True)  in matched
    assert ("是配置", False) in matched


def test_missing_section_does_not_crash():
    md = "# 标题\n\n## ① 实验链\n（空）\n"
    out = parse_interview(md)
    assert "①" in out["sections"]
    # missing later sections
    for k in "②③④⑤⑥⑦⑧⑨":
        assert out["sections"].get(k) is None or out["sections"][k]["raw"] == ""
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_parse_interview.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement parse_interview**

```python
# weekly_report/scripts/parse_interview.py
"""Parse a filled interview.md.

Strategy:
  H1 anchors (## ① ... ## ⑨) are STRICT: serial number must match.
  H2/text inside each H1 block is loose: parser doesn't care about section
  titles, just extracts (a) raw block, (b) all `**请填**:` text blocks,
  (c) all checkbox lines.
"""
from __future__ import annotations
import re

H1_RE = re.compile(r"^##\s+([①②③④⑤⑥⑦⑧⑨])\s+(.*)$", re.MULTILINE)
META_RE = re.compile(r"^-\s*(\w+):\s*(.+)$", re.MULTILINE)
FILLIN_RE = re.compile(r"\*\*请填\*\*\s*[:：]\s*(.+?)(?=\n\s*\n|\Z)", re.DOTALL)
CHECKBOX_RE = re.compile(r"^\s*-\s*\[(?P<m>[ xX])\]\s+(?P<text>.+)$", re.MULTILINE)

ALL_KEYS = list("①②③④⑤⑥⑦⑧⑨")


def parse_interview(md: str) -> dict:
    out: dict = {"meta": {}, "sections": {k: None for k in ALL_KEYS}}

    # Meta block: between first H1 and first H1 with sentinel
    head_split = H1_RE.split(md, maxsplit=1)
    head = head_split[0] if head_split else md
    for m in META_RE.finditer(head):
        out["meta"][m.group(1)] = m.group(2).strip()

    matches = list(H1_RE.finditer(md))
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        block = md[start:end].strip()
        fill_in_blocks = [t.strip().rstrip("\n").strip() for t in FILLIN_RE.findall(block)]
        checkboxes = []
        for cb in CHECKBOX_RE.finditer(block):
            checkboxes.append({
                "text": cb.group("text").strip(),
                "checked": cb.group("m").strip().lower() == "x",
            })
        out["sections"][key] = {
            "title": m.group(2).strip(),
            "raw": block,
            "fill_in": "\n\n".join(b for b in fill_in_blocks if b and b != "______"),
            "checkboxes": checkboxes,
        }
    return out
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_parse_interview.py -v
```

Expected: 4 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/parse_interview.py weekly_report/scripts/tests/test_parse_interview.py
git commit -m "feat(parse_interview): H1-strict/H2-loose questionnaire parser"
```

---

## Phase 8: Aggregation Index

### Task 16: update_index — append a row to D:\code\reports\index.md

**Spec ref:** §3 汇总区 / index.md

**Files:**
- Create: `weekly_report/scripts/update_index.py`
- Create: `weekly_report/scripts/tests/test_update_index.py`

- [ ] **Step 1: Write failing tests**

```python
# weekly_report/scripts/tests/test_update_index.py
from pathlib import Path
from scripts.update_index import upsert_index_row


def test_creates_index_when_missing(tmp_path: Path):
    idx = tmp_path / "index.md"
    upsert_index_row(idx, year="2026", week="W18",
                     date_range="2026-05-04~05-10",
                     project_short="radar",
                     highlight="rcs_stacking v25→v26",
                     link="2026/05/2026-05-04_05-10_W18_radar.md")
    text = idx.read_text(encoding="utf-8")
    assert "# 周报汇总索引" in text
    assert "## 2026" in text
    assert "rcs_stacking v25→v26" in text


def test_appends_without_dup(tmp_path: Path):
    idx = tmp_path / "index.md"
    upsert_index_row(idx, year="2026", week="W18",
                     date_range="2026-05-04~05-10",
                     project_short="radar",
                     highlight="x",
                     link="a.md")
    upsert_index_row(idx, year="2026", week="W18",
                     date_range="2026-05-04~05-10",
                     project_short="radar",
                     highlight="x_updated",
                     link="a.md")
    text = idx.read_text(encoding="utf-8")
    assert text.count("| W18 | 2026-05-04~05-10 | radar |") == 1
    assert "x_updated" in text and "| x |" not in text
```

- [ ] **Step 2: Run tests, verify they fail**

```bash
python -m pytest scripts/tests/test_update_index.py -v
```

Expected: ImportError; FAIL.

- [ ] **Step 3: Implement update_index**

```python
# weekly_report/scripts/update_index.py
"""Maintain D:\\code\\reports\\index.md across all projects/weeks.

Rules:
  - Idempotent: re-running with same (year, week, project) replaces row.
  - Year sections: ## YYYY  with a markdown table inside.
  - Newest year/week at top.
"""
from __future__ import annotations
from pathlib import Path

HEADER = "# 周报汇总索引\n"
TABLE_HEADER = (
    "| 周号 | 日期 | 工程 | 本周抓手 | 链接 |\n"
    "| --- | --- | --- | --- | --- |\n"
)


def _parse(md: str) -> dict[str, list[str]]:
    """Parse existing index.md into {year: [row_lines]} preserving rest of structure."""
    years: dict[str, list[str]] = {}
    current = None
    for line in md.splitlines():
        if line.startswith("## ") and line[3:].strip().isdigit():
            current = line[3:].strip()
            years.setdefault(current, [])
            continue
        if current is None:
            continue
        if line.startswith("| W") or (line.startswith("|") and "|" in line[1:] and "---" not in line):
            years[current].append(line)
    return years


def upsert_index_row(
    index_path: Path,
    *, year: str, week: str, date_range: str,
    project_short: str, highlight: str, link: str,
) -> None:
    md = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    years = _parse(md)

    new_row = f"| {week} | {date_range} | {project_short} | {highlight} | [→]({link}) |"

    rows = years.setdefault(year, [])
    rows = [r for r in rows if not r.startswith(f"| {week} | {date_range} | {project_short} |")]
    rows.append(new_row)
    years[year] = rows

    sorted_years = sorted(years.keys(), reverse=True)
    out_lines: list[str] = [HEADER]
    for y in sorted_years:
        out_lines.append(f"\n## {y}\n\n{TABLE_HEADER}".rstrip("\n"))
        out_lines.append("\n".join(years[y]))
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
```

- [ ] **Step 4: Run tests, verify they pass**

```bash
python -m pytest scripts/tests/test_update_index.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit (optional)**

```bash
git add weekly_report/scripts/update_index.py weekly_report/scripts/tests/test_update_index.py
git commit -m "feat(update_index): idempotent cross-project index.md maintainer"
```

---

## Phase 9: Templates & References

### Task 17: Replace assets/weekly-report-template.md with PhD format

**Spec ref:** §10 增量周报模板 + 样例 docx

**Files:**
- Modify: `weekly_report/assets/weekly-report-template.md`

- [ ] **Step 1: Read existing template**

Run: `cat weekly_report/assets/weekly-report-template.md`
Expected: 4 empty H2 headings (the rough draft).

- [ ] **Step 2: Replace with full template**

Replace file content with:

```markdown
**{semester}{month}{week_ordinal}周报**

{advisor_title}好：

向您汇报本周的学习情况，本周主要完成了 {N} 项工作：{(1) 工作 A; (2) 工作 B; ...}

# {主要工作 1 标题}

## 实验背景与目的
{从 paper bucket / theory bucket / interview ① 提炼}

## 自动化实验框架 / 方法
{L1 自动归并 + L2 摘要 + checkpoint_signal 整合，说明本周做了什么改动}

## 实验结果
{多 seed 聚合表 + checkpoint_signal best_acc + diff 对比表}

| 模型 | 均值 | 标准差 | 最小值 | 最大值 | 判定 |
| --- | --- | --- | --- | --- | --- |

{若 figures bucket 选中本节配图：}
![{caption}](images/{filename})

## 关键发现与分析
{interview ② 答案 + LLM 归纳出"为什么"}

## 理论 / 公式（如本周有理论变化才出）
{从 theory bucket math_blocks_added + interview ⑦ 拼出}

# {主要工作 2 标题}
{同上模板}

# 本周总结

1. {结论 1}
2. {结论 2}
3. {结论 3}

# 下周任务安排

1. {可验证的任务 1}
2. {可验证的任务 2}
3. {可验证的任务 3}

# 给老师的 ask
{interview ⑤；若空则不出此节}

祝您工作顺利，身体健康！

{student_name}

{date_range_slash}

---
*本周扫描指纹：{N} 文件 / {M} 实验链 / {K} 指标更新 ｜ 待确认新指标：{count} ｜ 命名异常 flag：{count}*
*Auto-generated by weekly-report-writer v1.0 · diff vs {last_week_id} · {scanned_at}*
```

- [ ] **Step 3: Verify the template parses as valid markdown**

```bash
python -c "import pathlib; print(pathlib.Path('weekly_report/assets/weekly-report-template.md').read_text(encoding='utf-8')[:200])"
```

Expected: First 200 chars include `**{semester}` and `{advisor_title}好：`.

- [ ] **Step 4: Commit (optional)**

```bash
git add weekly_report/assets/weekly-report-template.md
git commit -m "feat(template): replace draft with PhD-format incremental template"
```

---

### Task 18: Create assets/baseline-report-template.md (10 sections)

**Spec ref:** §11 baseline 模式

**Files:**
- Create: `weekly_report/assets/baseline-report-template.md`

- [ ] **Step 1: Write the baseline template**

```markdown
**{semester} 项目工作总报告**

{advisor_title}好：

向您汇报截至 {today_date} 的项目阶段性成果。本报告系统梳理 {project_display_name} 项目的整体进展、当前指标基线、理论方法、风险识别与未来 3 个月路线图，作为后续每周增量周报的对照基准。

# 一、项目背景与目标
{从 project.toml.domain + paper bucket 抽取项目说明}

# 二、整体架构概览
{按 bucket 列出主目录及其职责}

| 模块 | 职责 | 文件数 |
| --- | --- | --- |

{若 figures bucket 命中"architecture/overview"类，嵌入架构图：}
![架构图](images/{architecture_overview})

# 三、已完成的核心实验链
{每条 family_key 一个 H2 子节，含历史方法演进 V4→V5a→V5b 这种叙事}

# 四、当前指标基线
{全工程指标全景表 + 配图 box plot/CI 图}

# 五、理论与方法总结
{从 theory + paper bucket 抽核心公式块}

# 六、推进中的工作

# 七、已识别的风险与未解问题

# 八、未来 3 个月路线图
{由 baseline-roadmap-prompt.md 生成的四象限内容}

## 8.1 科学问题

## 8.2 方法路线
### Milestone 1（截至 YYYY-MM）
- 子问题 / 假设 / 成功标志 / 风险与 Plan B
### Milestone 2
### Milestone 3

## 8.3 预期产出
- 论文：目标 venue + 投稿日期
- 专利 / 开源 / Demo
- 节点：中期 / 答辩

## 8.4 资源与协作
- 计算 / 导师 / 外部合作

# 九、给老师的统一汇报点
{interview baseline ⑤}

祝您工作顺利，身体健康！

{student_name}

{baseline_date_slash}

---
*Auto-generated baseline by weekly-report-writer v1.0 · {scanned_at}*
*后续按周做增量，下次跑会基于本份生成 W{first_week} 增量周报。*
```

- [ ] **Step 2: Verify file exists**

```bash
ls -la weekly_report/assets/baseline-report-template.md
```

Expected: file exists, > 1KB.

- [ ] **Step 3: Commit (optional)**

```bash
git add weekly_report/assets/baseline-report-template.md
git commit -m "feat(template): 10-section baseline report template"
```

---

### Task 19: Create references/baseline-roadmap-prompt.md

**Spec ref:** §11.1 路线图章节的 LLM Prompt

**Files:**
- Create: `weekly_report/references/baseline-roadmap-prompt.md`

- [ ] **Step 1: Write the prompt reference**

```markdown
# Baseline Roadmap Prompt

This prompt drives §8 of the baseline report (the 3-month roadmap). It's
designed so the output can be lifted directly into a paper Introduction or
defense slides. Use it once per init/baseline run.

## When to use

- Running `/weekly-report init` for the first time on a project, OR
- Running `/weekly-report baseline --refresh` to re-cut the roadmap.

## Inputs to feed the LLM

1. `manifest.json` (full)
2. `metric_aggregates` (compiled across all output JSONs)
3. `theory.math_blocks` (existing equations established in the project)
4. `paper.section_changes` (latest paper section structure)
5. `project.toml` (domain, advisor, phd_year)
6. User's free-form input via baseline interview ① (one paragraph: 学生眼里的最高层科研问题)

## Prompt template

> 你是一个 PhD 学生的研究路线图起草助手。基于以下输入，按四象限结构起草未来 3 个月的路线图。
>
> 输入：
> - 项目领域：{domain}
> - 学生输入的最高层问题：{user_problem_statement}
> - 已有指标基线：{metric_aggregates}
> - 已成立公式：{theory_math_blocks}
> - 论文结构：{paper_sections}
>
> 约束：
> 1. 每个 milestone 必须有可验证的成功标志（数字、文件、章节）
> 2. 引用 theory bucket 中已成立的公式作为"已有基础"
> 3. 风险栏需写明 Plan B（而非笼统"如果不行就重来"）
> 4. 投稿时间点必须落到具体月份
> 5. 每条不超过 80 字，便于直接抠到论文 Introduction / 答辩 PPT
> 6. 用过去时讲已完成 / 现在时讲推进中 / 将来时讲下一步，不混
>
> 输出格式（不要更改 H2 编号）：
>
> ```markdown
> ## 8.1 科学问题
> （一句话，narrowing 公式：在 X 场景下，由于 Y 约束，导致 Z 问题，本课题旨在从 W 角度提供解法）
>
> ## 8.2 方法路线
>
> ### Milestone 1（截至 YYYY-MM）
> - 研究子问题：……
> - 待验证的假设：……
> - 可衡量的成功标志：……
> - 风险与 Plan B：……
>
> ### Milestone 2 / Milestone 3 同上
>
> ## 8.3 预期产出
> - 论文：目标 venue（IEEE TGRS / ICASSP / 其他），投稿日期
> - 专利 / 开源 / Demo
> - 节点：中期 / 终期答辩
>
> ## 8.4 资源与协作
> - 计算资源（GPU 类型、节点数）
> - 需要导师协调的事项
> - 可能的合作组
> ```
>
> 自审要求：输出后，重读一遍，问自己——「这段如果直接贴到导师面前，会不会觉得空？」如果会，重写至少一个 milestone 的成功标志使其更具体。

## After receiving LLM output

1. Save to `<project>/.weekly_report/baseline/roadmap_v1.md`
2. Insert into baseline report §8 directly
3. Add to baseline interview as "请审一遍这份路线图，有要改的地方在下方写 Δ"
4. After user reviews, generate `roadmap_v2.md` with their deltas applied

## Iterating

After each paper submission or rebuttal cycle, re-run this prompt with
updated `metric_aggregates` and `paper.section_changes` to produce a new
version. Old versions stay in `baseline/` for traceability.
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/baseline-roadmap-prompt.md
git commit -m "feat(roadmap): paper-quality 3-month roadmap LLM prompt"
```

---

### Task 20: Create references/greeting-templates.md

**Spec ref:** §10 模板字段映射 / 样例 docx 问候格式

**Files:**
- Create: `weekly_report/references/greeting-templates.md`

- [ ] **Step 1: Write the greeting templates**

```markdown
# Greeting / Closing Templates

Defines opener (问候语) and closer (结束语) for incremental and baseline reports.
Picked at render-time based on `project.toml`. Designed so the output matches the
academic style of `2026春-3月第1周报-李越.docx`.

## Title prefix patterns

| Style | Pattern | Example |
| --- | --- | --- |
| 学期 + 月 + 周序 | `{学年}{季节}学期{月份}第{n}周周报` | `2026春季学期三月第一周周报` |
| 简短 | `周报 · {YYYY-MM-DD ~ MM-DD}` | `周报 · 2026-05-04 ~ 2026-05-10` |
| 项目前缀 | `{project_display_name} · 周报 · {date_range}` | `多维特征融合的低空雷达目标识别 · 周报 · 2026-05-04 ~ 05-10` |

Default: 学期 + 月 + 周序 (matches sample).

## 季节判断

- 1-2月 / 3-6月：春季学期
- 7-8月：暑假
- 9-12月：秋季学期

## 第 n 周计算

`n = (day_of_month - 1) // 7 + 1`，输出"第一周/第二周/.../第五周"。

## 中文月份

mapping = {1:"一月", 2:"二月", ..., 12:"十二月"}.

## Greeting block

```
{advisor_title}好：

向您汇报本周的学习情况，本周主要完成了 {N} 项工作：{(1) ...; (2) ...; (3) ...}
```

`{advisor_title}` 来源：

1. project.toml `[project] advisor = "陈老师"` 配置
2. 若空，默认 "老师"
3. 学生交互首次询问后写入 project.toml

## Closing block

```
祝您工作顺利，身体健康！

{student_name}

{date_range_slash}
```

`{date_range_slash}` 格式：`YYYY/M/D-YYYY/M/D`（不补零，与样例一致）。
`{student_name}` 来源：project.toml `[project] student = "..."`。

## Variants by occasion

| 场合 | 结束祝福 |
| --- | --- |
| 普通周 | 祝您工作顺利，身体健康！ |
| 节假日前 | 祝您 {假期} 快乐！ |
| 学期初 | 新学期诸事顺利！ |
| 投稿期 | 期待您的进一步指导！ |

LLM 在 Writer 阶段根据 `today_date` 自动选祝福。

## Baseline 报告变体

baseline 总报告的开场段比增量更正式：

```
{advisor_title}好：

向您汇报截至 {today_date} 的项目阶段性成果。本报告系统梳理
{project_display_name} 项目的整体进展、当前指标基线、理论方法、
风险识别与未来 3 个月路线图，作为后续每周增量周报的对照基准。
```

## 示例（来自样例 docx）

```
**2026春季学期三月第一周周报**

陈老师好：

向您汇报本周的学习情况，本周主要完成了三项工作：(1)
蒙特卡洛鲁棒性验证实验；(2)
PhaseAmp_V5b相位保留方法的原理梳理与技术总结；(3)
低空雷达目标航迹3D可视化工具开发。

[正文]

祝您工作顺利，身体健康！

李越

2026/3/3-2026/3/9
```
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/greeting-templates.md
git commit -m "feat(greeting): opener/closer templates aligned with sample docx"
```

---

### Task 21: Create references/version-chain-heuristic.md

**Files:**
- Create: `weekly_report/references/version-chain-heuristic.md`

- [ ] **Step 1: Write the heuristic reference**

```markdown
# Version Chain Heuristic Reference

This document describes the family/version/status extraction algorithm used
by `parse_filename.py`. It mirrors spec §7 but with worked examples from
the radar_target_recognition project.

## The Algorithm in One Picture

```
stem  →  match _v(\d+)([a-z])?(_<suffix>)?$
                ↓
       version = "v17", semantic_suffix = "contrastive"
                ↓
       semantic_suffix in STATUS_SUFFIXES?
         yes → status = suffix, semantic_suffix = None
         no  → keep semantic_suffix
                ↓
       family_key = base + "_" + semantic_suffix (if any)
```

## Worked Examples (real files from this project)

| File | family_key | version | status | comment |
| --- | --- | --- | --- | --- |
| rcs_stacking_v26.py | rcs_stacking | v26 | None | clean version chain |
| train_v17_contrastive.py | train_contrastive | v17 | None | semantic branch |
| train_v17_fixed.py | train | v17 | fixed | bugfix iteration |
| train_v19_mstcn_contrastive.py | train_mstcn_contrastive | v19 | None | different family from train_contrastive |
| adaptive_fusion_v5b.py | adaptive_fusion | v5b | None | sub-version letter |
| data_loader_new.py | data_loader | None | new | bare status, no version |
| Final_inference_final.py | (anomaly) | None | None | double_status_marker — flagged |
| analyze_errors_v20v2.py | analyze_errors_v2 | None | None | suspected_version_typo — flagged |

## What is grouped vs not

- `rcs_stacking_v25.py` and `rcs_stacking_v26.py` → same family, advanced from v25 to v26.
- `train_v17_contrastive.py` and `train_v19_contrastive.py` would share family `train_contrastive`. ✅ Grouped.
- `train_v17_contrastive.py` and `train_v19_mstcn_contrastive.py` → different families (`train_contrastive` vs `train_mstcn_contrastive`). 

  By design, this **may over-split** semantically-related chains. The L3 interview
  asks the user whether to merge them via `family_aliases.json` (planned).

## Debugging tips

- Run `python -m scripts.parse_filename` interactively (REPL) to test individual stems.
- If a file is mis-classified, add it to the `pytest.parametrize` block in
  `tests/test_parse_filename.py` first, watch it fail, then patch the regex.

## Future: family_aliases.json

When ready, drop a file at `<project>/.weekly_report/family_aliases.json`:

```json
{
  "train_mstcn_contrastive": "train_contrastive",
  "train_supcon_v3":         "train_contrastive"
}
```

The differ reads this and rewrites family_key on the fly. No regex changes needed.
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/version-chain-heuristic.md
git commit -m "docs(version-chain): worked examples + future aliases plan"
```

---

### Task 22: Create references/metric-vocab-guide.md

**Files:**
- Create: `weekly_report/references/metric-vocab-guide.md`

- [ ] **Step 1: Write the metric vocab guide**

```markdown
# Metric Vocabulary Guide

This guide explains what `metric_vocab.json` is, how the first-time labeling
form works, and how to maintain it.

## What is metric_vocab.json

A per-project file at `<project>/.weekly_report/metric_vocab.json` that
classifies every numeric JSON top-level key into one of four categories:

| Category | Meaning |
| --- | --- |
| metric | Reported in weekly comparison tables (e.g. `track_acc`) |
| config | Experiment setup, not compared (e.g. `seed`, `backbone`) |
| ignored | Numeric but not interesting (e.g. `_internal_id`) |
| unknown | Not yet classified — pending user confirmation |

## First-time labeling

When you run `/weekly-report init <project>`, the skill scans every output JSON
in your project, applies hint-based heuristics (any key containing `acc/loss/f1/auc/...`
becomes a metric candidate), and writes the unresolved keys to
`metric_vocab_init.md`:

```markdown
### track_mean_per_seed
- 上下文：在 Forecasting/output/inference_results.json 中，与 seeds=[1..10] 同时出现
- 自动猜测：metric / aggregate of track_acc
- [ ] 是指标，方向 higher_better
- [ ] 是指标，方向 lower_better
- [ ] 是配置（不参与对比）
- [ ] 忽略
```

You check ONE box per key. Estimated time: 30 keys × 30 seconds = 5–10 minutes.

The skill parses your filled `metric_vocab_init.md` and writes the result to
`metric_vocab.json`. From this point on, the same keys are classified
automatically.

## Direction (higher_better vs lower_better)

For metrics, you must specify a direction:

- `higher_better`: accuracy, F1, AUC, IoU, recall, precision, BLEU
- `lower_better`: loss, error, MAE, RMSE, perplexity

This drives the sign of the "delta" column in the weekly comparison table:
- `track_acc 0.928 → 0.942` shows `+1.4%` (good, green).
- `loss 0.21 → 0.18` shows `−14%` (good, green) ONLY if direction is `lower_better`.

## Adding new keys later

Every weekly run, if the skill encounters a numeric key not in `metric_vocab.json`,
it does NOT silently include it. Instead:

1. The new key goes into `manifest.new_unknown_metrics`.
2. The interview.md ⑥ section asks you to classify it (same checkbox layout).
3. The weekly report flags `本周新增 N 个待确认指标，已写入问卷`.
4. Once you submit, the key is appended to `metric_vocab.json`.

This means the vocab grows incrementally without you ever having to re-do the
full first-time labeling.

## Manual editing

You can edit `metric_vocab.json` directly when needed:

```json
{
  "schema_version": "1.0",
  "project_name": "radar_target_recognition",
  "last_updated": "2026-05-04",
  "metrics": {
    "track_acc":        {"category": "metric", "direction": "higher_better"},
    "fusion_track_acc": {"category": "metric", "direction": "higher_better",
                         "aggregate_of": "track_acc"}
  },
  "config_keys": {
    "seed":     {"category": "config"},
    "backbone": {"category": "config"}
  },
  "ignored_keys": ["_run_id"],
  "stat_aggregates": ["_mean", "_std", "_ci_95"]
}
```

Re-run the skill — changes pick up immediately.

## Common patterns from radar_target_recognition

```json
"track_acc":        higher_better
"seg_acc":          higher_better
"fusion_track_acc": higher_better, aggregate_of: track_acc
"phase1_val_acc":   higher_better, group: phase1
"track_acc_mean":   stat_aggregate of track_acc — auto-handled
"seed":             config
"backbone":         config
"n_test_tracks":    config (count, not metric)
```
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/metric-vocab-guide.md
git commit -m "docs(metric-vocab): first-time labeling + incremental flow"
```

---

### Task 23: Create references/project-toml-reference.md

**Files:**
- Create: `weekly_report/references/project-toml-reference.md`

- [ ] **Step 1: Write the toml reference**

```markdown
# project.toml Field Reference

Every project has a `project.toml` at `<project>/.weekly_report/project.toml`.
It is auto-generated by `init_project.py` on the first run, but you should
review and edit it.

## Top-level structure

```toml
[project]                 # project metadata
[buckets.code]            # what to scan for source code
[buckets.experiment_data] # output/results JSONs
[buckets.paper]           # paper drafts
[buckets.reading]         # papers being read
[buckets.theory]          # theory/derivation notes
[buckets.figures]         # figures used in reports
[checkpoint_signal]       # training checkpoint heuristics
[metrics]                 # metric vocab settings
[scanner]                 # global ignore + scanner tuning
```

## [project]

| Field | Required | Default | Notes |
| --- | --- | --- | --- |
| name | yes | dirname | Used in manifest, must match dir name |
| display_name | yes | name | Shown in report title |
| short_name | yes | name | Used in aggregate filename `<date>_W<n>_<short>.md` |
| domain | no | "" | One-line domain description for baseline report §1 |
| advisor | no | "老师" | Used in greeting block |
| advisor_title | no | "老师" | If different from `advisor` (e.g., "陈老师") |
| student | no | "" | Signature in closer |
| phd_year | no | 1 | Influences baseline roadmap horizon |
| semester | no | auto | "春季"/"秋季", auto from current month |

## [buckets.{bucket_name}]

| Field | Notes |
| --- | --- |
| roots | List of glob-style paths relative to project_root. `**` means any depth. |
| ignore | Per-bucket ignore overrides; merged with `scanner.exclude_globs_global`. |
| include_extensions | List of extensions to keep within roots. |

### Bucket-specific extras

`buckets.code`:
- `content_diff_size_kb` (default 200) — files larger than this skip content diff.
- `sha1_for_content_diff` (default true)

`buckets.experiment_data`:
- `extract_metrics` (default true)

`buckets.paper`:
- `section_diff` (default true) — extract H1/H2/H3 changes

`buckets.theory`:
- `detect_math_in_paper` (default true) — also scan paper bucket .md/.tex
- `section_diff` (default true)

`buckets.figures`:
- `sample_strategy` (newest_3 / by_family / all)
- `max_per_report` (default 5)
- `max_size_mb` (default 5)

## [checkpoint_signal]

```toml
[checkpoint_signal]
enabled = true
roots = ["*/checkpoint", "*/weights_*"]
filename_patterns = [
  '_acc_(?P<acc>[\d.]+)',
  '_epoch_?(?P<epoch>\d+)',
  '_seed_?(?P<seed>\d+)',
  '_loss_(?P<loss>[\d.]+)',
]
ignore_content = true   # NEVER read .pt/.pth/.ckpt content
```

`active_window_days` is NOT here — it's prompted at runtime each weekly run.

## [metrics]

```toml
[metrics]
hint_tokens_extra = []      # add domain hints e.g. "track", "seg", "fusion"
config_keys_extra = []      # add config hints e.g. "rcs_mode"
multi_seed_aggregate = true
ci_field = "ci_95"
```

## [scanner]

```toml
[scanner]
exclude_globs_global = [...]   # See default-project.toml
follow_symlinks = false
include_hidden = false
metadata_only_size_mb = 10     # files larger than this skip sha1
```

## Editing best practices

1. After init, OPEN this file and review `roots` for each bucket — auto-detection
   is heuristic and may miss your custom dir names.
2. If your project has `core/`, `src/`, etc., add them to `buckets.code.roots`.
3. If `output/` is split between Forecasting/output and hardware/output, list both:
   `roots = ["Forecasting/output", "hardware/output"]`.
4. After editing, re-run `/weekly-report run`. Changes are picked up immediately.

## Multi-project setup

Each project has its OWN `.weekly_report/project.toml`. They are completely
independent — `metric_vocab.json`, `family_aliases.json`, history are all
per-project.
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/project-toml-reference.md
git commit -m "docs(project-toml): full field reference"
```

---

### Task 24: Create references/theory-extraction-rules.md

**Files:**
- Create: `weekly_report/references/theory-extraction-rules.md`

- [ ] **Step 1: Write the rules**

```markdown
# Theory Extraction Rules

`theory_extractor.py` extracts math blocks from .md/.tex files. This document
describes what counts as a "math block" and how the extractor handles edge cases.

## Recognized formats

1. **Display dollar**: `$$...$$` — `kind = display_dollar`
2. **Inline parenthesis**: `\(...\)` — `kind = inline_paren`
3. **Equation environment**: `\begin{equation}...\end{equation}` — `kind = equation_env`

## Not recognized (yet)

- `$...$` (inline single dollar) — too noisy, false-positive on `$1.99`
- `\[...\]` (display bracket) — rare; can be added in a future version
- `\begin{align}`, `eqnarray`, etc. — not crucial for weekly diff

## Skipped contexts

The extractor strips fenced code blocks (```` ``` ```` ... ```` ``` ````) before
scanning so equations inside a code block are not picked up.

## Section attribution

Each block is associated with the most recent markdown heading (`#`/`##`/`###`)
preceding it. If no heading exists, `section = None`.

## Diff between weeks

`compute_diff` compares blocks by `(file, body)` tuples:
- New `(file, body)` not seen last week → `math_blocks_added`
- Old `(file, body)` not seen this week → `math_blocks_deleted`
- Same `(file, _)` but different body in same `section` → `math_blocks_modified`

## Limitations

- Whitespace normalization is naïve. `$$x = y$$` and `$$x=y$$` are treated as
  different bodies. Acceptable for now since LLM Writer can dedupe semantically.
- LaTeX comments (`% ...`) inside an equation block are kept verbatim.

## Why theory matters in weekly reports

Pure code/data diff misses the most valuable PhD output: when you derive a new
equation, prove a lemma, or formalize a method, that goes in `.md` or `.tex` text,
not in code. The theory bucket exists so the weekly report doesn't miss this layer.

The sample weekly report (`2026春-3月第1周报-李越.docx`) demonstrates this:
section "PhaseAmp相位保留方法总结" contains formula derivations like
`|mean(exp(jφ))|` that wouldn't show up in any code/data diff.
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/theory-extraction-rules.md
git commit -m "docs(theory): extraction rules + radar example"
```

---

### Task 25: Create references/faq.md

**Files:**
- Create: `weekly_report/references/faq.md`

- [ ] **Step 1: Write the FAQ**

```markdown
# FAQ

## 第一次跑要多久？

约 5–15 分钟，主要时间在 metric_vocab 标注（30 个 key × 30 秒）。
Scanner 本身 < 1 分钟。

## 我每周不固定时间汇报，怎么办？

Skill 每次跑都会问 `active_window_days`，默认 7 天但可以输入 1-30 天的任意值。
你可以一周跑两次（输入 3 天），也可以两周跑一次（输入 14 天）。

## 工程目录里有几十 GB 的训练数据，会不会卡？

不会。Scanner 对 `*.mat / *.npy / *.pt / *.pth / *.ckpt` 默认 metadata-only，
不读内容、不算 sha1。71315 个数据文件实测扫描 < 30 秒。

## 我改了 `metric_vocab.json` 里的 direction，要重跑 init 吗？

不用。下次 `/weekly-report run` 自动生效。

## 周报不准怎么办？

按以下顺序排查：
1. 看 `manifest.json` 的 `anomalies` 字段——命名异常会被 flag。
2. 看 `diff.json` 的 `version_chains_advanced`——版本链是否识别正确。
3. 看 `metric_vocab.json`——是否有指标被错分到 config。
4. 看 `interview.md`——是否漏填了关键问题。

## 我的工程不是这个"PhD 雷达项目"格式，能用吗？

可以。`project.toml` 里的 `buckets.*.roots` 全部由你自己配。
init 模式会基于子目录名自动猜，你审一遍即可。
默认覆盖了：`Forecasting/`, `output/`, `paper_writing/`, `research-wiki/` 等常见命名。

## 我有多个项目（雷达 + 论文 + 别的），会不会串？

每个项目独立 `.weekly_report/`，metric_vocab、history、family_aliases 全部
per-project。汇总文件在 `D:\code\reports\<year>\<month>\` 按 short_name 区分。

## 漏写了一周怎么办？

下次跑时，skill 自动拿最近一份可用 manifest 做对比。中间漏掉的周不会被填补，
但会在 anomalies 里记录"跨周缺失检测"。

## 命名异常（如 `Final_inference_final.py`）怎么修？

skill 不会自动改文件名（红线：禁止改用户工程）。你手动改文件名后，
下次扫描自动正常归类。或者在 `family_aliases.json` 里加一条别名映射：
```json
{ "Final_inference_final": "inference" }
```

## Skill 会写到我工程目录吗？

只写到 `<project>/.weekly_report/` 与 `D:\code\reports\`。其他位置的写操作
会被 `path_guard.py` 拦截并报错。这是硬红线。

## 怎么把 skill 给师弟师妹？

1. 把 `D:\code\github_skill\weekly_report\` 整个目录拷给他。
2. 让他放到 `~/.claude/plugins/` 下。
3. 让他打开 README.md 跟着 quickstart 跑一遍。
4. 第一次跑时他自己的 `metric_vocab.json` 会基于他的项目重新生成，跟你的不串。

## skill 报"路径白名单越界"怎么办？

说明 skill 内部逻辑试图写到工程目录。这是 BUG，请贴堆栈信息回报。
临时解决：手动 fork skill，放宽 `path_guard.is_write_allowed` 中的判断（不推荐）。

## metric_vocab.json 弄丢了会怎样？

下次 init 重做一次（5–10 分钟）。或者手动复制一份 backup 文件。
这个文件不大（几 KB），建议 gitignore 之外另作备份。
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/references/faq.md
git commit -m "docs(faq): common questions + troubleshooting"
```

---

### Task 26: Refresh references/input-guide.md and references/writing-rules.md

**Files:**
- Modify: `weekly_report/references/input-guide.md` (trim, refer to interview)
- Modify: `weekly_report/references/writing-rules.md` (keep as-is mostly)

- [ ] **Step 1: Replace input-guide.md content**

```markdown
# 输入整理指南

When the user gives raw, scattered input INSTEAD of a clean interview.md,
this guide tells the LLM how to triage it.

## 常见原始输入

- 一段口语化的描述（"这周做了 X、Y、Z，但 Z 卡住了"）
- 聊天截图 / 笔记 / 待办列表
- 邮件内容
- 含 TODO / FIXME 的代码注释

## 整理步骤

1. **先把内容拆成原子事项**——"做了 v25→v26 的 stacking 改进"是一条；
   "RD 模型在 seed=3 上崩了"是一条。
2. **将每条归类**：
   - 已完成
   - 推进中
   - 风险 / 阻塞
   - 下周计划
3. **跟 manifest/diff 对照**——如果用户说"做了 X"但 manifest 里没看到 X
   相关的 file diff，要提示用户："系统未检测到对应文件改动，是否漏配 bucket roots？"
4. **统一到周报模板**——按第 10 节模板填空，不要扩展新结构。

## 整理规则

### 1. 同类事项先合并

如果多条记录在说同一件事（"换了 stacking 头" + "改了 fusion loss"），
若它们在同一个 family_key 下，合并成"实验链推进"一条；不同则分开。

### 2. 先抓动作，再抓结果

优先识别：
- 代码做了什么改变
- 与上周相比推进了什么
- 交付了什么结果
- 解决了什么问题
- 卡在什么地方

### 3. 没完成的不算完成

"已完成"必须有可验证标志（数字、文件、章节）。否则改写为
"已推进到 X 阶段"。

### 4. 很碎的小事要归并

不要写"改了标题/改了封面/调了排版"逐条；写
"完成第三章版式优化"。

### 5. 信息不足时先补问题

最少必要信息：
- 这周最重要的 2-3 件事？
- 哪件已完成、哪件推进中？
- 有没有要让老师知道的风险？
- 下周最明确的计划？

如缺，把问题列入 interview.md 让用户补，不要硬写。
```

- [ ] **Step 2: Verify writing-rules.md still aligned**

Read existing `weekly_report/references/writing-rules.md`. Keep it (already good).
Add this paragraph at the end:

```markdown
## 风格对齐：参考样例

样例文件：`D:\code\github_skill\2026春-3月第1周报-李越.docx`。
关键风格点：
- 开场段不超过 3 句，列出本周主要工作 1-3 项
- 每个主要工作有"实验背景与目的 / 方法 / 实验结果 / 关键发现"四节
- 实验结果优先用表格 + mean ± std + 95% CI
- 理论方法单独成节，含公式块
- 结尾固定"祝您工作顺利，身体健康！"+ 学生签名 + 日期斜杠格式
```

- [ ] **Step 3: Commit (optional)**

```bash
git add weekly_report/references/input-guide.md weekly_report/references/writing-rules.md
git commit -m "docs(refs): refresh input-guide; add style reference to writing-rules"
```

---

## Phase 10: Top-Level SKILL.md and README.md

### Task 27: Rewrite SKILL.md as the orchestration entry point

**Spec ref:** §12 SKILL.md 主流程伪代码

**Files:**
- Modify: `weekly_report/SKILL.md`

- [ ] **Step 1: Read existing SKILL.md to preserve frontmatter intent**

Run: `cat weekly_report/SKILL.md | head -10`
Expected: name and description fields present.

- [ ] **Step 2: Replace SKILL.md content**

```markdown
---
name: weekly-report-writer
description: PhD 学生周报全自动生成 skill。扫描工程目录、对比上周快照、半自动归并版本链与指标、L3 质询补语义、输出含问候语和结束祝福的 PhD 风格周报 markdown。当用户说"写周报"、"导师汇报"、"weekly report"、"本周做了什么"、"梳理工程进展"、"baseline 总报告"或类似表达时，必须使用此 skill。覆盖代码 / 实验数据 / 论文 / 阅读 / 理论公式 / 配图六类。支持多项目隔离、跨年月归档、师弟师妹零门槛复用。
---

# Weekly Report Writer

## 何时使用

- 用户要写每周给导师的周报
- 用户工程文件多到记不清，需要工具梳理
- 用户要做项目阶段性 baseline 总报告
- 用户希望把零散口语描述整理成结构化周报

## 何时不使用

- 用户要 PPT、论文初稿、grant proposal（用对应 skill）
- 用户希望从外部系统抓数据（Slack / 邮件 / Issue）—— 本 skill 仅扫工程目录
- 用户提供的信息明显不足，先质询而非硬写

## 红线（不可破）

🚫 **本 skill 严禁修改用户工程代码**。仅向 `<project>/.weekly_report/` 与 `D:\code\reports\` 写入。
所有写操作经 `scripts/path_guard.py` 守卫。一旦触发越界写，必须立即报错而不是覆盖。

## 入口指令

| 指令 | 行为 |
| --- | --- |
| `/weekly-report init <project_path>` | 首跑：自动检测 buckets → 生成 project.toml → metric_vocab 标注 → baseline 总报告 |
| `/weekly-report run [--project <path>]` | 增量：扫描 → diff → interview → 周报 |
| `/weekly-report rebase --week <id>` | 重建指定周（找回老周报） |

## 工作流程

### 1. 探测模式
- 检查 `<project>/.weekly_report/project.toml` 是否存在
- 不存在 → baseline 模式（走 init 流程）
- 存在但无历史周 → 仍按 baseline 模式
- 存在且有历史周 → incremental 模式

### 2. 运行时询问（每次必问）
- 问：「本次汇报覆盖的时间窗口是？」
  - 默认：上次跑到现在 / 7 天
  - 可选：自定义 N 天（1–30）/ 指定起止日期
- 此值即 active_window_days，用于 checkpoint_signal、figures、新增文件的 mtime 过滤
- 若上次跑距今 < 3 天，提示「距上次跑较近，确认要再写一次？」

### 3. Scanner 阶段
调用 `scripts/scan_project.py`：ThreadPool 并发，max_workers = `min(8, len(roots) * 2)`。
产出 `<week>/manifest.json`。

### 4. Diff 阶段
（仅 incremental）调用 `scripts/compute_diff.py`，对比上周 manifest。
产出 `<week>/diff.json`。

### 5. 配图与理论
- 调用 `scripts/figure_picker.py` 选候选图
- 调用 `scripts/theory_extractor.py` 抽 math 块
- 结果写入 manifest 与 diff 对应字段

### 6. Interview 阶段
调用 `scripts/interview_generator.py`，产出 `<week>/interview.md`。
提示用户：「请打开 `<week>/interview.md` 填写，填完告知。」

### 7. 等用户填完后
读取填好的 interview.md，调用 `scripts/parse_interview.py` → `interview_parsed.json`。

### 8. Writer 阶段
基于 manifest + diff + interview_parsed，按 `assets/weekly-report-template.md`
（incremental）或 `assets/baseline-report-template.md`（baseline）合成 `report.md`。

格式参考样例 `D:\code\github_skill\2026春-3月第1周报-李越.docx`：
- 开头 `**学期周序周报**` + 问候语 + 开场段
- 主要工作按 H1 分节（实验背景/方法/结果/分析）
- 表格 mean ± std + 95% CI
- 理论方法单独成节，含公式块
- 配图嵌入相对路径
- 结尾"祝您工作顺利，身体健康！"+ 签名 + 日期斜杠

详见 `references/greeting-templates.md` 与 `references/writing-rules.md`。

### 9. 落档
- 周报：`<project>/.weekly_report/<year>/<month>/<week>/report.md`
- Manifest/diff/interview/interview_parsed.json/images/ 同目录
- 副本：`D:\code\reports\<year>\<month>\<date_range>_W<n>_<short_name>.md`
- 调用 `scripts/update_index.py` 更新 `D:\code\reports\index.md`
- 写 `<project>/.weekly_report/latest.txt` 指针

### 10. 自检
LLM 读一遍 report.md，检查：
- 是否有空段
- 是否流水账（每条事项有"做了什么 / 做到什么程度 / 影响"）
- 是否漏 ask
- 是否漏配图（本周有候选图但 report 中没引用）
- 是否漏公式（theory 有新增但 report 中没体现）

## 写作原则
- 周报不是日记，要归纳
- 周报不是邀功表，要边界
- 周报不是任务列表照抄，要轻度提炼
- 一条事项尽量写清：做了什么、做到什么程度、产生了什么结果

## 默认行为
- 输入碎片化时先质询
- 同一件事重复出现时区分细节后再写
- 一项工作只有过程没结果时写"推进到 X 阶段"
- 信息不足时列出最少必要补充问题

## 关键参考文件

| 文件 | 用途 |
| --- | --- |
| `references/greeting-templates.md` | 开头问候 + 结束祝福格式 |
| `references/writing-rules.md` | 写作风格规则 |
| `references/version-chain-heuristic.md` | family_key 算法 |
| `references/metric-vocab-guide.md` | metric_vocab 维护 |
| `references/project-toml-reference.md` | project.toml 字段 |
| `references/baseline-roadmap-prompt.md` | baseline 路线图 prompt |
| `references/theory-extraction-rules.md` | 理论 / 公式抽取 |
| `references/input-guide.md` | 处理零散输入 |
| `references/faq.md` | 常见问题 |

## 输出要求
- 结构清晰，导师可快速扫读
- 优先写结果、进展和影响
- 避免口语和情绪化表达
- 未完成事项写清当前进展和下一步，不假装完成
- 风险 / 下周计划如缺信息，要审慎补齐或明确说"信息不足"

## 调试 / 故障排除
- 路径白名单越界 → `scripts/path_guard.py` 拦截，看堆栈定位写源
- 版本链拆得过细 → 在 `<project>/.weekly_report/family_aliases.json` 加别名
- 指标分类不准 → 编辑 `<project>/.weekly_report/metric_vocab.json`
- 扫描慢 → 检查 `project.toml [scanner]` 的 max_workers / metadata_only_size_mb
```

- [ ] **Step 3: Verify SKILL.md is < 300 lines**

```bash
wc -l weekly_report/SKILL.md
```

Expected: < 300 (target ~200).

- [ ] **Step 4: Commit (optional)**

```bash
git add weekly_report/SKILL.md
git commit -m "feat(SKILL): orchestration entry-point with init/run/rebase modes"
```

---

### Task 28: Create README.md (师弟师妹 onboarding)

**Spec ref:** §13 README.md

**Files:**
- Create: `weekly_report/README.md`

- [ ] **Step 1: Write the README**

```markdown
# Weekly Report Writer

> A Claude Code skill for PhD students: scans your project, diffs vs last
> week, asks you a short L3 questionnaire, and writes the advisor weekly report.

## Why use this

PhD work generates code, experiment data, paper drafts, theory derivations,
and figures faster than you can remember. By Friday, you're staring at
50 file changes asking "what did I actually do this week?".

This skill answers that for you. It scans your project directory, compares
to last week's snapshot, identifies advanced version chains (e.g. v25→v26),
extracts metric changes (mean ± std across seeds), surfaces new equations
in your theory notes, and asks you only what it cannot infer. Then it
writes a structured advisor-ready weekly report.

## What it produces

- `<project>/.weekly_report/<year>/<month>/<week>/report.md` — the report
- `D:\code\reports\<year>\<month>\<date_range>_W<n>_<short>.md` — aggregate copy
- `D:\code\reports\index.md` — cross-project index, all weeks listed

The report follows a PhD format: greeting, opening paragraph, major-work
sections with experiment results tables (mean ± std + 95% CI), theory blocks
with equations, embedded figures, week summary, next-week plan, asks for
advisor, closing wishes, signature, date range.

## Quickstart (first time, 10 minutes)

```bash
# 1. Init your project
/weekly-report init D:\code\my_phd_project

# Skill will:
#   - Scan to detect bucket roots (code/data/paper/...)
#   - Show you a draft project.toml — review it
#   - Walk all output JSONs to harvest metric keys
#   - Open metric_vocab_init.md asking you to classify ~30 keys
#     (one checkbox per key, 30s each)

# 2. Generate baseline total report
/weekly-report run

# Skill will:
#   - Open interview.md asking you ~5 questions about high-level direction
#   - Generate a 10-section baseline report including a 3-month roadmap
```

## Weekly use (after init, 5 minutes)

```bash
/weekly-report run

# 1. Skill asks: "active window? default 7 days"
# 2. Scans project (< 30s for ~70k data files)
# 3. Diffs vs last week
# 4. Opens interview.md with 5-9 sections (only the ones with content)
# 5. You fill the **请填**: blanks (5-10 minutes total)
# 6. Skill writes report.md
```

## What it scans

| Bucket | Default roots | What's tracked |
| --- | --- | --- |
| code | Forecasting/, hardware/, src/ | .py / .cpp / .h, version chains |
| experiment_data | */output, */results | .json metrics, multi-seed agg |
| paper | paper_writing/ | .tex / .md / .docx, section diff |
| reading | research-wiki/, docs/ | .md / .pdf, new papers |
| theory | theory/, derivations/ | math blocks ($$, \(\), equation env) |
| figures | */ppt_figures, */figs | .png / .svg / .pdf, embedded in report |
| checkpoint_signal | */checkpoint, */weights_* | filename regex (acc/epoch/seed) only |

## What it does NOT do

🚫 NEVER modifies your project code. Only writes to `.weekly_report/` and `D:\code\reports\`.

- Does not parse `git log` (works without git)
- Does not read training checkpoint contents (file names only)
- Does not access external systems (Slack/email/issues)
- Does not do AST-level code diff

## Configuration

Edit `<project>/.weekly_report/project.toml` after init. Full field reference
in `references/project-toml-reference.md`. The most common things you'd change:

- `[buckets.code] roots = [...]` — add your custom code dirs
- `[project] advisor = "陈老师"` — used in greeting
- `[project] student = "李越"` — used in signature
- `[buckets.figures] max_per_report = 5` — figure cap

## Maintaining `metric_vocab.json`

When the skill encounters a numeric JSON key it has never seen, it asks you to
classify (metric / config / ignore). Each classification is 30 seconds and
saved permanently. Direct edits to `metric_vocab.json` are also fine.

See `references/metric-vocab-guide.md` for details.

## Multi-project

Each project has its own `.weekly_report/`. They never share state. Run init
once per project. Reports go into the same `D:\code\reports\` aggregate
folder, organized by year/month.

## Sharing with your peers (师弟师妹)

```bash
# Copy the entire skill folder
cp -r D:\code\github_skill\weekly_report ~/.claude/plugins/

# Have them open this README.md and run init on their project.
# Their metric_vocab.json will be regenerated against their project.
```

The skill is project-agnostic — peer's project.toml will be different from
yours. Bucket roots, advisor name, metrics — all separate.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Scan extremely slow | Too many ckpt files in `roots` | Move ckpt dir under `checkpoint_signal.roots` only |
| Report missing my changes | Bucket root not configured | Add to `project.toml [buckets.code] roots` |
| Wrong metric in comparison table | metric_vocab miscategorized | Edit `metric_vocab.json` |
| Path whitelist error | Skill bug | File issue with stack trace |
| Version chain over-split | Heuristic too narrow | Add to `family_aliases.json` |

See `references/faq.md` for more.

## Architecture

```
SKILL.md (orchestrator, LLM-driven)
   ↓
scripts/ (deterministic Python)
   ├── scan_project.py      # ThreadPool walker
   ├── compute_diff.py      # cross-week diff
   ├── extract_metrics.py   # JSON metric extraction
   ├── parse_filename.py    # version chain heuristic
   ├── theory_extractor.py  # math block scanner
   ├── figure_picker.py     # figure candidate selection
   ├── interview_generator.py  # interview.md producer
   ├── parse_interview.py   # questionnaire parser
   ├── init_project.py      # auto-detect + project.toml scaffold
   ├── update_index.py      # cross-project index.md
   ├── metric_vocab.py      # vocab IO
   ├── path_guard.py        # write-whitelist enforcer
   ├── ignore_rules.py      # glob ignore matcher
   ├── file_metadata.py     # single-file inspector
   └── bucket_classifier.py # path → bucket
   ↓
references/ (LLM context)
assets/ (templates)
```

## License & Credit

Internal lab tool. Maintain in your group's git repo. Iterate together.
Credit when sharing publicly.
```

- [ ] **Step 2: Verify**

```bash
wc -l weekly_report/README.md
ls -la weekly_report/README.md
```

Expected: ~150 lines, file exists.

- [ ] **Step 3: Commit (optional)**

```bash
git add weekly_report/README.md
git commit -m "docs(README): user-facing onboarding for peers"
```

---

### Task 29: Create scripts/README.md

**Files:**
- Create: `weekly_report/scripts/README.md`

- [ ] **Step 1: Write the scripts README**

```markdown
# scripts/ Module Map

Deterministic Python helpers used by SKILL.md. Each is single-purpose,
testable in isolation, no LLM calls.

| Script | Purpose | Tested? |
| --- | --- | --- |
| `parse_filename.py` | Extract family/version/status from file stems | ✅ |
| `path_guard.py` | Enforce write whitelist (red line) | ✅ |
| `ignore_rules.py` | Glob-based file ignore matcher | ✅ |
| `file_metadata.py` | Per-file size/mtime/sha1 inspector | ✅ |
| `bucket_classifier.py` | Map relative path → bucket name | ✅ |
| `scan_project.py` | ThreadPool walker → manifest.json | ✅ |
| `extract_metrics.py` | JSON metric/config classifier + multi-seed agg | ✅ |
| `metric_vocab.py` | Read/write metric_vocab.json | ✅ |
| `theory_extractor.py` | Extract $$/\(\)/equation env blocks | ✅ |
| `figure_picker.py` | Select figure candidates by mtime + size + window | ✅ |
| `compute_diff.py` | Cross-week manifest diff | ✅ |
| `interview_generator.py` | Render interview.md from diff | ✅ |
| `parse_interview.py` | Parse filled interview.md → JSON | ✅ |
| `init_project.py` | Auto-detect buckets + render project.toml | ✅ |
| `update_index.py` | Maintain cross-project index.md | ✅ |

## Running tests

```bash
cd D:/code/github_skill/weekly_report
python -m pytest scripts/tests -v
```

All tests use `pytest` and tmp directories. No real project data is touched.

## Inter-script dependencies

```
SKILL.md
  └── scan_project.py
        ├── ignore_rules.py
        ├── file_metadata.py
        ├── bucket_classifier.py
        └── parse_filename.py

  └── compute_diff.py            (no script deps; pure data)

  └── extract_metrics.py         (no script deps)

  └── metric_vocab.py            (no script deps)

  └── interview_generator.py     (no script deps)

  └── parse_interview.py         (no script deps)

  └── theory_extractor.py        (no script deps)

  └── figure_picker.py           (no script deps)

  └── init_project.py            (no script deps)

  └── update_index.py            (no script deps)

  └── path_guard.py              (used by all that write)
```

## Adding a new script

1. Write `scripts/<name>.py` with module docstring linking to spec section.
2. Write `scripts/tests/test_<name>.py` with 3+ realistic cases.
3. Update this table.
4. Wire into `SKILL.md` workflow if user-facing.
```

- [ ] **Step 2: Commit (optional)**

```bash
git add weekly_report/scripts/README.md
git commit -m "docs(scripts): module map + testing notes"
```

---

## Phase 11: End-to-End Smoke Test

### Task 30: Dry-run Scanner against radar_target_recognition (read-only)

**Files:**
- No new files. Smoke test only.

- [ ] **Step 1: Set up a temporary CLI driver for the scanner**

Create `weekly_report/scripts/_smoke_scan.py` (will not be committed; just for the test):

```python
"""Throwaway smoke runner — DO NOT commit."""
import json
import time
from pathlib import Path
from scripts.scan_project import scan_project, ScanConfig

cfg = ScanConfig(
    project_root=Path(r"D:\code\radar_target_recognition"),
    buckets={
        "code": {"roots": ["Forecasting","hardware","Preprocess","feature_fusion_forecasting"],
                 "exts": [".py"]},
        "experiment_data": {"roots": ["Forecasting/output","Forecasting/results"],
                            "exts": [".json"]},
        "paper": {"roots": ["paper_writing"], "exts": [".md",".tex",".docx"]},
        "reading": {"roots": ["research-wiki","docs"], "exts": [".md",".pdf"]},
        "theory": {"roots": [], "exts": [".md",".tex"]},
        "figures": {"roots": ["**/ppt_figures","**/results"], "exts": [".png",".jpg",".svg",".pdf"]},
        "checkpoint_signal": {"roots": ["**/checkpoint","**/weights_*"],
                              "exts": [".pt",".pth",".ckpt"]},
    },
    global_ignores=[
        "__pycache__/**","*.pyc",".pytest_cache/**",
        "dist/**","build_tmp/**",".idea/**",".vscode/**",
        "*~","*_tmp.*","*_temp.*",
        ".weekly_report/**",
        "raw_data/**","dataset/**","*.mat","*.npy","*.h5",
    ],
    project_ignores=[],
    metadata_only_size_mb=10,
    max_workers=8,
)

t0 = time.time()
manifest = scan_project(cfg)
print(f"Scan duration: {time.time() - t0:.1f}s")
print(f"buckets: { {k: len(v.get('files',[])) for k,v in manifest['buckets'].items()} }")
print(f"version_chains: {len(manifest['buckets']['code'].get('version_chains',{}))}")
print(f"anomalies: {len(manifest['anomalies'])}")
```

- [ ] **Step 2: Run the smoke scan**

```bash
cd D:/code/github_skill/weekly_report
python -m scripts._smoke_scan
```

Expected output:
```
Scan duration: <60s>
buckets: {'code': ~331, 'experiment_data': ~tens, 'paper': >0, 'reading': >0, 'theory': 0, 'figures': ~tens, 'checkpoint_signal': ~tens, 'uncategorized': ~few}
version_chains: ~30+
anomalies: ~few
```

- [ ] **Step 3: Verify NO writes happened to radar_target_recognition outside .weekly_report**

```bash
cd D:/code/radar_target_recognition
git status 2>&1 || echo "(not a git repo)"
ls -la | head -20
```

Expected: no new top-level files, file mtimes preserved.

- [ ] **Step 4: Inspect a sample of detected version_chains**

```bash
python -c "
from scripts.scan_project import scan_project, ScanConfig
from pathlib import Path
cfg = ScanConfig(project_root=Path(r'D:\\code\\radar_target_recognition'),
                 buckets={'code':{'roots':['Forecasting'],'exts':['.py']},
                          'experiment_data':{'roots':[],'exts':[]},
                          'paper':{'roots':[],'exts':[]},
                          'reading':{'roots':[],'exts':[]},
                          'theory':{'roots':[],'exts':[]},
                          'figures':{'roots':[],'exts':[]},
                          'checkpoint_signal':{'roots':[],'exts':[]}},
                 global_ignores=['__pycache__/**','.weekly_report/**'],
                 project_ignores=[],
                 metadata_only_size_mb=10,
                 max_workers=4)
m = scan_project(cfg)
chains = m['buckets']['code'].get('version_chains', {})
for k in list(chains)[:10]:
    print(k, chains[k])
"
```

Expected: rcs_stacking / rcs_fusion / monte_carlo_train / data_loader_complex / etc., each with sane versions list.

- [ ] **Step 5: Remove the smoke runner and run real tests**

```bash
rm weekly_report/scripts/_smoke_scan.py
python -m pytest weekly_report/scripts/tests -v
```

Expected: all tests still PASS.

---

## Phase 12: Self-Review

### Task 31: Spec coverage audit + final cleanup

**Files:**
- No code; review only.

- [ ] **Step 1: Cross-check each spec section has a task**

Open `docs/superpowers/specs/2026-05-04-weekly-report-writer-design.md` and mentally
check off each requirement against this plan. Expected mapping:

| Spec § | Task # |
| --- | --- |
| §1 红线 | Task 3 (path_guard) + SKILL.md (Task 27) |
| §3 目录布局 | Task 27 (落档逻辑) |
| §4 project.toml | Task 13 |
| §5 Manifest schema | Task 7 |
| §6 Scanner | Tasks 4-7 |
| §7 Differ | Task 12 |
| §8 Metric | Tasks 8-9 |
| §9 Interview | Tasks 14-15 |
| §10 Writer 模板 | Task 17 |
| §11 baseline | Task 18-19 |
| §12 Skill 文件结构 | All tasks |
| §13 README | Task 28 |
| §14 边界情况 | Distributed across tests |
| §15 性能预算 | Task 30 verifies |
| §16 取舍 | Reflected in tests |
| §17 验收标准 | Task 30 verifies |
| §19 metric_vocab 澄清 | Task 22 |

If any gap, add a task and re-run plan.

- [ ] **Step 2: Run the full test suite**

```bash
cd D:/code/github_skill/weekly_report
python -m pytest scripts/tests -v --tb=short
```

Expected: all PASS.

- [ ] **Step 3: Confirm file count expectations**

```bash
ls weekly_report/scripts/*.py | wc -l        # expect 15 (incl __init__)
ls weekly_report/scripts/tests/*.py | wc -l  # expect ~13 (incl __init__, conftest)
ls weekly_report/references/*.md | wc -l     # expect 8
ls weekly_report/assets/*.{md,toml} 2>/dev/null | wc -l  # expect 5
```

- [ ] **Step 4: Final commit (optional)**

```bash
git add -A
git commit -m "test: full suite pass, structure sealed for v1.0"
```

---

## Done

After all phases complete, the skill is ready for end-to-end LLM-driven testing.
That is, the user runs `/weekly-report init D:\code\radar_target_recognition`
and the orchestrator inside SKILL.md executes the full pipeline, producing
the first baseline report.

If anything in the LLM stage misbehaves (writer hallucinations, interview
mismatch), fix in-place: typically `assets/*.md` or `references/*.md`,
not Python.

The Python layer is intentionally deterministic and can be debugged by running
its tests in isolation.
