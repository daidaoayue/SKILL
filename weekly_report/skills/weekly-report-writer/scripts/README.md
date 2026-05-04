# scripts/ Module Map

Deterministic Python helpers used by SKILL.md. Each is single-purpose,
testable in isolation, no LLM calls.

| Script | Purpose | Tested? |
| --- | --- | --- |
| `parse_filename.py` | Extract family/version/status from file stems | ✅ 16 tests |
| `path_guard.py` | Enforce write whitelist (red line) | ✅ 7 tests |
| `ignore_rules.py` | Glob-based file ignore matcher | ✅ 12 tests |
| `file_metadata.py` | Per-file size/mtime/sha1 inspector | ✅ 5 tests |
| `bucket_classifier.py` | Map relative path → bucket name | ✅ 10 tests |
| `scan_project.py` | ThreadPool walker → manifest.json | ✅ 5 tests |
| `extract_metrics.py` | JSON metric/config classifier + multi-seed agg | ✅ 16 tests |
| `metric_vocab.py` | Read/write metric_vocab.json | ✅ 4 tests |
| `theory_extractor.py` | Extract $$/\(\)/equation env blocks | ✅ 5 tests |
| `figure_picker.py` | Select figure candidates by mtime + size + window | ✅ 5 tests |
| `compute_diff.py` | Cross-week manifest diff | ✅ 7 tests |
| `interview_generator.py` | Render interview.md from diff | ✅ 5 tests |
| `parse_interview.py` | Parse filled interview.md → JSON | ✅ 5 tests |
| `init_project.py` | Auto-detect buckets + render project.toml | ✅ 4 tests |
| `metric_vocab_init.py` | Build/parse first-run metric labeling questionnaire | ✅ 12 tests |
| `render_pdf.py` | md → pandoc → LaTeX → xelatex → PDF | ✅ 4 tests |
| `run_baseline.py` | Top-level runner: scan + aggregate + render md + render PDF | manual |
| `update_index.py` | Maintain cross-project index.md | ✅ 4 tests |

## Running tests

```bash
cd D:/code/github_skill/weekly_report
python -m pytest scripts/tests -v
```

All tests use `pytest` and tmp directories. No real project data is touched.

## Inter-script dependencies

```
SKILL.md
  └── scan_project.py
        ├── ignore_rules.py
        ├── file_metadata.py
        ├── bucket_classifier.py
        └── parse_filename.py

  └── compute_diff.py            (no script deps; pure data)

  └── extract_metrics.py         (no script deps)

  └── metric_vocab.py            (no script deps)

  └── interview_generator.py     (no script deps)

  └── parse_interview.py         (no script deps)

  └── theory_extractor.py        (no script deps)

  └── figure_picker.py           (no script deps)

  └── init_project.py            (no script deps)

  └── update_index.py            (no script deps)

  └── path_guard.py              (used by all that write)
```

## Adding a new script

1. Write `scripts/<name>.py` with module docstring linking to spec section.
2. Write `scripts/tests/test_<name>.py` with 3+ realistic cases.
3. Update this table.
4. Wire into `SKILL.md` workflow if user-facing.
