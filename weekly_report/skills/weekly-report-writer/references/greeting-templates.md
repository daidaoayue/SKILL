# Greeting / Closing Templates

Defines opener (问候语) and closer (结束语) for incremental and baseline reports.
Picked at render-time based on `project.toml`. Designed so the output matches the
academic style of `2026春-3月第1周报-李越.docx`.

## Title prefix patterns

| Style | Pattern | Example |
| --- | --- | --- |
| 学期 + 月 + 周序 | `{学年}{季节}学期{月份}第{n}周周报` | `2026春季学期三月第一周周报` |
| 简短 | `周报 · {YYYY-MM-DD ~ MM-DD}` | `周报 · 2026-05-04 ~ 2026-05-10` |
| 项目前缀 | `{project_display_name} · 周报 · {date_range}` | `多维特征融合的低空雷达目标识别 · 周报 · 2026-05-04 ~ 05-10` |

Default: 学期 + 月 + 周序 (matches sample).

## 季节判断

- 1-2 月 / 3-6 月：春季学期
- 7-8 月：暑假
- 9-12 月：秋季学期

## 第 n 周计算

`n = (day_of_month - 1) // 7 + 1`，输出"第一周/第二周/.../第五周"。

## 中文月份

mapping = {1:"一月", 2:"二月", ..., 12:"十二月"}.

## Greeting block

```
{advisor_title}好：

向您汇报本周的学习情况，本周主要完成了 {N} 项工作：{(1) ...; (2) ...; (3) ...}
```

`{advisor_title}` 来源：

1. project.toml `[project] advisor = "陈老师"` 配置
2. 若空，默认 "老师"
3. 学生交互首次询问后写入 project.toml

## Closing block

```
祝您工作顺利，身体健康！

{student_name}

{date_range_slash}
```

`{date_range_slash}` 格式：`YYYY/M/D-YYYY/M/D`（不补零，与样例一致）。
`{student_name}` 来源：project.toml `[project] student = "..."`。

## Variants by occasion

| 场合 | 结束祝福 |
| --- | --- |
| 普通周 | 祝您工作顺利，身体健康！ |
| 节假日前 | 祝您 {假期} 快乐！ |
| 学期初 | 新学期诸事顺利！ |
| 投稿期 | 期待您的进一步指导！ |

LLM 在 Writer 阶段根据 `today_date` 自动选祝福。

## Baseline 报告变体

baseline 总报告的开场段比增量更正式：

```
{advisor_title}好：

向您汇报截至 {today_date} 的项目阶段性成果。本报告系统梳理
{project_display_name} 项目的整体进展、当前指标基线、理论方法、
风险识别与未来 3 个月路线图，作为后续每周增量周报的对照基准。
```

## 示例（来自样例 docx）

```
**2026春季学期三月第一周周报**

陈老师好：

向您汇报本周的学习情况，本周主要完成了三项工作：(1)
蒙特卡洛鲁棒性验证实验；(2)
PhaseAmp_V5b相位保留方法的原理梳理与技术总结；(3)
低空雷达目标航迹3D可视化工具开发。

[正文]

祝您工作顺利，身体健康！

李越

2026/3/3-2026/3/9
```
