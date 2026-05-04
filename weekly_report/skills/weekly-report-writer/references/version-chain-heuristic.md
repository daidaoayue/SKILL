# Version Chain Heuristic Reference

This document describes the family/version/status extraction algorithm used
by `parse_filename.py`. It mirrors spec §7 with worked examples from the
radar_target_recognition project.

## The Algorithm

```
stem  →  search _v(\d+)([a-z]?)  (case-insensitive, FIRST match left-to-right)
                ↓
       version = "v17", remainder = "_contrastive" or "_v2" or "_fixed" or empty
                ↓
       remainder in STATUS_SUFFIXES?
         yes → status = remainder, semantic_suffix = None
         no, looks like sub-version (v2, v19)? → drop remainder
         else → keep as semantic_suffix
                ↓
       family_key = base + "_" + semantic_suffix (if any)
```

## Worked Examples (real files from radar_target_recognition)

| File | family_key | version | status | comment |
| --- | --- | --- | --- | --- |
| rcs_stacking_v26.py | rcs_stacking | v26 | None | clean version chain |
| train_v17_contrastive.py | train_contrastive | v17 | None | semantic branch |
| train_v17_fixed.py | train | v17 | fixed | bugfix iteration |
| train_v19_mstcn_contrastive.py | train_mstcn_contrastive | v19 | None | different family from train_contrastive |
| adaptive_fusion_v5b.py | adaptive_fusion | v5b | None | sub-version letter |
| inference_v20_v2.py | inference | v20 | None | _v2 dropped as sub-version |
| compare_v17_v19.py | compare | v17 | None | _v19 dropped as sub-version |
| data_loader_new.py | data_loader | None | new | bare status, no version |
| Final_inference_final.py | (anomaly) | None | None | double_status_marker — flagged |
| analyze_errors_v20v2.py | (anomaly) | None | None | suspected_version_typo — flagged |

## What is grouped vs not

- `rcs_stacking_v25.py` and `rcs_stacking_v26.py` → same family, advanced from v25 to v26.
- `train_v17_contrastive.py` and `train_v19_contrastive.py` would share family `train_contrastive`. ✅ Grouped.
- `train_v17_contrastive.py` and `train_v19_mstcn_contrastive.py` → different families (`train_contrastive` vs `train_mstcn_contrastive`).

  By design, this **may over-split** semantically-related chains. The L3 interview
  asks the user whether to merge them via `family_aliases.json` (planned).

## Debugging tips

- Run `python -c "from scripts.parse_filename import parse_filename; print(parse_filename('your_stem'))"` interactively.
- If a file is mis-classified, add it to `pytest.parametrize` in
  `tests/test_parse_filename.py` first, watch it fail, then patch the regex.

## Future: family_aliases.json

When ready, drop a file at `<project>/.weekly_report/family_aliases.json`:

```json
{
  "train_mstcn_contrastive": "train_contrastive",
  "train_supcon_v3":         "train_contrastive"
}
```

The differ reads this and rewrites family_key on the fly. No regex changes needed.
