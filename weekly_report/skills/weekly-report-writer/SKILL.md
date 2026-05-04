---
name: weekly-report-writer
description: PhD 学生周报全自动生成 skill。扫描工程目录、对比上周快照、半自动归并版本链与指标、L3 质询补语义、输出含问候语和结束祝福的 PhD 风格周报 markdown。当用户说"写周报"、"导师汇报"、"weekly report"、"本周做了什么"、"梳理工程进展"、"baseline 总报告"或类似表达时，必须使用此 skill。覆盖代码 / 实验数据 / 论文 / 阅读 / 理论公式 / 配图六类。支持多项目隔离、跨年月归档、师弟师妹零门槛复用。
---

# Weekly Report Writer

## 何时使用

- 用户要写每周给导师的周报
- 用户工程文件多到记不清，需要工具梳理
- 用户要做项目阶段性 baseline 总报告
- 用户希望把零散口语描述整理成结构化周报

## 何时不使用

- 用户要 PPT、论文初稿、grant proposal（用对应 skill）
- 用户希望从外部系统抓数据（Slack / 邮件 / Issue）—— 本 skill 仅扫工程目录
- 用户提供的信息明显不足，先质询而非硬写

## 红线（不可破）

🚫 **本 skill 严禁修改用户工程代码**。仅向 `<project>/.weekly_report/` 与 `D:\code\reports\` 写入。
所有写操作经 `scripts/path_guard.py` 守卫。一旦触发越界写，必须立即报错而不是覆盖。

## 入口指令

| 指令 | 行为 |
| --- | --- |
| `/weekly-report init <project_path>` | 首跑：自动检测 buckets → 生成 project.toml → metric_vocab 标注 → baseline 总报告 |
| `/weekly-report run [--project <path>]` | 增量：扫描 → diff → interview → 周报 |
| `/weekly-report rebase --week <id>` | 重建指定周（找回老周报） |

## 工作流程

### 1. 探测模式

- 检查 `<project>/.weekly_report/project.toml` 是否存在
- 不存在 → baseline 模式（走 init 流程）
- 存在但无 `metric_vocab.json` → 跑 metric vocab 标注
- 存在但无历史周 → 仍按 baseline 模式
- 存在且有历史周 → incremental 模式

### 1a. Init 模式额外步骤（仅首跑）

- 调用 `scripts/init_project.py.detect_buckets()` 探测 bucket roots
- 调用 `scripts/init_project.py.build_project_toml()` 写 `project.toml`
- 跑一次 scanner 收集 experiment_data JSONs 的 numeric keys
- 调用 `scripts/metric_vocab_init.build_init_md()` 写 `metric_vocab_init.md`
- 提示用户：「请打开 `<project>/.weekly_report/metric_vocab_init.md` 标注 N 个 unknown keys（5-10 分钟），保存后告诉我」
- 用户保存后，调用 `scripts/metric_vocab_init.parse_filled_md()` 解析勾选
- 调用 `scripts/metric_vocab.save_metric_vocab()` 写 `metric_vocab.json`
- 然后才进入 §2 之后的常规流程

### 2. 运行时询问（每次必问）

- 问：「本次汇报覆盖的时间窗口是？」
  - 默认：上次跑到现在 / 7 天
  - 可选：自定义 N 天（1–30）/ 指定起止日期
- 此值即 active_window_days，用于 checkpoint_signal、figures、新增文件的 mtime 过滤
- 若上次跑距今 < 3 天，提示「距上次跑较近，确认要再写一次？」

### 3. Scanner 阶段

调用 `scripts/scan_project.py`：ThreadPool 并发，max_workers = `min(8, len(roots) * 2)`。
产出 `<week>/manifest.json`。

### 4. Diff 阶段

（仅 incremental）调用 `scripts/compute_diff.py`，对比上周 manifest。
产出 `<week>/diff.json`。

### 5. 配图与理论

- 调用 `scripts/figure_picker.py` 选候选图
- 调用 `scripts/theory_extractor.py` 抽 math 块
- 结果写入 manifest 与 diff 对应字段

### 6. Interview 阶段

调用 `scripts/interview_generator.py`，产出 `<week>/interview.md`。
提示用户：「请打开 `<week>/interview.md` 填写，填完告知。」

### 7. 等用户填完后

读取填好的 interview.md，调用 `scripts/parse_interview.py` → `interview_parsed.json`。

### 8. Writer 阶段

基于 manifest + diff + interview_parsed，按 `assets/weekly-report-template.md`
（incremental）或 `assets/baseline-report-template.md`（baseline）合成 `report.md`。

格式参考样例 `D:\code\github_skill\2026春-3月第1周报-李越.docx`：

- 开头 `**学期周序周报**` + 问候语 + 开场段
- 主要工作按 H1 分节（实验背景/方法/结果/分析）
- 表格 mean ± std + 95% CI
- 理论方法单独成节，含公式块
- 配图嵌入相对路径
- 结尾"祝您工作顺利，身体健康！"+ 签名 + 日期斜杠

详见 `references/greeting-templates.md` 与 `references/writing-rules.md`。

### 9. 落档

- 周报 markdown：`<project>/.weekly_report/<year>/<month>/<week>/report.md`
- 周报 PDF（如 pandoc + xelatex 在 PATH）：`<project>/.weekly_report/<year>/<month>/<week>/report.pdf`
- LaTeX 源 + aux：`<project>/.weekly_report/<year>/<month>/<week>_tex/`（与 PDF 平级，但单独目录隔离 .aux/.log/.toc 噪声）
- Manifest/diff/interview/interview_parsed.json/images/ 同 markdown 目录
- 副本：`D:\code\reports\<year>\<month>\<date_range>_W<n>_<short_name>.md`（report.md 副本）
- 调用 `scripts/update_index.py` 更新 `D:\code\reports\index.md`
- 写 `<project>/.weekly_report/latest.txt` 指针

### 9.1 PDF 渲染（baseline 模式同样适用）

- 依赖：`pandoc` + `xelatex`（MiKTeX / TeX Live 任一）
- 模板：`assets/baseline-tex-template.tex`（ctexart，无封面，xeCJK + 宋体正文 / 黑体标题，学术风格）
- 流程：md → pandoc 出 LaTeX 片段 → 替换 `% BODY_PLACEHOLDER` → xelatex 编译
- 工具缺失时：`render_pdf.py` 返回 `status="skipped"`，markdown 仍正常落档不阻塞

### 10. 自检

LLM 读一遍 report.md，检查：

- 是否有空段
- 是否流水账（每条事项有"做了什么 / 做到什么程度 / 影响"）
- 是否漏 ask
- 是否漏配图（本周有候选图但 report 中没引用）
- 是否漏公式（theory 有新增但 report 中没体现）

## 写作原则

- 周报不是日记，要归纳
- 周报不是邀功表，要边界
- 周报不是任务列表照抄，要轻度提炼
- 一条事项尽量写清：做了什么、做到什么程度、产生了什么结果

## 默认行为

- 输入碎片化时先质询
- 同一件事重复出现时区分细节后再写
- 一项工作只有过程没结果时写"推进到 X 阶段"
- 信息不足时列出最少必要补充问题

## 关键参考文件

| 文件 | 用途 |
| --- | --- |
| `references/greeting-templates.md` | 开头问候 + 结束祝福格式 |
| `references/writing-rules.md` | 写作风格规则 |
| `references/version-chain-heuristic.md` | family_key 算法 |
| `references/metric-vocab-guide.md` | metric_vocab 维护 |
| `references/project-toml-reference.md` | project.toml 字段 |
| `references/baseline-roadmap-prompt.md` | baseline 路线图 prompt |
| `references/theory-extraction-rules.md` | 理论 / 公式抽取 |
| `references/input-guide.md` | 处理零散输入 |
| `references/faq.md` | 常见问题 |

## 输出要求

- 结构清晰，导师可快速扫读
- 优先写结果、进展和影响
- 避免口语和情绪化表达
- 未完成事项写清当前进展和下一步，不假装完成
- 风险 / 下周计划如缺信息，要审慎补齐或明确说"信息不足"

## 调试 / 故障排除

- 路径白名单越界 → `scripts/path_guard.py` 拦截，看堆栈定位写源
- 版本链拆得过细 → 在 `<project>/.weekly_report/family_aliases.json` 加别名
- 指标分类不准 → 编辑 `<project>/.weekly_report/metric_vocab.json`
- 扫描慢 → 检查 `project.toml [scanner]` 的 max_workers / metadata_only_size_mb
