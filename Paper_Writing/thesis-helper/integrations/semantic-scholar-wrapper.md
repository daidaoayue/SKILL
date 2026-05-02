# semantic-scholar Integration Wrapper

> **包装的 skill**：`/semantic-scholar` (search published venue papers via Semantic Scholar API)
> **触发**：选题 / 文献综述 / related work / SOTA 对比

## Input
```yaml
query: <keywords>
venue_filter: ["IEEE", "ACM", "Springer"]    # 可选
year_range: <e.g. 2022-2026>
min_citations: 10                              # 排除低引论文
max_results: 30
```

## Output
```text
<project>/.thesis-helper/lit/semantic-scholar/
├── results.md               # 含 citation_count / venue / TLDR
├── results.bib              # 已格式化 BibTeX
└── citation_graph.json      # （可选）引用关系
```

## thesis-helper 调用条件

```text
config.integrations.semantic_scholar: true
   且
thesis_type ∈ {journal, conference, master-thesis}
   →  Phase 1 触发
```

## 触发流程

```text
1. /semantic-scholar search <topic> --venue IEEE --year 2023-2026 --min-cite 10
2. 解析结果，含 TLDR (one-line summary)
3. 自动转 BibTeX 写入 results.bib
4. 高引论文（>100 cite）→ /claude-paper:study 深度精读
5. 输出注入 paper-writing 的 references 阶段
```

## 与 arxiv 的协作

```text
union(arxiv, semantic_scholar)
   去重（按 DOI / title 模糊匹配）
   排序（cite count desc, date desc）
   输出统一 lit_pool.md
```

## 限制

- Semantic Scholar API 有 rate limit（100 req/5min），大批量查询要 throttle
- TLDR 字段不一定每篇都有

## 相关

- 同级：[`arxiv-wrapper.md`](arxiv-wrapper.md) [`research-lit-wrapper.md`](research-lit-wrapper.md)
- pipeline：journal / conference / master-thesis pipeline 的 Phase 1
