#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build.py — thesis-helper 跨平台编译器主入口

把 Claude SKILL.md 真源编译到各 AI 平台的对应入口格式：

    Source: thesis-helper/SKILL.md (+ 整个 thesis-helper/ 目录)
       │
       ├──> claude    → ~/.claude/skills/thesis-helper/  (整个目录复制)
       ├──> cursor    → <project>/.cursorrules            (单文件)
       ├──> gemini    → <project>/GEMINI.md               (单文件)
       ├──> cline     → <project>/.clinerules             (单文件)
       ├──> chatgpt   → thesis-helper-gpt-instructions.md (≤ 4096 字符)
       └──> universal → thesis-prompt-pack.md             (任意 AI 复制粘贴)

用法：
    python build.py --target cursor --output D:/my-project/.cursorrules
    python build.py --target all --output-dir D:/my-project/
    python build.py --target claude --install   # 直接装到 ~/.claude/skills/
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = SCRIPT_DIR.parent  # thesis-helper/

# 把 targets 加到 sys.path，便于动态导入
sys.path.insert(0, str(SCRIPT_DIR))

SUPPORTED_TARGETS = ["claude", "cursor", "gemini", "cline", "chatgpt", "universal"]


def build_one(target: str, output_path: Path | None, install: bool = False) -> Path:
    """编译单个 target，返回输出路径。"""
    if target not in SUPPORTED_TARGETS:
        raise ValueError(f"Unsupported target: {target}. Choose from {SUPPORTED_TARGETS}")

    # 动态导入对应 target 模块
    target_module = __import__(f"targets.{target}", fromlist=[target])

    if hasattr(target_module, "build"):
        return target_module.build(SOURCE_DIR, output_path, install=install)
    raise RuntimeError(f"Target module {target} missing build()")


def build_all(output_dir: Path) -> dict[str, Path]:
    """编译所有 target 到一个目录。"""
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, Path] = {}
    for target in SUPPORTED_TARGETS:
        if target == "claude":
            # claude 是目录复制模式，单独处理
            sub_out = output_dir / "claude" / "thesis-helper"
            results[target] = build_one(target, sub_out, install=False)
        else:
            ext_map = {
                "cursor": ".cursorrules",
                "gemini": "GEMINI.md",
                "cline": ".clinerules",
                "chatgpt": "thesis-helper-gpt-instructions.md",
                "universal": "thesis-prompt-pack.md",
            }
            out_name = ext_map.get(target, f"{target}.md")
            sub_out = output_dir / out_name
            results[target] = build_one(target, sub_out, install=False)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="thesis-helper cross-platform compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python build.py --target cursor --output D:/proj/.cursorrules\n"
               "  python build.py --target gemini --output D:/proj/GEMINI.md\n"
               "  python build.py --target chatgpt --output gpt-instructions.md\n"
               "  python build.py --target claude --install\n"
               "  python build.py --target all --output-dir D:/proj/\n",
    )
    parser.add_argument("--target", required=True,
                        choices=SUPPORTED_TARGETS + ["all"],
                        help="Target platform")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output file path (single target mode)")
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Output directory (--target all mode)")
    parser.add_argument("--install", action="store_true",
                        help="(claude only) Install directly to ~/.claude/skills/")
    args = parser.parse_args()

    if args.target == "all":
        if not args.output_dir:
            print("Error: --target all requires --output-dir", file=sys.stderr)
            return 1
        results = build_all(args.output_dir)
        print("[build] All targets compiled:")
        for t, p in results.items():
            print(f"  {t:10s} → {p}")
        return 0

    if args.target == "claude" and args.install:
        out = build_one("claude", None, install=True)
        print(f"[build] Installed to: {out}")
        return 0

    if not args.output:
        print(f"Error: --target {args.target} requires --output (or --install for claude)",
              file=sys.stderr)
        return 1

    out = build_one(args.target, args.output, install=False)
    print(f"[build] {args.target} compiled → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
