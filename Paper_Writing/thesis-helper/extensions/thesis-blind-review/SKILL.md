---
name: thesis-blind-review
description: "硕博毕设盲审版生成。系统化去除作者/导师/课题组/项目编号信息，保留学术内容，可选 paper-illustration 替换 self-cite。Triggers on: '/thesis-blind-review', '/盲审版', '/做盲审', '/去作者信息', 'blind review', 'anonymize thesis'."
argument-hint: [paper-tex-or-dir]
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Thesis Blind Review · 硕博毕设盲审版生成

> 仅在 `thesis_type == "master-thesis"` 或 `"phd-thesis"` 时由 thesis-helper 触发。
> 可独立调用，针对单个 .tex / 整个 paper/ 目录。

## 必须去除的 9 类信息

```text
1. 封面信息          标题 / 作者 / 学号 / 导师 / 学院 / 学校 / 专业 / 答辩日期
2. 致谢节            整章删除或替换为占位（"略 (盲审版)"）
3. 自引文献          作者本人的已发表论文（按作者名匹配 references.bib）
4. 项目编号          国家自然科学基金号 / 863 / 973 / 重点研发计划 / 实验室项目号
5. 实验室/课题组     PI 姓名 / 课题组英文缩写 / Lab 名 / 实验室门牌号
6. 个人化语句        "本人"/"我"/"作者"在第一人称叙事中的位置 → "本研究"/"本工作"
7. 数据/平台标识     学校超算账号 / 学校 GPU 集群 / 内部数据集名（含校名）
8. 图表水印          图片中含校徽 / 课题组 logo / 实验环境照片含人脸
9. 文件元数据        PDF metadata 中的作者 / 创建者字段
```

## Pipeline

### Phase 0 · 加载配置

```yaml
input:
  paper_dir: <project>/paper/
  identity:
    author_name: "带刀阿越"               # 必填，从 thesis.config.yml 提取
    author_id: "ZY2306xxxxx"             # 学号
    advisor_name: "陈某某"                # 导师
    school: "北航"
    college: "电子信息工程学院"
    major: "信息与通信工程"
    lab_keywords: ["XX 实验室", "XXLab"]  # 课题组关键词
    project_codes:                       # 基金/项目号
      - "61xxxxxxx"
      - "2023YFxxxxxxx"
  output_dir: <project>/paper_blind/
```

身份信息可由 thesis-helper 从 `thesis.config.yml` 自动注入，也可独立提供。

### Phase 1 · 复制 paper/ → paper_blind/

```bash
cp -r <project>/paper/ <project>/paper_blind/
# 不破坏原稿，只在副本上操作
```

### Phase 2 · 封面信息匿名化

读 `paper_blind/main.tex`：
- 找 `\title{}`, `\author{}`, `\school{}`, `\advisor{}`, `\studentid{}` 等命令
- 全部替换为：
  ```latex
  \title{[Title]}
  \author{[Author]}
  \school{[School]}
  ...
  ```
- 学校 LaTeX 模板封面页（如 `bachelor_info.tex`）整页替换为统一占位

### Phase 3 · 致谢节处理

```text
找：\chapter*{致谢} ... 到下一个 \chapter 之前的内容
替换为：
  \chapter*{致谢}
  \noindent 致谢内容已在盲审版中略去。
```

兼容路径：`致谢` / `Acknowledgement` / `Acknowledgements`。

### Phase 4 · 自引文献检测

读 `paper_blind/references.bib`：
```text
1. 解析每个 entry 的 author 字段
2. 用 author_name 做模糊匹配（中文/英文/姓名顺序变体）
3. 命中的 entry → 删除该 entry
4. 在 .tex 中找该 entry 的 \cite{key} → 替换为 \cite{anonymized_self}
5. 在 references.bib 末尾加：
   @misc{anonymized_self,
     note = {Self-citation removed for blind review.}
   }
```

### Phase 5 · 项目编号检测

在所有 `.tex` 中正则搜索：
```text
模式 1：基金号格式
  - 国家自然科学基金 \d{8}
  - National Natural Science Foundation .* No\.?\s*\d{8}
  - 863/973/重点研发：YYYY[A-Z]{2,3}\d{7,9}

模式 2：用户配置的 project_codes 字面匹配

命中后：
  - 整段含基金号的鸣谢/资助说明 → 替换为：
    "[Funding information removed for blind review.]"
```

### Phase 6 · 实验室/课题组关键词

按 `identity.lab_keywords` 做字面替换：
```text
"XX 实验室" → "[Lab]"
"XXLab" → "[Lab]"
PI 姓名 → "[Advisor]"
```

特别注意：脚注 `\footnote{}` 内的实验室信息也要删。

### Phase 7 · 个人化语句调整

不强制改写所有"本人/我"，因为合规盲审允许"本工作"。但：
```text
- "本人在 X 实验室" → "在某实验室"
- "我作为唯一作者" → "本研究" / "本工作"
- "我在 X 老师指导下" → "在指导下"
```

输出修改差异 → `blind_review_diff.md`（用户审核）。

### Phase 8 · 图表元数据扫描

```bash
# 扫描所有图片元数据
exiftool figures/*.{png,jpg,pdf} | grep -i "author\|creator\|comment"
```

发现作者元数据 → 用 `exiftool -All=` 清除。

⚠️ 图表内容（校徽/logo/课题组合影）需要**人工检查** + 替换或马赛克。
本 skill 输出 `blind_review_manual_check.md` 列出可疑图表。

### Phase 9 · PDF 元数据清理

编译完成后：
```bash
pdftk paper_blind/main.pdf dump_data | grep -i "author\|creator\|producer"
# 用 pdftk update_info 或 exiftool 清除
exiftool -Author= -Creator= -Producer= paper_blind/main.pdf
```

### Phase 10 · 闭环验证

```yaml
✅ 验证清单
- [ ] 封面无作者/学号/导师/学校
- [ ] 致谢节已替换
- [ ] 自引文献全部移除（grep 作者名 = 0）
- [ ] 项目编号正则扫描 = 0 命中
- [ ] 实验室关键词字面扫描 = 0 命中
- [ ] PDF 元数据无作者/创建者
- [ ] 图表元数据无作者标签
- [ ] manual_check.md 列出待人工核查项
```

任意一项未通过 → 不算完成。

## 输出

```text
<project>/paper_blind/
├── main.tex                          # 匿名化版本
├── main.pdf                          # 匿名化 PDF（已清元数据）
├── sections/*.tex                    # 各章节匿名化
├── references.bib                    # 已剔除自引
├── figures/*                         # 已清元数据（内容需人工核）
└── blind_review_report.md            # 修改清单 + 验证结果

<project>/paper_blind/blind_review_manual_check.md   # ⚠️ 人工核查清单
<project>/paper_blind/blind_review_diff.md           # 修改差异
```

## Constants

```yaml
PROJECT_CODE_PATTERNS:
  - "(国家自然科学基金|National Natural Science Foundation)[^\\n]{0,40}\\d{8}"
  - "(863|973|重点研发计划)[^\\n]{0,30}\\d{7,9}"
  - "(YFB|YFA)\\d{7,9}"
SELF_CITE_FUZZY_MATCH: true            # 中文姓名顺序变体
PRESERVE_ORIGINAL: true                # 不修改原 paper/
EXIFTOOL_REQUIRED: true                # Phase 8/9 必需
```

## 系统依赖

```text
- pdftk 或 exiftool（PDF/图片元数据清理）
- LaTeX 全套（重新编译盲审版）
```

## Owner 闭环承诺

- ❌ 自引未全部移除 → 盲审撤稿，写复盘
- ❌ 项目编号漏一个 → 盲审撤稿
- ❌ PDF 元数据没清 → 评委 Acrobat 一点就看到作者
- ❌ 图表里校徽没动 → 必须人工核查清单交付

> 因为信任所以简单——盲审是答辩前最后一道关，漏一个就重投，不能含糊。
