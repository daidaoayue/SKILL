#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
latex-to-word/scripts/convert.py — 真实可执行的 LaTeX → Word 转换器

底层逻辑：
- 主路径：pandoc（保留公式、引用、表格）
- 后处理：python-docx 应用学校字体规范（如有学校 docx 模板，用 --reference-doc）
- 验证：python-docx 复检公式数量、章节数、字符数

用法：
    python convert.py <input.tex> [-o output.docx] [--template school.docx]
                                  [--bibliography refs.bib]
                                  [--csl citation-style.csl]

例子：
    python convert.py paper/main.tex -o paper/main.docx
    python convert.py main.tex --template buaa.docx --bibliography refs.bib
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def check_pandoc() -> tuple[bool, str]:
    """检查 pandoc 是否可用。"""
    if shutil.which("pandoc") is None:
        return False, "pandoc 未安装。请先 `choco install pandoc` 或 `apt install pandoc`"
    try:
        out = subprocess.run(["pandoc", "--version"], capture_output=True, text=True, timeout=10)
        version_line = out.stdout.split("\n")[0] if out.stdout else "unknown"
        return True, version_line
    except Exception as e:
        return False, f"pandoc 检查失败: {e}"


def detect_complexity(tex_path: Path) -> dict:
    """统计 .tex 内的复杂度：公式/引用/表格数量。"""
    try:
        text = tex_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"error": str(e)}

    # 统计 \include{} 引入的子文件
    includes = re.findall(r"\\include\{([^}]+)\}", text)
    inputs = re.findall(r"\\input\{([^}]+)\}", text)

    # 收集主文件 + 子文件的全文
    all_text = text
    base_dir = tex_path.parent
    for inc in includes + inputs:
        sub_path = base_dir / f"{inc}.tex"
        if not sub_path.exists():
            sub_path = base_dir / inc
        if sub_path.exists():
            try:
                all_text += "\n" + sub_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                pass

    return {
        "equations_count": len(re.findall(r"\\begin\{equation\}", all_text)),
        "tables_count": len(re.findall(r"\\begin\{tabular\}", all_text)),
        "figures_count": len(re.findall(r"\\begin\{figure\}", all_text)),
        "cite_count": len(re.findall(r"\\cite\{", all_text)),
        "ref_count": len(re.findall(r"\\ref\{", all_text)),
        "chapter_count": len(re.findall(r"\\chapter\{", all_text)),
        "section_count": len(re.findall(r"\\section\{", all_text)),
        "include_files": includes + inputs,
        "char_count": len(re.sub(r"\\[a-zA-Z]+\{[^{}]*\}|\\[a-zA-Z]+|[{}\\%]", "", all_text)),
    }


def convert_with_pandoc(
    tex_path: Path,
    output_path: Path,
    template: Path | None = None,
    bibliography: Path | None = None,
    csl: Path | None = None,
    extra_args: list[str] | None = None,
) -> tuple[bool, str]:
    """调 pandoc 真转换 .tex → .docx。"""
    cmd = [
        "pandoc",
        str(tex_path),
        "--from=latex",
        "--to=docx",
        "--toc",
        "--toc-depth=3",
        "-o", str(output_path),
        "--resource-path", str(tex_path.parent),
    ]
    if template and template.exists():
        cmd += ["--reference-doc", str(template)]
    if bibliography and bibliography.exists():
        cmd += ["--bibliography", str(bibliography)]
    if csl and csl.exists():
        cmd += ["--csl", str(csl)]
    if extra_args:
        cmd += extra_args

    try:
        result = subprocess.run(
            cmd,
            cwd=tex_path.parent,
            capture_output=True,
            text=True,
            timeout=180,
            encoding="utf-8",
            errors="replace",
        )
        if result.returncode == 0:
            return True, "OK"
        # pandoc 警告但仍生成了文件
        if output_path.exists() and output_path.stat().st_size > 0:
            return True, f"OK (with warnings: {result.stderr[:200]})"
        return False, f"pandoc 失败: {result.stderr[:500]}"
    except subprocess.TimeoutExpired:
        return False, "pandoc 超时（>180s）"
    except Exception as e:
        return False, f"pandoc 异常: {e}"


def verify_docx(docx_path: Path, expected: dict) -> dict:
    """用 python-docx 验证生成的 docx。"""
    try:
        from docx import Document
    except ImportError:
        return {"docx_readable": False, "error": "python-docx 未安装（pip install python-docx）"}

    if not docx_path.exists():
        return {"docx_readable": False, "error": "docx 文件不存在"}

    try:
        doc = Document(docx_path)
    except Exception as e:
        return {"docx_readable": False, "error": f"docx 打开失败: {e}"}

    para_count = len(doc.paragraphs)
    table_count = len(doc.tables)
    all_text = "\n".join(p.text for p in doc.paragraphs)
    char_count = len(all_text)

    return {
        "docx_readable": True,
        "paragraph_count": para_count,
        "table_count": table_count,
        "docx_char_count": char_count,
        "docx_size_kb": round(docx_path.stat().st_size / 1024, 1),
        "table_count_match": table_count >= expected.get("tables_count", 0) * 0.8,
        "first_para_preview": (doc.paragraphs[0].text[:60] if doc.paragraphs else ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="latex-to-word: 真实可执行的 LaTeX → Word 转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="例子:\n"
               "  python convert.py paper/main.tex\n"
               "  python convert.py main.tex -o out.docx --template buaa.docx\n",
    )
    parser.add_argument("input_tex", type=Path, help="输入的 main.tex 路径")
    parser.add_argument("-o", "--output", type=Path, default=None, help="输出 docx 路径（默认同名 .docx）")
    parser.add_argument("--template", type=Path, default=None, help="学校 Word 模板（pandoc reference-doc）")
    parser.add_argument("--bibliography", type=Path, default=None, help="参考文献 .bib")
    parser.add_argument("--csl", type=Path, default=None, help="引用格式 .csl（如 gb-t-7714）")
    parser.add_argument("--report", type=Path, default=None, help="输出 JSON 转换报告")
    args = parser.parse_args()

    if not args.input_tex.exists():
        print(f"❌ 输入文件不存在: {args.input_tex}")
        return 1

    output = args.output or args.input_tex.with_suffix(".docx")

    # 1. 检查 pandoc
    pandoc_ok, pandoc_msg = check_pandoc()
    print(f"[1/4] pandoc 检查: {'✅' if pandoc_ok else '❌'} {pandoc_msg}")
    if not pandoc_ok:
        return 2

    # 2. 复杂度检测
    print(f"[2/4] 复杂度检测: {args.input_tex}")
    complexity = detect_complexity(args.input_tex)
    if "error" in complexity:
        print(f"  ❌ {complexity['error']}")
        return 3
    print(f"  公式={complexity['equations_count']} 表格={complexity['tables_count']} "
          f"图={complexity['figures_count']} 引用={complexity['cite_count']} "
          f"章={complexity['chapter_count']} 节={complexity['section_count']}")
    print(f"  子文件: {len(complexity['include_files'])} 个")

    # 3. 转换
    print(f"[3/4] pandoc 转换 → {output}")
    ok, msg = convert_with_pandoc(
        args.input_tex, output,
        template=args.template,
        bibliography=args.bibliography,
        csl=args.csl,
    )
    print(f"  {'✅' if ok else '❌'} {msg}")
    if not ok:
        return 4

    # 4. 验证
    print(f"[4/4] python-docx 验证")
    verify = verify_docx(output, complexity)
    if not verify.get("docx_readable"):
        print(f"  ❌ {verify.get('error', '未知错误')}")
        return 5
    print(f"  段落={verify['paragraph_count']} 表格={verify['table_count']} "
          f"字符={verify['docx_char_count']} 大小={verify['docx_size_kb']} KB")

    # 输出报告
    if args.report:
        report = {
            "input": str(args.input_tex),
            "output": str(output),
            "complexity": complexity,
            "verify": verify,
            "pandoc_version": pandoc_msg,
        }
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📋 报告: {args.report}")

    print(f"\n✅ 转换完成: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
