"""Tests for figure_picker."""
import time
from pathlib import Path
from scripts.figure_picker import pick_figures


def test_picks_newest_first():
    cands = [
        {"path": "fig_old.png", "mtime": 1.0, "size": 100},
        {"path": "fig_mid.png", "mtime": 2.0, "size": 100},
        {"path": "fig_new.png", "mtime": 3.0, "size": 100},
    ]
    sel = pick_figures(cands, strategy="newest_3", max_per_report=2,
                       max_size_mb=10, active_window_days=None)
    paths = [s["path"] for s in sel]
    assert paths == ["fig_new.png", "fig_mid.png"]


def test_filters_oversize():
    cands = [
        {"path": "fig_huge.png", "mtime": 1.0, "size": 11 * 1024 * 1024},
        {"path": "fig_ok.png",   "mtime": 2.0, "size": 1024},
    ]
    sel = pick_figures(cands, strategy="newest_3", max_per_report=5,
                       max_size_mb=10, active_window_days=None)
    paths = [s["path"] for s in sel]
    assert paths == ["fig_ok.png"]


def test_active_window_filters_old_figs():
    now = time.time()
    cands = [
        {"path": "old.png",  "mtime": now - 30 * 86400, "size": 100},
        {"path": "new.png",  "mtime": now - 1  * 86400, "size": 100},
    ]
    sel = pick_figures(cands, strategy="newest_3", max_per_report=5,
                       max_size_mb=10, active_window_days=7)
    paths = [s["path"] for s in sel]
    assert paths == ["new.png"]


def test_max_per_report_caps_pool():
    cands = [{"path": f"f{i}.png", "mtime": i, "size": 1} for i in range(10)]
    sel = pick_figures(cands, max_per_report=3, max_size_mb=10, active_window_days=None)
    assert len(sel) == 3


def test_empty_candidates_returns_empty():
    assert pick_figures([], max_per_report=5, max_size_mb=10, active_window_days=None) == []
