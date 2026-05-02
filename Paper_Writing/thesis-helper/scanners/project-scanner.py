#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
project-scanner.py — thesis-helper 项目资产扫描器

用途：智能识别用户论文项目目录中的所有资产，输出 ProjectMap.json。
不要求用户单独整理"数据/结果"目录——主动按规则扫描。

用法：
    python project-scanner.py <project_root> [--config thesis.config.yml]

输出：
    <project_root>/.thesis-helper/project_map.json

资产类型识别规则（命中即归类，按顺序匹配）：
    格式要求 / 参考文献 / 数据 / 图表源 / 实验日志 / 已有写作 / 工程代码
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# ---------- 默认配置 ----------

DEFAULT_EXCLUDES = {
    # 工程通用
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".idea", ".vscode", ".pytest_cache",
    ".thesis-helper", ".mypy_cache", ".ruff_cache", ".tox",
    "site-packages", ".next", "target",
    # ML/数据科学（v0.2 新增·防止 dataset 全量收录）
    "dataset", "datasets", "raw_data", "raw", "samples", "snapshots",
    "captures", "recordings", "weights", "checkpoints", "ckpt",
    "models", "pretrained", "cache", "tmp", "temp", "wandb",
    "rknn_outputs", "rknn_cache", "tensorboard_logs",
    # 雷达/特定项目（基于真实项目踩坑）
    "MC10", "mc10", "mc_data", "iq_data", "raw_iq",
}

DEFAULT_DATA_FILE_MAX_MB = 100   # 单文件大小上限，避免误扫大模型权重
DEFAULT_LIST_TRUNCATE_MAX = 200  # 每类列表最大长度，超过截断（防止 ProjectMap.json 爆炸）

# 路径关键词 → 资产类型（顺序匹配）
PATH_KEYWORD_RULES = [
    # (类型, 路径关键词列表 — 大小写不敏感)
    ("format_rules", [
        "格式要求", "format", "template", "templates",
        "模板", "latex模板", "论文模板", "毕设模板",   # v0.3 新增（中文）
    ]),
    ("references", ["refs", "references", "bib", "参考文献"]),
    ("data_files", ["data", "results", "output", "outputs", "数据"]),
    ("figure_sources", ["figs", "figures", "plots", "图", "figure"]),
    ("result_logs", ["logs", "wandb", "runs", "logging", "tensorboard"]),
]

# 强制优先后缀（不论路径，命中后缀直接归类，覆盖 PATH_KEYWORD_RULES）
# v0.3 新增·真实项目实测发现 LaTeX 学校模板被漏识别
PRIORITY_SUFFIX_RULES: dict[str, str] = {
    ".cls": "format_rules",      # LaTeX 文档类（学校模板核心）
    ".sty": "format_rules",      # LaTeX style package
    ".bst": "format_rules",      # BibTeX style file (gbt7714.bst 等)
    ".dotx": "format_rules",     # Word template
    ".dot": "format_rules",      # Word 97-2003 template
}

# 文件后缀 → 资产类型（在路径未命中时兜底）
SUFFIX_RULES: dict[str, str] = {
    # 数据
    ".csv": "data_files", ".tsv": "data_files",
    ".json": "data_files", ".jsonl": "data_files",
    ".npz": "data_files", ".npy": "data_files",
    ".h5": "data_files", ".hdf5": "data_files",
    ".mat": "data_files", ".parquet": "data_files",
    ".pkl": "data_files", ".pickle": "data_files",
    # 参考文献
    ".bib": "references", ".enl": "references", ".enw": "references",
    ".ris": "references",
    # 图（图片本身）
    ".png": "figure_sources", ".jpg": "figure_sources",
    ".jpeg": "figure_sources", ".svg": "figure_sources",
    ".eps": "figure_sources", ".tiff": "figure_sources",
    # 实验日志
    ".log": "result_logs", ".out": "result_logs",
    # 已有写作
    ".tex": "existing_writing", ".md": "existing_writing",
    ".docx": "existing_writing", ".doc": "existing_writing",
    ".rmd": "existing_writing",
    # 工程代码（最后兜底）
    ".py": "code_files", ".cpp": "code_files", ".c": "code_files",
    ".h": "code_files", ".hpp": "code_files", ".cu": "code_files",
    ".m": "code_files", ".ipynb": "code_files",
    ".js": "code_files", ".ts": "code_files", ".jsx": "code_files",
    ".tsx": "code_files", ".java": "code_files", ".go": "code_files",
    ".rs": "code_files", ".sh": "code_files", ".ps1": "code_files",
    ".yaml": "code_files", ".yml": "code_files", ".toml": "code_files",
    ".r": "code_files",
}

# PDF 单独判断：在 refs/ 下归 references，否则归 figure_sources
PDF_SUFFIX = ".pdf"


# ---------- 核心逻辑 ----------

def load_config(config_path: Path | None) -> dict[str, Any]:
    """读取 thesis.config.yml，无则用默认值。

    用户配置的 scan_excludes 会与默认 excludes **合并**（而非覆盖），
    避免用户少写一两个就把 ML 数据集全收录了。
    """
    cfg: dict[str, Any] = {
        "advanced": {
            "scan_excludes": list(DEFAULT_EXCLUDES),
            "data_file_max_mb": DEFAULT_DATA_FILE_MAX_MB,
            "list_truncate_max": DEFAULT_LIST_TRUNCATE_MAX,
        },
    }
    if config_path is None or not config_path.exists():
        return cfg
    try:
        import yaml  # type: ignore
        with open(config_path, "r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
        adv = user_cfg.get("advanced", {})
        if "scan_excludes" in adv:
            # 合并：默认 + 用户，去重
            cfg["advanced"]["scan_excludes"] = sorted(set(DEFAULT_EXCLUDES) | set(adv["scan_excludes"]))
        if "data_file_max_mb" in adv:
            cfg["advanced"]["data_file_max_mb"] = adv["data_file_max_mb"]
        if "list_truncate_max" in adv:
            cfg["advanced"]["list_truncate_max"] = adv["list_truncate_max"]
    except ImportError:
        print("[scanner] PyYAML not installed, using defaults.", file=sys.stderr)
    except Exception as e:
        print(f"[scanner] Failed to parse config: {e}", file=sys.stderr)
    return cfg


def classify_path(rel_path: Path, file_size_bytes: int, max_data_size_mb: int) -> str | None:
    """
    判定文件归属。返回类型字符串或 None（跳过）。

    优先级（v0.3 修订）：
      0. PRIORITY_SUFFIX_RULES（最高，.cls/.sty/.bst/.dotx 直接归 format_rules）
      1. 路径关键词
      2. 普通后缀（PDF 特殊处理）

    超大文件（>max_data_size_mb）若是数据类，仍归数据但加标记由调用方处理。
    """
    path_str_lower = str(rel_path).lower()
    suffix_lower = rel_path.suffix.lower()

    # 0. 强制优先后缀（v0.3 新增·覆盖路径规则）
    if suffix_lower in PRIORITY_SUFFIX_RULES:
        return PRIORITY_SUFFIX_RULES[suffix_lower]

    # 1. 路径关键词匹配（顺序优先）
    for category, keywords in PATH_KEYWORD_RULES:
        for kw in keywords:
            kw_lower = kw.lower()
            # 关键词须作为路径段出现
            parts = path_str_lower.replace("\\", "/").split("/")
            if any(kw_lower in part for part in parts[:-1]):
                # 路径命中，但还要看后缀是否合理
                suffix = rel_path.suffix.lower()
                if category == "format_rules":
                    return "format_rules"
                if category == "references" and suffix in {".bib", ".enl", ".enw", ".ris", ".pdf"}:
                    return "references"
                if category == "data_files" and suffix in {
                    ".csv", ".tsv", ".json", ".jsonl", ".npz", ".npy",
                    ".h5", ".hdf5", ".mat", ".parquet", ".pkl", ".pickle",
                }:
                    return "data_files"
                if category == "figure_sources" and suffix in {
                    ".png", ".jpg", ".jpeg", ".svg", ".eps", ".tiff", ".pdf", ".py",
                }:
                    return "figure_sources"
                if category == "result_logs" and suffix in {".log", ".out", ".txt"}:
                    return "result_logs"

    # 2. 后缀兜底
    suffix = rel_path.suffix.lower()
    if suffix == PDF_SUFFIX:
        # PDF 不在 refs/ 下默认当成 figure
        return "figure_sources"
    if suffix in SUFFIX_RULES:
        category = SUFFIX_RULES[suffix]
        # 大文件保护：data_files 超过阈值不收录（避免扫到大模型权重）
        if category == "data_files":
            if file_size_bytes > max_data_size_mb * 1024 * 1024:
                return None
        return category
    return None


def scan_project(project_root: Path, config: dict[str, Any]) -> dict[str, Any]:
    """扫描项目根目录，返回 ProjectMap dict。"""
    excludes = set(config["advanced"]["scan_excludes"])
    max_data_mb = config["advanced"]["data_file_max_mb"]

    project_map: dict[str, list[str]] = {
        "code_files": [],
        "data_files": [],
        "figure_sources": [],
        "result_logs": [],
        "existing_writing": [],
        "format_rules": [],
        "references": [],
    }

    skipped_too_large: list[str] = []
    total_files_scanned = 0

    for path in project_root.rglob("*"):
        # 跳过目录
        if path.is_dir():
            continue
        # 跳过排除目录中的文件
        rel = path.relative_to(project_root)
        if any(part in excludes for part in rel.parts):
            continue
        total_files_scanned += 1

        try:
            size = path.stat().st_size
        except OSError:
            continue

        category = classify_path(rel, size, max_data_mb)
        if category is None:
            # 大数据文件单独记录
            if rel.suffix.lower() in SUFFIX_RULES and SUFFIX_RULES[rel.suffix.lower()] == "data_files":
                if size > max_data_mb * 1024 * 1024:
                    skipped_too_large.append(str(rel).replace("\\", "/"))
            continue

        project_map[category].append(str(rel).replace("\\", "/"))

    # 排序 + 截断（防止 ProjectMap.json 爆炸）
    truncate_max = config["advanced"].get("list_truncate_max", DEFAULT_LIST_TRUNCATE_MAX)
    truncated: dict[str, int] = {}
    full_summary: dict[str, int] = {}
    for k in project_map:
        project_map[k].sort()
        full_count = len(project_map[k])
        full_summary[k] = full_count
        if full_count > truncate_max:
            truncated[k] = full_count - truncate_max
            project_map[k] = project_map[k][:truncate_max]

    return {
        "project_root": str(project_root.resolve()),
        "total_files_scanned": total_files_scanned,
        "skipped_too_large": skipped_too_large[:50],  # 只保留前 50 个示例
        "skipped_too_large_count": len(skipped_too_large),
        "data_file_max_mb": max_data_mb,
        "list_truncate_max": truncate_max,
        "truncated_categories": truncated,        # 哪些类被截断了多少
        "project_map": project_map,
        "summary_full": full_summary,             # 完整计数（包括截断前）
        "summary": {k: len(v) for k, v in project_map.items()},  # 实际列表长度
    }


def write_output(result: dict[str, Any], project_root: Path, output_dir: Path | None = None) -> Path:
    """
    写入 project_map.json。

    output_dir 优先级：
      1. 显式 --output-dir 参数（用于沙箱场景：testskill/.thesis-helper/）
      2. 默认 <project_root>/.thesis-helper/
    """
    if output_dir is None:
        out_dir = project_root / ".thesis-helper"
    else:
        out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "project_map.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="thesis-helper project asset scanner")
    parser.add_argument("project_root", help="Path to the thesis project root directory")
    parser.add_argument("--config", default=None, help="Path to thesis.config.yml (auto-detect in root if omitted)")
    parser.add_argument("--output-dir", default=None,
                        help="Output directory for project_map.json (default: <project_root>/.thesis-helper/). "
                             "Use this for sandbox scenarios where you don't want to write to the scanned project.")
    parser.add_argument("--stdout-json", action="store_true", help="Print full result as JSON to stdout")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.exists() or not project_root.is_dir():
        print(f"Error: project_root does not exist or is not a directory: {project_root}", file=sys.stderr)
        return 1

    # 自动检测 config
    config_path: Path | None = None
    if args.config:
        config_path = Path(args.config)
    else:
        for candidate in ["thesis.config.yml", "thesis.config.yaml", ".thesis-helper/config.yml"]:
            p = project_root / candidate
            if p.exists():
                config_path = p
                break

    config = load_config(config_path)
    result = scan_project(project_root, config)
    output_dir = Path(args.output_dir) if args.output_dir else None
    out_path = write_output(result, project_root, output_dir)

    # 简短报告
    s = result["summary_full"]
    print(f"[scanner] Scanned {result['total_files_scanned']} files in {project_root}")
    print(f"[scanner] code={s['code_files']} data={s['data_files']} figs={s['figure_sources']} "
          f"logs={s['result_logs']} writing={s['existing_writing']} "
          f"format={s['format_rules']} refs={s['references']}")
    if result["truncated_categories"]:
        truncated_summary = ", ".join(f"{k}+{v}" for k, v in result["truncated_categories"].items())
        print(f"[scanner] Truncated lists (kept first {result['list_truncate_max']}): {truncated_summary}")
    if result["skipped_too_large_count"]:
        print(f"[scanner] Skipped {result['skipped_too_large_count']} oversized data files (>{config['advanced']['data_file_max_mb']}MB)")
    print(f"[scanner] Output: {out_path}")

    if args.stdout_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
