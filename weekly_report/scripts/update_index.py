"""Maintain D:\\code\\reports\\index.md across all projects/weeks.

Idempotent: re-running with same (year, week, project) replaces row.
Years sorted newest-first.
"""
from __future__ import annotations
import re
from pathlib import Path

HEADER = "# 周报汇总索引\n"
TABLE_HEADER = (
    "| 周号 | 日期 | 工程 | 本周抓手 | 链接 |\n"
    "| --- | --- | --- | --- | --- |\n"
)

YEAR_RE = re.compile(r"^##\s+(\d{4})\s*$")
ROW_RE = re.compile(r"^\|\s*W\d+\s*\|", re.MULTILINE)


def _parse(md: str) -> dict[str, list[str]]:
    """Parse existing index.md into {year: [row_lines]}."""
    years: dict[str, list[str]] = {}
    current = None
    for line in md.splitlines():
        ym = YEAR_RE.match(line.strip())
        if ym:
            current = ym.group(1)
            years.setdefault(current, [])
            continue
        if current is None:
            continue
        if line.startswith("| W"):
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
    # Remove any pre-existing row with same (week, date_range, project)
    prefix = f"| {week} | {date_range} | {project_short} |"
    rows = [r for r in rows if not r.startswith(prefix)]
    rows.append(new_row)
    years[year] = rows

    sorted_years = sorted(years.keys(), reverse=True)
    out: list[str] = [HEADER]
    for y in sorted_years:
        out.append("")
        out.append(f"## {y}")
        out.append("")
        out.append(TABLE_HEADER.rstrip("\n"))
        out.append("\n".join(years[y]))
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(out) + "\n", encoding="utf-8")
