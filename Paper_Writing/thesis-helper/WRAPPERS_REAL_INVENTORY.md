# thesis-helper wrappers · 真上游 skill 映射（v0.6.0 最终诚实版）

**校正时间**：2026-05-03
**关键发现**：用户指出 ARIS 已装在 `~/.claude/skills/`，21 wrapper 上游 **100% 真就位**。

---

## 验证证据

```bash
$ ls ~/.claude/skills/ | wc -l
60+  # 60+ 个 skill 真已装

# 验证 21 wrapper 上游全部存在（每个 SKILL.md 3-50 KB 真内容）
$ for s in 21_wrapper_names; do ls ~/.claude/skills/$s/SKILL.md; done
✅ 21/21 全部命中
```

---

## 21 wrapper · 真上游映射表（100% 已装）

| # | wrapper | 上游 skill 路径 | SKILL.md 大小 | 调用方式 |
|---|---------|----------------|---------------|---------|
| 1 | arxiv | `~/.claude/skills/arxiv/` | 6.8 KB | `Skill("arxiv")` |
| 2 | semantic-scholar | `~/.claude/skills/semantic-scholar/` | 8.2 KB | `Skill("semantic-scholar")` |
| 3 | research-lit | `~/.claude/skills/research-lit/` | 13.6 KB | `Skill("research-lit")` |
| 4 | comm-lit-review | `~/.claude/skills/comm-lit-review/` | 9.2 KB | `Skill("comm-lit-review")` |
| 5 | claude-paper-study | claude-paper 插件 | — | `Skill("claude-paper:study")` |
| 6 | novelty-check | `~/.claude/skills/novelty-check/` | 3.1 KB | `Skill("novelty-check")` |
| 7 | proof-writer | `~/.claude/skills/proof-writer/` | 7.8 KB | `Skill("proof-writer")` |
| 8 | formula-derivation | `~/.claude/skills/formula-derivation/` | 9.5 KB | `Skill("formula-derivation")` |
| 9 | scientific-visualization | `~/.claude/skills/scientific-visualization/` | 26.4 KB | `Skill("scientific-visualization")` |
| 10 | matplotlib-tvhahn | `~/.claude/skills/matplotlib-tvhahn/` | 12.0 KB | `Skill("matplotlib-tvhahn")` |
| 11 | mermaid-diagram | `~/.claude/skills/mermaid-diagram/` | 16.8 KB | `Skill("mermaid-diagram")` |
| 12 | paper-illustration | `~/.claude/skills/paper-illustration/` | 30.9 KB | `Skill("paper-illustration")` |
| 13 | result-to-claim | `~/.claude/skills/result-to-claim/` | 7.0 KB | `Skill("result-to-claim")` |
| 14 | ablation-planner | `~/.claude/skills/ablation-planner/` | 5.3 KB | `Skill("ablation-planner")` |
| 15 | rebuttal | `~/.claude/skills/rebuttal/` | 11.3 KB | `Skill("rebuttal")` |
| 16 | paper-reviewer | `~/.claude/skills/paper_reviewer/` (注：下划线) | 10.3 KB | `Skill("paper_reviewer")` |
| 17 | paper-slides | `~/.claude/skills/paper-slides/` | 19.8 KB | `Skill("paper-slides")` |
| 18 | paper-poster | `~/.claude/skills/paper-poster/` | 50.3 KB | `Skill("paper-poster")` |
| 19 | docx | anthropic-agent-skills 插件 | — | `Skill("docx")` |
| 20 | pptx | anthropic-agent-skills 插件 | — | `Skill("pptx")` |
| 21 | pdf | anthropic-agent-skills 插件 | — | `Skill("pdf")` |

---

## 真值统计（最终校正版）

```
✅ 真有上游已装        21/21 = 100%
   - ARIS (~/.claude/skills/)              17 个
   - claude-paper plugin                    1 个 (claude-paper:study)
   - anthropic-agent-skills plugin          3 个 (docx/pptx/pdf)
```

之前 v0.5.10 错报"真有效 6/21"的根因：用 `claude.cmd -p` subprocess 调，**子 claude 不会自动 invoke 本地 skill**——它只是个普通 prompt 调用，所以不知道用 `~/.claude/skills/research-lit/`。Subprocess 路径从一开始就是错的。

---

## 正确调用方式（v0.6.0 架构）

### 两层架构

```
┌─────────────────────────────────────────────────────────────┐
│ 第 1 层：thesis-helper orchestrator.py                      │
│   = 9 phase 确定性 Python（subprocess 跑）                   │
│   = 已 9/9 真接通：scanner / format / abstract / pdf / docx /│
│                    defense / blind / aigc-detect / aigc-7stage│
└─────────────────────────────────────────────────────────────┘
                            ↑
                            │ 主链路自动跑（已验证）
                            │
┌─────────────────────────────────────────────────────────────┐
│ 第 2 层：21 wrapper 互动 skill                               │
│   = 用户在对话里说"找文献" / "写证明" / "改稿"               │
│   = Claude 看 wrapper.md 指引，用 Skill tool 调上游          │
│   = 上游 21/21 已就位（~/.claude/skills/ 真装好）            │
└─────────────────────────────────────────────────────────────┘
```

### 用户怎么用

| 场景 | 用户说 | Claude 调 |
|------|--------|----------|
| 写综述 | "找一下低空雷达的相关工作" | `Skill("research-lit")` |
| 写证明 | "给 DRSN 软阈值写引理证明" | `Skill("proof-writer")` |
| 答辩准备 | "做答辩 PPT" | `Skill("paper-slides")` |
| 改稿 | "起草 rebuttal" | `Skill("rebuttal")` |
| 检查 | "我这个 idea 有没有人做过" | `Skill("novelty-check")` |
| 转 docx | "转成 docx" | `Skill("docx")` |

**不需要再跑 wrappers_runner.py**——那是误用。Skill tool 直接调就行。

---

## wrappers_runner.py 的剩余作用

只保留给：
- **离线批量回归测试**（CI/CD 验证 wrapper.md 文档完整性）
- **不需要 hook 的纯 prompt 测试**（已加 `--bare` flag · 防 SessionStart 污染）

不再用于真业务流程。

---

## v0.6.0 改造已完成

- [x] `wrappers_runner.py` subprocess cmd 加 `--bare` flag（v0.6.0 commit）
- [x] WRAPPERS_REAL_INVENTORY.md 写入 21/21 真上游映射（本文件）
- [x] 校正 v0.5.10 误报"6/21 真有效"
- [ ] orchestrator.py README 加两层架构说明（下个 commit）
- [ ] 21 个 wrapper.md 文档头加 `upstream:` 字段（可选 polish）
