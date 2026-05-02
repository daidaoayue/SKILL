# pptx Integration Wrapper

> **包装的 skill**：`document-skills:pptx` (PPT 操作 — 创建/读取/编辑)
> **触发**：Beamer→PPTX 转换 / 学校 PPT 模板填充 / PPT 后处理

## Input
```yaml
mode: beamer_to_pptx | template_fill | edit | extract_text

# beamer_to_pptx
input:
  beamer_pdf: <project>/slides/slides.pdf
  beamer_tex: <project>/slides/slides.tex
  output_path: <project>/slides/slides.pptx

# template_fill
input:
  template_pptx: <project>/格式要求/答辩模板.pptx
  data_source: <project>/paper/sections/   # 提取章节内容填充
  output_path: <project>/slides/answer.pptx
```

## Output
```text
<project>/slides/<name>.pptx        # 转换/填充结果
<project>/.thesis-helper/integration_log.md   # 日志追加
```

## thesis-helper 调用条件

```text
config.integrations.pptx: true
   或被以下 skill 调用：
   - paper-slides (Beamer → PPTX 备选)
   - thesis-defense-prep (答辩 PPT 必交 PPTX)
```

## 触发流程（典型 beamer_to_pptx）

```text
1. paper-slides 输出 slides.pdf + slides.tex
2. 本 wrapper 调用 document-skills:pptx 把 PDF/Beamer 转 PPTX
3. 后处理：保留标题层级 / bullets / 图片
4. 学校系统/活动方多数只接受 PPTX，不接受 PDF
```

## 已知陷阱

- Beamer 高级动画在 PPTX 丢失（学校/活动方系统也不支持，可接受）
- 公式可能渲染为图片（保编号但不可二次编辑）
- 中文字体在 macOS PPTX 打开可能被替换 → 建议嵌入字体

## 相关

- 同级：[`docx-wrapper.md`](docx-wrapper.md) [`pdf-wrapper.md`](pdf-wrapper.md)
- 上游：[`paper-slides-wrapper.md`](paper-slides-wrapper.md)
- pipeline：conference Phase 5 / 毕设 Phase 8
