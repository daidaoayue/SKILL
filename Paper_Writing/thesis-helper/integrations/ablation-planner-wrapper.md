# ablation-planner Integration Wrapper

> **包装的 skill**：`/ablation-planner` (design ablation studies)
> **触发**：投稿前补 ablation / result-to-claim 触发的证据缺口

## Input
```yaml
main_claims: <list>
existing_experiments: <results-directory>
target_venue: <NeurIPS | IEEE | ...>
budget:
  gpu_hours_max: 100
  experiment_count_max: 8
```

## Output
```text
<project>/.thesis-helper/ablation_plan.md

Sections:
- Recommended Ablations (priority-ordered)
  - Ablation 1: Remove component X
    - Hypothesis: X contributes Y%
    - Setup: <minimal-config>
    - Expected GPU hours: <N>
- Already Sufficient (don't repeat)
- Reviewer Trap Avoidance (问题前置防御)
```

## thesis-helper 调用条件

```text
config.integrations.ablation_planner: true
   或
result-to-claim 输出 PARTIAL → 自动触发本 wrapper
```

## 触发流程

```text
1. 读 main claims（从 paper-plan）
2. 扫描 existing experiments
3. 用 reviewer 视角找"reviewer 一定会问"的 ablation
4. 排序输出（高 ROI 优先 = 关键 claim x 短运行时间）
5. 用户决定跑哪些
6. 跑完后回到 result-to-claim 二次评估
```

## 投稿场景

- ✅ NeurIPS / ICLR / ICML：reviewer 必查 ablation 完整性
- ✅ IEEE Trans：reviewer 重点看 component 贡献
- ✅ master-thesis 投稿前补强
- ❌ 本科毕设（不强求 ablation）

## 防御 reviewer 陷阱

常见 reviewer 反问：
- "Why did you choose X over Y?" → ablation: replace X with Y
- "Is the gain from architecture or just more parameters?" → ablation: parameter-matched baseline
- "Does it work without component Z?" → ablation: -Z 版本

## 相关

- 同级：[`result-to-claim-wrapper.md`](result-to-claim-wrapper.md)
- pipeline：journal / conference / master-thesis Phase 4
