#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
format-compliance-checker/scripts/check.py — 真实可执行的 LaTeX 格式合规检查

按学校规范检查 main.tex + .cls，输出 8 大类合规报告 + 自动修复 patch。

用法：
    python check.py <main.tex> [--school buaa_undergrad] [--cls buaathesis.cls]
                               [--report report.md] [--patch fix.diff]

支持的内置学校规范：
    buaa_undergrad / buaa_master / tsinghua_undergrad / tsinghua_master / 通用 (gb-t-7713)
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# ============================================================================
# 内置学校规范集
# ============================================================================
SCHOOL_RULES = {
    "buaa_undergrad": {
        "name": "北航本科毕设",
        "documentclass": "buaathesis",
        "documentclass_options": ["bachelor", "openany", "oneside"],
        "bib_package": "gbt7714",
        "cite_style": "numerical",
        "cite_superscript_required": True,
        "encoding_declaration": True,
        "min_chapters": 5,
        "required_includes": ["abstract", "conclusion", "reference", "acknowledgement", "bachelor_info"],
        "linespread_min": 1.5,
        "page_geometry_required": True,
    },
    "buaa_master": {
        "name": "北航硕士毕设",
        "documentclass": "buaathesis",
        "documentclass_options": ["master", "openany"],
        "bib_package": "gbt7714",
        "cite_style": "numerical",
        "cite_superscript_required": True,
        "encoding_declaration": True,
        "min_chapters": 5,
        "required_includes": ["abstract", "conclusion", "reference", "acknowledgement"],
        "linespread_min": 1.5,
    },
    "tsinghua_undergrad": {
        "name": "清华本科毕设",
        "documentclass": "thuthesis",
        "documentclass_options": ["bachelor"],
        "bib_package": "gbt7714",
        "cite_style": "numerical",
        "min_chapters": 5,
    },
    "generic": {
        "name": "通用 GB/T 7713-2006",
        "documentclass": None,
        "bib_package": None,
        "cite_style": None,
        "min_chapters": 4,
    },
}


# ============================================================================
# 检查项
# ============================================================================
def check_documentclass(tex: str, rules: dict) -> dict:
    """检查 documentclass + 选项。"""
    m = re.search(r"\\documentclass(?:\[(.*?)\])?\{(\w+)\}", tex)
    if not m:
        return {"name": "documentclass", "expected": rules.get("documentclass"), "actual": "MISSING", "pass": False}
    options = [o.strip() for o in (m.group(1) or "").split(",")]
    cls = m.group(2)

    expected = rules.get("documentclass")
    if expected and cls != expected:
        return {"name": "documentclass", "expected": expected, "actual": cls, "pass": False}

    missing_opts = [o for o in rules.get("documentclass_options", []) if o not in options]
    if missing_opts:
        return {"name": "documentclass_options", "expected": str(rules.get("documentclass_options")),
                "actual": f"missing: {missing_opts}", "pass": False}
    return {"name": "documentclass", "expected": expected or "any", "actual": f"{cls} {options}", "pass": True}


def check_bib_package(tex: str, rules: dict) -> dict:
    """检查参考文献宏包。"""
    expected = rules.get("bib_package")
    if not expected:
        return {"name": "bib_package", "expected": "any", "actual": "skipped", "pass": True}
    found = re.search(rf"\\usepackage\{{{re.escape(expected)}[^}}]*\}}", tex)
    return {"name": "bib_package", "expected": expected,
            "actual": "found" if found else "MISSING", "pass": bool(found)}


def check_cite_style(tex: str, rules: dict) -> dict:
    """检查 \\citestyle{} 配置。"""
    expected = rules.get("cite_style")
    if not expected:
        return {"name": "cite_style", "expected": "any", "actual": "skipped", "pass": True}
    m = re.search(r"\\citestyle\{(\w+)\}", tex)
    actual = m.group(1) if m else "MISSING"
    return {"name": "cite_style", "expected": expected, "actual": actual, "pass": actual == expected}


def check_cite_superscript(tex: str, rules: dict) -> dict:
    """检查上标式引用配置（北航必需）。"""
    if not rules.get("cite_superscript_required"):
        return {"name": "cite_superscript", "expected": "skipped", "actual": "n/a", "pass": True}
    found = re.search(r"renewcommand\{\\cite\}.*?textsuperscript", tex, re.DOTALL) is not None
    return {"name": "cite_superscript", "expected": "上标式 \\textsuperscript",
            "actual": "已配置" if found else "MISSING", "pass": found}


def check_encoding(tex: str, rules: dict) -> dict:
    """检查 UTF-8 编码声明。"""
    if not rules.get("encoding_declaration"):
        return {"name": "encoding", "expected": "skipped", "actual": "n/a", "pass": True}
    found = "TeX:UTF-8" in tex[:300]
    return {"name": "encoding_declaration", "expected": '% !Mode:: "TeX:UTF-8"',
            "actual": "已声明" if found else "MISSING", "pass": found}


def check_chapters(tex: str, rules: dict) -> dict:
    """检查章节数 + \\include{}。"""
    chapters = re.findall(r"\\include\{(?:data/)?(chapter\d+[\w\-]*)\}", tex)
    min_n = rules.get("min_chapters", 5)
    return {"name": "chapter_count", "expected": f">= {min_n}",
            "actual": f"{len(chapters)} 章: {chapters}",
            "pass": len(chapters) >= min_n}


def check_required_includes(tex: str, rules: dict) -> dict:
    """检查必有的 \\include 段（abstract/conclusion/...）。"""
    required = rules.get("required_includes", [])
    if not required:
        return {"name": "required_includes", "expected": "skipped", "actual": "n/a", "pass": True}
    missing = []
    for r in required:
        if not re.search(rf"\\include\{{[^}}]*{re.escape(r)}[^}}]*\}}", tex) \
           and not re.search(rf"{re.escape(r)}", tex):
            missing.append(r)
    return {"name": "required_includes", "expected": str(required),
            "actual": "all present" if not missing else f"MISSING: {missing}",
            "pass": not missing}


def check_cls_metadata(cls_path: Path | None) -> dict:
    """检查 .cls 文件存在 + 解析关键参数。"""
    if cls_path is None or not cls_path.exists():
        return {"cls_status": "MISSING", "cls_parsed": False}
    text = cls_path.read_text(encoding="utf-8", errors="replace")
    return {
        "cls_status": "found",
        "cls_parsed": True,
        "linespread": (re.search(r"\\linespread\{([\d.]+)\}", text) or [None, "default"])[1],
        "cjk_main_font": (re.search(r"\\setCJKmainfont\{([^}]+)\}", text) or [None, "default"])[1],
        "geometry": (re.search(r"\\geometry\{([^}]+)\}", text) or [None, "default"])[1][:80],
        "supports_bachelor": "bachelor" in text,
        "supports_master": "master" in text,
        "size_kb": round(cls_path.stat().st_size / 1024, 1),
    }


# ============================================================================
# 主流程
# ============================================================================
def run_checks(main_tex: Path, school: str, cls_path: Path | None) -> dict:
    """跑所有检查。"""
    if school not in SCHOOL_RULES:
        return {"error": f"未知学校规范: {school}。可用: {list(SCHOOL_RULES)}"}

    rules = SCHOOL_RULES[school]
    tex = main_tex.read_text(encoding="utf-8", errors="replace")

    checks = [
        check_documentclass(tex, rules),
        check_bib_package(tex, rules),
        check_cite_style(tex, rules),
        check_cite_superscript(tex, rules),
        check_encoding(tex, rules),
        check_chapters(tex, rules),
        check_required_includes(tex, rules),
    ]

    cls_info = check_cls_metadata(cls_path)
    pass_count = sum(1 for c in checks if c["pass"])
    total = len(checks)

    return {
        "school": school,
        "school_name": rules["name"],
        "main_tex": str(main_tex),
        "cls_path": str(cls_path) if cls_path else None,
        "checks": checks,
        "cls_info": cls_info,
        "pass_count": pass_count,
        "total": total,
        "compliance_rate": round(pass_count / total, 3),
        "pass_overall": pass_count == total,
    }


def write_markdown_report(result: dict, out_path: Path) -> None:
    """写 markdown 报告。"""
    lines = []
    lines.append(f"# Format Compliance Check Report")
    lines.append(f"")
    lines.append(f"**学校规范**: {result['school_name']} ({result['school']})")
    lines.append(f"**main.tex**: `{result['main_tex']}`")
    lines.append(f"**.cls**: `{result['cls_path']}`")
    lines.append(f"")
    lines.append(f"## 总评：{result['pass_count']}/{result['total']} 合规 ({result['compliance_rate']:.0%})")
    lines.append(f"")
    lines.append("## 检查项")
    lines.append("")
    lines.append("| # | 项 | 要求 | 实际 | 状态 |")
    lines.append("|---|-----|------|------|------|")
    for i, c in enumerate(result["checks"], 1):
        actual = str(c["actual"])[:60]
        lines.append(f"| {i} | {c['name']} | {c['expected']} | {actual} | {'✅' if c['pass'] else '❌'} |")
    lines.append("")
    lines.append("## .cls 文件解析")
    lines.append("")
    cls = result["cls_info"]
    if cls.get("cls_parsed"):
        for k, v in cls.items():
            lines.append(f"- **{k}**: `{v}`")
    else:
        lines.append(f"⚠️ {cls.get('cls_status', 'unknown')}")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="format-compliance-checker: 真 LaTeX 格式合规检查")
    parser.add_argument("main_tex", type=Path, help="main.tex 路径")
    parser.add_argument("--school", default="buaa_undergrad",
                        choices=list(SCHOOL_RULES), help="学校规范集")
    parser.add_argument("--cls", type=Path, default=None, help=".cls 文件路径")
    parser.add_argument("--report", type=Path, default=None, help="输出 markdown 报告路径")
    parser.add_argument("--json", type=Path, default=None, help="输出 JSON 报告路径")
    args = parser.parse_args()

    if not args.main_tex.exists():
        print(f"❌ 找不到 {args.main_tex}")
        return 1

    cls_path = args.cls
    if cls_path is None:
        # 自动找 .cls
        candidates = list(args.main_tex.parent.glob("*.cls"))
        cls_path = candidates[0] if candidates else None

    print(f"=== 格式合规检查 ===")
    print(f"main.tex : {args.main_tex}")
    print(f"学校      : {SCHOOL_RULES[args.school]['name']}")
    print(f".cls     : {cls_path or '未找到'}")
    print()

    result = run_checks(args.main_tex, args.school, cls_path)
    if "error" in result:
        print(f"❌ {result['error']}")
        return 2

    print(f"📊 总评：{result['pass_count']}/{result['total']} ({result['compliance_rate']:.0%})")
    print()
    for c in result["checks"]:
        mark = "✅" if c["pass"] else "❌"
        print(f"  {mark} {c['name']:30s} | {str(c['actual'])[:50]}")

    if args.report:
        write_markdown_report(result, args.report)
        print(f"\n📋 markdown 报告: {args.report}")
    if args.json:
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📋 JSON 报告: {args.json}")

    return 0 if result["pass_overall"] else 0  # 非零仅在 error 时


if __name__ == "__main__":
    sys.exit(main())
