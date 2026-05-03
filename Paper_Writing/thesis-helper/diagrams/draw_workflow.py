#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""thesis-helper 工作流架构图 - matplotlib 渲染版（汇报级）"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib as mpl

mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False

fig, ax = plt.subplots(figsize=(16, 11), dpi=150)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# === 配色 ===
C_USER = '#FFD93D'
C_ENTRY = '#FF6B6B'
C_SCAN = '#4ECDC4'
C_PIPE = '#95E1D3'
C_CHECK = '#A8DADC'
C_AIGC = '#F7B731'
C_DELIV = '#6C5CE7'
C_VERIFY = '#26DE81'
C_BG_L1 = '#FFF5E1'
C_BG_L2 = '#E8F4F8'
C_BG_L3 = '#F0E8FF'

def box(x, y, w, h, label, color, fontsize=9, fontweight='bold', text_color='black'):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=0.6",
                          linewidth=1.5, edgecolor='#333', facecolor=color, alpha=0.92)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight, color=text_color, wrap=True)

def arrow(x1, y1, x2, y2, color='#444', style='->'):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=18,
                        linewidth=1.6, color=color)
    ax.add_patch(a)

def layer_bg(x, y, w, h, label, color):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.5,rounding_size=1.5",
                          linewidth=2.0, edgecolor='#888', facecolor=color, alpha=0.35,
                          linestyle='--')
    ax.add_patch(rect)
    ax.text(x + 1.5, y + h - 1.8, label, ha='left', va='top',
            fontsize=10, fontweight='bold', color='#333',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#888', alpha=0.9))

# ========== 标题 ==========
ax.text(50, 96, 'thesis-helper · 学生论文写作一站式工作流',
        ha='center', va='center', fontsize=17, fontweight='bold', color='#222')
ax.text(50, 93.2, 'v0.6.4 · 9 phase 端到端自动化 + 21 ARIS 互动 skill + 不可裁剪契约',
        ha='center', va='center', fontsize=10, color='#555', style='italic')

# ========== L0 用户入口 ==========
box(28, 85, 44, 5.5, '用户：/thesis-helper  D:\\my-research-project  --type undergrad-thesis',
    C_USER, fontsize=11)

arrow(50, 85, 50, 81)

# ========== L1 入口契约 ==========
layer_bg(2, 70.5, 96, 11, 'L1 · 入口契约（v0.6.4 不可裁剪）', C_BG_L1)
box(8, 73, 22, 5, '🚦 钉死 TODO\nTodoWrite 列全步骤', C_ENTRY, fontsize=9.5)
box(35, 73, 22, 5, '🔒 禁止跳步\n仅 --skip 显式声明', C_ENTRY, fontsize=9.5)
box(62, 73, 30, 5, '📋 verification_report.md\n含每项真数字 + 文件路径', C_ENTRY, fontsize=9.5)

arrow(50, 70, 50, 67)

# ========== L2 主链路 9 phase ==========
layer_bg(2, 36, 96, 30, 'L2 · 主链路（orchestrator.py · 9 phase 确定性 Python · 真已 9/9 通）', C_BG_L2)

# 第一行 (Phase 0-2)
box(5, 56, 18, 5, 'Phase 0-A/B\n📂 project-scanner\n读 config + 扫资产', C_SCAN, fontsize=8.2)
box(26, 56, 18, 5, 'Phase 1\n📐 format-checker\n8 项含字数(母语)', C_PIPE, fontsize=8.2)
box(47, 56, 18, 5, 'Phase 1.5\n🔤 bilingual-abstract\n中英摘要平行', C_PIPE, fontsize=8.2)
box(68, 56, 18, 5, 'Phase 2 ⭐\n📄 compile-pdf\nthesis_FINAL.pdf', C_DELIV, fontsize=8.2, text_color='white')
arrow(23, 58.5, 26, 58.5)
arrow(44, 58.5, 47, 58.5)
arrow(65, 58.5, 68, 58.5)

# 第二行 (Phase 3-5)
box(5, 47, 18, 5, 'Phase 3 ⭐\n📝 latex-to-word\nFOR_CNKI_CHECK.docx', C_DELIV, fontsize=8.2, text_color='white')
box(26, 47, 18, 5, 'Phase 4\n🔍 aigc-detect\n7 章扫描', C_AIGC, fontsize=8.2)
box(47, 47, 18, 5, 'Phase 5\n✏️ aigc-reduce 7-stage\n→ _aigc 后缀(不动原文)', C_AIGC, fontsize=8.2)
box(68, 47, 18, 5, 'Phase 6\n🎤 thesis-defense-prep\n答辩 Q&A', C_PIPE, fontsize=8.2)
arrow(77, 56, 14, 52)  # phase 2 -> phase 3
arrow(23, 49.5, 26, 49.5)
arrow(44, 49.5, 47, 49.5)
arrow(65, 49.5, 68, 49.5)

# 第三行 (Phase 7-8)
box(15, 38, 30, 5, 'Phase 7（硕士必做）\n👁️ thesis-blind-review · 匿名版 + 报告', C_PIPE, fontsize=8.5)
box(55, 38, 30, 5, 'Phase 8 ⭐\n✅ verification_report.md · 真数字闭环', C_VERIFY, fontsize=8.5, text_color='white')
arrow(77, 47, 30, 43)  # phase 6 -> phase 7
arrow(45, 40.5, 55, 40.5)

# ========== L3 互动层 ==========
layer_bg(2, 6, 96, 28, 'L3 · 互动层（Claude 在对话里调 21 ARIS skill · 上游 100% 已装 ~/.claude/skills/）', C_BG_L3)

# 6 类 互动 skill
box(4.5, 25, 14, 5.5, '📚 找文献\nresearch-lit\narxiv\nsemantic-scholar', C_CHECK, fontsize=8)
box(20, 25, 14, 5.5, '💡 验新颖\nnovelty-check\nclaude-paper:study', C_CHECK, fontsize=8)
box(35.5, 25, 14, 5.5, '📐 写理论\nproof-writer\nformula-derivation', C_CHECK, fontsize=8)
box(51, 25, 14, 5.5, '🎨 出图表\nmermaid-diagram\nmatplotlib-tvhahn\npaper-illustration', C_CHECK, fontsize=8)
box(66.5, 25, 14, 5.5, '🧪 设计实验\nablation-planner\nresult-to-claim', C_CHECK, fontsize=8)
box(82, 25, 14, 5.5, '📤 投稿后\nrebuttal\npaper-reviewer\npaper-slides/poster', C_CHECK, fontsize=8)

# 用户调用范式
ax.text(50, 21.5, '用户说话方式 → Claude 自动 Skill tool 调用',
        ha='center', va='center', fontsize=10, fontweight='bold', color='#333')

usage_examples = [
    ('"找一下低空雷达相关工作"', 'Skill("research-lit")', 4, 17),
    ('"给软阈值写引理证明"', 'Skill("proof-writer")', 4, 13),
    ('"做答辩 PPT"', 'Skill("paper-slides")', 4, 9),
    ('"我这个 idea 有人做过吗"', 'Skill("novelty-check")', 52, 17),
    ('"起草 rebuttal"', 'Skill("rebuttal")', 52, 13),
    ('"做架构图"', 'Skill("paper-illustration")', 52, 9),
]
for u, s, x, y in usage_examples:
    ax.text(x, y, u, ha='left', va='center', fontsize=8.5, color='#555', style='italic')
    ax.text(x + 22, y, '→', ha='left', va='center', fontsize=10, color='#888')
    ax.text(x + 24.5, y, s, ha='left', va='center', fontsize=8.5,
            color='#6C5CE7', fontweight='bold', family='monospace')

# ========== 最终交付物 ==========
ax.text(50, 3, '⭐ 最终交付物：thesis_FINAL.pdf  +  thesis_FOR_CNKI_CHECK.docx  +  AIGC 改写版  +  答辩 Q&A  +  verification_report.md',
        ha='center', va='center', fontsize=10.5, fontweight='bold', color='#222',
        bbox=dict(boxstyle='round,pad=0.6', facecolor='#FFF9C4', edgecolor='#F57F17', linewidth=1.5))

plt.tight_layout()
out_png = 'D:/code/radar_target_recognition/test_skill_git/diagrams/thesis-helper-workflow.png'
out_svg = 'D:/code/radar_target_recognition/test_skill_git/diagrams/thesis-helper-workflow.svg'
plt.savefig(out_png, dpi=200, bbox_inches='tight', facecolor='white')
plt.savefig(out_svg, format='svg', bbox_inches='tight', facecolor='white')
print(f"PNG: {out_png}")
print(f"SVG: {out_svg}")
