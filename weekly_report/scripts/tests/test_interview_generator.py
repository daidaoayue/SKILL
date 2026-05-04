"""Tests for interview_generator."""
from scripts.interview_generator import generate_interview


def _empty_diff():
    return {
        "code": {"version_chains_advanced": [], "non_versioned_modified": [],
                 "added_loose_files": [], "deleted_files": []},
        "experiment_data": {"added": [], "modified": [], "deleted": []},
        "paper":           {"added": [], "modified": [], "deleted": []},
        "reading":         {"added": [], "modified": [], "deleted": []},
        "theory":          {"added": [], "modified": [], "deleted": []},
        "figures":         {"added": [], "modified": [], "deleted": []},
        "checkpoint_signal":{"added": [], "modified": [], "deleted": []},
    }


def test_generate_with_chain_advanced():
    diff = _empty_diff()
    diff["code"]["version_chains_advanced"] = [
        {"family":"rcs_stacking","from":"v25","to":"v26","diff_summary":""}
    ]
    diff["paper"]["modified"] = ["paper_writing/ch3.md"]
    md = generate_interview(
        week_id="2026-W18",
        project_name="radar",
        diff=diff,
        new_unknown_metrics=[],
        figure_candidates=[],
        theory_blocks_added=[],
    )
    assert "## ① 实验链进展" in md
    assert "rcs_stacking" in md
    assert "v25" in md and "v26" in md
    assert "## ③ 论文推进" in md
    assert "ch3.md" in md


def test_generate_with_new_unknown_metrics():
    md = generate_interview(
        week_id="W18", project_name="p", diff=_empty_diff(),
        new_unknown_metrics=[{"key":"weird_score","sample_file":"r.json"}],
        figure_candidates=[], theory_blocks_added=[],
    )
    assert "## ⑥ 本周发现新指标" in md
    assert "weird_score" in md
    assert "[ ] 是指标，方向 higher_better" in md


def test_generate_with_theory_blocks():
    md = generate_interview(
        week_id="W18", project_name="p", diff=_empty_diff(),
        new_unknown_metrics=[], figure_candidates=[],
        theory_blocks_added=[
            {"file":"theory/d.md","section":"2.1","body":r"|mean(exp(j\phi))|"}
        ],
    )
    assert "## ⑦ 理论 / 公式推导" in md
    assert "2.1" in md or "2.1 节" in md


def test_generate_with_figure_candidates():
    md = generate_interview(
        week_id="W18", project_name="p", diff=_empty_diff(),
        new_unknown_metrics=[], theory_blocks_added=[],
        figure_candidates=[
            {"path":"f/mc.png","caption_draft":"蒙特卡洛鲁棒性"}
        ],
    )
    assert "## ⑧ 配图建议" in md
    assert "f/mc.png" in md
    assert "蒙特卡洛鲁棒性" in md


def test_generate_all_sections_present_when_empty():
    md = generate_interview(
        week_id="W18", project_name="p", diff=_empty_diff(),
        new_unknown_metrics=[], figure_candidates=[], theory_blocks_added=[],
    )
    for anchor in ("## ①", "## ②", "## ③", "## ④", "## ⑤",
                   "## ⑥", "## ⑦", "## ⑧", "## ⑨"):
        assert anchor in md, f"missing anchor: {anchor}"
    assert "diff_signature:" in md
