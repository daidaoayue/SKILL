# VIPCS Detector Adapter · 维普 (VIP) 检测器适配

> **状态：🟡 接口预留（部分高校采用维普代替知网）**
> **适用：** 部分本科院校 / 部分高职院校 / 期刊投稿前自查

## 与 CNKI / PaperPass 的关系

```text
┌────────────────────────────────────────────────────────────────────┐
│ 维度       │ CNKI            │ 维普 VIPCS         │ PaperPass      │
├────────────┼───────────────┼──────────────────┼────────────────┤
│ 数据库     │ 中国学术 + 互联网 │ 中文期刊 + 维普库  │ 互联网 + 部分学术│
│ 算法       │ 句段双层匹配     │ 连续 12-15 字     │ 13 字符匹配    │
│ AI 检测    │ 强               │ 中等              │ 弱             │
│ 价格       │ 贵               │ 中                │ 便宜           │
│ 院校采用   │ 985/211 主流    │ 部分本科/高职     │ 个人备查       │
│ 阈值习惯   │ 8-15%            │ 20-30%            │ 30%+           │
└────────────────────────────────────────────────────────────────────┘
```

## 调用契约

### Input

```yaml
input:
  file_path: <project>/paper/main.tex     # 或 main.docx
  language: zh
  thesis_type: undergrad-thesis | master-thesis
  targets:
    similarity_rate_max: 25
    aigc_rate_max: 15
```

### Output

```yaml
output:
  reduced_file: <project>/paper/main_vipcs-reduced.tex
  reports:
    - <project>/paper/vipcs-reduce-report.md
  user_action_required:
    - "请上传维普官网验证"
```

## 维普特性

```text
1. 中文期刊数据库强 → 期刊综述章是重灾区
2. 12-15 字符连续匹配 → 类似 PaperPass，复用同套打断策略
3. 引用密集容易标红 → 必须显式标 "..."[X] 格式
4. 互联网内容覆盖比 CNKI 少 → 维基百科类来源相对安全
```

## Pipeline 调用方式

```text
1. thesis-helper 解析 thesis.config.yml
2. detector == "VIPCS" → 加载本 adapter
3. 触发 Skill 链（复用 CNKI 流水线 + 维普特化）：
   /aigc-reduce-vocab
   /aigc-reduce-cite-inject  ← 维普对引用格式敏感
   /aigc-reduce-rhythm
4. 用户上传维普官网验证
5. 验证后回填 vipcs-aigc-round*.md
```

## 阈值映射（学校规定）

```text
本科院校（部分采用维普）：
  - 文科类：< 30%
  - 理工类：< 25%
  - 重点学科：< 20%

高职院校：
  - 通常 < 30%

→ 本地处理建议留 5-10% buffer
```

## 与其他检测器的关系

```text
- ../cnki/adapter.md      生产可用 ✅
- ../turnitin/adapter.md  接口预留 🟡
- ../paperpass/adapter.md 接口预留 🟡
- ../vipcs/adapter.md     本文件 🟡
```

## 相关

- 上游可复用：[`../../../aigc-reduce-skills/aigc-reduce/SKILL.md`](../../../aigc-reduce-skills/aigc-reduce/SKILL.md)
- pipeline：[`../../pipelines/undergrad-thesis-pipeline.md`](../../pipelines/undergrad-thesis-pipeline.md)
