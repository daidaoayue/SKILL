# result-to-claim Integration Wrapper

> **包装的 skill**：`/result-to-claim` (judge what claims experiments support)
> **触发**：实验跑完后 / 写 paper-plan 前 / 投稿前最后一关

## Input
```yaml
intended_claims: <list-from-paper-plan>
experiment_results: <path-to-results-directory>
significance_threshold: 0.05
effect_size_threshold: 0.5
```

## Output
```text
<project>/.thesis-helper/result_to_claim_report.md

Sections:
- Claim 1: SUPPORTED / PARTIAL / NOT_SUPPORTED
  - Evidence: <experiment_X>
  - Effect size: <value>
  - Statistical significance: <p-value>
- Missing Evidence (need additional experiments)
- Recommended Next Action: WRITE_PAPER | RUN_ABLATION | PIVOT_CLAIM
```

## thesis-helper 调用条件

```text
config.integrations.result_to_claim: true
   且 thesis_type ∈ {journal, conference, master-thesis}
   →  Phase 4 (journal) / Phase 4 (conference) / Phase 4 (master-thesis)
   触发位置：paper_reviewer 之前
```

## 触发流程

```text
1. 收集 paper-plan 中列出的 intended claims
2. 扫描 results/ 找匹配实验
3. /result-to-claim 评估每个 claim 的证据强度
4. 输出 routing decision：
   ├── SUPPORTED → 进入 paper-write
   ├── PARTIAL → 自动调 ablation-planner 设计补强实验
   └── NOT_SUPPORTED → 暂停，提示用户改 claim 或重做实验
```

## 防止过度声称（overclaim）

学生最常犯：实验只支持"在小数据集上有效"，论文写"普适性突破"。
本 wrapper 强制 claim 与 evidence 1:1 对应，超出范围必须降语调。

## 与 ablation-planner 的串联

```text
result-to-claim          找出证据缺口
   ↓ 缺口列表
ablation-planner         设计补强实验
   ↓ 实验跑完
result-to-claim 二次评估  → 通过则进入 paper-write
```

## 相关

- 同级：[`ablation-planner-wrapper.md`](ablation-planner-wrapper.md) [`paper-reviewer-wrapper.md`](paper-reviewer-wrapper.md)
- pipeline：journal / conference / master-thesis Phase 4
