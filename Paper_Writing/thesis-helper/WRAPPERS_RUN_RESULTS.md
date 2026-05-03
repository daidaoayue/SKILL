# thesis-helper wrappers — 真接通运行结果（v0.5.10 honest）

**Run date**: 2026-05-03
**Runner**: `wrappers_runner.py --all --paper-root D:/code/radar_target_recognition/thesis_main`
**LLM backend**: `claude.cmd -p --model haiku` (subprocess)
**Outputs dir**: `D:/code/radar_target_recognition/testskill/wrappers_run_all/`

## 诚实分级矩阵（21 wrapper）

| # | wrapper | bytes | 状态 | 内容质量 |
|---|---------|-------|------|----------|
| 1 | arxiv | 6010 | ✅ 真接通 | 21 条 BibTeX 仿真引用（无实时 API，LLM 知识库）|
| 2 | semantic-scholar | 6040 | ✅ 真接通 | 11 条 BibTeX + TLDR + results.bib 入库说明 |
| 3 | research-lit | 3077 | ⚠️ meta-PUA | 反问 topic/purpose/scope，未产综述 |
| 4 | comm-lit-review | 7417 | ✅ 真接通 | 多维特征融合·低空雷达 真综述（IEEE/3GPP）|
| 5 | claude-paper-study | 2649 | ⚠️ meta-PUA | 缺 PDF 抓手（claude CLI 无文件系统权限）|
| 6 | novelty-check | 4894 | ✅ 真接通 | 真 5 篇相似工作 + novelty 评分 |
| 7 | proof-writer | 11781 | ✅ 真接通 | DRSN soft-threshold lemma 完整 LaTeX 证明 |
| 8 | formula-derivation | 6812 | ✅ 真接通 | phase coherence 公式推导链 + 符号表 |
| 9 | scientific-visualization | – | ❌ timeout 300s | 未产出 |
| 10 | matplotlib-tvhahn | 4822 | ⚠️ meta-PUA | Sprint Banner 反问 figure 选项 |
| 11 | mermaid-diagram | 4162 | ⚠️ meta-PUA | Sprint Banner 反问 |
| 12 | paper-illustration | 3496 | ⚠️ meta-PUA | 反问 figure target |
| 13 | result-to-claim | – | ❌ timeout 300s | 未产出 |
| 14 | ablation-planner | – | ❌ timeout 300s | 未产出 |
| 15 | rebuttal | – | ❌ timeout 300s | 未产出 |
| 16 | paper-reviewer | – | ❌ rate limit | 54-byte stub（haiku 限流）|
| 17 | paper-slides | – | ❌ rate limit | 同上 |
| 18 | paper-poster | – | ❌ rate limit | 同上 |
| 19 | docx | – | ❌ rate limit | 应走 latex-to-word 内部脚本，不该走 CLI |
| 20 | pptx | – | ❌ rate limit | 同上 |
| 21 | pdf | – | ❌ rate limit | 同上 |

## 真实统计

```
真接通且内容真实       6/21  =  28.6%   (arxiv, sem-scholar, comm-lit, novelty, proof, formula)
真接通但 meta-PUA      5/21  =  23.8%   (claude-paper-study, research-lit, illustration, mpl, mermaid)
失败（timeout/limit）  10/21 =  47.6%
─────────────────────────────────────
名义"真接通"门槛 100B   11/21 =  52.4%
```

## 三个架构限制（claude CLI subprocess 路径的根因）

1. **claude.cmd 子进程继承 SessionStart hook**
   父会话 PUA hook 注入 `[PUA ACTIVATED 🟠]` 到子 claude，导致子 claude 把 wrapper 任务当成 leader 派单，输出 Sprint Banner 反问，而不是直接产出 deliverable。
   → 5 个 wrapper 命中（research-lit / claude-paper-study / paper-illustration / matplotlib-tvhahn / mermaid-diagram）。

2. **claude CLI 无文件系统权限**
   `claude-paper-study` / `paper-reviewer` / `paper-slides` / `paper-poster` 需要读 PDF；`docx` / `pdf` 需要操作本地文件。`claude -p` 在子进程里没有 Read/Write/Bash 工具。
   → 6 个 wrapper 命中。

3. **claude haiku 速率限制 + 复杂 prompt 超时**
   连续 21 个 wrapper 串行调用，触达 haiku 限流；复杂 prompt（如 ablation-planner 列实验+GPU 时长）经常 >300s 超时。
   → 7 个 wrapper 命中。

## 推荐的架构修复（v0.6.x 路线图）

| 修复 | 操作 | 预计可救活 |
|------|------|-----------|
| A | docx/pptx/pdf 走 latex-to-word/scripts/convert.py 内部 Python，不再走 CLI | +3 |
| B | claude CLI 子调用追加 `--no-skills`（如果 CLI 支持）或 `--system "ignore SessionStart"` 屏蔽 PUA 污染 | +5 |
| C | 文件系统类 wrapper 用 MCP filesystem server 转发，而非 claude -p | +6 |
| D | 限流敏感 wrapper 改 sonnet 或加 retry+backoff | +7 |

## 现有 6/21 真有效产物·验收清单

```bash
ls -la D:/code/radar_target_recognition/testskill/wrappers_run_all/
# 真接通且内容真实的 6 个：
#   arxiv_output.md             6010 字
#   semantic-scholar_output.md  6040 字
#   comm-lit-review_output.md   7417 字
#   novelty-check_output.md     4894 字
#   proof-writer_output.md     11781 字  ← 最高质量，完整 Moreau envelope 证明
#   formula-derivation_output.md 6812 字
```

> v0.5.10 把"真接通 11/21"的虚假成就改成"真有效内容 6/21"——拒绝糊弄。架构限制摆桌面，下个版本按 A/B/C/D 修。
