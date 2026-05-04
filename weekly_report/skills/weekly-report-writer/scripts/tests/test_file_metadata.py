"""Tests for file_metadata single-file inspector."""
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
    assert rec is not None
    assert rec.size == 11 * 1024 * 1024
    assert rec.sha1 is None


def test_inspect_missing_returns_none(tmp_path: Path):
    f = tmp_path / "ghost.py"
    rec = inspect_file(f, metadata_only_size_mb=10)
    assert rec is None


def test_inspect_directory_returns_none(tmp_path: Path):
    d = tmp_path / "subdir"
    d.mkdir()
    rec = inspect_file(d, metadata_only_size_mb=10)
    assert rec is None


def test_inspect_uses_rel_path_when_provided(tmp_path: Path):
    f = tmp_path / "x.py"
    f.write_text("y")
    rec = inspect_file(f, metadata_only_size_mb=10, rel_path="Forecasting/x.py")
    assert rec.path == "Forecasting/x.py"
