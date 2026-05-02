---
name: format-compliance-checker
description: "学校格式规范自动检查器。字号/行距/页边距/页眉页脚/章节编号/公式编号/参考文献格式（GB/T 7714）一站式合规检查。Triggers on: '/format-compliance-checker', '/格式检查', '/合规检查', '/检查格式', 'format check', 'compliance check'."
argument-hint: [paper-tex-or-pdf]
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Format Compliance Checker · 学校格式规范检查

> 国内毕设的痛点：学校规范几十页 PDF，每个细节都可能扣分。
> 本 skill **按学校规范集自动比对** + **逐项报告** + **可修复项一键 patch**。

## 8 类检查项

```text
A. 字号字体        标题/正文/脚注/图注/表注/代码/公式
B. 段落格式        行距 / 段距 / 首行缩进 / 对齐方式
C. 页面布局        页边距 / 装订线 / 页眉页脚位置
D. 页眉页脚        奇偶页 / 章节标记 / 页码格式
E. 章节编号        Chapter X / X.Y / X.Y.Z 多级格式
F. 图表编号        "图 X-Y" / "Table X-Y" / 跨章节连续
G. 公式编号        (X.Y) 右对齐 + 跨章节
H. 参考文献         GB/T 7714-2015 / ACM / IEEE 等格式
```

## 学校规范集（内置 + 可扩展）

```text
schools/
├── buaa_undergrad.yml    北航本科毕设（详见示例）
├── buaa_master.yml       北航硕士毕设
├── tsinghua_undergrad.yml 清华本科
├── tsinghua_master.yml   清华硕士
├── pku_undergrad.yml     北大本科
└── ...                   其他学校
```

未内置的学校 → 从 `<project>/格式要求/` 自动解析（PDF/Word 模板）。

### 内置规范集示例（buaa_undergrad.yml）

```yaml
school: buaa
level: undergrad
font:
  title_chapter: { name: 黑体, size: 三号, bold: true, align: center }
  title_section: { name: 黑体, size: 小三, bold: true }
  title_subsection: { name: 黑体, size: 四号, bold: true }
  body: { name: 宋体, size: 小四, bold: false }
  body_en: { name: "Times New Roman", size: 12pt }
  caption: { name: 仿宋, size: 五号, align: center }
  code: { name: Consolas, size: 五号 }
  footnote: { name: 宋体, size: 小五 }
paragraph:
  line_spacing: 1.5
  paragraph_spacing: 0
  first_line_indent: 2  # 中文 2 字符
  alignment: justify
page:
  paper: A4
  margin_top_cm: 2.5
  margin_bottom_cm: 2.5
  margin_left_cm: 3.0   # 装订侧
  margin_right_cm: 2.5
header_footer:
  header_text: "北京航空航天大学本科生毕业设计（论文）"
  footer_format: page_number_only
  alternating_pages: true   # 奇偶页不同
  page_number_align: center
chapter_numbering:
  format: "第 X 章"
  cross_chapter_continuous_figures: false  # 图表按章节重新编号 "图 1-1"
  cross_chapter_continuous_equations: false
references:
  style: gb-t-7714-2015-numeric
  count_in_pages: false
  in_text_format: "[N]"      # 上标或方括号数字
```

## Pipeline

### Phase 1 · 检测论文格式

输入：`<project>/paper/main.tex` + 所有 `sections/*.tex`

提取：

```text
- 文档类：\documentclass{} 参数
- 字体设置：\usepackage{ctex} / \setCJKmainfont{} / \setmainfont{}
- 字号：\zihao{} \fontsize{} \large \small 等
- 行距：\linespread{} \setstretch{}
- 页边距：\geometry{} \usepackage[margin=]{geometry}
- 页眉页脚：\fancyhead{} \fancyfoot{}
- 章节计数器：\renewcommand{\thefigure}{...} 等
- bibstyle：\bibliographystyle{}
```

输出：`.format-check/detected.yml`（论文实际格式）

### Phase 2 · 加载学校规范

```text
1. 读 thesis.config.yml 的 venue + thesis_type
2. 找内置规范集：
   - buaa + undergrad-thesis → schools/buaa_undergrad.yml
3. 找不到 → 解析 <project>/格式要求/
   - 优先 .yml > .docx > .pdf
4. 仍找不到 → 用通用规范（GB/T 7713-2006）+ 警告用户
```

### Phase 3 · 逐项比对

```python
detected = load_yaml(".format-check/detected.yml")
required = load_yaml("schools/buaa_undergrad.yml")

issues = []
for category, rules in required.items():
    for key, expected in rules.items():
        actual = detected.get(category, {}).get(key)
        if actual != expected:
            issues.append({
                "category": category,
                "key": key,
                "expected": expected,
                "actual": actual,
                "auto_fixable": is_auto_fixable(category, key),
            })
```

### Phase 4 · 自动可修复项 → 生成 patch

```text
✅ 可自动修复：
   - 字号 / 字体 / 行距 / 页边距（修改 LaTeX preamble）
   - 章节编号格式（修改 \renewcommand{\thechapter}{}）
   - 图表编号格式
   - bibstyle

❌ 不可自动修复（必须人工）：
   - 章节正文内容长度（如要求"绪论 ≥ 5000 字"）
   - 图表内容（清晰度/标注语言）
   - 致谢节内容
```

可修复项 → 生成 `.format-check/auto_fix.diff`

### Phase 5 · 验证修复

应用 patch → 重新 `latexmk` → 重新检测：

```text
若仍有不合规项 → 进入 round 2
最多 3 round 自动修复
3 round 后仍不合规 → 列入"必须人工"清单
```

### Phase 6 · 输出报告

```markdown
# Format Compliance Check Report

## 总评：18 项合规 / 3 项需修 / 2 项需人工

学校规范：北京航空航天大学本科生毕业设计（论文）
检查时间：2026-05-02 14:23

---

## A. 字号字体 ✅ 8/8

| 项 | 要求 | 实际 | 状态 |
|----|------|------|------|
| 章标题 | 黑体三号居中 | 黑体三号居中 | ✅ |
| 正文 | 宋体小四 | 宋体小四 | ✅ |
| ...

## B. 段落格式 ⚠️ 2/3

| 项 | 要求 | 实际 | 状态 |
|----|------|------|------|
| 行距 | 1.5 | 1.5 | ✅ |
| 段距 | 0 | 0 | ✅ |
| 首行缩进 | 2 字符 | 0 | ❌ → auto_fix |

## C. 页面布局 ✅ 4/4
...

## H. 参考文献 ❌ → 必须人工

实际：natbib 默认样式
要求：GB/T 7714-2015 numeric
建议：\bibliographystyle{gbt7714-numerical}
（已经在 auto_fix.diff 里，但 .bst 文件需手动放到 paper/）

---

## 自动修复
patch 已生成：.format-check/auto_fix.diff
应用后预计修复 3 项

## 人工待修
1. [.bst 文件缺失] 需要把 gbt7714-numerical.bst 放到 paper/
2. [图 3-1 清晰度] 检测到 PNG 分辨率 < 300 dpi
```

输出：`<project>/paper/format_check_report.md` + `auto_fix.diff`

### Phase 7 · 闭环验证

```yaml
✅ 验证清单
- [ ] detected.yml 成功生成
- [ ] 学校规范集成功加载
- [ ] 报告含 8 大类全部检查
- [ ] 可修复项已生成 patch
- [ ] 不可修复项列出人工待修清单
- [ ] 应用 patch 后总合规率 >= 90%
```

## Constants

```yaml
SCHOOL_RULESETS_DIR: schools/
DEFAULT_FALLBACK_RULESET: gb-t-7713-2006
MAX_AUTO_FIX_ROUNDS: 3
MIN_COMPLIANCE_RATE_PASS: 0.90
GB_T_7714_BST_URL: "https://github.com/zepinglee/gbt7714-bibtex-style"
```

## 系统依赖

```text
基础（必需）：
  - python >= 3.9
  - PyYAML
  - LaTeX 全套（用于重编验证）

可选：
  - python-docx（解析 Word 模板时）
  - pdfplumber（解析 PDF 模板时）
```

## 与上游的关系

```text
thesis-helper Phase 7 调本 skill
   ├── 读 venue/thesis_type → 加载学校规范
   ├── 读 paper/main.tex → 检测实际格式
   ├── 输出 format_check_report.md
   └── 应用 auto_fix.diff（用户确认后）
```

## Owner 闭环承诺

- ❌ 学校规范找不到时 → 必须警告用户，不静默用通用规范
- ❌ auto_fix.diff 不实际跑一遍验证 → 不算完成
- ❌ 总合规率 < 90% → 必须列出每一项待修
- ❌ 人工待修清单为空但实际不合规 → 是 bug，必修

> 因为信任所以简单——格式扣分是最冤的扣分，写论文是脑力，做格式是体力，不该让学生熬夜。
