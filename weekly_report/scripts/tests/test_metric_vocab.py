"""Tests for metric_vocab IO."""
import json
from pathlib import Path
from scripts.metric_vocab import load_metric_vocab, save_metric_vocab, MetricVocab


def test_load_missing_returns_empty(tmp_path: Path):
    v = load_metric_vocab(tmp_path / "nope.json", project_name="proj")
    assert v.metrics == {}
    assert v.config_keys == {}
    assert v.ignored_keys == set()
    assert v.project_name == "proj"


def test_round_trip(tmp_path: Path):
    v = MetricVocab(project_name="proj",
                    metrics={"track_acc": {"category":"metric","direction":"higher_better"}},
                    config_keys={"seed": {"category":"config"}},
                    ignored_keys={"junk"})
    fp = tmp_path / "vocab.json"
    save_metric_vocab(fp, v)
    loaded = load_metric_vocab(fp, project_name="proj")
    assert loaded.metrics == v.metrics
    assert loaded.config_keys == v.config_keys
    assert loaded.ignored_keys == v.ignored_keys


def test_save_writes_schema_version(tmp_path: Path):
    v = MetricVocab(project_name="p")
    fp = tmp_path / "vocab.json"
    save_metric_vocab(fp, v)
    obj = json.loads(fp.read_text(encoding="utf-8"))
    assert obj["schema_version"] == "1.0"
    assert obj["project_name"] == "p"
    assert obj["stat_aggregates"] == ["_mean","_std","_ci","_ci_95","_min","_max","_median"]


def test_save_creates_parent_dir(tmp_path: Path):
    fp = tmp_path / "nested" / "deep" / "vocab.json"
    save_metric_vocab(fp, MetricVocab(project_name="p"))
    assert fp.exists()
