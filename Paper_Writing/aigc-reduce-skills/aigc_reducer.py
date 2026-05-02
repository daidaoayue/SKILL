#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
aigc_reducer.py — 真把 aigc-reduce 7 stage 全做成可执行 Python（不再懒）

7 stage 全实现：
  Stage 0 · destructure  打散整齐编号 + 教科书定义 + 三段平行 + 列表加粗
  Stage 1 · vocab        词汇精炼（CNKI 实测触发词清单 + LLM 签名词）
  Stage 2 · rhythm       句长方差（长句拆短 + 段长不齐）
  Stage 3 · cohesion     删机械过渡词（首先/其次/此外/因此/综上）
  Stage 4 · hedging      克制 hedging（删过密"在某种程度上""可能"）
  Stage 5 · perplexity   破 N-gram + 思维痕迹注入（"为什么有效？"等）
  Stage 6 · cite-inject  标记综述段需要注入 cite 的位置

用法：
    python aigc_reducer.py <input.tex> [-o output.tex] [--report report.md]
                                       [--stages all|0,1,2,3,4,5,6]
"""

from __future__ import annotations

import argparse
import io
import json
import random
import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# ============================================================================
# Stage 0 · destructure 规则（来自 aigc-reduce-destructure/SKILL.md）
# ============================================================================
DESTRUCTURE_PATTERNS = [
    (r"（[1-9]）", "·", "整齐编号-中文圆括号"),
    (r"\([1-9]\)", "·", "整齐编号-半角"),
    (r"其(数学|物理|几何|逻辑)(含义|定义)(为|是)：", "", "教科书定义引导词"),
    (r"其(数学|物理|几何|逻辑)(含义|定义)是", "", "教科书定义"),
    (r"(三|四|五|六|七)(个|大)(方面|层次|层面|环节|核心|挑战|步骤|要点)：", "", "概括化分层"),
    (r"(三|四|五|六|七)(个|大)(方面|层次|层面|环节)的", "", "概括化分层"),
    (r"\\textbf\{([^}]+)层\}", r"\1层", "列表式加粗分层"),
]

# ============================================================================
# Stage 1 · vocab 规则（来自 aigc-reduce-vocab/SKILL.md）
# ============================================================================
VOCAB_REPLACEMENTS_ZH = {
    "深入探讨": "探讨", "深入分析": "分析", "深入研究": "研究",
    "至关重要": "关键", "值得注意的是": "", "值得注意的是，": "",
    "综合性": "完整", "综合来看": "", "综合来看，": "",
    "具有重要意义": "有价值", "广泛应用": "应用",
    "迭代升级": "迭代", "纵深推进": "推进",
    "夯实基础": "基础", "释放潜力": "潜力",
    "深度融合": "融合", "有机结合": "结合",
    "强调了": "指出", "阐明了": "说明",
    "基于上述考虑，": "", "基于上述考虑": "",
    "综合上述研究现状分析，": "", "综合上述分析，": "",
    "具体而言，": "", "具体来说，": "",
    "该现象提示：": "", "机制分析显示：": "",
    "凸显了": "", "迫切需求": "需求",
    "其优势在于": "优势是", "其代价是": "代价是",
    "本课题": "课题", "本课题对": "对", "本课题的": "课题的",
    "促进": "推动", "彰显": "体现",
    "保驾护航": "支撑", "赋能": "支持",
    "完整的参考路径": "参考路径",
    "构建了一套": "构建了", "构建一套": "构建",
}
VOCAB_REPLACEMENTS_EN = {
    "delve into": "examine", "delve": "examine",
    "tapestry": "set", "multifaceted": "multiple",
    "foster": "support", "pivotal": "central",
    "underscore": "highlight", "shed light on": "clarify",
    "intricate": "complex", "comprehensive": "complete",
    "robust": "strong", "leverage": "use", "harness": "use",
    "in the realm of": "in",
    "it is worth noting that": "",
    "plays a pivotal role": "is central",
    "paramount": "critical", "seamless": "smooth",
    "in this paper, we propose": "we introduce",
    "the proposed method": "our method",
    "extensive experiments demonstrate": "experiments show",
    "due to the fact that": "because", "in order to": "to",
    "rapid development": "rapid scaling",
    "play a crucial role": "is central",
    "achieves state-of-the-art": "matches the strongest baselines",
}

# ============================================================================
# Stage 2 · rhythm 规则
# ============================================================================
def stage_2_rhythm_split_long_sentences(text: str) -> tuple[str, list[dict]]:
    """长句（> 80 字）按"，"拆短句，提升 burstiness。"""
    diffs = []
    sentences = re.split(r"(。|！|？)", text)
    new_parts = []
    for i in range(0, len(sentences) - 1, 2):
        sent = sentences[i]
        ender = sentences[i+1] if i+1 < len(sentences) else ""
        # 中文长句 > 80 字
        zh_chars = len(re.findall(r"[一-鿿]", sent))
        if zh_chars > 80 and "，" in sent:
            commas = sent.count("，")
            if commas >= 2:
                # 找中间逗号位置拆
                parts = sent.split("，")
                mid = len(parts) // 2
                first = "，".join(parts[:mid]) + "。"
                second = "，".join(parts[mid:])
                new_parts.append(first + second + ender)
                diffs.append({"stage": "rhythm", "type": "split_long",
                            "before_chars": zh_chars,
                            "preview": sent[:30] + "..."})
                continue
        new_parts.append(sent + ender)
    if len(sentences) % 2 == 1:
        new_parts.append(sentences[-1])
    return "".join(new_parts), diffs

# ============================================================================
# Stage 3 · cohesion 规则
# ============================================================================
COHESION_WORDS_TO_DELETE = [
    "首先，", "其次，", "再次，", "然后，", "接下来，", "之后，", "最后，",
    "首先,", "其次,", "再次,", "然后,",
    "此外，", "另外，", "而且，", "并且，", "同时，",
    "因此，", "所以，", "于是，", "故，", "由此，",
    "综上所述，", "综上，", "由此可见，", "由此观之，",
    "总之，", "总的来说，", "总而言之，",
    "Furthermore, ", "Moreover, ", "Additionally, ",
    "Therefore, ", "Thus, ", "Hence, ", "Consequently, ",
    "In conclusion, ", "In summary, ", "To summarize, ",
    "First, ", "Second, ", "Third, ", "Finally, ", "Lastly, ",
]

# ============================================================================
# Stage 4 · hedging 规则
# ============================================================================
HEDGING_OVERUSED = {
    "在某种程度上": "", "在某种程度上，": "",
    "在一定程度上": "", "在一定程度上，": "",
    "或许可以": "", "或许可以认为": "",
    "在很大程度上": "", "通常来说": "",
    "可能存在": "存在", "可能会": "会",
    "暗示了": "表明", "似乎表明": "表明",
    "我们认为可能": "我们认为", "可以认为": "",
}

# ============================================================================
# Stage 5 · perplexity + 思维痕迹注入
# ============================================================================
NGRAM_REPLACEMENTS = {
    "近年来，": "", "近年来": "",
    "随着...的发展": "", "随着深度学习的发展": "随着深度学习成熟",
    "广泛使用": "使用", "得到广泛应用": "已被采用",
    "众多学者": "多个团队", "国内外学者": "国内外团队",
    "取得了优异的性能": "达到了较好精度",
    "提出了一种新颖的": "提出了一种",
    "整体框架如图.*所示": "整体框架见图",  # regex
}

# 思维痕迹短语库（按位置选）
THOUGHT_TRACES = [
    "这个结果有点反直觉。",
    "为什么有效？",
    "从物理上看，",
    "换句话说，",
    "起初我们尝试了",
    "实际跑下来，",
    "麻烦在于",
    "难点集中在",
]

def stage_5_perplexity_traces(text: str, max_per_chapter: int = 3) -> tuple[str, list[dict]]:
    """破 N-gram + 注入思维痕迹（按规则）。"""
    diffs = []
    # N-gram 替换
    for old, new in NGRAM_REPLACEMENTS.items():
        if old.startswith(".*") or "*" in old:
            # 视为 regex
            pattern = re.compile(old)
            matches = pattern.findall(text)
            if matches:
                text = pattern.sub(new, text)
                diffs.append({"stage": "perplexity", "type": "ngram-regex",
                            "old": old, "new": new, "count": len(matches)})
        elif old in text:
            count = text.count(old)
            text = text.replace(old, new)
            diffs.append({"stage": "perplexity", "type": "ngram",
                        "old": old, "new": new, "count": count})

    # 思维痕迹注入：在"实验结果分析段"句首插入
    # 简易规则：找到含"我们做了"/"实验"/"结果"且段长 > 100 字的段落，插入痕迹
    paragraphs = text.split("\n\n")
    inject_count = 0
    for i, para in enumerate(paragraphs):
        if inject_count >= max_per_chapter:
            break
        if (("实验" in para or "结果" in para or "数据" in para)
            and len(para) > 200
            and not any(t in para for t in THOUGHT_TRACES)):
            # 在第一个句号后插入一条思维痕迹
            trace = THOUGHT_TRACES[inject_count % len(THOUGHT_TRACES)]
            new_para = re.sub(r"(。)", r"\1" + trace, para, count=1)
            if new_para != para:
                paragraphs[i] = new_para
                inject_count += 1
                diffs.append({"stage": "perplexity", "type": "thought-trace",
                            "trace": trace, "para_idx": i})
    text = "\n\n".join(paragraphs)
    return text, diffs

# ============================================================================
# Stage 6 · cite-inject 规则（标记，不真插）
# ============================================================================
def stage_6_cite_inject(text: str) -> tuple[str, list[dict]]:
    """标记综述段中可注入 cite 的位置（生成建议清单，不真插，避免引用伪造）。"""
    diffs = []
    paragraphs = text.split("\n\n")
    for i, para in enumerate(paragraphs):
        # 综述段特征：含"研究/工作/方法/团队/学者/年"等 + 段长 > 200 字 + cite < 1
        if (re.search(r"(研究|工作|方法|团队|学者|提出|采用|提到|发现)", para)
            and len(para) > 200
            and len(re.findall(r"\\cite\{", para)) < 1):
            diffs.append({"stage": "cite-inject", "type": "suggestion",
                        "para_idx": i, "preview": para[:50] + "...",
                        "action": "建议在段尾添加 \\cite{}"})
    return text, diffs


# ============================================================================
# Stage 1 · vocab
# ============================================================================
def stage_1_vocab(text: str) -> tuple[str, list[dict]]:
    diffs = []
    for old, new in VOCAB_REPLACEMENTS_ZH.items():
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            diffs.append({"stage": "vocab", "type": "zh", "old": old,
                         "new": new, "count": count})
    for old, new in VOCAB_REPLACEMENTS_EN.items():
        pattern = re.compile(r"\b" + re.escape(old) + r"\b", re.IGNORECASE)
        matches = pattern.findall(text)
        if matches:
            text = pattern.sub(new, text)
            diffs.append({"stage": "vocab", "type": "en", "old": old,
                         "new": new, "count": len(matches)})
    return text, diffs

# ============================================================================
# Stage 0 · destructure
# ============================================================================
def stage_0_destructure(text: str) -> tuple[str, list[dict]]:
    diffs = []
    for pat, repl, label in DESTRUCTURE_PATTERNS:
        matches = re.findall(pat, text)
        if matches:
            text = re.sub(pat, repl, text)
            diffs.append({"stage": "destructure", "label": label,
                         "pattern": pat, "count": len(matches)})
    return text, diffs

# ============================================================================
# Stage 3 · cohesion
# ============================================================================
def stage_3_cohesion(text: str) -> tuple[str, list[dict]]:
    diffs = []
    for word in COHESION_WORDS_TO_DELETE:
        if word in text:
            count = text.count(word)
            text = text.replace(word, "")
            diffs.append({"stage": "cohesion", "removed": word, "count": count})
    return text, diffs

# ============================================================================
# Stage 4 · hedging
# ============================================================================
def stage_4_hedging(text: str) -> tuple[str, list[dict]]:
    diffs = []
    for old, new in HEDGING_OVERUSED.items():
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            diffs.append({"stage": "hedging", "old": old, "new": new, "count": count})
    return text, diffs


# ============================================================================
# 主流程 — 7 stage 全跑
# ============================================================================
STAGE_FUNCS = {
    0: ("destructure", stage_0_destructure),
    1: ("vocab", stage_1_vocab),
    2: ("rhythm", stage_2_rhythm_split_long_sentences),
    3: ("cohesion", stage_3_cohesion),
    4: ("hedging", stage_4_hedging),
    5: ("perplexity", stage_5_perplexity_traces),
    6: ("cite-inject", stage_6_cite_inject),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="aigc-reduce 真程序化版（7 stage 全跑）")
    parser.add_argument("input", type=Path, help="输入 .tex / .md / .txt")
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--stages", default="all",
                        help="all 或 0,1,2,3,4,5,6")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"❌ {args.input} 不存在")
        return 1

    text = args.input.read_text(encoding="utf-8", errors="replace")
    original_len = len(text)

    if args.stages == "all":
        stages_to_run = list(range(7))
    else:
        stages_to_run = [int(s.strip()) for s in args.stages.split(",")]

    all_diffs = []
    print(f"=== aigc-reduce 7-stage 真跑 ===")
    print(f"输入: {args.input.name} ({original_len} 字符)")
    print(f"运行 stages: {stages_to_run}")
    print()

    for s in stages_to_run:
        if s not in STAGE_FUNCS:
            continue
        label, func = STAGE_FUNCS[s]
        text, diffs = func(text)
        total_count = sum(d.get("count", 1) for d in diffs)
        print(f"  Stage {s} · {label:12s}: {len(diffs):3d} 类规则命中, {total_count:4d} 次替换/标记")
        all_diffs.extend(diffs)

    final_len = len(text)
    print()
    print(f"📊 字符数: {original_len} → {final_len} (Δ={final_len - original_len})")
    print(f"📊 7 stage 总计: {len(all_diffs)} 类命中, "
          f"{sum(d.get('count', 1) for d in all_diffs)} 次实际操作")

    output = args.output or args.input.with_name(f"{args.input.stem}_reduced{args.input.suffix}")
    output.write_text(text, encoding="utf-8")
    print(f"\n✅ 输出: {output}")

    if args.json:
        args.json.write_text(json.dumps(all_diffs, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📋 JSON: {args.json}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(f"# aigc-reduce 7-stage 真改写清单\n\n")
            f.write(f"**输入**: `{args.input}` ({original_len} 字符)\n")
            f.write(f"**输出**: `{output}` ({final_len} 字符 / Δ={final_len-original_len})\n")
            f.write(f"**运行 stages**: {stages_to_run}\n\n")
            f.write(f"## 改写清单（{len(all_diffs)} 项）\n\n")
            for s in stages_to_run:
                stage_name = STAGE_FUNCS.get(s, ("?",))[0]
                stage_diffs = [d for d in all_diffs if d.get("stage") == stage_name]
                if stage_diffs:
                    f.write(f"\n### Stage {s} · {stage_name} ({len(stage_diffs)} 项)\n\n")
                    for d in stage_diffs:
                        if "old" in d:
                            f.write(f"- `{d['old']}` → `{d.get('new', '')}` (×{d['count']})\n")
                        elif "removed" in d:
                            f.write(f"- 删除 `{d['removed']}` (×{d['count']})\n")
                        elif "trace" in d:
                            f.write(f"- 注入思维痕迹 `{d['trace']}` (段 #{d['para_idx']})\n")
                        elif "label" in d:
                            f.write(f"- {d['label']}: `{d['pattern']}` (×{d['count']})\n")
                        elif "preview" in d:
                            f.write(f"- {d.get('action', '')}: {d['preview']}\n")
        print(f"📋 报告: {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
