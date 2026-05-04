"""Tests for extract_metrics heuristic + multi-seed aggregator."""
import pytest
from scripts.extract_metrics import (
    classify_key, extract_metrics_from_json, aggregate_by_seed,
    HINT_TOKENS_DEFAULT, CONFIG_HINT_DEFAULT, STAT_SUFFIX,
)


@pytest.mark.parametrize("k,expected", [
    ("track_acc",        "metric"),
    ("seg_acc",          "metric"),
    ("val_loss",         "metric"),
    ("f1_score",         "metric"),
    ("seed",             "config"),
    ("backbone",         "config"),
    ("n_train_tracks",   "config"),
    ("n_params",         "config"),
    ("track_acc_mean",   "metric"),
    ("track_acc_std",    "metric"),
    ("nonsense_xyz",     "unknown"),
])
def test_classify_key_default_vocab(k, expected):
    cat = classify_key(k, hint_tokens=HINT_TOKENS_DEFAULT,
                       config_hints=CONFIG_HINT_DEFAULT,
                       stat_suffixes=STAT_SUFFIX,
                       known_metrics=set(), known_configs=set(),
                       ignored=set())
    assert cat == expected


def test_classify_known_overrides_hint():
    cat = classify_key("nonsense_xyz",
                       hint_tokens=HINT_TOKENS_DEFAULT,
                       config_hints=CONFIG_HINT_DEFAULT,
                       stat_suffixes=STAT_SUFFIX,
                       known_metrics={"nonsense_xyz"},
                       known_configs=set(),
                       ignored=set())
    assert cat == "metric"


def test_classify_ignored_wins():
    cat = classify_key("track_acc",
                       hint_tokens=HINT_TOKENS_DEFAULT,
                       config_hints=CONFIG_HINT_DEFAULT,
                       stat_suffixes=STAT_SUFFIX,
                       known_metrics=set(), known_configs=set(),
                       ignored={"track_acc"})
    assert cat == "ignored"


def test_extract_from_json_dict():
    obj = {"track_acc": 0.94, "seed": 42, "backbone": "resnet34",
           "n_seeds": 8, "loss": 0.21, "label": "rcs"}
    out = extract_metrics_from_json(obj,
                                    known_metrics=set(),
                                    known_configs=set(),
                                    ignored=set())
    assert out["metrics"] == {"track_acc": 0.94, "loss": 0.21}
    assert "seed" in out["config"] and out["config"]["seed"] == 42
    assert "backbone" in out["config"]
    assert out["unknown_numeric"] == {}
    assert "label" not in out["metrics"] and "label" not in out["config"]


def test_extract_unknown_numeric_bucket():
    obj = {"weird_score_z": 0.5, "track_acc": 0.9}
    out = extract_metrics_from_json(obj,
                                    known_metrics=set(),
                                    known_configs=set(),
                                    ignored=set())
    # weird_score_z contains `score` → it's actually classified as metric, not unknown.
    # So replace with a name that has no hint.
    obj2 = {"qwertyz": 0.5, "track_acc": 0.9}
    out2 = extract_metrics_from_json(obj2,
                                     known_metrics=set(),
                                     known_configs=set(),
                                     ignored=set())
    assert out2["unknown_numeric"] == {"qwertyz": 0.5}
    assert out2["metrics"] == {"track_acc": 0.9}


def test_aggregate_by_seed_mean_std():
    runs = [
        {"track_acc": 0.92, "seed": 1},
        {"track_acc": 0.93, "seed": 2},
        {"track_acc": 0.95, "seed": 3},
    ]
    agg = aggregate_by_seed(runs, metric_keys=["track_acc"])
    assert pytest.approx(agg["track_acc"]["mean"], abs=1e-6) == (0.92+0.93+0.95)/3
    assert agg["track_acc"]["n_seeds"] == 3
    assert agg["track_acc"]["std"] > 0
    assert agg["track_acc"]["min"] == 0.92
    assert agg["track_acc"]["max"] == 0.95


def test_aggregate_single_seed_has_zero_std():
    runs = [{"track_acc": 0.94}]
    agg = aggregate_by_seed(runs, metric_keys=["track_acc"])
    assert agg["track_acc"]["n_seeds"] == 1
    assert agg["track_acc"]["std"] == 0.0
