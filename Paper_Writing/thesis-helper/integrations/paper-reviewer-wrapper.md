# paper_reviewer Integration Wrapper

> **包装的 skill**：`/paper_reviewer` (5 senior reviewer pre-submission committee)
> **触发**：投稿前自审 / 答辩前问答模拟 / 论文质量评估

## Input
```yaml
paper_pdf: <project>/paper/main.pdf
mode: pre_submission | thesis_defense | quick_check
target_venue: <NeurIPS | IEEE | 学位论文 | ...>
review_dimensions:
  - soundness
  - significance
  - novelty
  - clarity
  - reproducibility
```

## Output
```text
<project>/paper/review_self.md

Sections:
- 5 reviewer perspectives (each with score + comments)
- Critical issues (must fix before submission)
- Major issues (should fix)
- Minor issues (nice to fix)
- Overall: ACCEPT | WEAK_ACCEPT | BORDERLINE | WEAK_REJECT | REJECT
- Recommended actions (priority-ordered)
```

## thesis-helper 调用条件

```text
config.integrations.paper_reviewer: true
   →  Phase 5 (journal/conference) / Phase 4 (毕设)
```

## 5 维度审稿人模拟

```text
1. Soundness Expert       方法严谨性 / 推导正确性 / 实验合理
2. Significance Expert    研究意义 / impact / 与 SOTA gap
3. Novelty Expert         创新点 / 与 prior work 区分度
4. Clarity Expert         表述清晰度 / 章节组织 / 图表可读
5. Reproducibility Expert 代码 / 数据 / 超参 / 随机种子
```

每个 reviewer 给 1-10 分 + 详细意见。

## 与 thesis-defense-prep 的协作

```text
paper_reviewer  →  生成可能问题 + 评估论文
   ↓ 问题列表
thesis-defense-prep  →  把问题转成答辩 Q&A 模拟
```

## 与 rebuttal 的差异

```text
paper_reviewer    投稿前自审
rebuttal          投稿后回应真实审稿人
```

两者闭环：自审通过 → 投稿 → 收审稿 → rebuttal → 修改。

## 不依赖 Codex MCP

paper_reviewer 是独立 skill，不需要 Codex MCP（与 paper-write 等不同）。
任意 Claude 设置都能用。

## 相关

- 同级：[`rebuttal-wrapper.md`](rebuttal-wrapper.md) [`result-to-claim-wrapper.md`](result-to-claim-wrapper.md)
- pipeline：所有 4 类型 Phase 4-5
