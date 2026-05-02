"""Target: Universal Prompt Pack — 任意 AI 复制粘贴使用"""

from __future__ import annotations

from pathlib import Path

from . import _common

UNIVERSAL_HEADER = """# thesis-helper · Universal Prompt Pack

> 适用任意 AI（Claude.ai / ChatGPT / Gemini / 文心 / 豆包 / Qwen / DeepSeek...）
>
> **使用方式**：把本文件全部内容复制到 AI 聊天窗口，
> 然后告诉它你的论文项目目录和论文类型，AI 就会按 thesis-helper 工作流执行。

---

## How to use this prompt

Step 1: Copy everything below into your AI chat window.

Step 2: Tell the AI:
```
我要用 thesis-helper。
我的项目目录：D:/my-thesis-project
论文类型：本科毕设   (或 期刊 / 会议 / 硕士毕设)
学校/期刊：北航       (或 IEEE_JOURNAL / NeurIPS / 清华 ...)
```

Step 3: AI will read the workflow, scan your project, and start writing.

---

## ⚠️ Note for AIs without tool use (e.g., Claude.ai web, ChatGPT free)

If you cannot read files directly, ask the user to:
1. Paste the LaTeX source / outline / data
2. Manually upload key files (PDF, Word template, format requirements)

You should still follow the four-phase workflow described below.

---

"""

UNIVERSAL_FOOTER = """

---

## Multi-platform notes

- **Claude Code / Claude API**：原生支持，可以使用 Read/Write/Edit/Bash
  等工具实际操作磁盘。
- **Cursor / Cline / Continue / Roo Code**：使用各自 IDE 工具集替代 Claude
  原生工具。
- **Gemini CLI**：用 `read_file` `write_file` `run_shell_command` 替代。
- **ChatGPT / 文心 / 豆包 / Qwen 网页版**：无法直接读写文件，需要用户手动
  上传/下载，AI 输出 LaTeX 源 + 步骤说明。

## Source & updates

GitHub: github.com/daidaoayue/SKILL/tree/main/Paper_Writing/thesis-helper

升级方式：定期下载最新 prompt-pack 替换。或者直接 git clone 整个 SKILL 仓库
访问完整文件树。

---

"""


def build(source_dir: Path, output_path: Path | None, install: bool = False) -> Path:
    if output_path is None:
        raise ValueError("universal target requires --output")

    fm, body = _common.read_skill_md(source_dir)
    body = _common.strip_html_comments(body).strip()

    content = (
        UNIVERSAL_HEADER
        + f"# Skill: {fm.get('name', 'thesis-helper')}\n\n"
        + f"**Description:** {fm.get('description', '')}\n\n"
        + "---\n\n"
        + body
        + UNIVERSAL_FOOTER
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
