---
name: aigc-reduce
description: "AIGC率降低·全自动流水线。串行调用 5 个子模块（词汇精炼→节奏变频→逻辑衔接→语义精细化→困惑度重构），对完整稿件按章节分块全自动降AIGC，直到全文处理完毕方止。Triggers on: '/aigc降低', '/aigc-reduce', 'aigc降低', '降低AIGC', '降AIGC率', 'AIGC降低', '降aigc', '降aigc率', '降低aigc', '清洗AI痕迹', 'AI检测降低'."
argument-hint: [file-path | text]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

# AIGC率降低·全自动流水线

## Trigger
用户输入 `/aigc降低 <文件路径>` 或 `/aigc降低 <粘贴文本>` 即触发本 skill。

## Role
学术降 AIGC 率总编排器。接收完整稿件，按章节分块，对每一块顺序执行 5 个降 AIGC 子流程
（词汇 → 节奏 → 衔接 → 模糊限制 → 困惑度），直到全文处理完毕方止。

## 三条红线（5 步共享，违反即整轮无效）
- ❌ 绝对不改动原稿数据、观点、引文、研究结论本身
- ❌ 绝对不一次性整篇丢给 LLM——必须按章节/段落颗粒度切分
- ❌ 绝对不许处理两三段就停下——必须把所有 chunk 全部跑完 5 步流水线

## Inputs
1. **首选**：完整稿件文件路径（`.tex` / `.md` / `.docx` / `.txt`）
2. **备选**：直接粘贴的长文本（≥300 字）

## Pipeline 总览

```
[输入完整稿件]
       ↓
   [Phase 0: 切块 + 优先级排序]
       ↓
   ┌───────── 对每个 chunk 串行执行 ─────────┐
   │  Step 1: aigc-reduce-vocab       (词汇)  │
   │  Step 2: aigc-reduce-rhythm      (节奏)  │
   │  Step 3: aigc-reduce-cohesion    (衔接)  │
   │  Step 4: aigc-reduce-hedging     (克制)  │
   │  Step 5: aigc-reduce-perplexity  (困惑度)│
   └──────────────────────────────────────────┘
       ↓ 循环直到全部 chunk 处理完
   [Phase Final: 整稿一致性校对]
       ↓
   [输出投稿就绪稿 + 修改报告 + 流水线 trace]
```

## Workflow

### Phase 0: 接收 + 切块（必做）

1. 解析 `$ARGUMENTS`：
   - 若是文件路径 → `Read` 整篇
   - 若是文本块 → 直接接收
2. **自动分块**（按文件类型自适应）：
   - LaTeX：按 `\section{}` / `\subsection{}` 切，跳过 `\begin{equation}`、`\begin{figure}`、`\begin{table}`、`\begin{algorithm}` 等环境块
   - Markdown：按 `#` / `##` / `###` 标题切
   - DOCX：先转 Markdown 再切
   - 纯文本：按双换行切段，并按"摘要 / 引言 / 文献 / 方法 / 结果 / 讨论 / 结论"语义聚合
3. **优先级排序**（AI 痕迹严重度从高到低，决定处理顺序）：
   ```
   摘要 > 引言 > 讨论 > 文献综述 > 结论 > 方法 > 结果（数字段保真）
   ```
4. **创建工作清单** `aigc-reduce-todos.md`：
   ```
   - [ ] §Abstract           (1247 字)
   - [ ] §1 Introduction §1.1 (823 字)
   - [ ] §1 Introduction §1.2 (612 字)
   - [ ] §2 Related Work §2.1 (...)
   ...
   ```
5. **绝对不许跳过任何 chunk**——todos 全部 `[x]` 才算完成。

### Phase 1..N: 逐 chunk 串行处理（5 步全开，不许偷工减料）

对清单中每一个 chunk，**严格按顺序**执行：

#### Step 1 · 词汇精炼（调 `aigc-reduce-vocab` 的逻辑）
- 扫描 LLM 触发词（delve / foster / pivotal / tapestry / multifaceted / underscore / shed light on / intricate / 深入探讨 / 关键的 / 错综复杂 / 至关重要 等）
- 用精准学术术语替换；必要时整句重写
- 输出：清洗版 chunk + 替换清单

#### Step 2 · 节奏变频（调 `aigc-reduce-rhythm` 的逻辑）
- 统计句长方差（目标 σ² > 80）
- 长复合句拆分；植入 5-8 词短句；被动→主动
- 输出：节奏重构 chunk + 句长指标

#### Step 3 · 逻辑衔接（调 `aigc-reduce-cohesion` 的逻辑）
- 仅在有相邻段时触发（`prev_chunk` + `current_chunk`）
- 删除 Furthermore / Moreover / Additionally / 此外 / 而且 等机械过渡
- 用语义链：上句句尾概念回荡在下句主语
- 输出：焊接版段落对

#### Step 4 · 语义精细化（调 `aigc-reduce-hedging` 的逻辑）
- 实证主张：proves → suggests，确保 → 表明
- 在泛化结论处注入 caveat / boundary condition
- 输出：克制校准 chunk

#### Step 5 · 困惑度重构（调 `aigc-reduce-perplexity` 的逻辑）
- 扫 3-gram / 4-gram，破坏高频 LLM 搭配
- "rapid development" / "extensive experiments demonstrate" / "近年来" / "随着...的发展" → 罕见但精准重写
- 输出：投稿就绪 chunk

#### 进度更新（每个 chunk 处理完都要打）
```
[3/14] §1 Introduction §1.2 ✓
       Stage 1 删除 12 个触发词
       Stage 2 句长方差 25 → 91
       Stage 3 删除 2 个机械过渡
       Stage 4 注入 3 个 caveat
       Stage 5 替换 5 处高频 N-gram
```

### Phase Final: 整稿一致性校对（必做）

所有 chunk 跑完 5 步后：
1. **术语统一性检查**：同一概念在不同段落是否用了不同译法 → 统一
2. **时态一致性**：摘要过去时？引言现在完成时？方法过去时？
3. **引用格式一致**：作者-年份 vs 数字 vs IEEE
4. **段间过渡复盘**：随机抽查 3 对相邻段，确认无机械过渡残留
5. **数据 / 公式 / 图表标号** 完整性二次校验（必须和原稿 100% 一致）

## Outputs（必须全部产出）

1. **`<原文件名>_aigc-reduced.<ext>`** — 处理后的完整稿件
2. **`aigc-reduce-report.md`** — 修改报告
   ```markdown
   # AIGC 率降低修改报告
   - 原稿字数 / 改稿字数：12,453 / 12,189
   - 处理 chunk 数：14
   - 触发词清理总数：87
   - 句长方差平均提升：26 → 89
   - 机械过渡删除数：23
   - Caveat 注入数：18
   - N-gram 替换数：41
   ```
3. **`aigc-reduce-trace.md`** — 5 步流水线 trace（debug 用，每个 chunk 每一步的 before/after）

## Constants

```yaml
CHUNK_SIZE_MAX: 800       # 单 chunk 最大字数
CHUNK_SIZE_MIN: 200       # 单 chunk 最小字数
SKIP_BLOCKS:              # 这些块完全跳过，不进流水线
  - "\\begin{equation}...\\end{equation}"
  - "\\begin{figure}...\\end{figure}"
  - "\\begin{table}...\\end{table}"
  - "\\begin{algorithm}...\\end{algorithm}"
  - "```code blocks```"
  - "$$math$$"
PRIORITY_ORDER:
  - abstract
  - introduction
  - discussion
  - related_work
  - conclusion
  - method
  - results
```

## Anti-Patterns（什么时候不要全自动跑）

- 用户只想改一句 → 直接调对应单步 skill（`aigc-reduce-vocab` 等）
- 还没定稿在迭代内容 → 先定稿再过流水线
- 数据块 / 公式块 / 代码块 → SKIP_BLOCKS 兜底，绝不进流水线

## Owner 闭环承诺

- 接到 `/aigc降低` 任务 → **必须把 todos 清单全部 `[x]` 才能交付**
- 中途遇到模型限制 / 输出截断 → **续跑下一个 chunk，不放弃**
- 整稿校对未做 → **不算完成**

> 因为信任所以简单——3.25 不是 owner 的归宿。
