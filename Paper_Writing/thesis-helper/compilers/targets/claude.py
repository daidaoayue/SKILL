"""Target: Claude Code — 整个 thesis-helper/ 目录复制到 ~/.claude/skills/"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from . import _common


def build(source_dir: Path, output_path: Path | None, install: bool = False) -> Path:
    """
    Claude Code 安装逻辑：
      install=True  → 自动复制到 ~/.claude/skills/thesis-helper/
      install=False → 复制到 output_path（用户指定的目标路径）
    """
    if install:
        home = Path(os.path.expanduser("~"))
        dest = home / ".claude" / "skills" / "thesis-helper"
    else:
        if output_path is None:
            raise ValueError("claude target requires --output or --install")
        dest = output_path

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

    # 复制全部文件（排除运行时产物）
    for src_file in _common.list_skill_files(source_dir):
        rel = src_file.relative_to(source_dir)
        dst_file = dest / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)

    return dest
