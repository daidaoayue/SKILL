"""Tests for theory_extractor math block scanner."""
from pathlib import Path
from scripts.theory_extractor import extract_math_blocks


SAMPLE = r"""# Title
Some prose.

$$|mean(exp(j\phi))|$$

More prose with inline math \(a+b\) here.

\begin{equation}
\sum abs(RD)
\end{equation}
"""


def test_extract_three_kinds(tmp_path: Path):
    f = tmp_path / "theory.md"
    f.write_text(SAMPLE, encoding="utf-8")
    blocks = extract_math_blocks(f)
    kinds = sorted(b.kind for b in blocks)
    assert kinds == ["display_dollar", "equation_env", "inline_paren"]


def test_extract_returns_section_when_present(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("## 2.1 PhaseAmp\n\n$$x=y$$\n", encoding="utf-8")
    blocks = extract_math_blocks(f)
    assert blocks[0].section == "2.1 PhaseAmp"


def test_extract_skips_code_fences(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("```\n$$ignore$$\n```\n\n$$keep$$\n", encoding="utf-8")
    blocks = extract_math_blocks(f)
    assert len(blocks) == 1
    assert "keep" in blocks[0].body


def test_extract_returns_in_source_order(tmp_path: Path):
    f = tmp_path / "t.md"
    f.write_text("$$first$$\n\n\\(second\\)\n\n\\begin{equation}third\\end{equation}\n",
                 encoding="utf-8")
    blocks = extract_math_blocks(f)
    assert [b.body for b in blocks] == ["first", "second", "third"]


def test_extract_empty_file(tmp_path: Path):
    f = tmp_path / "empty.md"
    f.write_text("", encoding="utf-8")
    assert extract_math_blocks(f) == []


def test_tex_file_recognizes_latex_section(tmp_path: Path):
    """In .tex files, \\section{...} is the heading source — not markdown #."""
    f = tmp_path / "ch.tex"
    f.write_text(
        "\\section{2.1 RD signal processing}\n"
        "Some text.\n"
        "\\begin{equation}\n"
        "S(k) = \\sum x_n e^{-j2\\pi kn}\n"
        "\\end{equation}\n"
        "\\subsection{2.1.1 fusion}\n"
        "More text.\n"
        "$$y = Wx$$\n",
        encoding="utf-8",
    )
    blocks = extract_math_blocks(f)
    assert len(blocks) == 2
    # First block: under \section
    assert blocks[0].section == "2.1 RD signal processing"
    # Second block: under \subsection (most recent)
    assert blocks[1].section == "2.1.1 fusion"


def test_md_file_unchanged_for_tex_recognition(tmp_path: Path):
    """In .md files, only # headings count, NOT \\section{} (would be literal text)."""
    f = tmp_path / "x.md"
    f.write_text(
        "## My MD section\n\n"
        "\\section{This is literal text in md}\n\n"
        "$$x=1$$\n",
        encoding="utf-8",
    )
    blocks = extract_math_blocks(f)
    assert blocks[0].section == "My MD section"


def test_tex_section_with_optional_argument(tmp_path: Path):
    """\\section[short]{long title} — capture only the {} argument."""
    f = tmp_path / "ch.tex"
    f.write_text(
        "\\section[Short ToC entry]{完整章节标题}\n"
        "$$a+b=c$$\n",
        encoding="utf-8",
    )
    blocks = extract_math_blocks(f)
    assert blocks[0].section == "完整章节标题"
