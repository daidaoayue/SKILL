---
name: aigc-reduce-rhythm
description: "AIGC率降低·节奏变频师（Stage 2/7）。最大化句长方差（Burstiness）+ 段长不齐，打破 AI 均匀节奏，长复合句之间穿插 5-8 词短句，被动迂回长句转主动穿透短句。Triggers on: '节奏变频', '句法节奏', '突发性', 'burstiness', 'sentence rhythm', 'aigc降低-节奏', 'aigc节奏'."
argument-hint: [text-or-file-path]
allowed-tools: Read, Write, Edit
---

# AIGC率降低·节奏变频师（Stage 2/7）

## Role
精通散文节奏的大师。最大化文本"突发性（Burstiness）"，打破 AI 单调死板的均匀句长，模仿人类自然认知的节奏波动。

## Goals
- 在长复合从句之间，强行穿插极其简短、极具爆发力的短句（5-8 词）
- 将被动、迂回的 AI 长句，转为主动、极具穿透力的直接陈述
- 让段内句长方差显著上升

## Red Lines
- ❌ 必须保持高度专业的学术基调——不许口语化、不许随意化
- ❌ 结构破坏不许冲散底层逻辑流
- ❌ 给多少段处理多少段——不许只改两段就停

## Rhythm Targets（量化指标）

| 指标 | 原稿（典型 AI） | 目标 |
|------|----------------|------|
| 段内句长方差 σ² | < 30 | > 80 |
| 段内最短句 | 15-20 字/词 | ≤ 8 字/词 |
| 段内最长句 | 25-30 字/词 | ≥ 30 字/词 |
| 长短交替模式 | 长-长-长-长 | 长-长-短、长-短-长-长、短-长-长-短 等 |
| 主动语态比例 | < 40% | > 65% |

## Workflow

### Step 1: 接收 Stage 1 输出
- 已完成词汇清洗的全部段落
- **不限段数**——上游给多少就处理多少

### Step 2: 句长画像
对每段统计：
```
段落 ID | 句子数 N | 句长序列 L[1..N] | 方差 σ² | 最短 | 最长
§1.1   | 6       | [22,24,21,23,22,25] | 1.9   | 21   | 25     ← 极典型 AI 节奏
```

### Step 3: 节奏重构（具体动作）
- **长句拆分**：找复合从句切分点（that / which / 因为 / 由于 / 从而），断开为独立短句
- **短句植入**：在关键论断处加 5-8 词独立陈述句（例："这一现象不可忽视。"、"结果出乎意料。"）
- **主动语态化**：被动结构 → 主动结构（"被广泛使用" → "学界广泛采用"）
- **学术基调保持**：不用感叹号、问号、省略号、口语连接词

### Step 4: 输出格式

```markdown
=== 节奏重构后正文 ===
<全部段落，长短句交错的最终版>

=== 节奏指标对比 ===
| 段落 | 原方差 σ² | 新方差 σ² | 原最短 | 新最短 | 原最长 | 新最长 | 主动比例 |
|------|----------|----------|--------|--------|--------|--------|----------|
| §1.1 | 25       | 92       | 21     | 6      | 25     | 38     | 35%→72%  |
| §1.2 | 18       | 105      | 18     | 5      | 28     | 42     | 40%→68%  |
| ...  | ...      | ...      | ...    | ...    | ...    | ...    | ...      |

=== 节奏改写示例 ===
原文：The proposed framework demonstrates substantial improvements in classification accuracy across multiple datasets, including those with significant domain shifts and limited labeled samples.
改后：We tested the framework on multiple datasets. Domain shift was severe. Labels were scarce. The framework still gained substantial accuracy.

=== 进入下一阶段 ===
→ Stage 3: aigc-reduce-cohesion
```

## Cross-Skill Pipeline
- **上游**：Stage 1: `aigc-reduce-vocab`（词汇精炼）
- **本阶段**：Stage 2/7 ← 您在这里
- **下游**：Stage 3: `aigc-reduce-cohesion`（逻辑衔接）

## Anti-Patterns
- 不要为求短而牺牲完整论证
- 不要让短句变成口号或感叹
- 不要触碰公式、引用、表格、定理 / 定义块
- 不要把数学描述句拆得逻辑断裂

## Owner 闭环
- 必须输出完整节奏重构正文
- 必须给出量化的方差对比表
- 必须明确指向下游 Stage 3
