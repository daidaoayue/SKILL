#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_skills.py — 真审查 thesis-helper 工作流接入的所有 skill 是否真接通

不嘴炮——对每个 skill 真去文件系统检查：
  - 有 SKILL.md？
  - 有可执行 .py？
  - python 真能 --help？
  - subprocess 真能跑？
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

THIS_DIR = Path(__file__).resolve().parent
SKILL_BASE = THIS_DIR.parent

# ============================================================================
# 审查清单：thesis-helper 应该接通的所有 skill
# ============================================================================
SKILLS_TO_AUDIT = [
    # === thesis-helper 自己的核心工具（应全部真可执行）===
    {"id": "scanner", "name": "project-scanner",
     "py_path": THIS_DIR / "scanners" / "project-scanner.py",
     "category": "thesis-helper-core", "must_executable": True},
    {"id": "build", "name": "compilers/build",
     "py_path": THIS_DIR / "compilers" / "build.py",
     "category": "thesis-helper-core", "must_executable": True},
    {"id": "orchestrator", "name": "orchestrator",
     "py_path": THIS_DIR / "orchestrator.py",
     "category": "thesis-helper-core", "must_executable": True},

    # === thesis-helper 5 个 extensions（应全部真可执行）===
    {"id": "ext-latex2word", "name": "latex-to-word",
     "py_path": THIS_DIR / "extensions" / "latex-to-word" / "scripts" / "convert.py",
     "skill_md": THIS_DIR / "extensions" / "latex-to-word" / "SKILL.md",
     "category": "extension", "must_executable": True},
    {"id": "ext-format", "name": "format-compliance-checker",
     "py_path": THIS_DIR / "extensions" / "format-compliance-checker" / "scripts" / "check.py",
     "skill_md": THIS_DIR / "extensions" / "format-compliance-checker" / "SKILL.md",
     "category": "extension", "must_executable": True},
    {"id": "ext-bilingual", "name": "bilingual-abstract",
     "py_path": THIS_DIR / "extensions" / "bilingual-abstract" / "scripts" / "check.py",
     "skill_md": THIS_DIR / "extensions" / "bilingual-abstract" / "SKILL.md",
     "category": "extension", "must_executable": True},
    {"id": "ext-blind", "name": "thesis-blind-review",
     "py_path": THIS_DIR / "extensions" / "thesis-blind-review" / "scripts" / "anonymize.py",
     "skill_md": THIS_DIR / "extensions" / "thesis-blind-review" / "SKILL.md",
     "category": "extension", "must_executable": True},
    {"id": "ext-defense", "name": "thesis-defense-prep",
     "py_path": THIS_DIR / "extensions" / "thesis-defense-prep" / "scripts" / "extract_qa.py",
     "skill_md": THIS_DIR / "extensions" / "thesis-defense-prep" / "SKILL.md",
     "category": "extension", "must_executable": True},

    # === aigc-reduce skill（用户上游真生产 skill）===
    {"id": "aigc-detect", "name": "aigc-reduce/detect_aigc",
     "py_path": SKILL_BASE / "aigc-reduce-skills" / "detect_aigc" / "detect_aigc.py",
     "category": "aigc-reduce-upstream", "must_executable": True,
     "note": "需要 torch 环境（drsn_env）"},
    {"id": "aigc-reducer", "name": "aigc-reduce 7-stage reducer",
     "py_path": SKILL_BASE / "aigc-reduce-skills" / "aigc_reducer.py",
     "category": "aigc-reduce-upstream", "must_executable": True},

    # === 21 个 integrations wrapper（只有 .md 文档，需要 LLM 真执行）===
    *[
        {"id": f"wrap-{name}", "name": f"integrations/{name}",
         "wrapper_md": THIS_DIR / "integrations" / f"{name}.md",
         "category": "integration-wrapper",
         "must_executable": False,
         "note": "wrapper 是文档，真调用需要 Claude 在对话里按 wrapper.md 执行上游 skill"}
        for name in [
            "arxiv-wrapper", "semantic-scholar-wrapper",
            "research-lit-wrapper", "comm-lit-review-wrapper",
            "claude-paper-study-wrapper", "novelty-check-wrapper",
            "proof-writer-wrapper", "formula-derivation-wrapper",
            "scientific-visualization-wrapper", "matplotlib-tvhahn-wrapper",
            "mermaid-diagram-wrapper", "paper-illustration-wrapper",
            "result-to-claim-wrapper", "ablation-planner-wrapper",
            "rebuttal-wrapper", "paper-reviewer-wrapper",
            "paper-slides-wrapper", "paper-poster-wrapper",
            "docx-wrapper", "pptx-wrapper", "pdf-wrapper",
        ]
    ],

    # === 4 个 detector adapter（只有 .md 文档）===
    *[
        {"id": f"det-{name}", "name": f"detectors/{name}",
         "adapter_md": THIS_DIR / "detectors" / name / "adapter.md",
         "category": "detector",
         "must_executable": False,
         "note": "adapter 是接口文档；CNKI 通过 detect_aigc.py 真接通；其余仅占位"}
        for name in ["cnki", "turnitin", "paperpass", "vipcs"]
    ],
]


def audit_one(skill: dict) -> dict:
    """对一个 skill 真审查。"""
    result = {
        "id": skill["id"], "name": skill["name"],
        "category": skill["category"],
        "must_executable": skill.get("must_executable", False),
        "checks": {},
    }

    # 1. SKILL.md / wrapper.md / adapter.md 存在性
    for key in ["skill_md", "wrapper_md", "adapter_md"]:
        if key in skill:
            p = Path(skill[key])
            result["checks"][key] = {
                "exists": p.exists(),
                "size_bytes": p.stat().st_size if p.exists() else 0,
                "path": str(p),
            }

    # 2. .py 真可执行
    if "py_path" in skill:
        p = Path(skill["py_path"])
        py_check = {"exists": p.exists(),
                    "size_bytes": p.stat().st_size if p.exists() else 0,
                    "path": str(p)}
        if p.exists():
            try:
                r = subprocess.run([sys.executable, str(p), "--help"],
                                   capture_output=True, text=True, timeout=15,
                                   encoding="utf-8", errors="replace")
                py_check["help_works"] = r.returncode == 0
                py_check["help_lines"] = len(r.stdout.split("\n")) if r.stdout else 0
            except Exception as e:
                py_check["help_works"] = False
                py_check["help_error"] = str(e)
        result["checks"]["py"] = py_check

    # 3. 总评
    if skill.get("must_executable"):
        py = result["checks"].get("py", {})
        result["status"] = "✅ 真接通" if py.get("exists") and py.get("help_works") else "❌ 未接通"
    else:
        # wrapper / adapter 只看文件存在
        for k in ["wrapper_md", "adapter_md"]:
            if k in result["checks"]:
                result["status"] = "📝 文档存在(待 Claude 执行)" if result["checks"][k]["exists"] else "❌ 缺失"
                break

    if "note" in skill:
        result["note"] = skill["note"]
    return result


def main() -> int:
    print("=" * 78)
    print("thesis-helper · 全 skill 真接通审查")
    print("=" * 78)
    results = [audit_one(s) for s in SKILLS_TO_AUDIT]

    # 按 category 分组打印
    categories = {}
    for r in results:
        categories.setdefault(r["category"], []).append(r)

    for cat, rs in categories.items():
        print(f"\n━━ {cat} ({len(rs)}) ━━")
        for r in rs:
            print(f"  {r['status']:25s}  {r['name']}")
            if "note" in r:
                print(f"    └─ {r['note']}")

    # 统计
    print("\n" + "=" * 78)
    print("📊 真接通率统计")
    print("=" * 78)
    total = len(results)
    by_status = {}
    for r in results:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    for status, count in sorted(by_status.items()):
        print(f"  {status:25s}  {count}/{total} = {count/total:.0%}")

    must_exec = [r for r in results if r["must_executable"]]
    must_pass = sum(1 for r in must_exec if "真接通" in r["status"])
    print(f"\n  必须可执行的 skill: {must_pass}/{len(must_exec)} 真接通")

    # 写 JSON 详细报告
    out = THIS_DIR / "audit_report.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n📋 详细报告: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
