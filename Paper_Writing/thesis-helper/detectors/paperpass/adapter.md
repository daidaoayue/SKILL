# PaperPass Detector Adapter · PaperPass 检测器适配

> **状态：🟡 接口预留（算法相近 CNKI，可复用 90% 规则）**
> **适用：** 国内毕设 / 期刊投稿前自查 / 比 CNKI 便宜的备查

## 与 CNKI 的关系

PaperPass 的检测算法和数据库与 CNKI 接近但不完全相同：

```text
┌────────────────────────────────────────────────────────────────────┐
│ 维度       │ CNKI                  │ PaperPass                    │
├────────────┼──────────────────────┼─────────────────────────────┤
│ 数据库     │ 中国学术 + 互联网     │ 互联网 + 部分中国学术         │
│ 算法       │ 句子级 + 段落级       │ 13 字符连续匹配               │
│ AI 检测    │ 有                    │ 较弱                          │
│ 价格       │ 贵（机构账号）        │ 便宜（学生订阅）              │
│ 公认度     │ 国内学位论文唯一终审   │ 备查 / 投稿前自查              │
│ 阈值习惯   │ 8-15%                 │ 通常 < 30%（学校规定）         │
└────────────────────────────────────────────────────────────────────┘
```

**核心策略：用 CNKI adapter 的 95% 规则，仅调整阈值。**

## 调用契约

### Input

```yaml
input:
  file_path: <project>/paper/main.tex     # 或 main.docx
  language: zh
  thesis_type: undergrad-thesis | master-thesis
  targets:
    similarity_rate_max: 30                # PaperPass 通常允许更高
    aigc_rate_max: 10                      # PaperPass AI 检测较弱，留 buffer
```

### Output

```yaml
output:
  reduced_file: <project>/paper/main_paperpass-reduced.tex
  reports:
    - <project>/paper/paperpass-reduce-report.md
  user_action_required:
    - "请购买 PaperPass 学生套餐验证"
    - "PaperPass 与 CNKI 结果不可互换，仅作初筛"
```

## 13 字符连续匹配的应对

PaperPass 核心算法是"13 字符连续匹配"（中文 6-7 个字）：

```text
- 任意 13 字符片段在数据库中找到 → 标红
- 改写策略：每 6-7 个字打断一次（同义改写、增删字）
- 引用密集段落容易撞——主动改写引文摘要部分
```

→ 复用 `aigc-reduce-rhythm` 的句长方差工具 + `aigc-reduce-vocab` 的同义替换。

## Pipeline 调用方式

```text
1. thesis-helper 解析 thesis.config.yml
2. detector == "PaperPass" → 加载本 adapter
3. 触发 Skill 链（复用 CNKI 流水线 + 阈值放宽）：
   /aigc-reduce-vocab
   /aigc-reduce-rhythm
   /aigc-reduce-cohesion
   /aigc-reduce-cite-inject
4. 提示用户：上传 PaperPass 验证（学生套餐）
5. 验证后回填 paperpass-aigc-round*.md
```

## 阈值映射

```text
学校规定上限   建议本地 buffer
< 30%         本地处理到 < 25%
< 25%         本地处理到 < 20%
< 20%         本地处理到 < 15%
```

注：PaperPass 不是国内学位论文终审，仅供初筛。**最终上交务必用 CNKI**。

## 与其他检测器的关系

```text
- ../cnki/adapter.md      生产可用 ✅（学位论文终审）
- ../turnitin/adapter.md  接口预留 🟡（海外）
- ../paperpass/adapter.md 本文件 🟡
- ../vipcs/adapter.md     占位 🚧
```

## 相关

- 上游可复用：[`../../../aigc-reduce-skills/aigc-reduce/SKILL.md`](../../../aigc-reduce-skills/aigc-reduce/SKILL.md)
- pipeline：[`../../pipelines/undergrad-thesis-pipeline.md`](../../pipelines/undergrad-thesis-pipeline.md)
