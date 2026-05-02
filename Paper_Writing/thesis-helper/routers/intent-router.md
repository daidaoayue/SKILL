# Intent Router · 论文类型路由规则

> 输入：`thesis.config.yml` 的 `thesis_type` 字段（必填）+ ProjectMap.json
> 输出：完整调用链 + 触发的 integrations + 触发的 extensions

## 决策树（顶层 SKILL.md 按此执行）

```text
读 thesis_type
   │
   ├── "journal"             → journal-pipeline.md
   ├── "conference"          → conference-pipeline.md
   ├── "undergrad-thesis"    → undergrad-thesis-pipeline.md
   ├── "master-thesis"       → master-thesis-pipeline.md
   └── 其他/缺失              → 走交互式 config 生成（SKILL.md Phase 0-D）
```

## 四种类型的调用链对照

| 步骤 | journal | conference | undergrad-thesis | master-thesis |
|------|:-------:|:----------:|:----------------:|:-------------:|
| /research-lit (前置) | ✓ | ✓ | △ | △ |
| /comm-lit-review | △ | △ | ✓ (理工科) | ✓ |
| /novelty-check | ✓ (投稿前) | ✓ | ✗ | △ |
| /paper-writing | ✓ | ✓ | ✓ | ✓ |
| /scientific-visualization | ✓ | ✓ | △ | △ |
| /paper_reviewer (自审) | ✓ | ✓ | ✓ | ✓ |
| /aigc降低 | ✗ | ✗ | ✓ (≤8%) | ✓ (≤5%) |
| /latex-to-word | ✗ | ✗ | ✓ | ✓ |
| /thesis-defense-prep | ✗ | △ | ✓ | ✓ |
| /thesis-blind-review | ✗ | ✗ | ✗ | ✓ |
| /bilingual-abstract | ✗ | ✗ | ✓ | ✓ |
| /format-compliance-checker | ✗ | △ | ✓ | ✓ |
| /paper-slides | △ | ✓ | △ | ✓ |
| /paper-poster | ✗ | ✓ | ✗ | ✗ |
| /rebuttal (投稿后) | ✓ | ✓ | ✗ | ✗ |

✓ 默认开 / △ 配置可开 / ✗ 默认关

## 路由规则细节

### Rule 1 · 检测器自动绑定

```text
thesis_type == "undergrad-thesis" or "master-thesis"
   且 detector 字段缺失
   → 默认 detector = "CNKI"

thesis_type == "journal" or "conference"
   且 detector 字段缺失
   → 默认 detector = "none"（期刊/会议不查）
```

### Rule 2 · 阈值自动绑定

```text
thesis_type == "undergrad-thesis" → aigc_rate_max=8, duplicate_rate_max=8
thesis_type == "master-thesis"    → aigc_rate_max=5, duplicate_rate_max=5
thesis_type == "journal"          → 跳过 aigc-reduce
thesis_type == "conference"       → 跳过 aigc-reduce + 强制开 paper-slides + paper-poster
```

config 显式设置的 `targets.*` 字段优先级最高，覆盖默认。

### Rule 3 · 学校规则覆盖

```text
config.school_rules.<key> 命中（按 venue 字段查找）
   → 用学校规则覆盖默认阈值

示例：venue == "北航" 且 thesis_type == "undergrad-thesis"
   → 找 school_rules.buaa_undergrad
   → aigc_hidden_redline=true 触发 aigc-reduce 强制运行
```

### Rule 4 · 语言绑定文献综述

```text
language == "zh" → 优先 /comm-lit-review (中文领域综述)
language == "en" → 优先 /research-lit (英文综述)
```

### Rule 5 · 缺失 narrative 报告 → 引导生成

```text
config.narrative.report_path 缺失或文件不存在
   且 config.narrative.topic 为空
   → 暂停 pipeline，提示用户：
     "我需要 NARRATIVE_REPORT.md 或论文主题。
      要不要我先用 /research-refine 帮你细化研究方案？"
```

## 输出格式（路由决策后写入 .thesis-helper/）

```yaml
# .thesis-helper/route_decision.yml
route_decision:
  thesis_type: undergrad-thesis
  pipeline: undergrad-thesis-pipeline.md
  detector: CNKI
  effective_targets:
    aigc_rate_max: 8
    duplicate_rate_max: 8
  enabled_integrations:
    - research-lit
    - paper_reviewer
    - mermaid-diagram
    - paper-illustration
    - docx
  enabled_extensions:
    - latex-to-word
    - thesis-defense-prep
    - bilingual-abstract
    - format-compliance-checker
  triggered_by:
    - "config.thesis_type=undergrad-thesis"
    - "config.school_rules.buaa_undergrad.aigc_hidden_redline=true"
```

后续 pipeline 直接读这份决策文件，不重复路由。

## 与 venue-router / detector-router 的关系

```text
intent-router (本文件)
   ├── 决定 pipeline 文件
   └── 委托：
       ├── venue-router.md       → 按 venue 字段映射学校规则
       └── detector-router.md    → 按 detector 字段映射检测器 adapter
```

venue-router 和 detector-router 在 Batch 3 实现。当前 v0.1 路由直接走 SKILL.md
中的硬编码规则。
