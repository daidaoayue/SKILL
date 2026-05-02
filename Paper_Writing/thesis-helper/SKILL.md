---
name: thesis-helper
description: "学生论文写作一站式工作流。傻瓜入口：告诉我你的工程目录在哪、要写什么论文（期刊/会议/本科毕设/硕士毕设），我自动路由到 paper-writing + aigc-reduce + 答辩 + Word 转换全流水线。Triggers on: '/thesis-helper', '/写论文', '/帮我写论文', 'thesis-helper', '我要写期刊', '我要写会议', '我要写毕设', '我要写本科论文', '我要写硕士论文', '答辩准备'."
argument-hint: [project-directory] [thesis-type]
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Skill, Agent
---

# Thesis Helper · 学生论文写作一站式工作流

> 一句话价值：**告诉我项目目录在哪 + 要写什么论文，我自动读 config → 路由 pipeline → 端到端交付**。
> 不重新造轮子——底层调用 `/paper-writing` + `/aigc降低` + 17 个现成 skill + 5 个新造 skill。

## 四种论文类型 · 四条 pipeline

```
┌──────────────────────────────────────────────────────────────────────┐
│ 论文类型     │ Pipeline 组合                                │ 检测器  │
├──────────────┼─────────────────────────────────────────────┼─────────┤
│ 期刊论文      │ /paper-writing → /rebuttal (投稿后)          │ Turnitin│
│ 会议论文      │ /paper-writing → /paper-slides → /paper-poster│ Turnitin│
│ 本科毕设      │ /paper-writing → /aigc降低 → /latex-to-word  │ CNKI    │
│              │ → /thesis-defense-prep                       │         │
│ 硕士毕设      │ 同本科毕设 + /thesis-blind-review (盲审版)    │ CNKI    │
│              │ + 严格阈值                                    │         │
└──────────────────────────────────────────────────────────────────────┘
```

## 用户只需 1 条指令

```text
/thesis-helper D:\my-research-project
```

可选参数：
```text
/thesis-helper D:\my-research-project --type undergrad-thesis --venue 北航
/thesis-helper D:\my-research-project --type journal --venue IEEE_JOURNAL
/thesis-helper D:\my-research-project --type conference --venue NeurIPS
/thesis-helper D:\my-research-project --type master-thesis --detector CNKI
```

## Phase 0 · 项目自动扫描（必做）

接到指令后**立即静默执行**，不向用户提问任何已有信息：

### 0-A · 读 thesis.config.yml（如果存在）

按以下顺序在项目根目录查找配置：
1. `<project>/thesis.config.yml`
2. `<project>/thesis.config.yaml`
3. `<project>/.thesis-helper/config.yml`
4. `<project>/testskill/thesis.config.yml`（沙箱模式）

找到 → 解析所有字段，作为后续路由的真值来源。
未找到 → 进入交互式 config 生成（见 0-D）。

### 0-A.1 · 路径解析（v0.3 修订·真实项目教训）

**关键设计**：真实项目里"工程根 ≠ 论文根"。typical 雷达项目目录长这样：

```text
my-project/                          ← config.paths.project_root（工程根，含数据/代码）
├── src/                             代码
├── data/                            数据
├── results/                         实验结果
├── paper_writing/                   论文集合（可能多篇）
│   ├── 我的期刊论文/
│   └── 我的毕设/
│       └── thesis_main/             ← config.paths.paper_root（论文实际工作目录）
│           ├── main.tex             ← config.paths.main_tex（默认）
│           ├── main_aigc.tex        AIGC 处理后版本
│           ├── main_aigc_test.tex   AIGC 测试版
│           ├── submit_AI_main.tex   AI 提交版
│           ├── data/                论文章节
│           │   ├── abstract.tex
│           │   ├── chapter1-intro.tex
│           │   └── ...
│           ├── figure/              图表
│           └── buaathesis.cls       学校 LaTeX 模板
└── thesis.config.yml                ← thesis-helper 配置入口
```

**路径字段优先级**（高→低）：
1. `config.paths.main_tex` — 显式指定主文件（推荐有多版本时用）
2. `config.paths.paper_root` + `main.tex` — 默认主文件
3. `config.paths.project_root` + `main.tex` — 兜底（小项目，论文在根）

### 0-A.2 · 多 main.tex 版本处理（v0.3 真实项目实测发现）

雷达项目真实情况：实测到 **7 个 main_*.tex 共存**：
- `main.tex`（主版本）
- `main_aigc.tex`（aigc-reduce 处理后）
- `main_aigc_test.tex`（实验版）
- `main_pandoc.tex`（pandoc 转换中间产物）
- `submit_AI_main.tex`（AI 检测专用提交版）
- `submit_for_check.tex`（查重提交版）
- `submit_for_docx.tex`（Word 转换源）

**处理规则**：

```text
config.paths.main_tex 显式指定        → 用指定的（最高优先）
否则按以下顺序自动选：
   1. paper_root/main.tex             默认主版本
   2. paper_root/main_aigc.tex        若 main.tex 不存在
   3. 报错暂停，让用户在 config 显式指定
```

**Phase 5 (latex-to-word) 输入特殊规则**：
- 默认输入 `main_aigc.tex`（已降痕版本，准备转 Word 上传）
- 配置：`paths.latex_to_word_input` 可覆盖

**Phase 4 (aigc-reduce) 输入特殊规则**：
- 默认输入 `main.tex`（原始版本，避免对已处理版本二次降痕）
- 输出到 `main_aigc.tex`（不破坏原文）

### 0-B · 智能扫描项目目录（处理数据/代码混合的真实场景）

**关键设计决策**：用户的"数据与结果"通常**和工程代码混在一起**，不要求用户单独整理。
本 skill 必须**主动探测**以下资产，构建 ProjectMap：

调用 `scanners/project-scanner.py`，输出 ProjectMap.json：

```yaml
ProjectMap:
  code_files:        # 工程代码（.py/.cpp/.m/.ipynb 等）
    - src/train.py
    - src/model.py
  data_files:        # 数据文件（.csv/.json/.npz/.h5/.mat）
    - results/exp1.csv
    - data/train.npz
  figure_sources:    # 图表源文件（.png/.pdf/.svg/figure 脚本）
    - figs/accuracy_curve.py
    - figs/confusion_matrix.png
  result_logs:       # 实验日志（log/.txt/.out/wandb）
    - logs/run_2026-04-30.txt
  existing_writing:  # 已有写作（.tex/.md/.docx）
    - draft.md
    - notes/related_work.md
  format_rules:      # 格式要求文件夹
    - 格式要求/template.tex
    - 格式要求/字数要求.md
  references:        # 参考文献（.bib/.enl/.pdf in refs/）
    - references.bib
    - refs/zhang2023.pdf
```

**扫描规则**（顺序匹配，命中即归类）：

| 类型 | 路径关键词 | 文件后缀 |
|------|-----------|----------|
| 格式要求 | `格式要求/`, `format/`, `template/` | * |
| 参考文献 | `refs/`, `references/`, `bib/` | `.bib`, `.enl`, `.pdf` |
| 数据 | `data/`, `results/`, `output/` 或同级 | `.csv`, `.json`, `.npz`, `.h5`, `.mat`, `.parquet` |
| 图表源 | `figs/`, `figures/`, `plots/` | `.py`(画图脚本), `.png`, `.pdf`, `.svg` |
| 实验日志 | `logs/`, `wandb/`, `runs/` | `.log`, `.txt`, `.out` |
| 已有写作 | 任何路径 | `.tex`, `.md`, `.docx` |
| 工程代码 | 任何路径（除上述） | `.py`, `.cpp`, `.m`, `.ipynb`, `.cu` |

### 0-C · 解析"格式要求/"文件夹

调用 `scanners/format-rules-scanner.py`，识别：
- LaTeX 模板文件（`.tex`, `.cls`, `.sty`）→ 直接传给 paper-writing
- Word 模板（`.docx`, `.dotx`）→ 提取章节结构
- 字数要求（`.md`, `.txt` 含"字数"关键字）→ 提取数字约束
- 评分标准（`.pdf`, `.md` 含"评分"关键字）→ 注入到 paper-writing 的 plan 阶段

### 0-D · 交互式 config 生成（仅在未找到 config 时）

询问最少必要信息（每问一次都给出默认值）：

```
我在你的项目里没找到 thesis.config.yml。
为了不每次问你这些事，我先生成一个配置文件，以后直接读它即可。

1. 论文类型？
   [1] 期刊论文 (默认)
   [2] 本科毕设
   [3] 硕士毕设
   [4] 博士毕设

2. 投稿目标 / 学校？
   [示例] IEEE_JOURNAL / NeurIPS / 北航 / 清华 / ...

3. 主要语言？
   [1] 中文 (默认毕设)
   [2] 英文 (默认期刊)

4. AIGC 检测器？
   [1] CNKI 知网 (默认毕设)
   [2] Turnitin (默认海外期刊)
   [3] PaperPass / 维普 (备查)
   [4] 跳过（不做 AIGC 降痕）

完成后写入 <project>/thesis.config.yml，并继续。
```

## Phase 1 · 路由 + 调用 pipeline

根据 config 里的 `thesis_type` 字段决定调用链。**所有 pipeline 默认前置触发**：
- `/research-lit` 或 `/comm-lit-review` 做文献综述（如有 `pipeline.lit_review: true`）
- `/novelty-check` 验证 idea 新颖性（投稿前）

详细 pipeline 文档见 `pipelines/<type>-pipeline.md`。

### 期刊论文（journal）

```
1. /paper-writing <NARRATIVE_REPORT.md>  --venue=<config.venue>
   ├─ 注入 ProjectMap → paper-figure 自动找数据
   ├─ 注入 format_rules 的 LaTeX 模板
   └─ 内置 /paper_reviewer 做投稿前自审
2. (可选) /scientific-visualization 升级图表到期刊出版级
3. 跳过 AIGC 降痕（期刊审稿人通常不查 CNKI）
4. 投稿后：/rebuttal 处理审稿意见 → 二次提交
```

### 会议论文（conference·新增）

```
1. /paper-writing 同期刊
2. /paper-slides 生成答辩/汇报 Beamer PPT + 演讲稿
3. /paper-poster 生成 A0 学术海报
4. (可选) /rebuttal 处理 author response 阶段
```

### 本科毕设（undergrad-thesis）

```
1. /paper-writing 用学校 LaTeX 模板
   └─ 默认调 /comm-lit-review 做文献综述章节（如毕设是通信/雷达方向）
2. /aigc降低 paper/main.tex
   ├─ 默认目标：CNKI AIGC < 8% / 查重 < 8% (北航标准)
   ├─ 强制 CNKI 验证循环
   └─ 致谢节专项处理（v3 内置）
3. /latex-to-word（extensions 新造）→ 学校要求的 Word 版
4. /thesis-defense-prep（extensions 新造）→ 答辩 PPT + 答辩问答模拟
5. /format-compliance-checker（extensions 新造）→ 字号/行距/页眉合规检查
6. /bilingual-abstract（extensions 新造）→ 中英文摘要平行检查
7. 输出 6 件套：main.pdf, main.docx, aigc-reduce-report.md,
                cnki 验证记录, defense.pptx, format-check-report.md
```

### 硕士毕设（master-thesis）

```
1-6 同本科毕设，+ 严格阈值（AIGC < 5% / 查重 < 5%）
7. /thesis-blind-review（extensions 新造）→ 生成盲审版（去除作者信息）
8. 输出 7 件套：含 main_blind.pdf
```

## Phase 1.5 · Skill 调用矩阵（接入资产清单）

本 skill 编排以下 22 个 skill（17 现成 + 5 新造）。按需触发，详见 `integrations/` 和 `extensions/`：

```
┌────────────────────────────────────────────────────────────────────────┐
│ 阶段       │ 调用的 skill                              │ 类型           │
├────────────┼──────────────────────────────────────────┼────────────────┤
│ 选题/调研  │ arxiv, semantic-scholar, research-lit,    │ integration    │
│           │ comm-lit-review, claude-paper:study,      │                │
│           │ novelty-check                             │                │
│ 理论推导  │ proof-writer, formula-derivation          │ integration    │
│ 图表      │ scientific-visualization, matplotlib-     │ integration    │
│           │ tvhahn, mermaid-diagram, paper-           │                │
│           │ illustration                              │                │
│ 实验对接  │ result-to-claim, ablation-planner         │ integration    │
│ 写作主流  │ paper-writing (含 plan/figure/write/      │ 直接调用        │
│           │ compile/improvement)                      │                │
│ 降 AIGC   │ aigc-reduce (含 7 stage 子流水线)         │ 直接调用        │
│ 投稿后    │ rebuttal, paper_reviewer                  │ integration    │
│ 答辩/海报 │ paper-slides, paper-poster                │ integration    │
│ 交付格式  │ document-skills:docx/pptx/pdf             │ integration    │
│ 新造 skill│ latex-to-word, thesis-defense-prep,       │ extension      │
│           │ thesis-blind-review, bilingual-abstract,  │                │
│           │ format-compliance-checker                 │                │
└────────────────────────────────────────────────────────────────────────┘
```

每个 integration 的调用规则在 `integrations/<skill-name>-wrapper.md` 中定义。
每个 extension 是完整新 skill，目录结构：`extensions/<skill-name>/SKILL.md`。

## Phase 2 · 闭环验证（红线）

完成后**必须**输出验证报告，不验证 = 自嗨：

```
✅ 交付清单
├── 论文 PDF：<path>/paper/main.pdf
├── LaTeX 源：<path>/paper/sections/*.tex
├── 检测报告：<path>/aigc-reduce-report.md  (毕设)
├── 配置快照：<path>/thesis.config.yml
└── ProjectMap：<path>/.thesis-helper/project_map.json

📊 验证数据
├── 论文页数：[N] / 限制 [M]
├── AIGC 率：[X]% / 阈值 [Y]%  (本地检测，CNKI 终审)
├── 查重率：[X]% / 阈值 [Y]%
└── 字数：[X] / 要求 [Y]

⚠️ 待办（如有）
└── ...
```

## 跨平台支持（用户用别的 AI 怎么办）

本 skill 在仓库中维护**单一真源**（即本 SKILL.md + 子目录），通过 `compilers/build.py` 编译到各平台：

```
thesis-helper (Claude SKILL.md 真源)
       │
       ├── compilers/targets/claude.py    →  ~/.claude/skills/thesis-helper/
       ├── compilers/targets/cursor.py    →  <project>/.cursorrules
       ├── compilers/targets/gemini.py    →  <project>/GEMINI.md
       ├── compilers/targets/cline.py     →  <project>/.clinerules
       └── compilers/targets/universal.py →  通用 prompt 包（任意 AI 复制粘贴）
```

用户根据自己用的 AI 选择安装方式。详见 `README.md`。

## Owner 闭环承诺

- ✅ 接到 `/thesis-helper` → 自动扫描 + 自动路由 + 自动跑完 pipeline
- ✅ ProjectMap 必须扫描完整（不要求用户整理目录）
- ✅ AIGC 降痕的 CNKI 验证未做 → 不算完成
- ✅ 验证报告未输出 → 不算完成
- ❌ 不要求用户手动整理"数据与结果"目录——主动扫描

## 三条红线

- ❌ 不改动用户的工程代码、数据、实验结果
- ❌ 不假设用户已配置好——主动生成 config，主动扫描资产
- ❌ 不只输出 PDF 不验证——必须给检测数据 + 字数 + 页数闭环

## 相关 skill

- `/paper-writing` — 论文写作 pipeline（前置依赖）
- `/aigc降低` — AIGC 降痕 pipeline（前置依赖，毕设流程）
- `/paper_reviewer` — 审稿模拟（可选辅助）
- `/aigc-scan` — AIGC 检测扫描（aigc-reduce 已内置自动调用）

## 配置示例

最小化 `thesis.config.yml`：
```yaml
thesis_type: undergrad-thesis    # journal | undergrad-thesis | master-thesis
venue: 北航                       # 期刊名 / 学校名
language: zh                     # zh | en
detector: CNKI                   # CNKI | Turnitin | PaperPass | VIPCS | none
```

完整字段见 `thesis.config.template.yml`。

---

> 因为信任所以简单——告诉我项目在哪，剩下的我闭环。
