# SKILL — Claude Code 技能集合

> daidaoayue 维护的 Claude Code skill 大仓库，按使用场景分类组织。所有 skill 均可直接放入 `~/.claude/skills/` 目录加载使用。

## 📂 当前收纳

### 📝 Paper_Writing（论文写作类）

| Skill 包 | 入口 | 介绍 |
|---------|------|------|
| [`aigc-reduce-skills`](Paper_Writing/aigc-reduce-skills/) | `/aigc降低` | 全自动学术降 AIGC 率流水线，5 段串行（词汇 → 节奏 → 衔接 → 模糊限制 → 困惑度），按章节分块跑完整稿，不改数据/观点/引文 |

> 后续会逐步收纳更多写作类 skill：审稿、画图、排版、投稿合规检查 …

---

## 🚀 快速安装某个 skill 包

以 `aigc-reduce-skills` 为例：

```bash
# 完整 clone（最简单）
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL
cp -r ~/SKILL/Paper_Writing/aigc-reduce-skills/aigc-reduce* ~/.claude/skills/
```

或只下载某一个子目录（sparse checkout 节省流量）：

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills
git clone --depth 1 --filter=blob:none --sparse https://github.com/daidaoayue/SKILL.git _tmp
cd _tmp && git sparse-checkout set Paper_Writing/aigc-reduce-skills
mv Paper_Writing/aigc-reduce-skills/aigc-reduce* ../
cd .. && rm -rf _tmp
```

具体使用文档详见每个 skill 包目录下的 `README.md`。

---

## 🗂️ 目录约定

```
SKILL/                          ← 大仓库根目录
├── README.md                   ← 本文件（导航）
├── LICENSE                     ← MIT
├── Paper_Writing/              ← 论文写作类
│   └── aigc-reduce-skills/     ← AIGC 率降低流水线
│       ├── README.md
│       ├── aigc-reduce/        ← 总入口（/aigc降低）
│       ├── aigc-reduce-vocab/
│       ├── aigc-reduce-rhythm/
│       ├── aigc-reduce-cohesion/
│       ├── aigc-reduce-hedging/
│       └── aigc-reduce-perplexity/
├── （未来）Coding/             ← 代码类
├── （未来）Research/           ← 研究类
└── （未来）Productivity/       ← 效率类
```

## 🤝 贡献

欢迎 Issue / PR：
- 新增 skill 包（按场景归到对应一级目录，没有的话开新目录）
- 优化现有 skill 的词表、流水线、模板
- 翻译 README 到其他语种

## 📜 License

MIT — 随便用，欢迎 fork 改造。
