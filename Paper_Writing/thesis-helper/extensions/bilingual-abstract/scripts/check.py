#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bilingual-abstract/scripts/check.py — 真实可执行的中英摘要平行检查

按 SKILL.md 4 维度检查：字数比例 / 关键词数量 / 段落结构 / 术语一致性

用法：
    python check.py <abstract.tex> [--thesis-type undergrad-thesis]
                                   [--report report.md] [--json data.json]
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


# 字数区间（按论文类型）
LIMITS = {
    "undergrad-thesis": {
        "zh_chars": (300, 600), "en_words": (200, 350), "ratio": (1.5, 2.5),
        "keywords_min": 3, "keywords_max": 5,
    },
    "master-thesis": {
        "zh_chars": (500, 1000), "en_words": (350, 600), "ratio": (1.5, 2.5),
        "keywords_min": 3, "keywords_max": 5,
    },
    "phd-thesis": {
        "zh_chars": (800, 1500), "en_words": (500, 800), "ratio": (1.5, 2.5),
        "keywords_min": 3, "keywords_max": 5,
    },
    "journal-ieee": {
        "zh_chars": (150, 300), "en_words": (100, 250), "ratio": (1.5, 2.0),
        "keywords_min": 3, "keywords_max": 6,
    },
}


def clean_latex(text: str) -> str:
    """剥离 LaTeX 命令、公式、注释。"""
    text = re.sub(r"%.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\$[^$]*\$", " <MATH> ", text)
    text = re.sub(r"\\[a-zA-Z]+\{[^{}]*\}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    text = re.sub(r"[{}\\]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_abstracts(tex: str) -> tuple[str, str, list[str], list[str]]:
    """提取中英摘要 + 关键词。"""
    # 模式 1: cabstract / eabstract（北航 buaathesis）
    zh_m = re.search(r"\\begin\{cabstract\}(.*?)\\end\{cabstract\}", tex, re.DOTALL)
    en_m = re.search(r"\\begin\{eabstract\}(.*?)\\end\{eabstract\}", tex, re.DOTALL)

    # 模式 2: \chapter*{摘要} / \chapter*{Abstract}
    if not zh_m:
        zh_m = re.search(r"\\chapter\*\{摘\s*要\}(.*?)(?=\\chapter|$)", tex, re.DOTALL)
    if not en_m:
        en_m = re.search(r"\\chapter\*\{Abstract\}(.*?)(?=\\chapter|$)", tex, re.DOTALL)

    zh_raw = zh_m.group(1).strip() if zh_m else ""
    en_raw = en_m.group(1).strip() if en_m else ""

    # 关键词提取
    zh_kw_m = re.search(r"\\(?:keywords|chinakeywords)\{([^}]+)\}", tex)
    en_kw_m = re.search(r"\\(?:ekeywords|englishkeywords)\{([^}]+)\}", tex)
    # 也尝试 "关键词：" 后的内容
    if not zh_kw_m:
        zh_kw_m = re.search(r"关键词[：:]\s*([^\n\\]+)", tex)
    if not en_kw_m:
        en_kw_m = re.search(r"[Kk]eywords[：:]\s*([^\n\\]+)", tex)

    zh_kws = []
    en_kws = []
    if zh_kw_m:
        zh_kws = [k.strip() for k in re.split(r"[；;,，]", zh_kw_m.group(1)) if k.strip()]
    if en_kw_m:
        en_kws = [k.strip() for k in re.split(r"[;,]", en_kw_m.group(1)) if k.strip()]

    return zh_raw, en_raw, zh_kws, en_kws


def count_chinese_chars(text: str) -> int:
    return len(re.findall(r"[一-鿿]", text))


def count_english_words(text: str) -> int:
    return len(re.findall(r"\b[A-Za-z][A-Za-z\-']+\b", text))


def split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def check_dimension_1(zh_chars: int, en_words: int, limits: dict) -> dict:
    """字数比例检查。"""
    ratio = zh_chars / en_words if en_words else 0
    zh_min, zh_max = limits["zh_chars"]
    en_min, en_max = limits["en_words"]
    r_min, r_max = limits["ratio"]
    return {
        "name": "字数比例",
        "zh_chars": zh_chars, "zh_pass": zh_min <= zh_chars <= zh_max,
        "zh_range": f"{zh_min}-{zh_max}",
        "en_words": en_words, "en_pass": en_min <= en_words <= en_max,
        "en_range": f"{en_min}-{en_max}",
        "ratio": round(ratio, 2), "ratio_pass": r_min <= ratio <= r_max,
        "ratio_range": f"{r_min}-{r_max}",
    }


def check_dimension_2(zh_kws: list, en_kws: list, limits: dict) -> dict:
    """关键词数量与对齐。"""
    return {
        "name": "关键词",
        "zh_count": len(zh_kws), "en_count": len(en_kws),
        "count_match": len(zh_kws) == len(en_kws) and len(zh_kws) > 0,
        "in_range": limits["keywords_min"] <= len(zh_kws) <= limits["keywords_max"],
        "zh_keywords": zh_kws, "en_keywords": en_kws,
    }


def check_dimension_3(zh_paras: list, en_paras: list) -> dict:
    """段落结构。"""
    return {
        "name": "段落结构",
        "zh_paragraphs": len(zh_paras), "en_paragraphs": len(en_paras),
        "match": len(zh_paras) == len(en_paras),
    }


def check_dimension_4(zh: str, en: str) -> dict:
    """术语一致性（简易频率分析）。"""
    # 中文 2-6 字术语
    zh_terms = re.findall(r"[一-鿿]{3,8}", zh)
    # 英文 Title Case 短语
    en_terms = re.findall(r"\b[A-Z][a-zA-Z\-]+(?:\s+[A-Z][a-zA-Z\-]+){0,3}\b", en)

    from collections import Counter
    zh_top = Counter(zh_terms).most_common(8)
    en_top = Counter(en_terms).most_common(8)

    return {
        "name": "术语一致性",
        "zh_top_terms": zh_top,
        "en_top_terms": en_top,
        "note": "简易频率扫描；完整对齐需要 sentence-transformers 多语义模型",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="bilingual-abstract: 真中英摘要平行检查")
    parser.add_argument("abstract_tex", type=Path, help="abstract.tex 路径")
    parser.add_argument("--thesis-type", default="undergrad-thesis",
                        choices=list(LIMITS), help="论文类型")
    parser.add_argument("--report", type=Path, default=None, help="输出 markdown 报告")
    parser.add_argument("--json", type=Path, default=None, help="输出 JSON 数据")
    args = parser.parse_args()

    if not args.abstract_tex.exists():
        print(f"❌ 找不到 {args.abstract_tex}")
        return 1

    tex = args.abstract_tex.read_text(encoding="utf-8", errors="replace")
    zh_raw, en_raw, zh_kws, en_kws = extract_abstracts(tex)

    if not zh_raw or not en_raw:
        print(f"❌ 摘要提取失败 (zh={len(zh_raw)} en={len(en_raw)})")
        print(f"   请检查是否有 \\begin{{cabstract}}/\\begin{{eabstract}} 或 \\chapter*{{摘要}}/\\chapter*{{Abstract}}")
        return 2

    zh_clean = clean_latex(zh_raw)
    en_clean = clean_latex(en_raw)
    zh_chars = count_chinese_chars(zh_clean)
    en_words = count_english_words(en_clean)
    zh_paras = split_paragraphs(zh_raw)
    en_paras = split_paragraphs(en_raw)

    limits = LIMITS[args.thesis_type]

    d1 = check_dimension_1(zh_chars, en_words, limits)
    d2 = check_dimension_2(zh_kws, en_kws, limits)
    d3 = check_dimension_3(zh_paras, en_paras)
    d4 = check_dimension_4(zh_clean, en_clean)

    issues = []
    if not (d1["zh_pass"] and d1["en_pass"] and d1["ratio_pass"]):
        issues.append("字数比例")
    if not (d2["count_match"] and d2["in_range"]):
        issues.append("关键词")
    if not d3["match"]:
        issues.append("段落数")

    print(f"=== 中英摘要平行检查 ({args.thesis_type}) ===")
    print(f"")
    print(f"维度 1 · 字数：")
    print(f"  中文 {zh_chars} 字 (区间 {d1['zh_range']}) {'✅' if d1['zh_pass'] else '❌'}")
    print(f"  英文 {en_words} 词 (区间 {d1['en_range']}) {'✅' if d1['en_pass'] else '❌'}")
    print(f"  比例 {d1['ratio']} (区间 {d1['ratio_range']}) {'✅' if d1['ratio_pass'] else '❌'}")
    print(f"")
    print(f"维度 2 · 关键词：")
    print(f"  中文 {d2['zh_count']} 个 / 英文 {d2['en_count']} 个 / "
          f"匹配={'✅' if d2['count_match'] else '❌'} 在区间={'✅' if d2['in_range'] else '❌'}")
    if d2["zh_keywords"]:
        print(f"  中文: {d2['zh_keywords']}")
        print(f"  英文: {d2['en_keywords']}")
    print(f"")
    print(f"维度 3 · 段落数：中 {d3['zh_paragraphs']} vs 英 {d3['en_paragraphs']} {'✅' if d3['match'] else '❌'}")
    print(f"")
    print(f"维度 4 · 术语 top 8（频率扫描）：")
    print(f"  中文 top: {[t for t, _ in d4['zh_top_terms'][:5]]}")
    print(f"  英文 top: {[t for t, _ in d4['en_top_terms'][:5]]}")
    print(f"")
    print(f"📊 总评：{'✅ ALL PASS' if not issues else f'⚠️ {len(issues)} 项需修：{issues}'}")

    result = {
        "abstract_tex": str(args.abstract_tex),
        "thesis_type": args.thesis_type,
        "dimension_1_word_count": d1,
        "dimension_2_keywords": d2,
        "dimension_3_paragraphs": d3,
        "dimension_4_terms": d4,
        "issues": issues,
        "pass_overall": not issues,
    }

    if args.json:
        args.json.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📋 JSON: {args.json}")
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(f"# Bilingual Abstract Check\n\n")
            f.write(f"**Source**: `{args.abstract_tex}`\n")
            f.write(f"**Type**: {args.thesis_type}\n\n")
            f.write(f"## 总评：{'✅ ALL PASS' if not issues else f'⚠️ {len(issues)} 项需修'}\n\n")
            f.write(f"详见 JSON 数据 (--json)\n")
        print(f"📋 报告: {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
