"""Shared pytest fixtures for weekly_report scripts tests."""
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
