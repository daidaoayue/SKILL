# aigc-reduce-skills 学术语体加固 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 `aigc-reduce-skills` 降 AIGC 流水线加固学术语体，消除口语化/碎句/反问句/中文第一人称，正文锁定 L1 书面体，致谢节豁免。

**Architecture:** 方案 B —— 新增单一真相源 `_REGISTER-SPEC.md` 定义语体红线与口语→L1 映射表；各产出正文的 skill 把口语词库/示例替换为 L1 版并加指针引用该规范。不改流水线 Stage 编号、skill `name`/触发词、Python 脚本。

**Tech Stack:** Markdown skill 文件；grep 验证；git（仓库 `daidaoayue/SKILL`，分支 `feat/aigc-reduce-academic-register`）。

**工作目录:** 所有路径相对 `C:/Users/带刀阿越/SKILL/`。skill 包在 `Paper_Writing/aigc-reduce-skills/`。

**验证说明:** 本计划无单元测试，验证手段为 grep 禁用词清单。每个任务「先验证当前残留 → 改 → 再验证清零 → 提交」。

---

## Task 1: 新建 `_REGISTER-SPEC.md` 共享语体规范

**Files:**
- Create: `Paper_Writing/aigc-reduce-skills/_REGISTER-SPEC.md`

- [ ] **Step 1: 创建 `_REGISTER-SPEC.md`，完整内容如下**

````markdown
# 学术语体规范（_REGISTER-SPEC.md）

> aigc-reduce-skills 流水线的**单一语体真相源**。所有产出正文的 skill（destructure / vocab / rhythm / cohesion / hedging / perplexity / cite-inject 及编排器 aigc-reduce）的改写一律遵循本规范。

## 1. 语体定级

- **正文章节** = L1 严格书面学术体：零反问句、零口号碎句、零口语词、零中文第一人称。
- **认知深度保留 L2**：反直觉结果、机制疑问、方法取舍等「研究过程」事实必须保留，但以客观陈述句承载——降 AIGC 靠的是认知内容的具体性，不是口语化。
- **英文 `we` 保留**：英文学术论文使用 `we` 是规范，不在禁用范围。禁用仅针对中文 `我们/课题组`。
- **致谢节豁免**：致谢（Acknowledgement）按惯例是个人化谢词，保留第一人称与个人化语气，不受本规范第 2 节红线与第 4 节主语池约束。

## 2. 四条禁用红线（正文，致谢节除外）

1. **禁反问句** —— 例：`为什么有效？`、`这么做的意义是什么呢？`。一律改为客观陈述引导语。
2. **禁口号式碎句** —— 例：`数字说明了问题。`、`结果出乎意料。`。短句仍允许（节奏变频需要句长方差），但必须是完整、有学术内容的陈述句。
3. **禁口语词** —— 例：`有点`、`绕不过的坑`、`实际跑下来`、`跑通之后`、`麻烦在于`、`换个视角看`、`反转了个个`、`说不了太多`。
4. **禁中文第一人称作主语** —— `我们`、`咱们`、`课题组`。英文 `we` 保留。

## 3. 口语 → L1 映射表

### 3.1 研究过程思维痕迹（14 条）

| 口语原版 | L1 客观书面版 |
|---|---|
| 这个结果有点反直觉。 | 该结果与预期不符。/ 一个出乎预期的现象是，…… |
| 数字说明了问题。 | 上述数据已清楚反映这一点。 |
| 为什么有效？ | 其有效性可解释如下。/ 该机制的作用路径分析如下。 |
| 从物理上看…… | 从物理机制层面分析，…… |
| 换句话说…… | 亦即，…… / 更准确地说，…… |
| 没有走……这条路。 | 本文未采用……路径。 |
| 起初尝试了……，但发现…… | 前期实验中曾尝试……，结果表明…… |
| 实际跑下来…… | 实际运行结果显示，…… |
| 跑通之后才发现…… | 系统集成后发现，…… |
| 麻烦在于…… | 其主要困难在于…… |
| 难点集中在…… | 难点主要集中在…… |
| 根源很可能是…… | 造成这一现象的主要原因在于……/ 其根源可归结为…… |
| 这从侧面佐证了…… | 这一现象间接印证了…… |
| 这正是……的出发点。 | 这构成了……的设计动因。/ 这一问题正是……的提出动机。 |

### 3.2 去结构化口语词（7 条）

| 口语原版 | L1 客观书面版 |
|---|---|
| 绕不过的坑 | 难以回避的问题 |
| 更棘手的是 | 更为困难的是 / 更突出的问题是 |
| 换个视角看 | 从另一角度分析 |
| 这条路确实丢掉了 | 该方案确实牺牲了 |
| 另一个短板 | 另一处不足 |
| 我们的切入点是 | 本文的切入点是 |
| 其实有几个…… | 存在若干…… |

## 4. 正文主语池

正文主语轮换池 = `本文 / 本课题 / 本章 / 该方法 / 上述策略 / 该现象 / 无主语被动`（如「实验结果显示」「经验证」）。**不使用 `我们 / 课题组`。**

`本文/本课题 密度 < 30%` 指标保留（连续多句以 `本文` 开头确被 CNKI 标红），但降密度手法为「换成客观替代主语 + 无主语化」，而非「换成我们」。

## 5. 致谢节豁免条款

第 2 节四条红线与第 4 节主语池**不适用于致谢节**。致谢继续按 `aigc-reduce-destructure` 的「致谢节专项处理」个人化语气示例处理（保留第一人称、口语化、具体情境）。
````

- [ ] **Step 2: 验证文件创建成功**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -c "L1" _REGISTER-SPEC.md`
Expected: 输出 ≥ 5（文件存在且含 L1 定义）

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/带刀阿越/SKILL"
git add Paper_Writing/aigc-reduce-skills/_REGISTER-SPEC.md
git commit -m "feat(aigc-reduce): 新增 _REGISTER-SPEC.md 共享语体规范" -m "L1 书面体定级 + 四条禁用红线 + 口语→L1 映射表(21条) + 正文主语池 + 致谢节豁免条款。" -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 2: 重写 `aigc-reduce-perplexity/SKILL.md`

**Files:**
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce-perplexity/SKILL.md`

- [ ] **Step 1: 验证当前残留**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "有点反直觉\|为什么有效\|数字说明了问题\|实际跑下来\|麻烦在于\|跑通之后\|根源很可能是" aigc-reduce-perplexity/SKILL.md`
Expected: 多处命中（frontmatter、Red Lines、思维痕迹表、改写示例、Step 5 表）

- [ ] **Step 2: 改 frontmatter description（第 3 行）**

旧文本片段 `并注入研究过程思维痕迹（这个结果有点反直觉/为什么有效/起初尝试了X但...）。`
改为 `并注入研究过程思维痕迹（以 L1 书面体表达，如'该结果与预期不符'/'其有效性可解释如下'）。`

- [ ] **Step 3: 在 Role 段后插入语体规范指针**

在第 11 行（Role 段末句）之后、`## Goals` 之前插入一空行与一行：

```markdown

> 本 skill 的所有改写遵循同目录 `_REGISTER-SPEC.md` 的学术语体红线（L1 书面体；禁反问句、口号碎句、口语词、中文第一人称；致谢节豁免）。
```

- [ ] **Step 4: 改 Red Lines（第 23 行）**

旧行 `- ❌ 思维痕迹注入不等于口语化——"这个结果有点反直觉" ✅，"撞了一堵墙" ❌`
改为 `- ❌ 思维痕迹注入必须用 L1 书面体——"该结果与预期不符" ✅；反问句、口号碎句、口语词、中文第一人称一律 ❌（详见 _REGISTER-SPEC.md）`

- [ ] **Step 5: 整表替换「思维痕迹注入词库」的「按使用场景分类」表**

定位 `### 按使用场景分类` 下的表格（第 75-90 行附近，从 `| 场景 | 思维痕迹短语` 到 `| 结论侧面 | "这正是...的出发点。"` 整张表），整张替换为：

```markdown
| 场景 | 客观书面引导语（L1，致谢节除外） | 注意事项 |
|------|--------------------------------|---------|
| 结果分析·反预期 | "该结果与预期不符。" / "一个出乎预期的现象是，……" | 放在数据陈述后 |
| 结果分析·数据直陈 | "上述数据已清楚反映这一点。" | 紧接数据 |
| 机制解释·有效性 | "其有效性可解释如下。" / "该机制的作用路径分析如下。" | 后接机制分析，不用反问句 |
| 机制解释·物理层面 | "从物理机制层面分析，……" | 物理可解释段开头 |
| 机制解释·重述 | "亦即，……" / "更准确地说，……" | 重新陈述同一内容 |
| 方法选择·取舍 | "本文未采用……路径。" | 说明方法取舍 |
| 方法选择·过程 | "前期实验中曾尝试……，结果表明……" | 研究过程叙述，不用第一人称 |
| 工程实践·运行 | "实际运行结果显示，……" | 实验结果段 |
| 工程实践·集成 | "系统集成后发现，……" | 工程问题揭示 |
| 问题阐述·困难 | "其主要困难在于……" | 问题严重性说明 |
| 问题阐述·难点 | "难点主要集中在……" | 多重困难总括 |
| 问题阐述·根因 | "造成这一现象的主要原因在于……" / "其根源可归结为……" | 原因分析推断 |
| 结论侧面·印证 | "这一现象间接印证了……" | 间接支撑论点 |
| 结论侧面·动机 | "这构成了……的设计动因。" / "这一问题正是……的提出动机。" | 动机关联说明 |
```

- [ ] **Step 6: 改「注入规则」验证条（第 97 行附近）**

旧行 `4. **验证**：注入后读一遍，确保不口语化、不失学术基调`
改为 `4. **验证**：注入后逐句对照 _REGISTER-SPEC.md 禁用红线，确认无反问句、碎句、口语词、中文第一人称`

- [ ] **Step 7: 整段替换「改写示例」（第 99-112 行附近）**

定位 `### 改写示例` 到其代码块结束，整段替换为：

````markdown
### 改写示例

**原文（纯 AI 分析语气）**：
```
该现象提示：特征工程中盲目堆叠通道并非更优，Ch2 引入的噪声拖累了整体性能。
```

**口语化注入（v3 旧做法，已废弃——含反问、碎句、口语词）**：
```
这个结果有点反直觉。加了 Ch2 之后精度掉了，根源很可能是……
```

**L1 书面体注入（现行做法，CNKI 实测 5.9% → 修复后 <1%）**：
```
该结果与预期不符：引入 Ch2 通道后识别精度不升反降。造成这一现象的主要原因在于，
在当前信噪比条件下，Ch2 引入的相位噪声覆盖了 Ch3 所携带的判别信号。这一现象间接
印证了 Ch3 的实际贡献，同时暴露出一处工程隐患：在缺乏约束的情况下，网络倾向于
优先利用幅度通道而弱化相位通道。这一问题构成了下一小节幅度 Dropout 策略的设计动因。
```
````

- [ ] **Step 8: 改 Step 5 输出格式中的「思维痕迹注入报告」示例表行**

旧两行：
```
| 1 | §3.5.3 结果段 | "这个结果有点反直觉。" | "该现象提示：..." | CNKI 5.9%→修复 |
| 2 | §3.5.3 机制段 | "为什么有效？" | "机制分析显示：..." | 打破引导句模板 |
```
改为：
```
| 1 | §3.5.3 结果段 | "该结果与预期不符。" | "该现象提示：..." | CNKI 5.9%→修复 |
| 2 | §3.5.3 机制段 | "其有效性可解释如下。" | "机制分析显示：..." | 打破引导句模板 |
```

- [ ] **Step 9: 验证禁用词清零**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "有点反直觉\|为什么有效？\|数字说明了问题\|实际跑下来\|麻烦在于\|跑通之后\|根源很可能是" aigc-reduce-perplexity/SKILL.md`
Expected: 仅「口语化注入（v3 旧做法，已废弃）」反例代码块内允许出现 `有点反直觉` / `根源很可能是`（作为对比反例展示）；其余位置零命中。若其他位置仍命中，回到对应 Step 修复。

- [ ] **Step 10: Commit**

```bash
cd "C:/Users/带刀阿越/SKILL"
git add Paper_Writing/aigc-reduce-skills/aigc-reduce-perplexity/SKILL.md
git commit -m "refactor(aigc-reduce): perplexity 思维痕迹词库改为 L1 书面体" -m "整表重写 14 条思维痕迹为客观引导语; 改写示例重铸; 加 _REGISTER-SPEC.md 指针。" -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 3: 重写 `aigc-reduce-destructure/SKILL.md`（致谢示例不动）

**Files:**
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce-destructure/SKILL.md`

- [ ] **Step 1: 验证当前残留**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "绕不过\|更棘手\|换个视角\|这条路确实\|另一个短板\|我们的切入点\|包了两类" aigc-reduce-destructure/SKILL.md`
Expected: 第 46、47、71、92、117、175、214 行附近命中

- [ ] **Step 2: 在 Role 段后插入语体规范指针**

在第 11 行之后、`## Goals` 之前插入空行与：

```markdown

> 本 skill 的所有改写遵循同目录 `_REGISTER-SPEC.md` 的学术语体红线（L1 书面体；禁反问句、口号碎句、口语词、中文第一人称）。**例外：致谢节豁免**——本 skill「致谢节专项处理」的改写示例保留个人化、口语化语气，不受此红线约束。
```

- [ ] **Step 3: 替换特征 1「改写后」代码块（第 45-49 行附近）**

旧三行：
```
工程实现起来其实有几个绕不过的坑。最直接的是参数量翻倍——每个权重都要复值表示。
更棘手的是训练稳定性：损失曲面比实值情形复杂，超参敏感度高一截。
最后是部署，主流框架对复值算子的支持稀薄，INT8 量化路径几乎没成熟方案。
```
改为：
```
工程实现存在若干难以回避的问题。最直接的是参数量翻倍，每个权重均须以复值形式表示。
更为困难的是训练稳定性：损失曲面较实值情形更为复杂，超参数敏感度明显更高。
最后是部署环节，主流框架对复值算子的支持有限，INT8 量化路径尚无成熟方案。
```

- [ ] **Step 4: 替换特征 2「改写后」代码块（第 71-72 行附近）**

旧两行：
```
公式 [3.8] 给出 γ 的形式。换个视角看，γ 就是单位圆上 W 个相位向量的归一化合矢量长度——
W 帧相位完全一致时 γ=1，相位完全随机时 γ→0。
```
改为：
```
公式 [3.8] 给出 γ 的形式。从另一角度分析，γ 即单位圆上 W 个相位向量的归一化合矢量长度：
W 帧相位完全一致时 γ=1，相位完全随机时 γ→0。
```

- [ ] **Step 5: 替换特征 3「改写后」代码块（第 91-93 行附近）**

旧三行：
```
本文绕开 CVNN 的复值实现，把相位以"实值通道"的形式拼到幅度通道旁边，
让标准 CNN 直接处理。这条路确实丢掉了复值乘法天然携带的几何先验。
但相位判别力保住了，部署链路也干净。
```
改为：
```
本文绕开 CVNN 的复值实现，将相位以"实值通道"的形式与幅度通道并置，
由标准 CNN 直接处理。该方案确实牺牲了复值乘法天然携带的几何先验，
但保留了相位的判别能力，部署链路也更为简洁。
```

- [ ] **Step 6: 改特征 4「改写后」第一句（第 117 行附近）**

旧行 `融合机制是另一个短板。固定权重的决策级融合信息损失太大，大参数量的拼接/注意力`
改为 `融合机制是另一处不足。固定权重的决策级融合信息损失过大，大参数量的拼接/注意力`

- [ ] **Step 7: 替换特征 5「改写后」代码块（第 144-155 行附近）**

旧文本（三段）：
```
软件系统的底层是硬件抽象层（HAL），包了两类接口：一是雷达数据接入（兼容本地
.dat 文件回放与实时网络流），二是 NPU 推理（封装 RKNN-Runtime 调用）。HAL
向上层暴露统一的"数据流"抽象。

往上是信号处理与推理两层。信号处理层把 PC 端 MATLAB 流程用 Python 重写，包括
距离向 FFT、MTD 滤波、Taylor 窗、16 帧累积、相位差与相干性计算，确保板上输出
与 PC 训练数据严格对齐。推理层并行调度 RD/Phase/RCS 三分支模型在 3 个 NPU
Core 上的推理，并执行门控融合与航迹级软投票，对每个新到片段更新累积概率分布。

最上层是 GUI 应用，基于 Qt 提供图形化交互——实时显示雷达图谱、识别结果、
统计数据，支持配置调整与日志记录。
```
改为：
```
软件系统的底层是硬件抽象层（HAL），封装了两类接口：一是雷达数据接入（兼容本地
.dat 文件回放与实时网络流），二是 NPU 推理（封装 RKNN-Runtime 调用）。HAL
向上层暴露统一的"数据流"抽象。

往上是信号处理与推理两层。信号处理层将 PC 端 MATLAB 流程以 Python 重写，包括
距离向 FFT、MTD 滤波、Taylor 窗、16 帧累积、相位差与相干性计算，确保板上输出
与 PC 训练数据严格对齐。推理层并行调度 RD/Phase/RCS 三分支模型在 3 个 NPU
Core 上的推理，并执行门控融合与航迹级软投票，对每个新到片段更新累积概率分布。

最上层是 GUI 应用，基于 Qt 提供图形化交互：实时显示雷达图谱、识别结果、
统计数据，支持配置调整与日志记录。
```

- [ ] **Step 8: 改特征 6「改写思路」两行（第 169、173 行附近）**

旧行 `- 主语轮换：本文 → 我们 / 课题组 / 在 CQ-08 上 / 上述方法 / 这条路径`
改为 `- 主语轮换：本文 → 本课题 / 该方法 / 在 CQ-08 上 / 上述方法 / 该技术路径（不使用"我们/课题组"等中文第一人称）`

旧行 `- 思维痕迹注入："起初我们..."、"实际跑下来..."`
改为 `- 思维痕迹注入（L1 书面体）："前期实验中曾尝试……"、"实际运行结果显示……"`

- [ ] **Step 9: 替换特征 6「改写后」代码块（第 174-179 行附近）**

旧四行：
```
我们的切入点是相位信息的物理价值，沿着特征设计、融合识别、边缘部署三段铺开。
CQ-08 实测条件下航迹级精度达到 98.50%；RK3588 板上 INT8 部署的端到端延迟
约 30 ms，平均功耗约 6 W。这套方法学——相位保留特征通道、自适应门控融合、
板上 QAT 部署链路——希望能给多模态雷达识别后续研究提供一份可参考的实现。
```
改为：
```
本文的切入点是相位信息的物理价值，沿特征设计、融合识别、边缘部署三个环节展开。
CQ-08 实测条件下航迹级精度达到 98.50%；RK3588 板上 INT8 部署的端到端延迟
约 30 ms，平均功耗约 6 W。本文形成的方法体系，涵盖相位保留特征通道、自适应
门控融合与板上 QAT 部署链路，可为多模态雷达识别的后续研究提供参考实现。
```

- [ ] **Step 10: 改「改写清单」示例表行（第 214 行附近）**

旧行片段 `"工程实现起来其实有几个绕不过的坑。最直接的是...更棘手的是...最后是..."`
改为 `"工程实现存在若干难以回避的问题。最直接的是...更为困难的是...最后是..."`

- [ ] **Step 11: 确认致谢示例未动**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "最欠的是陈老师\|说不了太多" aigc-reduce-destructure/SKILL.md`
Expected: 「致谢节专项处理」改写示例区（第 237-249 行附近）仍命中——致谢示例**必须保持原样**，这是预期结果。

- [ ] **Step 12: 验证正文区禁用词清零**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "绕不过\|更棘手\|换个视角\|这条路确实\|另一个短板\|我们的切入点\|包了两类" aigc-reduce-destructure/SKILL.md`
Expected: 零命中

- [ ] **Step 13: Commit**

```bash
cd "C:/Users/带刀阿越/SKILL"
git add Paper_Writing/aigc-reduce-skills/aigc-reduce-destructure/SKILL.md
git commit -m "refactor(aigc-reduce): destructure 改写示例改为 L1 书面体" -m "6 大特征改写后示例去口语化; 主语池删我们/课题组; 致谢示例保持不动; 加指针。" -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 4: 更新编排器 `aigc-reduce/SKILL.md`

**Files:**
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce/SKILL.md`

- [ ] **Step 1: 验证当前残留**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "这个结果有点反直觉\|为什么有效\|起初我们\|实际跑下来\|麻烦在于\|跑通之后\|数字说明了问题\|我们/课题组" aigc-reduce/SKILL.md`
Expected: 第 16、49、113-119、122、274-280 行附近命中

- [ ] **Step 2: 在标题后插入语体规范指针**

在第 8 行标题 `# AIGC率降低·CNKI 实战版全自动流水线（v3）` 之后插入空行与：

```markdown

> **语体规范**：本流水线 7 步的所有改写遵循同目录 `_REGISTER-SPEC.md` —— 正文锁 L1 书面体（禁反问句、口号碎句、口语词、中文第一人称），致谢节豁免。
```

- [ ] **Step 3: 改 v3 版本说明「思维痕迹注入」条（第 16 行）**

旧行 `- **思维痕迹注入（Thought Trace Injection）**：实测验证最有效的 AIGC 降低手法之一。"这个结果有点反直觉。""为什么有效？" 等研究过程痕迹，远比文学化比喻更安全。`
改为 `- **思维痕迹注入（Thought Trace Injection）**：实测验证最有效的 AIGC 降低手法之一。以 L1 书面体表达的研究过程痕迹（如"该结果与预期不符。""其有效性可解释如下。"），远比文学化比喻或口语化碎句更安全。`

- [ ] **Step 4: 改 §3.5.3 修复手法表行（第 49 行附近）**

旧行片段 `改为"这个结果有点反直觉""为什么有效？"`
改为 `改为 L1 客观陈述："该结果与预期不符""其有效性可解释如下"`

- [ ] **Step 5: 替换「v3 反检测核心原则」第 2 条思维痕迹清单（第 113-119 行附近）**

旧文本：
```
2. **注入思维痕迹**（v3 新增）：加入研究过程的真实语气：
   - "这个结果有点反直觉。"
   - "为什么有效？"
   - "起初我们尝试了 X，但发现..."
   - "实际跑下来..."
   - "换句话说..."
   - "从物理上看..."
```
改为：
```
2. **注入思维痕迹**（v3 新增，已校准为 L1 书面体）：以客观书面陈述句呈现研究过程认知，禁用反问句、口号碎句、口语词、中文第一人称：
   - "该结果与预期不符。"
   - "其有效性可解释如下。"
   - "前期实验中曾尝试 X，结果表明……"
   - "实际运行结果显示……"
   - "更准确地说……"
   - "从物理机制层面分析……"
```

- [ ] **Step 6: 改「轮换主语」条（第 122 行附近）**

旧行 `5. **轮换主语**：本文/本课题 → 我们/课题组/在X上/上述方法`
改为 `5. **轮换主语**：本文/本课题 → 该方法/上述策略/该现象/无主语被动（"在X上""经验证"）；不使用"我们/课题组"等中文第一人称`

- [ ] **Step 7: 整表替换「思维痕迹词汇库」（第 272-280 行附近）**

旧文本（标题行 + 表）：
```
**思维痕迹词汇库**（用于 Stage 5 注入）：

| 场景 | 思维痕迹短语 |
|------|------------|
| 结果分析 | "这个结果有点反直觉。" / "数字说明了问题。" |
| 机制解释 | "为什么有效？" / "从物理上看..." / "换句话说..." |
| 方法选择 | "没有走...这条路。" / "起初尝试了...，但..." |
| 工程实践 | "实际跑下来..." / "跑通之后才发现..." |
| 问题描述 | "麻烦在于..." / "难点集中在..." |
```
改为：
```
**思维痕迹词汇库**（用于 Stage 5 注入，均为 L1 书面体；完整映射见 _REGISTER-SPEC.md）：

| 场景 | 客观书面引导语（L1） |
|------|--------------------|
| 结果分析 | "该结果与预期不符。" / "上述数据已清楚反映这一点。" |
| 机制解释 | "其有效性可解释如下。" / "从物理机制层面分析……" / "更准确地说……" |
| 方法选择 | "本文未采用……路径。" / "前期实验中曾尝试……，结果表明……" |
| 工程实践 | "实际运行结果显示……" / "系统集成后发现……" |
| 问题描述 | "其主要困难在于……" / "难点主要集中在……" |
```

- [ ] **Step 8: 在 Anti-Patterns 末尾追加一条**

定位 `## Anti-Patterns（v3 更新）` 列表，在 `- **不要只信本地 detector**：...` 这条之后追加一行：

```markdown
- **不要用反问句或口号碎句降 AIGC**："为什么有效？""数字说明了问题。" = 口语化，违反 L1 书面体（详见 _REGISTER-SPEC.md）
```

- [ ] **Step 9: 验证禁用词清零**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "这个结果有点反直觉\|起初我们\|实际跑下来\|跑通之后\|数字说明了问题" aigc-reduce/SKILL.md`
Expected: 零命中（注：Anti-Patterns 新增行含"为什么有效？"作为反例展示，属预期；`grep "为什么有效"` 仅该反例行命中可接受）

- [ ] **Step 10: 确认编排器内致谢示例未动**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -n "最欠的是陈老师" aigc-reduce/SKILL.md`
Expected: 「致谢节专项处理」改写示例区仍命中——预期保留。

- [ ] **Step 11: Commit**

```bash
cd "C:/Users/带刀阿越/SKILL"
git add Paper_Writing/aigc-reduce-skills/aigc-reduce/SKILL.md
git commit -m "refactor(aigc-reduce): 编排器思维痕迹/主语轮换改为 L1 书面体" -m "v3 原则 + 思维痕迹词汇库表 + 主语轮换池更新; 加语体规范指针与反问句反模式。" -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 5: 轻量修改 vocab / rhythm / hedging / cite-inject

**Files:**
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce-vocab/SKILL.md`
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce-rhythm/SKILL.md`
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce-hedging/SKILL.md`
- Modify: `Paper_Writing/aigc-reduce-skills/aigc-reduce-cite-inject/SKILL.md`

指针统一文本（4 个文件均在 Role 段后、下一个 `##` 标题前插入空行与此行）：

```markdown

> 本 skill 的所有改写遵循同目录 `_REGISTER-SPEC.md` 的学术语体红线（L1 书面体；禁反问句、口号碎句、口语词、中文第一人称；致谢节豁免）。
```

- [ ] **Step 1: vocab —— 插入指针**

在 `aigc-reduce-vocab/SKILL.md` 第 12 行（Role 段末）之后、`## Goals` 之前插入上述指针行。

- [ ] **Step 2: vocab —— 改 CNKI 安全替代表 2 行（第 72-73 行附近）**

旧两行：
```
| "该现象提示：" | 改为"这个结果有点反直觉。" 或直接陈述发现 |
| "机制分析显示：" | 改为"为什么有效？" 后接机制 |
```
改为：
```
| "该现象提示：" | 删除引导句前缀，直接陈述发现（如"该结果与预期不符"） |
| "机制分析显示：" | 改为客观引导句"其机制可解释如下"，避免冒号式模板 |
```

- [ ] **Step 3: rhythm —— 插入指针**

在 `aigc-reduce-rhythm/SKILL.md` 第 11 行（Role 段末）之后、`## Goals` 之前插入指针行。

- [ ] **Step 4: rhythm —— 改短句植入示例（第 48 行）**

旧行 `- **短句植入**：在关键论断处加 5-8 词独立陈述句（例："这一现象不可忽视。"、"结果出乎意料。"）`
改为 `- **短句植入**：在关键论断处加 5-8 词完整陈述句（例："该现象与预期相悖。"、"这一偏差不可忽视。"）；短句须为合格学术陈述句，不得为口号、反问或碎句`

- [ ] **Step 5: hedging —— 插入指针**

在 `aigc-reduce-hedging/SKILL.md` 第 12 行（Role 段末）之后、`## Goals` 之前插入指针行。

- [ ] **Step 6: hedging —— 改 caveat 模板中文第一人称（第 59 行）**

旧行 `"我们将这一结果解读为支持假设 H1，但不排除替代解释..."`
改为 `"本文将这一结果解读为支持假设 H1，但不排除替代解释..."`

（注：同段英文模板 `"Under the assumption of [X], we observe..."` 保留——英文 `we` 是学术惯例。）

- [ ] **Step 7: cite-inject —— 插入指针**

在 `aigc-reduce-cite-inject/SKILL.md` 第 11 行（Role 段末）之后、`## 单一目标` 之前插入指针行。

- [ ] **Step 8: 验证**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -c "_REGISTER-SPEC.md" aigc-reduce-vocab/SKILL.md aigc-reduce-rhythm/SKILL.md aigc-reduce-hedging/SKILL.md aigc-reduce-cite-inject/SKILL.md && grep -n "这个结果有点反直觉\|为什么有效？\|结果出乎意料\|我们将这一结果" aigc-reduce-vocab/SKILL.md aigc-reduce-rhythm/SKILL.md aigc-reduce-hedging/SKILL.md`
Expected: 第一条 grep 每个文件均输出 ≥ 1；第二条 grep 零命中

- [ ] **Step 9: Commit**

```bash
cd "C:/Users/带刀阿越/SKILL"
git add Paper_Writing/aigc-reduce-skills/aigc-reduce-vocab/SKILL.md Paper_Writing/aigc-reduce-skills/aigc-reduce-rhythm/SKILL.md Paper_Writing/aigc-reduce-skills/aigc-reduce-hedging/SKILL.md Paper_Writing/aigc-reduce-skills/aigc-reduce-cite-inject/SKILL.md
git commit -m "refactor(aigc-reduce): vocab/rhythm/hedging/cite-inject 加语体规范指针" -m "vocab 安全替代表去口语; rhythm 短句示例去口号; hedging caveat 去中文第一人称。" -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 6: 更新 `README.md`

**Files:**
- Modify: `Paper_Writing/aigc-reduce-skills/README.md`

- [ ] **Step 1: 改流水线表 Stage 5 行（第 143 行附近）**

旧行 `| 5. 困惑度+思维痕迹 ⭐ | 破坏 N-gram + 注入"为什么有效？/这个结果有点反直觉" | 每章 ≥ 2 处痕迹 |`
改为 `| 5. 困惑度+思维痕迹 ⭐ | 破坏 N-gram + 注入 L1 书面体研究痕迹（"该结果与预期不符"等） | 每章 ≥ 2 处痕迹 |`

- [ ] **Step 2: 新增「学术语体规范」一节**

在 `## ⚠️ 三条红线（7 步共享）` 一节之后、`## 📋 各 Stage 处理什么` 之前，插入新节：

```markdown
## 📐 学术语体规范（_REGISTER-SPEC.md）

`aigc-reduce-skills/_REGISTER-SPEC.md` 是全流水线的**单一语体真相源**。所有产出正文的 skill 一律遵循：

- **正文锁 L1 严格书面体**：禁反问句（`为什么有效？`）、禁口号碎句（`数字说明了问题。`）、禁口语词（`绕不过的坑`、`实际跑下来`）、禁中文第一人称（`我们/课题组`）。
- **保留 L2 认知内容**：反直觉结果、机制疑问、方法取舍等研究过程事实保留，但用客观陈述句承载。
- **英文 `we` 保留**（学术惯例）；**致谢节豁免**（按惯例保留个人化语气）。

需要调整语体级别时，只改 `_REGISTER-SPEC.md` 一处即可，无需逐个 skill 修改。

```

- [ ] **Step 3: 验证**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -c "_REGISTER-SPEC.md" README.md && grep -n "为什么有效？/这个结果有点反直觉" README.md`
Expected: 第一条 grep 输出 ≥ 2；第二条 grep 零命中

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/带刀阿越/SKILL"
git add Paper_Writing/aigc-reduce-skills/README.md
git commit -m "docs(aigc-reduce): README 增补学术语体规范说明" -m "流水线表去口语示例; 新增 _REGISTER-SPEC.md 一节。" -m "Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>"
```

---

## Task 7: 全包验收 grep 扫描

**Files:** 无修改，仅验证。

- [ ] **Step 1: 全包正文区禁用词扫描**

Run:
```bash
cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills"
grep -rn "有点反直觉\|为什么有效？\|数字说明了问题\|实际跑下来\|跑通之后\|麻烦在于\|根源很可能是\|绕不过\|更棘手\|换个视角\|结果出乎意料" --include="*.md" .
```
Expected: 仅以下两处「反例展示」允许命中，其余零命中——
  1. `aigc-reduce-perplexity/SKILL.md` 改写示例中标注「v3 旧做法，已废弃」的反例代码块；
  2. `aigc-reduce/SKILL.md` Anti-Patterns 中标注反模式的 `为什么有效？` 反例行。
若出现其他命中，定位文件回到对应 Task 修复并补一个 commit。

- [ ] **Step 2: 中文第一人称扫描**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -rn "我们/课题组\|我们的切入点\|起初我们\|我们将这一结果" --include="*.md" .`
Expected: 零命中

- [ ] **Step 3: 致谢豁免完整性确认**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && grep -rn "最欠的是陈老师" --include="*.md" .`
Expected: `aigc-reduce-destructure/SKILL.md` 与 `aigc-reduce/SKILL.md` 各命中一次——致谢示例保持不动，预期结果。

- [ ] **Step 4: 指针覆盖确认**

Run: `cd "C:/Users/带刀阿越/SKILL/Paper_Writing/aigc-reduce-skills" && for f in aigc-reduce aigc-reduce-destructure aigc-reduce-vocab aigc-reduce-rhythm aigc-reduce-hedging aigc-reduce-perplexity aigc-reduce-cite-inject; do echo -n "$f: "; grep -c "_REGISTER-SPEC.md" "$f/SKILL.md"; done`
Expected: 7 个 skill 每个输出 ≥ 1

- [ ] **Step 5: 流水线契约未破坏确认（Stage 编号 / name / 触发词）**

Run: `cd "C:/Users/带刀阿越/SKILL" && git diff main -- "Paper_Writing/aigc-reduce-skills/*/SKILL.md" | grep -E "^[-+](name:|argument-hint:|Triggers on)" `
Expected: 零输出（`name` / `argument-hint` / `Triggers on` 行无任何增删改）

- [ ] **Step 6: 提交日志确认**

Run: `cd "C:/Users/带刀阿越/SKILL" && git log main..feat/aigc-reduce-academic-register --oneline`
Expected: 7 条 commit（设计文档 + Task 1-6）。分支就绪，等待用户决定推送。

---

## Self-Review 记录

- **Spec 覆盖**：spec 第 4.1 节 → Task 1；4.2 表逐行 → Task 2-6；4.3 重铸示例 → Task 2 Step 7；第 6 节 7 条验收 → Task 7 Step 1-6。无遗漏。
- **占位符**：无 TBD/TODO，所有改写后文本均给出完整内容。
- **一致性**：指针文本各 skill 统一；`_REGISTER-SPEC.md` 映射表与 Task 2/4 表内引导语逐条对齐（如「该结果与预期不符」「其有效性可解释如下」全文一致）。
- **边界**：致谢示例在 Task 3 Step 11、Task 4 Step 10、Task 7 Step 3 三处显式确认不动。

---

## 勘误（2026-05-18 执行后回填）

本计划在执行中发现并修正了 3 处计划/spec 缺陷，另吸收 1 项新增需求。以上 Task 描述保留原始措辞作为历史快照，实际交付以本节为准。

### 勘误 1：致谢改写示例位置误判

- **错误**：spec 第 4.2 节与本计划 Task 3 Step 11、Task 7 Step 3 均认为致谢改写示例（`最欠的是陈老师……`）在 `aigc-reduce-destructure/SKILL.md`。
- **事实**：grep 全包确认，该致谢示例只在编排器 `aigc-reduce/SKILL.md` 的「致谢节专项处理」中；`aigc-reduce-destructure` 根本没有致谢章节。
- **修正**：destructure 的语体指针由「本 skill『致谢节专项处理』」改为指向编排器 `aigc-reduce`；所有致谢相关改动全部落在 Task 4。Task 7 Step 3 验收口径相应改为「`最欠的是` 仅存于编排器」。

### 勘误 2：perplexity N-gram 表中文第一人称漏网

- **错误**：本计划 Task 2 未覆盖 `aigc-reduce-perplexity` 的 N-gram 替换表中 `提出了一种新颖的 → 我们引入了一种` 一行；Task 7 Step 2 的第一人称 grep 清单也未含 `我们引入`。
- **修正**：执行 Task 2 时一并将该行改为 `本文引入了一种`，并在 commit message 留痕。

### 勘误 3：`_REGISTER-SPEC.md` 定位 bug（计划未预见）

- **bug 3a**：7 处语体指针写「同目录 `_REGISTER-SPEC.md`」，但该文件在 `aigc-reduce-skills/` 包根目录，各 `SKILL.md` 在子文件夹内——应为「与各 skill 文件夹同级」。
- **bug 3b**：README 三种安装方式均用 `aigc-reduce*` glob 拷贝/移动，匹配不到 `_` 开头的 `_REGISTER-SPEC.md`，导致安装后运行副本缺失该文件。
- **修正**：Task 6 一并修复——7 处指针措辞改为「与各 skill 文件夹同级」，三种安装命令补拷 `_REGISTER-SPEC.md`。

### 新增需求：致谢负面歧义检查（执行中追加）

- 用户在 Task 3 后追加要求：致谢阶段必须逐句排查负面歧义（如 `最欠的是陈老师` 的「最亏欠 / 最欠揍」双关）。
- **吸收方式**：`_REGISTER-SPEC.md` 第 5 节新增两条硬约束（负面歧义零容忍、破机械平行留修辞排比）；编排器「致谢节专项处理」新增逐句负面歧义复核（强制）步骤；Phase Final 追加全文收尾歧义轻扫；致谢改写示例参照用户真实致谢行文逻辑（导师→同辈→长辈递进、逐个点名、零双关）重写。对应独立 commit `462c0bf`。

### 提交数说明

本计划 Task 7 Step 6 原估「7 条 commit」。实际分支共 9 条（设计文档 + 实现计划 + Task 1-6 + 新增需求 commit `462c0bf`），已 squash-free 合并入 `main`（merge commit `9168f93`）。
