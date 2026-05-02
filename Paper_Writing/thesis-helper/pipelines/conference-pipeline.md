# Conference Pipeline · 会议论文端到端流程

> 触发条件：`thesis.config.yml` 中 `thesis_type: conference`
> 默认目标：NeurIPS / ICLR / ICML / CVPR / ACL / AAAI 等顶会
> 默认交付：8 件套（PDF + 源 + figures + slides + poster + cover/notes）
> 跳过：AIGC 降痕

## Pipeline 总览

```text
┌─────────────────────────────────────────────────────────────────────┐
│ Phase 0  · 项目扫描 + config 读取                                     │
│ Phase 1  · 文献综述 + novelty check                                   │
│ Phase 2  · 论文写作 (paper-writing 全流程，会议模板)                  │
│ Phase 3  · 出版级图表 + AI 配图                                       │
│ Phase 4  · 自审 (paper_reviewer)                                     │
│ Phase 5  · 答辩/汇报 PPT (paper-slides)                              │
│ Phase 6  · 学术海报 (paper-poster)                                   │
│ Phase 7  · 闭环验证 + 投稿/汇报包                                     │
│ Phase 8  · (投稿后) Author Response 处理                             │
└─────────────────────────────────────────────────────────────────────┘
```

## 与 journal pipeline 的差异

```text
journal-pipeline                conference-pipeline
──────────────────             ───────────────────
没有 slides / poster           ✅ 必有 slides + poster
专注 cover letter              专注 reviewer response (rebuttal 期更短)
长文（10-25 页）               短文（NeurIPS 9 页 + appendix）
偏向理论严谨                   偏向 idea novelty + 实验充分
audience: 同行专家             audience: 评委 + 海报巡视者
```

## Phase 0 · 项目扫描

读 `thesis.config.yml`，确认：

```yaml
thesis_type: conference
venue: NeurIPS                   # ICLR / ICML / CVPR / ACL / AAAI / ...
language: en
detector: none
school_rules:
  neurips_conference:
    page_count_max: 9            # NeurIPS 主体 9 页
    references_count_in_pages: false
    auto_generate_slides: true
    auto_generate_poster: true
```

## Phase 1 · 文献综述 + novelty check

强制 `/novelty-check`——会议比期刊更看 idea 新颖性，desk reject 多源于此。

```text
1. /research-lit + /semantic-scholar 找近 2 年同方向工作
2. /novelty-check 验证 contribution 是否真新
3. 若新颖性 < 阈值 → 提示用户考虑 pivot 或加 ablation
```

## Phase 2 · 论文写作

```yaml
venue: <config.venue>
template: <auto-detect>          # NeurIPS 用 neurips2025.tex 等
page_limit: <school_rules.page_count_max>
references_count_in_pages: false
auto_proceed: true
improvement_rounds: 2
```

输出：`paper/main.tex` + `main.pdf`

## Phase 3 · 出版级图表 + AI 配图

```text
/scientific-visualization → 数据图升级 vector PDF + colorblind
/paper-illustration       → method 章节的架构图（AI 生成）
/mermaid-diagram          → 流程图（pipeline / system overview）
```

## Phase 4 · 自审

调用 `/paper_reviewer`，会议特化维度：

```text
- Soundness         严谨性
- Significance      意义（会议看 impact）
- Novelty           新颖性（会议第一指标）
- Clarity           清晰度
- Reproducibility   可复现性（NeurIPS 必查）
```

## Phase 5 · 答辩/汇报 PPT

调用 `/paper-slides paper/`，会议汇报用：

```yaml
mode: conference                 # 区别于 thesis-defense / lab_meeting
duration_min: 12                 # 多数顶会 oral 12 分钟 + 3 分钟 Q&A
audience: peer_researchers
emphasis:
  - novelty_first              # 第一页就讲 contribution
  - one_diagram_per_idea
  - reproducibility_callout    # 提 GitHub link
```

输出：`<project>/slides/slides.pdf` + `.pptx`

## Phase 6 · 学术海报

调用 `/paper-poster paper/`：

```yaml
size: A0                         # 多数会议默认 A0
orientation: portrait            # 竖版（NeurIPS）；横版传 landscape
template: tcbposter
sections:
  - intro_with_one_image
  - contribution_bullets
  - method_diagram
  - main_results_table
  - qualitative_examples
  - conclusion + qr_code_to_paper
```

输出：`<project>/poster/poster.pdf`

## Phase 7 · 闭环验证

```yaml
✅ 交付清单
├── paper/main.pdf
├── paper/main.tex + sections/
├── paper/references.bib
├── figures/journal/*
├── slides/slides.pdf + slides.pptx
├── poster/poster.pdf
├── paper/review_self.md
└── submission/openreview_metadata.json (NeurIPS/ICLR)

📊 验证数据
├── 页数：[N] / 限制 [M]
├── 自审分数：[X/10]               ← 推荐 ≥ 7.5
├── novelty 分：[X/10]
└── 海报阅读时间预估：≤ 5 分钟      ← 海报视觉密度合规
```

## Phase 8 · Author Response

NeurIPS / ICLR 等会议有 1 周 author response 期：

```text
/rebuttal --mode conference --char-limit 5000
   ↓
按审稿人 + 元审稿人分组回复
   ↓
revised paper diff
```

详见 [`../integrations/rebuttal-wrapper.md`](../integrations/rebuttal-wrapper.md)。

## Owner 闭环承诺

- ❌ NeurIPS 主体超 9 页 → desk reject，必须压
- ❌ Reproducibility 章节缺失 → NeurIPS 直接低分
- ❌ Slides + Poster 缺一 → 不算完成（会议接收必须做这两个）
- ❌ Author response 阶段超字符限制 → reviewer 不会读

> 因为信任所以简单——会议接收只是开始，slides + poster + author response 才是会议舞台。
