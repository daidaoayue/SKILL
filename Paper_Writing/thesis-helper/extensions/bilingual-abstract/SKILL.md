---
name: bilingual-abstract
description: "中英文摘要平行对照检查。字数/关键词/段落/术语四维度对齐，专为国内毕设（中英摘要必有）和双语期刊设计。Triggers on: '/bilingual-abstract', '/中英摘要', '/摘要对齐', '/检查摘要', 'bilingual abstract', 'abstract align'."
argument-hint: [paper-tex-or-abstract-files]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Bilingual Abstract · 中英文摘要平行对照检查

> 国内毕设/双语期刊都要求中英文摘要并列。学生最常踩的坑：
> - 字数比例失衡（中文 800 字英文 100 词）
> - 关键词数量不一致（中文 5 个英文 3 个）
> - 关键术语翻译不统一（"目标识别" 一会 target recognition 一会 target classification）
> - 段落结构不对应

## 四维度检查 + 一项术语一致性

```text
维度 1 · 字数比例    中文字数 vs 英文词数（推荐范围 1.5:1 ~ 2.5:1）
维度 2 · 关键词数量   中英文 keywords 数量必须相等（毕设通常 3-5 个）
维度 3 · 关键词翻译   每个中文 keyword 必须有对应英文翻译
维度 4 · 段落结构    中英摘要段落数一致 + 每段语义对应

附加 · 术语一致性     全文核心术语在 abstract / abstract_en 中翻译统一
```

## Pipeline

### Phase 1 · 提取中英文摘要

输入：`<project>/paper/main.tex` 或单独的 `abstract.tex` / `abstract_en.tex`

提取规则（按优先级匹配）：

```text
模式 1 · LaTeX 命令
  \begin{abstract} ... \end{abstract}
  \begin{abstract_en} ... \end{abstract_en}
  \input{data/abstract.tex} → 解析对应文件

模式 2 · 中文学校模板
  \chinaabstract{...}
  \englishabstract{...}

模式 3 · Markdown
  ## 摘要 ... ## Abstract
  ## 中文摘要 ... ## English Abstract
```

输出中间产物：
```text
.bilingual-check/
├── abstract_zh.txt        # 提取的中文摘要纯文本
├── abstract_en.txt        # 提取的英文摘要纯文本
├── keywords_zh.txt        # 中文关键词
└── keywords_en.txt        # 英文关键词
```

### Phase 2 · 字数比例检查

```python
zh_chars = count_chinese_characters(abstract_zh)   # 不计标点
en_words = count_english_words(abstract_en)
ratio = zh_chars / en_words
```

合规区间（默认）：

```text
本科毕设：300 ≤ zh_chars ≤ 600   200 ≤ en_words ≤ 350   1.5 ≤ ratio ≤ 2.5
硕士毕设：500 ≤ zh_chars ≤ 1000  350 ≤ en_words ≤ 600   1.5 ≤ ratio ≤ 2.5
期刊（IEEE）: 150 ≤ zh_chars ≤ 300  100 ≤ en_words ≤ 250  1.5 ≤ ratio ≤ 2.0
```

学校规则可在 `school_rules.<key>.abstract_word_limits` 覆盖。

### Phase 3 · 关键词数量与翻译对齐

提取 keywords：

```text
中文：\keywords{雷达; 目标识别; 多特征融合; 门控机制}
英文：\keywords_en{Radar; Target Recognition; Multi-feature Fusion; Gating Mechanism}
```

检查：

```text
1. 数量必须相等（不等 = ERROR）
2. 顺序对应：第 N 个中文 ↔ 第 N 个英文
3. 翻译一致性：每个 (zh_kw, en_kw) 对查 abstract 中两边是否都用统一表达
```

### Phase 4 · 段落结构对齐

```python
zh_paragraphs = split_paragraphs(abstract_zh)
en_paragraphs = split_paragraphs(abstract_en)

if len(zh_paragraphs) != len(en_paragraphs):
    error("段落数不一致")

for i, (zh, en) in enumerate(zip(zh_paragraphs, en_paragraphs)):
    # 用语义嵌入 + cosine 相似度判断对应
    similarity = sentence_transformers.similarity(zh, en)
    if similarity < 0.5:
        warning(f"段落 {i+1} 语义对应度低：{similarity:.2f}")
```

兜底：若无 sentence_transformers，用关键词重叠率（每段 top-5 关键词在另一边出现的比例）。

### Phase 5 · 术语一致性扫描

提取全文核心术语（`<project>/.thesis-helper/glossary.json` 若有则用，否则从 abstract keywords + introduction 自动提取）：

```text
对每个核心术语：
  - 中文形式 + 全文出现次数
  - 英文翻译候选（在 abstract_en 和 全文括注中找）
  - 检查：是否出现多种翻译
  
示例：
  ✗ "目标识别" 翻译有 3 种：
    - target recognition  (abstract_en, ch3)
    - target classification  (ch4)
    - target identification  (ch5)
  → 必须统一为 "target recognition"
```

输出术语一致性表 → `glossary_check.md`。

### Phase 6 · 输出报告

```markdown
# Bilingual Abstract Check Report

## 总评：⚠️ 3 个问题需修

### Phase 2 · 字数比例 ✅ PASS
- 中文：512 字 (合规区间 500-1000)
- 英文：231 词 (合规区间 350-600) ⚠️ 偏少
- 比例：2.22 ✅

### Phase 3 · 关键词 ❌ FAIL
- 数量：中文 5 个 vs 英文 4 个
- 缺失翻译：「相位特征」无对应 English keyword
- 建议：补 "Phase Feature"

### Phase 4 · 段落结构 ⚠️ WARN
- 段落数：3 vs 3 ✅
- 段落 2 语义对应度 0.42（低于阈值 0.5）
- 建议：检查英文第 2 段是否完整翻译了"门控融合机制"部分

### Phase 5 · 术语一致性 ❌ FAIL
- "目标识别" 有 3 种英文翻译 → 见 glossary_check.md
- 建议：统一为 "target recognition"

## 修复建议（按优先级）
1. [P0] 补充 keywords_en 缺失项
2. [P0] 统一术语翻译
3. [P1] 扩展英文摘要至 350+ 词
4. [P2] 调整段落 2 翻译完整度
```

输出：`<project>/paper/abstract_check_report.md`

### Phase 7 · 闭环验证

```yaml
✅ 验证清单
- [ ] 中英摘要均成功提取（非空）
- [ ] 字数都在合规区间
- [ ] 关键词数量相等
- [ ] 每个 keyword 有对应翻译
- [ ] 段落数一致
- [ ] 术语翻译统一（全文）
- [ ] 报告已生成
```

## Constants

```yaml
DEFAULT_RATIO_RANGE: [1.5, 2.5]
PARAGRAPH_SIMILARITY_THRESHOLD: 0.5
SENTENCE_TRANSFORMERS_MODEL: "paraphrase-multilingual-MiniLM-L12-v2"
FALLBACK_TO_KEYWORD_OVERLAP: true
SUPPORTED_THESIS_TYPES:
  - undergrad-thesis    # 300-600 字 / 200-350 词
  - master-thesis       # 500-1000 字 / 350-600 词
  - phd-thesis          # 800-1500 字 / 500-800 词
  - journal-ieee        # 150-300 字 / 100-250 词
  - journal-springer    # 150-300 字 / 100-250 词
```

## 与上游的关系

```text
thesis-helper Phase 6 调本 skill
   ├── 读 thesis_type / school_rules → 决定字数区间
   ├── 读 paper/main.tex → 提取双摘要
   └── 输出 abstract_check_report.md
```

## Owner 闭环承诺

- ❌ 摘要提取失败 → 必须报错并提示用户检查 LaTeX 命令名
- ❌ 报告未生成 → 不算完成
- ❌ ERROR 级问题未列修复建议 → 不算完成

> 因为信任所以简单——摘要是论文门面，差一个翻译都让审稿人皱眉。
