---
name: latex-to-word
description: "LaTeX → Word 高保真转换器。专为国内毕设场景设计：保留公式编号、图表交叉引用、双列布局、学校字体规范。Triggers on: '/latex-to-word', '/转 word', '/转换 word', 'LaTeX 转 Word', '论文转 Word'."
argument-hint: [tex-file] [output-docx-path]
allowed-tools: Read, Write, Edit, Bash, Glob
---

# LaTeX → Word 高保真转换器

> 国内毕设的真实痛点：写完 LaTeX 后学校要 Word 版上传查重 / 给导师批注。
> 直接 pandoc 转换 → 公式编号断、图表交叉引用丢失、字体不合规。
> 本 skill 用 **多路径转换 + 后处理修复** 解决这些问题。

## 三条转换路径（按优先级）

```text
路径 A · pandoc + Lua 过滤器           ← 简单论文（无复杂公式/表）
路径 B · tex4ht → ODT → docx           ← 复杂公式 / 交叉引用 ⭐推荐
路径 C · LaTeX → PDF → 文本提取 + 模板  ← 兜底（保格式但失语义）
```

skill 自动判断走哪条：
```text
统计 .tex 中：
   equation 数量 > 30 或 \ref{} 数量 > 50  →  走路径 B
   表格数量 > 10                          →  走路径 B
   其他                                    →  走路径 A
```

## Pipeline

### Phase 1 · 预检查

```text
1. 检查 .tex 是否能编译通过（必需）
   → 不通过 → 报错并提示先编译
2. 提取所有 \ref{} \cite{} 标号  → ref_map.json
3. 提取所有 \begin{equation}...\end{equation}  → equations.json
4. 提取所有 figure / table  → floats.json
5. 检查 \begin{document} 后的 \title{} \author{}
```

### Phase 2 · 主转换（按路径分支）

#### 路径 A · pandoc

```bash
pandoc main.tex \
    --bibliography=references.bib \
    --csl=gb-t-7714-2015-numeric.csl \
    --from=latex --to=docx \
    --reference-doc=<学校模板.docx> \
    --lua-filter=fix-equations.lua \
    --output=main.docx
```

关键：`--reference-doc` 用学校 Word 模板，保留页眉/页脚/字体。

#### 路径 B · tex4ht

```bash
make4ht -u -uf 'docx,charset=utf-8' main.tex
# 输出 main.odt
libreoffice --headless --convert-to docx main.odt
# 后处理修复
python converter.py --post-process main.docx --ref-map ref_map.json
```

为什么用 tex4ht：
- 公式以 MathML 嵌入（Word 原生支持）→ 保编号
- 交叉引用作为 docx 书签 → \ref{eq:1} 在 Word 里仍然是可点击链接
- 浮动体（figure/table）位置由 LaTeX 决定 → 不会乱跑

#### 路径 C · 兜底

复杂度高且 tex4ht 失败时使用：编译 PDF → pdf2docx 提取 → 应用学校模板。
保留视觉但失去语义（不可改公式），仅用于"提交查重"场景。

### Phase 3 · 后处理（converter.py）

```text
1. 字体应用：
   ├── 标题：黑体小三
   ├── 正文：宋体小四
   ├── 图注/表注：仿宋五号
   └── 代码：Consolas 五号
   字体规范从 <project>/格式要求/ 提取或用 school_rules 默认

2. 章节编号：
   "Chapter 1" → "第一章"  (中文毕设)
   "1.1 Section" → "1.1 节"

3. 图表编号：
   "Figure 1" → "图 1-1"  (按章节编号)
   "Table 1" → "表 1-1"

4. 公式编号：
   保持 (1.1) (1.2) 格式 + 右对齐

5. 参考文献样式：
   GB/T 7714-2015（国内毕设标准）

6. 页眉页脚：
   学校规范（北航：奇偶页不同）
```

### Phase 4 · 验证

```text
1. 用 python-docx 打开输出 .docx
2. 检查：
   ├── 公式数量 == 原 LaTeX 数量
   ├── 图表数量 == 原 LaTeX 数量
   ├── 交叉引用数量 == 原 LaTeX 数量（不能丢）
   ├── 参考文献条数 == 原 .bib 引用数量
   └── 字数 ≈ 原 LaTeX 估算（差异 ±10% 内）
3. 输出 conversion_report.md
```

## 输出

```text
<project>/paper/main.docx                       # 转换结果
<project>/paper/conversion_report.md            # 转换报告
<project>/paper/conversion_warnings.md          # 警告（如丢失的交叉引用）
<project>/.thesis-helper/conversion_path.json   # 用了哪条路径
```

## Constants

```yaml
DEFAULT_PATH: B                          # tex4ht（推荐）
PANDOC_MIN_VERSION: "2.19"
TEX4HT_REQUIRED: true                    # 路径 B 必需
LIBREOFFICE_REQUIRED: true               # 路径 B 必需
DEFAULT_CSL: gb-t-7714-2015-numeric     # 中文毕设
FALLBACK_TO_PATH_A_ON_FAILURE: true     # B 失败回退 A
SCHOOL_TEMPLATES:
  buaa_undergrad: 北航本科毕设模板.docx
  tsinghua_master: 清华硕士毕设模板.docx
  pku_undergrad: 北大本科毕设模板.docx
```

## 系统依赖

```text
必需：
  - pandoc >= 2.19
  - python >= 3.9
  - python-docx
  - lxml

路径 B 额外需要：
  - tex4ht / make4ht (TeXLive 自带)
  - libreoffice (用于 odt → docx)

路径 C 额外需要：
  - pdf2docx
```

Windows 用户：
```powershell
# pandoc
choco install pandoc
# libreoffice
choco install libreoffice-fresh
# python deps
pip install python-docx lxml pdf2docx
```

## 三条红线

- ❌ 不允许丢失公式编号或交叉引用——必须验证
- ❌ 不允许字体不合规——必须应用学校模板
- ❌ 不允许"差不多就行"——验证通过才算完成

## 与上游的关系

```text
thesis-helper (Phase 5)
   └── 调用本 skill
       └── 调用 integrations/docx-wrapper（后处理学校模板）
```

## Owner 闭环承诺

- 转换失败 → 自动回退路径 + 报告原因
- 验证未通过 → 不算完成
- 字体不合规 → 不算完成
- 转换报告未生成 → 不算完成

> 因为信任所以简单——把 Word 这件烦人的事，做成一次性闭环。
