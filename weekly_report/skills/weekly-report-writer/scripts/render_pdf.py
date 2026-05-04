"""Markdown report → LaTeX → PDF via pandoc + xelatex.

Pipeline:
  1. md → pandoc → latex fragment (body only, no preamble)
  2. wrap fragment in `assets/baseline-tex-template.tex` (BODY_PLACEHOLDER)
  3. xelatex compile with -output-directory pointed at <project>/.weekly_report/baseline_tex/
  4. copy resulting PDF up to <project>/.weekly_report/baseline/<name>.pdf

External tools required:
  - pandoc (any 2.x or 3.x)
  - xelatex (e.g. MiKTeX or TeX Live)

If either is missing, the function returns dict with status='skipped' and a reason,
so the markdown report still ships even on machines without LaTeX.
"""
from __future__ import annotations
import re
import shutil
import subprocess
from pathlib import Path

from scripts.path_guard import assert_write_allowed


# --- Post-process the pandoc-emitted .tex to make long file paths breakable ---
# Pandoc renders inline `code` as \texttt{...}, which by default does not break
# in the middle, causing long file paths to overflow longtable cells. We inject
# \allowbreak{} after every "/" or "\_" inside path-like \texttt spans, which
# gives TeX explicit line-break opportunities without changing the rendered
# glyphs. \allowbreak is a primitive — no package needed — and (unlike seqsplit)
# coexists peacefully with pandoc's "\_" escaping of underscores.
_PATH_TEXTTT_RE = re.compile(r"\\texttt\{([^{}]+)\}")


def _is_pathlike(s: str) -> bool:
    """Heuristic: a `code` span is "path-like" if it has / or _ or is long."""
    return ("/" in s) or (len(s) >= 22 and ("_" in s or r"\_" in s))


def _inject_breakopps(s: str) -> str:
    """Add \\allowbreak{} after each "/" and after each pandoc-escaped "\\_"."""
    s = re.sub(r"(/)", r"\1\\allowbreak{}", s)
    s = re.sub(r"(\\_)", r"\1\\allowbreak{}", s)
    return s


def break_long_paths(tex: str) -> str:
    """Inject \\allowbreak{} into path-like \\texttt{...} spans."""
    def repl(m: re.Match) -> str:
        s = m.group(1)
        if _is_pathlike(s):
            return r"\texttt{" + _inject_breakopps(s) + r"}"
        return m.group(0)
    return _PATH_TEXTTT_RE.sub(repl, tex)


# --- Rebalance pandoc's equal-width longtable columns ---
# Pandoc emits naive equal widths (0.5/0.5 for 2-col, 0.25*4 for 4-col), causing
# file-path columns to wrap while timestamp columns sit half-empty. We rewrite
# common patterns to favor the (long) file-path column.
_LONGTABLE_BLOCK_RE = re.compile(
    r"(\\begin\{longtable\}\[\]\{@\{\}\s*\n"
    r"(?:\s*>\{\\raggedright\\arraybackslash\}p\{\([^)]+\)\s*\*\s*\\real\{[0-9.]+\}\}\s*\n?)+"
    r"\s*@\{\}\})",
    re.MULTILINE,
)
_REAL_WIDTH_RE = re.compile(r"\\real\{([0-9.]+)\}")


def _rebalance_block(block: str) -> str:
    """Rewrite column-width \\real{...} values inside one longtable spec.

    Heuristics tuned for the weekly-report tables:
    - 2 cols both 0.5 → 0.78 / 0.22 (file / mtime)
    - 4 cols all 0.25 → 0.20 / 0.12 / 0.50 / 0.18 (family / 版本 / path / mtime)
    - 5 cols all 0.2  → 0.28 / 0.22 / 0.13 / 0.13 / 0.24 (metric tables)
    Other patterns left untouched.
    """
    widths = _REAL_WIDTH_RE.findall(block)
    n = len(widths)
    floats = [float(w) for w in widths]
    target: list[float] | None = None
    if n == 2 and all(abs(w - 0.5) < 0.01 for w in floats):
        target = [0.78, 0.22]
    elif n == 4 and all(abs(w - 0.25) < 0.01 for w in floats):
        target = [0.20, 0.12, 0.50, 0.18]
    elif n == 5 and all(abs(w - 0.2) < 0.01 for w in floats):
        target = [0.28, 0.22, 0.13, 0.13, 0.24]
    if target is None:
        return block
    it = iter(f"{t:.4f}" for t in target)
    return _REAL_WIDTH_RE.sub(lambda m: f"\\real{{{next(it)}}}", block)


def rebalance_longtable_columns(tex: str) -> str:
    """Apply _rebalance_block to every longtable column spec in `tex`."""
    return _LONGTABLE_BLOCK_RE.sub(lambda m: _rebalance_block(m.group(1)), tex)


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def md_to_tex_fragment(md_path: Path) -> str:
    """Run pandoc to convert markdown → LaTeX fragment (no preamble)."""
    proc = subprocess.run(
        [
            "pandoc",
            str(md_path),
            "-f", "markdown+tex_math_dollars",
            "-t", "latex",
            "--wrap=preserve",
            "--no-highlight",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return proc.stdout


def render_pdf(
    *,
    md_path: Path,
    template_path: Path,
    project_root: Path,
    out_pdf_dir: Path,    # <project>/.weekly_report/baseline/
    aux_dir: Path,        # <project>/.weekly_report/baseline_tex/
    output_basename: str = "baseline_report",
) -> dict:
    """Compile markdown report to PDF.

    Returns: {"status": "ok" | "skipped" | "error",
              "pdf_path": str | None, "tex_path": str | None,
              "reason": str | None, "log_tail": str | None}
    """
    assert_write_allowed(out_pdf_dir / f"{output_basename}.pdf", project_root=project_root)
    assert_write_allowed(aux_dir / f"{output_basename}.tex", project_root=project_root)
    out_pdf_dir.mkdir(parents=True, exist_ok=True)
    aux_dir.mkdir(parents=True, exist_ok=True)

    if not _have("pandoc"):
        return {"status": "skipped", "pdf_path": None, "tex_path": None,
                "reason": "pandoc not in PATH", "log_tail": None}
    if not _have("xelatex"):
        return {"status": "skipped", "pdf_path": None, "tex_path": None,
                "reason": "xelatex not in PATH", "log_tail": None}

    # Step 1: md → tex fragment
    try:
        fragment = md_to_tex_fragment(md_path)
    except subprocess.CalledProcessError as e:
        return {"status": "error", "pdf_path": None, "tex_path": None,
                "reason": f"pandoc failed: {e.stderr[:500] if e.stderr else 'no stderr'}",
                "log_tail": None}

    # Step 1.5: post-process — break long paths + rebalance equal-width columns
    fragment = break_long_paths(fragment)
    fragment = rebalance_longtable_columns(fragment)

    # Step 2: wrap in template
    template = template_path.read_text(encoding="utf-8")
    if "% BODY_PLACEHOLDER" not in template:
        return {"status": "error", "pdf_path": None, "tex_path": None,
                "reason": f"template missing '% BODY_PLACEHOLDER' marker: {template_path}",
                "log_tail": None}
    wrapped = template.replace("% BODY_PLACEHOLDER", fragment)
    tex_out = aux_dir / f"{output_basename}.tex"
    tex_out.write_text(wrapped, encoding="utf-8")

    # Step 3: xelatex compile (one pass — no ToC/cross-refs in baseline)
    try:
        proc = subprocess.run(
            [
                "xelatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={aux_dir}",
                str(tex_out),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(aux_dir),
            check=False,
        )
    except FileNotFoundError as e:
        return {"status": "error", "pdf_path": None, "tex_path": str(tex_out),
                "reason": f"xelatex launch failed: {e}", "log_tail": None}

    pdf_in_aux = aux_dir / f"{output_basename}.pdf"
    if not pdf_in_aux.exists():
        log_path = aux_dir / f"{output_basename}.log"
        log_tail = ""
        if log_path.exists():
            try:
                log_tail = log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
            except OSError:
                pass
        return {"status": "error", "pdf_path": None, "tex_path": str(tex_out),
                "reason": f"xelatex did not produce PDF (returncode={proc.returncode})",
                "log_tail": log_tail}

    # Step 4: copy PDF up to baseline dir
    pdf_final = out_pdf_dir / f"{output_basename}.pdf"
    assert_write_allowed(pdf_final, project_root=project_root)
    shutil.copy2(pdf_in_aux, pdf_final)

    return {"status": "ok", "pdf_path": str(pdf_final), "tex_path": str(tex_out),
            "reason": None, "log_tail": None}
