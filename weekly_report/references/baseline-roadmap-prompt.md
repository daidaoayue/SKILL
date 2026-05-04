# Baseline Roadmap Prompt

This prompt drives §8 of the baseline report (the 3-month roadmap). It's
designed so the output can be lifted directly into a paper Introduction or
defense slides. Use it once per init/baseline run.

## When to use

- Running `/weekly-report init` for the first time on a project, OR
- Running `/weekly-report baseline --refresh` to re-cut the roadmap.

## Inputs to feed the LLM

1. `manifest.json` (full)
2. `metric_aggregates` (compiled across all output JSONs)
3. `theory.math_blocks` (existing equations established in the project)
4. `paper.section_changes` (latest paper section structure)
5. `project.toml` (domain, advisor, phd_year)
6. User's free-form input via baseline interview ① (one paragraph: 学生眼里的最高层科研问题)

## Prompt template

> 你是一个 PhD 学生的研究路线图起草助手。基于以下输入，按四象限结构起草未来 3 个月的路线图。
>
> 输入：
> - 项目领域：{domain}
> - 学生输入的最高层问题：{user_problem_statement}
> - 已有指标基线：{metric_aggregates}
> - 已成立公式：{theory_math_blocks}
> - 论文结构：{paper_sections}
>
> 约束：
> 1. 每个 milestone 必须有可验证的成功标志（数字、文件、章节）
> 2. 引用 theory bucket 中已成立的公式作为"已有基础"
> 3. 风险栏需写明 Plan B（而非笼统"如果不行就重来"）
> 4. 投稿时间点必须落到具体月份
> 5. 每条不超过 80 字，便于直接抠到论文 Introduction / 答辩 PPT
> 6. 用过去时讲已完成 / 现在时讲推进中 / 将来时讲下一步，不混
>
> 输出格式（不要更改 H2 编号）：
>
> ```markdown
> ## 8.1 科学问题
> （一句话，narrowing 公式：在 X 场景下，由于 Y 约束，导致 Z 问题，本课题旨在从 W 角度提供解法）
>
> ## 8.2 方法路线
>
> ### Milestone 1（截至 YYYY-MM）
> - 研究子问题：……
> - 待验证的假设：……
> - 可衡量的成功标志：……
> - 风险与 Plan B：……
>
> ### Milestone 2 / Milestone 3 同上
>
> ## 8.3 预期产出
> - 论文：目标 venue（IEEE TGRS / ICASSP / 其他），投稿日期
> - 专利 / 开源 / Demo
> - 节点：中期 / 终期答辩
>
> ## 8.4 资源与协作
> - 计算资源（GPU 类型、节点数）
> - 需要导师协调的事项
> - 可能的合作组
> ```
>
> 自审要求：输出后，重读一遍，问自己——「这段如果直接贴到导师面前，会不会觉得空？」如果会，重写至少一个 milestone 的成功标志使其更具体。

## After receiving LLM output

1. Save to `<project>/.weekly_report/baseline/roadmap_v1.md`
2. Insert into baseline report §8 directly
3. Add to baseline interview as "请审一遍这份路线图，有要改的地方在下方写 Δ"
4. After user reviews, generate `roadmap_v2.md` with their deltas applied

## Iterating

After each paper submission or rebuttal cycle, re-run this prompt with
updated `metric_aggregates` and `paper.section_changes` to produce a new
version. Old versions stay in `baseline/` for traceability.
