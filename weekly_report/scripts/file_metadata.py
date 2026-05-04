"""Inspect a single file: size, mtime, sha1 (only if small enough)."""
from __future__ import annotations
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FileRecord:
    path: str            # relative-to-project, posix style
    size: int
    mtime: float
    sha1: Optional[str]  # None if metadata-only (file size > threshold)


def _sha1_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha1()
    with p.open("rb") as fh:
        while True:
            data = fh.read(chunk)
            if not data:
                break
            h.update(data)
    return h.hexdigest()


def inspect_file(
    abs_path: Path,
    metadata_only_size_mb: int,
    rel_path: Optional[str] = None,
) -> Optional[FileRecord]:
    """Return FileRecord for abs_path, or None if missing / not a file."""
    if not abs_path.exists() or not abs_path.is_file():
        return None
    st = abs_path.stat()
    size = st.st_size
    sha1 = None
    if size <= metadata_only_size_mb * 1024 * 1024:
        sha1 = _sha1_of(abs_path)
    return FileRecord(
        path=rel_path or str(abs_path).replace("\\", "/"),
        size=size,
        mtime=st.st_mtime,
        sha1=sha1,
    )
