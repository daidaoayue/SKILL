# -*- coding: utf-8 -*-
"""
variant-E-clean.py

Clean two-column pipeline architecture diagram for thesis-helper.

Layout (top to bottom):
  1) Title strip with legend (I/O orange + CPU blue + Skill green)
  2) Two-column body wrapped in a dashed rounded rectangle:
       Left  : "Project Offline Setup" panel (3 cards stacked)
       Right : "On-board Runtime" panel containing 3 dashed sub-layers,
               each holding 3 cards horizontally.
  3) Bottom: 3 KPI cards (End-to-End Phase / Skill Registry / Pipeline Version)

Color coding (strict):
  - I/O   : fill #f4d6b8, text #c87f3a, edge #d4a76a
  - CPU   : fill #cce0f5, text #3a7ec4, edge #6ba6dc
  - Skill : fill #d4ead4, text #4a8c4a, edge #7eb87e

Icons are drawn with matplotlib primitives (Rectangle / Polygon / Circle /
Wedge), so they do NOT depend on Unicode glyph coverage of the system font.
That keeps the figure font-portable and avoids the tofu (□) problem.
"""

import math
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import (
    FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon, Circle, Wedge,
    PathPatch,
)
from matplotlib.path import Path
from matplotlib.lines import Line2D

# ---------- font ----------
mpl.rcParams['font.sans-serif'] = [
    'Microsoft YaHei UI', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans'
]
mpl.rcParams['font.serif'] = ['SimSun', 'Times New Roman']
mpl.rcParams['axes.unicode_minus'] = False

# ---------- palette ----------
BG          = '#fafbfc'
PANEL_EDGE  = '#b8b8b8'
TXT_DARK    = '#2c3e50'
TXT_GREY    = '#6c7a89'
TXT_FAINT   = '#9aa5b1'

# I/O (orange)
IO_FILL = '#f4d6b8'
IO_EDGE = '#d4a76a'
IO_TXT  = '#c87f3a'

# CPU (light blue)
CPU_FILL = '#cce0f5'
CPU_EDGE = '#6ba6dc'
CPU_TXT  = '#3a7ec4'

# Skill (mint green)
SK_FILL = '#d4ead4'
SK_EDGE = '#7eb87e'
SK_TXT  = '#4a8c4a'

# KPI background
KPI_FILL = '#fbf6ec'
KPI_EDGE = '#e0d4b8'

ARROW_COLOR  = '#222222'
FANOUT_COLOR = '#7eb87e'
FANIN_COLOR  = '#7eb87e'

# ---------- canvas ----------
fig, ax = plt.subplots(figsize=(16, 13), dpi=220)
ax.set_xlim(0, 160)
ax.set_ylim(0, 130)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor(BG)


# =============================================================
# helpers
# =============================================================
def card(ax, cx, cy, w, h, fill, edge, lw=1.4, zorder=2, rounding=1.5):
    p = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rounding}",
        facecolor=fill, edgecolor=edge, linewidth=lw, zorder=zorder
    )
    ax.add_patch(p)


def dashed_panel(ax, x0, y0, w, h, edge=PANEL_EDGE, lw=1.3, rounding=2.0,
                 fill='none', zorder=1):
    p = FancyBboxPatch(
        (x0, y0), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={rounding}",
        facecolor=fill, edgecolor=edge, linewidth=lw,
        linestyle=(0, (5, 4)), zorder=zorder
    )
    ax.add_patch(p)


def arrow(ax, x1, y1, x2, y2, color=ARROW_COLOR, lw=1.4, mut=12, zorder=3,
          style='-'):
    a = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='-|>', mutation_scale=mut,
        color=color, linewidth=lw, zorder=zorder, linestyle=style,
        shrinkA=0, shrinkB=0
    )
    ax.add_patch(a)


# =============================================================
# ICON drawing primitives — all matplotlib, no font dependency
# =============================================================
def _add(ax, p, z=4):
    p.set_zorder(z)
    ax.add_patch(p)


def icon_doc(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Document icon: page + folded corner + 3 lines."""
    w, h = s * 1.5, s * 2.0
    x0, y0 = cx - w / 2, cy - h / 2
    # main body
    _add(ax, Rectangle((x0, y0), w, h, facecolor='white',
                       edgecolor=color, linewidth=1.2), z)
    # folded corner triangle
    fold = s * 0.55
    poly = Polygon(
        [(x0 + w - fold, y0 + h),
         (x0 + w, y0 + h - fold),
         (x0 + w - fold, y0 + h - fold)],
        facecolor=color, edgecolor=color, linewidth=0.8)
    _add(ax, poly, z)
    # text lines
    for i in range(3):
        ly = y0 + h - fold - s * 0.55 - i * s * 0.42
        ax.add_line(Line2D([x0 + s * 0.25, x0 + w - s * 0.25],
                           [ly, ly], color=color, linewidth=0.9, zorder=z))


def icon_graph(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Three connected nodes (skill graph)."""
    r = s * 0.32
    p1 = (cx - s * 0.7, cy - s * 0.5)
    p2 = (cx + s * 0.75, cy - s * 0.5)
    p3 = (cx, cy + s * 0.85)
    # edges
    for a_, b_ in [(p1, p2), (p1, p3), (p2, p3)]:
        ax.add_line(Line2D([a_[0], b_[0]], [a_[1], b_[1]],
                           color=color, linewidth=1.1, zorder=z))
    # nodes
    for pt in (p1, p2, p3):
        _add(ax, Circle(pt, r, facecolor='white',
                        edgecolor=color, linewidth=1.3), z + 1)


def icon_gear(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Simple gear icon: 8 teeth + center hole."""
    R_out = s * 1.05
    R_in  = s * 0.78
    R_hole = s * 0.32
    teeth = 8
    pts = []
    # build alternating points (teeth)
    n = teeth * 2
    for i in range(n):
        ang = 2 * math.pi * i / n - math.pi / 2
        # add a flat top: pair samples per tooth
        r = R_out if (i % 2 == 0) else R_in
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    poly = Polygon(pts, closed=True, facecolor='white',
                   edgecolor=color, linewidth=1.2)
    _add(ax, poly, z)
    # inner ring
    _add(ax, Circle((cx, cy), R_hole, facecolor=color,
                    edgecolor=color, linewidth=1.0), z + 1)
    # very small white center
    _add(ax, Circle((cx, cy), R_hole * 0.45, facecolor='white',
                    edgecolor='none'), z + 2)


def icon_terminal(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Terminal icon: rectangle + chevron + cursor underline."""
    w, h = s * 2.0, s * 1.4
    x0, y0 = cx - w / 2, cy - h / 2
    _add(ax, FancyBboxPatch((x0, y0), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.25",
                            facecolor='white', edgecolor=color,
                            linewidth=1.2), z)
    # top bar
    _add(ax, Rectangle((x0, y0 + h - s * 0.32), w, s * 0.32,
                       facecolor=color, edgecolor=color, linewidth=0.8), z + 1)
    # chevron >
    cy_c = y0 + h * 0.42
    chevron = Polygon(
        [(x0 + s * 0.35, cy_c + s * 0.32),
         (x0 + s * 0.85, cy_c),
         (x0 + s * 0.35, cy_c - s * 0.32)],
        closed=False, fill=False,
        edgecolor=color, linewidth=1.3)
    _add(ax, chevron, z + 1)
    # cursor
    ax.add_line(Line2D([x0 + s * 1.0, x0 + s * 1.55],
                       [y0 + s * 0.35, y0 + s * 0.35],
                       color=color, linewidth=1.4, zorder=z + 1))


def icon_folder(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Folder icon."""
    w, h = s * 2.0, s * 1.4
    x0, y0 = cx - w / 2, cy - h / 2
    # tab
    tab = Polygon([(x0, y0 + h),
                   (x0 + s * 0.55, y0 + h + s * 0.32),
                   (x0 + s * 1.05, y0 + h + s * 0.32),
                   (x0 + s * 1.05, y0 + h)],
                  closed=True, facecolor='white',
                  edgecolor=color, linewidth=1.1)
    _add(ax, tab, z)
    # body
    _add(ax, FancyBboxPatch((x0, y0), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.18",
                            facecolor='white', edgecolor=color,
                            linewidth=1.2), z + 1)


def icon_magnifier(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Magnifying glass."""
    R = s * 0.7
    cyc = (cx - s * 0.15, cy + s * 0.2)
    _add(ax, Circle(cyc, R, facecolor='white',
                    edgecolor=color, linewidth=1.4), z)
    # handle
    hx0, hy0 = cyc[0] + R * 0.7, cyc[1] - R * 0.7
    hx1, hy1 = hx0 + s * 0.65, hy0 - s * 0.65
    ax.add_line(Line2D([hx0, hx1], [hy0, hy1],
                       color=color, linewidth=2.0, zorder=z + 1,
                       solid_capstyle='round'))


def icon_check(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Check mark in a rounded square."""
    w, h = s * 1.7, s * 1.7
    x0, y0 = cx - w / 2, cy - h / 2
    _add(ax, FancyBboxPatch((x0, y0), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.3",
                            facecolor='white', edgecolor=color,
                            linewidth=1.2), z)
    # check stroke
    pts_x = [x0 + s * 0.32, x0 + s * 0.78, x0 + s * 1.40]
    pts_y = [y0 + s * 0.85, y0 + s * 0.40, y0 + s * 1.20]
    ax.add_line(Line2D(pts_x, pts_y, color=color,
                       linewidth=2.2, zorder=z + 1,
                       solid_capstyle='round',
                       solid_joinstyle='round'))


def icon_funnel(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Funnel icon."""
    # top wide trapezoid
    top_w = s * 1.8
    mid_w = s * 0.5
    h_top = s * 0.85
    h_stem = s * 0.95
    poly = Polygon(
        [(cx - top_w / 2, cy + h_top),
         (cx + top_w / 2, cy + h_top),
         (cx + mid_w / 2, cy),
         (cx + mid_w / 2 * 0.5, cy - h_stem),
         (cx - mid_w / 2 * 0.5, cy - h_stem),
         (cx - mid_w / 2, cy)],
        closed=True, facecolor='white',
        edgecolor=color, linewidth=1.3)
    _add(ax, poly, z)
    # rim
    ax.add_line(Line2D([cx - top_w / 2, cx + top_w / 2],
                       [cy + h_top, cy + h_top],
                       color=color, linewidth=1.6, zorder=z + 1))


def icon_chart(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Bar chart icon (3 bars + axis)."""
    w, h = s * 1.9, s * 1.6
    x0, y0 = cx - w / 2, cy - h / 2
    # axis
    ax.add_line(Line2D([x0, x0 + w], [y0, y0],
                       color=color, linewidth=1.4, zorder=z))
    ax.add_line(Line2D([x0, x0], [y0, y0 + h],
                       color=color, linewidth=1.4, zorder=z))
    # bars
    bw = s * 0.38
    gap = s * 0.18
    heights = [s * 0.55, s * 1.05, s * 0.78]
    for i, bh in enumerate(heights):
        bx = x0 + s * 0.25 + i * (bw + gap)
        _add(ax, Rectangle((bx, y0 + 0.01), bw, bh,
                           facecolor=color, edgecolor=color,
                           linewidth=0.8), z + 1)


def icon_monitor(ax, cx, cy, s=2.2, color='#2c3e50', z=4):
    """Monitor / display icon."""
    w, h = s * 2.1, s * 1.5
    x0, y0 = cx - w / 2, cy - h / 2 + s * 0.15
    _add(ax, FancyBboxPatch((x0, y0), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.2",
                            facecolor='white', edgecolor=color,
                            linewidth=1.3), z)
    # inner screen
    pad = s * 0.15
    _add(ax, Rectangle((x0 + pad, y0 + pad),
                       w - 2 * pad, h - 2 * pad,
                       facecolor=color, edgecolor='none', alpha=0.18), z + 1)
    # stand
    sx0, sy0 = cx - s * 0.55, y0 - s * 0.3
    _add(ax, Rectangle((sx0, sy0), s * 1.1, s * 0.18,
                       facecolor=color, edgecolor=color), z + 1)
    ax.add_line(Line2D([cx, cx], [y0, sy0 + s * 0.18],
                       color=color, linewidth=1.4, zorder=z + 1))


def icon_clock(ax, cx, cy, s=2.6, color='#2c3e50', z=4):
    """Clock icon."""
    R = s * 0.95
    _add(ax, Circle((cx, cy), R, facecolor='white',
                    edgecolor=color, linewidth=1.5), z)
    # ticks at 12/3/6/9
    for ang_deg in (0, 90, 180, 270):
        a = math.radians(ang_deg)
        x1 = cx + (R * 0.85) * math.cos(a)
        y1 = cy + (R * 0.85) * math.sin(a)
        x2 = cx + R * math.cos(a)
        y2 = cy + R * math.sin(a)
        ax.add_line(Line2D([x1, x2], [y1, y2],
                           color=color, linewidth=1.2, zorder=z + 1))
    # hands
    ax.add_line(Line2D([cx, cx], [cy, cy + R * 0.55],
                       color=color, linewidth=1.7, zorder=z + 2,
                       solid_capstyle='round'))
    ax.add_line(Line2D([cx, cx + R * 0.65], [cy, cy + R * 0.05],
                       color=color, linewidth=1.7, zorder=z + 2,
                       solid_capstyle='round'))
    _add(ax, Circle((cx, cy), R * 0.08, facecolor=color,
                    edgecolor=color), z + 3)


def icon_lightning(ax, cx, cy, s=2.6, color='#2c3e50', z=4):
    """Lightning bolt."""
    pts = [
        (cx - s * 0.2, cy + s * 1.05),
        (cx + s * 0.55, cy + s * 0.10),
        (cx + s * 0.05, cy + s * 0.10),
        (cx + s * 0.55, cy - s * 1.05),
        (cx - s * 0.45, cy + s * 0.05),
        (cx + s * 0.05, cy + s * 0.05),
    ]
    _add(ax, Polygon(pts, closed=True, facecolor=color,
                     edgecolor=color, linewidth=1.0), z)


def icon_target(ax, cx, cy, s=2.6, color='#2c3e50', z=4):
    """Bullseye / target rings."""
    radii = [s * 0.95, s * 0.65, s * 0.35]
    fills = ['white', color, 'white']
    for r, f in zip(radii, fills):
        if f == 'white':
            _add(ax, Circle((cx, cy), r, facecolor='white',
                            edgecolor=color, linewidth=1.4), z)
        else:
            _add(ax, Circle((cx, cy), r, facecolor=f,
                            edgecolor=color, linewidth=0.8), z + 1)
        z += 1
    # center dot
    _add(ax, Circle((cx, cy), s * 0.12, facecolor=color,
                    edgecolor=color), z + 5)


# =============================================================
# 1. TITLE strip
# =============================================================
ax.text(72, 124.5,
        'thesis-helper End-to-End Pipeline',
        ha='center', va='center',
        fontsize=22, fontweight='bold', color=TXT_DARK)

ax.text(72, 120.2,
        'Multi-branch Workflow for Student Thesis Writing',
        ha='center', va='center',
        fontsize=11.5, fontstyle='italic', color=TXT_GREY)


def legend_box(ax, cx, cy, fill, edge, label):
    sw = 3.2
    sh = 2.0
    ax.add_patch(Rectangle((cx - sw / 2, cy - sh / 2), sw, sh,
                           facecolor=fill, edgecolor=edge, linewidth=1.0))
    ax.text(cx + 2.3, cy, label, ha='left', va='center',
            fontsize=10, color=TXT_DARK)


legend_y = 124
legend_box(ax, 130, legend_y, IO_FILL, IO_EDGE, 'I/O')
legend_box(ax, 141, legend_y, CPU_FILL, CPU_EDGE, 'CPU')
legend_box(ax, 152, legend_y, SK_FILL,  SK_EDGE,  'Skill')

ax.add_line(Line2D([6, 154], [117.2, 117.2],
                   color='#dcdcdc', linewidth=1.0))


# =============================================================
# 2. BODY: dashed wrapper holding two panels
# =============================================================
BODY_X0, BODY_Y0 = 5, 28
BODY_W,  BODY_H  = 150, 86
dashed_panel(ax, BODY_X0, BODY_Y0, BODY_W, BODY_H,
             edge=PANEL_EDGE, lw=1.4, rounding=2.5)

# left panel ~25%, right panel ~75%
LEFT_X0  = BODY_X0 + 3
LEFT_Y0  = BODY_Y0 + 4
LEFT_H   = BODY_H - 8
LEFT_W_INNER = 33

RIGHT_X0 = LEFT_X0 + LEFT_W_INNER + 4
RIGHT_Y0 = LEFT_Y0
RIGHT_W  = BODY_X0 + BODY_W - RIGHT_X0 - 3
RIGHT_H  = LEFT_H

# ---------- LEFT panel: Project Offline Setup ----------
ax.add_patch(FancyBboxPatch(
    (LEFT_X0, LEFT_Y0), LEFT_W_INNER, LEFT_H,
    boxstyle="round,pad=0.0,rounding_size=1.6",
    facecolor='#ffffff', edgecolor='#d8d8d8', linewidth=1.0, zorder=1.5
))

ax.text(LEFT_X0 + LEFT_W_INNER / 2, LEFT_Y0 + LEFT_H - 3.4,
        'Project Offline Setup',
        ha='center', va='center',
        fontsize=12.5, fontstyle='italic', fontweight='bold',
        color=TXT_DARK)
ax.text(LEFT_X0 + LEFT_W_INNER / 2, LEFT_Y0 + LEFT_H - 6.4,
        '(项目离线准备)',
        ha='center', va='center',
        fontsize=9.5, color=TXT_GREY)

# 3 cards stacked
card_w = LEFT_W_INNER - 6
card_h = 17
left_card_cx = LEFT_X0 + LEFT_W_INNER / 2
left_top    = LEFT_Y0 + LEFT_H - 13
left_card_cy = [left_top - card_h / 2,
                left_top - card_h - 3.5 - card_h / 2,
                left_top - 2 * (card_h + 3.5) - card_h / 2]

left_specs = [
    dict(fill=IO_FILL, edge=IO_EDGE, txt=IO_TXT,
         icon='doc',
         title='Project Files', sub='(项目目录)',
         tail='main.tex · refs · figs'),
    dict(fill=SK_FILL, edge=SK_EDGE, txt=SK_TXT,
         icon='graph',
         title='Skill Registry', sub='(21 ARIS skills)',
         tail='skill graph · tool index'),
    dict(fill=CPU_FILL, edge=CPU_EDGE, txt=CPU_TXT,
         icon='gear',
         title='Orchestrator', sub='(9-phase 调度器)',
         tail='phase contract · DAG'),
]


def render_icon(name, ax, cx, cy, s, color):
    fn = {
        'doc': icon_doc,
        'graph': icon_graph,
        'gear': icon_gear,
        'terminal': icon_terminal,
        'folder': icon_folder,
        'magnifier': icon_magnifier,
        'check': icon_check,
        'funnel': icon_funnel,
        'chart': icon_chart,
        'monitor': icon_monitor,
        'clock': icon_clock,
        'lightning': icon_lightning,
        'target': icon_target,
    }[name]
    fn(ax, cx, cy, s=s, color=color)


for cy, spec in zip(left_card_cy, left_specs):
    card(ax, left_card_cx, cy, card_w, card_h,
         spec['fill'], spec['edge'], lw=1.4, zorder=2, rounding=1.4)
    # icon (left side)
    icon_cx = left_card_cx - card_w / 2 + 5.0
    icon_cy = cy + 0.0
    render_icon(spec['icon'], ax, icon_cx, icon_cy, s=2.0,
                color=spec['txt'])
    # title (right of icon, top line)
    ax.text(left_card_cx + 3.5, cy + 3.2,
            spec['title'], ha='center', va='center',
            fontsize=11.2, fontweight='bold', color=spec['txt'], zorder=3)
    ax.text(left_card_cx + 3.5, cy - 0.3,
            spec['sub'], ha='center', va='center',
            fontsize=9.0, color=TXT_DARK, zorder=3)
    ax.text(left_card_cx + 3.5, cy - 4.2,
            spec['tail'], ha='center', va='center',
            fontsize=7.8, color=TXT_GREY, fontstyle='italic', zorder=3)

# arrows between left cards
for i in range(2):
    y_top = left_card_cy[i] - card_h / 2
    y_bot = left_card_cy[i + 1] + card_h / 2
    arrow(ax, left_card_cx, y_top, left_card_cx, y_bot,
          color=ARROW_COLOR, lw=1.3, mut=11)

# panel bottom italic note
ax.text(LEFT_X0 + LEFT_W_INNER / 2, LEFT_Y0 + 3.0,
        'deployment',
        ha='center', va='center',
        fontsize=9.0, fontstyle='italic', color=TXT_GREY)
ax.text(LEFT_X0 + LEFT_W_INNER / 2, LEFT_Y0 + 0.8,
        '(orchestrator.py)',
        ha='center', va='center',
        fontsize=8.2, color=TXT_FAINT)


# ---------- RIGHT panel: On-board Runtime ----------
ax.add_patch(FancyBboxPatch(
    (RIGHT_X0, RIGHT_Y0), RIGHT_W, RIGHT_H,
    boxstyle="round,pad=0.0,rounding_size=1.6",
    facecolor='#ffffff', edgecolor='#d8d8d8', linewidth=1.0, zorder=1.5
))

ax.text(RIGHT_X0 + RIGHT_W / 2, RIGHT_Y0 + RIGHT_H - 3.4,
        'On-board Runtime',
        ha='center', va='center',
        fontsize=12.5, fontstyle='italic', fontweight='bold', color=TXT_DARK)
ax.text(RIGHT_X0 + RIGHT_W / 2, RIGHT_Y0 + RIGHT_H - 6.4,
        '(thesis-helper · v0.6.9)',
        ha='center', va='center',
        fontsize=9.5, color=TXT_GREY)

# Three sub-layers
sub_x0 = RIGHT_X0 + 3
sub_w  = RIGHT_W - 6
sub_top = RIGHT_Y0 + RIGHT_H - 9
sub_bot = RIGHT_Y0 + 3.5
sub_total_h = sub_top - sub_bot
gap = 2.5
sub_h = (sub_total_h - 2 * gap) / 3

layer_y0 = [
    sub_top - sub_h,
    sub_top - sub_h - gap - sub_h,
    sub_top - sub_h - 2 * (gap + sub_h),
]


def card_row(ax, x0, w_total, y_center, n, card_h, specs):
    inter_gap = 4.0
    card_w = (w_total - (n - 1) * inter_gap - 4) / n
    start_x = x0 + 2 + card_w / 2
    centers = []
    for i, spec in enumerate(specs):
        cx = start_x + i * (card_w + inter_gap)
        card(ax, cx, y_center, card_w, card_h,
             spec['fill'], spec['edge'], lw=1.4, zorder=3, rounding=1.3)
        # icon left
        icon_cx = cx - card_w / 2 + 4.4
        icon_cy = y_center + 0.5
        render_icon(spec['icon'], ax, icon_cx, icon_cy, s=1.7,
                    color=spec['txt'])
        # title
        ax.text(cx + 3.0, y_center + 3.0,
                spec['title'], ha='center', va='center',
                fontsize=10.5, fontweight='bold', color=spec['txt'],
                zorder=4)
        # cn sub
        ax.text(cx + 3.0, y_center - 0.1,
                spec['sub'], ha='center', va='center',
                fontsize=8.6, color=TXT_DARK, zorder=4)
        # tail
        if spec.get('tail'):
            ax.text(cx + 3.0, y_center - 3.6,
                    spec['tail'], ha='center', va='center',
                    fontsize=7.6, color=TXT_GREY, fontstyle='italic',
                    zorder=4)
        centers.append((cx, card_w))
    return centers


# --------- Layer 1 ----------
L1_y0 = layer_y0[0]
L1_y1 = L1_y0 + sub_h
dashed_panel(ax, sub_x0, L1_y0, sub_w, sub_h,
             edge='#cfcfcf', lw=1.0, rounding=1.6)

ax.text(sub_x0 + 2.2, L1_y1 - 2.5,
        'Layer 1 · Input Pre-process (CPU)',
        ha='left', va='center',
        fontsize=9.5, fontstyle='italic', fontweight='bold', color=TXT_GREY)
ax.text(sub_x0 + 2.2, L1_y1 - 5.2,
        '输入预处理',
        ha='left', va='center',
        fontsize=8.5, color=TXT_FAINT)

L1_card_h = sub_h - 11
L1_cy = L1_y0 + sub_h / 2 - 2.2
L1_specs = [
    dict(fill=IO_FILL, edge=IO_EDGE, txt=IO_TXT,
         icon='terminal',
         title='User Command', sub='(用户指令)',
         tail='/thesis-helper PATH'),
    dict(fill=CPU_FILL, edge=CPU_EDGE, txt=CPU_TXT,
         icon='folder',
         title='Project Scan', sub='(项目扫描)',
         tail='main.tex 共存解析'),
    dict(fill=CPU_FILL, edge=CPU_EDGE, txt=CPU_TXT,
         icon='magnifier',
         title='Path Resolve', sub='(路径解析)',
         tail=''),  # explicitly empty per spec
]
L1_centers = card_row(ax, sub_x0, sub_w, L1_cy, 3, L1_card_h, L1_specs)

for i in range(2):
    cxA, wA = L1_centers[i]
    cxB, wB = L1_centers[i + 1]
    arrow(ax, cxA + wA / 2, L1_cy, cxB - wB / 2, L1_cy,
          color=ARROW_COLOR, lw=1.3, mut=11)

ax.text(sub_x0 + sub_w - 2.5, L1_y0 + 1.8,
        'fan-out (3-way)',
        ha='right', va='center',
        fontsize=8.4, fontstyle='italic', color=TXT_FAINT)


# --------- Layer 2 ----------
L2_y0 = layer_y0[1]
L2_y1 = L2_y0 + sub_h
dashed_panel(ax, sub_x0, L2_y0, sub_w, sub_h,
             edge='#cfcfcf', lw=1.0, rounding=1.6)

ax.text(sub_x0 + 2.2, L2_y1 - 2.5,
        'Layer 2 · Multi-branch Processing (Skill)',
        ha='left', va='center',
        fontsize=9.5, fontstyle='italic', fontweight='bold', color=TXT_GREY)
ax.text(sub_x0 + 2.2, L2_y1 - 5.2,
        '多分支处理',
        ha='left', va='center',
        fontsize=8.5, color=TXT_FAINT)

L2_card_h = sub_h - 11
L2_cy = L2_y0 + sub_h / 2 - 2.2
L2_specs = [
    dict(fill=SK_FILL, edge=SK_EDGE, txt=SK_TXT,
         icon='check',
         title='Format Branch', sub='(格式合规)',
         tail='format-checker → word_count'),
    dict(fill=SK_FILL, edge=SK_EDGE, txt=SK_TXT,
         icon='doc',
         title='PDF / docx Gen', sub='(生成分支)',
         tail='compile-pdf → latex-to-word'),
    dict(fill=SK_FILL, edge=SK_EDGE, txt=SK_TXT,
         icon='funnel',
         title='AIGC Reduce', sub='(降痕分支)',
         tail='aigc-detect → 7-stage rewrite'),
]
L2_centers = card_row(ax, sub_x0, sub_w, L2_cy, 3, L2_card_h, L2_specs)

# fan-out arrows from L1 path-resolve (right-most) to all 3 L2 cards
src_cx = L1_centers[-1][0]
src_y  = L1_cy - L1_card_h / 2

for cx, w in L2_centers:
    arrow(ax, src_cx, src_y, cx, L2_cy + L2_card_h / 2,
          color=FANOUT_COLOR, lw=1.2, mut=10)

ax.text(sub_x0 + sub_w - 2.5, L2_y0 + 1.8,
        'fan-in',
        ha='right', va='center',
        fontsize=8.4, fontstyle='italic', color=TXT_FAINT)


# --------- Layer 3 ----------
L3_y0 = layer_y0[2]
L3_y1 = L3_y0 + sub_h
dashed_panel(ax, sub_x0, L3_y0, sub_w, sub_h,
             edge='#cfcfcf', lw=1.0, rounding=1.6)

ax.text(sub_x0 + 2.2, L3_y1 - 2.5,
        'Layer 3 · Fusion & Delivery (CPU)',
        ha='left', va='center',
        fontsize=9.5, fontstyle='italic', fontweight='bold', color=TXT_GREY)
ax.text(sub_x0 + 2.2, L3_y1 - 5.2,
        '融合与交付',
        ha='left', va='center',
        fontsize=8.5, color=TXT_FAINT)

L3_card_h = sub_h - 11
L3_cy = L3_y0 + sub_h / 2 - 2.2
L3_specs = [
    dict(fill=CPU_FILL, edge=CPU_EDGE, txt=CPU_TXT,
         icon='funnel',
         title='Pipeline Aggregator', sub='(流水汇总)',
         tail='orchestrator.py'),
    dict(fill=CPU_FILL, edge=CPU_EDGE, txt=CPU_TXT,
         icon='chart',
         title='Verification', sub='(验证报告)',
         tail='verification.md'),
    dict(fill=IO_FILL, edge=IO_EDGE, txt=IO_TXT,
         icon='monitor',
         title='Deliverables', sub='(最终交付物)',
         tail='PDF · docx · _aigc.tex'),
]
L3_centers = card_row(ax, sub_x0, sub_w, L3_cy, 3, L3_card_h, L3_specs)

# fan-in arrows from L2 -> L3 first card
dst_cx, dst_w = L3_centers[0]
dst_y = L3_cy + L3_card_h / 2
for cx, w in L2_centers:
    arrow(ax, cx, L2_cy - L2_card_h / 2, dst_cx, dst_y,
          color=FANIN_COLOR, lw=1.2, mut=10)

# horizontal arrows in layer 3
for i in range(2):
    cxA, wA = L3_centers[i]
    cxB, wB = L3_centers[i + 1]
    arrow(ax, cxA + wA / 2, L3_cy, cxB - wB / 2, L3_cy,
          color=ARROW_COLOR, lw=1.3, mut=11)


# =============================================================
# 3. BOTTOM KPI cards
# =============================================================
KPI_Y0 = 4
KPI_H  = 19
KPI_TOTAL_W = 150
KPI_X0 = 5
KPI_GAP = 4
KPI_W = (KPI_TOTAL_W - 2 * KPI_GAP) / 3

kpis = [
    dict(icon='clock',
         title='End-to-End Phase', value='9 / 9',
         note='真接通 · 全 phase 钉死'),
    dict(icon='lightning',
         title='ARIS Skill Registry', value='21 / 21',
         note='已就位 · skill+tool 全可控'),
    dict(icon='target',
         title='Pipeline Version', value='v 0.6.9',
         note='不可裁剪契约 · 可回滚'),
]

for i, k in enumerate(kpis):
    x = KPI_X0 + i * (KPI_W + KPI_GAP)
    cx = x + KPI_W / 2
    cy = KPI_Y0 + KPI_H / 2
    card(ax, cx, cy, KPI_W, KPI_H, KPI_FILL, KPI_EDGE,
         lw=1.4, zorder=2, rounding=1.6)
    # icon left (drawn primitive)
    icon_cx = x + 8.0
    icon_cy = cy
    render_icon(k['icon'], ax, icon_cx, icon_cy, s=3.0, color=TXT_DARK)
    # title
    ax.text(x + 16, cy + 4.6,
            k['title'], ha='left', va='center',
            fontsize=11.2, fontweight='bold', color=TXT_DARK, zorder=4)
    # value
    ax.text(x + 16, cy + 0.0,
            k['value'], ha='left', va='center',
            fontsize=17, fontweight='bold', color=TXT_DARK, zorder=4)
    # note
    ax.text(x + 16, cy - 4.8,
            k['note'], ha='left', va='center',
            fontsize=8.8, fontstyle='italic', color=TXT_GREY, zorder=4)


# =============================================================
# 4. Save
# =============================================================
out_png = r"D:/code/radar_target_recognition/test_skill_git/diagrams/variant-E-clean.png"
# DPI 360 gives ~4500x3700 — bigger and visually crisp; PNG well over 1 MB.
plt.savefig(out_png, dpi=520, bbox_inches='tight',
            facecolor=fig.get_facecolor(), pad_inches=0.2)
print(f"Saved -> {out_png}")
