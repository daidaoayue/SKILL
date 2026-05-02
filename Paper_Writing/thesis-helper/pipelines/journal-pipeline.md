# Journal Pipeline · 期刊论文端到端流程

> 触发条件：`thesis.config.yml` 中 `thesis_type: journal`
> 默认目标：IEEE / Springer / Elsevier 期刊投稿就绪
> 默认交付：投稿包（PDF + LaTeX 源 + 出版级图表 + cover letter + 自审报告）
> 跳过：AIGC 降痕（期刊不查 CNKI）

## Pipeline 总览

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 0  · 项目扫描 + config 读取                                     │
│ Phase 1  · 文献综述 + novelty check（前置）                           │
│ Phase 2  · 论文写作 (paper-writing 全流程，期刊模板)                  │
│ Phase 3  · 出版级图表升级 (scientific-visualization)                 │
│ Phase 4  · 公式推导整理 (formula-derivation / proof-writer)          │
│ Phase 5  · 自审 (paper_reviewer 多角色)                              │
│ Phase 6  · Cover Letter + Highlight 生成                            │
│ Phase 7  · 闭环验证 + 投稿包                                          │
│ Phase 8  · (投稿后) Rebuttal 处理审稿意见                             │
└─────────────────────────────────────────────────────────────────────┘
```

## Phase 0 · 项目扫描

```bash
python scanners/project-scanner.py <project_root>
```

读 `thesis.config.yml`，确认：

```yaml
thesis_type: journal
venue: IEEE_JOURNAL              # 或 NeurIPS / ACL / IEEE_TPAMI 等
language: en                     # 期刊默认英文
detector: none                   # 跳过 CNKI
```

## Phase 1 · 文献综述 + novelty check

触发：`pipeline.lit_review: true` + `pipeline.novelty_check: true`

```text
language=en → /research-lit
领域专业（通信/雷达）→ + /comm-lit-review
投稿前 → /novelty-check 验证 idea 新颖性（避免 desk reject）
```

输出：`<project>/.thesis-helper/lit_review.md` + `novelty_check_report.md`

## Phase 2 · 论文写作

调用 `/paper-writing <NARRATIVE_REPORT.md>`，参数：

```yaml
venue: <config.venue>            # IEEE_JOURNAL / NeurIPS / ...
language: en
template: <project_map.format_rules>   # 期刊 .cls 模板
page_limit: <school_rules.page_count_max>
references_count_in_pages: <true/false>
auto_proceed: true               # 期刊全自动跑通
improvement_rounds: 2            # 自审改进 2 轮
```

输出：

```text
<project>/paper/main.tex
<project>/paper/sections/*.tex
<project>/paper/main.pdf
<project>/paper/references.bib
```

## Phase 3 · 出版级图表升级

调用 `/scientific-visualization` —— 期刊投稿要求 vector PDF + colorblind-safe：

```yaml
input: <project>/figures/*
target_format: pdf                # vector for journal
colorblind_safe: true
font: serif                       # 与正文字体一致
output: <project>/figures/journal/
update_includes: true             # 自动更新 figures/latex_includes.tex
```

可选 `/matplotlib-tvhahn` 用 Tim Hahn 风格（whitegrid + cubehelix）。

## Phase 4 · 公式推导整理

仅当 paper 含理论章（>5 个 equation）：

```text
/formula-derivation → 整理推导链 + 验证假设
/proof-writer       → 补全证明步骤（如有 theorem/lemma）
```

输出注入到 `paper/sections/method.tex`。

## Phase 5 · 自审

调用 `/paper_reviewer <project>/paper/main.pdf` —— 5 维度审稿人模拟：

```text
Soundness    方法严谨性
Significance 研究意义
Novelty      新颖性
Clarity      表述清晰度
Reproducibility 可复现性
```

输出：`<project>/paper/review_self.md`

如有 CRITICAL → 暂停 pipeline，提示用户修改后再继续。

## Phase 6 · Cover Letter + Highlight

```text
基于 paper 内容自动生成：
1. cover_letter.md
   - 论文一句话价值
   - 创新点 3-5 条
   - 与 venue scope 的契合度论述
   - 推荐审稿人 (suggested reviewers)
2. highlights.md (Elsevier 期刊需要)
   - 4-5 条 bullet，每条 ≤ 85 字符
3. graphical_abstract_brief.md (推荐做)
   - 一图概括论文，提供 mermaid 草图
```

输出：`<project>/submission/`

## Phase 7 · 闭环验证 + 投稿包

```yaml
✅ 交付清单
├── <project>/paper/main.pdf                     # 论文 PDF
├── <project>/paper/main.tex + sections/         # LaTeX 源
├── <project>/paper/references.bib
├── <project>/figures/journal/*                  # 出版级图表
├── <project>/paper/review_self.md               # 自审报告
├── <project>/submission/cover_letter.md
├── <project>/submission/highlights.md
└── <project>/submission/suggested_reviewers.md

📊 验证数据
├── 页数：[N] / 限制 [M]                ← 必须 ≤ 限制
├── 字数：英文 [N] words
├── 图表数：[N] (vector/colorblind ✓)
├── 引用条数：[N]
└── 自审分数：[X/10]                    ← 推荐 ≥ 7
```

## Phase 8 · Rebuttal（投稿后触发）

收到审稿意见后，调用 `/rebuttal`：

```yaml
input: 审稿意见 PDF / Markdown
output: <project>/rebuttal/
  - response_to_reviewer1.md
  - response_to_reviewer2.md
  - response_to_editor.md
  - revised_paper_diff.md (修改追踪)
```

详见 [`../integrations/rebuttal-wrapper.md`](../integrations/rebuttal-wrapper.md)。

## Owner 闭环承诺

- ❌ Phase 5 自审分数 < 7 → 必须修到 ≥ 7 再交付
- ❌ 页数超限 → 必须列出可压缩段落
- ❌ Cover letter 缺失 → 不算完成
- ❌ Vector 图表缺失 → 期刊编辑会打回

> 因为信任所以简单——期刊 desk reject 大多输在 cover letter 和图表，本 pipeline 把这些坑全填了。
