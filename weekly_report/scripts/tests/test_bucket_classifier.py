"""Tests for bucket_classifier path → bucket mapping."""
import pytest
from scripts.bucket_classifier import BucketClassifier, BUCKETS

CONFIG = {
    "code":            {"roots": ["Forecasting", "hardware"], "exts": [".py"]},
    "experiment_data": {"roots": ["Forecasting/output"],      "exts": [".json"]},
    "paper":           {"roots": ["paper_writing"],            "exts": [".tex", ".md"]},
    "reading":         {"roots": ["research-wiki"],            "exts": [".md", ".pdf"]},
    "theory":          {"roots": ["theory"],                   "exts": [".md", ".tex"]},
    "figures":         {"roots": ["**/ppt_figures"],           "exts": [".png", ".svg"]},
    "checkpoint_signal":{"roots": ["**/checkpoint"],           "exts": [".pt", ".pth", ".ckpt"]},
}


@pytest.mark.parametrize("rel,bucket", [
    ("Forecasting/train.py",                       "code"),
    ("Forecasting/output/inference.json",          "experiment_data"),
    ("paper_writing/chapter3.tex",                 "paper"),
    ("research-wiki/notes.md",                     "reading"),
    ("theory/derivation.md",                       "theory"),
    ("Forecasting/ppt_figures/fig1.png",           "figures"),
    ("Forecasting/checkpoint/best_acc_0.94.pt",    "checkpoint_signal"),
    ("misc/random.txt",                            "uncategorized"),
])
def test_classify(rel, bucket):
    c = BucketClassifier(CONFIG)
    assert c.classify(rel) == bucket


def test_buckets_constant_matches_config():
    expected = {"code","experiment_data","paper","reading","theory","figures","checkpoint_signal","uncategorized"}
    assert set(BUCKETS) == expected


def test_extension_filter_blocks_wrong_ext():
    c = BucketClassifier(CONFIG)
    # .py file under research-wiki — wiki only allows .md/.pdf
    assert c.classify("research-wiki/script.py") == "uncategorized"
