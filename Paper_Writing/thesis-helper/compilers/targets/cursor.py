"""Target: Cursor IDE — 生成 .cursorrules 单文件"""

from __future__ import annotations

from pathlib import Path

from . import _common

CURSOR_HEADER = """# Cursor Rules · thesis-helper

These rules instruct Cursor to act as the thesis-helper assistant for student
paper writing. When the user mentions "写论文" / "thesis" / "毕设" / "期刊" /
"会议", load this skill and follow the workflow below.

Source: thesis-helper @ daidaoayue/SKILL (Paper_Writing/thesis-helper)
Compiled by: thesis-helper/compilers/build.py

---

"""


def build(source_dir: Path, output_path: Path | None, install: bool = False) -> Path:
    if output_path is None:
        raise ValueError("cursor target requires --output")

    fm, body = _common.read_skill_md(source_dir)

    # Cursor 没有字符上限，但建议精简（移除 ASCII 表格的视觉装饰会更紧凑）
    body = _common.strip_html_comments(body).strip()

    content = (
        CURSOR_HEADER
        + f"## Skill: {fm.get('name', 'thesis-helper')}\n\n"
        + f"**Description:** {fm.get('description', '')}\n\n"
        + "---\n\n"
        + body
        + "\n\n---\n\n"
        + "## Cursor Usage Notes\n\n"
        + "- This rules file is auto-generated. Edit thesis-helper/SKILL.md upstream.\n"
        + "- Cursor's tools (read/edit/grep/run) replace Claude's allowed-tools above.\n"
        + "- Sub-skill calls (e.g. `/paper-writing`, `/aigc降低`) translate to:\n"
        + "  read the corresponding skill file under thesis-helper/{integrations,extensions}/\n"
        + "  and follow its pipeline.\n"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
