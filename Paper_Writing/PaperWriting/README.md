# Paper Writing Skills for Claude Code

> 学术论文写作技能包 — 从实验结果到投稿就绪 PDF 的全自动流水线

## 声明 / Attribution

本目录下的 skills 均为 **Claude Code（Anthropic）** 技能文件，需配合 [Claude Code](https://claude.ai/code) 使用。

核心 pipeline 技能（`paper-write`、`paper-plan`、`paper-figure`、`paper-compile` 等）来源于 **[skills-codex](https://github.com/skills-codex) 插件生态**，依赖 `mcp__codex__codex` MCP 插件。本仓库仅作个人备份和学习用途，**不主张原创权**，如有侵权请联系删除。

`paper_reviewer` 技能为独立开发版本，不依赖 Codex MCP。

---

## 技能列表

| 技能 | 触发命令 | 功能 | 依赖 |
|------|---------|------|------|
| `paper-plan` | `/paper-plan` | 从实验结论生成论文大纲（含 Claims-Evidence 矩阵） | Codex MCP |
| `paper-figure` | `/paper-figure` | 从实验数据生成出版级图表（PDF/PNG） | Codex MCP |
| `paper-write` | `/paper-write` | 按大纲逐节生成 LaTeX 正文 | Codex MCP |
| `paper-compile` | `/paper-compile` | 编译 LaTeX → PDF，自动修复编译错误 | Codex MCP |
| `paper-illustration` | `/paper-illustration` | 生成论文配图（架构图/流程图） | Codex MCP |
| `paper-slides` | `/paper-slides` | 生成 Beamer 幻灯片 + PPTX + 演讲稿 | Codex MCP |
| `paper-poster` | `/paper-poster` | 生成学术海报（LaTeX beamerposter） | Codex MCP |
| `paper-writing` | `/paper-writing` | 全流程编排器（plan→figure→write→compile→review） | Codex MCP |
| `paper_reviewer` | `/paper_reviewer` | 审稿人视角评审，输出结构化审稿意见 | 无额外依赖 |

---

## 安装

### 前置要求

- [Claude Code](https://claude.ai/code) CLI 已安装
- Codex MCP 插件（paper-plan/write/figure/slides/poster/compile 需要）

### 安装 Codex MCP 插件

```bash
claude mcp add codex
```

### 安装 Skills

将本目录下各 skill 文件夹复制到 Claude Code skills 目录：

**macOS / Linux：**
```bash
cp -r paper-* ~/.claude/skills/
cp -r paper_reviewer ~/.claude/skills/
```

**Windows：**
```powershell
Copy-Item -Recurse paper-* $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse paper_reviewer $env:USERPROFILE\.claude\skills\
```

重启 Claude Code 后生效。

---

## 使用说明

### 完整写论文流程（推荐）

```
/paper-writing path/to/NARRATIVE_REPORT.md
```

`paper-writing` 是全流程编排器，自动串联以下步骤：

```
/paper-plan → /paper-figure → /paper-write → /paper-compile → 自动审稿循环
```

**整个流程无需手动干预**，Claude 会依次完成大纲→图表→正文→编译→审稿润色。

---

### 单步调用（高级用法）

#### 1. 生成论文大纲

```
/paper-plan path/to/NARRATIVE_REPORT.md
```

输出：`PAPER_PLAN.md`（含章节规划、Claims-Evidence 矩阵、图表规划）

支持期刊/会议：`ICLR`、`NeurIPS`、`ICML`、`CVPR`、`ACL`、`AAAI`、`ACM`、`IEEE_JOURNAL`、`IEEE_CONF`

指定投稿目标：
```
/paper-plan NARRATIVE_REPORT.md -- venue: IEEE_JOURNAL
```

---

#### 2. 生成图表

```
/paper-figure path/to/results/
```

从实验数据（CSV/JSON/NPZ）生成出版级 PDF 图表，同时生成 `figures/latex_includes.tex`。

---

#### 3. 生成 LaTeX 正文

```
/paper-write
```

需先完成 `/paper-plan` 和 `/paper-figure`。逐节生成 LaTeX，自动从 DBLP 获取真实 BibTeX（避免幻觉引用）。

---

#### 4. 编译 PDF

```
/paper-compile
```

运行 `latexmk`，自动修复常见编译错误（未定义引用、缺失包等），直到编译成功。

---

#### 5. 生成幻灯片

```
/paper-slides path/to/paper/
```

输出：Beamer LaTeX 源码 + 编译好的 PDF + PPTX（可选）+ 完整演讲稿（含每页 speaker notes）

自定义时长：
```
/paper-slides paper/ -- duration: 15min
```

---

#### 6. 生成海报

```
/paper-poster path/to/paper/
```

输出：A0 竖版学术海报（LaTeX beamerposter），适合学术会议展示。

---

#### 7. 审稿（独立使用）

```
/paper_reviewer path/to/paper.pdf
```

以审稿人视角评审，输出结构化意见（Soundness / Significance / Novelty / Clarity 各维度评分 + 详细 comments）。

**不依赖 Codex MCP**，可单独使用。

---

### 常用工作流示例

**从零开始写 NeurIPS 论文：**
```
/paper-plan NARRATIVE_REPORT.md -- venue: NeurIPS
/paper-figure results/
/paper-write
/paper-compile
/paper_reviewer paper/main.pdf
```

**已有论文，只需要幻灯片 + 海报：**
```
/paper-slides paper/
/paper-poster paper/
```

---

## 输出文件结构

```
your-project/
├── PAPER_PLAN.md          # /paper-plan 输出
├── figures/
│   ├── fig1_accuracy.pdf  # /paper-figure 输出
│   ├── fig2_ablation.pdf
│   └── latex_includes.tex # 图表引用宏
├── paper/
│   ├── main.tex           # /paper-write 输出
│   ├── main.bib
│   ├── main.pdf           # /paper-compile 输出
│   └── sections/
│       ├── introduction.tex
│       ├── method.tex
│       └── ...
├── slides/
│   ├── slides.tex         # /paper-slides 输出
│   └── slides.pdf
└── poster/
    ├── poster.tex         # /paper-poster 输出
    └── poster.pdf
```

---

## 注意事项

- 所有 pipeline 技能（`paper-write` 等）需要 Codex MCP 插件，`/paper_reviewer` 不需要
- 模型默认投稿目标为 `ICLR`，IEEE 系列需显式指定 `venue: IEEE_JOURNAL` 或 `IEEE_CONF`
- IEEE 期刊/会议参考文献计入页数限制，与 ML 会议不同
- DBLP BibTeX 自动抓取需要网络连接（避免 LLM 幻觉引用）
- `paper-compile` 需本地安装 `latexmk` 和完整 TeX 发行版（TeX Live / MiKTeX）

---

## 与 aigc-reduce 联动

写完论文后，可直接用 `aigc-reduce` 技能包降低 AIGC 检测率：

```
/aigc降低 paper/main.tex
```

详见 [`../aigc-reduce-skills/README.md`](../aigc-reduce-skills/README.md)
