# Theory Extraction Rules

`theory_extractor.py` extracts math blocks from .md/.tex files. This document
describes what counts as a "math block" and how the extractor handles edge cases.

## Recognized formats

1. **Display dollar**: `$$...$$` — `kind = display_dollar`
2. **Inline parenthesis**: `\(...\)` — `kind = inline_paren`
3. **Equation environment**: `\begin{equation}...\end{equation}` — `kind = equation_env`

## Not recognized (yet)

- `$...$` (inline single dollar) — too noisy, false-positive on `$1.99`
- `\[...\]` (display bracket) — rare; can be added in a future version
- `\begin{align}`, `eqnarray`, etc. — not crucial for weekly diff

## Skipped contexts

The extractor strips fenced code blocks (```` ``` ```` ... ```` ``` ````) before
scanning so equations inside a code block are not picked up.

## Section attribution

Each block is associated with the most recent markdown heading (`#`/`##`/`###`)
preceding it. If no heading exists, `section = None`.

## Diff between weeks

`compute_diff` compares blocks by `(file, body)` tuples:
- New `(file, body)` not seen last week → `math_blocks_added`
- Old `(file, body)` not seen this week → `math_blocks_deleted`
- Same `(file, _)` but different body in same `section` → `math_blocks_modified`

## Limitations

- Whitespace normalization is naïve. `$$x = y$$` and `$$x=y$$` are treated as
  different bodies. Acceptable for now since LLM Writer can dedupe semantically.
- LaTeX comments (`% ...`) inside an equation block are kept verbatim.

## Why theory matters in weekly reports

Pure code/data diff misses the most valuable PhD output: when you derive a new
equation, prove a lemma, or formalize a method, that goes in `.md` or `.tex` text,
not in code. The theory bucket exists so the weekly report doesn't miss this layer.

The sample weekly report (`2026春-3月第1周报-李越.docx`) demonstrates this:
section "PhaseAmp相位保留方法总结" contains formula derivations like
`|mean(exp(jφ))|` that wouldn't show up in any code/data diff.
