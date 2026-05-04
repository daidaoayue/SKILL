**{semester} 项目工作总报告**

{advisor_title}好：

向您汇报截至 {today_date} 的项目阶段性成果。本报告系统梳理 {project_display_name} 项目的整体进展、当前指标基线、理论方法、风险识别与未来 3 个月路线图，作为后续每周增量周报的对照基准。

# 一、项目背景与目标
{从 project.toml.domain + paper bucket 抽取项目说明}

# 二、整体架构概览
{按 bucket 列出主目录及其职责}

| 模块 | 职责 | 文件数 |
| --- | --- | --- |

{若 figures bucket 命中"architecture/overview"类，嵌入架构图：}
![架构图](images/{architecture_overview})

# 三、已完成的核心实验链
{每条 family_key 一个 H2 子节，含历史方法演进 V4→V5a→V5b 这种叙事}

# 四、当前指标基线
{全工程指标全景表 + 配图 box plot/CI 图}

# 五、理论与方法总结
{从 theory + paper bucket 抽核心公式块}

# 六、推进中的工作

# 七、已识别的风险与未解问题

# 八、未来 3 个月路线图
{由 baseline-roadmap-prompt.md 生成的四象限内容}

## 8.1 科学问题

## 8.2 方法路线
### Milestone 1（截至 YYYY-MM）
- 子问题 / 假设 / 成功标志 / 风险与 Plan B
### Milestone 2
### Milestone 3

## 8.3 预期产出
- 论文：目标 venue + 投稿日期
- 专利 / 开源 / Demo
- 节点：中期 / 答辩

## 8.4 资源与协作
- 计算 / 导师 / 外部合作

# 九、给老师的统一汇报点
{interview baseline ⑤}

祝您工作顺利，身体健康！

{student_name}

{baseline_date_slash}

---
*Auto-generated baseline by weekly-report-writer v1.0 · {scanned_at}*
*后续按周做增量，下次跑会基于本份生成 W{first_week} 增量周报。*
