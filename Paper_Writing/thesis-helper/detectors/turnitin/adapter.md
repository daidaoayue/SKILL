# Turnitin Detector Adapter · Turnitin 检测器适配

> **状态：🟡 接口预留 · 等待真实数据迭代**
> **适用：** 海外期刊 / 海外大学硕博毕设 / 国际会议

## 调用契约

### Input

```yaml
input:
  file_path: <project>/paper/main.tex     # 或 main.docx
  language: en                             # Turnitin 主要英文
  thesis_type: journal | master-thesis | phd-thesis
  targets:
    similarity_index_max: 15               # Turnitin Similarity Index 上限 (%)
    ai_writing_max: 20                     # AI Writing Indicator 上限 (%)
  exclusions:
    quotes: true                           # 排除引用
    bibliography: true                     # 排除参考文献
    small_matches_below_words: 8           # 小于 N 词的匹配不计
```

### Output

```yaml
output:
  reduced_file: <project>/paper/main_turnitin-reduced.tex
  reports:
    - <project>/paper/turnitin-reduce-report.md
    - <project>/paper/turnitin-trace.md
  user_action_required:
    - "请上传到机构 Turnitin 账号验证"
    - "推荐使用 Turnitin Draft Coach (Word 插件) 实时检查"
  metrics:
    similarity_index_before: <float>%
    similarity_index_after_local_estimate: <float>%
    ai_writing_indicator_estimate: <float>%
```

## 与 CNKI adapter 的关键差异

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 维度          │ CNKI                  │ Turnitin                       │
├───────────────┼──────────────────────┼───────────────────────────────┤
│ 主语言        │ 中文                  │ 英文（多语言版有限）            │
│ 数据库        │ 中国学术库 + 互联网    │ 全球期刊 + 学位论文 + 互联网    │
│ AI 检测       │ AI 比例               │ AI Writing Indicator           │
│ 引用排除      │ 用户手动              │ 可自动（quoted_words）          │
│ 自引识别      │ 弱                    │ 强（按机构内 ID 匹配）          │
│ 触发关键词    │ 学术规范化语言         │ 通用学术 + 模板语言             │
│ 阈值习惯      │ 8-15%                 │ 15-25%（更宽松）               │
└──────────────────────────────────────────────────────────────────────┘
```

## 降痕策略（基于 Turnitin 公开特性）

### 1. Quoted text 必加引号 + 引用

Turnitin 自动识别 `"..."` 和 `\textquote{}` 内的内容并排除。
**关键**：直接引用必须加 cite，否则即使有引号也会标红。

### 2. AI Writing Indicator 应对

Turnitin 的 AI 检测和 GPTZero / Originality.ai 类似：
- 困惑度（Perplexity）低 → 标 AI
- Burstiness（句长方差）小 → 标 AI
- 重复模板短语（"In conclusion" / "Furthermore"）→ 标 AI

→ 可复用 thesis-helper 的 `aigc-reduce-perplexity` + `aigc-reduce-cohesion` skill。

### 3. Bibliography exclusion

`\bibliography{}` 内容默认排除——但脚注、appendix 内的非标准引用要手动加 cite。

### 4. Small matches 不计

Turnitin 默认 8 词以下匹配不计。**不要被诱导写得"太顺"**——保留学术常用 phrase
即可，硬避反而扣 burstiness。

## Pipeline 调用方式（thesis-helper 内部）

```text
1. thesis-helper 解析 thesis.config.yml
2. detector == "Turnitin" → 加载本 adapter
3. 触发 Skill 链：
   /aigc-reduce-perplexity (复用)
   /aigc-reduce-cohesion (复用)
   /aigc-reduce-vocab     (复用，删通用模板词)
4. 提示用户：上传到机构 Turnitin Originality Check
5. 用户手填 CNKI-style 反馈到 cnki-aigc-round1.md（命名兼容）
```

## 阈值映射

```text
┌──────────────────────────────────────────────────────────────────────┐
│ 场景             │ Similarity Index │ AI Writing Indicator           │
├──────────────────┼─────────────────┼────────────────────────────────┤
│ IEEE/Springer    │ < 15%            │ < 20%                          │
│ Elsevier         │ < 20%            │ < 20%                          │
│ Nature 系列      │ < 10%            │ < 15%                          │
│ 海外硕博毕设      │ < 15-25%（学校）│ < 20%                          │
└──────────────────────────────────────────────────────────────────────┘
```

## 待迭代

- 🚧 Turnitin AI Writing Indicator 算法尚不公开，需要积累实测数据校准
- 🚧 Originality.ai / GPTZero 互相对照
- 🚧 Quoted text 自动包装工具

## 与其他检测器的关系

```text
- ../cnki/adapter.md      生产可用 ✅（中文）
- ../turnitin/adapter.md  本文件 🟡（英文/海外）
- ../paperpass/adapter.md 占位 🚧（中文备查）
- ../vipcs/adapter.md     占位 🚧（部分高校）
```

## 相关

- 上游可复用：[`../../../aigc-reduce-skills/aigc-reduce/SKILL.md`](../../../aigc-reduce-skills/aigc-reduce/SKILL.md)
- pipeline：[`../../pipelines/journal-pipeline.md`](../../pipelines/journal-pipeline.md)
