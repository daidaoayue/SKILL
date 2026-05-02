# research-lit Integration Wrapper

> **包装的 skill**：`/research-lit` (general research paper search + analysis)
> **触发**：通用文献综述（任何领域）

## Input
```yaml
topic: <research-direction>
seed_papers: <list-from-arxiv-or-semantic-scholar>     # 可选种子
depth: shallow | medium | deep                         # 综述深度
output_format: bib_only | summary | full_review
```

## Output
```text
<project>/.thesis-helper/lit/research-lit/
├── related_work_draft.md       # 可直接注入 sections/related_work.tex
├── citation_pool.bib           # 整合后 BibTeX
└── gap_analysis.md             # 现有工作的 gap → 你的 contribution 立足点
```

## thesis-helper 调用条件

```text
config.integrations.research_lit: true
config.pipeline.lit_review: true
   且 language=en（中文用 comm-lit-review）
   →  Phase 1 触发
```

## 触发流程

```text
1. 收集种子（来自 arxiv-wrapper / semantic-scholar-wrapper 输出）
2. /research-lit topic=<...> --depth medium --seed <list>
3. AI 自动按主题聚类 / 时间线 / 方法分类
4. 输出 related_work_draft.md
5. gap_analysis.md 给 paper-plan 阶段用作 motivation
```

## 与 comm-lit-review 的差异

```text
research-lit       通用，覆盖所有学科
comm-lit-review    专攻通信/无线/雷达/卫星/Wi-Fi/cellular
```

中文工科毕设用 `comm-lit-review`，跨学科或英文期刊用 `research-lit`。

## 相关

- 同级：[`comm-lit-review-wrapper.md`](comm-lit-review-wrapper.md)
- pipeline：所有 4 类型 Phase 1
