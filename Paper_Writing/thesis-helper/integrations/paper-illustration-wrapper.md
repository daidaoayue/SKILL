# paper-illustration Integration Wrapper

> **包装的 skill**：`/paper-illustration` (AI illustrations via Gemini image generation)
> **触发**：method 章节 hero figure / 方法论可视化 / 概念示意图

## Input
```yaml
description: <natural-language>
style: academic_clean | technical_diagram | conceptual_metaphor
aspect_ratio: 16:9 | 1:1 | 4:3
iterations: 3                # 迭代次数（Claude 监督优化）
```

## Output
```text
<project>/figures/illustration/
├── <name>_v1.png             # 初版
├── <name>_v2.png             # 改进版
├── <name>_final.png
└── prompt_log.md             # 完整 prompt 链（便于复现）
```

## thesis-helper 调用条件

```text
config.integrations.paper_illustration: true
   且 thesis_type ∈ {journal, conference, master-thesis}
   →  Phase 3 触发
```

## 触发流程

```text
1. 用户描述要画的图（"显示一个 radar 系统从信号到识别的端到端流程"）
2. /paper-illustration → Gemini 出图
3. Claude 监督审查（清晰度 / 学术风格 / 与论文契合）
4. 迭代 2-3 轮直到合格
5. 输出 final.png 注入 figures/
```

## 与 mermaid-diagram 的协作

```text
精确流程 → /mermaid-diagram (代码生成)
艺术示意 → /paper-illustration (AI 生成)
两者并存于 method 章
```

## 适用场景

- ✅ Hero figure（论文第一图，吸引眼球）
- ✅ 抽象概念可视化
- ✅ 系统对比图（your method vs SOTA）
- ❌ 精确架构图（用 mermaid）
- ❌ 数据图（用 scientific-visualization）

## 注意

AI 生图存在 hallucination 风险——重要技术细节务必人工校对。

## 相关

- 同级：[`mermaid-diagram-wrapper.md`](mermaid-diagram-wrapper.md) [`scientific-visualization-wrapper.md`](scientific-visualization-wrapper.md)
- pipeline：conference / master-thesis Phase 3
