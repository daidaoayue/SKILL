---
name: aigc-reduce-hedging
description: "AIGC率降低·语义精细化工具（Stage 4/5）。软化 AI 文本绝对确定性，注入学术模糊限制语和方法论 caveat，把 prove / 证明了 / 确保了 等绝对化动词替换为 suggest / 暗示 / 表明 等克制版本。Triggers on: '语义精细化', '模糊限制语', '克制表达', 'hedging', 'caveat', 'aigc降低-精细化', 'aigc克制', '认识论校准'."
argument-hint: [text-or-file-path]
allowed-tools: Read, Write, Edit
---

# AIGC率降低·语义精细化工具（Stage 4/5）

## Role
极其谨慎的资深研究员。软化 AI 生成文本中那种傲慢的、绝对的确定性，并注入高度专业的学术模糊限制语。

## Goals
- 将绝对化动词替换为克制版（"证明了" → "暗示了"，"确保" → "表明"）
- 在宽泛主张中注入方法论层面的警示语（Caveats）和边界条件
- 仅在认识论层面适当处注入克制——不在每句都加

## Red Lines
- ❌ 绝对不能让文本显得软弱无力或对自身数据失去信心
- ❌ 不在每一句都加"可能"、"也许"——只在该加的地方加
- ❌ 必须处理完所有实证主张和泛化结论——不许只改两段

## Replacement Map（绝对化 → 克制）

### English
| 绝对化 | 克制替换 |
|--------|---------|
| proves / demonstrates that | suggests / indicates that |
| ensures / guarantees | tends to / is associated with |
| eliminates | mitigates / reduces |
| solves | addresses |
| confirms | is consistent with |
| outperforms (无 caveat) | outperforms ... under [condition] |
| achieves the best | achieves the strongest reported result |
| significantly better (无显著性检验) | better (with p < x.xx) / appears to be better |
| is the most effective | is among the most effective in our setting |
| works on all cases | works in the evaluated regimes |

### 中文
| 绝对化 | 克制替换 |
|--------|---------|
| 证明了 | 暗示了 / 表明 |
| 确保了 / 保证了 | 有助于 / 倾向于 |
| 解决了 | 缓解了 / 改善了 |
| 完全消除 | 显著减少 |
| 完美 / 完美地 | 较优 / 在测试集上较优 |
| 一定 / 肯定 | 在当前条件下 |
| 总是 / 始终 | 在大多数样本中 |
| 最好的方法 | 当前评估中最强的基线之一 |

## Caveat Templates（注入模板）

```
"在当前样本范围内，..."
"在 X 数据集 / Y 场景下，结果提示..."
"这一趋势可能受到 [因素] 影响..."
"在 [假设] 条件下，本文观察到..."
"需要进一步在 [更广场景] 中验证..."
"我们将这一结果解读为支持假设 H1，但不排除替代解释..."
"该结论的外推应限制在 [边界]..."
"统计显著性检验（p = ...）表明..."
"Within the scope of our experiments, ..."
"Under the assumption of [X], we observe..."
"This finding is suggestive but not definitive, given..."
"Generalization beyond [setting] requires further study..."
```

## 主张分级（决定加多少 caveat）

| 等级 | 类型 | 是否加 caveat |
|------|------|--------------|
| L0 | 定义性陈述（"卷积层是..."） | 不加 |
| L1 | 方法描述（"我们使用 Adam 优化器..."） | 一般不加 |
| L2 | 实证主张（"准确率达到 98.5%"） | 重点加：边界条件 |
| L3 | 泛化结论（"该方法在所有场景下..."） | 必加：明确 boundary |
| L4 | 因果断言（"X 导致 Y"） | 必加：替代解释空间 |

## Workflow

### Step 1: 接收 Stage 3 输出
- 已完成词汇 / 节奏 / 衔接三步处理的整篇文本

### Step 2: 主张分级扫描
- 通读全文，对每个论断句标注 L0-L4
- 重点关注摘要、引言末段（贡献声明）、结果讨论、结论

### Step 3: 替换 + 注入
- L2 / L3 / L4 主张句：替换绝对化动词为克制版
- 必要处加 caveat 短语（用 Caveat Templates）
- **数据数字保持原值**——只改语气，不改事实

### Step 4: 输出格式

```markdown
=== 校准后正文 ===
<全部段落，绝对化语气全部克制化，必要处注入 caveat>

=== Hedging 清单 ===
| 位置 | 等级 | 原句 | 校准后 | 加的 caveat |
|------|------|------|--------|------------|
| Abstract ¶1 末 | L3 | "本方法证明了在所有信噪比条件下都优于现有基线" | "在 SNR ∈ [-10, 20] dB 范围内，本方法表明优于现有基线" | 边界条件 |
| §4.2 Results ¶3 | L2 | "确保了 98.5% 的准确率" | "在测试集上达到 98.5% 准确率（n=1247，95% CI: 97.8-99.0）" | 统计区间 |
| §5 Discussion ¶1 | L4 | "X 导致了性能提升" | "X 与性能提升强相关；不排除 [替代解释]" | 替代解释 |
| ... | ... | ... | ... | ... |

=== 进入下一阶段 ===
→ Stage 5: aigc-reduce-perplexity
```

## Cross-Skill Pipeline
- **上游**：Stage 3: `aigc-reduce-cohesion`（逻辑衔接）
- **本阶段**：Stage 4/5 ← 您在这里
- **下游**：Stage 5: `aigc-reduce-perplexity`（困惑度重构）

## Anti-Patterns
- 不要让每句都"可能"、"也许"——会让审稿人觉得作者没自信
- 不要给方法描述（L1）加无谓 caveat
- 不要修改数据数字
- 不要把"证明了"全部一刀切替换为"暗示了"——看主张层级

## Owner 闭环
- 必须输出完整校准正文
- 必须给出 Hedging 清单（每一处都可追溯）
- 必须明确指向下游 Stage 5
