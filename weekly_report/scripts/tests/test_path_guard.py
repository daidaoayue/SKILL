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
    target = tmp_project / ".weekly_report" / ".." / "Forecasting" / "x.py"
    assert is_write_allowed(target, project_root=tmp_project) is False


def test_neither_root_provided_denies(tmp_path: Path):
    """No whitelist roots = nothing allowed."""
    assert is_write_allowed(tmp_path / "anywhere.txt") is False
