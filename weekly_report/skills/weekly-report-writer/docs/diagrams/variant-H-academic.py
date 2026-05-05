"""Variant H · Academic Diagram (matplotlib).

Clean academic style — like a figure that goes into a paper or a thesis.
Black & white only, sans-serif labels (Helvetica fallback), boxed nodes,
explicit data flows annotated.

Run:
    python variant-H-academic.py

Output:
    variant-H-academic.png  (landscape, 200 dpi)
"""
from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

# --- Palette (3 grays only — academic minimalism) ---
BLACK = "#000000"
GRAY  = "#555555"
LIGHT = "#DDDDDD"
WHITE = "#FFFFFF"

# Landscape layout, suitable for a 2-column paper figure.
W_IN, H_IN = 11.0, 6.5
DPI = 200


def box(ax, x, y, w, h, label, sublabel=None, *, fill=WHITE,
        edge=BLACK, lw=1.2, fontsize=10):
    rect = patches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.005,rounding_size=0.008",
        facecolor=fill, edgecolor=edge, linewidth=lw,
        transform=ax.transAxes,
    )
    ax.add_patch(rect)
    cy = y + h / 2 + (0.012 if sublabel else 0)
    ax.text(x + w / 2, cy, label, fontsize=fontsize, color=BLACK,
            family="sans-serif", weight="medium",
            ha="center", va="center", transform=ax.transAxes)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 - 0.015, sublabel, fontsize=fontsize - 2.5,
                color=GRAY, family="sans-serif",
                ha="center", va="center", transform=ax.transAxes)


def arrow(ax, x0, y0, x1, y1, label=None, *, lw=1.0, label_offset=(0, 0.012)):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color=BLACK, lw=lw,
                        shrinkA=2, shrinkB=2),
    )
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx + label_offset[0], my + label_offset[1], label,
                fontsize=7.5, color=GRAY, family="sans-serif", style="italic",
                ha="center", va="center", transform=ax.transAxes)


def main(out_path: Path):
    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI)
    fig.patch.set_facecolor(WHITE)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    # Title
    ax.text(0.5, 0.94,
            "Figure 1. weekly-report-writer · End-to-end Workflow",
            fontsize=12, color=BLACK, family="sans-serif", weight="medium",
            ha="center", va="center", transform=ax.transAxes)

    # Top row: pipeline (5 stages, left to right)
    stages = [
        ("Init",      "user invokes\n/weekly-report init"),
        ("Scan",      "ThreadPool walker\n→ manifest.json"),
        ("Diff",      "compute_diff\n→ diff.json"),
        ("Interview", "L3 questionnaire\n→ interview.md"),
        ("Render",    "writer + pandoc\n→ report.{md,pdf}"),
    ]
    x_left, x_right = 0.05, 0.95
    n = len(stages)
    box_w = 0.13
    box_h = 0.16
    y_top = 0.62
    centers = [x_left + (x_right - x_left) * (i + 0.5) / n for i in range(n)]
    for cx, (name, sub) in zip(centers, stages):
        box(ax, cx - box_w / 2, y_top, box_w, box_h, name, sub,
            fill=WHITE, lw=1.4, fontsize=11)

    # Pipeline arrows
    for i in range(n - 1):
        x0 = centers[i] + box_w / 2
        x1 = centers[i + 1] - box_w / 2
        arrow(ax, x0, y_top + box_h / 2, x1, y_top + box_h / 2)

    # Section divider line
    ax.plot([0.05, 0.95], [0.55, 0.55], color=GRAY, lw=0.6,
            linestyle=(0, (4, 3)), transform=ax.transAxes)
    ax.text(0.05, 0.535, "Internal modules (deterministic)",
            fontsize=9, color=GRAY, family="sans-serif", style="italic",
            ha="left", va="center", transform=ax.transAxes)

    # Internal modules: 3 columns × 2 rows  (the 6 most important deterministic scripts)
    mods = [
        ("scan_project",      "ThreadPool walker"),
        ("parse_filename",    "family · version · status"),
        ("bucket_classifier", "path → 7 buckets"),
        ("compute_diff",      "cross-week comparison"),
        ("extract_metrics",   "JSON → mean ± std"),
        ("theory_extractor",  ".md / .tex → math blocks"),
    ]
    box_w2 = 0.16
    box_h2 = 0.12
    y_mods_top = 0.40
    y_mods_bot = 0.22
    cols_x = [0.13, 0.42, 0.71]
    for i, (name, sub) in enumerate(mods):
        col = i % 3
        row_y = y_mods_top if i < 3 else y_mods_bot
        box(ax, cols_x[col], row_y, box_w2, box_h2, name, sub,
            fill=LIGHT, edge=GRAY, lw=0.8, fontsize=9.5)

    # Bottom: outputs
    ax.text(0.05, 0.135, "Persisted outputs (write-whitelisted)",
            fontsize=9, color=GRAY, family="sans-serif", style="italic",
            ha="left", va="center", transform=ax.transAxes)
    ax.plot([0.05, 0.95], [0.12, 0.12], color=GRAY, lw=0.6,
            linestyle=(0, (4, 3)), transform=ax.transAxes)

    out_w = 0.27
    out_h = 0.07
    out_y = 0.03
    out_xs = [0.06, 0.36, 0.66]
    out_items = [
        ("<project>/.weekly_report/", "per-project state + report"),
        ("reports_root/<year>/<month>/", "cross-project archive"),
        ("reports_root/index.md", "global index"),
    ]
    for cx, (name, sub) in zip(out_xs, out_items):
        box(ax, cx, out_y, out_w, out_h, name, sub,
            fill=WHITE, edge=BLACK, lw=1.0, fontsize=8.5)

    # Side caption
    ax.text(0.95, 0.55, "Red line: scripts/path_guard.py blocks any write\n"
                       "outside the two whitelisted roots.",
            fontsize=7.5, color=GRAY, family="sans-serif", style="italic",
            ha="right", va="bottom", transform=ax.transAxes)

    fig.savefig(out_path, dpi=DPI, facecolor=WHITE, bbox_inches=None)
    plt.close(fig)
    print(f"Rendered → {out_path}")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "variant-H-academic.png"
    main(out)
