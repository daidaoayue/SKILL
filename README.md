<div align="center">

# 🛠️ SKILL

**带刀阿越 维护的 Claude Code 技能集合**

🇨🇳 **简体中文** · 🇺🇸 [English](README.en.md)

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Skills](https://img.shields.io/badge/skills-26%2B-green.svg) ![Categories](https://img.shields.io/badge/categories-2%20published-blue.svg)

</div>

---

> Claude Code skill 大仓库。按使用场景分类组织，所有 skill 均可装入 `~/.claude/skills/` 或通过 marketplace 安装。

---

## 📂 收纳分类总览

| 分类 | 状态 | 当前 | 详情 |
|------|------|------|------|
| 📝 [Paper_Writing](Paper_Writing/) · 论文写作 | ✅ 已发布 | **3 包 / 25+ skills** · thesis-helper / aigc-reduce-skills / PaperWriting | [→ 详情](Paper_Writing/) |
| ⚡ [weekly_report](weekly_report/) · 周报生成 | ✅ 已发布 | **1 包 / 1 skill** · PhD 周报全自动 | [→ 详情](weekly_report/) |
| 💻 Coding · 编程辅助 | ⏳ 规划中 | – | – |
| 🔬 Research · 科研工具 | ⏳ 规划中 | – | – |

> 想推动某个分类提前发布？开 [Issue](https://github.com/daidaoayue/SKILL/issues) 投票或贡献 PR。

---

## 📝 Paper_Writing · 论文写作

> ✅ 已发布 · 3 个 skill 包 · 25+ skills · 覆盖选题→写作→降 AIGC→投稿/答辩

![thesis-helper 工作流架构图](Paper_Writing/thesis-helper/diagrams/variant-E-clean.png)

| Skill 包 | 入口 | 一句话 |
|---------|------|--------|
| ⭐ `thesis-helper` | `/thesis-helper PATH` | 一站式入口·给项目目录就自动跑完 9 phase |
| `aigc-reduce-skills` | `/aigc降低` | 7 段流水线降 AIGC + 模型驱动 |
| `PaperWriting` | `/paper-writing` 等 | 论文写作 9 skill 集合 |

**🌐 跨 AI 适配**：thesis-helper 用 `compilers/build.py` 一份真源编译到 6 个目标平台 ——
**Claude Code** / **Cursor** (`.cursorrules`) / **Gemini CLI** (`GEMINI.md`) / **Cline** (`.clinerules`) / **ChatGPT** / **Universal**（任意 AI 复制粘贴的通用 prompt 包）。不是 Claude 独占，跨工具链可用。

**详情** → [Paper_Writing/README.md](Paper_Writing/) （含完整流程清单 / 9 类字数门槛规范 / 安装命令 / 跨 AI 编译 / 推荐组合）

---

## ⚡ weekly_report · PhD 周报生成器

> ✅ 已发布 · 1 个 skill 包 · 扫工程 → 对比上周 → 自动写周报

| Skill 包 | 入口 | 一句话 |
|---------|------|--------|
| ⭐ `weekly-report` | `/weekly-report init <project>` 然后 `/weekly-report run` | 博士生周报全自动：扫工程 → 识别版本链推进 → 跨 seed 聚合指标 → 抽公式块 → L3 质询 → 出 PhD 风格 Markdown + PDF 周报 |

**🔥 核心能力**：
- 🔒 红线：永不修改用户工程代码（仅写 `.weekly_report/` 与聚合目录）
- 🔍 ThreadPool 并发扫描，71315 数据文件 < 30s
- 📈 多 seed 聚合 mean ± std + 95% CI，自动抓 v25→v26 版本链推进
- 📐 抽 `$$ / \( \) / equation` 公式块，识别 `## H2` 与 `\section{}` 双格式
- 📄 PDF：pandoc + xelatex，宋体正文 + 黑体标题，学术风格

**详情** → [weekly_report/README.md](weekly_report/) （含安装方式 / 配置说明 / 多项目隔离 / 故障排除）

---

## 💻 Coding · 编程辅助

> ⏳ 规划中 · 尚未收纳具体 skill

**计划方向**：代码评审 / 重构辅助 / debug 模式 / API 测试 / git 工作流 / CI 流水线 / 文档生成

> 欢迎 Issue 提需求 或 贡献 skill 包。

---

## 🔬 Research · 科研工具

> ⏳ 规划中 · 尚未收纳具体 skill

**计划方向**：文献管理（zotero/obsidian 桥接）/ idea 验证 / 实验调度 / 复现性检查 / 数据集管理 / 实验日志

> 欢迎 Issue 提需求 或 贡献 skill 包。

---

## 🚀 通用安装方式

任意 skill 包都可用以下三种方式装入 `~/.claude/skills/`：

### 方式 A · 完整 clone + junction/symlink（推荐 · 仓库与本地同步）

```bash
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL

# Windows（PowerShell · 无需管理员）
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\<skill-name>" -Target "$env:USERPROFILE\SKILL\<分类>\<skill-name>"

# Linux / macOS
ln -s ~/SKILL/<分类>/<skill-name> ~/.claude/skills/<skill-name>
```

### 方式 B · 完整 clone + 复制（一次性，不再随仓库更新）

```bash
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL
cp -r ~/SKILL/<分类>/<skill-name> ~/.claude/skills/
```

### 方式 C · sparse checkout（只下载某个子目录，省流量）

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills
git clone --depth 1 --filter=blob:none --sparse https://github.com/daidaoayue/SKILL.git _tmp
cd _tmp && git sparse-checkout set <分类>/<skill-name>
mv <分类>/<skill-name> ../
cd .. && rm -rf _tmp
```

> 各分类的具体安装命令、依赖说明、使用示例 → 见对应分类目录下的 `README.md`。

---

## 🗂️ 目录约定

```
SKILL/                                    ← 大仓库根目录
├── README.md / README.en.md              ← 本文件（分类总览，中英双语）
├── LICENSE                               ← MIT
├── .claude-plugin/marketplace.json       ← Claude Code marketplace 入口
├── Paper_Writing/                        ← ✅ 已发布
│   ├── README.md                         ← 分类详情（推荐入口、流程清单、字数门槛）
│   ├── thesis-helper/                    ← 一站式入口（含 5 种工作流图）
│   ├── aigc-reduce-skills/               ← AIGC 率降低 v4
│   └── PaperWriting/                     ← 论文写作 9 skill 集合
├── weekly_report/                        ← ✅ 已发布（PhD 周报生成器）
│   ├── commands/weekly-report.md         ← slash command 定义
│   └── skills/weekly-report-writer/      ← skill 内容
├── Coding/                               ← ⏳ 规划中
└── Research/                             ← ⏳ 规划中
```

**新增 skill 的目录归属规则**：
- 论文/学术写作 → `Paper_Writing/`
- 编程/代码相关 → `Coding/`
- 科研工具/实验/数据 → `Research/`
- 体量较大、独立 plugin 的 skill 可置于根目录（如 `weekly_report/`）
- 不确定 → 开 Issue 讨论分类归属

---

## 🤝 贡献

欢迎 Issue / PR：
- **新增 skill 包**：按场景归到对应分类目录，没有的话开新分类目录
- **优化现有 skill**：词表 / 流水线 / 模板 / 文档
- **贡献样本/数据**：CNKI 实测标红样本到 `aigc-reduce-*` 词库 / 新论文模板等
- **翻译**：README / SKILL.md 到其他语种

提 PR 前请确认：
- skill 入口（slash command）唯一不冲突
- 有 `SKILL.md`（含 frontmatter description / triggers）
- 有最小 README 说明用法
- License 兼容 MIT

---

## 📜 License

MIT — 随便用，欢迎 fork 改造。

> ⚠️ `Paper_Writing/PaperWriting/` 下除 `paper_reviewer` 外的 skills 来自 [skills-codex](https://github.com/skills-codex) 插件生态，**本仓库仅作个人备份与学习用途，不主张原创权**。如有侵权请联系删除。
