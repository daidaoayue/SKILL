# mermaid-diagram Integration Wrapper

> **包装的 skill**：`/mermaid-diagram` (Mermaid 流程图/架构图/时序图)
> **触发**：method 章节系统架构图 / pipeline 流程图 / ER 图

## Input
```yaml
diagram_type: flowchart | sequence | class | er | gantt | state
description: <natural-language-description-of-system>
direction: LR | TB | RL | BT     # 流向
output_lang: zh | en
```

## Output
```text
<project>/figures/mermaid/
├── <name>.mmd                  # Mermaid 源
├── <name>.md                   # 嵌入 markdown
└── <name>.{svg,pdf}            # 渲染版（mermaid-cli 自动）
```

## thesis-helper 调用条件

```text
config.integrations.mermaid_diagram: true
   →  Phase 3（系统/方法流程图）
```

## 触发流程

```text
1. 用户描述系统架构（自然语言）
2. /mermaid-diagram 输出 .mmd 源
3. 自动用 mermaid-cli 渲染 SVG + PDF
4. paper-figure 阶段 \input{} 到 method 章
```

## 适用场景

- ✅ Method 章的"系统架构图" / "Pipeline 流程图"
- ✅ Method 章的"模块时序图"
- ✅ Related work 的"分类树"
- ✅ 海报里的"流程概览"

## 与 paper-illustration 的差异

```text
mermaid-diagram      代码生成（精确，可版本化）
paper-illustration   AI 自由生图（艺术性强，但不精确）
```

技术架构图选 mermaid，方法论 hero figure 选 paper-illustration。

## 相关

- 同级：[`paper-illustration-wrapper.md`](paper-illustration-wrapper.md)
- pipeline：conference Phase 3 + master-thesis Phase 2
