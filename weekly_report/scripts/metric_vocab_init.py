"""Build / parse `metric_vocab_init.md` for first-run metric labeling.

Workflow:
  1. `build_init_md(...)` writes a markdown questionnaire from harvested keys.
  2. User opens it, ticks ONE checkbox per unknown key.
  3. `parse_filled_md(...)` reads back the ticks and returns a MetricVocab.

Choices supported (one per key):
  - higher_better          → metric with direction higher_better
  - lower_better           → metric with direction lower_better
  - 配置                   → config (not in metric comparison)
  - 统计聚合               → metric, marked is_stat_aggregate (auto-grouped to base metric)
  - 忽略                   → added to ignored_keys
  - 不清楚                 → left out (re-asked on next run)

Spec: §8 Metric 抽取 / 新指标谨慎处理流 / §19 metric_vocab 澄清
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Mapping

from scripts.metric_vocab import MetricVocab

# Choice marker → category. The marker is matched as a substring anywhere
# in the checkbox label, so tweaks to the user-facing wording (parens, examples)
# don't break parsing.
CHOICE_MARKERS: tuple[tuple[str, str], ...] = (
    ("higher_better",   "higher_better"),
    ("lower_better",    "lower_better"),
    ("是统计聚合",       "stat_aggregate"),
    ("是配置",           "config"),
    ("忽略",             "ignored"),
    ("不清楚",           "unknown_pending"),
)

# Standard line variants we emit. Kept here so build + tests share one source.
CHOICE_LINES = {
    "higher_better":    "- [ ] 是指标，方向 higher_better（数值越高越好，如 acc / f1 / iou）",
    "lower_better":     "- [ ] 是指标，方向 lower_better（数值越低越好，如 loss / mae / rmse）",
    "config":           "- [ ] 是配置（不参与指标对比，如 seed / n_samples / batch_size 这种实验设置）",
    "stat_aggregate":   "- [ ] 是统计聚合（`_mean`/`_std`/`_min`/`_max`/`_ci` — 自动归并到对应指标）",
    "ignored":          "- [ ] 忽略（不感兴趣的内部字段）",
    "unknown_pending":  "- [ ] 不清楚（先放着，下次跑 skill 时再问）",
}

H3_RE = re.compile(r"^###\s+`(?P<key>[^`]+)`\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^\s*-\s*\[(?P<m>[ xX])\]\s+(?P<text>.+)$", re.MULTILINE)


def build_init_md(
    *,
    project_name: str,
    auto_metrics: Mapping[str, list[str]],
    auto_configs: Mapping[str, list[str]],
    unknowns: Mapping[str, list[str]],
) -> str:
    """Render the labeling questionnaire as markdown."""
    parts: list[str] = []
    parts.append(f"# Metric Vocab 首次标注 · {project_name}")
    parts.append("")
    parts.append(
        "本文件由 init 自动生成。请为每个未知 key 勾选 **一个** 分类，保存后 skill 会"
        "解析此文件并写入 `metric_vocab.json`。"
    )
    parts.append("")
    parts.append("## 自动识别为指标（无需标注，已视为 metric · higher_better）")
    parts.append("")
    if auto_metrics:
        for k in sorted(auto_metrics, key=lambda x: -len(auto_metrics[x])):
            parts.append(f"- `{k}` (出现于 {len(auto_metrics[k])} 个文件)")
    else:
        parts.append("（无）")
    parts.append("")
    parts.append("## 自动识别为配置（无需标注，已视为 config · 不参与指标对比）")
    parts.append("")
    if auto_configs:
        for k in sorted(auto_configs, key=lambda x: -len(auto_configs[x])):
            parts.append(f"- `{k}` (出现于 {len(auto_configs[k])} 个文件)")
    else:
        parts.append("（无）")
    parts.append("")
    parts.append("---")
    parts.append("")
    parts.append("## 需要你标注的字段")
    parts.append("")

    if not unknowns:
        parts.append("（无 unknown 字段，标注阶段可跳过。）")
    else:
        for k in sorted(unknowns, key=lambda x: -len(unknowns[x])):
            sample = unknowns[k][0] if unknowns[k] else "?"
            n = len(unknowns[k])
            parts.append(f"### `{k}`")
            parts.append("")
            parts.append(f"- 出现于 **{n}** 个文件，例：`{sample}`")
            for choice in (
                "higher_better", "lower_better", "config",
                "stat_aggregate", "ignored", "unknown_pending",
            ):
                parts.append(CHOICE_LINES[choice])
            parts.append("")

    return "\n".join(parts)


def parse_filled_md(
    md: str,
    *,
    project_name: str,
    auto_metrics: Mapping[str, list[str]] | None = None,
    auto_configs: Mapping[str, list[str]] | None = None,
) -> MetricVocab:
    """Parse a filled-in metric_vocab_init.md into a MetricVocab.

    auto_metrics / auto_configs are the heuristic-classified keys the user did
    not touch — they are merged into the returned vocab.
    """
    vocab = MetricVocab(project_name=project_name)

    # Auto pre-classified
    for k in (auto_metrics or {}):
        vocab.metrics[k] = {"category": "metric", "direction": "higher_better",
                             "source": "auto_hint"}
    for k in (auto_configs or {}):
        vocab.config_keys[k] = {"category": "config", "source": "auto_hint"}

    # Walk H3 anchors; for each, pick the FIRST ticked checkbox.
    matches = list(H3_RE.finditer(md))
    for i, m in enumerate(matches):
        key = m.group("key")
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        block = md[start:end]
        chosen: str | None = None
        for cb in CHECKBOX_RE.finditer(block):
            if cb.group("m").strip().lower() != "x":
                continue
            text = cb.group("text")
            for marker, category in CHOICE_MARKERS:
                if marker in text:
                    chosen = category
                    break
            if chosen:
                break

        if chosen == "higher_better":
            vocab.metrics[key] = {"category": "metric", "direction": "higher_better",
                                  "source": "user_label"}
        elif chosen == "lower_better":
            vocab.metrics[key] = {"category": "metric", "direction": "lower_better",
                                  "source": "user_label"}
        elif chosen == "config":
            vocab.config_keys[key] = {"category": "config", "source": "user_label"}
        elif chosen == "stat_aggregate":
            vocab.metrics[key] = {"category": "metric", "is_stat_aggregate": True,
                                  "source": "user_label"}
        elif chosen == "ignored":
            vocab.ignored_keys.add(key)
        elif chosen == "unknown_pending":
            # Leave key out — it will reappear in next run's interview ⑥
            pass
        # No box ticked → also leave out

    return vocab
