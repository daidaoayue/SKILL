# -*- coding: utf-8 -*-
"""
variant-D-academic-cn.py

中国学术系统架构图风格 (Chinese Academic System Architecture Diagram)
- 顶部主标题
- 中部 "研究内容一/二/三" 深海军蓝色块 + 大白箭头
- 底部输入源 -> 三色平行分支 -> 门控融合头 -> 最终输出
- 虚线 callout 标注 + 右下角性能指标
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Polygon
from matplotlib.lines import Line2D

# ---------- font config ----------
mpl.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
mpl.rcParams['font.serif']      = ['SimSun', 'Times New Roman']
mpl.rcParams['axes.unicode_minus'] = False

# ---------- palette ----------
NAVY        = '#1f3a5f'   # 研究内容主块
NAVY_DARK   = '#16294a'
NAVY_BORDER = '#3d5a80'
WHITE       = '#ffffff'
GREY_LINE   = '#5a5a5a'
GREY_TEXT   = '#666666'
GREY_BG     = '#f0f2f5'

BLUE_PASTEL   = '#b8d4e8'
BLUE_DARK     = '#4a78a0'
PURPLE_PASTEL = '#d4c5e8'
PURPLE_DARK   = '#7e5aa6'
GREEN_PASTEL  = '#c8e6c9'
GREEN_DARK    = '#3d7a3f'

ORANGE        = '#f5b041'
ORANGE_DARK   = '#b8741a'
PINK          = '#f8c4c4'
PINK_DARK     = '#c0392b'

CALLOUT_EDGE  = '#7d3c98'

# ---------- canvas ----------
fig, ax = plt.subplots(figsize=(20, 13), dpi=220)
ax.set_xlim(0, 200)
ax.set_ylim(0, 130)
ax.set_aspect('equal')
ax.axis('off')
fig.patch.set_facecolor('#fafbfc')

# =====================================================================
# 0. 主标题
# =====================================================================
ax.text(100, 124,
        'thesis-helper · 学生论文写作一站式工作流系统架构',
        ha='center', va='center',
        fontsize=24, fontweight='bold',
        color='#0a1929', family='SimHei')

ax.text(100, 119,
        'thesis-helper: An End-to-End Pipeline for Student Thesis Writing',
        ha='center', va='center',
        fontsize=12, fontstyle='italic',
        color=GREY_TEXT, family='Times New Roman')

# 主标题下分隔线
ax.add_line(Line2D([18, 182], [116, 116], color=NAVY, linewidth=1.6))
ax.add_line(Line2D([18, 182], [115.3, 115.3], color=NAVY, linewidth=0.6))

# =====================================================================
# 1. "研究内容" 三块 (顶部条带)
# =====================================================================
# 每块 60 单位宽,中心 x = 33, 100, 167
research_centers = [33, 100, 167]
research_titles  = ['研究内容一', '研究内容二', '研究内容三']
research_subs    = ['自动化项目扫描\n与配置生成',
                    '端到端确定性\n流水线编排',
                    '互动层与上游\nskill 调用']
research_diffs   = [
    '难点：多版本 main.tex 共存 + paper_root ≠ project_root 路径解析',
    '难点：9 phase 真打通、上下游数据契约、失败可恢复',
    '难点：21 ARIS skill 路由、Skill tool 触发可控',
]

block_w  = 52
block_h  = 13
outer_w  = 58
outer_h  = 25

for cx, title, sub, diff in zip(research_centers, research_titles, research_subs, research_diffs):
    # 外层白底 dashed 圆角框 (顶部到 100 区间)
    outer = FancyBboxPatch(
        (cx - outer_w/2, 90),
        outer_w, outer_h,
        boxstyle="round,pad=0.4,rounding_size=1.5",
        linewidth=1.5, edgecolor=GREY_LINE,
        facecolor='white', linestyle='--', zorder=2)
    ax.add_patch(outer)

    # 顶部白底小标题(白色背景 + 黑色加粗字)
    label_box = FancyBboxPatch(
        (cx - 14, 109),
        28, 5,
        boxstyle="round,pad=0.1,rounding_size=0.4",
        linewidth=1.2, edgecolor=NAVY,
        facecolor='white', zorder=4)
    ax.add_patch(label_box)
    ax.text(cx, 111.5, title,
            ha='center', va='center',
            fontsize=14, fontweight='bold',
            color=NAVY_DARK, family='SimHei', zorder=5)

    # 难点小灰字
    ax.text(cx, 106.3, diff,
            ha='center', va='center',
            fontsize=8, color=GREY_TEXT,
            family='SimHei', zorder=5)

    # 深海军蓝实心块
    inner = FancyBboxPatch(
        (cx - block_w/2, 92),
        block_w, block_h,
        boxstyle="round,pad=0.1,rounding_size=0.8",
        linewidth=0, facecolor=NAVY, zorder=3)
    ax.add_patch(inner)

    # 块内白字加粗
    ax.text(cx, 98.5, sub,
            ha='center', va='center',
            fontsize=12, fontweight='bold',
            color='white', family='SimHei', zorder=4,
            linespacing=1.3)

# =====================================================================
# 2. 大白色箭头 (从研究内容块向下指)
# =====================================================================
def big_white_arrow(cx, y_top, y_bot, width=8):
    """绘制大白色 5 边形向下箭头, 带深色边框"""
    half = width / 2
    head_h = (y_top - y_bot) * 0.45
    body_h = (y_top - y_bot) - head_h
    pts = [
        (cx - half*0.55, y_top),               # left top
        (cx + half*0.55, y_top),               # right top
        (cx + half*0.55, y_top - body_h),      # right body
        (cx + half,      y_top - body_h),      # right shoulder
        (cx,             y_bot),               # tip
        (cx - half,      y_top - body_h),      # left shoulder
        (cx - half*0.55, y_top - body_h),      # left body
    ]
    poly = Polygon(pts, closed=True,
                   facecolor='white',
                   edgecolor=NAVY, linewidth=1.6, zorder=6)
    ax.add_patch(poly)

for cx in research_centers:
    big_white_arrow(cx, y_top=89.5, y_bot=83, width=9)

# =====================================================================
# 3. 底部架构主体
# =====================================================================
# 整体框 (一个浅灰背景区分层次)
base_bg = FancyBboxPatch(
    (3, 5), 194, 76,
    boxstyle="round,pad=0.4,rounding_size=1.5",
    linewidth=1.0, edgecolor='#cccccc',
    facecolor='#f7f9fc', zorder=0)
ax.add_patch(base_bg)

ax.text(8, 78, '系统架构 · System Architecture',
        ha='left', va='center',
        fontsize=11, fontweight='bold',
        color=NAVY_DARK, family='SimHei', zorder=1)

# ---------- 3.1 左侧输入源 ----------
input_x  = 7
input_w  = 28

def soft_box(x, y, w, h, text, fc='#e9ecef', ec='#909090', fz=10, fw='normal',
             color='#202020', family='SimHei', linespacing=1.2, dashed=False, z=3):
    style = "round,pad=0.15,rounding_size=0.6"
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=style,
        linewidth=1.2, edgecolor=ec,
        facecolor=fc,
        linestyle='--' if dashed else '-',
        zorder=z)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2, text,
            ha='center', va='center',
            fontsize=fz, fontweight=fw,
            color=color, family=family,
            linespacing=linespacing, zorder=z+1)
    return box

# 输入源标签
ax.text(input_x + input_w/2, 73, '输 入 源',
        ha='center', va='center',
        fontsize=10, fontweight='bold',
        color=GREY_TEXT, family='SimHei', zorder=2)

soft_box(input_x, 60, input_w, 9,
         '用户指令\n/thesis-helper PATH',
         fc='#e9ecef', ec='#7a7a7a',
         fz=10, fw='bold', linespacing=1.3, z=4)
soft_box(input_x, 46, input_w, 11,
         '项目目录\n(config + .tex +\nfigure + bib)',
         fc='#e9ecef', ec='#7a7a7a',
         fz=9.5, linespacing=1.3, z=4)

# ---------- 3.2 中间三色分支 ----------
# 三个并排分支, x 中心: 70, 100, 130; 每个分支 3 个矩形纵向排列
branch_specs = [
    # (cx, fc_pastel, ec_dark, label_zh, label_en, [step1, step2, step3])
    (62, BLUE_PASTEL,   BLUE_DARK,
     '格式合规分支', 'Format Compliance Branch',
     ['format-checker', 'bilingual-abstract', 'word_count\n(母语单位)']),
    (100, PURPLE_PASTEL, PURPLE_DARK,
     'PDF / docx 生成分支', 'PDF/docx Build Branch',
     ['compile-pdf', 'latex-to-word', 'main_aigc.tex']),
    (138, GREEN_PASTEL,  GREEN_DARK,
     'AIGC 降痕分支', 'AIGC Reduction Branch',
     ['aigc-detect', 'aigc-reduce-7stage', '7 章改写\n(Stage 0–6)']),
]

step_w  = 28
step_h  = 8
step_ys = [62, 51, 40]   # 三个 step 的下沿 y
branch_top = 72
branch_bot = 35

for cx, fc, ec, zh, en, steps in branch_specs:
    # 分支顶部彩色标题条
    title_bar = FancyBboxPatch(
        (cx - step_w/2 - 1, branch_top - 3.2),
        step_w + 2, 4.6,
        boxstyle="round,pad=0.1,rounding_size=0.5",
        linewidth=1.2, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(title_bar)
    ax.text(cx, branch_top - 0.9, zh,
            ha='center', va='center',
            fontsize=11, fontweight='bold',
            color=ec, family='SimHei', zorder=4)

    # 三个 step 矩形
    for sy, st in zip(step_ys, steps):
        soft_box(cx - step_w/2, sy, step_w, step_h,
                 st,
                 fc=fc, ec=ec,
                 fz=10.5, fw='bold', color=ec,
                 family='SimHei', linespacing=1.2, z=4)

    # step 之间垂直箭头
    for i in range(len(step_ys) - 1):
        y1 = step_ys[i]              # 上 step 下沿
        y2 = step_ys[i+1] + step_h   # 下 step 上沿
        ax.add_patch(FancyArrowPatch(
            (cx, y1), (cx, y2),
            arrowstyle='-|>', mutation_scale=14,
            color=ec, linewidth=1.5, zorder=3))

    # 顶部标题条 -> 第一个 step
    ax.add_patch(FancyArrowPatch(
        (cx, branch_top - 3.2 + 0), (cx, step_ys[0] + step_h),
        arrowstyle='-|>', mutation_scale=14,
        color=ec, linewidth=1.5, zorder=3))

# ---------- 3.3 输入源 -> 各分支顶部 ----------
input_right_x = input_x + input_w
for cx, _, ec, *_ in branch_specs:
    target_x = cx - step_w/2 - 1
    target_y = branch_top - 0.9
    # 从输入块右侧引出, 拐弯到分支顶部
    ax.add_patch(FancyArrowPatch(
        (input_right_x + 0.3, 65),
        (target_x - 0.3, target_y),
        arrowstyle='-|>', mutation_scale=13,
        color='#404040', linewidth=1.3,
        connectionstyle="arc3,rad=0.0",
        zorder=2))

# ---------- 3.4 右侧门控融合头 (橙) ----------
gate_x = 165
gate_w = 30
gate_y = 48
gate_h = 24

gate = FancyBboxPatch(
    (gate_x, gate_y), gate_w, gate_h,
    boxstyle="round,pad=0.15,rounding_size=1.0",
    linewidth=1.6, edgecolor=ORANGE_DARK,
    facecolor=ORANGE, zorder=4)
ax.add_patch(gate)

ax.text(gate_x + gate_w/2, gate_y + gate_h - 3.2,
        '门控融合头',
        ha='center', va='center',
        fontsize=12, fontweight='bold',
        color='white', family='SimHei', zorder=5)
ax.text(gate_x + gate_w/2, gate_y + gate_h - 7.5,
        'Gating Fusion Head',
        ha='center', va='center',
        fontsize=8.5, fontstyle='italic',
        color='white', family='Times New Roman', zorder=5)

# 三行内容
gate_lines = [
    'orchestrator.py',
    '· 9 phase 调度器',
    '· 验证报告生成',
]
for i, ln in enumerate(gate_lines):
    ax.text(gate_x + gate_w/2, gate_y + gate_h - 12.5 - i*3,
            ln, ha='center', va='center',
            fontsize=10, fontweight='bold' if i == 0 else 'normal',
            color='white', family='SimHei' if i > 0 else 'Times New Roman',
            zorder=5)

# 三分支末端 -> 门控融合头
for cx, _, ec, *_ in branch_specs:
    ax.add_patch(FancyArrowPatch(
        (cx + step_w/2, step_ys[-1] + step_h/2),
        (gate_x, gate_y + gate_h/2 + (cx - 100) * 0.15),
        arrowstyle='-|>', mutation_scale=13,
        color=ec, linewidth=1.5,
        connectionstyle="arc3,rad=-0.05",
        zorder=3))

# ---------- 3.5 最终输出 (4 个粉/红块, 横排底部) ----------
out_y = 13
out_h = 14
out_w = 38
out_xs = [8, 50, 100, 150]
out_titles = [
    'thesis_FINAL.pdf',
    'thesis_FOR_CNKI_CHECK.docx',
    'AIGC 改写版 _aigc.tex',
    '答辩 Q&A +\nverification_report.md',
]
out_subs = [
    '终稿 PDF · 投稿/答辩用',
    '查重送检 · CNKI 兼容',
    '7 章降痕版 · 不动原文',
    '答辩问答 + 自动化验证',
]

# 输出区标签
ax.text(100, 30, '最 终 交 付 物  ·  Final Deliverables',
        ha='center', va='center',
        fontsize=11, fontweight='bold',
        color=PINK_DARK, family='SimHei', zorder=2)

for x, t, s in zip(out_xs, out_titles, out_subs):
    box = FancyBboxPatch(
        (x, out_y), out_w, out_h,
        boxstyle="round,pad=0.15,rounding_size=0.8",
        linewidth=1.5, edgecolor=PINK_DARK,
        facecolor=PINK, zorder=4)
    ax.add_patch(box)
    ax.text(x + out_w/2, out_y + out_h - 4, t,
            ha='center', va='center',
            fontsize=10.5, fontweight='bold',
            color=PINK_DARK,
            family='SimHei', linespacing=1.2, zorder=5)
    ax.text(x + out_w/2, out_y + 4, s,
            ha='center', va='center',
            fontsize=8.5, color='#5b1a14',
            family='SimHei', zorder=5)

# 门控融合头 -> 最终输出 (汇聚式 4 条)
gate_bottom_x = gate_x + gate_w/2
gate_bottom_y = gate_y
for x in out_xs:
    target_x = x + out_w/2
    target_y = out_y + out_h
    ax.add_patch(FancyArrowPatch(
        (gate_bottom_x, gate_bottom_y),
        (target_x, target_y + 0.2),
        arrowstyle='-|>', mutation_scale=12,
        color=ORANGE_DARK, linewidth=1.3,
        connectionstyle="arc3,rad=0.15",
        zorder=2))

# =====================================================================
# 4. callout 虚线注解框
# =====================================================================
# callout #1: PDF/docx 分支 (中间紫色) 注解
callout1 = FancyBboxPatch(
    (50, 23.0), 28, 5.5,
    boxstyle="round,pad=0.15,rounding_size=0.6",
    linewidth=1.4, edgecolor=CALLOUT_EDGE,
    facecolor='#fff8fc', linestyle='--', zorder=5)
ax.add_patch(callout1)
ax.text(64, 25.7,
        'v0.6.4 不可裁剪契约\nTodoWrite 钉全步骤 · 禁跳步',
        ha='center', va='center',
        fontsize=8.8, fontweight='bold',
        color=CALLOUT_EDGE, family='SimHei',
        linespacing=1.25, zorder=6)
# 引线: callout -> PDF 分支底部
ax.add_patch(FancyArrowPatch(
    (78, 28.5), (100, 38),
    arrowstyle='-', mutation_scale=10,
    color=CALLOUT_EDGE, linewidth=1.2,
    linestyle='--', zorder=5))

# callout #2: AIGC 分支 (右绿) 注解
callout2 = FancyBboxPatch(
    (135, 26.5), 30, 5.5,
    boxstyle="round,pad=0.15,rounding_size=0.6",
    linewidth=1.4, edgecolor=GREEN_DARK,
    facecolor='#f6fff5', linestyle='--', zorder=5)
ax.add_patch(callout2)
ax.text(150, 29.2,
        '写到 _aigc 后缀,不动原文\nowner 闭环 · 可回滚',
        ha='center', va='center',
        fontsize=8.8, fontweight='bold',
        color=GREEN_DARK, family='SimHei',
        linespacing=1.25, zorder=6)
ax.add_patch(FancyArrowPatch(
    (138, 32), (138, 38),
    arrowstyle='-', mutation_scale=10,
    color=GREEN_DARK, linewidth=1.2,
    linestyle='--', zorder=5))

# =====================================================================
# 5. 右下角性能指标
# =====================================================================
metric_box = FancyBboxPatch(
    (138, 6.2), 58, 5.0,
    boxstyle="round,pad=0.15,rounding_size=0.5",
    linewidth=1.2, edgecolor=NAVY,
    facecolor='#eef3fa', zorder=5)
ax.add_patch(metric_box)
ax.text(167, 8.7,
        '关键指标 · 9/9 phase 真接通  ·  21/21 ARIS skill 已就位  ·  v0.6.6 (2026-05-03)',
        ha='center', va='center',
        fontsize=9, fontweight='bold',
        color=NAVY_DARK, family='SimHei', zorder=6)

# =====================================================================
# 6. 顶部 -> 底部架构 衔接 (可选: 三个研究内容块的箭头落在底部架构上沿)
# =====================================================================
# 把研究内容三块的"白箭头出口"再用一根细线引到底部架构区, 表示落地
arch_top_y = 81
for cx in research_centers:
    ax.add_line(Line2D([cx, cx], [82.8, arch_top_y + 0.2],
                       color=NAVY, linewidth=0.8,
                       linestyle=(0, (4, 3)), zorder=1))

# =====================================================================
# 7. 左下角图例 / 来源
# =====================================================================
ax.text(7, 8.5,
        '架构层级:  研究内容(顶) → 输入源 → 三色分支 → 门控融合头 → 最终交付物',
        ha='left', va='center',
        fontsize=8.5, color=GREY_TEXT,
        family='SimHei', zorder=2)
ax.text(7, 6.0,
        'Architecture Layers:  Research Goals (top) → Input → 3 Branches → Gating Head → Deliverables',
        ha='left', va='center',
        fontsize=7.5, fontstyle='italic',
        color=GREY_TEXT, family='Times New Roman', zorder=2)

# =====================================================================
# save
# =====================================================================
out_path = r'D:/code/radar_target_recognition/test_skill_git/diagrams/variant-D-academic-cn.png'
plt.savefig(out_path, dpi=220, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print('[OK] saved:', out_path)
