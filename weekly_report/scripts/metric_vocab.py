"""Read/write per-project metric_vocab.json (incremental learning)."""
from __future__ import annotations
import datetime as _dt
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class MetricVocab:
    project_name: str
    metrics: dict[str, dict] = field(default_factory=dict)
    config_keys: dict[str, dict] = field(default_factory=dict)
    ignored_keys: set[str] = field(default_factory=set)
    last_updated: Optional[str] = None


def load_metric_vocab(path: Path, *, project_name: str) -> MetricVocab:
    if not path.exists():
        return MetricVocab(project_name=project_name)
    obj = json.loads(path.read_text(encoding="utf-8"))
    return MetricVocab(
        project_name=obj.get("project_name", project_name),
        metrics=obj.get("metrics", {}),
        config_keys=obj.get("config_keys", {}),
        ignored_keys=set(obj.get("ignored_keys", [])),
        last_updated=obj.get("last_updated"),
    )


def save_metric_vocab(path: Path, vocab: MetricVocab) -> None:
    obj = {
        "schema_version": "1.0",
        "project_name": vocab.project_name,
        "last_updated": _dt.date.today().isoformat(),
        "metrics": vocab.metrics,
        "config_keys": vocab.config_keys,
        "stat_aggregates": ["_mean","_std","_ci","_ci_95","_min","_max","_median"],
        "ignored_keys": sorted(vocab.ignored_keys),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
