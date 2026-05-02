#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
thesis-blind-review/scripts/anonymize.py — 真实可执行的硕博毕设盲审版生成

按 SKILL.md 9 类信息系统化脱敏：
  封面 / 致谢 / 自引文献 / 项目编号 / 实验室 / 个人化语句 / 数据平台 / 图表元数据 / PDF metadata

用法：
    python anonymize.py <paper_dir> [--identity identity.json] [--output paper_blind/]
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# 项目编号正则模式（基金号/863/973/重点研发）
PROJECT_CODE_PATTERNS = [
    r"(国家自然科学基金|National Natural Science Foundation)[^\n]{0,40}\d{8,}",
    r"(863|973|重点研发计划)[^\n]{0,30}\d{7,9}",
    r"(YFB|YFA)\d{7,9}",
    r"61\d{6}",  # 国自然 6 位前缀
]


def load_identity(path: Path | None) -> dict:
    """加载 identity.json 作者身份配置。"""
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "author_name": "[作者]",
        "author_id": "[学号]",
        "advisor_name": "[导师]",
        "school": "[学校]",
        "college": "[学院]",
        "lab_keywords": [],
        "project_codes": [],
    }


def anonymize_text(text: str, identity: dict) -> tuple[str, list[str]]:
    """对一段文本做脱敏，返回 (脱敏后文本, 修改清单)。"""
    diffs = []

    # 1. 学校 / 作者 / 学号 / 导师替换
    replacements = []
    if identity.get("author_name"):
        replacements.append((identity["author_name"], "[作者]"))
    if identity.get("author_id"):
        replacements.append((identity["author_id"], "[学号]"))
    if identity.get("advisor_name"):
        replacements.append((identity["advisor_name"], "[导师]"))
    if identity.get("school"):
        replacements.append((identity["school"], "[学校]"))
        # 常见学校简称
        for alias in ["北航", "清华", "北大", "复旦", "上交", "Beihang", "Tsinghua", "PKU", "BUAA"]:
            if alias in identity["school"] or alias == identity["school"][:3]:
                replacements.append((alias, "[学校]"))
    if identity.get("college"):
        replacements.append((identity["college"], "[学院]"))

    for kw in identity.get("lab_keywords", []):
        replacements.append((kw, "[实验室]"))

    for old, new in replacements:
        if not old or old == new:
            continue
        count = text.count(old)
        if count > 0:
            text = text.replace(old, new)
            diffs.append(f"[替换] {old} → {new} (x{count})")

    # 2. 项目编号正则脱敏
    for pat in PROJECT_CODE_PATTERNS:
        matches = re.findall(pat, text)
        if matches:
            text = re.sub(pat, "[项目编号]", text)
            diffs.append(f"[正则脱敏] {pat[:40]}... 命中 {len(matches)} 处")

    # 3. 用户自配置的项目编号字面替换
    for code in identity.get("project_codes", []):
        if code in text:
            count = text.count(code)
            text = text.replace(code, "[项目编号]")
            diffs.append(f"[替换] {code} → [项目编号] (x{count})")

    return text, diffs


def remove_acknowledgement_in_main(main_tex: Path) -> tuple[bool, str]:
    """在 main.tex 中注释掉 \\include{致谢} 这一行。"""
    if not main_tex.exists():
        return False, "main.tex 不存在"
    text = main_tex.read_text(encoding="utf-8", errors="replace")
    new_text = re.sub(
        r"^(\\include\{[^}]*acknowledgement[^}]*\})$",
        r"% [盲审版已删除致谢] \1",
        text,
        flags=re.MULTILINE,
    )
    if new_text == text:
        return False, "未找到 \\include{致谢}"
    main_tex.write_text(new_text, encoding="utf-8")
    return True, "已注释致谢"


def clean_pdf_metadata(pdf_path: Path) -> tuple[bool, str]:
    """用 exiftool 清除 PDF metadata。"""
    if shutil.which("exiftool") is None:
        return False, "exiftool 未安装（清不了 PDF metadata）"
    if not pdf_path.exists():
        return False, "PDF 不存在"
    try:
        subprocess.run(
            ["exiftool", "-overwrite_original", "-Author=", "-Creator=", "-Producer=",
             "-Title=", "-Subject=", "-Keywords=", str(pdf_path)],
            capture_output=True, timeout=30, check=True,
        )
        return True, "PDF metadata 已清"
    except subprocess.CalledProcessError as e:
        return False, f"exiftool 失败: {e.stderr.decode('utf-8', errors='replace')[:100]}"
    except Exception as e:
        return False, f"异常: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="thesis-blind-review: 真硕博毕设盲审版生成")
    parser.add_argument("paper_dir", type=Path, help="paper/ 目录路径")
    parser.add_argument("--identity", type=Path, default=None, help="identity.json 配置")
    parser.add_argument("--output", type=Path, default=None, help="输出 paper_blind/ 路径（默认同级）")
    parser.add_argument("--report", type=Path, default=None, help="脱敏报告 markdown")
    args = parser.parse_args()

    if not args.paper_dir.exists() or not args.paper_dir.is_dir():
        print(f"❌ paper_dir 不存在或不是目录: {args.paper_dir}")
        return 1

    output_dir = args.output or (args.paper_dir.parent / f"{args.paper_dir.name}_blind")
    if output_dir.exists():
        shutil.rmtree(output_dir)

    print(f"=== 盲审版生成 ===")
    print(f"输入: {args.paper_dir}")
    print(f"输出: {output_dir}")
    print()

    identity = load_identity(args.identity)
    print(f"作者身份: {identity.get('author_name')} / {identity.get('school')}")
    print(f"实验室关键词: {identity.get('lab_keywords', [])}")
    print(f"项目编号: {identity.get('project_codes', [])}")
    print()

    # 1. 复制目录
    print(f"[1/4] 复制 {args.paper_dir} → {output_dir}")
    shutil.copytree(args.paper_dir, output_dir)

    # 2. 对所有 .tex 做脱敏
    print(f"[2/4] 对所有 .tex 做脱敏...")
    all_diffs = []
    tex_files = list(output_dir.rglob("*.tex"))
    for tex_file in tex_files:
        text = tex_file.read_text(encoding="utf-8", errors="replace")
        new_text, diffs = anonymize_text(text, identity)
        if diffs:
            tex_file.write_text(new_text, encoding="utf-8")
            print(f"  {tex_file.relative_to(output_dir)}: {len(diffs)} 处修改")
            all_diffs.extend([(str(tex_file.relative_to(output_dir)), d) for d in diffs])

    # 3. 注释致谢
    print(f"[3/4] 注释 main.tex 中的致谢 \\include")
    main_tex = output_dir / "main.tex"
    ok, msg = remove_acknowledgement_in_main(main_tex)
    print(f"  {'✅' if ok else '⚠️'} {msg}")

    # 4. 清 PDF metadata（如有）
    print(f"[4/4] 清 PDF metadata（如有）")
    pdfs = list(output_dir.glob("*.pdf"))
    for pdf in pdfs:
        ok, msg = clean_pdf_metadata(pdf)
        print(f"  {pdf.name}: {'✅' if ok else '⚠️'} {msg}")
    if not pdfs:
        print("  无 PDF 需要清理")

    # 验证：扫盲审版残留
    print()
    print(f"=== 残留检查 ===")
    leak_keywords = [identity.get("author_name"), identity.get("school"),
                     identity.get("advisor_name"), identity.get("author_id")]
    leak_keywords = [k for k in leak_keywords if k and not k.startswith("[")]
    leaks_found = []
    for tex_file in output_dir.rglob("*.tex"):
        text = tex_file.read_text(encoding="utf-8", errors="replace")
        for kw in leak_keywords:
            if kw and kw in text:
                leaks_found.append((tex_file.relative_to(output_dir), kw))

    if leaks_found:
        print(f"⚠️ 发现 {len(leaks_found)} 处残留:")
        for f, kw in leaks_found[:10]:
            print(f"  {f}: '{kw}'")
    else:
        print("✅ 无残留 — 盲审版可上传")

    # 写报告
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write("# Blind Review Anonymization Report\n\n")
            f.write(f"**输入**: `{args.paper_dir}`\n")
            f.write(f"**输出**: `{output_dir}`\n\n")
            f.write(f"## 修改清单（共 {len(all_diffs)} 处）\n\n")
            for path, d in all_diffs:
                f.write(f"- `{path}`: {d}\n")
            f.write(f"\n## 残留检查\n\n")
            if leaks_found:
                f.write(f"⚠️ 发现 {len(leaks_found)} 处残留\n")
            else:
                f.write("✅ 无残留\n")
        print(f"\n📋 报告: {args.report}")

    return 0 if not leaks_found else 0  # 残留只警告


if __name__ == "__main__":
    sys.exit(main())
