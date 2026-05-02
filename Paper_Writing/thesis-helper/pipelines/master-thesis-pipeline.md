# Master Thesis Pipeline · 硕士毕设端到端流程

> 触发条件：`thesis.config.yml` 中 `thesis_type: master-thesis`
> 严格阈值：AIGC ≤ 5% / 查重 ≤ 5%（比本科严）
> 默认交付：8 件套（PDF + Word + 盲审版 + AIGC 报告 + CNKI 记录 + 答辩 + 格式 + 摘要）
> 与本科毕设差异：**+ 盲审版（thesis-blind-review）+ 严格阈值 + 答辩节奏更长**

## Pipeline 总览

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 0  · 项目扫描 + config 读取                                     │
│ Phase 1  · 文献综述（前置）                                            │
│ Phase 2  · 论文写作 (paper-writing 全流程)                            │
│ Phase 3  · 公式推导整理 (formula-derivation / proof-writer)          │
│ Phase 4  · 自审 (paper_reviewer)                                     │
│ Phase 5  · AIGC 降痕 + CNKI 验证（严格阈值）                          │
│ Phase 6  · LaTeX → Word (latex-to-word)                            │
│ Phase 7  · 中英摘要 (bilingual-abstract) + 格式 (format-checker)     │
│ Phase 8  · 盲审版生成 (thesis-blind-review) ⭐ 硕士专属                │
│ Phase 9  · 答辩准备 (thesis-defense-prep) — 25-30 分钟版               │
│ Phase 10 · 闭环验证 + 交付                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## 与本科毕设差异详表

| 维度 | undergrad-thesis | master-thesis |
|------|:---------------:|:-------------:|
| AIGC 阈值 | 8% | **5%** |
| 查重阈值 | 8% | **5%** |
| 字数下限 | 30000 | **50000** |
| 字数上限 | 80000 | **150000** |
| 摘要字数（中） | 300-600 | **500-1000** |
| 摘要字数（英） | 200-350 | **350-600** |
| 公式推导整理 | 选 | **必** |
| 盲审版 | ✗ | **✓** |
| 答辩时长 | 15 分钟 | **25-30 分钟** |
| 致谢节专项 | 必 | 必 |

## Phase 0 · 项目扫描

```yaml
thesis_type: master-thesis
venue: 清华大学                    # 或北航/北大/...
language: zh
detector: CNKI
targets:
  aigc_rate_max: 5
  duplicate_rate_max: 5
  word_count_min: 50000
  word_count_max: 150000
school_rules:
  tsinghua_master:
    aigc_rate_max: 5
    duplicate_rate_max: 5
    require_blind_review: true
identity:                          # 盲审版需要
  author_name: "张三"
  advisor_name: "李四教授"
  school: "清华大学"
  lab_keywords: ["XX 实验室"]
```

## Phase 1 · 文献综述（前置）

硕士毕设文献综述章通常较长（本身一章 5-10k 字）。

```text
language=zh + 工科 → /comm-lit-review
其他              → /research-lit
+ /semantic-scholar 抓 IEEE/Springer/Elsevier 已发表
+ /arxiv 抓最新 preprint
```

输出注入到 `paper/sections/related_work.tex`。

## Phase 2 · 论文写作

调用 `/paper-writing`，硕士毕设特化：

```yaml
venue: <school>                   # 学校 LaTeX 模板
language: zh
template: <project_map.format_rules>
chapter_min_count: 5              # 硕士通常 5-7 章
chapter_min_words: 8000           # 每章下限
auto_proceed: true
improvement_rounds: 3             # 比本科多 1 轮
```

## Phase 3 · 公式推导整理

硕士理论章必备：

```text
/formula-derivation → 公式推导链整理
/proof-writer       → theorem/lemma 完整证明
```

注入到 `paper/sections/theory.tex`。

## Phase 4 · 自审

调用 `/paper_reviewer`，硕士专项审查：

```text
+ 文献综述充分性
+ 创新点 vs 工作量平衡
+ 实验设计完整性（含 ablation）
+ 答辩问答可能问题预测
```

## Phase 5 · AIGC 降痕（严格阈值）

调用 `/aigc降低 paper/main.tex`，严格目标：

```yaml
target:
  aigc_rate_max: 5                # 比本科严
  duplicate_rate_max: 5
strict_mode: true
mandatory_cnki_validation: true   # 必须 CNKI 真实验证
acknowledgement_special_treatment: true   # 致谢节 v3 专项
thought_trace_per_chapter: 3      # 比本科多 1 处
```

如本地检测后 ai_prob > 5% → 自动 round 2 处理。

## Phase 6 · LaTeX → Word

调用 `/latex-to-word`：

```yaml
template_school_docx: <项目>/格式要求/清华硕士.docx
output: paper/main.docx
```

## Phase 7 · 摘要 + 格式

并行：

```text
/bilingual-abstract paper/main.tex
   阈值：中 500-1000 / 英 350-600
   术语一致性：必查（5+ 个核心术语）

/format-compliance-checker paper/main.tex
   学校规范：tsinghua_master.yml
   GB/T 7714-2015 引用格式
```

## Phase 8 · 盲审版生成（硕士专属）⭐

调用 `/thesis-blind-review`：

```yaml
input:
  paper_dir: paper/
  identity: <config.identity>
output:
  paper_blind/main.tex
  paper_blind/main.pdf            # 已清 PDF metadata
  paper_blind/blind_review_report.md
  paper_blind/blind_review_manual_check.md   # 校徽/合影需人工
```

⚠️ 强制：`identity` 字段必填，否则报错暂停。

## Phase 9 · 答辩准备（25-30 分钟版）

调用 `/thesis-defense-prep`：

```yaml
duration_min: 25                  # 硕士答辩通常 20-30 分钟
emphasis:
  - 工作量与创新点平衡           # 硕士最常被问
  - 实验充分性
  - 应用价值
backup_slides_count: 8            # 比本科多
qa_critical_min: 8                # ⚠️⚠️⚠️ 必问 ≥ 8 题
```

## Phase 10 · 闭环验证 + 交付

```yaml
✅ 8 件套交付清单
├── paper/main.pdf                              # 论文 PDF
├── paper/main.docx                             # Word 版（学校上传）
├── paper_blind/main.pdf                        # 盲审版 PDF ⭐
├── paper_blind/main.docx                       # 盲审版 Word
├── paper/aigc-reduce-report.md                 # AIGC 降痕详报
├── paper/cnki-aigc-round*.md                   # CNKI 验证记录
├── paper/abstract_check_report.md              # 中英摘要
├── paper/format_check_report.md                # 格式合规
├── defense/slides.pdf + .pptx                  # 答辩 PPT
└── defense/qa_simulation.md                    # 答辩问答模拟

📊 严格验证数据
├── 字数：[N] / 区间 [50k-150k]
├── AIGC 率：本地 [X]% / CNKI [Y]% / 阈值 5%   ← CNKI 终审
├── 查重率：本地 [X]% / 阈值 5%
├── 盲审版验证：自引 0 / 项目编号 0 / 实验室 0
├── 格式合规：[N]/[N] 项
├── 摘要术语一致性：[N]/[N] 项
└── 答辩问答：[N] 题（含 ≥8 题 ⚠️⚠️⚠️）
```

## Owner 闭环承诺

- ❌ Phase 5 CNKI 实测 > 5% → 不算完成（必须 round 2）
- ❌ Phase 8 自引/项目编号未清 0 → 盲审撤稿，必须 100% 清
- ❌ Phase 9 答辩 PPT 时长不在 25-30 min → 重做
- ❌ identity 字段缺失 → 不能进 Phase 8

> 因为信任所以简单——硕士毕设是三年的总结，每个细节都要 owner 闭环，不让导师/评委/盲审挑刺。
