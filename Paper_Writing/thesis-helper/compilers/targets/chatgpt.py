"""Target: ChatGPT 自定义 GPTs Instructions — 必须 ≤ 8000 字符（建议 < 7500）"""

from __future__ import annotations

from pathlib import Path

from . import _common

# OpenAI 限制：Instructions ≤ 8000 字符。建议留 ≤ 7500 字符 buffer。
MAX_CHARS = 7500


CHATGPT_HEADER_TEMPLATE = """You are **thesis-helper**, an academic writing
assistant for students. {description}

**Workflow philosophy** (do NOT skip):
1. Always ask for the project directory first.
2. Detect thesis_type: journal | conference | undergrad-thesis | master-thesis.
3. Apply the appropriate pipeline (see below).
4. Always close the loop: deliver verification metrics (AIGC %, word count,
   page count, format compliance %).

---

"""

CHATGPT_FOOTER = """

---

## Cross-platform behavior

- This GPT was compiled from a Claude Code skill. Original tool names like
  Read/Write/Edit/Glob/Grep/Bash are **not** available — use ChatGPT's
  built-in code interpreter and file upload.
- For sub-skills (`/paper-writing`, `/aigc降低`, `/latex-to-word` etc.),
  ask the user to paste the corresponding SKILL.md content from the GitHub
  repo: github.com/daidaoayue/SKILL/tree/main/Paper_Writing/thesis-helper

## What to do FIRST in every conversation

Greet the user with:
"嗨，我是 thesis-helper。请告诉我：
 1. 你的论文项目目录（或直接上传 paper/main.tex）
 2. 论文类型：期刊 / 会议 / 本科毕设 / 硕士毕设
 3. 学校/期刊名（如 北航 / IEEE_JOURNAL / NeurIPS）"
"""


def build(source_dir: Path, output_path: Path | None, install: bool = False) -> Path:
    if output_path is None:
        raise ValueError("chatgpt target requires --output")

    fm, body = _common.read_skill_md(source_dir)
    desc = fm.get("description", "")

    # 关键章节抽取（不全文塞）
    sections_to_keep = [
        "四种论文类型 · 四条 pipeline",
        "用户只需 1 条指令",
        "Phase 0 · 项目自动扫描（必做）",
        "Phase 1 · 路由 + 调用 pipeline",
        "Owner 闭环承诺",
        "三条红线",
    ]
    body_compressed = ""
    for sec in sections_to_keep:
        content = _common.extract_section(body, sec)
        if content:
            body_compressed += f"## {sec}\n\n{content}\n\n"

    full = (
        CHATGPT_HEADER_TEMPLATE.format(description=desc)
        + body_compressed
        + CHATGPT_FOOTER
    )

    # 强制压缩
    full = _common.compress_markdown(full, MAX_CHARS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full, encoding="utf-8")
    return output_path
