<div align="center">

# 🛠️ SKILL

**Claude Code skill collection maintained by daidaoayue**

🇨🇳 [简体中文](README.md) · 🇺🇸 **English**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Skills](https://img.shields.io/badge/skills-26%2B-green.svg) ![Categories](https://img.shields.io/badge/categories-2%20published-blue.svg)

</div>

---

> A monorepo of Claude Code skills, organized by use case. All skills can be installed into `~/.claude/skills/` or via the Claude Code marketplace mechanism.

---

## 📂 Categories Overview

| Category | Status | Current | Details |
|------|------|------|------|
| 📝 [Paper_Writing](Paper_Writing/) · Academic Writing | ✅ Published | **3 packages / 25+ skills** · thesis-helper / aigc-reduce-skills / PaperWriting | [→ Details](Paper_Writing/) |
| ⚡ [weekly_report](weekly_report/) · Weekly Reports | ✅ Published | **1 package / 1 skill** · PhD weekly-report automation | [→ Details](weekly_report/) |
| 💻 Coding · Programming Aids | ⏳ Planned | – | – |
| 🔬 Research · Research Tools | ⏳ Planned | – | – |

> Want to push a category to release sooner? Open an [Issue](https://github.com/daidaoayue/SKILL/issues) to vote or contribute a PR.

---

## 📝 Paper_Writing · Academic Writing

> ✅ Published · 3 skill packages · 25+ skills · covers topic-selection → writing → AIGC-reduction → submission/defense

![thesis-helper workflow architecture](Paper_Writing/thesis-helper/diagrams/variant-E-clean.png)

| Skill Package | Entry | One-liner |
|---------|------|--------|
| ⭐ `thesis-helper` | `/thesis-helper PATH` | One-stop entry · point to project dir, runs all 9 phases automatically |
| `aigc-reduce-skills` | `/aigc降低` | 7-stage pipeline AIGC-reduction + model-driven |
| `PaperWriting` | `/paper-writing` etc. | Paper writing 9-skill collection |

**🌐 Cross-AI compatibility**: thesis-helper uses `compilers/build.py` to compile a single source-of-truth into 6 target platforms ——
**Claude Code** / **Cursor** (`.cursorrules`) / **Gemini CLI** (`GEMINI.md`) / **Cline** (`.clinerules`) / **ChatGPT** / **Universal** (generic prompt pack any AI can copy-paste). Not Claude-exclusive, works across the toolchain.

**Details** → [Paper_Writing/README.md](Paper_Writing/) (full pipeline · 9-tier word-count standards · install · cross-AI compile · recommended combos)

---

## ⚡ weekly_report · PhD Weekly Report Generator

> ✅ Published · 1 skill package · scan project → diff vs last week → write report

| Skill Package | Entry | One-liner |
|---------|------|--------|
| ⭐ `weekly-report` | `/weekly-report init <project>` then `/weekly-report run` | PhD weekly-report automation: scan project → identify version-chain advancement → aggregate multi-seed metrics → extract formula blocks → L3 questionnaire → output PhD-format Markdown + PDF |

**🔥 Core capabilities**:
- 🔒 Red line: **never modifies user's project code** (writes only to `<project>/.weekly_report/` and aggregate dir)
- 🔍 ThreadPool concurrent scanner — large repos produce a manifest in seconds
- 📈 Cross-seed metric aggregation (mean ± std); auto-detects version-chain advancement within a family (e.g. `train_v3.py → train_v4.py`)
- 📐 Extracts formula blocks from `.md` / `.tex` (supports `$$`, `\(\)`, `\begin{equation}`), preserving the parent section
- 📄 PDF rendering: pandoc + xelatex, academic style (Chinese serif body + sans-serif headings)

**Details** → [weekly_report/README.md](weekly_report/) (install · config · multi-project isolation · troubleshooting)

---

## 💻 Coding · Programming Aids

> ⏳ Planned · no skills published yet

**Planned directions**: code review / refactoring aid / debug mode / API testing / git workflow / CI pipelines / doc generation

> Welcome Issues to request features or contribute skill packages.

---

## 🔬 Research · Research Tools

> ⏳ Planned · no skills published yet

**Planned directions**: literature management (zotero/obsidian bridges) / idea validation / experiment scheduling / reproducibility checks / dataset management / experiment logging

> Welcome Issues to request features or contribute skill packages.

---

## 🚀 Installation Methods

### Method A · Claude Code marketplace (Recommended for `weekly-report`)

```
# Inside Claude Code:
/plugin marketplace add daidaoayue/SKILL
/plugin install weekly-report@daidaoayue-skills
```

### Method B · Full clone + junction/symlink (for any skill)

```bash
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL

# Windows (PowerShell · no admin needed)
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\<skill-name>" -Target "$env:USERPROFILE\SKILL\<category>\<skill-name>"

# Linux / macOS
ln -s ~/SKILL/<category>/<skill-name> ~/.claude/skills/<skill-name>
```

### Method C · Full clone + copy (one-shot, no auto-update)

```bash
git clone https://github.com/daidaoayue/SKILL.git ~/SKILL
cp -r ~/SKILL/<category>/<skill-name> ~/.claude/skills/
```

### Method D · sparse checkout (download just one subdir)

```bash
mkdir -p ~/.claude/skills && cd ~/.claude/skills
git clone --depth 1 --filter=blob:none --sparse https://github.com/daidaoayue/SKILL.git _tmp
cd _tmp && git sparse-checkout set <category>/<skill-name>
mv <category>/<skill-name> ../
cd .. && rm -rf _tmp
```

> Each category's specific install commands, dependencies, and usage examples → see the `README.md` in each category folder.

---

## 🗂️ Directory Convention

```
SKILL/                                    ← repo root
├── README.md / README.en.md              ← this file (categories overview, ZH+EN)
├── LICENSE                               ← MIT
├── .claude-plugin/marketplace.json       ← Claude Code marketplace entry
├── Paper_Writing/                        ← ✅ Published
│   ├── README.md
│   ├── thesis-helper/
│   ├── aigc-reduce-skills/
│   └── PaperWriting/
├── weekly_report/                        ← ✅ Published (PhD weekly report)
│   ├── commands/weekly-report.md         ← slash command definition
│   └── skills/weekly-report-writer/      ← skill content
├── Coding/                               ← ⏳ Planned
└── Research/                             ← ⏳ Planned
```

**Directory placement rules for new skills**:
- Academic / paper writing → `Paper_Writing/`
- Programming / code-related → `Coding/`
- Research tools / experiments / data → `Research/`
- Large self-contained plugin skills can live at the repo root (e.g. `weekly_report/`)
- Unsure → open an Issue to discuss

---

## 🤝 Contributing

Issues / PRs welcome:
- **Add new skill packages**: place under the matching category folder, or open a new category folder if needed
- **Improve existing skills**: dictionaries / pipelines / templates / docs
- **Contribute samples / data**: CNKI red-flagged samples to `aigc-reduce-*` dictionaries / new paper templates / etc.
- **Translation**: README / SKILL.md to other languages

Before submitting a PR:
- Skill entry (slash command) is unique and non-conflicting
- Has `SKILL.md` (with frontmatter `description` / triggers)
- Has minimal README explaining usage
- License compatible with MIT

---

## 📜 License

MIT — use freely, fork at will.

> ⚠️ Skills under `Paper_Writing/PaperWriting/` (excluding `paper_reviewer`) come from the [skills-codex](https://github.com/skills-codex) plugin ecosystem; **this repo is for personal backup and learning purposes only and does not claim original authorship**. If you believe there is infringement, please contact for removal.
