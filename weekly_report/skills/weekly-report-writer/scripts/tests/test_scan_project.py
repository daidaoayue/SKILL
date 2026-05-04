"""Tests for scan_project ThreadPool walker."""
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


def _empty_buckets():
    return {b: {"roots": [], "exts": []} for b in
            ("code","experiment_data","paper","reading","theory","figures","checkpoint_signal")}


def test_scan_basic_buckets(tmp_path: Path):
    proj = tmp_path / "proj"
    _make_realistic_tree(proj)
    cfg_buckets = _empty_buckets()
    cfg_buckets["code"]            = {"roots": ["Forecasting"],         "exts": [".py"]}
    cfg_buckets["experiment_data"] = {"roots": ["Forecasting/output"],  "exts": [".json"]}
    cfg_buckets["paper"]           = {"roots": ["paper_writing"],       "exts": [".md"]}

    cfg = ScanConfig(
        project_root=proj,
        buckets=cfg_buckets,
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
    cfg_buckets = _empty_buckets()
    cfg_buckets["code"] = {"roots": ["Forecasting"], "exts": [".py"]}
    cfg = ScanConfig(
        project_root=proj,
        buckets=cfg_buckets,
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
    cfg_buckets = _empty_buckets()
    cfg_buckets["code"] = {"roots": ["Forecasting"], "exts": [".py"]}
    cfg = ScanConfig(
        project_root=proj,
        buckets=cfg_buckets,
        global_ignores=[],
        project_ignores=[],
        metadata_only_size_mb=10,
        max_workers=2,
    )
    manifest = scan_project(cfg)
    assert manifest["schema_version"] == "2.0"
    assert manifest["scanner_version"] == "1.0"
    assert manifest["project_root"].endswith("proj")
    assert manifest["project_name"] == "proj"
    assert "scanned_at" in manifest
    assert "anomalies" in manifest


def test_latest_path_picks_highest_version_deterministically(tmp_path: Path):
    """latest_path must come from the file whose version sorts highest, not filesystem order."""
    proj = tmp_path / "proj"
    (proj / "Forecasting").mkdir(parents=True)
    # Intentionally write v26 BEFORE v25 to invert filesystem creation order
    (proj / "Forecasting" / "rcs_stacking_v26.py").write_text("# v26")
    (proj / "Forecasting" / "rcs_stacking_v25.py").write_text("# v25")
    (proj / "Forecasting" / "rcs_stacking_v5b.py").write_text("# v5b — sub-version letter")
    cfg_buckets = _empty_buckets()
    cfg_buckets["code"] = {"roots": ["Forecasting"], "exts": [".py"]}
    cfg = ScanConfig(
        project_root=proj, buckets=cfg_buckets,
        global_ignores=[], project_ignores=[],
        metadata_only_size_mb=10, max_workers=2,
    )
    manifest = scan_project(cfg)
    chain = manifest["buckets"]["code"]["version_chains"]["rcs_stacking"]
    assert chain["latest_path"] == "Forecasting/rcs_stacking_v26.py", (
        f"Expected v26 as latest, got {chain['latest_path']}; versions={chain['versions']}"
    )
    # versions list must be in natural sort order (v5b < v25 < v26)
    assert chain["versions"] == ["v5b", "v25", "v26"]


def test_scan_dedupes_files_visited_via_multiple_roots(tmp_path: Path):
    """If two bucket roots overlap, a file should appear once in the manifest."""
    proj = tmp_path / "proj"
    _make_realistic_tree(proj)
    cfg_buckets = _empty_buckets()
    # Both code roots cover Forecasting/output/* — but classifier puts the json under experiment_data
    cfg_buckets["code"]            = {"roots": ["Forecasting"],         "exts": [".py"]}
    cfg_buckets["experiment_data"] = {"roots": ["Forecasting"],         "exts": [".json"]}
    cfg = ScanConfig(
        project_root=proj,
        buckets=cfg_buckets,
        global_ignores=["__pycache__/**","*_tmp.*"],
        project_ignores=["raw_data/**"],
        metadata_only_size_mb=10,
        max_workers=4,
    )
    manifest = scan_project(cfg)
    all_paths = []
    for b in manifest["buckets"].values():
        all_paths.extend(f["path"] for f in b.get("files", []))
    assert len(all_paths) == len(set(all_paths)), f"duplicates: {all_paths}"
