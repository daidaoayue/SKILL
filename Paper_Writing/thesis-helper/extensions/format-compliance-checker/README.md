<!-- markdownlint-disable MD032 -->
# format-compliance-checker · 学校格式规范自动检查

> thesis-helper extension · 状态：✅ Batch B 实现

## 一句话价值

输入 `paper/main.tex` + 学校（自动识别）。

输出：

- 8 大类格式合规报告（字号/段落/页面/页眉/章节/图表/公式/参考文献）
- 自动可修复项 patch（一键应用）
- 不可修复项的人工待修清单

## 8 类检查项

```text
A. 字号字体    标题/正文/脚注/图注/表注/代码/公式
B. 段落格式    行距/段距/首行缩进/对齐
C. 页面布局    页边距/装订线/页眉页脚位置
D. 页眉页脚    奇偶页/章节标记/页码
E. 章节编号    "第 X 章" / X.Y / X.Y.Z
F. 图表编号    "图 X-Y" / "Table X-Y" / 跨章节连续
G. 公式编号    (X.Y) 右对齐 + 跨章节
H. 参考文献    GB/T 7714-2015 / ACM / IEEE
```

## 学校规范支持

```text
内置：
  - schools/buaa_undergrad.yml
  - schools/buaa_master.yml
  - schools/tsinghua_undergrad.yml
  - schools/tsinghua_master.yml
  - schools/pku_undergrad.yml
  - ...

未内置 → 自动从 <project>/格式要求/ 提取（PDF/Word/YAML）。
仍找不到 → 用通用规范 GB/T 7713-2006 + 警告用户。
```

欢迎 PR 新增学校规范集到 `schools/`。

## 用法

```text
# thesis-helper 自动调用（Phase 7）
/thesis-helper D:\my-thesis-project

# 独立调用
/format-compliance-checker path/to/paper/main.tex

# 指定学校
/format-compliance-checker paper/main.tex --school buaa --level undergrad
```

## 输出

```text
.format-check/                          中间产物
├── detected.yml                        论文实际格式（自动提取）
├── required.yml                        学校规范（加载/解析）
├── auto_fix.diff                       可自动修复项 patch
└── manual_check.md                     必须人工的待修清单

paper/format_check_report.md            主报告
```

## 报告示例

```markdown
# 总评：18/23 合规 + 3 项可自动修复 + 2 项人工

## A. 字号字体 ✅ 8/8
## B. 段落格式 ⚠️ 2/3 — 首行缩进 0 → 应 2 字符
## C. 页面布局 ✅ 4/4
## H. 参考文献 ❌ → 必须人工（gbt7714.bst 缺失）

## 自动修复
patch 已生成：.format-check/auto_fix.diff
应用后预计修复 3 项

## 人工待修
1. 把 gbt7714-numerical.bst 放到 paper/
2. 图 3-1 分辨率 < 300 dpi（学校要求 ≥ 300）
```

## 自动修复能力

| 类别 | 可自动修复 | 必须人工 |
|------|:---------:|:-------:|
| 字号字体 | ✅ | — |
| 段落 | ✅ | — |
| 页边距 | ✅ | — |
| 页眉页脚 | ✅ | — |
| 章节编号格式 | ✅ | — |
| 图表编号格式 | ✅ | — |
| bibstyle | ✅ | .bst 文件需人工放置 |
| 章节字数下限 | ❌ | ✅ |
| 图表清晰度 | ❌ | ✅ |
| 致谢节内容 | ❌ | ✅ |

## 与 latex-to-word 的关系

```text
latex-to-word 转换时已应用部分字体规范（学校 docx 模板）。
本 skill 在 LaTeX 阶段就检查所有项，避免依赖 Word 模板补救。
```

## 系统依赖

```text
- python >= 3.9
- PyYAML
- LaTeX 全套（重编验证）

可选：
  - python-docx（解析 Word 模板）
  - pdfplumber（解析 PDF 模板）
```

## 相关

- [SKILL.md](SKILL.md) — 完整 pipeline + 学校规范 yaml 示例
- [`../latex-to-word/SKILL.md`](../latex-to-word/SKILL.md) — Word 转换前先跑本 skill
- [`../../pipelines/undergrad-thesis-pipeline.md`](../../pipelines/undergrad-thesis-pipeline.md) Phase 7
