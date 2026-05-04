"""Pick figure candidates to embed in a weekly report.

Strategies:
  - "newest_3": pick the N most recently modified figures within the active window.
  - "by_family": (future) pick one per family_key.
  - "all": take everything that fits the limits (cap by max_per_report).
"""
from __future__ import annotations
import time
from typing import Optional


def pick_figures(
    candidates: list[dict],
    *,
    strategy: str = "newest_3",
    max_per_report: int = 5,
    max_size_mb: float = 5.0,
    active_window_days: Optional[int] = None,
) -> list[dict]:
    """Filter candidates by size + active window, sort by mtime desc, cap by max_per_report."""
    cutoff = None
    if active_window_days is not None:
        cutoff = time.time() - active_window_days * 86400
    pool = []
    for c in candidates:
        if c.get("size", 0) > max_size_mb * 1024 * 1024:
            continue
        if cutoff is not None and c.get("mtime", 0) < cutoff:
            continue
        pool.append(c)
    pool.sort(key=lambda c: c.get("mtime", 0), reverse=True)
    return pool[:max_per_report]
