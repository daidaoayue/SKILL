#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thesis-helper 工作流架构图 v2 — academic figure style.

设计原则:
  * 学术 paper figure 风格（黑白灰为主, 极少强调色）
  * 单方向自顶向下纵向流程, 砍掉 Z 字形
  * 16:9 横版, 左侧主链路, 右侧 ARIS skill 网格
  * Times New Roman + 中文 SimSun/YaHei
  * 严谨 1.0 px 描边, 无阴影无 emoji 装饰

参考: ResNet (He et al., 2016) / Transformer (Vaswani et al., 2017) /
      ViT (Dosovitskiy et al., 2021) 的 architecture diagram 排版.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

# ---------------------------------------------------------------------------
# Typography & global style — academic figure look
# ---------------------------------------------------------------------------
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.serif'] = ['Times New Roman', 'Times', 'DejaVu Serif']
# 中文回退栈：宋体优先（论文标准），其次微软雅黑
mpl.rcParams['font.sans-serif'] = ['SimSun', 'Microsoft YaHei', 'SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams['axes.linewidth'] = 0.8
mpl.rcParams['mathtext.fontset'] = 'stix'

# Greyscale-first palette + ONE accent (deliverable / verification highlight)
INK = '#1a1a1a'           # primary text / strokes
GREY_DARK = '#4a4a4a'     # secondary text
GREY_MID = '#7a7a7a'      # arrows / minor strokes
GREY_LINE = '#b8b8b8'     # box borders, grid
GREY_FILL = '#f4f4f4'     # neutral phase fill
GREY_BAND = '#fafafa'     # panel background
GREY_BAND_EDGE = '#d4d4d4'
WHITE = '#ffffff'

ACCENT = '#1f3a5f'        # deep navy — single accent for key deliverables
ACCENT_FILL = '#e8eef5'   # light tint of accent
ACCENT_LINE = '#2c5282'

# ---------------------------------------------------------------------------
# Figure setup — 16:9
# ---------------------------------------------------------------------------
FIG_W, FIG_H = 16.0, 9.0
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=220)
ax.set_xlim(0, 160)
ax.set_ylim(0, 90)
ax.set_aspect('equal')
ax.axis('off')

# subtle bounding frame (academic figures often have a thin box)
fig.patch.set_facecolor('white')


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
def panel(x: float, y: float, w: float, h: float, title: str | None = None) -> None:
    """Draw a thin-bordered panel section, optionally with a small italic title tab."""
    rect = Rectangle(
        (x, y), w, h,
        facecolor=GREY_BAND, edgecolor=GREY_BAND_EDGE,
        linewidth=0.8, zorder=1,
    )
    ax.add_patch(rect)
    if title:
        # title tab — small, top-left
        ax.text(
            x + 0.8, y + h - 1.4, title,
            ha='left', va='top',
            fontsize=8.5, fontstyle='italic', color=GREY_DARK,
            zorder=3,
        )


def phase_box(
    cx: float, cy: float, w: float, h: float,
    head: str, body: str,
    *, accent: bool = False, milestone: bool = False,
) -> None:
    """Draw a phase node centred at (cx, cy)."""
    x, y = cx - w / 2, cy - h / 2
    if accent:
        face, edge, text_color, head_color = ACCENT_FILL, ACCENT_LINE, INK, ACCENT
        lw = 1.2
    else:
        face, edge, text_color, head_color = WHITE, GREY_LINE, INK, GREY_DARK
        lw = 0.9

    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.10,rounding_size=0.5",
        facecolor=face, edgecolor=edge, linewidth=lw, zorder=4,
    )
    ax.add_patch(box)

    # Optional milestone tick on the left edge
    if milestone:
        ax.add_patch(Rectangle(
            (x, y), 0.5, h,
            facecolor=ACCENT, edgecolor='none', zorder=5,
        ))

    # Header line — phase id (English serif look)
    ax.text(
        cx, cy + h / 2 - 1.05, head,
        ha='center', va='center',
        fontsize=8.5, fontweight='bold', color=head_color, zorder=6,
    )
    # Body line — Chinese description (sans, smaller)
    ax.text(
        cx, cy - h / 2 + 0.95, body,
        ha='center', va='center',
        fontsize=7.6, color=text_color,
        family='sans-serif', zorder=6,
    )


def vertical_arrow(cx: float, y_top: float, y_bot: float, *, label: str | None = None) -> None:
    """Vertical down arrow on the spine."""
    arrow = FancyArrowPatch(
        (cx, y_top), (cx, y_bot),
        arrowstyle='-|>', mutation_scale=10,
        linewidth=0.9, color=GREY_MID, zorder=3,
    )
    ax.add_patch(arrow)
    if label:
        ax.text(
            cx + 0.6, (y_top + y_bot) / 2, label,
            ha='left', va='center', fontsize=7.0,
            color=GREY_DARK, fontstyle='italic', zorder=3,
        )


def aris_card(
    x: float, y: float, w: float, h: float,
    code: str, title_cn: str, skills: list[str],
) -> None:
    """An ARIS skill-category card on the right grid."""
    box = Rectangle(
        (x, y), w, h,
        facecolor=WHITE, edgecolor=GREY_LINE, linewidth=0.9, zorder=4,
    )
    ax.add_patch(box)

    # Code stripe at top
    ax.text(
        x + 0.6, y + h - 0.9, code,
        ha='left', va='top',
        fontsize=7.5, fontweight='bold', color=ACCENT,
        family='serif', zorder=5,
    )
    # Title (Chinese)
    ax.text(
        x + w - 0.6, y + h - 0.9, title_cn,
        ha='right', va='top',
        fontsize=7.8, fontweight='bold', color=INK,
        family='sans-serif', zorder=5,
    )
    # Hairline under header
    ax.add_line(Line2D(
        [x + 0.4, x + w - 0.4], [y + h - 1.9, y + h - 1.9],
        color=GREY_LINE, linewidth=0.5, zorder=5,
    ))
    # Skill list (monospace-ish via serif italic)
    for i, sk in enumerate(skills):
        ax.text(
            x + 0.7, y + h - 2.7 - i * 0.95, sk,
            ha='left', va='top',
            fontsize=6.8, color=GREY_DARK,
            family='serif', zorder=5,
        )


# ---------------------------------------------------------------------------
# Title block (top)
# ---------------------------------------------------------------------------
ax.text(
    80, 86.5,
    'thesis-helper: An End-to-End Workflow for Undergraduate / Graduate Thesis Writing',
    ha='center', va='center',
    fontsize=14, fontweight='bold', color=INK, family='serif',
)
ax.text(
    80, 84.0,
    r'v0.6.4  $\cdot$  9-phase deterministic orchestrator  $\cdot$  21 ARIS interactive skills  $\cdot$  non-skippable contract',
    ha='center', va='center',
    fontsize=9.5, color=GREY_DARK, fontstyle='italic', family='serif',
)
# Hairline rule under the title
ax.add_line(Line2D([8, 152], [82.5, 82.5], color=GREY_LINE, linewidth=0.6))

# ---------------------------------------------------------------------------
# LEFT COLUMN — vertical pipeline (L1 entry + L2 9-phase main chain)
# ---------------------------------------------------------------------------
LEFT_X0, LEFT_W = 4, 78
PANEL_TOP = 80.0
PANEL_BOT = 6.5
panel(LEFT_X0, PANEL_BOT, LEFT_W, PANEL_TOP - PANEL_BOT, title=None)

# Banner at top of LEFT panel (parallel to L3 banner on the right)
ax.text(
    LEFT_X0 + LEFT_W / 2, 76.8,
    'L1 / L2  Deterministic Pipeline',
    ha='center', va='center',
    fontsize=10.5, fontweight='bold', color=INK, family='serif',
)
ax.text(
    LEFT_X0 + LEFT_W / 2, 74.9,
    'orchestrator.py · 9 phase 顺序执行 · TodoWrite 钉死步骤 · 真已 9/9 通',
    ha='center', va='center',
    fontsize=8.0, color=GREY_DARK, fontstyle='italic', family='sans-serif',
)
ax.add_line(Line2D(
    [LEFT_X0 + 2, LEFT_X0 + LEFT_W - 2], [73.7, 73.7],
    color=GREY_LINE, linewidth=0.5,
))

SPINE_X = LEFT_X0 + LEFT_W / 2  # 43

# ---- L1: User entry contract -----------------------------------------------
# User invocation
USER_Y = 71.5
phase_box(
    SPINE_X, USER_Y, 64, 3.4,
    'User Invocation',
    '/thesis-helper  D:\\my-research-project  --type undergrad-thesis',
)
vertical_arrow(SPINE_X, USER_Y - 1.7, USER_Y - 3.4)

# L1 entry contract — three side-by-side small chips on a single row
L1_Y = 65.0
L1_H = 4.2
chip_w = 20
gap = 1.5
total = chip_w * 3 + gap * 2
x0 = SPINE_X - total / 2
for i, (head, body) in enumerate([
    ('I.  Pinned TODO', 'TodoWrite 列全步骤'),
    ('II.  No-skip', '仅 --skip 显式声明'),
    ('III.  Verify Report', 'verification_report.md'),
]):
    cx = x0 + chip_w / 2 + i * (chip_w + gap)
    phase_box(cx, L1_Y, chip_w, L1_H, head, body)

vertical_arrow(SPINE_X, L1_Y - L1_H / 2, L1_Y - L1_H / 2 - 1.7)

# ---- L2: 9-phase main chain (vertical) -------------------------------------
# Phase definitions: (head, body, accent?, milestone?)
phases = [
    ('Phase 0-A / 0-B   project-scanner',  '读取 config 与扫描资产',           False, False),
    ('Phase 1   format-checker',           '8 项格式检查（含母语字数）',        False, False),
    ('Phase 1.5   bilingual-abstract',     '中英摘要平行生成',                  False, False),
    ('Phase 2   compile-pdf',              'thesis_FINAL.pdf（关键交付）',      True,  True),
    ('Phase 3   latex-to-word',            'FOR_CNKI_CHECK.docx（关键交付）',   True,  True),
    ('Phase 4   aigc-detect',              '7 章 AIGC 扫描',                    False, False),
    ('Phase 5   aigc-reduce  (7-stage)',   '改写至 _aigc 后缀，不动原文',        False, False),
    ('Phase 6   thesis-defense-prep',      '答辩 Q&A 与陈述脚本',                False, False),
    ('Phase 7   thesis-blind-review',      '匿名版生成 + 评审报告（硕士必做）',  False, False),
    ('Phase 8   verification_report.md',   '真数字闭环验证（关键交付）',         True,  True),
]

# Vertical layout for the 10 boxes between top and bottom of L2 region
n = len(phases)
y_top = 60.0
y_bot = 9.0
box_w = 64
box_h = 3.6
spacing = (y_top - y_bot) / (n - 1) if n > 1 else 0

centers = [y_top - i * spacing for i in range(n)]
for (head, body, accent, milestone), cy in zip(phases, centers):
    phase_box(SPINE_X, cy, box_w, box_h, head, body,
              accent=accent, milestone=milestone)

# Connecting arrows between consecutive phases
for cy_from, cy_to in zip(centers[:-1], centers[1:]):
    y_a = cy_from - box_h / 2
    y_b = cy_to + box_h / 2
    vertical_arrow(SPINE_X, y_a, y_b)

# Milestone legend — placed top-right corner of the LEFT panel
LEG_X = LEFT_X0 + LEFT_W - 22.5
LEG_Y = 78.7
ax.add_patch(Rectangle((LEG_X, LEG_Y - 0.6), 0.5, 1.4,
                       facecolor=ACCENT, edgecolor='none', zorder=5))
ax.text(
    LEG_X + 0.9, LEG_Y + 0.1,
    'navy bar = key deliverable / milestone',
    ha='left', va='center', fontsize=7.0,
    color=GREY_DARK, fontstyle='italic', family='serif',
)

# ---------------------------------------------------------------------------
# RIGHT COLUMN — ARIS skill grid (6 categories x 21 skills)
# ---------------------------------------------------------------------------
RIGHT_X0, RIGHT_W = 84, 72
# Right panel uses the L3 banner as its own title (no italic tab to avoid overlap)
panel(RIGHT_X0, PANEL_BOT, RIGHT_W, PANEL_TOP - PANEL_BOT, title=None)

# Header line under the panel title
ax.text(
    RIGHT_X0 + RIGHT_W / 2, 76.8,
    'L3 Interactive Layer',
    ha='center', va='center',
    fontsize=10.5, fontweight='bold', color=INK, family='serif',
)
ax.text(
    RIGHT_X0 + RIGHT_W / 2, 74.9,
    'Claude 在对话中按需调用上游 ARIS skill（~/.claude/skills/）',
    ha='center', va='center',
    fontsize=8.0, color=GREY_DARK, fontstyle='italic', family='sans-serif',
)
ax.add_line(Line2D(
    [RIGHT_X0 + 2, RIGHT_X0 + RIGHT_W - 2], [73.7, 73.7],
    color=GREY_LINE, linewidth=0.5,
))

# 3x2 grid of ARIS category cards
cards = [
    ('A1', '文献调研',
     ['research-lit', 'arxiv', 'semantic-scholar']),
    ('A2', '新颖性核验',
     ['novelty-check', 'claude-paper:study']),
    ('A3', '理论与公式',
     ['proof-writer', 'formula-derivation']),
    ('A4', '图表绘制',
     ['mermaid-diagram', 'matplotlib-tvhahn', 'paper-illustration']),
    ('A5', '实验设计',
     ['ablation-planner', 'result-to-claim']),
    ('A6', '投稿与评审',
     ['rebuttal', 'paper-reviewer', 'paper-slides', 'paper-poster']),
]

# Grid geometry: 2 cols x 3 rows
GRID_LEFT = RIGHT_X0 + 2.0
GRID_TOP = 72.0
GRID_BOT = 36.0
COL_GAP = 1.5
ROW_GAP = 1.5
n_cols, n_rows = 2, 3
card_w = (RIGHT_W - 4.0 - COL_GAP) / n_cols
card_h = (GRID_TOP - GRID_BOT - ROW_GAP * (n_rows - 1)) / n_rows

for i, (code, title, skills) in enumerate(cards):
    row = i // n_cols
    col = i % n_cols
    cx = GRID_LEFT + col * (card_w + COL_GAP)
    cy = GRID_TOP - card_h - row * (card_h + ROW_GAP)
    aris_card(cx, cy, card_w, card_h, code, title, skills)

# Usage examples block under the grid
ex_y_top = 33.5
ax.text(
    RIGHT_X0 + RIGHT_W / 2, ex_y_top,
    'Invocation pattern: natural language  -->  Skill(  )',
    ha='center', va='center',
    fontsize=9.0, fontweight='bold', color=INK, family='serif',
)

examples = [
    ('"找一下低空雷达相关工作"',     'Skill("research-lit")'),
    ('"给软阈值写引理证明"',         'Skill("proof-writer")'),
    ('"做答辩 PPT"',                'Skill("paper-slides")'),
    ('"我这个 idea 有人做过吗"',     'Skill("novelty-check")'),
    ('"起草 rebuttal"',             'Skill("rebuttal")'),
    ('"生成系统架构图"',             'Skill("paper-illustration")'),
]
ex_x_left = RIGHT_X0 + 3.0
ex_x_arrow = RIGHT_X0 + RIGHT_W * 0.48
ex_x_right = RIGHT_X0 + RIGHT_W * 0.52
row_h = 2.4
for i, (utt, call) in enumerate(examples):
    yy = ex_y_top - 2.5 - i * row_h
    ax.text(
        ex_x_left, yy, utt,
        ha='left', va='center',
        fontsize=7.5, color=GREY_DARK, fontstyle='italic',
        family='sans-serif',
    )
    ax.text(
        ex_x_arrow, yy, '-->',
        ha='center', va='center',
        fontsize=7.5, color=GREY_MID, family='serif',
    )
    ax.text(
        ex_x_right, yy, call,
        ha='left', va='center',
        fontsize=7.5, color=ACCENT, fontweight='bold',
        family='monospace',
    )

# ---------------------------------------------------------------------------
# Bottom delivery bar (spans full width, below both panels)
# ---------------------------------------------------------------------------
deliv_y = 3.0
deliv_h = 2.6
deliv_box = FancyBboxPatch(
    (8, deliv_y - deliv_h / 2), 144, deliv_h,
    boxstyle="round,pad=0.05,rounding_size=0.4",
    facecolor=ACCENT_FILL, edgecolor=ACCENT_LINE, linewidth=1.0, zorder=4,
)
ax.add_patch(deliv_box)
ax.text(
    80, deliv_y + 0.05,
    'Final deliverables :  thesis_FINAL.pdf   |   thesis_FOR_CNKI_CHECK.docx   |   '
    'AIGC-rewritten _aigc.docx   |   defense Q&A   |   verification_report.md',
    ha='center', va='center',
    fontsize=9.2, fontweight='bold', color=INK, family='serif',
    zorder=5,
)

# Caption-style footer
ax.text(
    80, 0.6,
    'Figure 1.  thesis-helper workflow.  (a) The L1 entry contract gates the L2 deterministic '
    '9-phase orchestrator that produces all key deliverables top-down.  '
    '(b) The L3 ARIS layer exposes 21 reusable skills across six categories, '
    'invoked on-demand via natural language during interactive editing.',
    ha='center', va='center',
    fontsize=7.6, color=GREY_DARK, fontstyle='italic', family='serif',
)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
out_png = 'D:/code/radar_target_recognition/test_skill_git/diagrams/variant-C-academic.png'
out_svg = 'D:/code/radar_target_recognition/test_skill_git/diagrams/variant-C-academic.svg'
plt.savefig(out_png, dpi=220, bbox_inches='tight', facecolor='white', pad_inches=0.15)
plt.savefig(out_svg, format='svg', bbox_inches='tight', facecolor='white', pad_inches=0.15)
print(f"PNG: {out_png}")
print(f"SVG: {out_svg}")
