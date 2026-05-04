<div align="center">

# 📊 周报生成器 · Weekly Report Writer

**博士生专用 Claude Code skill** · 扫工程 → 对比上周 → 自动写周报

🇨🇳 **简体中文** · 🇺🇸 [English](README.md)

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Version](https://img.shields.io/badge/version-v1.0-green.svg) ![Tests](https://img.shields.io/badge/tests-132%20passed-brightgreen.svg) ![Output](https://img.shields.io/badge/output-Markdown%20%2B%20PDF-orange.svg)

</div>

---

> 一个 Claude Code skill，专为博士生设计：扫描你的工程目录、对比上周快照、问你简短的 L3 问卷，自动写出可直接交导师的 PhD 风格周报（Markdown + PDF）。

## 为什么要用

PhD 一周里产生的代码、实验结果、论文草稿、理论推导、配图量大到周五完全记不清。盯着 50 个文件改动问自己「这周到底干了啥」是常态。

这个 skill 替你回答。它扫工程目录、对比上周快照、识别推进的版本链（如 v25→v26）、跨 seed 聚合指标（mean ± std）、抽 paper 里的新公式块，只问你它推不出来的语义部分。然后写出结构化的导师周报。

## 输出物

- `<工程>/.weekly_report/<年>/<月>/<周>/report.md` —— 周报 Markdown
- `<工程>/.weekly_report/<年>/<月>/<周>/report.pdf` —— PDF（如装了 pandoc + xelatex）
- `<工程>/.weekly_report/<年>/<月>/<周>_tex/` —— LaTeX 源 + 中间文件
- `D:\code\reports\<年>\<月>\<日期范围>_W<周号>_<short>.md` —— 副本汇总
- `D:\code\reports\index.md` —— 跨工程索引（按年/周倒序）

报告版式贴合 PhD 风格：问候语 → 开场段 → 主要工作分节（实验背景 / 方法 / 实验结果 mean ± std + 95% CI / 关键发现 / 理论公式块 / 配图）→ 本周总结 → 下周计划 → 给老师的 ask → 结束祝福 → 学生签名 → 日期。

## 快速上手（首次使用，10 分钟）

```bash
# 1. 初始化你的工程
/weekly-report init D:\code\my_phd_project

# Skill 会：
#   - 扫描子目录探测 bucket roots（code / 实验数据 / 论文 / ...）
#   - 给你一个 project.toml 草稿让你确认
#   - 遍历所有 output JSONs 收集指标 key
#   - 打开 metric_vocab_init.md 让你给 ~30 个 unknown key 打勾分类（一个 30 秒）

# 2. 生成 baseline 总报告
/weekly-report run

# Skill 会：
#   - 打开 interview.md 问你 ~5 个高层方向问题
#   - 生成 10 节式 baseline 总报告（含 3 个月路线图）
```

## 每周使用（init 后，5 分钟）

```bash
/weekly-report run

# 1. Skill 问：「时间窗口几天？默认 7」
# 2. 扫工程（71315 数据文件实测 < 30s）
# 3. 对比上周
# 4. 打开 interview.md，5-9 个 section（仅有内容的）
# 5. 你填 **请填**: 后的空（共 5-10 分钟）
# 6. Skill 出 report.md / report.pdf
```

## 扫什么

| Bucket | 默认 root | 扫什么 |
| --- | --- | --- |
| code | Forecasting/, hardware/, src/ | .py / .cpp / .h，识别版本链 |
| experiment_data | */output, */results | .json 指标，多 seed 聚合 |
| paper | paper_writing/ | .tex / .md / .docx，章节级 diff |
| reading | research-wiki/, docs/ | .md / .pdf，新增论文 |
| theory | theory/, derivations/ | math 块（`$$...$$` / `\(\)` / equation env） |
| figures | */ppt_figures, */figs | .png / .svg / .pdf，嵌入周报 |
| checkpoint_signal | */checkpoint, */weights_* | 仅文件名 regex（acc / epoch / seed） |

## 不会做什么

🚫 **永远不会修改你的工程代码**。仅写到 `.weekly_report/` 和 `D:\code\reports\`。

- 不解析 `git log`（不需要 git 仓库）
- 不读训练 checkpoint 内容（仅文件名）
- 不访问外部系统（Slack / 邮件 / Issue）
- 不做 AST 级代码 diff

## 配置

init 后编辑 `<工程>/.weekly_report/project.toml`。完整字段说明在 `references/project-toml-reference.md`。最常调的几个：

- `[buckets.code] roots = [...]` —— 加自定义代码目录
- `[project] advisor = "陈老师"` —— 用于问候
- `[project] student = "李越"` —— 用于结尾签名
- `[project] domain = "..."` —— §1 项目背景的领域描述
- `[buckets.figures] max_per_report = 5` —— 配图数上限

## 维护 metric_vocab.json

skill 第一次见到没见过的 numeric JSON key，会问你分类（指标 / 配置 / 忽略）。每条 30 秒，永久保存。也可以直接编辑 `metric_vocab.json`。

详见 `references/metric-vocab-guide.md`。

## 多工程支持

每个工程有自己的 `.weekly_report/`。互不干扰。每个工程跑一次 init。所有工程的副本汇总到 `D:\code\reports\` 按年/月归档。

## 分享给师弟师妹

```bash
# 整目录复制到他们的 plugins
cp -r D:\code\github_skill\weekly_report ~/.claude/plugins/

# 让他们打开本 README，对自己的工程跑 init。
# 他们的 metric_vocab.json 会基于他们工程重新生成，不会和你串。
```

skill 是 project-agnostic 的——师弟师妹的 project.toml 跟你的会完全不同。Bucket roots、导师名、指标——全部隔离。

## PDF 渲染依赖

- pandoc（任意 2.x / 3.x 版本）
- xelatex（MiKTeX / TeX Live 任一）
- 模板：`assets/baseline-tex-template.tex`（基于 `ctexart`，无封面，xeCJK + 宋体正文 / 黑体标题）

工具缺失时 PDF 步骤自动跳过，不影响 markdown 周报正常生成。

## 故障排除

| 现象 | 原因 | 修法 |
| --- | --- | --- |
| 扫描特别慢 | `roots` 包含太多 ckpt 文件 | 把 ckpt 目录只放在 `checkpoint_signal.roots` 下 |
| 报告漏了我的改动 | bucket root 没配 | 加到 `project.toml [buckets.code] roots` |
| 指标对比表不准 | metric_vocab 错分类 | 编辑 `metric_vocab.json` |
| 路径白名单错误 | skill bug | 提交 issue 附上栈 |
| 版本链拆得太细 | 启发式过窄 | 在 `family_aliases.json` 加别名 |

更多见 `references/faq.md`。

## 架构

```
SKILL.md（编排，LLM 驱动）
   ↓
scripts/（确定性 Python）
   ├── scan_project.py        # ThreadPool 扫描器
   ├── compute_diff.py        # 跨周 diff
   ├── extract_metrics.py     # JSON 指标抽取
   ├── parse_filename.py      # 版本链启发式
   ├── theory_extractor.py    # math 块扫描
   ├── figure_picker.py       # 配图候选
   ├── interview_generator.py # 生成问卷
   ├── parse_interview.py     # 解析填好的问卷
   ├── init_project.py        # 自动检测 + project.toml 脚手架
   ├── metric_vocab_init.py   # 生成/解析首次 metric 标注表
   ├── run_baseline.py        # baseline 总报告 runner
   ├── render_pdf.py          # md → pandoc → xelatex → PDF
   ├── update_index.py        # 跨工程 index.md
   ├── metric_vocab.py        # vocab 读写
   ├── path_guard.py          # 写白名单守卫（红线）
   ├── ignore_rules.py        # glob 忽略匹配
   ├── file_metadata.py       # 单文件 inspect
   └── bucket_classifier.py   # 路径 → bucket
   ↓
references/（LLM 上下文文档）
assets/（模板）
```

## 许可与归属

实验室内部工具。在你课题组的 git 仓库里维护、一起迭代。公开发布时请保留作者信息。

英文版：[README.md](README.md)
