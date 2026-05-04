"""Tests for init_project bucket detection + project.toml scaffold."""
import sys
from pathlib import Path
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
    if sys.version_info >= (3, 11):
        import tomllib
        obj = tomllib.loads(text)
        assert obj["project"]["name"] == "proj"
        assert obj["buckets"]["code"]["roots"] == ["Forecasting"]
    else:
        # tomllib not available pre-3.11; do string sanity checks
        assert 'name = "proj"' in text
        assert '"Forecasting"' in text


def test_detect_skips_hidden_dirs(tmp_path: Path):
    (tmp_path / ".weekly_report").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "Forecasting").mkdir()
    detected = detect_buckets(tmp_path)
    # .weekly_report should not appear in any bucket
    for bucket_roots in detected.values():
        assert ".weekly_report" not in bucket_roots
        assert ".git" not in bucket_roots


def test_detect_each_dir_assigned_at_most_once_top_level(tmp_path: Path):
    """Top-level dir name 'output' could match both code (no) and experiment_data (yes).
    The first match wins."""
    (tmp_path / "output").mkdir()
    detected = detect_buckets(tmp_path)
    assert "output" in detected["experiment_data"]
    assert "output" not in detected["code"]
