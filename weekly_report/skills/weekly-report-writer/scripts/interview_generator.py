"""Generate interview.md from manifest + diff data.

Output is a markdown questionnaire with H1 anchors (## ① ... ## ⑨) that the
H1-strict / H2-loose parser in parse_interview.py expects.
"""
from __future__ import annotations
import datetime as _dt
import hashlib
import json


def _diff_signature(diff: dict) -> str:
    return hashlib.sha1(json.dumps(diff, sort_keys=True, default=str).encode()).hexdigest()[:12]


def _section_chain_advanced(diff: dict) -> str:
    advanced = diff.get("code", {}).get("version_chains_advanced", [])
    if not advanced:
        return "（本周无版本链推进。如有遗漏请人工补充。）"
    out = []
    for c in advanced:
        out.append(
            f"### {c['family']} 链：{c.get('from')} → {c.get('to')}\n"
            f"**自动 diff 摘要**：{c.get('diff_summary') or '（待填，由 LLM/手动补）'}\n\n"
            f"**请填**：\n"
            f"- {c.get('to')} 相对 {c.get('from')} 的核心改动：______\n"
            f"- 改动动机 / 解决的问题：______\n"
            f"- 是否达到预期：______\n"
        )
    return "\n".join(out)


def _section_paper(diff: dict) -> str:
    paper_d = diff.get("paper", {})
    mods = list(paper_d.get("modified", [])) + list(paper_d.get("added", []))
    if not mods:
        return "（本周论文文件无变化。）"
    body = []
    for f in mods:
        body.append(
            f"### {f}\n"
            f"**章节变动**：（章节级 diff 暂留待 LLM 阶段补全）\n\n"
            f"**请填**：\n"
            f"- 推进到：[ ] 初稿完成 [ ] 评审中 [ ] 待确认 [ ] 其他：____\n"
            f"- 预计完成时间：______\n"
        )
    return "\n".join(body)


def _section_unknown_metrics(metrics: list[dict]) -> str:
    if not metrics:
        return "（本周未发现新指标。）"
    out = []
    for m in metrics:
        out.append(
            f"### `{m['key']}`\n"
            f"- 出现位置：{m.get('sample_file','?')}\n"
            f"- 自动猜测：{m.get('auto_guess','metric / 待确认')}\n"
            f"- [ ] 是指标，方向 higher_better\n"
            f"- [ ] 是指标，方向 lower_better\n"
            f"- [ ] 是配置（不参与对比）\n"
            f"- [ ] 忽略\n"
        )
    return "\n".join(out)


def _section_theory(blocks: list[dict]) -> str:
    if not blocks:
        return "（本周无新增公式块。如本周有理论推导，请手动补一段。）"
    out = []
    for b in blocks:
        out.append(
            f"### {b.get('file','?')} 第 {b.get('section','?')} 节\n"
            f"**自动检测的新公式**：\n- `{(b.get('body','') or '')[:100]}`\n\n"
            f"**请填**：\n"
            f"- 物理含义 / 数学动机：______\n"
            f"- 是否计划写进论文，哪一节：______\n"
            f"- 是否需要进一步推导 / 验证：______\n"
        )
    return "\n".join(out)


def _section_figures(cands: list[dict]) -> str:
    if not cands:
        return "（本周无候选配图。）"
    body = ["skill 已根据 mtime + family link 选出候选图，请勾选要嵌入周报的图（标题如有不准请改）：\n"]
    for c in cands:
        body.append(f"- [ ] {c['path']} (caption: {c.get('caption_draft','')})")
    return "\n".join(body)


def generate_interview(
    *,
    week_id: str,
    project_name: str,
    diff: dict,
    new_unknown_metrics: list[dict],
    figure_candidates: list[dict],
    theory_blocks_added: list[dict],
) -> str:
    sig = _diff_signature(diff)
    sections = [
        ("① 实验链进展（必填）",   _section_chain_advanced(diff)),
        ("② 实验指标突变（必填）", "（指标突变检测见 manifest.metric_aggregates，请基于本节自动填表后审一遍）"),
        ("③ 论文推进（必填）",     _section_paper(diff)),
        ("④ 阅读 / 思考类（选填）","（系统不一定能从 mtime 看到，请你简述本周读了什么、有何启发）\n\n**请填**：______"),
        ("⑤ 给老师的 ask（选填）", "**请填**：\n- 需要的实验器材 / 数据：______\n- 需要老师确认的方向：______\n- 需要的计算资源：______"),
        ("⑥ 本周发现新指标（必处理）", _section_unknown_metrics(new_unknown_metrics)),
        ("⑦ 理论 / 公式推导（必填如有变化）", _section_theory(theory_blocks_added)),
        ("⑧ 配图建议（半自动）", _section_figures(figure_candidates)),
        ("⑨ 风险与阻塞（选填）", "**请填**：______"),
    ]
    section_md = "\n\n".join(f"## {h}\n\n{body}" for h, body in sections)
    return (
        f"# 周报质询问卷 · {week_id} · {project_name}\n\n"
        f"## 元数据（自动生成，不要改）\n"
        f"- generated_at: {_dt.datetime.now().isoformat(timespec='seconds')}\n"
        f"- diff_signature: {sig}\n\n"
        f"{section_md}\n\n"
        f"---\n"
        f"*Filled questionnaire is parsed by parse_interview.py.*\n"
        f"*H1 anchors (## ① ② ...) MUST stay; H2 sub-sections may be edited.*\n"
    )
