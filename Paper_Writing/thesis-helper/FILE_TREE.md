# Thesis Helper · 完整文件树设计 (v0.2)

> v0.2 更新：新增 `integrations/`（17 个现成 skill 接入）+ `extensions/`（5 个新造 skill），支持 4 种论文类型。
> 已实现文件带 ✅，待造文件带 🚧。

```text
thesis-helper/
│
├── ✅ SKILL.md                          # Claude Code 顶层 orchestrator 入口
├── ✅ README.md                         # 用户指南（含跨平台安装）
├── ✅ FILE_TREE.md                      # 你正在看的文件
├── ✅ thesis.config.template.yml        # 用户项目根目录配置模板（v0.2 加 conference + integrations）
│
├── routers/                             # 【路由层 ✅ Batch 3 完成】决定走哪条 pipeline
│   ├── ✅ intent-router.md             # 论文类型路由 (4 类)
│   ├── ✅ venue-router.md              # 学校/期刊/会议规则路由
│   └── ✅ detector-router.md           # 检测器路由（CNKI/Turnitin/...）
│
├── scanners/                            # 【扫描层】智能识别项目资产
│   ├── 🚧 project-scanner.py           # 扫描数据/代码混合目录 → ProjectMap.json
│   ├── 🚧 format-rules-scanner.py      # 解析"格式要求/"文件夹
│   └── 🚧 README.md                    # 扫描规则说明
│
├── compilers/                           # 【编译层 ✅ Batch A 完成】跨平台 skill 编译器
│   ├── ✅ build.py                     # 主入口：编译 Claude SKILL.md → 各平台
│   ├── ✅ README.md                    # 编译规则
│   └── targets/
│       ├── ✅ __init__.py
│       ├── ✅ _common.py               # 共享工具（frontmatter/压缩）
│       ├── ✅ claude.py                # 整目录复制到 ~/.claude/skills/
│       ├── ✅ cursor.py                # 输出 <project>/.cursorrules
│       ├── ✅ gemini.py                # 输出 <project>/GEMINI.md
│       ├── ✅ cline.py                 # 输出 <project>/.clinerules
│       ├── ✅ chatgpt.py               # 输出 ChatGPT 自定义 GPTs（≤7500 字符）
│       └── ✅ universal.py             # 输出通用 prompt 包
│
├── detectors/                           # 【检测器适配层 ✅ Batch 3 完成】每种检测器一个 adapter
│   ├── cnki/                           # 知网（生产可用，已通过 aigc-reduce v3 实测）
│   │   └── ✅ adapter.md               # 调用 ../../../aigc-reduce-skills/aigc-reduce
│   ├── turnitin/                       # 海外期刊/毕设
│   │   └── ✅ adapter.md
│   ├── paperpass/                      # 国内备查（算法相近 CNKI）
│   │   └── ✅ adapter.md
│   └── vipcs/                          # 维普（部分高校）
│       └── ✅ adapter.md
│
├── pipelines/                           # 【Pipeline 详细定义 ✅ Batch 3 完成】4 种论文类型
│   ├── ✅ journal-pipeline.md          # 期刊：paper-writing + rebuttal
│   ├── ✅ conference-pipeline.md       # 会议：+ slides + poster
│   ├── ✅ undergrad-thesis-pipeline.md # 本科毕设：+ aigc-reduce + word + defense
│   └── ✅ master-thesis-pipeline.md    # 硕士毕设：+ blind-review + 严格阈值
│
├── integrations/                        # 【接入层 ✅ Batch 3 完成】20 个现成 skill 的 wrapper
│   │  每个 wrapper 定义：触发条件 + 调用参数 + 输出处理
│   │  ─── 选题/调研 (6) ───
│   ├── ✅ arxiv-wrapper.md
│   ├── ✅ semantic-scholar-wrapper.md
│   ├── ✅ research-lit-wrapper.md
│   ├── ✅ comm-lit-review-wrapper.md
│   ├── ✅ claude-paper-study-wrapper.md
│   ├── ✅ novelty-check-wrapper.md
│   │  ─── 理论 (2) ───
│   ├── ✅ proof-writer-wrapper.md
│   ├── ✅ formula-derivation-wrapper.md
│   │  ─── 图表 (4) ───
│   ├── ✅ scientific-visualization-wrapper.md
│   ├── ✅ matplotlib-tvhahn-wrapper.md
│   ├── ✅ mermaid-diagram-wrapper.md
│   ├── ✅ paper-illustration-wrapper.md
│   │  ─── 实验对接 (2) ───
│   ├── ✅ result-to-claim-wrapper.md
│   ├── ✅ ablation-planner-wrapper.md
│   │  ─── 投稿后/答辩 (4) ───
│   ├── ✅ rebuttal-wrapper.md
│   ├── ✅ paper-reviewer-wrapper.md
│   ├── ✅ paper-slides-wrapper.md
│   ├── ✅ paper-poster-wrapper.md
│   │  ─── 交付格式 (3) ───
│   ├── ✅ docx-wrapper.md              # ⭐ Batch 1 已造（毕设要交 Word）
│   ├── ✅ pptx-wrapper.md
│   └── ✅ pdf-wrapper.md
│
├── extensions/                          # 【扩展层 v0.2 新增】5 个新造 skill
│   ├── latex-to-word/                  # ⭐ 国内毕设必交 Word，pandoc 转换不够用
│   │   ├── ✅ SKILL.md
│   │   ├── ✅ README.md
│   │   └── 🚧 converter.py             # 后续迭代（核心 LaTeX→Word 转换器）
│   ├── thesis-defense-prep/            # ⭐ 答辩 PPT + 答辩问答模拟
│   │   ├── ✅ SKILL.md
│   │   └── ✅ README.md
│   ├── thesis-blind-review/            # ⭐ 硕博毕设盲审版（去作者信息）
│   │   ├── ✅ SKILL.md
│   │   └── ✅ README.md
│   ├── bilingual-abstract/             # ⭐ 中英文摘要平行对照检查
│   │   ├── ✅ SKILL.md
│   │   └── ✅ README.md
│   └── format-compliance-checker/      # ⭐ 学校格式规范字号/行距/页眉自动检查
│       ├── ✅ SKILL.md
│       └── ✅ README.md
│
├── platforms/                           # 【平台元数据 ✅ Batch A 完成】各 AI 平台说明
│   ├── claude/
│   │   └── ✅ README.md
│   ├── cursor/
│   │   └── ✅ README.md
│   ├── gemini/
│   │   └── ✅ README.md
│   ├── cline/
│   │   └── ✅ README.md
│   ├── chatgpt/
│   │   └── ✅ README.md
│   └── universal/
│       └── ✅ README.md                # 通用 prompt 包说明（实际包由 build.py 生成）
│
└── examples/                            # 【示例配置 ✅ Batch 3 完成】4 种典型场景
    ├── ✅ undergrad-thesis-example.yml # 本科毕设示例（北航雷达）
    ├── ✅ master-thesis-example.yml    # 硕士毕设示例（清华）
    ├── ✅ journal-paper-example.yml    # 期刊示例（IEEE_JOURNAL）
    └── ✅ conference-paper-example.yml # 会议示例（NeurIPS）
```

---

## 实现优先级 (P8 颗粒度对齐 v0.2)

按 MVP 原则分三批：

### Batch 1 · MVP（本科毕设端到端跑通）

```text
✅ SKILL.md                              已完成
✅ README.md                             已完成
✅ thesis.config.template.yml            已完成
✅ FILE_TREE.md                          已完成
🚧 scanners/project-scanner.py          【本批必造】
🚧 routers/intent-router.md             【本批必造】
🚧 detectors/cnki/adapter.md            【本批必造】
🚧 pipelines/undergrad-thesis-pipeline.md  【本批必造】
🚧 examples/undergrad-thesis-example.yml   【本批必造】
🚧 integrations/docx-wrapper.md         【本批必造·关键】
🚧 extensions/latex-to-word/SKILL.md    【本批必造·关键】
```

完成后：用户跑 `/thesis-helper <dir>` 能完成本科毕设：写 LaTeX → 降 AIGC → 转 Word → 验证。

### Batch A (✅ 已完成) · 跨平台支持 + ChatGPT

```text
✅ compilers/build.py                                    主入口路由
✅ compilers/README.md                                   编译规则
✅ compilers/targets/__init__.py
✅ compilers/targets/_common.py                          共享工具
✅ compilers/targets/{claude,cursor,gemini,cline,chatgpt,universal}.py   6 个 target
✅ platforms/{claude,cursor,gemini,cline,chatgpt,universal}/README.md    6 平台指南
```

实测验证：build.py --target all 一次编译 6 平台全部输出，ChatGPT 严格控制在 7500 字符内。

### Batch B (✅ 已完成) · 5 个 extensions 全造

```text
✅ extensions/latex-to-word/SKILL.md + README.md
✅ extensions/thesis-defense-prep/SKILL.md + README.md
✅ extensions/thesis-blind-review/SKILL.md + README.md
✅ extensions/bilingual-abstract/SKILL.md + README.md
✅ extensions/format-compliance-checker/SKILL.md + README.md
```

5 个 extension 全部 SKILL.md + README 落地，可独立调用或被 thesis-helper pipeline 触发。
辅助脚本（converter.py / checker.py）后续按需迭代。

### Batch 3 (✅ 已完成) · 全 4 类型 pipeline + 20 integrations + 检测器扩展

```text
✅ pipelines/journal-pipeline.md
✅ pipelines/conference-pipeline.md
✅ pipelines/master-thesis-pipeline.md
✅ examples/{journal,conference,master-thesis}-example.yml  (3 个)
✅ integrations/*-wrapper.md  (20 个，docx 已在 Batch 1)
✅ detectors/{turnitin,paperpass,vipcs}/adapter.md  (3 个)
✅ routers/{venue-router,detector-router}.md  (2 个)
```

实测验证：4 种论文类型全支持，20+1 现成 integrations 全接入，4 种检测器全覆盖。
build.py 重新跑 --target all 仍编译通过，所有新增文件被 claude target 完整复制。

---

## 与已有 skill 的关系（v0.2 全景）

```text
thesis-helper (本 skill)
    │
    ├── 直接调用 → ../PaperWriting/paper-writing/        (paper-* x9)
    ├── 直接调用 → ../aigc-reduce-skills/aigc-reduce/   (aigc-* x8)
    │
    ├── integrations 接入（17 个）
    │   ├── arxiv, semantic-scholar, research-lit, comm-lit-review,
    │   ├── claude-paper:study, novelty-check
    │   ├── proof-writer, formula-derivation
    │   ├── scientific-visualization, matplotlib-tvhahn,
    │   ├── mermaid-diagram, paper-illustration
    │   ├── result-to-claim, ablation-planner
    │   ├── rebuttal, paper_reviewer
    │   ├── paper-slides, paper-poster
    │   └── document-skills:docx/pptx/pdf
    │
    └── extensions 自研（5 个）
        ├── latex-to-word          (LaTeX → Word，国内毕设必备)
        ├── thesis-defense-prep    (答辩 PPT + 问答模拟)
        ├── thesis-blind-review    (盲审版生成)
        ├── bilingual-abstract     (中英文摘要平行检查)
        └── format-compliance-checker  (学校格式规范检查)
```
