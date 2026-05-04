"""Tests for parse_interview H1-strict / H2-loose parser."""
from scripts.parse_interview import parse_interview


SAMPLE = """# 周报质询问卷 · 2026-W18 · radar

## 元数据
- generated_at: 2026-05-04T10:00
- diff_signature: deadbeef

## ① 实验链进展（必填）
### rcs_stacking 链：v25 → v26
**请填**：
- v26 相对 v25 的核心改动：换了 stacking 头从 LR 改 GBM
- 改动动机：解决 v25 的 underfit
- 是否达到预期：是

## ② 实验指标突变（必填）
（无）

## ⑥ 本周发现新指标
### `weird_score`
- [x] 是指标，方向 higher_better
- [ ] 是配置
"""


def test_parse_collects_sections():
    out = parse_interview(SAMPLE)
    assert "①" in out["sections"]
    assert out["sections"]["①"] is not None
    assert "v25" in out["sections"]["①"]["raw"]
    assert out["meta"]["diff_signature"] == "deadbeef"


def test_parse_extracts_fill_in_text_blocks():
    out = parse_interview(SAMPLE)
    text = out["sections"]["①"]["fill_in"]
    assert "stacking 头" in text
    assert "underfit" in text


def test_parse_extracts_checkboxes():
    out = parse_interview(SAMPLE)
    boxes = out["sections"]["⑥"]["checkboxes"]
    matched = [(b["text"], b["checked"]) for b in boxes]
    assert ("是指标，方向 higher_better", True) in matched
    assert ("是配置", False) in matched


def test_missing_section_does_not_crash():
    md = "# 标题\n\n## ① 实验链\n（空）\n"
    out = parse_interview(md)
    assert out["sections"]["①"] is not None
    # other sections absent
    for k in "②③④⑤⑥⑦⑧⑨":
        assert out["sections"][k] is None


def test_parse_chinese_colon_in_fillin():
    """Some users may type 全角 colon ：instead of half-width :"""
    md = "## ① 实验链\n**请填**：本周做了 X\n"
    out = parse_interview(md)
    assert "本周做了 X" in out["sections"]["①"]["fill_in"]
