# arxiv Integration Wrapper

> **包装的 skill**：`/arxiv` (search/download/summarize arXiv papers)
> **触发**：选题阶段 / 文献综述前 / 写 related work 章节

## Input
```yaml
mode: search | download | summarize
query: <user-keywords>
year_range: <e.g. 2023-2026>
max_results: 20
```

## Output
```text
<project>/.thesis-helper/lit/arxiv/
├── search_results.md              # 排序后的论文清单
├── papers/<arxiv_id>.pdf          # 已下载 PDF
└── summaries/<arxiv_id>.md        # /claude-paper:summary 输出
```

## thesis-helper 调用条件

```text
config.integrations.arxiv: true
   且
config.pipeline.lit_review: true 或 thesis_type ∈ {journal, conference, master-thesis}
   →  Phase 1 触发
```

调用前置：先读 `<project>/NARRATIVE_REPORT.md` 提取主关键词，
若无 → 用 `config.narrative.topic` 字段。

## 触发流程

```text
1. /arxiv search "radar target recognition" --year 2024-2026 --max 20
2. 解析结果，按引用数 + 时间排序，取 top 10
3. 自动 /arxiv download top 5 → PDF 落到 .thesis-helper/lit/arxiv/papers/
4. (可选) /claude-paper:summary 每篇 → summaries/
5. 输出文献清单注入 /research-lit 作为种子
```

## 与 semantic-scholar 的分工

```text
arxiv             →  最新 preprint（可能未审稿）
semantic-scholar  →  已发表期刊/会议（IEEE/ACM/Springer）
两者并行使用，去重后合并
```

## 相关

- 同级：[`semantic-scholar-wrapper.md`](semantic-scholar-wrapper.md) [`research-lit-wrapper.md`](research-lit-wrapper.md)
- pipeline：所有 4 类型 pipeline 的 Phase 1
