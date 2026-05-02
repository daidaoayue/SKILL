#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
thesis-defense-prep/scripts/extract_qa.py — 真实可执行的答辩素材提取器

按 SKILL.md Phase 1 (论文解析) + Phase 2 (时间规划) + Phase 6 (Q&A 模拟):
  - 解析 paper/main.tex 提取论文骨架
  - 按答辩时长分配每一页时间预算
  - 输出 5 维度评委可能问的问题（基于论文实际内容）

用法：
    python extract_qa.py <paper_dir> [--duration 15] [--output defense/]
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


# 答辩黄金时间分配（按 SKILL.md Phase 2）
TIME_ALLOCATION = {
    "opening": 0.10,         # 开场（自我介绍 + 选题背景）
    "contributions": 0.15,   # 研究内容 / 创新点
    "method": 0.25,          # 方法与技术路线
    "experiments": 0.30,     # 实验结果
    "conclusion": 0.10,      # 结论 / 应用价值 / 展望
    "thanks": 0.10,          # 致谢
}


def parse_main_tex(main_tex: Path) -> dict:
    """解析 main.tex 提取论文骨架。"""
    text = main_tex.read_text(encoding="utf-8", errors="replace")

    # 标题
    title_m = re.search(r"\\title\{([^}]+)\}", text)
    title = title_m.group(1) if title_m else "[标题]"

    # 作者
    author_m = re.search(r"\\author\{([^}]+)\}", text)
    author = author_m.group(1)[:30] if author_m else "[作者]"

    # 章节
    chapters = re.findall(r"\\include\{(?:data/|sections/)?(chapter[\w\-]+|conclusion|abstract)\}", text)

    # 各章节实际内容
    chapter_data = []
    base = main_tex.parent
    for chap in chapters:
        for sub in [base / "sections" / f"{chap}.tex", base / "data" / f"{chap}.tex", base / f"{chap}.tex"]:
            if sub.exists():
                chap_text = sub.read_text(encoding="utf-8", errors="replace")
                sections = re.findall(r"\\section\{([^}]+)\}", chap_text)
                tables = len(re.findall(r"\\begin\{tabular\}", chap_text))
                figures = len(re.findall(r"\\begin\{figure\}", chap_text))
                equations = len(re.findall(r"\\begin\{equation\}", chap_text))
                # 抽取关键数字（精度、参数量等）
                numbers = re.findall(r"\d+\.\d{2}\s*[%％]?", chap_text)
                chapter_data.append({
                    "name": chap,
                    "section_count": len(sections),
                    "section_titles": sections[:5],
                    "tables": tables, "figures": figures, "equations": equations,
                    "key_numbers_sample": numbers[:5],
                    "char_count": len(re.sub(r"\\[a-zA-Z]+\{[^{}]*\}|\\[a-zA-Z]+|[{}\\%]", "", chap_text)),
                })
                break

    return {
        "title": title,
        "author": author,
        "chapters": chapter_data,
        "total_chars": sum(c.get("char_count", 0) for c in chapter_data),
    }


def plan_time_budget(duration_min: int) -> dict:
    """按答辩时长分配各阶段时间预算。"""
    total_seconds = duration_min * 60
    budget = {}
    for phase, ratio in TIME_ALLOCATION.items():
        seconds = int(total_seconds * ratio)
        # 假设每页 30-60 秒，取均值 45
        pages = max(1, round(seconds / 45))
        budget[phase] = {"seconds": seconds, "pages": pages, "ratio_pct": int(ratio * 100)}
    budget["_total_seconds"] = total_seconds
    budget["_total_pages"] = sum(b["pages"] for k, b in budget.items() if not k.startswith("_"))
    return budget


def generate_qa_simulation(paper_meta: dict) -> list[dict]:
    """5 维度评委生成可能问的问题（基于论文实际内容）。"""
    qa = []
    title = paper_meta["title"]
    chapter_count = len(paper_meta["chapters"])
    has_experiments = any("result" in c["name"].lower() or "experiment" in c["name"].lower()
                          or "实验" in str(c.get("section_titles", "")) for c in paper_meta["chapters"])
    has_method = any("method" in c["name"].lower() or "方法" in str(c.get("section_titles", ""))
                     or "fusion" in c["name"].lower() for c in paper_meta["chapters"])

    # 维度 1：方法严谨性
    qa.append({
        "judge_role": "方法严谨性专家",
        "question": "你的方法相比 baseline 的提升，统计上显著吗？做了 t-test 或类似的显著性检验吗？",
        "severity": "⚠️⚠️⚠️ 必问",
        "answer_hint": "1. 直面：是的，做了配对 t-test/Welch's t-test。2. 数据：N 次重复实验均值±标准差。3. 转移：在子集上提升更显著。",
    })
    qa.append({
        "judge_role": "方法严谨性专家",
        "question": "你的实验数据集划分方式是什么？训练/验证/测试是按什么比例划分的？是否做了 K-fold 交叉验证？",
        "severity": "⚠️⚠️⚠️ 必问",
        "answer_hint": "明确说明划分粒度（按样本/按航迹/按时段）+ 比例 + 是否多种子蒙特卡洛验证",
    })

    # 维度 2：工程实现
    qa.append({
        "judge_role": "工程实现专家",
        "question": "代码可复现吗？数据集会公开吗？超参数（学习率、batch size）是怎么选的？",
        "severity": "⚠️⚠️⚠️ 必问",
        "answer_hint": "1. 代码：GitHub 链接（已开源/审批中）。2. 数据：合作单位私有，但说明可申请。3. 超参：明确列出网格搜索范围。",
    })

    # 维度 3：选题立意
    qa.append({
        "judge_role": "选题立意专家",
        "question": f"《{title[:30]}...》这个课题，为什么这个时间点做？解决的是哪类实际场景的痛点？",
        "severity": "⚠️⚠️ 高频",
        "answer_hint": "1. 时间窗：行业政策/技术成熟度/数据可获得性的交汇点。2. 场景：举 1-2 个具体应用案例。",
    })
    qa.append({
        "judge_role": "选题立意专家",
        "question": "你的工作和最相关的国内外 SOTA 工作相比，主要的差异和优势在哪？",
        "severity": "⚠️⚠️⚠️ 必问",
        "answer_hint": "明确指出 1-2 篇最相关工作 + 你的差异化贡献（数据/方法/部署任一维度）",
    })

    # 维度 4：理论功底
    if has_method:
        qa.append({
            "judge_role": "理论功底专家",
            "question": "你的核心方法依赖的关键数学假设是什么？这些假设在你的真实数据上成立吗？",
            "severity": "⚠️⚠️ 高频",
            "answer_hint": "列出 1-3 个关键假设 + 用统计检验或经验数据验证",
        })

    # 维度 5：应用价值
    if has_experiments:
        qa.append({
            "judge_role": "应用价值专家",
            "question": "你的方法在实际工程部署中的瓶颈是什么？延迟、功耗、内存的硬指标如何？",
            "severity": "⚠️⚠️ 高频",
            "answer_hint": "1. 给出 PC 端 vs 边缘端的精度/延迟/功耗对比。2. 说明已识别的瓶颈与改进方向。",
        })

    qa.append({
        "judge_role": "应用价值专家",
        "question": "如果实际场景下数据分布与训练分布有差异，你的模型表现会怎么样？",
        "severity": "⚠️ 偶发",
        "answer_hint": "1. 承认这是局限。2. 提出可能的应对（在线学习/增量训练）。3. 引到展望章节。",
    })

    return qa


def main() -> int:
    parser = argparse.ArgumentParser(description="thesis-defense-prep: 真答辩素材提取")
    parser.add_argument("paper_dir", type=Path, help="paper/ 目录")
    parser.add_argument("--duration", type=int, default=15, help="答辩时长（分钟，默认 15）")
    parser.add_argument("--output", type=Path, default=None, help="输出目录")
    args = parser.parse_args()

    main_tex = args.paper_dir / "main.tex"
    if not main_tex.exists():
        print(f"❌ {main_tex} 不存在")
        return 1

    output = args.output or (args.paper_dir.parent / "defense")
    output.mkdir(parents=True, exist_ok=True)

    print(f"=== 答辩素材提取 ===")
    print(f"论文: {main_tex}")
    print(f"答辩时长: {args.duration} 分钟")
    print(f"输出: {output}")
    print()

    # 1. 解析论文
    print(f"[1/3] 解析 main.tex 提取骨架...")
    paper_meta = parse_main_tex(main_tex)
    print(f"  标题: {paper_meta['title'][:50]}")
    print(f"  章节: {len(paper_meta['chapters'])} 章")
    for c in paper_meta["chapters"]:
        print(f"    - {c['name']}: {c['section_count']} 节, {c['tables']} 表, "
              f"{c['figures']} 图, {c['equations']} 公式, {c['char_count']} 字")

    (output / "paper_metadata.json").write_text(
        json.dumps(paper_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. 时间规划
    print(f"\n[2/3] 时间预算分配（{args.duration} 分钟）")
    budget = plan_time_budget(args.duration)
    print(f"  总页数预估: {budget['_total_pages']} 页 (每页 ~45 秒)")
    for phase, b in budget.items():
        if not phase.startswith("_"):
            print(f"  - {phase:15s}: {b['ratio_pct']:3d}% / {b['seconds']:4d}s / {b['pages']} 页")

    (output / "time_plan.json").write_text(
        json.dumps(budget, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. Q&A 模拟
    print(f"\n[3/3] 5 维度评委 Q&A 模拟")
    qa = generate_qa_simulation(paper_meta)
    critical = sum(1 for q in qa if "⚠️⚠️⚠️" in q["severity"])
    print(f"  生成 {len(qa)} 题（含 {critical} 题 ⚠️⚠️⚠️ 必问）")

    # 写 Q&A markdown
    qa_md = output / "qa_simulation.md"
    with open(qa_md, "w", encoding="utf-8") as f:
        f.write(f"# 答辩问答模拟\n\n")
        f.write(f"**论文**: {paper_meta['title']}\n")
        f.write(f"**答辩时长**: {args.duration} 分钟\n")
        f.write(f"**生成题数**: {len(qa)} (其中必问 {critical} 题)\n\n")
        f.write("---\n\n")
        for i, q in enumerate(qa, 1):
            f.write(f"## Q{i} · {q['severity']}\n\n")
            f.write(f"**评委角色**: {q['judge_role']}\n\n")
            f.write(f"**问题**: {q['question']}\n\n")
            f.write(f"**建议回答**: {q['answer_hint']}\n\n")
            f.write("---\n\n")
    print(f"  Q&A 报告: {qa_md}")

    # 写时间分配 markdown
    tp_md = output / "time_plan.md"
    with open(tp_md, "w", encoding="utf-8") as f:
        f.write(f"# 答辩时间分配（{args.duration} 分钟版）\n\n")
        f.write("| 阶段 | 占比 | 时间(秒) | 建议页数 |\n")
        f.write("|------|------|---------|---------|\n")
        for phase, b in budget.items():
            if not phase.startswith("_"):
                f.write(f"| {phase} | {b['ratio_pct']}% | {b['seconds']} | {b['pages']} |\n")
        f.write(f"\n**总计**: {budget['_total_seconds']} 秒 / {budget['_total_pages']} 页\n")
    print(f"  时间分配: {tp_md}")

    print(f"\n✅ 答辩素材提取完成 → {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
