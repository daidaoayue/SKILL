# -*- coding: utf-8 -*-
"""
Quiet Cartography — thesis-helper architecture poster.
Renders a 16:9 PNG suitable for slide use.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch, Circle
from matplotlib.font_manager import FontProperties
import matplotlib.lines as mlines

# ---- font loading ---------------------------------------------------------
FONT_DIR = r"C:\Users\带刀阿越\.claude\plugins\cache\anthropic-agent-skills\document-skills\98669c11ca63\skills\canvas-design\canvas-fonts"
WIN_FONT = r"C:\Windows\Fonts"

def fp(path, size):
    return FontProperties(fname=path, size=size)

def spaced(s, n=1):
    """Fake letter-spacing by inserting spaces between glyphs."""
    sep = " " * n
    return sep.join(list(s))

# Latin engineering / mono
F_MONO       = os.path.join(FONT_DIR, "GeistMono-Regular.ttf")
F_MONO_BOLD  = os.path.join(FONT_DIR, "GeistMono-Bold.ttf")
F_JBMONO     = os.path.join(FONT_DIR, "JetBrainsMono-Regular.ttf")
F_JBMONO_B   = os.path.join(FONT_DIR, "JetBrainsMono-Bold.ttf")
F_INSTSERIF  = os.path.join(FONT_DIR, "InstrumentSerif-Regular.ttf")
F_INSTSERIF_I= os.path.join(FONT_DIR, "InstrumentSerif-Italic.ttf")
F_INSTSANS   = os.path.join(FONT_DIR, "InstrumentSans-Regular.ttf")
F_INSTSANS_B = os.path.join(FONT_DIR, "InstrumentSans-Bold.ttf")
# Chinese
F_CN         = os.path.join(WIN_FONT, "msyh.ttc")
F_CN_BOLD    = os.path.join(WIN_FONT, "msyhbd.ttc")

# ---- palette: Quiet Cartography ------------------------------------------
INK    = "#0E1A2B"   # deep ink-navy (structure, primary text)
GRAPH  = "#3F4A5B"   # warm graphite (secondary)
MUTE   = "#8C95A4"   # muted slate (tertiary lines)
HAIR   = "#D7DAE0"   # hairline rule
PAPER  = "#F4F1EA"   # paper cream ground
PAPER2 = "#ECE7DC"   # subtle band
EMBER  = "#C2562B"   # accent — reserved for deliverables
EMBER2 = "#7A2E14"   # accent dark
RIBBON = "#1A2638"   # darker bottom ribbon

# ---- canvas ---------------------------------------------------------------
W, H = 19.2, 10.8   # 16:9 in inches
fig = plt.figure(figsize=(W, H), dpi=200, facecolor=PAPER)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 56.25)   # keep 16:9 ratio
ax.set_axis_off()

# paper ground
ax.add_patch(Rectangle((0, 0), 100, 56.25, facecolor=PAPER, zorder=0))

# faint grid notation marks at edges (cartographer ticks)
for x in range(5, 100, 5):
    ax.plot([x, x], [55.6, 55.85], lw=0.4, color=MUTE, alpha=0.5, zorder=1)
    ax.plot([x, x], [0.4, 0.65], lw=0.4, color=MUTE, alpha=0.5, zorder=1)
for y in range(5, 56, 5):
    ax.plot([0.4, 0.65], [y, y], lw=0.4, color=MUTE, alpha=0.5, zorder=1)
    ax.plot([99.35, 99.6], [y, y], lw=0.4, color=MUTE, alpha=0.5, zorder=1)

# corner survey marks
for (cx, cy) in [(2.2, 53.8), (97.8, 53.8), (2.2, 2.2), (97.8, 2.2)]:
    ax.add_patch(Circle((cx, cy), 0.35, facecolor="none", edgecolor=GRAPH, lw=0.6, zorder=2))
    ax.plot([cx-0.6, cx+0.6], [cy, cy], lw=0.4, color=GRAPH, zorder=2)
    ax.plot([cx, cx], [cy-0.6, cy+0.6], lw=0.4, color=GRAPH, zorder=2)

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
# top folio strip
ax.text(2.4, 54.2, "PLATE  I", fontproperties=fp(F_MONO, 8), color=GRAPH, va="center")
ax.text(50, 54.2, "—  THESIS-HELPER  ARCHITECTURE  —",
        fontproperties=fp(F_INSTSANS, 8), color=GRAPH, ha="center", va="center")
ax.text(97.6, 54.2, "WORKFLOW · v.A", fontproperties=fp(F_MONO, 8),
        color=GRAPH, ha="right", va="center")
ax.plot([2.4, 97.6], [53.55, 53.55], lw=0.6, color=GRAPH, zorder=2)

# title (Latin)
ax.text(50, 50.6, "thesis-helper",
        fontproperties=fp(F_INSTSERIF_I, 56), color=INK, ha="center", va="center")
# subtitle (Chinese)
ax.text(50, 46.6, "学生论文写作  ·  一站式工作流",
        fontproperties=fp(F_CN, 17), color=GRAPH, ha="center", va="center")

# tagline
ax.text(50, 44.0,
        "A  SINGLE  COMMAND  ·  NINE  DETERMINISTIC  PHASES  ·  TWENTY-ONE  INTERACTIVE  SKILLS",
        fontproperties=fp(F_INSTSANS, 7.2), color=MUTE, ha="center", va="center")

# ---------------------------------------------------------------------------
# L1 — USER ENTRY
# ---------------------------------------------------------------------------
# row label
ax.text(3.0, 41.4, "L1", fontproperties=fp(F_MONO_BOLD, 9), color=EMBER, va="center")
ax.text(6.0, 41.4, spaced("USER ENTRY", 1), fontproperties=fp(F_INSTSANS_B, 8), color=INK, va="center")
ax.text(15.5, 41.4, "用户入口", fontproperties=fp(F_CN, 7.5), color=GRAPH, va="center")
ax.plot([3.0, 97.0], [40.5, 40.5], lw=0.4, color=HAIR, zorder=2)

# command pill — single, centered, calm
cmd = "/thesis-helper  D:\\my-research-project  --type undergrad-thesis"
pill_y = 38.0
ax.add_patch(FancyBboxPatch((20, pill_y - 1.6), 60, 3.2,
                            boxstyle="round,pad=0.0,rounding_size=0.6",
                            facecolor=PAPER2, edgecolor=INK, lw=0.9, zorder=3))
# little prompt glyph
ax.text(22.0, pill_y, "$", fontproperties=fp(F_MONO_BOLD, 12), color=EMBER, va="center")
ax.text(24.5, pill_y, cmd, fontproperties=fp(F_JBMONO, 11.5), color=INK, va="center")

# downward axis (single thin spine)
SPINE_X = 50.0
ax.plot([SPINE_X, SPINE_X], [36.0, 34.6], lw=0.7, color=GRAPH, zorder=2)
# arrowhead
ax.add_patch(mpatches.FancyArrow(SPINE_X, 34.6, 0, -0.4,
                                 width=0.0, head_width=0.7, head_length=0.5,
                                 length_includes_head=True, color=GRAPH, zorder=2))

# ---------------------------------------------------------------------------
# L2 — MAIN PIPELINE (9 phases)
# ---------------------------------------------------------------------------
# row label
L2_TOP = 33.4
ax.text(3.0, L2_TOP, "L2", fontproperties=fp(F_MONO_BOLD, 9), color=EMBER, va="center")
ax.text(6.0, L2_TOP, spaced("MAIN PIPELINE", 1), fontproperties=fp(F_INSTSANS_B, 8), color=INK, va="center")
ax.text(20.0, L2_TOP, "主链路 · 确定性 Python", fontproperties=fp(F_CN, 7.5), color=GRAPH, va="center")
# right-aligned status
ax.text(97.0, L2_TOP, "9 / 9   PASSED", fontproperties=fp(F_MONO_BOLD, 8), color=INK, va="center", ha="right")
ax.add_patch(Circle((90.4, L2_TOP), 0.4, facecolor=EMBER, edgecolor="none", zorder=3))
ax.plot([3.0, 97.0], [L2_TOP - 0.9, L2_TOP - 0.9], lw=0.4, color=HAIR, zorder=2)

# phase data
phases = [
    ("0",   "project-scanner",      "扫描工程",      False),
    ("1",   "format-checker",       "格式 · 字数",   False),
    ("1.5", "bilingual-abstract",   "中英摘要",      False),
    ("2",   "compile-pdf",          "thesis_FINAL.pdf",          True),   # deliverable
    ("3",   "latex-to-word",        "thesis_FOR_CNKI_CHECK.docx",True),   # deliverable
    ("4",   "aigc-detect",          "AIGC 检测",     False),
    ("5",   "aigc-reduce",          "7-stage 降痕",  False),
    ("6",   "thesis-defense-prep",  "答辩准备",      False),
    ("7",   "thesis-blind-review",  "盲审 · 硕士",   False),
]
# Phase 8 (verification report) sits as the closure on the spine — we render it
# as the implicit hand-off to the deliverable ribbon below.

# layout: a single horizontal track
TRACK_Y    = 26.0
TRACK_LEFT = 5.0
TRACK_RIGHT= 95.0
N = len(phases)
# the track baseline (the "stave")
ax.plot([TRACK_LEFT, TRACK_RIGHT], [TRACK_Y, TRACK_Y], lw=0.6, color=GRAPH, zorder=2)

# evenly spaced anchor points
xs = [TRACK_LEFT + (TRACK_RIGHT - TRACK_LEFT) * (i + 0.5) / N for i in range(N)]

# tick marks at each phase
for x in xs:
    ax.plot([x, x], [TRACK_Y - 0.45, TRACK_Y + 0.45], lw=0.6, color=GRAPH, zorder=3)

# direction arrow at the right end
ax.add_patch(mpatches.FancyArrow(TRACK_RIGHT, TRACK_Y, 0.6, 0,
                                 width=0.0, head_width=0.7, head_length=0.6,
                                 length_includes_head=True, color=GRAPH, zorder=3))

# small "PHASE" label at the start
ax.text(TRACK_LEFT - 0.4, TRACK_Y, "PHASE", fontproperties=fp(F_MONO, 6.2),
        color=MUTE, va="center", ha="right")

# render each phase: number above the track, name + cn below
for (num, name, cn, deliv), x in zip(phases, xs):
    # phase number (large, above)
    num_color = EMBER if deliv else INK
    ax.text(x, TRACK_Y + 4.7, num,
            fontproperties=fp(F_INSTSERIF, 22 if not deliv else 26),
            color=num_color, ha="center", va="center")
    # tiny "0 / 1 / ..." caption
    ax.text(x, TRACK_Y + 7.6, f"P{num}", fontproperties=fp(F_MONO, 6),
            color=MUTE, ha="center", va="center")
    # connector from number down to track
    ax.plot([x, x], [TRACK_Y + 2.6, TRACK_Y + 0.5], lw=0.4, color=MUTE, zorder=2)

    # star marker for deliverables (above number)
    if deliv:
        # small filled diamond as the mark of consequence
        d = 0.55
        ax.add_patch(mpatches.Polygon(
            [[x, TRACK_Y + 9.2], [x + d, TRACK_Y + 8.6],
             [x, TRACK_Y + 8.0], [x - d, TRACK_Y + 8.6]],
            closed=True, facecolor=EMBER, edgecolor="none", zorder=4))

    # name (mono, below the track)
    name_size = 7.5 if not deliv else 8.0
    name_color = EMBER2 if deliv else INK
    ax.text(x, TRACK_Y - 1.6, name,
            fontproperties=fp(F_JBMONO_B if deliv else F_JBMONO, name_size),
            color=name_color, ha="center", va="center")
    # chinese caption
    cn_color = EMBER2 if deliv else GRAPH
    ax.text(x, TRACK_Y - 3.2, cn,
            fontproperties=fp(F_CN, 6.6 if deliv else 6.4),
            color=cn_color, ha="center", va="center")

# small footer caption under the track — diamond drawn as vector
_dx, _dy, _ds = TRACK_LEFT + 0.35, TRACK_Y - 5.4, 0.36
ax.add_patch(mpatches.Polygon(
    [[_dx, _dy + _ds], [_dx + _ds, _dy], [_dx, _dy - _ds], [_dx - _ds, _dy]],
    closed=True, facecolor=EMBER, edgecolor="none", zorder=4))
ax.text(TRACK_LEFT + 1.4, TRACK_Y - 5.4,
        "marks artefacts that leave the system",
        fontproperties=fp(F_INSTSERIF_I, 8), color=GRAPH, va="center")
ax.text(TRACK_RIGHT, TRACK_Y - 5.4,
        "Phase 8  /  verification_report.md",
        fontproperties=fp(F_JBMONO, 7.2), color=GRAPH, va="center", ha="right")

# spine continues downward
ax.plot([SPINE_X, SPINE_X], [TRACK_Y - 6.4, TRACK_Y - 7.6], lw=0.7, color=GRAPH, zorder=2)
ax.add_patch(mpatches.FancyArrow(SPINE_X, TRACK_Y - 7.6, 0, -0.4,
                                 width=0.0, head_width=0.7, head_length=0.5,
                                 length_includes_head=True, color=GRAPH, zorder=2))

# ---------------------------------------------------------------------------
# L3 — INTERACTIVE LAYER (21 ARIS skills · 6 families)
# ---------------------------------------------------------------------------
L3_TOP = 18.0
ax.text(3.0, L3_TOP, "L3", fontproperties=fp(F_MONO_BOLD, 9), color=EMBER, va="center")
ax.text(6.0, L3_TOP, spaced("INTERACTIVE SKILLS", 1), fontproperties=fp(F_INSTSANS_B, 8), color=INK, va="center")
ax.text(24.0, L3_TOP, "互动层 · 21 个 ARIS 技能 · 6 类场景",
        fontproperties=fp(F_CN, 7.5), color=GRAPH, va="center")
ax.text(97.0, L3_TOP, "21  CALLABLE", fontproperties=fp(F_MONO_BOLD, 8), color=INK, va="center", ha="right")
ax.plot([3.0, 97.0], [L3_TOP - 0.9, L3_TOP - 0.9], lw=0.4, color=HAIR, zorder=2)

families = [
    ("01", "FIND  LITERATURE",  "找文献",
     ["research-lit", "arxiv", "semantic-scholar"]),
    ("02", "VERIFY  NOVELTY",   "验新颖",
     ["novelty-check", "claude-paper:study"]),
    ("03", "WRITE  THEORY",     "写理论",
     ["proof-writer", "formula-derivation"]),
    ("04", "MAKE  FIGURES",     "出图表",
     ["mermaid-diagram", "matplotlib-tvhahn", "paper-illustration"]),
    ("05", "DESIGN  EXPERIMENT","设计实验",
     ["ablation-planner", "result-to-claim"]),
    ("06", "POST-SUBMISSION",   "投稿后",
     ["rebuttal", "paper-reviewer", "paper-slides", "paper-poster"]),
]

# six columns, evenly spaced
COL_LEFT  = 5.0
COL_RIGHT = 95.0
M = len(families)
col_w = (COL_RIGHT - COL_LEFT) / M
fam_y_top = L3_TOP - 2.6

for i, (idx, label, cn, items) in enumerate(families):
    cx = COL_LEFT + col_w * (i + 0.5)
    # vertical hairline separating columns (except after the last)
    if i < M - 1:
        sep_x = COL_LEFT + col_w * (i + 1)
        ax.plot([sep_x, sep_x], [fam_y_top - 0.4, 7.2],
                lw=0.35, color=HAIR, zorder=2)
    # family number
    ax.text(cx, fam_y_top, idx,
            fontproperties=fp(F_MONO, 7), color=EMBER, ha="center", va="center")
    # latin label
    ax.text(cx, fam_y_top - 1.5, label,
            fontproperties=fp(F_INSTSANS_B, 7.2), color=INK,
            ha="center", va="center")
    # chinese
    ax.text(cx, fam_y_top - 3.0, cn,
            fontproperties=fp(F_CN, 7.8), color=GRAPH, ha="center", va="center")
    # divider
    ax.plot([cx - 3.5, cx + 3.5], [fam_y_top - 4.0, fam_y_top - 4.0],
            lw=0.4, color=MUTE, zorder=2)
    # skill items, listed
    for j, item in enumerate(items):
        y = fam_y_top - 5.0 - j * 1.25
        ax.text(cx, y, item,
                fontproperties=fp(F_JBMONO, 6.8), color=INK,
                ha="center", va="center")

# ---------------------------------------------------------------------------
# DELIVERABLE RIBBON (bottom)
# ---------------------------------------------------------------------------
RIB_Y = 2.8
RIB_H = 3.4
ax.add_patch(Rectangle((0, RIB_Y - 0.3), 100, RIB_H + 0.6,
                       facecolor=RIBBON, edgecolor="none", zorder=3))
# subtle ember underline
ax.add_patch(Rectangle((0, RIB_Y - 0.3), 100, 0.18,
                       facecolor=EMBER, edgecolor="none", zorder=4))

# label
ax.text(3.0, RIB_Y + RIB_H/2 + 0.2, spaced("DELIVERABLES", 1),
        fontproperties=fp(F_INSTSANS_B, 7.5), color=PAPER, va="center")
ax.text(3.0, RIB_Y + RIB_H/2 - 1.1, "最终交付物",
        fontproperties=fp(F_CN, 6.5), color="#9FA8B8", va="center")

# Each entry: (latin_name, optional_cn_inline_suffix, cn_caption)
# When latin_name contains CJK it must be rendered in YaHei, so we keep them split.
deliverables = [
    {"lat": "thesis_FINAL.pdf",           "cn_inline": "",       "cap": "答辩用主稿"},
    {"lat": "thesis_FOR_CNKI_CHECK.docx", "cn_inline": "",       "cap": "知网查重版"},
    {"lat": "rewrite_aigc",               "cn_inline": "AIGC 改写版", "cap": "降痕保留原文"},
    {"lat": "defense_qa.md",              "cn_inline": "答辩 Q&A",   "cap": "Defense ready"},
    {"lat": "verification_report.md",     "cn_inline": "",       "cap": "全流程留痕"},
]

# evenly distribute deliverables in the ribbon
RIB_LEFT  = 18.0
RIB_RIGHT = 98.0
K = len(deliverables)
slot_w = (RIB_RIGHT - RIB_LEFT) / K
for i, d in enumerate(deliverables):
    slot_left = RIB_LEFT + slot_w * i
    text_x = slot_left + 1.6
    # diamond marker — pinned to the slot's left edge
    dm = 0.32
    mx, my = slot_left + 0.7, RIB_Y + RIB_H/2
    ax.add_patch(mpatches.Polygon(
        [[mx, my + dm], [mx + dm, my], [mx, my - dm], [mx - dm, my]],
        closed=True, facecolor=EMBER, edgecolor="none", zorder=5))

    # main latin name (top line)
    ax.text(text_x, my + 0.35, d["lat"],
            fontproperties=fp(F_JBMONO_B, 6.6), color=PAPER, va="center")
    # optional inline CN tag rendered in YaHei, after measuring latin width approx
    if d["cn_inline"]:
        # rough offset: monospace ~ 0.46 unit per char at size 6.6
        offset = len(d["lat"]) * 0.46 + 0.6
        ax.text(text_x + offset, my + 0.35, d["cn_inline"],
                fontproperties=fp(F_CN, 6.6), color=PAPER, va="center")
    # caption (CN)
    ax.text(text_x, my - 1.1, d["cap"],
            fontproperties=fp(F_CN, 6.0), color="#B8C0CE", va="center")

# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
ax.text(2.4, 1.2, "QUIET  CARTOGRAPHY  ·  PLATE  I  ·  thesis-helper",
        fontproperties=fp(F_MONO, 6.5), color=GRAPH, va="center")
ax.text(97.6, 1.2, "16 : 9  ·  POSTER  EDITION",
        fontproperties=fp(F_MONO, 6.5), color=GRAPH, va="center", ha="right")

# ---- save -----------------------------------------------------------------
OUT = r"D:/code/radar_target_recognition/test_skill_git/diagrams/variant-A-canvas.png"
fig.savefig(OUT, dpi=200, facecolor=PAPER, bbox_inches=None, pad_inches=0)
print(f"WROTE: {OUT}")
print(f"SIZE_BYTES: {os.path.getsize(OUT)}")
