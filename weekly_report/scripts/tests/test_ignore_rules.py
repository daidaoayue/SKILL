"""Tests for ignore_rules glob matcher."""
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
    m = IgnoreMatcher(global_globs=[], skip_symlinks=True)
    target = tmp_project / "real.py"
    target.write_text("x")
    link = tmp_project / "link.py"
    try:
        link.symlink_to(target)
        assert m.is_symlink(link) is True
    except (OSError, NotImplementedError):
        pytest.skip("symlink not permitted on this platform")


def test_skip_symlinks_off_returns_false(tmp_project: Path):
    m = IgnoreMatcher(global_globs=[], skip_symlinks=False)
    target = tmp_project / "real.py"
    target.write_text("x")
    assert m.is_symlink(target) is False
