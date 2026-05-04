"""Tests for metric_vocab_init build + parse round-trip."""
from scripts.metric_vocab_init import build_init_md, parse_filled_md, CHOICE_LINES


def test_build_includes_all_sections():
    md = build_init_md(
        project_name="proj",
        auto_metrics={"track_acc": ["a.json", "b.json"]},
        auto_configs={"seed": ["a.json"]},
        unknowns={"weird_score": ["x.json"], "elapsed_sec": ["y.json"]},
    )
    assert "## 自动识别为指标" in md
    assert "## 自动识别为配置" in md
    assert "## 需要你标注的字段" in md
    assert "`track_acc`" in md
    assert "`weird_score`" in md
    # all 6 choices present per unknown
    assert "higher_better" in md and "lower_better" in md
    assert "是统计聚合" in md and "是配置" in md
    assert "忽略" in md and "不清楚" in md


def test_build_handles_no_unknowns():
    md = build_init_md(
        project_name="p", auto_metrics={"acc": []}, auto_configs={}, unknowns={}
    )
    assert "无 unknown 字段" in md or "（无 unknown 字段" in md


def test_parse_higher_better_metric():
    md = "### `weird_score`\n\n" + CHOICE_LINES["higher_better"].replace("[ ]", "[x]") + "\n"
    v = parse_filled_md(md, project_name="p")
    assert v.metrics["weird_score"]["direction"] == "higher_better"


def test_parse_lower_better_metric():
    md = "### `time_s`\n\n" + CHOICE_LINES["lower_better"].replace("[ ]", "[X]") + "\n"
    v = parse_filled_md(md, project_name="p")
    assert v.metrics["time_s"]["direction"] == "lower_better"


def test_parse_config():
    md = "### `seed`\n\n" + CHOICE_LINES["config"].replace("[ ]", "[x]") + "\n"
    v = parse_filled_md(md, project_name="p")
    assert "seed" in v.config_keys


def test_parse_stat_aggregate_marked_as_metric_with_flag():
    md = "### `seg_mean`\n\n" + CHOICE_LINES["stat_aggregate"].replace("[ ]", "[x]") + "\n"
    v = parse_filled_md(md, project_name="p")
    assert "seg_mean" in v.metrics
    assert v.metrics["seg_mean"].get("is_stat_aggregate") is True


def test_parse_ignored():
    md = "### `_internal`\n\n" + CHOICE_LINES["ignored"].replace("[ ]", "[x]") + "\n"
    v = parse_filled_md(md, project_name="p")
    assert "_internal" in v.ignored_keys


def test_parse_unknown_pending_drops_key():
    """`不清楚` keys should NOT land in any category (they re-ask next run)."""
    md = "### `dunno`\n\n" + CHOICE_LINES["unknown_pending"].replace("[ ]", "[x]") + "\n"
    v = parse_filled_md(md, project_name="p")
    assert "dunno" not in v.metrics
    assert "dunno" not in v.config_keys
    assert "dunno" not in v.ignored_keys


def test_parse_no_tick_drops_key():
    md = "### `forgot`\n\n" + CHOICE_LINES["higher_better"] + "\n"  # all unchecked
    v = parse_filled_md(md, project_name="p")
    assert "forgot" not in v.metrics


def test_parse_first_ticked_wins():
    """If user ticks more than one, take the first."""
    md = (
        "### `confused`\n\n"
        + CHOICE_LINES["higher_better"].replace("[ ]", "[x]") + "\n"
        + CHOICE_LINES["lower_better"].replace("[ ]", "[x]") + "\n"
    )
    v = parse_filled_md(md, project_name="p")
    assert v.metrics["confused"]["direction"] == "higher_better"


def test_parse_merges_auto_classified():
    md = "### `weird_score`\n\n" + CHOICE_LINES["higher_better"].replace("[ ]", "[x]") + "\n"
    v = parse_filled_md(
        md,
        project_name="p",
        auto_metrics={"track_acc": ["a.json"]},
        auto_configs={"seed": ["a.json"]},
    )
    assert "track_acc" in v.metrics
    assert v.metrics["track_acc"]["source"] == "auto_hint"
    assert "seed" in v.config_keys
    assert "weird_score" in v.metrics
    assert v.metrics["weird_score"]["source"] == "user_label"


def test_round_trip_build_then_parse():
    md = build_init_md(
        project_name="p",
        auto_metrics={"track_acc": ["a.json"]},
        auto_configs={"seed": ["a.json"]},
        unknowns={"time_s": ["x.json"], "weird_score": ["y.json"]},
    )
    # Simulate user ticking
    md = md.replace(
        f"`time_s`\n\n- 出现于 **1** 个文件，例：`x.json`\n"
        + CHOICE_LINES["higher_better"] + "\n"
        + CHOICE_LINES["lower_better"],
        f"`time_s`\n\n- 出现于 **1** 个文件，例：`x.json`\n"
        + CHOICE_LINES["higher_better"] + "\n"
        + CHOICE_LINES["lower_better"].replace("[ ]", "[x]"),
        1,
    )
    v = parse_filled_md(md, project_name="p", auto_metrics={"track_acc":["a.json"]},
                        auto_configs={"seed":["a.json"]})
    assert v.metrics["time_s"]["direction"] == "lower_better"
    assert "track_acc" in v.metrics
    assert "seed" in v.config_keys
