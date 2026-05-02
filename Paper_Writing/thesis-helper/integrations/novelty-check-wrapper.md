# novelty-check Integration Wrapper

> **包装的 skill**：`/novelty-check` (verify research idea novelty)
> **触发**：投稿前 / 选题确认 / 预防 desk reject

## Input
```yaml
your_idea: <one-paragraph-description>
target_venue: <where-you-plan-to-submit>
literature_pool: <from-arxiv + semantic-scholar>
strict_mode: false                       # 严格模式：要求 100% 新；普通：80% 新可接受
```

## Output
```text
<project>/.thesis-helper/novelty_check_report.md

Sections:
- Closest Prior Work (top 5 most similar)
- Your Unique Contribution (if any)
- Novelty Score: X/10
- Recommendation: PROCEED | PIVOT | INTEGRATE_PRIOR
- Suggested Differentiation (if score < 7)
```

## thesis-helper 调用条件

```text
config.integrations.novelty_check: true
   或
thesis_type ∈ {journal, conference}（强烈推荐）
   →  Phase 1 触发
```

## 触发流程

```text
1. 收集 literature_pool（arxiv + semantic-scholar 输出）
2. /novelty-check your_idea --pool ... --venue NeurIPS
3. AI 在 pool 中找最相似 5 篇
4. 输出 novelty_score
   ├── ≥ 7 → PROCEED 进入 paper-writing
   ├── 4-6 → PIVOT 提示用户调整定位
   └── < 4 → INTEGRATE_PRIOR 提示作 incremental 而非 novel
```

## 何时跳过

```text
thesis_type == undergrad-thesis     # 本科毕设不要求"新"，做扎实即可
config.pipeline.novelty_check: false
```

## 与 paper-plan 的串联

novelty check 通过 → paper-plan 阶段把"differentiation"写进 introduction motivation。
未通过 → 暂停 pipeline，提示用户重新定位。

## 相关

- 上游：[`arxiv-wrapper.md`](arxiv-wrapper.md) [`semantic-scholar-wrapper.md`](semantic-scholar-wrapper.md)
- pipeline：journal / conference Phase 1
