"""Tests for update_index idempotent cross-project index.md."""
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
    assert text.count(f"| W18 | 2026-05-04~05-10 | radar |") == 1
    assert "x_updated" in text and "| x |" not in text


def test_multiple_years_sorted_newest_first(tmp_path: Path):
    idx = tmp_path / "index.md"
    upsert_index_row(idx, year="2025", week="W50",
                     date_range="2025-12-08~12-14",
                     project_short="x", highlight="h", link="l.md")
    upsert_index_row(idx, year="2026", week="W18",
                     date_range="2026-05-04~05-10",
                     project_short="x", highlight="h", link="l.md")
    text = idx.read_text(encoding="utf-8")
    pos_2026 = text.find("## 2026")
    pos_2025 = text.find("## 2025")
    assert 0 < pos_2026 < pos_2025  # 2026 appears before 2025


def test_creates_parent_dir(tmp_path: Path):
    idx = tmp_path / "deep" / "nested" / "index.md"
    upsert_index_row(idx, year="2026", week="W1",
                     date_range="d", project_short="p",
                     highlight="h", link="l.md")
    assert idx.exists()
