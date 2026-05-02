# Undergrad Thesis Pipeline · 本科毕设端到端流程

> 触发条件：`thesis.config.yml` 中 `thesis_type: undergrad-thesis`
> 默认阈值（北航）：AIGC ≤ 8% / 查重 ≤ 8%
> 默认交付：6 件套（PDF + Word + AIGC 报告 + CNKI 记录 + 答辩 PPT + 格式检查报告）

## Pipeline 总览

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 0  · 项目扫描 + config 读取                                     │
│ Phase 1  · 文献综述（前置）                                            │
│ Phase 2  · 论文写作 (paper-writing 全流程)                            │
│ Phase 3  · 自审（paper_reviewer）                                     │
│ Phase 4  · AIGC 降痕 + CNKI 验证 (aigc-reduce)                       │
│ Phase 5  · LaTeX → Word 转换 (latex-to-word)                        │
│ Phase 6  · 中英文摘要平行检查 (bilingual-abstract)                    │
│ Phase 7  · 格式合规检查 (format-compliance-checker)                  │
│ Phase 8  · 答辩准备 (thesis-defense-prep)                            │
│ Phase 9  · 闭环验证 + 交付报告                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0 · 项目扫描 + config 读取

执行：
```bash
python scanners/project-scanner.py <project_root>
```
读取：`thesis.config.yml`
输出：`<project>/.thesis-helper/project_map.json` + `route_decision.yml`

---

## Phase 1 · 文献综述（前置，可选）

触发：`pipeline.lit_review: true`

```text
language=zh + 工科领域 → /comm-lit-review (通信/雷达/无线)
language=zh + 其他      → /research-lit
language=en              → /research-lit
```

输出：`<project>/.thesis-helper/lit_review.md` → 注入到 paper-writing Phase 1。

---

## Phase 2 · 论文写作（paper-writing 全流程）

调用：`/paper-writing <NARRATIVE_REPORT.md>` （上游 9 步）

注入参数：
```yaml
venue: <config.venue>                    # 北航 / 清华 / ...
language: <config.language>              # zh
template: <project_map.format_rules>     # 学校 LaTeX 模板
data_sources: <project_map.data_files>   # 自动找数据
figure_sources: <project_map.figure_sources>
references: <project_map.references>
```

输出：
```text
<project>/paper/main.tex
<project>/paper/sections/*.tex
<project>/paper/main.pdf      (paper-compile 编译)
<project>/paper/references.bib
```

---

## Phase 3 · 自审（paper_reviewer）

调用：`/paper_reviewer <project>/paper/main.pdf`

输出：`<project>/paper/review_self.md`（结构化审稿意见）

如有 CRITICAL → 暂停 pipeline，提示用户修改后再继续。

---

## Phase 4 · AIGC 降痕 + CNKI 验证

调用：`/aigc降低 <project>/paper/main.tex`

加载：[`../detectors/cnki/adapter.md`](../detectors/cnki/adapter.md)

阈值：AIGC ≤ 8% / 查重 ≤ 8%（北航）→ 学校规则可覆盖

输出：
```text
<project>/paper/main_aigc-reduced.tex
<project>/paper/aigc-reduce-report.md
<project>/paper/aigc-scan-results/results_*.json
```

⚠️ 强制 CNKI 验证循环：
- 提示用户导出 Word 上传 CNKI（aigc-reduce 内置）
- 用户填回 `<project>/paper/cnki-aigc-round1.md`
- 若 CNKI 仍超标 → 自动 round2

---

## Phase 5 · LaTeX → Word 转换

调用：[`/latex-to-word`](../extensions/latex-to-word/SKILL.md)

输入：`<project>/paper/main_aigc-reduced.tex`
输出：`<project>/paper/main.docx`（保留公式编号 / 图表 / 引用 / 字体）

为什么自研：pandoc 直接转换会丢失公式编号、图表交叉引用、双列布局。
本 skill 用 LaTeX → tex4ht → docx + 后处理修复。

---

## Phase 6 · 中英文摘要平行检查

调用：[`/bilingual-abstract`](../extensions/bilingual-abstract/SKILL.md)

检查：
- 中英文摘要字数比例（中文 ≈ 300-500 字 / 英文 ≈ 200-300 词）
- 关键词数量一致（通常 3-5 个）
- 关键词翻译对齐
- 段落结构对齐

输出：`<project>/paper/abstract_check_report.md`

---

## Phase 7 · 格式合规检查

调用：[`/format-compliance-checker`](../extensions/format-compliance-checker/SKILL.md)

按学校规范检查：
- 字号（标题 / 正文 / 图表）
- 行距
- 页边距
- 页眉页脚
- 章节编号格式
- 公式编号格式
- 参考文献格式（GB/T 7714 等）

学校规范从 `<project>/格式要求/` 提取，或使用 `school_rules` 内置。

输出：`<project>/paper/format_check_report.md`

---

## Phase 8 · 答辩准备

调用：[`/thesis-defense-prep`](../extensions/thesis-defense-prep/SKILL.md)

生成：
- `<project>/defense/slides.pdf`（Beamer，10-15 分钟答辩）
- `<project>/defense/slides.pptx`（备选 PPT 格式）
- `<project>/defense/qa_simulation.md`（可能问题 + 建议回答，调用 `paper_reviewer` 模拟）
- `<project>/defense/speaker_notes.md`（演讲稿）

---

## Phase 9 · 闭环验证 + 交付报告

```yaml
✅ 交付清单
├── <project>/paper/main.pdf                      # 论文 PDF
├── <project>/paper/main.docx                     # 论文 Word（学校要求）
├── <project>/paper/main_aigc-reduced.tex         # AIGC 降痕版 LaTeX
├── <project>/paper/aigc-reduce-report.md         # 降痕详细报告
├── <project>/paper/cnki-aigc-round*.md           # CNKI 验证记录
├── <project>/paper/abstract_check_report.md      # 中英摘要检查
├── <project>/paper/format_check_report.md        # 格式合规检查
├── <project>/defense/slides.pdf                  # 答辩 PPT
├── <project>/defense/qa_simulation.md            # 答辩问答模拟
└── <project>/.thesis-helper/                     # 内部状态
    ├── project_map.json
    ├── route_decision.yml
    └── lit_review.md (如有)

📊 验证数据（必须输出）
├── 论文页数：[N]
├── 字数：[N] / 要求 [N-N]
├── AIGC 率：本地 [X]% / CNKI [Y]% / 阈值 8%
├── 查重率：本地估算 [X]% / 阈值 8%
├── 格式合规：[N]/[N] 项通过
└── 答辩材料：✓ 已生成

⚠️ 待办（如有）
├── 手动检查：[N] 项 CRITICAL 审稿意见未修
├── 手动操作：上传 CNKI 验证（aigc-reduce 已提示）
└── 学校特殊要求（任务书 / 中期检查）：暂未生成（后续 extensions）
```

## Owner 闭环承诺

- ❌ Phase 4 未跑 CNKI 验证 → 不算完成
- ❌ Phase 5 未生成 Word → 不算完成（学校强制）
- ❌ Phase 9 验证数据缺失 → 不算完成
- ✅ 全部 9 phase 走完 + 6 件套交付 + 验证报告 = 端到端闭环

> 因为信任所以简单——把毕设这件事，做成 owner 闭环，不让学生半夜 emo。
