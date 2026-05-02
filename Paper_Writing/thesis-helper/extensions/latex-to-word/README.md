# latex-to-word · LaTeX → Word 高保真转换器

> thesis-helper 的扩展 skill 之一，专为国内毕设场景。

## 为什么自研

| 现成工具 | 痛点 |
|---------|------|
| pandoc 直转 | 公式编号断、交叉引用丢失、字体不合规 |
| Overleaf 导出 docx | 复杂公式渲染崩、表格全错位 |
| Word "插入 PDF" | 不可编辑、字体丢失 |
| 手动复制粘贴 | 7 万字毕设要复制 3 天 |

本 skill 用 **多路径转换 + 后处理修复** 解决：
- 公式以 MathML 嵌入（Word 原生），保编号
- 交叉引用做成 docx 书签，可点击
- 字体应用学校模板（北航/清华/北大）
- 参考文献按 GB/T 7714-2015 格式化

## 用法

最简：
```text
/latex-to-word path/to/main.tex
```

指定输出和模板：
```text
/latex-to-word path/to/main.tex --output paper.docx --template 格式要求/北航模板.docx
```

强制路径：
```text
/latex-to-word path/to/main.tex --path B    # 强制 tex4ht
```

## 三条转换路径

| 路径 | 工具链 | 适用 | 特点 |
|------|-------|------|------|
| A | pandoc + Lua filter | 简单论文 | 快但公式可能掉编号 |
| B ⭐ | tex4ht → ODT → docx | 复杂公式/交叉引用多 | 慢但保真度最高 |
| C | LaTeX → PDF → pdf2docx | 兜底 | 保视觉但失语义 |

skill 自动判断走哪条；用户也可以 `--path` 强制指定。

## 系统依赖

详见 [SKILL.md](SKILL.md) 末尾"系统依赖"章节。

## 文件

```text
latex-to-word/
├── SKILL.md      ← Claude 入口 + 完整 pipeline 定义
├── README.md     ← 本文件
└── converter.py  ← 后处理脚本（待造）
```

## 与上游 skill 的关系

```text
thesis-helper (Phase 5)
   ├── 调用本 skill 完成主转换
   └── 调用 integrations/docx-wrapper 后处理（学校模板/导师批注）
```
