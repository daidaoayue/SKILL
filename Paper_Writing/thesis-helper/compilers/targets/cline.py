"""Target: Cline / Continue / Roo Code — 生成 .clinerules"""

from __future__ import annotations

from pathlib import Path

from . import _common

CLINE_HEADER = """# .clinerules · thesis-helper

This file is loaded by Cline (and compatible AI coding assistants such as
Continue, Roo Code) when opened at the project root. It activates the
thesis-helper workflow for academic paper writing.

Source: thesis-helper @ daidaoayue/SKILL
Compiled by: thesis-helper/compilers/build.py

---

"""


def build(source_dir: Path, output_path: Path | None, install: bool = False) -> Path:
    if output_path is None:
        raise ValueError("cline target requires --output")

    fm, body = _common.read_skill_md(source_dir)
    body = _common.strip_html_comments(body).strip()

    content = (
        CLINE_HEADER
        + f"## Skill: {fm.get('name', 'thesis-helper')}\n\n"
        + f"**Trigger phrases:** 写论文 / 毕设 / 期刊 / conference / "
        + f"thesis-helper / paper writing\n\n"
        + f"**What it does:** {fm.get('description', '')}\n\n"
        + "---\n\n"
        + body
        + "\n\n---\n\n"
        + "## Cline Notes\n\n"
        + "- Skill调用：本 skill 引用其他 skill（如 /paper-writing /aigc降低）时，\n"
        + "  Cline 应读取 `thesis-helper/{integrations,extensions}/<name>/SKILL.md`\n"
        + "  并按其 pipeline 执行。\n"
        + "- 工具映射与 Cursor 相同（read/write/edit/run/grep）。\n"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
