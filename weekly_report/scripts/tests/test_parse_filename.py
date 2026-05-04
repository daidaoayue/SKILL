"""Tests for parse_filename heuristic."""
import pytest
from scripts.parse_filename import parse_filename, ParsedName


@pytest.mark.parametrize("stem,family,version,status", [
    ("rcs_stacking_v26",        "rcs_stacking",         "v26", None),
    ("rcs_fusion_v25",          "rcs_fusion",           "v25", None),
    ("train_v17_contrastive",   "train_contrastive",    "v17", None),
    ("train_v17_fixed",         "train",                "v17", "fixed"),
    ("train_v19_mstcn_contrastive", "train_mstcn_contrastive", "v19", None),
    ("adaptive_fusion_v5b",     "adaptive_fusion",      "v5b", None),
    ("data_loader_complex_v2",  "data_loader_complex",  "v2",  None),
    ("data_loader_new",         "data_loader",          None,  "new"),
    ("inference_v20_v2",        "inference",            "v20", None),  # _v2 as semantic
    ("compare_v17_v19",         "compare",              "v17", None),  # comparison script
    ("plain_module",            "plain_module",         None,  None),
])
def test_parse_filename_basic(stem, family, version, status):
    result = parse_filename(stem)
    assert result.family_key == family
    assert result.version == version
    assert result.status == status


def test_parse_filename_double_final_anomaly():
    """Final_inference_final.py → flagged as anomaly."""
    result = parse_filename("Final_inference_final")
    assert result.is_anomaly
    assert "double_status_marker" in result.anomaly_reasons


def test_parse_filename_v20v2_typo():
    """analyze_errors_v20v2 → flagged as suspected typo."""
    result = parse_filename("analyze_errors_v20v2")
    assert result.is_anomaly
    assert "suspected_version_typo" in result.anomaly_reasons


def test_parse_filename_returns_dataclass():
    """Return type must be ParsedName dataclass for downstream use."""
    result = parse_filename("rcs_stacking_v26")
    assert isinstance(result, ParsedName)
    assert hasattr(result, "raw_stem")
    assert result.raw_stem == "rcs_stacking_v26"


def test_uppercase_version_token_recognized():
    """Windows-native filenames may capitalize: `_V17` should match like `_v17`."""
    result = parse_filename("Train_V17_contrastive")
    assert result.version is not None and result.version.lower() == "v17"
    assert result.family_key.lower() == "train_contrastive"


def test_non_anomaly_inputs_have_clean_flag():
    """Lock the contract: regular files must NOT be flagged as anomalies."""
    for stem in ("rcs_stacking_v26", "train", "data_loader_new", "plain_module"):
        assert not parse_filename(stem).is_anomaly
