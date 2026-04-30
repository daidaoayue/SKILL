# AIGC率降低·全自动学术降痕流水线

> 给 Claude Code 的一套学术论文降 AIGC 率技能包：5 段串行流水线，1 个总入口，**全自动跑完整稿**。

## ✨ 一句话价值

输入一句 `/aigc降低 你的论文.tex`，Claude 自动按章节分块，对每一块依次执行 **词汇精炼 → 节奏变频 → 逻辑衔接 → 语义精细化 → 困惑度重构** 5 步处理，直到全文跑完。**不改数据、不改观点、不改引文**，只让表达更像严谨的人类作者。

## 📦 包含 6 个 Skill

| Skill | 角色 | 阶段 |
|-------|------|------|
| `aigc-reduce` | 总编排器（`/aigc降低` 入口） | Pipeline |
| `aigc-reduce-vocab` | 词汇精炼器 | Stage 1/5 |
| `aigc-reduce-rhythm` | 节奏变频师 | Stage 2/5 |
| `aigc-reduce-cohesion` | 逻辑衔接专家 | Stage 3/5 |
| `aigc-reduce-hedging` | 语义精细化工具 | Stage 4/5 |
| `aigc-reduce-perplexity` | 困惑度重构员 | Stage 5/5 |

## 🚀 安装（30 秒）

> 本 skill 包位于 `daidaoayue/SKILL` 大仓库的 `Paper_Writing/aigc-reduce-skills/` 子目录下，下面三种方式任选其一。

### 方式一：完整 clone（最简单）

```bash
# macOS / Linux / Windows (Git Bash) 通用
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL
cp -r ~/SKILL/Paper_Writing/aigc-reduce-skills/aigc-reduce* ~/.claude/skills/
```

### 方式二：Sparse checkout（只下载本 skill 包，省流量）

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills
git clone --depth 1 --filter=blob:none --sparse https://github.com/daidaoayue/SKILL.git _tmp
cd _tmp && git sparse-checkout set Paper_Writing/aigc-reduce-skills
mv Paper_Writing/aigc-reduce-skills/aigc-reduce* ../
cd .. && rm -rf _tmp
```

### 方式三：手动下载 ZIP

1. 打开 https://github.com/daidaoayue/SKILL → `Code` → `Download ZIP`
2. 解压后进入 `SKILL-main/Paper_Writing/aigc-reduce-skills/`
3. 把 6 个 `aigc-reduce*` 文件夹**整体放进**：
   - macOS / Linux：`~/.claude/skills/`
   - Windows：`C:\Users\<你的用户名>\.claude\skills\`
4. 重启 Claude Code

## 🎯 使用

打开 Claude Code，在任意项目下：

```
/aigc降低 path/to/your/paper.tex
```

或粘贴一段长文本：

```
/aigc降低 <粘贴 ≥300 字的论文段落>
```

Claude 会自动：
1. 切块（LaTeX 按 `\section` 切；Markdown 按标题切；纯文本按双换行切）
2. 按 AI 痕迹严重度排序：摘要 > 引言 > 讨论 > 文献 > 结论 > 方法 > 结果
3. 对每块串行跑完 5 步流水线
4. 输出 3 个文件：`*_aigc-reduced.<ext>`、`aigc-reduce-report.md`、`aigc-reduce-trace.md`

## 🔧 单步调用（高级用法）

如果你只想跑某一步，可以直接调用对应 skill：

```
/aigc-reduce-vocab        # 只清洗触发词
/aigc-reduce-rhythm       # 只调节奏
/aigc-reduce-cohesion     # 只焊接段间过渡
/aigc-reduce-hedging      # 只注入 caveat
/aigc-reduce-perplexity   # 只破坏 N-gram 套搭配
```

## 🧱 流水线总览

```
[输入完整稿件]
       ↓
   [Phase 0: 切块 + 优先级排序]
       ↓
   ┌───────── 对每个 chunk 串行执行 ─────────┐
   │  Step 1: aigc-reduce-vocab       (词汇)  │
   │  Step 2: aigc-reduce-rhythm      (节奏)  │
   │  Step 3: aigc-reduce-cohesion    (衔接)  │
   │  Step 4: aigc-reduce-hedging     (克制)  │
   │  Step 5: aigc-reduce-perplexity  (困惑度)│
   └──────────────────────────────────────────┘
       ↓ 循环直到全部 chunk 处理完
   [Phase Final: 整稿一致性校对]
       ↓
   [输出投稿就绪稿 + 修改报告 + 流水线 trace]
```

## ⚠️ 三条红线（5 步共享）

- ❌ 绝对不改动原稿数据、观点、引文、研究结论本身
- ❌ 绝对不一次性整篇丢给 LLM——必须按章节/段落颗粒度切分
- ❌ 绝对不许处理两三段就停下——必须把所有 chunk 全部跑完 5 步流水线

## 📋 各 Stage 处理什么

| Stage | 处理目标 | 量化指标 |
|-------|---------|---------|
| 1. 词汇精炼 | 根除 delve / foster / pivotal / underscore / 深入探讨 / 至关重要 等 | 触发词清零 |
| 2. 节奏变频 | 句长方差 < 30 → > 80，长短交错 | σ² 提升 3 倍+ |
| 3. 逻辑衔接 | 删除 Furthermore / Moreover / 此外 / 因此，用语义链 | 段首禁用词清零 |
| 4. 语义精细化 | proves → suggests，加 caveat / boundary condition | 实证主张全部加边界 |
| 5. 困惑度重构 | 破坏 "rapid development" / "近年来" / "extensive experiments demonstrate" | N-gram 替换 + 整稿一致性 |

## 🛠️ 系统要求

- Claude Code（任意版本）
- 6 个 skill 文件夹放在 `~/.claude/skills/` 下即可被自动加载

## 📜 License

MIT — 随便用，欢迎二次开发。

## 🤝 贡献

欢迎提 Issue / PR：
- 发现新的 LLM 触发词 → 贡献到 `aigc-reduce-vocab` 词表
- 发现新的高频 N-gram → 贡献到 `aigc-reduce-perplexity` 套搭配库
- 适配新的语种 → 复制现有 skill 改 Trigger Words 列表

---

**因为信任所以简单——把降 AIGC 这件事，做成 owner 闭环。**
