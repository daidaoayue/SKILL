<!-- markdownlint-disable MD032 -->
# thesis-blind-review · 硕博毕设盲审版生成

> thesis-helper extension · 状态：✅ Batch B 实现

## 一句话价值

输入：硕/博毕设 `paper/` 目录 + 作者身份信息。

输出 `paper_blind/` 目录，自动完成：

- 封面、致谢、自引、项目编号全部匿名
- PDF 元数据已清
- 图表元数据已清
- 输出待人工核查清单（校徽 / 合影类）

## 必须去除的 9 类信息

```text
1. 封面信息（标题/作者/学号/导师/学院/学校/专业/答辩日期）
2. 致谢节
3. 自引文献（按作者名匹配 references.bib）
4. 项目编号（基金号/863/973/重点研发）
5. 实验室/课题组（PI 姓名/课题组缩写/Lab 名）
6. 个人化语句（"本人/我"→"本研究"）
7. 数据/平台标识（学校超算/内部数据集名）
8. 图表水印（校徽/课题组 logo/合影）⚠️ 人工核查
9. 文件元数据（PDF/图片的 Author/Creator）
```

## 用法

```text
# thesis-helper 自动调用（master/phd 类型）
/thesis-helper D:\my-thesis-project --type master-thesis

# 独立调用（已有 paper/ 目录）
/thesis-blind-review path/to/paper/
```

## 身份信息来源

| 来源 | 优先级 |
|------|--------|
| `thesis.config.yml` 的 identity 字段 | 1 (最高) |
| 命令行参数 `--author "张三" --advisor "李四"` | 2 |
| 从 `paper/main.tex` 自动提取 `\author{}` 等 | 3 |
| 交互式询问 | 4 (兜底) |

## 输出

```text
paper_blind/
├── main.tex                          匿名化 LaTeX
├── main.pdf                          匿名化 PDF（含 metadata 清理）
├── sections/*.tex                    各章节
├── references.bib                    已剔除自引
└── figures/*                         元数据已清

paper_blind/blind_review_report.md    完整修改清单
paper_blind/blind_review_diff.md      修改前后差异
paper_blind/blind_review_manual_check.md   ⚠️ 人工核查清单
```

## 与 latex-to-word 的兼容

```text
完整毕设交付链：
  paper/main.tex (原版)
    ↓
  thesis-blind-review → paper_blind/main.tex (匿名版)
    ↓
  latex-to-word → paper_blind/main.docx (匿名 Word，盲审上传)
```

## 系统依赖

```text
必需：
  - pdftk 或 exiftool（PDF/图片元数据清理）
  - LaTeX 全套（重编盲审版 PDF）

Windows 安装：
  choco install exiftool
  choco install pdftk-server
```

## 相关

- [SKILL.md](SKILL.md) — 完整 pipeline
- [`../latex-to-word/SKILL.md`](../latex-to-word/SKILL.md) — 配合输出 Word 盲审版
- master-thesis-pipeline.md（Batch 3 实现）
