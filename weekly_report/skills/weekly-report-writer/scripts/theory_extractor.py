"""Extract math blocks from .md/.tex files for the theory bucket diff.

Recognized:
  - $$...$$         (display_dollar)
  - \\(...\\)       (inline_paren)
  - \\begin{equation}...\\end{equation}  (equation_env)
Skips fenced code blocks (``` ... ```).
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from pathlib import Path

DOLLAR_RE   = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
INLINE_RE   = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
EQUATION_RE = re.compile(r"\\begin\{equation\}(.+?)\\end\{equation\}", re.DOTALL)
# Markdown heading: # / ## / ###
MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
# LaTeX section command: \section{...} / \subsection{...} / \subsubsection{...} / \paragraph{...} / \chapter{...}
TEX_HEADING_RE = re.compile(
    r"^\s*\\(?:chapter|section|subsection|subsubsection|paragraph|subparagraph)\*?"
    r"(?:\[[^\]]*\])?\{([^}]+)\}",
    re.MULTILINE,
)
FENCE_RE    = re.compile(r"```.*?```", re.DOTALL)


@dataclass
class MathBlock:
    file: str
    kind: str       # display_dollar / inline_paren / equation_env
    body: str
    section: str | None
    span: tuple[int, int]


def _strip_code_fences(text: str) -> str:
    # Replace fenced code blocks with whitespace of equal length so spans stay valid.
    return FENCE_RE.sub(lambda m: " " * (m.end() - m.start()), text)


def _section_for(text: str, pos: int, is_tex: bool) -> str | None:
    """Find the most recent heading before `pos`. Recognizes both markdown
    `#` headings and LaTeX `\\section{}` family for `.tex` files."""
    last = None
    if is_tex:
        # Inside .tex, only LaTeX section commands count as headings.
        # `# foo` is not a markdown heading; it's just a comment-like char.
        for m in TEX_HEADING_RE.finditer(text):
            if m.start() > pos:
                break
            last = m.group(1).strip()
    else:
        for m in MD_HEADING_RE.finditer(text):
            if m.start() > pos:
                break
            last = m.group(2).strip()
    return last


def extract_math_blocks(path: Path) -> list[MathBlock]:
    """Return all math blocks in `path`, in source order."""
    raw = path.read_text(encoding="utf-8")
    cleaned = _strip_code_fences(raw)
    is_tex = path.suffix.lower() == ".tex"
    out: list[MathBlock] = []
    for kind, regex in (
        ("display_dollar", DOLLAR_RE),
        ("inline_paren",   INLINE_RE),
        ("equation_env",   EQUATION_RE),
    ):
        for m in regex.finditer(cleaned):
            section = _section_for(raw, m.start(), is_tex=is_tex)
            out.append(MathBlock(
                file=str(path),
                kind=kind,
                body=m.group(1).strip(),
                section=section,
                span=(m.start(), m.end()),
            ))
    out.sort(key=lambda b: b.span[0])
    return out
