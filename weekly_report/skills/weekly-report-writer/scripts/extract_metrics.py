"""Heuristic JSON metric/config classifier + multi-seed aggregator.

Categories: metric / config / unknown / ignored.
Layered: hint tokens → known sets (from metric_vocab) → unknown bucket.
"""
from __future__ import annotations
import statistics
from typing import Iterable, Mapping

HINT_TOKENS_DEFAULT = (
    "acc", "accuracy", "loss", "f1", "auc", "error", "err",
    "iou", "map", "recall", "precision",
    "mae", "rmse", "psnr", "ssim",
    "bleu", "rouge", "perplexity", "rate", "score",
)
CONFIG_HINT_DEFAULT = (
    "seed", "backbone", "lr", "epoch", "batch", "ratio", "pretrain",
    "n_params", "mode", "n_train", "n_val", "n_test", "rcs_mode",
)
STAT_SUFFIX = ("_mean", "_std", "_ci", "_ci_95", "_min", "_max", "_median")


def _strip_stat_suffix(k: str, suffixes: Iterable[str]) -> str:
    lk = k.lower()
    for s in suffixes:
        if lk.endswith(s):
            return k[: -len(s)]
    return k


def classify_key(
    key: str,
    *,
    hint_tokens: Iterable[str],
    config_hints: Iterable[str],
    stat_suffixes: Iterable[str],
    known_metrics: set[str],
    known_configs: set[str],
    ignored: set[str],
) -> str:
    """Return one of: 'metric' / 'config' / 'unknown' / 'ignored'.

    Resolution order:
      1. ignored set (explicit user override)
      2. known_metrics (from metric_vocab)
      3. known_configs (from metric_vocab)
      4. config hint tokens (must come BEFORE metric hints, e.g. `n_test_tracks`
         contains `acc`-substring trap-free but `n_train_tracks` could trip;
         specifically `n_params` would otherwise match `param` partial)
      5. metric hint tokens (after stripping stat suffix)
      6. unknown
    """
    if key in ignored:
        return "ignored"
    if key in known_metrics:
        return "metric"
    if key in known_configs:
        return "config"
    lk = key.lower()
    for c in config_hints:
        if c in lk:
            return "config"
    base = _strip_stat_suffix(key, stat_suffixes).lower()
    for h in hint_tokens:
        if h in base:
            return "metric"
    return "unknown"


def extract_metrics_from_json(
    obj: Mapping,
    *,
    known_metrics: set[str],
    known_configs: set[str],
    ignored: set[str],
    hint_tokens: Iterable[str] = HINT_TOKENS_DEFAULT,
    config_hints: Iterable[str] = CONFIG_HINT_DEFAULT,
    stat_suffixes: Iterable[str] = STAT_SUFFIX,
) -> dict[str, dict]:
    """Classify the top-level keys of a JSON-like object.

    Returns {"metrics": {k: float}, "config": {k: any}, "unknown_numeric": {k: float}}.
    Non-numeric metric candidates are dropped. Non-config strings are dropped.
    """
    metrics: dict[str, float] = {}
    config: dict[str, object] = {}
    unknown_numeric: dict[str, float] = {}

    for k, v in obj.items():
        cat = classify_key(
            k,
            hint_tokens=hint_tokens, config_hints=config_hints,
            stat_suffixes=stat_suffixes,
            known_metrics=known_metrics, known_configs=known_configs,
            ignored=ignored,
        )
        if cat == "metric" and isinstance(v, (int, float)) and not isinstance(v, bool):
            metrics[k] = float(v)
        elif cat == "config":
            config[k] = v
        elif cat == "unknown" and isinstance(v, (int, float)) and not isinstance(v, bool):
            unknown_numeric[k] = float(v)
    return {"metrics": metrics, "config": config, "unknown_numeric": unknown_numeric}


def aggregate_by_seed(runs: list[dict], metric_keys: list[str]) -> dict[str, dict]:
    """Aggregate metrics across seeds. Each run dict must contain the metric keys."""
    out: dict[str, dict] = {}
    for mk in metric_keys:
        values = [float(r[mk]) for r in runs if mk in r]
        if not values:
            continue
        mean = statistics.fmean(values)
        std = statistics.pstdev(values) if len(values) > 1 else 0.0
        out[mk] = {
            "mean": mean,
            "std": std,
            "n_seeds": len(values),
            "min": min(values),
            "max": max(values),
        }
    return out
