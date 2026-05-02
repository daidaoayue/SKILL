<!-- markdownlint-disable MD032 -->
# bilingual-abstract · 中英文摘要平行对照检查

> thesis-helper extension · 状态：✅ Batch B 实现

## 一句话价值

输入论文 LaTeX，自动检查中英文摘要的：

- 字数比例（中文字数 / 英文词数 ≈ 1.5~2.5）
- 关键词数量一致 + 翻译对齐
- 段落结构对应（语义相似度）
- 全文术语翻译一致性

## 解决的真实痛点

```text
学生最常踩的坑：
  ✗ 中文摘要 800 字，英文摘要只有 100 词（比例失衡）
  ✗ 中文 5 个 keyword，英文只列了 3 个
  ✗ "目标识别" 一会 target recognition 一会 target classification
  ✗ 英文摘要漏翻了"门控融合机制"那一段
```

## 用法

```text
# thesis-helper 自动调用（Phase 6）
/thesis-helper D:\my-thesis-project

# 独立调用
/bilingual-abstract path/to/paper/main.tex

# 指定单独的摘要文件
/bilingual-abstract abstract.tex --en abstract_en.tex
```

## 字数合规区间（按论文类型）

```text
本科毕设  300-600 字  /  200-350 词
硕士毕设  500-1000 字 /  350-600 词
博士毕设  800-1500 字 /  500-800 词
IEEE 期刊 150-300 字  /  100-250 词
```

`school_rules.<key>.abstract_word_limits` 可覆盖默认。

## 输出

```text
.bilingual-check/                     中间产物
├── abstract_zh.txt
├── abstract_en.txt
├── keywords_zh.txt
└── keywords_en.txt

paper/abstract_check_report.md        主报告
paper/glossary_check.md               术语一致性表
```

## 报告示例

```markdown
# 总评：⚠️ 3 个问题需修

## 字数比例 ✅ PASS
## 关键词 ❌ FAIL — 中 5 vs 英 4
## 段落结构 ⚠️ WARN — 段落 2 语义对应 0.42
## 术语一致性 ❌ FAIL — "目标识别" 3 种翻译

## 修复建议（按优先级）
1. [P0] 补 English keyword "Phase Feature"
2. [P0] 统一 "目标识别" → target recognition
...
```

## 系统依赖

```text
基础（必需）：
  - python >= 3.9

可选（语义对齐增强）：
  - sentence-transformers
  - paraphrase-multilingual-MiniLM-L12-v2 模型

无 sentence-transformers → 自动降级到关键词重叠率算法。
```

## 相关

- [SKILL.md](SKILL.md) — 完整 pipeline
- [`../../pipelines/undergrad-thesis-pipeline.md`](../../pipelines/undergrad-thesis-pipeline.md) Phase 6
