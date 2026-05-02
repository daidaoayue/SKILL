#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
orchestrator.py — thesis-helper 端到端真编排器

不再只靠 SKILL.md 文档"指导 Claude 怎么做"——这个脚本真把
scanner + 5 个 extensions + cnki adapter 串起来，一键真跑。

用法：
    python orchestrator.py <project_dir> [--config thesis.config.yml]
                                          [--phase all|scan|format|abstract|word|defense|blind]
                                          [--output report_dir]

例子：
    python orchestrator.py D:/code/radar_target_recognition --phase all
    python orchestrator.py . --phase format
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

THIS_DIR = Path(__file__).resolve().parent
SCANNER = THIS_DIR / "scanners" / "project-scanner.py"
EXT = THIS_DIR / "extensions"

# 5 个 extension 的 entry point
EXTENSIONS = {
    "format": EXT / "format-compliance-checker" / "scripts" / "check.py",
    "abstract": EXT / "bilingual-abstract" / "scripts" / "check.py",
    "word": EXT / "latex-to-word" / "scripts" / "convert.py",
    "defense": EXT / "thesis-defense-prep" / "scripts" / "extract_qa.py",
    "blind": EXT / "thesis-blind-review" / "scripts" / "anonymize.py",
}


def load_config(config_path: Path) -> dict:
    """读 thesis.config.yml（用 PyYAML 或简易解析）。"""
    if not config_path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except ImportError:
        return {}


def find_paper_root(project_dir: Path, config: dict) -> Path | None:
    """根据 config.paths.paper_root 找论文实际目录。"""
    if config.get("paths", {}).get("paper_root"):
        rel = config["paths"]["paper_root"]
        candidate = (project_dir / rel).resolve()
        if candidate.exists():
            return candidate
    # 兜底：搜 main.tex
    for p in project_dir.rglob("main.tex"):
        if "paper_writing" in str(p) or "thesis" in str(p).lower():
            return p.parent
    return None


def find_main_tex(paper_root: Path, config: dict) -> Path | None:
    """根据 config.paths.main_tex 找主文件。"""
    if config.get("paths", {}).get("main_tex"):
        candidate = paper_root / config["paths"]["main_tex"]
        if candidate.exists():
            return candidate
    # 默认 main.tex
    candidate = paper_root / "main.tex"
    return candidate if candidate.exists() else None


def find_abstract_tex(paper_root: Path) -> Path | None:
    """找 abstract.tex（typical: data/abstract.tex 或 sections/abstract.tex）。"""
    for sub in ["data/abstract.tex", "sections/abstract.tex", "abstract.tex"]:
        candidate = paper_root / sub
        if candidate.exists():
            return candidate
    return None


def run_subprocess(cmd: list, label: str, timeout: int = 300) -> dict:
    """跑子进程，返回结构化结果。"""
    print(f"\n{'─' * 70}")
    print(f"▶ {label}")
    print(f"  命令: {' '.join(str(c) for c in cmd)}")
    print(f"{'─' * 70}")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace",
        )
        # 实时打印 stdout
        if result.stdout:
            for line in result.stdout.split("\n"):
                if line.strip():
                    print(f"  {line}")
        if result.stderr and result.returncode != 0:
            print(f"  ⚠️ stderr: {result.stderr[:300]}")
        return {
            "label": label,
            "cmd": [str(c) for c in cmd],
            "returncode": result.returncode,
            "success": result.returncode == 0,
            "stdout_lines": result.stdout.count("\n") if result.stdout else 0,
        }
    except subprocess.TimeoutExpired:
        print(f"  ❌ 超时 (>{timeout}s)")
        return {"label": label, "success": False, "error": "timeout"}
    except Exception as e:
        print(f"  ❌ 异常: {e}")
        return {"label": label, "success": False, "error": str(e)}


def phase_0_scan(project_dir: Path, config_path: Path | None, output_dir: Path) -> dict:
    """Phase 0: 项目扫描。"""
    cmd = ["python", str(SCANNER), str(project_dir),
           "--output-dir", str(output_dir)]
    if config_path and config_path.exists():
        cmd += ["--config", str(config_path)]
    return run_subprocess(cmd, "Phase 0 · project-scanner", timeout=120)


def phase_format(main_tex: Path, school: str, output_dir: Path) -> dict:
    """Phase: 格式合规检查。"""
    cmd = ["python", str(EXTENSIONS["format"]), str(main_tex),
           "--school", school,
           "--report", str(output_dir / "format_check.md"),
           "--json", str(output_dir / "format_check.json")]
    return run_subprocess(cmd, "Phase · format-compliance-checker", timeout=60)


def phase_abstract(abstract_tex: Path, thesis_type: str, output_dir: Path) -> dict:
    """Phase: 中英摘要检查。"""
    cmd = ["python", str(EXTENSIONS["abstract"]), str(abstract_tex),
           "--thesis-type", thesis_type,
           "--report", str(output_dir / "abstract_check.md"),
           "--json", str(output_dir / "abstract_check.json")]
    return run_subprocess(cmd, "Phase · bilingual-abstract", timeout=60)


def phase_word(main_tex: Path, output_dir: Path) -> dict:
    """Phase: LaTeX 转 Word。"""
    cmd = ["python", str(EXTENSIONS["word"]), str(main_tex),
           "-o", str(output_dir / "thesis.docx"),
           "--report", str(output_dir / "convert_report.json")]
    return run_subprocess(cmd, "Phase · latex-to-word", timeout=600)


def phase_defense(paper_root: Path, duration: int, output_dir: Path) -> dict:
    """Phase: 答辩素材生成。"""
    cmd = ["python", str(EXTENSIONS["defense"]), str(paper_root),
           "--duration", str(duration),
           "--output", str(output_dir / "defense")]
    return run_subprocess(cmd, "Phase · thesis-defense-prep", timeout=120)


def phase_blind(paper_root: Path, identity_path: Path | None, output_dir: Path) -> dict:
    """Phase: 盲审版生成。"""
    cmd = ["python", str(EXTENSIONS["blind"]), str(paper_root),
           "--output", str(output_dir / "thesis_blind"),
           "--report", str(output_dir / "blind_review_report.md")]
    if identity_path and identity_path.exists():
        cmd += ["--identity", str(identity_path)]
    return run_subprocess(cmd, "Phase · thesis-blind-review", timeout=120)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="thesis-helper 端到端真编排器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_dir", type=Path, help="工程项目根目录")
    parser.add_argument("--config", type=Path, default=None,
                        help="thesis.config.yml 路径（默认在项目根找）")
    parser.add_argument("--phase",
                        choices=["all", "scan", "format", "abstract", "word", "defense", "blind"],
                        default="all", help="只跑某个阶段")
    parser.add_argument("--output", type=Path, default=None,
                        help="输出目录（默认 testskill/orchestrator_run）")
    parser.add_argument("--identity", type=Path, default=None,
                        help="thesis-blind-review 用的 identity.json")
    parser.add_argument("--duration", type=int, default=15,
                        help="thesis-defense-prep 答辩时长")
    args = parser.parse_args()

    if not args.project_dir.exists():
        print(f"❌ 项目目录不存在: {args.project_dir}")
        return 1

    # 找 config
    config_path = args.config
    if config_path is None:
        for c in [args.project_dir / "thesis.config.yml",
                  args.project_dir / "testskill" / "thesis.config.yml"]:
            if c.exists():
                config_path = c
                break
    config = load_config(config_path) if config_path else {}

    # 找 paper_root + main.tex
    paper_root = find_paper_root(args.project_dir, config)
    main_tex = find_main_tex(paper_root, config) if paper_root else None
    abstract_tex = find_abstract_tex(paper_root) if paper_root else None

    # 输出目录
    output_dir = args.output or (args.project_dir / "testskill" / "orchestrator_run")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 头部信息
    print("=" * 70)
    print("thesis-helper Orchestrator · 端到端真编排")
    print("=" * 70)
    print(f"项目目录    : {args.project_dir}")
    print(f"config 路径 : {config_path or '未找到（用默认）'}")
    print(f"paper_root  : {paper_root or '未找到'}")
    print(f"main.tex    : {main_tex or '未找到'}")
    print(f"abstract.tex: {abstract_tex or '未找到'}")
    print(f"输出目录    : {output_dir}")
    print(f"运行阶段    : {args.phase}")
    print(f"开始时间    : {datetime.now().isoformat()}")
    print()

    # 路由参数
    school = config.get("school_rules", {}).get("buaa_undergrad", {}).get("name") or "buaa_undergrad"
    if "school" in school:
        school = school
    else:
        school = "buaa_undergrad"
    thesis_type = config.get("thesis_type", "undergrad-thesis")

    results = []

    # Phase 0 · scan
    if args.phase in ("all", "scan"):
        results.append(phase_0_scan(args.project_dir, config_path, output_dir / ".thesis-helper"))

    # Phase format
    if args.phase in ("all", "format") and main_tex:
        results.append(phase_format(main_tex, school, output_dir))

    # Phase abstract
    if args.phase in ("all", "abstract") and abstract_tex:
        results.append(phase_abstract(abstract_tex, thesis_type, output_dir))

    # Phase word（latex-to-word）
    if args.phase in ("all", "word") and main_tex:
        results.append(phase_word(main_tex, output_dir))

    # Phase defense
    if args.phase in ("all", "defense") and paper_root:
        results.append(phase_defense(paper_root, args.duration, output_dir))

    # Phase blind
    if args.phase in ("all", "blind") and paper_root:
        results.append(phase_blind(paper_root, args.identity, output_dir))

    # 汇总报告
    print()
    print("=" * 70)
    print("📊 端到端汇总")
    print("=" * 70)
    pass_count = sum(1 for r in results if r.get("success"))
    total = len(results)
    print(f"成功阶段: {pass_count}/{total}")
    print()
    for r in results:
        status = "✅" if r.get("success") else "❌"
        print(f"  {status} {r['label']}")
        if not r.get("success"):
            print(f"      原因: {r.get('error', 'returncode != 0')}")

    # 写汇总 JSON
    summary_path = output_dir / "orchestrator_summary.json"
    summary = {
        "timestamp": datetime.now().isoformat(),
        "project_dir": str(args.project_dir),
        "config_path": str(config_path) if config_path else None,
        "paper_root": str(paper_root) if paper_root else None,
        "main_tex": str(main_tex) if main_tex else None,
        "phase": args.phase,
        "results": results,
        "pass_count": pass_count,
        "total": total,
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n📋 汇总报告: {summary_path}")
    print(f"📂 全部产物: {output_dir}")

    return 0 if pass_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
