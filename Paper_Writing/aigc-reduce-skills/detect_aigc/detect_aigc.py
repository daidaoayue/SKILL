"""
AIGC 检测脚本 — 可移植版（v3）

模型：Hello-SimpleAI/chatgpt-detector-roberta (NeurIPS 2023 SafeNLP / Guo 2023)
  论文："How Close is ChatGPT to Human Experts?"
  支持：中英文双语二分类（human / chatgpt）

用法：
    # 单文件检测（默认按 token 数切块）
    python detect_aigc.py paper.tex
    python detect_aigc.py paper.md

    # 按 section/subsection 切块（LaTeX 专用，输出与 aigc-reduce skill 分块对齐）
    python detect_aigc.py paper.tex --section-split

    # 指定输出目录
    python detect_aigc.py paper.tex --out ./results

    # 批量检测（目录下所有支持的文件）
    python detect_aigc.py ./my_paper/ --batch

    # 对比两次扫描结果（before vs after aigc-reduce）
    python detect_aigc.py after.tex --section-split --compare results/results_before.json

    # 只输出 JSON 到 stdout（供管道使用，不打印报告）
    python detect_aigc.py paper.tex --section-split --stdout-json

⚠️  重要说明：
    本地模型 ≠ CNKI 检测系统。实测本地 2.4% 但 CNKI 15.1% 的情况真实发生过。
    本脚本仅供初筛参考，最终以学校 CNKI 系统为准。

v3 新增功能：
    --section-split  : LaTeX 文件按 \\section/\\subsection 切块，输出 section-level 评分
                       与 aigc-reduce skill 的分块模型对齐，支持精准优先级排序
    --compare FILE   : 与上次扫描结果对比，输出 before/after delta 表格
    --stdout-json    : 将摘要 JSON 输出到 stdout（静默模式，供脚本管道使用）
"""
import re
import json
import argparse
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "Hello-SimpleAI/chatgpt-detector-roberta"
CHUNK_TOKENS = 480      # roberta 最大 512，留 32 给 special tokens
MIN_CHUNK_CHARS = 50    # 太短的尾块直接丢弃

SUPPORTED_EXT = {".tex", ".md", ".txt", ".markdown"}

# AIGC 风险阈值（与 aigc-reduce skill 的优先级排序对齐）
THRESHOLD_HIGH = 0.5    # 高风险（强制处理）
THRESHOLD_MID = 0.3     # 中等风险（建议处理）
THRESHOLD_LOW = 0.1     # 偏高（可选处理）


# ─── 文本预处理 ────────────────────────────────────────────────────────────────

def strip_latex(text: str) -> str:
    """去除 LaTeX 命令，保留纯中英文正文。"""
    text = re.sub(r'(?m)^%.*$', '', text)
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\\(begin|end)\{[^}]+\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+\*?\s*(\[[^\]]*\])?\s*(\{[^}]*\})?', '', text)
    text = re.sub(r'\$[^$]*\$', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def strip_markdown(text: str) -> str:
    """去除 Markdown 标记，保留正文。"""
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def preprocess(text: str, ext: str = ".txt") -> str:
    """根据文件扩展名选择预处理方式。"""
    if ext == ".tex":
        return strip_latex(text)
    elif ext in {".md", ".markdown"}:
        return strip_markdown(text)
    else:
        return re.sub(r'\s+', ' ', text).strip()


# ─── 分块（section-split 模式）────────────────────────────────────────────────

def split_by_sections(raw: str) -> list[dict]:
    """
    LaTeX 专用：按 \\section / \\subsection / \\chapter 切块。
    返回 [{"title": str, "raw": str}, ...] 列表。
    未命中任何 section 则整篇作为单块返回。
    """
    # 匹配 \chapter*, \section*, \subsection*, \subsubsection*（含带 * 的变体）
    pattern = re.compile(
        r'(\\(?:chapter|section|subsection|subsubsection)\*?\s*\{([^}]*)\})',
        re.IGNORECASE
    )
    matches = list(pattern.finditer(raw))

    if not matches:
        return [{"title": "full_document", "raw": raw}]

    sections = []
    for i, m in enumerate(matches):
        title = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        content = raw[start:end]
        sections.append({"title": title, "raw": content})

    # 如果有前言（在第一个 \section 之前），作为 preamble 块
    preamble = raw[:matches[0].start()].strip()
    if len(preamble) > MIN_CHUNK_CHARS:
        sections.insert(0, {"title": "preamble", "raw": preamble})

    return sections


# ─── 分块（token 模式，原有逻辑）──────────────────────────────────────────────

def chunk_text(text: str, tokenizer, max_tokens: int = CHUNK_TOKENS) -> list[str]:
    """按 token 数切块，丢弃过短尾块。"""
    tokens = tokenizer.encode(text, add_special_tokens=False)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        sub = tokens[i:i + max_tokens]
        decoded = tokenizer.decode(sub, skip_special_tokens=True)
        if len(decoded) >= MIN_CHUNK_CHARS:
            chunks.append(decoded)
    return chunks


# ─── 检测 ─────────────────────────────────────────────────────────────────────

def detect_text(model, tokenizer, text: str, device: str) -> dict:
    """对单段文本运行检测，返回 {human_prob, ai_prob}。"""
    model.eval()
    with torch.no_grad():
        inputs = tokenizer(
            text, return_tensors="pt", truncation=True,
            max_length=512, padding=True
        ).to(device)
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
    return {"human_prob": float(probs[0]), "ai_prob": float(probs[1])}


def detect_chunks(model, tokenizer, chunks: list, device: str) -> list:
    """对每块跑检测（token 模式），返回结果列表。"""
    results = []
    for idx, ck in enumerate(chunks):
        scores = detect_text(model, tokenizer, ck, device)
        results.append({
            "chunk_idx": idx,
            "char_len": len(ck),
            **scores,
            "preview": ck[:80] + "..." if len(ck) > 80 else ck,
        })
    return results


def detect_sections(model, tokenizer, sections: list, device: str, ext: str) -> list:
    """
    对 section 列表逐块检测（section-split 模式）。
    每个 section 内部按 token 切块 → 加权平均得 section-level ai_prob。
    """
    results = []
    for sec in sections:
        clean = preprocess(sec["raw"], ext)
        if len(clean) < MIN_CHUNK_CHARS:
            continue
        # section 内部细切块，加权平均
        sub_chunks = chunk_text(clean, tokenizer)
        if not sub_chunks:
            continue
        sub_results = []
        for ck in sub_chunks:
            scores = detect_text(model, tokenizer, ck, device)
            sub_results.append({"char_len": len(ck), **scores})

        total_chars = sum(r["char_len"] for r in sub_results)
        weighted_ai = sum(r["ai_prob"] * r["char_len"] for r in sub_results) / total_chars
        weighted_human = 1.0 - weighted_ai

        results.append({
            "section_title": sec["title"],
            "char_len": total_chars,
            "n_sub_chunks": len(sub_results),
            "ai_prob": weighted_ai,
            "human_prob": weighted_human,
            "risk_label": _risk_label(weighted_ai),
            "sub_chunks": sub_results,
        })
    return results


def compute_summary(results: list, mode: str = "token") -> dict:
    """计算加权平均 AIGC 概率及高风险块统计。"""
    if not results:
        return {"weighted_ai_probability": 0.0, "high_ai_chunk_count": 0,
                "high_ai_chunk_ratio": 0.0, "n_chunks": 0}

    prob_key = "ai_prob"
    total_chars = sum(r["char_len"] for r in results)
    weighted_ai = sum(r[prob_key] * r["char_len"] for r in results) / total_chars
    high_ai = [r for r in results if r[prob_key] >= THRESHOLD_HIGH]
    mid_ai = [r for r in results if THRESHOLD_MID <= r[prob_key] < THRESHOLD_HIGH]

    return {
        "weighted_ai_probability": weighted_ai,
        "high_ai_chunk_count": len(high_ai),
        "mid_ai_chunk_count": len(mid_ai),
        "high_ai_chunk_ratio": len(high_ai) / len(results),
        "n_chunks": len(results),
        "total_chars_clean": total_chars,
        "mode": mode,
    }


# ─── 输出渲染 ─────────────────────────────────────────────────────────────────

def _bar(prob: float, width: int = 20) -> str:
    filled = round(prob * width)
    return "█" * filled + "░" * (width - filled)


def _risk_label(prob: float) -> str:
    if prob < THRESHOLD_LOW:
        return "✅ 安全"
    elif prob < THRESHOLD_MID:
        return "🟡 偏高"
    elif prob < THRESHOLD_HIGH:
        return "🔴 显著"
    else:
        return "🚨 极高"


def print_report_token_mode(file_path: Path, label: str, results: list,
                            summary: dict) -> None:
    """打印 token 切块模式的报告。"""
    wai = summary["weighted_ai_probability"]
    n = summary["n_chunks"]
    high = summary["high_ai_chunk_count"]

    print(f"\n{'='*60}")
    print(f"  文件: {file_path.name}  |  标签: {label}")
    print(f"  模型: {MODEL_NAME}  |  模式: token 切块")
    print(f"{'='*60}")
    print(f"  总字符数（清洗后）: {summary.get('total_chars_clean', 0):,}")
    print(f"  切块数: {n}")
    print(f"  加权平均 AIGC 概率: {wai:.1%}  {_bar(wai)}  {_risk_label(wai)}")
    print(f"  高风险块（≥{THRESHOLD_HIGH:.0%}）: {high}/{n} = {summary['high_ai_chunk_ratio']:.1%}")
    print(f"\n  ⚠️  本地分数 ≠ CNKI 检测分数，最终以学校 CNKI 系统为准")
    print(f"{'='*60}")

    flagged = [r for r in results if r["ai_prob"] >= THRESHOLD_MID]
    if flagged:
        print(f"\n  偏高块明细（ai_prob ≥ {THRESHOLD_MID:.0%}，共 {len(flagged)} 块）:")
        for r in sorted(flagged, key=lambda x: -x["ai_prob"])[:10]:
            bar = _bar(r["ai_prob"], 15)
            print(f"  块 #{r['chunk_idx']:02d}  {r['ai_prob']:.1%} {bar}  {_risk_label(r['ai_prob'])}")
            print(f"         {r['preview']}")
    else:
        print(f"\n  无高风险块（所有块 ai_prob < {THRESHOLD_MID:.0%}）✅")
    print()


def print_report_section_mode(file_path: Path, label: str, results: list,
                               summary: dict) -> None:
    """打印 section 切块模式的报告，含优先级排序表。"""
    wai = summary["weighted_ai_probability"]
    n = summary["n_chunks"]

    print(f"\n{'='*65}")
    print(f"  文件: {file_path.name}  |  标签: {label}")
    print(f"  模型: {MODEL_NAME}  |  模式: section 切块（与 aigc-reduce 对齐）")
    print(f"{'='*65}")
    print(f"  总字符数（清洗后）: {summary.get('total_chars_clean', 0):,}")
    print(f"  section 数: {n}")
    print(f"  全文加权 AIGC 概率: {wai:.1%}  {_bar(wai)}  {_risk_label(wai)}")
    print(f"\n  ⚠️  本地分数 ≠ CNKI 检测分数，最终以学校 CNKI 系统为准")
    print(f"{'='*65}")

    # 按 ai_prob 降序排列，输出优先级处理队列
    sorted_results = sorted(results, key=lambda x: -x["ai_prob"])
    print(f"\n  ── 按 AIGC 风险排序（优先处理高风险 section）──")
    print(f"  {'优先级':<5} {'ai_prob':<9} {'进度条':<22} {'风险':<10} {'section'}")
    print(f"  {'─'*5} {'─'*8} {'─'*21} {'─'*9} {'─'*30}")
    for rank, r in enumerate(sorted_results, 1):
        bar = _bar(r["ai_prob"], 18)
        title_short = r["section_title"][:35] + ("..." if len(r["section_title"]) > 35 else "")
        print(f"  #{rank:<4} {r['ai_prob']:.1%}    {bar}  {r['risk_label']:<10} {title_short}")

    print()
    need_action = [r for r in results if r["ai_prob"] >= THRESHOLD_MID]
    if need_action:
        print(f"  📋 aigc-reduce 建议处理顺序（ai_prob ≥ {THRESHOLD_MID:.0%}，共 {len(need_action)} 个 section）:")
        for rank, r in enumerate(sorted([r for r in results if r["ai_prob"] >= THRESHOLD_MID],
                                         key=lambda x: -x["ai_prob"]), 1):
            print(f"     {rank}. [{r['risk_label']}] {r['section_title']}  ({r['ai_prob']:.1%})")
    else:
        print(f"  ✅ 全部 section ai_prob < {THRESHOLD_MID:.0%}，已达标")
    print()


def print_compare_report(before_data: dict, after_results: list,
                          after_summary: dict, file_path: Path) -> None:
    """打印 before/after 对比报告。"""
    before_wai = before_data.get("weighted_ai_probability", 0)
    after_wai = after_summary["weighted_ai_probability"]
    delta_wai = after_wai - before_wai

    print(f"\n{'='*65}")
    print(f"  ── Before/After 对比报告 ──")
    print(f"  文件: {file_path.name}")
    print(f"{'='*65}")
    print(f"  全文 AIGC 概率: {before_wai:.1%} → {after_wai:.1%}  "
          f"({'↓' if delta_wai < 0 else '↑'}{abs(delta_wai):.1%})")
    print(f"  {'─'*60}")

    before_mode = before_data.get("mode", "token")
    after_mode = after_summary.get("mode", "token")

    if before_mode == "section" and after_mode == "section":
        # section 级别对比
        before_map = {r["section_title"]: r["ai_prob"]
                      for r in before_data.get("section_results", [])}
        print(f"\n  {'section':<35} {'before':>8} {'after':>8} {'delta':>8} {'状态':>6}")
        print(f"  {'─'*35} {'─'*8} {'─'*8} {'─'*8} {'─'*6}")
        for r in sorted(after_results, key=lambda x: -x["ai_prob"]):
            title = r["section_title"]
            after_p = r["ai_prob"]
            before_p = before_map.get(title)
            if before_p is not None:
                delta = after_p - before_p
                arrow = "↓" if delta < 0 else ("↑" if delta > 0 else "─")
                status = "✅" if after_p < THRESHOLD_MID else ("🟡" if after_p < THRESHOLD_HIGH else "🚨")
                title_short = title[:33] + ".." if len(title) > 33 else title
                print(f"  {title_short:<35} {before_p:>7.1%} {after_p:>7.1%} "
                      f"{arrow}{abs(delta):>6.1%} {status:>6}")
            else:
                title_short = title[:33] + ".." if len(title) > 33 else title
                print(f"  {title_short:<35} {'N/A':>8} {after_p:>7.1%} {'─':>8}")
    else:
        print(f"\n  前后扫描模式不同（before={before_mode}, after={after_mode}），仅显示全文汇总")

    print()
    if delta_wai < -0.02:
        print(f"  🎉 AIGC 率显著下降 {abs(delta_wai):.1%}，aigc-reduce 生效")
    elif delta_wai < 0:
        print(f"  ✅ AIGC 率小幅下降 {abs(delta_wai):.1%}")
    elif delta_wai < 0.01:
        print(f"  ⚠️  AIGC 率基本不变，建议继续处理高风险 section")
    else:
        print(f"  ❌ AIGC 率上升 {delta_wai:.1%}，请检查处理是否引入新的 AI 结构")
    print()


# ─── 主入口 ───────────────────────────────────────────────────────────────────

def load_model(device: str):
    """加载模型（会自动缓存到 HuggingFace cache 目录）。"""
    print(f"[模型] 加载 {MODEL_NAME} (device={device})", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)
    return mdl, tok


def detect_file(file_path: Path, label: str, model, tokenizer, device: str,
                out_dir: Path, section_split: bool = False,
                compare_file: Path = None, stdout_json: bool = False) -> dict:
    """检测单个文件，输出 JSON 结果并打印报告。"""
    if not stdout_json:
        print(f"\n[处理] {file_path.name}", flush=True)

    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    ext = file_path.suffix.lower()

    output = {
        "label": label,
        "file": str(file_path),
        "model": MODEL_NAME,
        "device": device,
    }

    if section_split and ext == ".tex":
        # ── Section 切块模式 ──
        sections = split_by_sections(raw)
        if not stdout_json:
            print(f"  按 section 切块：共 {len(sections)} 个 section", flush=True)

        results = detect_sections(model, tokenizer, sections, device, ext)
        if not results:
            if not stdout_json:
                print(f"  ⚠️  切块后无内容，跳过")
            return {}

        summary = compute_summary(results, mode="section")
        output.update({**summary, "section_results": results})

        if not stdout_json:
            print_report_section_mode(file_path, label, results, summary)

        # 对比报告
        if compare_file and compare_file.exists():
            before_data = json.loads(compare_file.read_text(encoding="utf-8"))
            if not stdout_json:
                print_compare_report(before_data, results, summary, file_path)
            output["compare_before_file"] = str(compare_file)
            output["compare_before_wai"] = before_data.get("weighted_ai_probability", None)
            output["compare_delta"] = (summary["weighted_ai_probability"]
                                       - before_data.get("weighted_ai_probability", 0))
    else:
        # ── Token 切块模式（原有逻辑）──
        text = preprocess(raw, ext)
        if not text:
            if not stdout_json:
                print(f"  ⚠️  文件为空或无可检测文本，跳过")
            return {}

        if not stdout_json:
            print(f"  纯文本字符数: {len(text):,}", flush=True)
        chunks = chunk_text(text, tokenizer)
        if not stdout_json:
            print(f"  切分为 {len(chunks)} 块", flush=True)

        if not chunks:
            if not stdout_json:
                print(f"  ⚠️  切块后无内容，跳过")
            return {}

        results = detect_chunks(model, tokenizer, chunks, device)
        summary = compute_summary(results, mode="token")
        output.update({**summary, "per_chunk_results": results})

        if not stdout_json:
            print_report_token_mode(file_path, label, results, summary)

    safe_label = re.sub(r'[^\w\-]', '_', label)
    out_file = out_dir / f"results_{file_path.stem}_{safe_label}.json"
    out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    if not stdout_json:
        print(f"  → 结果保存至: {out_file}")
    else:
        # stdout-json 模式：把摘要 JSON 输出到 stdout
        stdout_summary = {
            "file": str(file_path),
            "label": label,
            "weighted_ai_probability": summary["weighted_ai_probability"],
            "n_chunks": summary["n_chunks"],
            "mode": summary.get("mode", "token"),
            "result_file": str(out_file),
        }
        if section_split and "section_results" in output:
            # 输出 section 级别摘要（供 aigc-reduce skill 直接消费）
            stdout_summary["section_scores"] = [
                {
                    "section_title": r["section_title"],
                    "ai_prob": round(r["ai_prob"], 4),
                    "risk_label": r["risk_label"],
                    "char_len": r["char_len"],
                }
                for r in sorted(output["section_results"], key=lambda x: -x["ai_prob"])
            ]
        print(json.dumps(stdout_summary, ensure_ascii=False, indent=2))

    return output


def main():
    ap = argparse.ArgumentParser(
        description="AIGC 检测工具 v3 — 基于 Hello-SimpleAI/chatgpt-detector-roberta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("input", help="待检测文件（.tex/.md/.txt）或目录路径")
    ap.add_argument("--label", default="detect",
                    help="结果标签（如 baseline / after_reduce）")
    ap.add_argument("--out", default=".", help="JSON 结果输出目录（默认当前目录）")
    ap.add_argument("--batch", action="store_true",
                    help="批量模式：input 为目录，处理其中所有支持文件")
    ap.add_argument("--cpu", action="store_true", help="强制使用 CPU（忽略 CUDA）")
    ap.add_argument("--section-split", action="store_true",
                    help="LaTeX 专用：按 \\section/\\subsection 切块（与 aigc-reduce skill 对齐）")
    ap.add_argument("--compare", metavar="PREV_JSON",
                    help="与上次扫描的 JSON 结果对比，输出 before/after delta 报告")
    ap.add_argument("--stdout-json", action="store_true",
                    help="将摘要 JSON 输出到 stdout（静默模式，供管道使用）")
    args = ap.parse_args()

    # 设备选择
    if args.cpu:
        device = "cpu"
    elif torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    input_path = Path(args.input)
    compare_file = Path(args.compare) if args.compare else None

    # 收集待检测文件
    if args.batch:
        if not input_path.is_dir():
            print(f"错误: --batch 模式需要目录路径，但 '{input_path}' 不是目录")
            sys.exit(1)
        files = [f for f in sorted(input_path.iterdir())
                 if f.suffix.lower() in SUPPORTED_EXT]
        if not files:
            print(f"目录 '{input_path}' 中没有支持的文件（{', '.join(SUPPORTED_EXT)}）")
            sys.exit(1)
    else:
        if not input_path.exists():
            print(f"错误: 文件不存在: '{input_path}'")
            sys.exit(1)
        if input_path.suffix.lower() not in SUPPORTED_EXT:
            print(f"警告: 不支持的扩展名 '{input_path.suffix}'，将尝试以纯文本处理")
        files = [input_path]

    # 加载模型（只加载一次）
    if not args.stdout_json:
        model, tokenizer = load_model(device)
    else:
        # stdout-json 模式静默加载
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            model, tokenizer = load_model(device)

    # 逐文件检测
    all_results = []
    for fp in files:
        label = args.label if len(files) == 1 else fp.stem
        r = detect_file(fp, label, model, tokenizer, device, out_dir,
                        section_split=args.section_split,
                        compare_file=compare_file,
                        stdout_json=args.stdout_json)
        if r:
            all_results.append(r)

    # 批量汇总（仅非 stdout-json 模式）
    if len(all_results) > 1 and not args.stdout_json:
        print(f"\n{'='*60}")
        print(f"  批量汇总（{len(all_results)} 个文件）")
        print(f"{'='*60}")
        for r in sorted(all_results, key=lambda x: -x["weighted_ai_probability"]):
            wai = r["weighted_ai_probability"]
            name = Path(r["file"]).name
            print(f"  {wai:.1%}  {_bar(wai, 15)}  {_risk_label(wai)}  {name}")
        print()


if __name__ == "__main__":
    main()
