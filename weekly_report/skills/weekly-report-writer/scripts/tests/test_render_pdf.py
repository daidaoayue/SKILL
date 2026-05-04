"""Tests for render_pdf md→tex→pdf pipeline.

Network-free + tool-aware: when pandoc/xelatex unavailable, the call
returns status='skipped' rather than failing. Tests assert that contract.
"""
import shutil
from pathlib import Path
import pytest
from scripts.render_pdf import render_pdf, md_to_tex_fragment, break_long_paths


HAS_PANDOC = shutil.which("pandoc") is not None
HAS_XELATEX = shutil.which("xelatex") is not None


def _template_path() -> Path:
    return (Path(__file__).resolve().parents[2]
            / "assets" / "baseline-tex-template.tex")


def test_skipped_status_when_tool_missing(tmp_path: Path, monkeypatch):
    """Force pandoc-missing to verify the skip contract."""
    monkeypatch.setattr("scripts.render_pdf._have", lambda cmd: False)
    md = tmp_path / "r.md"
    md.write_text("# Hi\n", encoding="utf-8")
    out = render_pdf(
        md_path=md, template_path=_template_path(),
        project_root=tmp_path,
        out_pdf_dir=tmp_path / ".weekly_report" / "baseline",
        aux_dir=tmp_path / ".weekly_report" / "baseline_tex",
    )
    assert out["status"] == "skipped"
    assert out["pdf_path"] is None
    assert "not in PATH" in out["reason"]


@pytest.mark.skipif(not HAS_PANDOC, reason="pandoc not installed")
def test_pandoc_fragment_basic(tmp_path: Path):
    md = tmp_path / "r.md"
    md.write_text("# 一、标题\n\n这是 **加粗** 文本。\n\n$$x = y$$\n", encoding="utf-8")
    frag = md_to_tex_fragment(md)
    assert "\\section" in frag
    assert "\\textbf{" in frag
    assert "x = y" in frag


def test_template_has_placeholder():
    """Template must contain the substitution marker."""
    text = _template_path().read_text(encoding="utf-8")
    assert "% BODY_PLACEHOLDER" in text


def test_break_long_paths_injects_allowbreak_at_slashes():
    """Path-like \\texttt cells get \\allowbreak after each slash."""
    src = r"\texttt{hardware/radar/train_v5b.py}"
    out = break_long_paths(src)
    assert r"hardware/\allowbreak{}radar/\allowbreak{}train_v5b.py" in out
    assert r"\seqsplit" not in out  # we no longer use seqsplit


def test_break_long_paths_handles_pandoc_escaped_underscores():
    """Pandoc emits \\_ for _; allowbreak after \\_ should be added too."""
    src = r"\texttt{LSS\_database/results/seed\_1.json}"
    out = break_long_paths(src)
    # After both / and \_ we should see \allowbreak
    assert r"\_\allowbreak{}" in out
    assert r"/\allowbreak{}" in out


def test_break_long_paths_leaves_short_identifiers_untouched():
    src = r"value \texttt{seed} and \texttt{n_seeds}"
    out = break_long_paths(src)
    assert r"\texttt{seed}" in out
    # n_seeds: 7 chars, not pathlike, leave alone
    assert r"\texttt{n_seeds}" in out


@pytest.mark.skipif(not (HAS_PANDOC and HAS_XELATEX), reason="pandoc + xelatex required")
def test_full_pipeline_smoke(tmp_path: Path):
    """End-to-end on a tiny markdown sample. Verifies PDF lands in target dir."""
    md = tmp_path / ".weekly_report" / "baseline" / "tiny.md"
    md.parent.mkdir(parents=True)
    md.write_text(
        "**Smoke 报告**\n\n李老师好：\n\n# 一、节标题\n\n"
        "测试内容 $a^2 + b^2 = c^2$ 与中文混排。\n",
        encoding="utf-8",
    )
    out = render_pdf(
        md_path=md, template_path=_template_path(),
        project_root=tmp_path,
        out_pdf_dir=tmp_path / ".weekly_report" / "baseline",
        aux_dir=tmp_path / ".weekly_report" / "baseline_tex",
        output_basename="tiny",
    )
    assert out["status"] == "ok", f"reason={out.get('reason')}"
    assert Path(out["pdf_path"]).exists()
    assert Path(out["pdf_path"]).stat().st_size > 1000
