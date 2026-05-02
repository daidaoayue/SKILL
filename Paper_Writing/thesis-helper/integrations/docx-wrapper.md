# docx Integration Wrapper · Word 文档操作

> **包装的 skill**：`document-skills:docx`
> **触发场景**：thesis-helper Phase 5 (LaTeX → Word) + 学校 Word 模板填充 + 导师批注合并

## 三个使用场景

### 场景 1 · LaTeX 转 Word（最常用）

毕设流程 Phase 5 触发。底层调用 [`extensions/latex-to-word`](../extensions/latex-to-word/SKILL.md)
完成主转换，本 wrapper 负责后处理：

```text
extensions/latex-to-word/converter.py 输出原始 .docx
   ↓
本 wrapper 调用 document-skills:docx 做后处理：
   ├── 应用学校 Word 模板（页眉/页脚/封面页）
   ├── 修复公式编号样式
   ├── 修复图表交叉引用样式
   ├── 应用学校字体规范（标题/正文/图注）
   └── 生成目录（Word 自动目录，非 LaTeX 编译版）
```

### 场景 2 · 填充学校 Word 模板

部分学校（清华/北大/北航）提供"任务书 / 中期检查 / 开题报告"Word 模板，
学生需要按章节填空。本 wrapper：

```text
读取 <project>/格式要求/<模板>.docx
   ↓
解析模板的占位符（{{title}} / {{abstract}} / {{ch1}} ...）
   ↓
从 <project>/paper/ 提取对应内容
   ↓
调用 document-skills:docx 填充并保存
```

### 场景 3 · 导师批注合并

导师改完返回 .docx 后，需要把批注（"修订"和"评论"）合并回 LaTeX：

```text
读取 <project>/paper/main_advisor_reviewed.docx
   ↓
调用 document-skills:docx 提取所有批注
   ↓
按章节定位到 <project>/paper/sections/*.tex 对应位置
   ↓
生成 <project>/paper/advisor_comments.md（结构化）
   ↓
提示用户：哪些已采纳 / 哪些需要讨论
```

## 调用契约

### Input
```yaml
mode: latex_to_docx | template_fill | merge_comments

# Mode: latex_to_docx
input:
  tex_file: <project>/paper/main.tex
  template_docx: <project>/格式要求/template.docx (可选)
  output_path: <project>/paper/main.docx

# Mode: template_fill
input:
  template_docx: <project>/格式要求/任务书模板.docx
  data_source: <project>/paper/sections/  # 或 yaml 数据
  output_path: <project>/任务书.docx

# Mode: merge_comments
input:
  advisor_docx: <project>/paper/main_advisor_reviewed.docx
  base_tex_dir: <project>/paper/sections/
  output_md: <project>/paper/advisor_comments.md
```

### Output
均输出对应 .docx / .md，并在 `<project>/.thesis-helper/integration_log.md` 追加记录。

## 已知陷阱（来自实战经验）

```text
1. ❌ 公式：pandoc / 直接转换会把 LaTeX 公式变成 OMML，但编号和交叉引用断了
   ✅ 用 latex-to-word 的 tex4ht 路径，公式以 PNG 嵌入并保留交叉引用

2. ❌ 图表：双列 LaTeX 文档转 Word 后图表位置全乱
   ✅ 强制单列输出 + 用 docx 的 break_after_figure 选项

3. ❌ 字体：学校规范要求"宋体小四"，pandoc 默认 Calibri
   ✅ 后处理脚本应用学校 docx_template

4. ❌ 引用：\cite{xxx} 在 docx 里变成纯文本，丢失超链接
   ✅ 用 BibTeX → CSL → docx 引用样式映射

5. ❌ 批注合并：直接 diff docx 会丢失格式信息
   ✅ 用 python-docx 解析 w:comment 节点 + w:ins/w:del 修订标记
```

## 与 extensions/latex-to-word 的分工

```text
extensions/latex-to-word/   ← 主转换器（自研）
   - 输入 .tex
   - 输出 .docx 原始版本
   - 处理公式 / 图表 / 引用 / 编号

integrations/docx-wrapper   ← 后处理（本文件）
   - 输入 .docx 原始版本
   - 应用学校模板 / 字体 / 页眉
   - 填充任务书 / 合并批注
   - 输出最终交付版
```

## 相关文件

- 上游 skill：`document-skills:docx`
- 同级：[`pptx-wrapper.md`](pptx-wrapper.md) [`pdf-wrapper.md`](pdf-wrapper.md)
- 下游：[`../extensions/latex-to-word/SKILL.md`](../extensions/latex-to-word/SKILL.md)
- pipeline：[`../pipelines/undergrad-thesis-pipeline.md`](../pipelines/undergrad-thesis-pipeline.md) Phase 5
