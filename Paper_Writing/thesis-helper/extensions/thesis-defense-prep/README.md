<!-- markdownlint-disable MD032 -->
# thesis-defense-prep · 毕业答辩准备一站式

> thesis-helper extension · 状态：✅ Batch B 实现

## 一句话价值

输入论文 PDF，30 分钟内拿到：

- Beamer 答辩 PPT (PDF + PPTX 双格式)
- 演讲稿 (每页 1-2 段，含口播 + 转场)
- 答辩问答模拟 (30+ 题 + 建议回答 + 陷阱提示)
- 时间分配表 (精确到秒)

## 为什么不直接用 /paper-slides

| 维度 | /paper-slides | 本 skill |
|------|---------------|----------|
| 目标场景 | 会议汇报 / 组会 | **毕业答辩** |
| 时长适配 | 通用 | 10/15/20/25/30 分钟分级 |
| 评委模拟 | ✗ | ✓ 5 维度评委角色 + 30+ Q&A |
| 创新点突出 | 通用强调 | **本人 vs 已有工作** 必标 |
| 备查 PPT | ✗ | ✓ 评委追问图表用 |
| 致谢页 | 可选 | 强制 |
| PPTX 输出 | 可选 | 强制（学校系统多用 PPT） |

## 用法

```text
# 最简（默认 15 分钟）
/thesis-defense-prep paper/main.pdf

# 指定时长
/thesis-defense-prep paper/main.pdf --duration-min 20

# 同时指定时长和评委侧重
/thesis-defense-prep paper/main.pdf --duration-min 25 --emphasis 工程实现
```

## 输出结构

```text
defense/
├── slides.tex             Beamer 源（可二次修改）
├── slides.pdf             PDF 答辩
├── slides.pptx            PowerPoint 备选（学校系统）
├── speaker_notes.md       演讲稿（开场白/转场/结语）
├── qa_simulation.md       30+ 题答辩问答模拟
├── time_plan.md           时间分配表（精确到秒）
└── .parsed_paper.json     中间产物（论文解析结果）
```

## 五维度评委模拟（Phase 6 核心）

```text
1. 方法严谨性专家  → t-test / 对比基线 / 统计显著性
2. 工程实现专家   → 可复现性 / 数据来源 / 超参选择
3. 选题立意专家   → 研究意义 / SOTA 差距 / 落地价值
4. 理论功底专家   → 基础概念 / 公式细节 / 边界条件
5. 应用价值专家   → 商业化 / 工程部署 / 局限性
```

每个角色生成 6-10 个问题，按 **严苛度三档** 分级：
- ⚠️⚠️⚠️ 必问（≥ 5 题）
- ⚠️⚠️ 高频
- ⚠️ 偶发

## 与 thesis-helper pipeline 的关系

undergrad-thesis-pipeline.md / master-thesis-pipeline.md 的 **Phase 8** 调本 skill。
也可独立调用，不依赖完整 pipeline。

## 相关

- [SKILL.md](SKILL.md) — 完整 pipeline 定义
- [`../latex-to-word/SKILL.md`](../latex-to-word/SKILL.md) — Phase 5 兄弟
- [`../../pipelines/undergrad-thesis-pipeline.md`](../../pipelines/undergrad-thesis-pipeline.md) — 上游 pipeline
