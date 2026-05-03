# Paper_Writing · 论文写作类 skill 集合

> 带刀阿越 维护的论文写作工作流子集。从选题/调研 → 写作 → 降 AIGC → 投稿/答辩，全链路覆盖。
> 上一级 → [SKILL 大仓库](../README.md)

![thesis-helper 工作流架构图](thesis-helper/diagrams/variant-E-clean.png)

---

## 📦 当前收纳（3 包 · 25+ skills）

| Skill 包 | 入口 | 介绍 |
|---------|------|------|
| [`thesis-helper`](thesis-helper/) ⭐ | `/thesis-helper PATH` | **顶层一站式入口**（v0.6.13+）。本科/硕士/博士毕设、IEEE/Elsevier 期刊、ACM 会议——给项目目录就自动路由：扫资产 → 格式合规（含字数按学校母语单位 9 类规范）→ 中英摘要平行检查 → PDF/docx 双交付 → AIGC 7-stage 真改写（写到 _aigc 后缀，不动原文）→ 答辩 Q&A → 盲审版。底层调 `aigc-reduce-skills` + `PaperWriting` + 17 个 ARIS skill。**接到指令后第一时间钉死 TODO 流水线清单，禁止"我觉得不需要"地跳步骤** |
| [`aigc-reduce-skills`](aigc-reduce-skills/) | `/aigc降低` | 全自动学术降 AIGC 率流水线 v4，**模型驱动 + 7 段串行**（去结构化 → 词汇 → 节奏 → 衔接 → 克制 → 困惑度+思维痕迹 → 引用注入），自动调用 NeurIPS 2023 检测模型预扫描，按 `ai_prob` 排序处理，处理后 before/after delta 验证 |
| [`PaperWriting`](PaperWriting/) | `/paper-writing` 等 | 学术论文写作 skill 集合（来源 [skills-codex](https://github.com/skills-codex) 生态 + 独立 `paper_reviewer`）：从实验结果到投稿就绪 PDF 的全流程 — `paper-plan` / `paper-figure` / `paper-write` / `paper-compile` / `paper-illustration` / `paper-slides` / `paper-poster` / `paper-writing` / `paper_reviewer` |

> 推荐入口顺序：**真懒 → `/thesis-helper`（一句话起飞）；想精控某段 → 直接调 `/paper-writing` 或 `/aigc降低`**。

---

## 🚦 thesis-helper · 完整流程清单（接到指令逐项跑完，禁止跳步）

接到 `/thesis-helper PATH` 第一时间，agent **必须** 用 TodoWrite 工具把对应论文类型的
pipeline 全步骤写成 TODO 列表，逐项打钩。**不允许凭"我觉得这步不需要"自行省略**——
之前真实事故：agent 漏跑 word_count、format-check、AIGC 扫描，导致字数不达标和格式不合规没被发现。
完整流程清单详见 [`thesis-helper/SKILL.md`](thesis-helper/SKILL.md) 的 "🚦 完整流程清单" 章节。

---

## 📊 字数门槛 · 9 类论文规范母语单位（v0.6.13）

| 规范 | 门槛 | 单位 | | 规范 | 门槛 | 单位 |
|------|------|------|---|------|------|------|
| buaa_undergrad | 30k-100k | 中文字符 | | journal-ieee | 4k-12k | 英文单词 |
| buaa_master | 50k-150k | 中文字符 | | journal-elsevier | 5k-15k | 英文单词 |
| tsinghua_undergrad | 30k-100k | 中文字符 | | conference-acm | 3k-9k | 英文单词 |
| tsinghua_master | 50k-150k | 中文字符 | | generic | 5k-100k | auto |
| phd-thesis | 80k-200k | 中文字符 | | | | |

> 中文论文按"中文字符数"比，英文论文按"英文单词数"比——按学校规范母语去比，不是字+词混算。

---

## 🚀 安装

### 安装 `thesis-helper`（一站式论文工作流，**推荐入口**）

```bash
# 完整 clone + 目录 junction（保仓库与本地同步）
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL

# Windows（PowerShell，无需管理员）：
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\thesis-helper" -Target "$env:USERPROFILE\SKILL\Paper_Writing\thesis-helper"

# Linux / macOS：
ln -s ~/SKILL/Paper_Writing/thesis-helper ~/.claude/skills/thesis-helper
```

使用：

```text
/thesis-helper D:\my-research-project
/thesis-helper D:\my-research-project --type undergrad-thesis --venue 北航
/thesis-helper D:\my-research-project --type journal --venue IEEE_JOURNAL
```

接到指令后 agent 自动：扫资产 → 钉 TODO 流水线（完整流程清单）→ 逐项跑 → 输出 PDF + docx + AIGC 改写 + 答辩 Q&A + 验证报告。

### 安装 `aigc-reduce-skills`（AIGC 降低 v4）

```bash
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL
cp -r ~/SKILL/Paper_Writing/aigc-reduce-skills/aigc-reduce* ~/.claude/skills/
cp -r ~/SKILL/Paper_Writing/aigc-reduce-skills/aigc-scan ~/.claude/skills/

# 安装本地检测模型依赖（首次运行 detect_aigc.py 自动下载 ~500MB 模型）
pip install -r ~/SKILL/Paper_Writing/aigc-reduce-skills/detect_aigc/requirements.txt
```

使用：`/aigc降低 path/to/paper.tex` — 自动跑完 7 段流水线 + before/after delta 验证。

### 安装 `PaperWriting`（论文写作全流程）

```bash
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL
cp -r ~/SKILL/Paper_Writing/PaperWriting/paper-* ~/.claude/skills/
cp -r ~/SKILL/Paper_Writing/PaperWriting/paper_reviewer ~/.claude/skills/
```

> ⚠️ `paper-plan` / `paper-write` / `paper-figure` 等核心 pipeline 技能依赖 [Codex MCP](https://github.com/skills-codex) 插件（用 `claude mcp add codex` 安装），`paper_reviewer` 可独立使用。

使用：`/paper-writing path/to/NARRATIVE_REPORT.md` — 一键串联 `plan → figure → write → compile → review`。

---

## 🔗 推荐组合用法

### 一句话起飞（推荐）

```bash
/thesis-helper D:\my-research-project
```

→ 自动按论文类型路由完整 pipeline，端到端给你 PDF + docx + AIGC 改写 + 答辩 Q&A + 验证报告。

### 或精控某段（传统三段式）

```bash
# 1. 从实验报告生成投稿就绪的 LaTeX + PDF
/paper-writing path/to/NARRATIVE_REPORT.md

# 2. 跑 AIGC 降痕（v4 自动预扫描 + 模型评分排序）
/aigc降低 paper/main.tex

# 3. 导出 Word 上传 CNKI 终审（thesis-helper 也会自动做）
```

---

## 📁 目录结构

```
Paper_Writing/
├── README.md                          ← 本文件
├── thesis-helper/                     ← ⭐ 顶层一站式入口（推荐）
│   ├── SKILL.md
│   ├── orchestrator.py                ← 9 phase 调度器
│   ├── extensions/                    ← 5 个内置扩展
│   ├── integrations/                  ← 21 个 ARIS skill 桥接
│   ├── pipelines/                     ← 4 类论文流水线规范
│   └── diagrams/                      ← 5 种工作流图（PNG/SVG/Mermaid）
├── aigc-reduce-skills/                ← AIGC 率降低 v4（模型驱动）
│   ├── aigc-reduce/                   ← 总入口
│   ├── aigc-reduce-{destructure,vocab,rhythm,cohesion,hedging,perplexity,cite-inject}/
│   ├── aigc-scan/                     ← 独立预扫描诊断
│   └── detect_aigc/                   ← 本地 NeurIPS 2023 检测模型
└── PaperWriting/                      ← 论文写作 9 skill 集合
    ├── paper-{plan,figure,write,compile,illustration,slides,poster,writing}/
    └── paper_reviewer/                ← 独立 5 维审稿模拟
```
