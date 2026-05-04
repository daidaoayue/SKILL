"""Parse a filled interview.md.

Strategy:
  H1 anchors (## ① ... ## ⑨) are STRICT: serial number must match.
  H2/text inside each H1 block is loose: parser doesn't care about section
  titles, just extracts (a) raw block, (b) all `**请填**:` text blocks,
  (c) all checkbox lines.
"""
from __future__ import annotations
import re

H1_RE = re.compile(r"^##\s+([①②③④⑤⑥⑦⑧⑨])\s+(.*)$", re.MULTILINE)
META_RE = re.compile(r"^-\s*(\w+):\s*(.+)$", re.MULTILINE)
FILLIN_RE = re.compile(r"\*\*请填\*\*\s*[:：]\s*(.+?)(?=\n\s*\n|\Z)", re.DOTALL)
CHECKBOX_RE = re.compile(r"^\s*-\s*\[(?P<m>[ xX])\]\s+(?P<text>.+)$", re.MULTILINE)

ALL_KEYS = list("①②③④⑤⑥⑦⑧⑨")


def parse_interview(md: str) -> dict:
    """Parse a filled-in interview.md. Returns {meta: {...}, sections: {anchor: {...}}}."""
    out: dict = {"meta": {}, "sections": {k: None for k in ALL_KEYS}}

    head_split = H1_RE.split(md, maxsplit=1)
    head = head_split[0] if head_split else md
    for m in META_RE.finditer(head):
        out["meta"][m.group(1)] = m.group(2).strip()

    matches = list(H1_RE.finditer(md))
    for i, m in enumerate(matches):
        key = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        block = md[start:end].strip()
        fill_in_blocks = [t.strip().rstrip("\n").strip() for t in FILLIN_RE.findall(block)]
        checkboxes = []
        for cb in CHECKBOX_RE.finditer(block):
            checkboxes.append({
                "text": cb.group("text").strip(),
                "checked": cb.group("m").strip().lower() == "x",
            })
        out["sections"][key] = {
            "title": m.group(2).strip(),
            "raw": block,
            "fill_in": "\n\n".join(b for b in fill_in_blocks if b and b != "______"),
            "checkboxes": checkboxes,
        }
    return out
