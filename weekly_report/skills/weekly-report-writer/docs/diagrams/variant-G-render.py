"""Variant G renderer — "Studio Friday Evening".

Render the weekly-report-writer workflow as a calm, paper-cream A4 figure
following the philosophy in `variant-G-philosophy.md`.

Run:
    python variant-G-render.py

Output:
    variant-G-poster.png  (A4, 300 dpi)
"""
from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

# --- Palette (four hues, philosophy-mandated) ---
PAPER  = "#F5F1E8"
INK    = "#1A2332"
PENCIL = "#6B6F76"
EMBER  = "#C4541C"

# --- Canvas: portrait, slightly wider than A4 for better legibility at on-screen view ---
A4_W_IN, A4_H_IN = 9.6, 13.0
DPI = 300


def text(ax, x, y, s, *, size=10, color=INK, weight="normal",
         family="serif", ha="left", va="baseline", style="normal"):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                   family=family, ha=ha, va=va, style=style, transform=ax.transAxes)


def hline(ax, x0, x1, y, *, lw=1.0, color=INK, double=False):
    ax.plot([x0, x1], [y, y], lw=lw, color=color, transform=ax.transAxes,
            solid_capstyle="butt")
    if double:
        ax.plot([x0, x1], [y - 0.005, y - 0.005], lw=lw, color=color,
                transform=ax.transAxes, solid_capstyle="butt")


def stage_circle(ax, cx, cy, num, label, sub, *, deliverable=False):
    color_fill = EMBER if deliverable else PAPER
    color_edge = EMBER if deliverable else INK
    color_num = PAPER if deliverable else INK
    color_label = EMBER if deliverable else INK

    # circle
    circle = patches.Circle(
        (cx, cy), radius=0.030, facecolor=color_fill,
        edgecolor=color_edge, linewidth=1.8, transform=ax.transAxes, zorder=3,
    )
    ax.add_patch(circle)
    text(ax, cx, cy, num, size=14, color=color_num,
         family="monospace", ha="center", va="center", weight="medium")
    text(ax, cx, cy - 0.062, label, size=16, color=color_label,
         family="serif", weight="semibold", ha="center", va="center")
    text(ax, cx, cy - 0.094, sub, size=10, color=PENCIL,
         family="monospace", ha="center", va="center")


def main(out_path: Path):
    fig = plt.figure(figsize=(A4_W_IN, A4_H_IN), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(PAPER)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    # === Top header strip ===
    hline(ax, 0.06, 0.94, 0.948, lw=1.0, color=INK, double=True)
    hline(ax, 0.06, 0.94, 0.928, lw=0.6, color=INK)
    text(ax, 0.06, 0.937, "SHEET 01 · WORKFLOW · REV E",
         size=11, color=PENCIL, family="monospace")
    text(ax, 0.5, 0.937, "weekly-report-writer · v1.0",
         size=12, color=INK, weight="semibold", family="serif", ha="center")
    text(ax, 0.94, 0.937, "SCALE 1:1 · A4",
         size=11, color=PENCIL, family="monospace", ha="right")

    # === Title ===
    text(ax, 0.06, 0.86, "The Weekly Report,",
         size=42, color=INK, weight="bold", family="serif")
    text(ax, 0.06, 0.808, "drafted in 5 minutes.",
         size=42, color=EMBER, weight="bold", family="serif")
    text(ax, 0.06, 0.770,
         "A Claude Code skill — scan project · diff vs last week · "
         "interview · render PhD-format report.",
         size=11, color=PENCIL, family="monospace")

    # === Pipeline ===
    text(ax, 0.06, 0.720, "PIPELINE",
         size=11, color=PENCIL, family="monospace", weight="medium")
    hline(ax, 0.06, 0.94, 0.712, lw=0.6, color=INK)

    # rail line
    rail_y = 0.66
    ax.plot([0.13, 0.87], [rail_y, rail_y], lw=0.7, color=INK,
            transform=ax.transAxes, zorder=1)

    stages = [
        ("01", "Init",      "/weekly-report init",  False),
        ("02", "Scan",      "manifest.json",         False),
        ("03", "Diff",      "metric delta · new eqs", False),
        ("04", "Interview", "L3 questionnaire",      False),
        ("05", "Report",    ".md + .pdf",            True),
    ]
    xs = [0.13, 0.31, 0.49, 0.67, 0.87]
    for x, (n, lbl, sub, deliver) in zip(xs, stages):
        stage_circle(ax, x, rail_y, n, lbl, sub, deliverable=deliver)

    # === Architecture / three strata ===
    text(ax, 0.06, 0.485, "ARCHITECTURE · THREE STRATA",
         size=11, color=PENCIL, family="monospace", weight="medium")
    hline(ax, 0.06, 0.94, 0.476, lw=0.6, color=INK)

    layers = [
        ("LLM Orchestration", "SKILL.md",
         ["mode router", "narrative synthesis", "interview drive"], INK),
        ("Deterministic Python", "scripts/ · 16 modules",
         ["scan_project", "compute_diff", "extract_metrics",
          "theory_extractor", "render_pdf"], INK),
        ("Path Guard", "RED LINE",
         ["whitelist enforcer", "PathGuardError", "21 test cases"], EMBER),
        ("Persistence", "writeable only",
         ["<project>/.weekly_report/", "reports_root/<year>/<month>/", "index.md"], INK),
    ]
    y = 0.450
    row_h = 0.072
    for name, tag, mods, accent in layers:
        # left label
        text(ax, 0.06, y - 0.022, name, size=14, color=accent,
             weight="semibold", family="serif")
        text(ax, 0.06, y - 0.045, tag, size=9.5, color=accent,
             family="monospace", weight="medium")
        # modules: wrap as comma-list
        mods_str = "  ·  ".join(mods)
        text(ax, 0.32, y - 0.034, mods_str, size=10.5, color=PENCIL,
             family="monospace")
        # rule
        hline(ax, 0.06, 0.94, y - row_h + 0.006,
              lw=0.4, color=PENCIL if accent != EMBER else EMBER)
        y -= row_h

    # === Ledger ===
    text(ax, 0.06, 0.150, "LEDGER",
         size=11, color=PENCIL, family="monospace", weight="medium")
    hline(ax, 0.06, 0.94, 0.140, lw=1.0, color=INK, double=True)

    ledger_items = [
        ("INIT TIME", "~10 min"),
        ("WEEKLY TIME", "~5–10 min"),
        ("TESTS", "132 passed"),
        ("LICENSE", "MIT"),
    ]
    xs_l = [0.10, 0.32, 0.55, 0.78]
    for x, (label, val) in zip(xs_l, ledger_items):
        text(ax, x, 0.095, label, size=10, color=PENCIL,
             family="monospace", weight="medium")
        text(ax, x, 0.058, val, size=20, color=INK,
             family="serif", weight="semibold")

    # === Footer signature ===
    text(ax, 0.06, 0.020,
         "drawn in the spirit of Quiet Cartography · 2026",
         size=10, color=PENCIL, family="serif", style="italic")
    text(ax, 0.94, 0.020, "daidaoayue/SKILL",
         size=10, color=PENCIL, family="monospace", ha="right")

    # save
    fig.savefig(out_path, dpi=DPI, facecolor=PAPER, bbox_inches=None)
    plt.close(fig)
    print(f"Rendered → {out_path}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "variant-G-poster.png"
    main(out)
