"""
AIGC 检测脚本 — 可移植版（v2）

模型：Hello-SimpleAI/chatgpt-detector-roberta (NeurIPS 2023 SafeNLP / Guo 2023)
  论文："How Close is ChatGPT to Human Experts?"
  支持：中英文双语二分类（human / chatgpt）

用法：
    # 单文件检测
    python detect_aigc.py paper.tex
    python detect_aigc.py paper.md
    python detect_aigc.py paper.txt

    # 指定输出目录
    python detect_aigc.py paper.tex --out ./results

    # 批量检测（目录下所有支持的文件）
    python detect_aigc.py ./my_paper/ --batch

    # 对比两版本
    python detect_aigc.py before.tex --label baseline
    python detect_aigc.py after.tex  --label after_reduce

⚠️  重要说明：
    本地模型 ≠ CNKI 检测系统。实测本地 2.4% 但 CNKI 15.1% 的情况真实发生过。
    本脚本仅供初筛参考，最终以学校 CNKI 系统为准。
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


def preprocess(file_path: Path) -> str:
    """根据文件扩展名选择预处理方式。"""
    raw = file_path.read_text(encoding="utf-8", errors="ignore")
    ext = file_path.suffix.lower()
    if ext == ".tex":
        return strip_latex(raw)
    elif ext in {".md", ".markdown"}:
        return strip_markdown(raw)
    else:
        return re.sub(r'\s+', ' ', raw).strip()


# ─── 分块 ─────────────────────────────────────────────────────────────────────

def chunk_text(text: str, tokenizer, max_tokens: int = CHUNK_TOKENS):
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

def detect_chunks(model, tokenizer, chunks: list, device: str) -> list:
    """对每块跑检测，返回结果列表。"""
    results = []
    model.eval()
    with torch.no_grad():
        for idx, ck in enumerate(chunks):
            inputs = tokenizer(
                ck, return_tensors="pt", truncation=True,
                max_length=512, padding=True
            ).to(device)
            logits = model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).cpu().numpy()[0]
            # label_0 = human, label_1 = chatgpt（按 model card 顺序）
            results.append({
                "chunk_idx": idx,
                "char_len": len(ck),
                "human_prob": float(probs[0]),
                "ai_prob": float(probs[1]),
                "preview": ck[:80] + "..." if len(ck) > 80 else ck,
            })
    return results


def compute_summary(results: list) -> dict:
    """计算加权平均 AIGC 概率及高风险块统计。"""
    if not results:
        return {"weighted_ai_probability": 0.0, "high_ai_chunk_count": 0,
                "high_ai_chunk_ratio": 0.0, "n_chunks": 0}
    total_chars = sum(r["char_len"] for r in results)
    weighted_ai = sum(r["ai_prob"] * r["char_len"] for r in results) / total_chars
    high_ai = [r for r in results if r["ai_prob"] >= 0.5]
    return {
        "weighted_ai_probability": weighted_ai,
        "high_ai_chunk_count": len(high_ai),
        "high_ai_chunk_ratio": len(high_ai) / len(results),
        "n_chunks": len(results),
        "total_chars_clean": total_chars,
    }


# ─── 输出渲染 ─────────────────────────────────────────────────────────────────

def _bar(prob: float, width: int = 20) -> str:
    filled = round(prob * width)
    return "█" * filled + "░" * (width - filled)


def _risk_label(prob: float) -> str:
    if prob < 0.1:
        return "✅ 安全"
    elif prob < 0.3:
        return "🟡 偏高"
    elif prob < 0.5:
        return "🔴 显著"
    else:
        return "🚨 极高"


def print_report(file_path: Path, label: str, results: list, summary: dict) -> None:
    """打印彩色控制台报告。"""
    wai = summary["weighted_ai_probability"]
    n = summary["n_chunks"]
    high = summary["high_ai_chunk_count"]

    print(f"\n{'='*60}")
    print(f"  文件: {file_path.name}  |  标签: {label}")
    print(f"  模型: {MODEL_NAME}")
    print(f"{'='*60}")
    print(f"  总字符数（清洗后）: {summary.get('total_chars_clean', 0):,}")
    print(f"  切块数: {n}")
    print(f"  加权平均 AIGC 概率: {wai:.1%}  {_bar(wai)}  {_risk_label(wai)}")
    print(f"  高风险块（≥0.5）: {high}/{n} = {summary['high_ai_chunk_ratio']:.1%}")
    print(f"\n  ⚠️  本地分数 ≠ CNKI 检测分数，最终以学校 CNKI 系统为准")
    print(f"{'='*60}")

    # 列出高风险块明细
    flagged = [r for r in results if r["ai_prob"] >= 0.3]
    if flagged:
        print(f"\n  偏高块明细（ai_prob ≥ 0.3，共 {len(flagged)} 块）:")
        for r in sorted(flagged, key=lambda x: -x["ai_prob"])[:10]:
            bar = _bar(r["ai_prob"], 15)
            print(f"  块 #{r['chunk_idx']:02d}  {r['ai_prob']:.1%} {bar}  {_risk_label(r['ai_prob'])}")
            print(f"         {r['preview']}")
    else:
        print("\n  无高风险块（所有块 ai_prob < 0.3）✅")
    print()


# ─── 主入口 ───────────────────────────────────────────────────────────────────

def load_model(device: str):
    """加载模型（会自动缓存到 HuggingFace cache 目录）。"""
    print(f"[模型] 加载 {MODEL_NAME} (device={device})", flush=True)
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME).to(device)
    return mdl, tok


def detect_file(file_path: Path, label: str, model, tokenizer, device: str,
                out_dir: Path) -> dict:
    """检测单个文件，输出 JSON 结果并打印报告。"""
    print(f"\n[处理] {file_path.name}", flush=True)

    text = preprocess(file_path)
    if not text:
        print(f"  ⚠️  文件为空或无可检测文本，跳过")
        return {}

    print(f"  纯文本字符数: {len(text):,}", flush=True)
    chunks = chunk_text(text, tokenizer)
    print(f"  切分为 {len(chunks)} 块", flush=True)

    if not chunks:
        print(f"  ⚠️  切块后无内容，跳过")
        return {}

    results = detect_chunks(model, tokenizer, chunks, device)
    summary = compute_summary(results)
    print_report(file_path, label, results, summary)

    output = {
        "label": label,
        "file": str(file_path),
        "model": MODEL_NAME,
        "device": device,
        **summary,
        "per_chunk_results": results,
    }

    safe_label = re.sub(r'[^\w\-]', '_', label)
    out_file = out_dir / f"results_{file_path.stem}_{safe_label}.json"
    out_file.write_text(json.dumps(output, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"  → 结果保存至: {out_file}")
    return output


def main():
    ap = argparse.ArgumentParser(
        description="AIGC 检测工具 — 基于 Hello-SimpleAI/chatgpt-detector-roberta",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("input", help="待检测文件（.tex/.md/.txt）或目录路径")
    ap.add_argument("--label", default="detect", help="结果标签（如 baseline / after_reduce）")
    ap.add_argument("--out", default=".", help="JSON 结果输出目录（默认当前目录）")
    ap.add_argument("--batch", action="store_true",
                    help="批量模式：input 为目录，处理其中所有支持文件")
    ap.add_argument("--cpu", action="store_true", help="强制使用 CPU（忽略 CUDA）")
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
    model, tokenizer = load_model(device)

    # 逐文件检测
    all_results = []
    for fp in files:
        label = args.label if len(files) == 1 else fp.stem
        r = detect_file(fp, label, model, tokenizer, device, out_dir)
        if r:
            all_results.append(r)

    # 批量汇总
    if len(all_results) > 1:
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
