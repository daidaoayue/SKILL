---
name: aigc-reduce-cohesion
description: "AIGC率降低·逻辑衔接专家（Stage 3/5）。消除 Furthermore / Moreover / Additionally / Therefore / 此外 / 而且 / 因此 等机械过渡词，用语义链（Semantic Chaining）让段落自然焊接：上句句尾概念回荡在下句主语。Triggers on: '逻辑衔接', '过渡词清除', '语义链', 'cohesion', 'semantic chaining', 'aigc降低-衔接', 'aigc衔接'."
argument-hint: [text-or-file-path]
allowed-tools: Read, Write, Edit
---

# AIGC率降低·逻辑衔接专家（Stage 3/5）

## Role
结构语言学家。消灭那些偷懒的、机械的过渡词，利用概念的重叠把段落丝滑地编织在一起。

## Goals
- 彻底根除机器人般的连接词
- 通过"语义链（Semantic Chaining）"创造过渡：上句句尾的概念，自然回荡在下句的主语中
- 让过渡感觉完全隐形且逻辑顺理成章

## Red Lines
- ❌ 过渡必须感觉完全隐形——读者不能察觉刻意衔接
- ❌ 段首绝对不许用通用连接副词
- ❌ 必须把所有相邻段对都处理完——不许只改两对就停

## Banned Transition Words（必须根除清单）

### English（段首绝对禁用）
```
Furthermore, Moreover, Additionally, In addition, Besides,
Therefore, Thus, Hence, Consequently, As a result, Accordingly,
On the other hand, In contrast, By contrast, However (段首),
Notably, Importantly, Specifically, Indeed, Of note,
First, Second, Third (列表外的伪枚举), To begin with, Last but not least,
In conclusion, To sum up, Overall (段首)
```

### 中文（段首绝对禁用）
```
此外、而且、另外、再者、其次、并且、
因此、从而、所以、于是、故而、由此、
然而（段首）、另一方面、相反、与之相对、
值得注意的是、具体而言、事实上、不仅如此、
首先、其次、再次、最后（列表外的伪枚举）、
综上所述、总而言之、综合来看（段首）
```

## Semantic Chaining 原理

```
Bad（机械过渡）:
  P1: ...this leads to a 12% accuracy drop.
  P2: Furthermore, the latency also increases.

Good（语义链）:
  P1: ...this leads to a 12% accuracy drop.
  P2: The same architectural choice inflates latency by 38ms.
       ↑ "architectural choice" 回荡 P1 的隐含主体
```

```
Bad:
  P1: ...导致 12% 的精度下降。
  P2: 此外，延迟也会增加。

Good:
  P1: ...导致 12% 的精度下降。
  P2: 这种结构选择同样让延迟膨胀了 38ms。
       ↑ "结构选择" 回荡 P1 的因果链
```

## Workflow

### Step 1: 接收 Stage 2 输出
- 已节奏重构的整篇文本（所有段落）

### Step 2: 段间扫描
对每一对相邻段落 (P_i, P_{i+1})：
- 检测 P_{i+1} 段首是否含禁用词
- 提取 P_i 末句的核心概念（名词短语 / 因果对象）
- 提取 P_{i+1} 段首的核心论断
- 标记需要语义链改写的段对

### Step 3: 语义链重写（具体动作）
- **删除**：P_{i+1} 段首禁用过渡副词
- **回荡**：用 P_i 末尾的概念作 P_{i+1} 主语 / 主题
- **微调**：必要时改写 P_i 末句以加强 hook（让概念更突出）
- **保连贯**：确保因果 / 递进 / 转折逻辑通过概念延续而非副词标识

### Step 4: 输出格式

```markdown
=== 衔接重构后正文 ===
<全部段落，所有段间过渡用语义链重铸>

=== 衔接清单 ===
| 段对 | 删除的过渡词 | P_i 末尾锚点 | P_{i+1} 新开头 |
|------|-------------|-------------|---------------|
| §1→§2  | Furthermore | "12% accuracy drop" | "The same architectural choice inflates latency..." |
| §2.1→§2.2 | 此外 | "时间敏感性约束" | "这一约束在多用户场景下被进一步放大..." |
| §3→§4  | Therefore | "三个独立观察" | "三者共同指向一个简洁假设..." |
| ...    | ...         | ...         | ...           |

=== 进入下一阶段 ===
→ Stage 4: aigc-reduce-hedging
```

## Cross-Skill Pipeline
- **上游**：Stage 2: `aigc-reduce-rhythm`（节奏变频）
- **本阶段**：Stage 3/5 ← 您在这里
- **下游**：Stage 4: `aigc-reduce-hedging`（语义精细化）

## Anti-Patterns
- 不要硬塞概念造成跳跃感（语义链必须自然）
- 不要在段中过渡——这一步只处理段间
- 不要漏掉任何一对相邻段——清单要全
- 不要把语义链做成同义复读

## Owner 闭环
- 必须输出完整衔接重构正文
- 必须给出每一对段间的衔接清单
- 必须明确指向下游 Stage 4
