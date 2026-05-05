<div align="center">

# 📊 Weekly Report Writer

**A Claude Code skill for PhD students** · scan project → diff vs last week → write advisor-ready report

🇨🇳 [简体中文](README.zh-CN.md) · 🇺🇸 **English**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Version](https://img.shields.io/badge/version-v1.0-green.svg) ![Tests](https://img.shields.io/badge/tests-132%20passed-brightgreen.svg) ![Output](https://img.shields.io/badge/output-Markdown%20%2B%20PDF-orange.svg)

</div>

---

## Why use this

PhD work generates code, experiment data, paper drafts, theory derivations,
and figures faster than you can remember. By Friday, you're staring at
50 file changes asking "what did I actually do this week?".

This skill answers that for you. It scans your project directory, compares
to last week's snapshot, identifies advanced version chains (e.g. `xxx_v3.py
→ xxx_v4.py`), extracts metric changes (mean ± std across seeds), surfaces
new equations in your theory notes, and asks you only what it cannot infer.
Then it writes a structured advisor-ready weekly report.

## What it produces

Layout: **md + pdf** archived by month; **tex intermediates** isolated by year/month/day to prevent cross-week contamination.

```
<project>/.weekly_report/
  ├── <year>/<month>/<date>_baseline_report.{md,pdf}      ← baseline
  ├── <year>/<month>/<date>_W<n>_report.{md,pdf}          ← weekly increments
  └── tex/<year>/<month>/<day>/<date>_*_report.{tex,aux,log,out}

<reports_root>/
  ├── <year>/<month>/<date>_baseline_<short>.{md,pdf}
  ├── <year>/<month>/<date>_W<n>_<short>.{md,pdf}
  ├── tex/<year>/<month>/<day>/<date>_*_<short>.tex
  └── index.md   (cross-project index, all reports listed)
```

The report follows a PhD format: greeting, opening paragraph, major-work
sections with experiment results tables (mean ± std + 95% CI), theory blocks
with equations, embedded figures, week summary, next-week plan, asks for
advisor, closing wishes, signature, date range.

## Quickstart (first time, 10 minutes)

```bash
# 1. Init your project
/weekly-report init D:\code\my_phd_project

# Skill will:
#   - Scan to detect bucket roots (code/data/paper/...)
#   - Show you a draft project.toml — review it
#   - Walk all output JSONs to harvest metric keys
#   - Open metric_vocab_init.md asking you to classify ~30 keys
#     (one checkbox per key, 30s each)

# 2. Generate baseline total report
/weekly-report run

# Skill will:
#   - Open interview.md asking you ~5 questions about high-level direction
#   - Generate a 10-section baseline report including a 3-month roadmap
```

## Weekly use (after init, 5 minutes)

```bash
/weekly-report run

# 1. Skill asks: "active window? default 7 days"
# 2. Scans project (< 30s for ~70k data files)
# 3. Diffs vs last week
# 4. Opens interview.md with 5-9 sections (only the ones with content)
# 5. You fill the **请填**: blanks (5-10 minutes total)
# 6. Skill writes report.md
```

## What it scans

| Bucket | Default roots | What's tracked |
| --- | --- | --- |
| code | Forecasting/, hardware/, src/ | .py / .cpp / .h, version chains |
| experiment_data | */output, */results | .json metrics, multi-seed agg |
| paper | paper_writing/ | .tex / .md / .docx, section diff |
| reading | research-wiki/, docs/ | .md / .pdf, new papers |
| theory | theory/, derivations/ | math blocks ($$, \(\), equation env) |
| figures | */ppt_figures, */figs | .png / .svg / .pdf, embedded in report |
| checkpoint_signal | */checkpoint, */weights_* | filename regex (acc/epoch/seed) only |

## What it does NOT do

🚫 NEVER modifies your project code. Only writes to `.weekly_report/` and `D:\code\reports\`.

- Does not parse `git log` (works without git)
- Does not read training checkpoint contents (file names only)
- Does not access external systems (Slack/email/issues)
- Does not do AST-level code diff

## Configuration

Edit `<project>/.weekly_report/project.toml` after init. Full field reference
in `references/project-toml-reference.md`. The most common things you'd change:

- `[buckets.code] roots = [...]` — add your custom code dirs
- `[project] advisor = "陈老师"` — used in greeting
- `[project] student = "李越"` — used in signature
- `[buckets.figures] max_per_report = 5` — figure cap

## Maintaining `metric_vocab.json`

When the skill encounters a numeric JSON key it has never seen, it asks you to
classify (metric / config / ignore). Each classification is 30 seconds and
saved permanently. Direct edits to `metric_vocab.json` are also fine.

See `references/metric-vocab-guide.md` for details.

## Multi-project

Each project has its own `.weekly_report/`. They never share state. Run init
once per project. Reports go into the same `D:\code\reports\` aggregate
folder, organized by year/month.

## Sharing with your peers (师弟师妹)

```bash
# Copy the entire skill folder
cp -r D:\code\github_skill\weekly_report ~/.claude/plugins/

# Have them open this README.md and run init on their project.
# Their metric_vocab.json will be regenerated against their project.
```

The skill is project-agnostic — peer's project.toml will be different from
yours. Bucket roots, advisor name, metrics — all separate.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| Scan extremely slow | Too many ckpt files in `roots` | Move ckpt dir under `checkpoint_signal.roots` only |
| Report missing my changes | Bucket root not configured | Add to `project.toml [buckets.code] roots` |
| Wrong metric in comparison table | metric_vocab miscategorized | Edit `metric_vocab.json` |
| Path whitelist error | Skill bug | File issue with stack trace |
| Version chain over-split | Heuristic too narrow | Add to `family_aliases.json` |

See `references/faq.md` for more.

## Architecture

```
SKILL.md (orchestrator, LLM-driven)
   ↓
scripts/ (deterministic Python)
   ├── scan_project.py      # ThreadPool walker
   ├── compute_diff.py      # cross-week diff
   ├── extract_metrics.py   # JSON metric extraction
   ├── parse_filename.py    # version chain heuristic
   ├── theory_extractor.py  # math block scanner
   ├── figure_picker.py     # figure candidate selection
   ├── interview_generator.py  # interview.md producer
   ├── parse_interview.py   # questionnaire parser
   ├── init_project.py      # auto-detect + project.toml scaffold
   ├── update_index.py      # cross-project index.md
   ├── metric_vocab.py      # vocab IO
   ├── path_guard.py        # write-whitelist enforcer
   ├── ignore_rules.py      # glob ignore matcher
   ├── file_metadata.py     # single-file inspector
   └── bucket_classifier.py # path → bucket
   ↓
references/ (LLM context)
assets/ (templates)
```

## License & Credit

Internal lab tool. Maintain in your group's git repo. Iterate together.
Credit when sharing publicly.
