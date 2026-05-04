"""Tests for compute_diff cross-week manifest diff."""
from scripts.compute_diff import compute_diff


def _mk_manifest(week, files, version_chains=None):
    bucket_names = ("code", "experiment_data", "paper", "reading",
                    "theory", "figures", "checkpoint_signal", "uncategorized")
    return {
        "week_id": week,
        "buckets": {
            **{
                "code": {
                    "files": [{"path": p, "sha1": h, "mtime": 1.0, "size": 1}
                              for (p, h) in files],
                    "version_chains": version_chains or {},
                },
            },
            **{b: {"files": []} for b in bucket_names if b != "code"},
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


def test_deletion_detected():
    last = _mk_manifest("W17", [("a.py","h1"), ("gone.py","h2")])
    this = _mk_manifest("W18", [("a.py","h1")])
    d = compute_diff(last, this)
    assert d["code"]["deleted_files"] == ["gone.py"]


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


def test_version_chain_no_change_omits_entry():
    last = _mk_manifest("W17",
        [("rcs_stacking_v26.py","h1")],
        version_chains={"rcs_stacking": {"versions":["v26"], "latest_path":"rcs_stacking_v26.py"}})
    this = _mk_manifest("W18",
        [("rcs_stacking_v26.py","h1")],
        version_chains={"rcs_stacking": {"versions":["v26"], "latest_path":"rcs_stacking_v26.py"}})
    d = compute_diff(last, this)
    assert d["code"]["version_chains_advanced"] == []


def test_deleted_family_flagged():
    last = _mk_manifest("W17",
        [("old_v1.py","h1")],
        version_chains={"old": {"versions":["v1"], "latest_path":"old_v1.py"}})
    this = _mk_manifest("W18", [], version_chains={})
    d = compute_diff(last, this)
    advanced = d["code"]["version_chains_advanced"]
    assert any(a["family"] == "old" and a["to"] is None for a in advanced)


def test_other_buckets_diff():
    last = _mk_manifest("W17", [])
    this = _mk_manifest("W18", [])
    last["buckets"]["paper"]["files"] = [
        {"path": "ch3.md", "sha1": "old", "mtime": 1.0, "size": 100}
    ]
    this["buckets"]["paper"]["files"] = [
        {"path": "ch3.md", "sha1": "new", "mtime": 2.0, "size": 200}
    ]
    d = compute_diff(last, this)
    assert d["paper"]["modified"] == ["ch3.md"]


def test_uses_mtime_when_sha_missing():
    """metadata-only files (no sha1) compare by mtime+size."""
    last = _mk_manifest("W17", [])
    this = _mk_manifest("W18", [])
    last["buckets"]["experiment_data"]["files"] = [
        {"path": "big.json", "sha1": None, "mtime": 100, "size": 999999}
    ]
    this["buckets"]["experiment_data"]["files"] = [
        {"path": "big.json", "sha1": None, "mtime": 200, "size": 999999}
    ]
    d = compute_diff(last, this)
    assert d["experiment_data"]["modified"] == ["big.json"]
