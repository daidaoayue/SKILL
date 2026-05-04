"""Glob-based ignore matcher with global + project layered rules."""
from __future__ import annotations
import fnmatch
from pathlib import Path
from typing import Iterable, Optional


class IgnoreMatcher:
    def __init__(
        self,
        global_globs: Optional[Iterable[str]] = None,
        project_globs: Optional[Iterable[str]] = None,
        skip_symlinks: bool = True,
    ) -> None:
        self._globs: list[str] = []
        if global_globs:
            self._globs.extend(global_globs)
        if project_globs:
            self._globs.extend(project_globs)
        self._skip_symlinks = skip_symlinks

    def is_ignored(self, rel_path: Path) -> bool:
        s = str(rel_path).replace("\\", "/")
        parts = s.split("/")
        for g in self._globs:
            # `dir/**` matches the dir at any depth, plus everything under it.
            if "/**" in g:
                head = g.replace("/**", "")
                if s == head or s.startswith(head + "/"):
                    return True
                if "/" not in head and head in parts:
                    # bare dir name like "build_tmp" — match at any depth
                    return True
            # full-path glob (handles **/ patterns and explicit paths)
            if fnmatch.fnmatch(s, g):
                return True
            # basename glob (catches top-level patterns like "*_tmp.*", "*~")
            if fnmatch.fnmatch(rel_path.name, g):
                return True
        return False

    def is_symlink(self, abs_path: Path) -> bool:
        if not self._skip_symlinks:
            return False
        try:
            return abs_path.is_symlink()
        except OSError:
            return False
