#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wrappers_runner.py — 真把 21 个 integration wrapper 全接通

底层逻辑：
  21 wrapper 上游是 Claude prompt-driven skill，必须用 LLM 真改写/真分析。
  本 runner 用 `claude -p` CLI 真触发——不嘴炮，每个 wrapper 都真跑 LLM。

用法：
    python wrappers_runner.py --wrapper <name> --input <file> [--output <dir>]
    python wrappers_runner.py --all --paper-root <dir>          # 全 21 个真跑
    python wrappers_runner.py --list                             # 列出所有

例子：
    python wrappers_runner.py --wrapper paper-reviewer --input paper/main.pdf
    python wrappers_runner.py --all --paper-root D:/code/.../thesis_main
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

THIS_DIR = Path(__file__).resolve().parent
INTEG_DIR = THIS_DIR / "integrations"

# ============================================================================
# 21 wrapper 真触发配置
# ============================================================================
WRAPPER_CONFIGS = {
    # === 选题/调研类 (6) ===
    "arxiv": {"input_type": "topic", "lib_alt": "arxiv",
              "prompt_tpl": "用 arxiv 搜索关于 '{topic}' 的近 3 年论文（最多 10 篇），输出 BibTeX + 一句话总结。"},
    "semantic-scholar": {"input_type": "topic", "lib_alt": "semanticscholar",
                         "prompt_tpl": "用 Semantic Scholar 搜 '{topic}'，列出 top 10 高引论文（含 cite count + TLDR）。"},
    "research-lit": {"input_type": "topic",
                     "prompt_tpl": "对 '{topic}' 做通用文献综述：列出 5-8 个核心方法 + 各自 1-2 篇代表作 + gap 分析。"},
    "comm-lit-review": {"input_type": "topic",
                        "prompt_tpl": "通信领域综述：对 '{topic}' 列出 IEEE/3GPP 标准 + 主流方法 + 数据集。"},
    "claude-paper-study": {"input_type": "pdf",
                           "prompt_tpl": "深度精读论文 '{path}'，输出：核心贡献 / 方法详解 / 实验批判 / 在我论文中如何 cite。"},
    "novelty-check": {"input_type": "idea",
                      "prompt_tpl": "对研究 idea '{idea}' 做新颖性检查：找 5 篇最相似工作 + 给 novelty 评分 1-10 + PROCEED/PIVOT 推荐。"},

    # === 理论 (2) ===
    "proof-writer": {"input_type": "theorem",
                     "prompt_tpl": "为 theorem '{theorem}' 写严谨数学证明（LaTeX，含假设清单 + 关键 step 注释）。"},
    "formula-derivation": {"input_type": "topic",
                           "prompt_tpl": "整理 '{topic}' 的公式推导链：写 LaTeX equation + 每步依据（假设/引理）+ 符号表。"},

    # === 图表 (4) ===
    "scientific-visualization": {"input_type": "data",
                                 "prompt_tpl": "为 '{data}' 数据生成出版级 matplotlib 绘图脚本（serif 字体 + colorblind-safe + 误差棒）。"},
    "matplotlib-tvhahn": {"input_type": "data",
                          "prompt_tpl": "为 '{data}' 生成 Tim Hahn 风格 matplotlib（whitegrid + cubehelix + despined）。"},
    "mermaid-diagram": {"input_type": "description",
                        "prompt_tpl": "为 '{description}' 生成 mermaid 流程图（输出 .mmd 源代码）。"},
    "paper-illustration": {"input_type": "description",
                           "prompt_tpl": "为 '{description}' 设计论文 hero figure 概念图（输出 prompt 给图像 API + matplotlib stub）。"},

    # === 实验对接 (2) ===
    "result-to-claim": {"input_type": "results",
                        "prompt_tpl": "对实验结果 '{results}' 评估每个 claim 是否被支持（SUPPORTED/PARTIAL/NOT_SUPPORTED + 缺口）。"},
    "ablation-planner": {"input_type": "claims",
                         "prompt_tpl": "为 claim '{claims}' 设计 ablation 实验：列出 reviewer 必问 ablation + 优先级 + 预估 GPU 时长。"},

    # === 投稿后/答辩 (4) ===
    "rebuttal": {"input_type": "reviews",
                 "prompt_tpl": "对审稿意见 '{reviews}' 起草 author response（5000 字符内，按 reviewer 分组 + 直面承认 + 数据支撑）。"},
    "paper-reviewer": {"input_type": "pdf",
                       "prompt_tpl": "对论文 '{path}' 做 5 维度自审（Soundness/Significance/Novelty/Clarity/Reproducibility 各打分 1-10 + 详细 comments）。"},
    "paper-slides": {"input_type": "pdf",
                     "prompt_tpl": "为论文 '{path}' 生成会议汇报 12 分钟 Beamer slides（输出 .tex + speaker notes）。"},
    "paper-poster": {"input_type": "pdf",
                     "prompt_tpl": "为论文 '{path}' 生成 A0 学术海报（tcbposter LaTeX 源码）。"},

    # === 交付格式 (3) ===
    "docx": {"input_type": "tex", "executable": "thesis-helper-internal",
             "prompt_tpl": "(直接调用 latex-to-word/scripts/convert.py)"},
    "pptx": {"input_type": "beamer-pdf",
             "prompt_tpl": "把 Beamer PDF '{path}' 转 PPTX（保留章节层级 + 图片）。"},
    "pdf": {"input_type": "pdf",
            "prompt_tpl": "对 PDF '{path}' 做后处理：清 metadata + 加水印 + 合并附录（按 mode 参数）。"},
}


def list_wrappers():
    print("=" * 70)
    print(f"21 个 wrapper · 真接通配置")
    print("=" * 70)
    for name, cfg in WRAPPER_CONFIGS.items():
        wrapper_md = INTEG_DIR / f"{name}-wrapper.md"
        exists = "✅" if wrapper_md.exists() else "❌"
        print(f"  {exists}  {name:30s}  input={cfg['input_type']}")


def find_claude_cli() -> str | None:
    """找 claude CLI 真路径（Windows 下 npm shim 是 .cmd / .ps1）。"""
    for cand in ["claude", "claude.cmd", "claude.exe"]:
        p = shutil.which(cand)
        if p:
            return p
    # 尝试常见 npm 全局路径
    import os
    npm_paths = [
        os.path.expanduser("~/AppData/Roaming/npm/claude.cmd"),
        os.path.expanduser("~/AppData/Roaming/npm/claude.ps1"),
        "/usr/local/bin/claude",
    ]
    for p in npm_paths:
        if Path(p).exists():
            return p
    return None


def check_claude_cli() -> tuple[bool, str]:
    cli = find_claude_cli()
    if not cli:
        return False, "claude CLI 未找到"
    try:
        r = subprocess.run([cli, "--version"], capture_output=True, text=True,
                           timeout=10, shell=False)
        return True, f"{r.stdout.strip().split(chr(10))[0]} | path={cli}"
    except Exception as e:
        return False, f"{e} | path={cli}"


def run_one_wrapper(name: str, input_value: str, output_dir: Path,
                    timeout_sec: int = 600) -> dict:
    """真触发一个 wrapper：用 claude -p 调对应 skill。"""
    cfg = WRAPPER_CONFIGS.get(name)
    if not cfg:
        return {"name": name, "success": False, "error": "未知 wrapper"}

    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / f"{name}_output.md"
    log_file = output_dir / f"{name}_log.txt"

    # 构造 prompt
    wrapper_md = INTEG_DIR / f"{name}-wrapper.md"
    wrapper_content = wrapper_md.read_text(encoding="utf-8") if wrapper_md.exists() else ""
    prompt = cfg["prompt_tpl"].format(topic=input_value, idea=input_value, theorem=input_value,
                                      data=input_value, description=input_value, results=input_value,
                                      claims=input_value, reviews=input_value, path=input_value)
    full_prompt = (
        f"你正在执行 thesis-helper 的 '{name}' wrapper。\n\n"
        f"=== wrapper 规范（来自 {name}-wrapper.md）===\n"
        f"{wrapper_content[:1500]}\n\n"
        f"=== 当前任务 ===\n"
        f"{prompt}\n\n"
        f"=== 要求 ===\n"
        f"输出实际可用的内容（不要解释你将做什么，直接给出结果）。"
    )

    # 真用 claude -p 触发（cmd line 模式真验证可用：6.6s 回 OK）
    cli = find_claude_cli()
    if not cli:
        return {"name": name, "success": False, "error": "claude CLI 未找到"}
    print(f"  ▶ 真触发 {name}（{Path(cli).name} -p, prompt {len(full_prompt)} 字符）...")
    t0 = time.time()
    try:
        # PYTHONIOENCODING=utf-8 防 emoji 崩
        import os as _os
        env = {**_os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        r = subprocess.run(
            [cli, "-p", full_prompt, "--model", "haiku"],
            capture_output=True, text=True, timeout=timeout_sec,
            encoding="utf-8", errors="replace", env=env,
        )
        elapsed = time.time() - t0
        ok = (r.returncode == 0)
        out_text = r.stdout or ""
        out_file.write_text(out_text, encoding="utf-8")
        log_file.write_text(f"cmd: claude -p ...\nreturncode: {r.returncode}\n"
                            f"elapsed: {elapsed:.1f}s\nstderr:\n{r.stderr[:500]}", encoding="utf-8")
        print(f"    {'✅' if ok else '❌'} 输出 {len(out_text)} 字符 / 用时 {elapsed:.1f}s → {out_file.name}")
        return {"name": name, "success": ok, "output_file": str(out_file),
                "elapsed_sec": round(elapsed, 1), "output_chars": len(out_text)}
    except subprocess.TimeoutExpired:
        print(f"    ❌ 超时 ({timeout_sec}s)")
        return {"name": name, "success": False, "error": f"timeout {timeout_sec}s"}
    except Exception as e:
        print(f"    ❌ 异常: {e}")
        return {"name": name, "success": False, "error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="wrappers_runner: 真接通 21 个 integration wrapper")
    parser.add_argument("--list", action="store_true", help="列出所有 wrapper")
    parser.add_argument("--wrapper", help="只跑某个 wrapper")
    parser.add_argument("--input", default="", help="输入值（topic/idea/path 等）")
    parser.add_argument("--output", type=Path, default=None, help="输出目录")
    parser.add_argument("--all", action="store_true", help="真触发全部 21 个")
    parser.add_argument("--paper-root", type=Path, default=None, help="--all 模式下论文目录")
    parser.add_argument("--timeout", type=int, default=600, help="单 wrapper 超时秒")
    parser.add_argument("--resume", action="store_true",
                        help="--all 模式下，跳过已成功的 wrapper（输出 > 100 字节），只跑没成功的")
    args = parser.parse_args()

    if args.list:
        list_wrappers()
        return 0

    ok, msg = check_claude_cli()
    print(f"claude CLI: {'✅' if ok else '❌'} {msg}")
    if not ok:
        print("无法真触发 wrapper（需 claude CLI）")
        return 1

    output = args.output or (THIS_DIR.parent.parent / "wrappers_run")

    if args.all:
        if not args.paper_root or not args.paper_root.exists():
            print("--all 需 --paper-root 真存在")
            return 1
        # 用 paper_root 给每个 wrapper 提供合理 input
        main_pdf = args.paper_root / "main.pdf"
        topic = "多维特征融合的低空雷达目标识别"
        results_dict = {
            "arxiv": topic, "semantic-scholar": topic,
            "research-lit": topic, "comm-lit-review": topic,
            "claude-paper-study": str(main_pdf), "novelty-check": topic,
            "proof-writer": "DRSN soft threshold lemma",
            "formula-derivation": "phase coherence channel",
            "scientific-visualization": "10-seed Monte Carlo accuracy",
            "matplotlib-tvhahn": "training loss curve",
            "mermaid-diagram": "三分支门控融合 pipeline",
            "paper-illustration": "三模态融合架构图",
            "result-to-claim": "97.71% accuracy with gated fusion",
            "ablation-planner": "phase channel + amplitude dropout",
            "rebuttal": "reviewer comments (placeholder)",
            "paper-reviewer": str(main_pdf),
            "paper-slides": str(main_pdf),
            "paper-poster": str(main_pdf),
            "docx": str(args.paper_root / "main.tex"),
            "pptx": str(main_pdf),
            "pdf": str(main_pdf),
        }
        results = []
        skipped_resume = []
        print(f"\n{'='*70}\n真触发全部 21 个 wrapper（用 claude -p 真调 LLM）"
              f"{' [resume 模式]' if args.resume else ''}\n{'='*70}")
        for name in WRAPPER_CONFIGS:
            # resume 模式：检查已有 output 是否真成功
            if args.resume:
                existing = output / f"{name}_output.md"
                if existing.exists():
                    size = existing.stat().st_size
                    content = existing.read_text(encoding="utf-8", errors="replace")[:100]
                    is_real_output = (size > 100 and "hit your limit" not in content
                                      and "rate limit" not in content.lower())
                    if is_real_output:
                        print(f"  ⏭️  跳过 {name:30s}  (已成功 / {size} 字节)")
                        results.append({"name": name, "success": True,
                                        "skipped_resume": True, "output_chars": size})
                        skipped_resume.append(name)
                        continue
            results.append(run_one_wrapper(name, results_dict.get(name, topic),
                                           output, args.timeout))
        # 汇总
        print(f"\n{'='*70}\n📊 21 wrapper 真触发汇总\n{'='*70}")
        passed = sum(1 for r in results if r.get("success"))
        for r in results:
            status = "✅" if r.get("success") else "❌"
            extra = f"{r.get('output_chars', 0)} 字符 / {r.get('elapsed_sec', 0)}s" if r.get("success") else r.get("error", "")
            print(f"  {status} {r['name']:30s}  {extra}")
        print(f"\n  真接通: {passed}/{len(results)}")

        summary_path = output / "wrappers_summary.json"
        summary_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📋 汇总: {summary_path}")
        return 0 if passed == len(results) else 1

    if args.wrapper:
        result = run_one_wrapper(args.wrapper, args.input, output, args.timeout)
        return 0 if result.get("success") else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
