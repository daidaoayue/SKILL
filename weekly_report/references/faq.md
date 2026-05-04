# FAQ

## 第一次跑要多久？

约 5–15 分钟，主要时间在 metric_vocab 标注（30 个 key × 30 秒）。
Scanner 本身 < 1 分钟。

## 我每周不固定时间汇报，怎么办？

Skill 每次跑都会问 `active_window_days`，默认 7 天但可以输入 1-30 天的任意值。
你可以一周跑两次（输入 3 天），也可以两周跑一次（输入 14 天）。

## 工程目录里有几十 GB 的训练数据，会不会卡？

不会。Scanner 对 `*.mat / *.npy / *.pt / *.pth / *.ckpt` 默认 metadata-only，
不读内容、不算 sha1。71315 个数据文件实测扫描 < 30 秒。

## 我改了 `metric_vocab.json` 里的 direction，要重跑 init 吗？

不用。下次 `/weekly-report run` 自动生效。

## 周报不准怎么办？

按以下顺序排查：
1. 看 `manifest.json` 的 `anomalies` 字段——命名异常会被 flag。
2. 看 `diff.json` 的 `version_chains_advanced`——版本链是否识别正确。
3. 看 `metric_vocab.json`——是否有指标被错分到 config。
4. 看 `interview.md`——是否漏填了关键问题。

## 我的工程不是这个"PhD 雷达项目"格式，能用吗？

可以。`project.toml` 里的 `buckets.*.roots` 全部由你自己配。
init 模式会基于子目录名自动猜，你审一遍即可。
默认覆盖了：`Forecasting/`, `output/`, `paper_writing/`, `research-wiki/` 等常见命名。

## 我有多个项目（雷达 + 论文 + 别的），会不会串？

每个项目独立 `.weekly_report/`，metric_vocab、history、family_aliases 全部
per-project。汇总文件在 `D:\code\reports\<year>\<month>\` 按 short_name 区分。

## 漏写了一周怎么办？

下次跑时，skill 自动拿最近一份可用 manifest 做对比。中间漏掉的周不会被填补，
但会在 anomalies 里记录"跨周缺失检测"。

## 命名异常（如 `Final_inference_final.py`）怎么修？

skill 不会自动改文件名（红线：禁止改用户工程）。你手动改文件名后，
下次扫描自动正常归类。或者在 `family_aliases.json` 里加一条别名映射：
```json
{ "Final_inference_final": "inference" }
```

## Skill 会写到我工程目录吗？

只写到 `<project>/.weekly_report/` 与 `D:\code\reports\`。其他位置的写操作
会被 `path_guard.py` 拦截并报错。这是硬红线。

## 怎么把 skill 给师弟师妹？

1. 把 `D:\code\github_skill\weekly_report\` 整个目录拷给他。
2. 让他放到 `~/.claude/plugins/` 下。
3. 让他打开 README.md 跟着 quickstart 跑一遍。
4. 第一次跑时他自己的 `metric_vocab.json` 会基于他的项目重新生成，跟你的不串。

## skill 报"路径白名单越界"怎么办？

说明 skill 内部逻辑试图写到工程目录。这是 BUG，请贴堆栈信息回报。
临时解决：手动 fork skill，放宽 `path_guard.is_write_allowed` 中的判断（不推荐）。

## metric_vocab.json 弄丢了会怎样？

下次 init 重做一次（5–10 分钟）。或者手动复制一份 backup 文件。
这个文件不大（几 KB），建议 gitignore 之外另作备份。
