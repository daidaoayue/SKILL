# Metric Vocabulary Guide

This guide explains what `metric_vocab.json` is, how the first-time labeling
form works, and how to maintain it.

## What is metric_vocab.json

A per-project file at `<project>/.weekly_report/metric_vocab.json` that
classifies every numeric JSON top-level key into one of four categories:

| Category | Meaning |
| --- | --- |
| metric | Reported in weekly comparison tables (e.g. `track_acc`) |
| config | Experiment setup, not compared (e.g. `seed`, `backbone`) |
| ignored | Numeric but not interesting (e.g. `_internal_id`) |
| unknown | Not yet classified — pending user confirmation |

## First-time labeling

When you run `/weekly-report init <project>`, the skill scans every output JSON
in your project, applies hint-based heuristics (any key containing `acc/loss/f1/auc/...`
becomes a metric candidate), and writes the unresolved keys to
`metric_vocab_init.md`:

```markdown
### track_mean_per_seed
- 上下文：在 Forecasting/output/inference_results.json 中，与 seeds=[1..10] 同时出现
- 自动猜测：metric / aggregate of track_acc
- [ ] 是指标，方向 higher_better
- [ ] 是指标，方向 lower_better
- [ ] 是配置（不参与对比）
- [ ] 忽略
```

You check ONE box per key. Estimated time: 30 keys × 30 seconds = 5–10 minutes.

The skill parses your filled `metric_vocab_init.md` and writes the result to
`metric_vocab.json`. From this point on, the same keys are classified
automatically.

## Direction (higher_better vs lower_better)

For metrics, you must specify a direction:

- `higher_better`: accuracy, F1, AUC, IoU, recall, precision, BLEU
- `lower_better`: loss, error, MAE, RMSE, perplexity

This drives the sign of the "delta" column in the weekly comparison table:
- `track_acc 0.928 → 0.942` shows `+1.4%` (good, green).
- `loss 0.21 → 0.18` shows `−14%` (good, green) ONLY if direction is `lower_better`.

## Adding new keys later

Every weekly run, if the skill encounters a numeric key not in `metric_vocab.json`,
it does NOT silently include it. Instead:

1. The new key goes into `manifest.new_unknown_metrics`.
2. The interview.md ⑥ section asks you to classify it (same checkbox layout).
3. The weekly report flags `本周新增 N 个待确认指标，已写入问卷`.
4. Once you submit, the key is appended to `metric_vocab.json`.

This means the vocab grows incrementally without you ever having to re-do the
full first-time labeling.

## Manual editing

You can edit `metric_vocab.json` directly when needed:

```json
{
  "schema_version": "1.0",
  "project_name": "radar_target_recognition",
  "last_updated": "2026-05-04",
  "metrics": {
    "track_acc":        {"category": "metric", "direction": "higher_better"},
    "fusion_track_acc": {"category": "metric", "direction": "higher_better",
                         "aggregate_of": "track_acc"}
  },
  "config_keys": {
    "seed":     {"category": "config"},
    "backbone": {"category": "config"}
  },
  "ignored_keys": ["_run_id"],
  "stat_aggregates": ["_mean", "_std", "_ci_95"]
}
```

Re-run the skill — changes pick up immediately.

## Common patterns from radar_target_recognition

```json
"track_acc":        higher_better
"seg_acc":          higher_better
"fusion_track_acc": higher_better, aggregate_of: track_acc
"phase1_val_acc":   higher_better, group: phase1
"track_acc_mean":   stat_aggregate of track_acc — auto-handled
"seed":             config
"backbone":         config
"n_test_tracks":    config (count, not metric)
```
