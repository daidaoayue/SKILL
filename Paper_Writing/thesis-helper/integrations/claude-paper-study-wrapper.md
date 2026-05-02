# claude-paper:study Integration Wrapper

> **包装的 skill**：`claude-paper:study` (deep paper study with study materials)
> **触发**：精读关键文献（综述前 / SOTA 对比前）

## Input
```yaml
paper: <pdf_path | arxiv_id | url>
study_depth: shallow | deep
output_lang: zh | en
```

## Output
```text
<project>/.thesis-helper/study/<paper_id>/
├── reading_notes.md         # 章节级笔记 + 关键公式
├── key_concepts.md          # 核心概念词汇表
├── methodology_summary.md   # 方法论详解
├── results_critique.md      # 实验结果批判性分析
└── how_to_cite.md           # 在你论文中引用本文的最佳方式
```

## thesis-helper 调用条件

```text
config.integrations.claude_paper_study: true
   且 (
      paper-writing 阶段需要深度对比某 SOTA
      或 用户主动请求 "/精读 <paper>"
   )
```

## 触发流程

```text
1. arxiv-wrapper / semantic-scholar-wrapper 输出 top 5 高引论文
2. 自动 /claude-paper:study 每篇 → study/
3. methodology_summary 注入 paper-writing 的 "Method Comparison" section
4. results_critique 注入 "Limitations of Existing Work"
```

## 与 claude-paper:summary 的差异

```text
summary       1-2 段速读，知道这篇大致干啥
study         深读全文，含公式推导、实验细节、可引用材料
```

speed: summary 5min/paper, study 30-60min/paper（按需选）。

## 相关

- 同级：[`arxiv-wrapper.md`](arxiv-wrapper.md) [`research-lit-wrapper.md`](research-lit-wrapper.md)
- pipeline：journal / conference / master-thesis Phase 1（深度精读）
