---
name: thesis-defense-prep
description: "毕业论文答辩准备一站式：Beamer/PPTX 答辩 PPT + 演讲稿 + 答辩问答模拟。专为答辩节奏（10-20 分钟）优化，区别于通用会议汇报。Triggers on: '/thesis-defense-prep', '/答辩准备', '/答辩 PPT', '/做答辩', '答辩问答', 'defense prep', 'thesis defense'."
argument-hint: [paper-pdf-or-tex] [duration-min]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Skill, Agent
---

# Thesis Defense Prep · 毕设答辩准备一站式

> 与 `/paper-slides` 的区别：本 skill **专为答辩**优化（节奏短/重点突出/Q&A 模拟），
> `/paper-slides` 是会议汇报通用 PPT 生成器。

## 三件套交付

```text
defense/
├── slides.tex          # Beamer 源码
├── slides.pdf          # 答辩 PDF
├── slides.pptx         # 备选 PPT 格式（学校系统通常要 PPT）
├── speaker_notes.md    # 演讲稿（每页 1-2 段，含开场白/转场/结语）
├── qa_simulation.md    # 答辩问答模拟（30+ 题 + 建议回答）
└── time_plan.md        # 时间分配表（精确到秒）
```

## Pipeline

### Phase 1 · 解析论文

输入：`<project>/paper/main.tex` 或 `main.pdf`

提取：
```text
- 标题 / 作者 / 导师 / 学校
- Abstract（中英文）
- 章节结构（含字数分布）
- Claims（从 PAPER_PLAN.md 或自动识别）
- 主要 figure（从 figures/latex_includes.tex）
- 主要 table
- 创新点（从 introduction 末尾）
- 实验数据（从 results 章）
- 结论与展望
```

输出：`defense/.parsed_paper.json`（中间文件）

### Phase 2 · 时间规划

依据 `--duration-min` 参数（默认 15 分钟）按答辩黄金分配：

```text
开场（自我介绍 + 选题背景）            10%   ≈ 1.5 min  (1-2 页)
研究内容 / 创新点                     15%   ≈ 2.0 min  (2-3 页)
方法与技术路线                        25%   ≈ 4.0 min  (3-5 页)
实验结果 / 创新性验证                 30%   ≈ 4.5 min  (4-6 页)
结论 / 应用价值 / 展望                10%   ≈ 1.5 min  (2 页)
致谢                                 10%   ≈ 1.5 min  (1 页)
```

10 分钟版自动压缩；20 分钟版扩展（详细方法 + 多组实验）。

输出：`defense/time_plan.md`

### Phase 3 · 生成 Beamer 答辩 PPT

调用 `/paper-slides` 但**注入答辩特化的 prompt**：

```yaml
mode: defense                          # 区别于 conference / lab_meeting
duration_minutes: <user-provided>
target_audience: thesis_committee      # 评委是审稿人，不是同行
emphasis:
  - innovation_points: 突出创新点（评委必问）
  - quantitative_results: 数据要可视化（不要光报数字）
  - my_contribution: 标明"本人完成"vs"已有工作"
  - limitation: 必须有局限性章节（评委挑刺）
visual_style: academic_clean
include_acknowledgement: true          # 末尾致谢
include_qa_buffer_slides: true         # 备查 PPT（评委问到的图表）
```

输出：`defense/slides.tex` + `defense/slides.pdf`

### Phase 4 · 生成 PPTX 备选格式

调用 `document-skills:pptx` 把 Beamer 转 PowerPoint（学校答辩系统通常要 PPT）：

```text
Beamer .tex → 解析每页 → 生成对应 PPTX 页
保留：标题层级 / bullets / 图片
丢失：Beamer 高级动画（学校系统也不支持）
```

输出：`defense/slides.pptx`

### Phase 5 · 生成演讲稿（speaker notes）

每页一段，按口播节奏：

```text
[第 N 页 · 标题]  ⏱️ 用时 ≈ X 秒

口播内容：
"接下来介绍...的设计思路。这一部分的核心问题是...，
我们提出的方法是...，关键创新点在于...。"

转场：
"接下来看这个方法的实验验证。"

⚠️ 提醒：
- 这一页评委可能问 [问题 1] / [问题 2]
- 备查 PPT：第 X 页
```

输出：`defense/speaker_notes.md`

### Phase 6 · 答辩问答模拟（最关键）

调用 `paper_reviewer` 以**答辩评委视角**生成可能问题：

```text
评委角色（多维度）：
1. 方法严谨性专家 → 问推导/对比基线/统计显著性
2. 工程实现专家 → 问代码可复现/数据集来源/超参选择
3. 选题立意专家 → 问研究意义/与 SOTA 差距/落地价值
4. 理论功底专家 → 问基础概念/公式细节/边界条件
5. 应用价值专家 → 问商业化/工程部署/局限性
```

每个角色生成 6-10 个问题，按高频度排序：

```markdown
### Q1 · [严苛度: ⚠️⚠️⚠️ 评委必问]

**问题**：你的方法相比 baseline 提升 1.5%，这个差距统计上显著吗？
做了 t-test 吗？

**建议回答**（30-60 秒）：
1. 直面：是的，我们做了配对 t-test，p < 0.05
2. 数据：5 次重复实验均值 ± 标准差是 X ± Y
3. 转移：更重要的是在 [困难子集] 上提升达到 5%（详见备查 PPT 第 N 页）

**陷阱提示**：不要说"提升不大但思路新"——评委吃这套但要先肯定数据
```

输出：`defense/qa_simulation.md`（30+ 题 + 建议回答 + 陷阱提示）

### Phase 7 · 闭环验证

```yaml
✅ 验证清单
- [ ] slides.pdf 编译通过
- [ ] 页数符合时间预算（每页 30-60 秒）
- [ ] slides.pptx 生成 + 可在 PowerPoint 打开
- [ ] speaker_notes.md 每页有口播 + 转场 + 提醒
- [ ] qa_simulation.md 至少 30 题 + 5 个 ⚠️⚠️⚠️ 必问
- [ ] 包含致谢页
- [ ] 包含至少 3 页备查 PPT
- [ ] 时间分配总和 == 用户设定时长
```

未通过任何一项 → 不算完成。

## Constants

```yaml
DEFAULT_DURATION_MIN: 15                     # 本科毕设标准
DURATION_OPTIONS: [10, 15, 20, 25, 30]      # 硕博答辩通常 20-30 分钟
MIN_QA_QUESTIONS: 30
MIN_CRITICAL_QA: 5                          # ⚠️⚠️⚠️ 必问数量下限
PAGE_TIME_RANGE_SECONDS: [30, 60]
INCLUDE_BACKUP_SLIDES: true
DEFAULT_BEAMER_THEME: metropolis
```

## 与上游 skill 的关系

```text
thesis-defense-prep (本 skill)
  ├── 调用 /paper-slides (Phase 3，注入 mode=defense)
  ├── 调用 document-skills:pptx (Phase 4)
  └── 调用 /paper_reviewer (Phase 6，多角色评委模拟)
```

## Owner 闭环承诺

- ❌ 不允许只生成 PDF 不生成 PPTX——学校系统通常只接受 PPT
- ❌ 不允许 Q&A 少于 30 题——答辩 30 分钟评委能问 10 个，要预测一倍以上
- ❌ 不允许时间分配不精确到秒——答辩超时直接扣分
- ❌ 没有备查 PPT → 评委问图表细节会现场翻车

> 因为信任所以简单——把答辩这件事，做成胸有成竹的闭环，不让学生临场掉链子。
