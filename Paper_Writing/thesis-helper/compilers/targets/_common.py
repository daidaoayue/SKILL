"""共享工具：解析 frontmatter / 提取章节 / 压缩 markdown。"""

from __future__ import annotations

import re
from pathlib import Path


def read_skill_md(source_dir: Path) -> tuple[dict, str]:
    """读 SKILL.md，分离 frontmatter (yaml dict) 和正文 markdown。"""
    skill_path = source_dir / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")

    # 解析 frontmatter
    fm: dict = {}
    body = text
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end > 0:
            fm_text = text[4:end]
            body = text[end + 5:]
            # 简易 yaml 解析（避免依赖 PyYAML）
            for line in fm_text.split("\n"):
                if ":" in line:
                    k, _, v = line.partition(":")
                    fm[k.strip()] = v.strip().strip('"')
    return fm, body


def extract_section(markdown: str, heading: str) -> str:
    """提取指定 ## 标题下的章节内容。找不到返回空。"""
    pattern = rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s+|\Z)"
    m = re.search(pattern, markdown, re.MULTILINE | re.DOTALL)
    return m.group(1).strip() if m else ""


def strip_html_comments(text: str) -> str:
    """去除 HTML 注释（如 <!-- markdownlint-disable -->）。"""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def compress_markdown(text: str, max_chars: int) -> str:
    """
    压缩 markdown 到指定字符上限（用于 ChatGPT 4096 限制）。

    策略（按顺序应用）：
      1. 去除 HTML 注释
      2. 折叠 3+ 连续空行为 1 空行
      3. 移除 ASCII 表格内的对齐空格
      4. 移除示例代码块
      5. 截断（保留前 max_chars-100 字符 + 末尾说明）
    """
    text = strip_html_comments(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 折叠表格列宽（多空格 → 单空格）
    text = re.sub(r"  +", " ", text)
    if len(text) <= max_chars:
        return text
    # 截断
    truncated_marker = "\n\n... (内容截断，完整版见 GitHub)\n"
    keep_chars = max_chars - len(truncated_marker)
    return text[:keep_chars] + truncated_marker


def list_skill_files(source_dir: Path) -> list[Path]:
    """列出 thesis-helper 下所有应该被打包的文件（排除运行时产物）。"""
    excludes = {".thesis-helper", "__pycache__", ".git", ".venv"}
    out: list[Path] = []
    for p in source_dir.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(source_dir)
        if any(part in excludes for part in rel.parts):
            continue
        out.append(p)
    return sorted(out)
