---
description: "PhD 学生周报生成 — 扫描工程、对比上周、L3 质询、出 PhD 风格周报"
argument-hint: "[init|run|rebase] <project-path>"
---

User invoked `/weekly-report`. Interpret the arguments and run the workflow.

## Argument parsing

Examples of how the user might invoke this:
- `/weekly-report` — assume `run` on the most recently-used project (read `latest.txt` if multiple .weekly_report dirs exist)
- `/weekly-report init D:\code\my_proj` — first-time setup
- `/weekly-report run` — incremental weekly diff
- `/weekly-report run --project D:\code\my_proj`
- `/weekly-report rebase --week 2026-W17` — rebuild a specific past week

If the user typed only `/weekly-report` with no args, ask: 「要 init 新项目还是 run 已有项目？告诉我项目路径。」

## What to do

You MUST invoke the skill `weekly-report-writer` via the `Skill` tool, passing along the user's args. The skill itself contains the orchestration: scanner → diff → interview → writer.

After the skill takes over, follow its SKILL.md instructions. Key reminders:

1. 🚫 Red line: never write outside `<project>/.weekly_report/` or `D:\code\reports\`. The skill enforces this via `scripts/path_guard.py`.
2. Always ask the user `active_window_days` at runtime (default 7).
3. For `init` mode: detect buckets, generate `project.toml`, run metric_vocab labeling, then output baseline report.
4. For `run` mode: scanner → diff → interview.md → wait for user → writer →落档.

## Important context

- This skill is project-agnostic. The user can run it on any project directory.
- Sample reports go to `D:\code\reports\` (cross-project aggregate) and `<project>/.weekly_report/` (per-project archive).
- Never modify the user's project code. Read-only access only.
