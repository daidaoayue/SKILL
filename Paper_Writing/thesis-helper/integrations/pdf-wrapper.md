# pdf Integration Wrapper

> **包装的 skill**：`document-skills:pdf` (PDF 操作 — 合并/分割/旋转/水印/元数据/提取)
> **触发**：投稿包打包 / 盲审版 PDF 元数据清理 / 多文件合并

## Input
```yaml
mode: merge | split | rotate | watermark | clean_metadata | extract_text

# merge (投稿打包)
input:
  files:
    - main.pdf
    - supplementary.pdf
    - appendix.pdf
  output: submission_combined.pdf

# clean_metadata (盲审用)
input:
  pdf: paper_blind/main.pdf
  remove: [author, creator, producer, title]

# extract_text (审稿意见解析)
input:
  pdf: review_letter.pdf
  output_md: review_letter.md
```

## Output
```text
对应 PDF 或 .md 文件
```

## thesis-helper 调用条件

```text
config.integrations.pdf: true
   或被以下 skill 调用：
   - thesis-blind-review (Phase 9 必清 PDF metadata)
   - rebuttal (审稿意见 PDF → markdown 解析)
   - paper-writing (合并 main + appendix + supplementary)
```

## 关键场景

### 1. 盲审 PDF 元数据清理

```text
PDF metadata 含 \author{} 字段或导出工具信息时，评委 Acrobat 一点就看到。
本 wrapper 用 exiftool / pdftk 清除：
  - Author / Creator / Producer / Title
  - XMP metadata
  - 嵌入字体的 vendor 信息
```

### 2. 投稿包合并

```text
IEEE / Elsevier 要求单一 PDF：
  main.pdf + supplementary.pdf → submission.pdf (含目录)
NeurIPS / ICLR：分开上传 main + appendix。
```

### 3. 审稿意见 PDF → Markdown

```text
许多期刊邮件附 PDF 审稿意见。
本 wrapper 用 pdfplumber 提取文本 → 注入 rebuttal-wrapper。
```

## 系统依赖

```text
- pdftk-server 或 qpdf
- exiftool
- pdfplumber (Python)
```

## 相关

- 同级：[`docx-wrapper.md`](docx-wrapper.md) [`pptx-wrapper.md`](pptx-wrapper.md)
- 上游：[`../extensions/thesis-blind-review/SKILL.md`](../extensions/thesis-blind-review/SKILL.md) [`rebuttal-wrapper.md`](rebuttal-wrapper.md)
- pipeline：master-thesis Phase 8 / journal Phase 8
