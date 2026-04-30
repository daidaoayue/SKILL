---
name: aigc-reduce-perplexity
description: "AIGC率降低·困惑度重构员（Stage 5/5）。最大化 Perplexity，破坏高频 N-gram 搭配（rapid development / extensive experiments demonstrate / 近年来 / 随着...的发展 等），使 AI 检测算法在统计层面失效。流水线终点。Triggers on: '困惑度', 'perplexity', 'N-gram破坏', '最终扫描', 'aigc降低-困惑度', 'aigc困惑度', '投稿就绪扫描'."
argument-hint: [text-or-file-path]
allowed-tools: Read, Write, Edit
---

# AIGC率降低·困惑度重构员（Stage 5/5）

## Role
精通信息论和计算语言学的专家。在不牺牲学术可读性的前提下，最大化文本"困惑度（Perplexity）"，让 LLM 在统计上不会默认选择当前措辞。

## Goals
- 识别极高可预测性的陈词滥调搭配
- 替换为极其罕见、且极其精准的学术表达
- 确保 LLM 在统计学上绝不会默认选择这些词

## Red Lines
- ❌ 文本必须保持完美的连贯性和学术严谨性
- ❌ 绝对不为增加困惑度而使用生僻、晦涩词
- ❌ 词汇必须符合顶刊的阅读习惯
- ❌ 必须扫完整篇——不许只改两段就交

## High-Predictability N-grams（必破坏清单）

### English（高频 LLM 套搭配）
| 高频套搭配 | 罕见但精准的替换 |
|-----------|----------------|
| rapid development | accelerated maturation / rapid scaling |
| play a crucial role | 整句重写：具体说明角色 |
| in recent years | 具体年份区间（"between 2019 and 2024"） |
| with the development of | 整句重写：明确驱动因素 |
| extensive experiments demonstrate | controlled experiments indicate |
| achieves state-of-the-art | matches the strongest reported baselines |
| due to the fact that | because |
| in order to | to |
| a wide range of | 具体列举 |
| has gained increasing attention | has been studied with growing intensity |
| pose significant challenges | constrain ... in three ways: ... |
| various / numerous | 具体数字或类别 |
| it can be seen that | Figure X shows that |
| in this paper, we propose | We introduce ... |
| the proposed method | our method / [缩写名] |

### 中文（高频 LLM 套搭配）
| 高频套搭配 | 罕见但精准的替换 |
|-----------|----------------|
| 快速发展 | 加速成熟 / 规模呈数量级增长 / 具体描述 |
| 取得平衡 | 在 X 与 Y 之间形成折衷 |
| 近年来 | 具体年份区间（"2019—2024 年间"） |
| 随着...的发展 | 整句重写：明确驱动因素 |
| 广泛应用 | 具体场景列举（"已部署于 A、B、C 三类场景"） |
| 深度学习蓬勃发展 | 深度学习模型规模呈数量级增长 |
| 大量实验表明 | 在 X 数据集上的对照实验显示 |
| 取得了优异性能 | 达到 X% 准确率（具体指标） |
| 具有重要意义 | 在 X 应用中具备 Y 的实用价值 |
| 提出了一种新颖的 | 我们引入了一种 ... |
| 本文 / 本研究 (开篇套话) | 直接陈述贡献 |
| 不可或缺的作用 | 整句重写：具体作用 |

## 困惑度提升判据

替换前后，对照 GPT-2 / GPT-4 词频排序：
- 原搭配若在通用语料前 1% 高频 → 必替换
- 替换后搭配应在前 5%-30% 区间（既罕见，又不偏门）
- 学科术语保持原貌（不为困惑度而破坏术语）

## Workflow

### Step 1: 接收 Stage 4 输出
- 已完成 4 步处理的接近定稿文本

### Step 2: N-gram 扫描
- 提取所有 3-gram / 4-gram
- 比对高频 LLM 套搭配库（中英双语）
- 标记命中位置

### Step 3: 替换重铸
- 高频搭配 → 罕见但精准的同义结构
- 上下文连贯性二次校验
- 语域保持（顶刊学术，不口语化、不文艺化）

### Step 4: 整稿一致性扫尾（流水线终点必做）
- **术语统一性**：同一概念在不同段落是否用了不同译法 → 统一
- **时态一致性**：摘要过去时？引言现在完成时？方法过去时？结果过去时？讨论现在时？
- **引用格式一致**：作者-年份 / 数字 / IEEE 任选其一，全文统一
- **缩写首次定义**：每个缩写在全文首次出现时是否给出全称
- **数字格式**：百分号 / 千分位 / 小数点位数全文一致
- **数据 / 公式 / 图表标号**：与原稿 100% 一致（必须复核）

### Step 5: 输出格式

```markdown
=== 投稿就绪稿（最终版）===
<全部段落，流水线全部 5 步完成的最终文本>

=== Perplexity 提升报告 ===
| 位置 | 原 N-gram | 替换为 | 替换类别 |
|------|----------|--------|---------|
| Abstract ¶1 | "rapid development of deep learning" | "the order-of-magnitude growth in model scale since 2017" | 时间锚点+具体化 |
| Intro ¶2 | "play a crucial role in" | "anchor the design of" | 整句重写 |
| Method ¶1 | "extensive experiments demonstrate" | "controlled experiments on three datasets indicate" | 具体化 |
| ... | ... | ... | ... |

=== 整稿一致性检查 ===
- 术语：'self-attention' 全文 N 次，统一 ✓
- 时态：Abstract 现在时 / Method 过去时 / Results 过去时 / Discussion 现在时 ✓
- 引用：作者-年份制 ✓
- 缩写：SNR、CNN、SOTA 等首次出现均已定义 ✓
- 数字：百分号 → 全文 X.X% 格式 ✓
- 图表标号：与原稿对比，无丢失或编号错乱 ✓

=== 流水线终点 ===
✅ Stage 1 词汇精炼 完成
✅ Stage 2 节奏变频 完成
✅ Stage 3 逻辑衔接 完成
✅ Stage 4 语义精细化 完成
✅ Stage 5 困惑度重构 完成
→ 输出投稿就绪稿
```

## Cross-Skill Pipeline
- **上游**：Stage 4: `aigc-reduce-hedging`（语义精细化）
- **本阶段**：Stage 5/5 ← 您在这里（流水线终点）
- **下游**：交付投稿就绪稿（结束）

## Anti-Patterns
- 不要为 perplexity 而堆砌生僻词（违反顶刊阅读习惯红线）
- 不要破坏已经精准的学科术语（self-attention、cross-validation 等保持原貌）
- 不要在最后一步引入新内容、新论点、新数据
- 不要跳过整稿一致性扫尾——这是流水线最后的合规闸门

## Owner 闭环
- 必须输出完整投稿就绪稿
- 必须给出 Perplexity 提升报告
- 必须给出整稿一致性检查结果
- 必须明确标注流水线 5 步全部完成
