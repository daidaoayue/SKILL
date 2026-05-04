"""Path write guard. Hard rule: skill MUST NOT modify user code.

Whitelisted write locations:
  - <project_root>/.weekly_report/**
  - <reports_root>/**           (cross-project aggregate, e.g. D:\\code\\reports\\)

Any other write attempt raises PathGuardError. Use assert_write_allowed()
before any open(..., 'w') / 'wb' / Path.write_text() / write_bytes() / mkdir
within scripts that synthesize output files.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional


class PathGuardError(RuntimeError):
    """Raised when a script tries to write outside the whitelist."""


def _is_within(child: Path, parent: Path) -> bool:
    try:
        Path(child).resolve().relative_to(Path(parent).resolve())
        return True
    except ValueError:
        return False


def is_write_allowed(
    target: Path,
    project_root: Optional[Path] = None,
    reports_root: Optional[Path] = None,
) -> bool:
    """Return True iff target is inside one of the whitelisted roots."""
    target = Path(target)
    if project_root is not None:
        weekly_report = Path(project_root) / ".weekly_report"
        if _is_within(target, weekly_report):
            return True
    if reports_root is not None:
        if _is_within(target, Path(reports_root)):
            return True
    return False


def assert_write_allowed(
    target: Path,
    project_root: Optional[Path] = None,
    reports_root: Optional[Path] = None,
) -> None:
    if not is_write_allowed(target, project_root, reports_root):
        raise PathGuardError(
            f"Write target {target} not in write whitelist "
            f"(project_root={project_root}, reports_root={reports_root})"
        )
