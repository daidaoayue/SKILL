# Weekly-Report-Writer Skill · 设计规格 v2

**日期**：2026-05-04
**作者**：levanduong0523@gmail.com（PhD candidate）+ Claude (brainstorming)
**目标受众**：作者本人 + 后续要继承使用的师弟师妹
**状态**：Design approved（pending spec review）→ 进入 writing-plans

---

## 0. 一句话定位

把博士生周报从"每周回忆 + 手写"升级为 **"工程目录 diff + 半自动归并 + L3 质询补语义 + 模板化输出"** 的闭环工具，覆盖代码 / 实验数据 / 论文 / 阅读四类工作。

---

## 1. 目标与非目标

### 目标
- 通过对工程目录的 **结构化扫描** 还原"本周到底改了什么"。
- 通过 **diff 上周 manifest** 自动识别新增 / 修改 / 删除的工程产物。
- 通过 **多级启发式版本链识别** 把零碎文件改动归并成"实验线推进"。
- 通过 **L3 质询问卷** 补齐机器无法判断的语义信息（实验结论、论文章节、风险）。
- 输出 **结构清晰、PhD 汇报友好** 的周报 markdown。
- 支持 **多项目** 切换，per-project 配置不耦合。
- 第一次跑产出 **baseline 项目总报告**；后续每周产出 **增量周报**。
- 完整 README 让师弟师妹零门槛复用。

### 非目标 / 红线（强制）

- **🚫 严禁修改用户工程代码**（最高级别红线，仅只读访问；任何写操作只发生在 `<project>/.weekly_report/` 与 `D:\code\reports\` 内部）
- 不做 git history 解析（用户工程不是 git 仓库）
- 不替代当面汇报（只是材料）
- 不抓外部系统（邮件 / Slack / Issue）
- 不读训练 ckpt 内容（只读文件名 + mtime）
- 不做 AST 级代码 diff（行级 diff + LLM 摘要够用）

### 红线工程化保障

- Scanner / Differ / Writer 全流程使用只读文件 API（Python `pathlib.Path` + `open(..., 'r')`）
- 任何 `open(..., 'w')` / `'wb'` 调用必须经过白名单路径检查（白名单：`<project>/.weekly_report/**` 和 `D:\code\reports\**`）
- 单元测试覆盖"写入路径越界"用例

---

## 2. 顶层架构

```
                    ┌──────────────────────────────────┐
                    │ project.toml （per-project 配置） │
                    └──────────────────────────────────┘
                                    │
                                    ▼
┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌──────────┐
│ Scanner  │ → │  Differ  │ → │  Interview   │ → │  Writer  │
│ 扫工程   │   │ 对比上周 │   │ L3 问卷生成  │   │ 出周报md │
└──────────┘   └──────────┘   └──────────────┘   └──────────┘
     ↓               ↓               ↑                ↓
  manifest.json   diff.json      用户填问卷      report.md
                                                   + 落档
```

四层流水线 = **bundle 脚本（确定性）+ LLM prompt（语义）** 混合：

| 层 | 实现 | 理由 |
|---|---|---|
| Scanner | Python 脚本 | 71,315 数据文件，纯 LLM walk 不可行 |
| Differ | Python 脚本 | 跨周对比是确定性集合运算 |
| Interview | LLM + 模板 | 需要 LLM 判断哪些 diff 需要追问 |
| Writer | LLM + 模板 | 自然语言归纳压缩 |

---

## 3. 目录布局（最终）

### 工程内部（按年/月分层，因项目以年为周期）

```
<project_root>/.weekly_report/
├── project.toml                       # per-project 配置（首跑生成）
├── metric_vocab.json                  # 项目级指标词汇表（增量学习）
├── ignore.toml                        # 项目级 ignore 规则（可选）
├── family_aliases.json                # 版本链别名表（人工合并近邻链，可选）
├── latest.txt                         # 指向最新周目录的指针
├── 2026/                              # 年
│   ├── 03/                            # 月
│   │   ├── 2026-03-02_03-08_W10/
│   │   └── 2026-03-09_03-15_W11/
│   ├── 04/...
│   └── 05/
│       └── 2026-05-04_05-10_W18/
│           ├── report.md              # 给老师的周报
│           ├── manifest.json          # 本周快照
│           ├── diff.json              # 本周 vs 上周 diff
│           ├── interview.md           # L3 质询问卷（带用户填写答案）
│           ├── images/                # 周报采图缓存（从工程拷贝过来的副本）
│           └── raw_scan.json          # 原始扫描数据（debug；可清）
├── 2025/...                           # 旧年份归档
└── baseline/                          # 首次 baseline 报告固定位置
    └── 2026-05-04_baseline.md
```

### 汇总区（跨项目跨年）

```
D:\code\reports\
├── index.md                           # 跨工程汇总索引（自动维护）
├── 2026/                              # 年
│   ├── 03/                            # 月
│   │   ├── 2026-03-02_03-08_W10_radar.md
│   │   └── 2026-03-02_03-08_W10_paperwriting.md
│   └── 05/
│       └── 2026-05-04_05-10_W18_radar.md
└── 2025/...
```

**`index.md` 内容**（跨工程跨年的导航地图）：

- 按"年-周"倒序列出所有周报，每条 1 行
- 显示：日期区间 / 周号 / 工程短名 / 主要 highlight 一句话 / 文件链接
- 自动维护，每次跑 skill 时增量更新一行；从不删

```markdown
# 周报汇总索引

## 2026
| 周号 | 日期 | 工程 | 本周抓手 | 链接 |
|---|---|---|---|---|
| W18 | 2026-05-04~05-10 | radar | rcs_stacking v25→v26, +1.4% | [→](2026/05/...) |
| W17 | 2026-04-27~05-03 | radar | PhaseAmp V5b 蒙特卡洛复核 | [→](2026/04/...) |
| W17 | 2026-04-27~05-03 | paperwriting | 第三章实验部分初稿 | [→](2026/04/...) |
```

汇总文件命名规则：`<起始日>_<结束日>_W<周号>_<project_short_name>.md`，下划线为分隔符。

---

## 4. project.toml Schema（per-project 配置）

```toml
[project]
name = "radar_target_recognition"          # 与目录同名，机读用
display_name = "多维特征融合的低空雷达目标识别"  # 周报标题用
short_name = "radar"                       # 汇总文件名用
domain = "雷达目标识别 / 多模态融合"
advisor = ""                               # 选填
phd_year = 2                               # 选填，影响第一份 baseline 中的"路线图"模板

[buckets.code]
roots = ["Forecasting", "hardware", "Preprocess", "feature_fusion_forecasting"]
ignore = ["__pycache__", "dist", "build_tmp", ".pytest_cache"]
include_extensions = [".py", ".cpp", ".h", ".cu"]
content_diff_size_kb = 200                 # 大于此则只 metadata diff
sha1_for_content_diff = true

[buckets.experiment_data]
roots = ["*/output", "*/results"]
ignore = ["raw_data/**", "dataset/**", "*.mat", "*.npy", "*.h5"]
include_extensions = [".json", ".csv", ".tsv"]
extract_metrics = true                     # 从 JSON 抽 metric

[buckets.paper]
roots = ["paper_writing"]
ignore = [".aux", ".log", ".out", ".synctex.gz", "*.bak"]
include_extensions = [".tex", ".md", ".docx"]
section_diff = true                        # 抽取 H1/H2/H3 章节级 diff

[buckets.reading]
roots = ["research-wiki", "docs"]
include_extensions = [".md", ".pdf"]

[buckets.theory]
# 理论 / 公式推导专区（独立 bucket）
roots = ["theory", "derivations", "notes_math", "**/*math*", "**/*derivation*"]
include_extensions = [".md", ".tex", ".ipynb"]
detect_math_in_paper = true                # 同时扫 paper bucket 里的 .md/.tex 中含 \\(...\\) / $$...$$ 的段落
section_diff = true

[buckets.figures]
# 图片采集（写进周报用）
roots = ["**/figures", "**/figs", "**/ppt_figures", "**/results/*.png"]
include_extensions = [".png", ".jpg", ".jpeg", ".svg", ".pdf"]
sample_strategy = "newest_3"               # 采图策略: newest_3 / by_family / all
max_per_report = 5                         # 周报最多嵌入 5 张图
max_size_mb = 5                            # 单张图大于此跳过

[checkpoint_signal]
enabled = true
roots = ["*/checkpoint", "*/weights_*"]
filename_patterns = [
  '_acc_(?P<acc>[\d.]+)',
  '_epoch_?(?P<epoch>\d+)',
  '_seed_?(?P<seed>\d+)',
  '_loss_(?P<loss>[\d.]+)'
]
ignore_content = true                      # 永远不读权重内容
# active_window_days 不再写死在配置里，每次跑 skill 时运行时询问
# 默认 7 天但允许 1-30 范围内动态指定（详见第 12 节运行时交互）

[metrics]
hint_tokens_extra = []                     # 项目特殊指标 hint，叠加全局
config_keys_extra = []                     # 项目特殊配置字段
multi_seed_aggregate = true
ci_field = "ci_95"                         # 置信区间字段名

[scanner]
exclude_globs_global = [
  "__pycache__/**", "*.pyc", ".pytest_cache/**",
  "dist/**", "build/**", "build_tmp/**",
  ".idea/**", ".vscode/**",
  "*~", "*_tmp.*", "*_temp.*",
  ".weekly_report/**"                       # 自循环防护
]
follow_symlinks = false
include_hidden = false
metadata_only_size_mb = 10                  # 大于此跳 sha1
```

---

## 5. Manifest Schema（机器对比用）

```json
{
  "schema_version": "2.0",
  "week_id": "2026-W18",
  "date_range": ["2026-05-04", "2026-05-10"],
  "scanned_at": "2026-05-04T...",
  "project_root": "D:/code/radar_target_recognition",
  "project_name": "radar_target_recognition",
  "scanner_version": "1.0",

  "buckets": {
    "code": {
      "files": [
        {"path": "Forecasting/rcs_stacking_v26.py",
         "mtime": 1735000000, "size": 12340, "sha1": "abc...",
         "family_key": "rcs_stacking", "version": "v26", "status": null}
      ],
      "version_chains": {
        "rcs_stacking": {"versions": ["v25","v26"], "latest_path": "..."},
        "monte_carlo_train": {"variants": ["phase","rcs","rd","v17","v19"]}
      },
      "loc_total": 18234,
      "file_count": 331
    },
    "experiment_data": {
      "files": [...],
      "metric_aggregates": {
        "rcs_stacking_v26": {
          "track_acc": {"mean": 0.942, "std": 0.008, "n_seeds": 8},
          "seg_acc":   {"mean": 0.881, "std": 0.012, "n_seeds": 8}
        }
      },
      "json_count": 2221
    },
    "paper": {
      "files": [...],
      "section_changes": [
        {"file": "paper_writing/.../report.md",
         "sections_modified": ["3.2 方法"], "sections_added": [], "sections_deleted": []}
      ]
    },
    "reading": {
      "files": [...],
      "new_papers_added": [...]
    },
    "theory": {
      "files": [...],
      "math_blocks": [
        {"file":"theory/derivation_v3.md","section":"2.1 PhaseAmp 三通道",
         "formulas_added":["\\(|mean(exp(j\\phi))|\\)","\\(\\sum abs(RD)\\)"],
         "formulas_modified":[],
         "summary_hint":"新推导：相位相干性度量"}
      ],
      "section_changes":[...]
    },
    "figures": {
      "candidates": [
        {"path":"Forecasting/ppt_figures/mc_robustness.png",
         "mtime":..., "size":..., "family_link":"monte_carlo",
         "embed_priority": 0.92}
      ],
      "selected_for_report": []   // Writer 阶段填
    }
  },

  "checkpoint_signal": {
    "active_dirs": ["Forecasting/checkpoint/rcs_stacking_v26/"],
    "signals": [
      {"path":"Forecasting/checkpoint/best_acc_0.942_epoch50.pt",
       "mtime":..., "extracted":{"acc":0.942,"epoch":50}}
    ],
    "weekly_best": {
      "rcs_stacking_v26": {"best_acc":0.942, "epoch":50, "ts":"..."}
    }
  },

  "anomalies": [
    "Final_inference_final.py: 双 final 后缀，命名异常",
    "analyze_errors_v20v2.py: 疑似 _v20_v2 typo"
  ],

  "new_unknown_metrics": []   # 新发现待人工确认的 numeric key
}
```

---

## 6. Scanner 规则（确定性）

### 文件级处理决策树
```
对每个文件 f:
  1) 是否命中 exclude_globs_global / 项目 ignore？ → skip
  2) 后缀是 *_tmp.* / *_temp.*？                  → skip（用户已确认废除）
  3) 是否软链接？                                 → skip
  4) 是否在 .weekly_report/ 下？                  → skip（自循环防护）
  5) f.size > metadata_only_size_mb (10MB)？      → metadata-only（不算 sha1）
  6) f 在 buckets.* roots 命中？                  → 入对应 bucket
  7) 都没命中？                                   → 入 "uncategorized" bucket（用户审）
```

### 各 bucket 特殊处理

| bucket | 内容 | 策略 |
|---|---|---|
| code | path + mtime + size + sha1 + family_key + version + status | 全量索引 |
| experiment_data | path + mtime + size + 抽取 metric | 不算 sha1（json 内容多，文件名 + mtime + extracted_metrics 更稳） |
| paper | path + mtime + size + sha1 + 章节抽取 | 章节通过 H1/H2/H3 抽取 |
| reading | path + mtime + size + sha1（小文件） | PDF 不读内容，只 metadata |
| theory | path + mtime + size + sha1 + math 块抽取 | 抽取 `\(...\)` `$$...$$` `\begin{equation}` 块 |
| figures | path + mtime + size + 缩略图签名（pHash） | 不读完整内容；用于配图采样 |
| checkpoint_signal | path + mtime + 文件名 regex 抽取数字字段 | 永远不读内容 |

### 并发模型（已拍板：ThreadPool walking）

- 不同 bucket roots 之间 **彼此关联但独立扫描**（一个 root 的扫描不依赖另一个 root 的中间结果）
- 用 `concurrent.futures.ThreadPoolExecutor`，max_workers = `min(8, len(roots) * 2)`
- I/O 密集型（os.stat + 小文件读 sha1），ThreadPool 比 ProcessPool 更合适，无 GIL 序列化代价
- 每个线程负责一个 root 的递归 walk，结果汇总到主线程的 manifest builder
- **单元测试覆盖**：模拟两个 root 同时被扫，确保结果合并无重复无丢失

### 性能预算

- **首次扫描**（无 sha1 cache，ThreadPool 8 worker）：71,315 数据文件 metadata-only + 553 内容文件 sha1 → < 30 秒（并发后比串行 < 60s 提升一档）
- **增量扫描**（有 sha1 cache）：复用 mtime 未变的 sha1 → < 15 秒
- mtime 未变 → 直接跳过 sha1 计算（即使 size 变化也只在 size 不同才重算，避免误命中）

---

## 7. Differ 规则

### 文件级 diff（集合运算）
```
本周 manifest.files - 上周 manifest.files = added
上周 manifest.files - 本周 manifest.files = deleted
两者交集中 sha1 变化       = modified_content
两者交集中 mtime 变化但 sha1 不变 = touched_only（忽略）
```

### 版本链识别启发式（替代单条 regex）
```python
def parse_filename(stem: str) -> tuple[str, str|None, str|None]:
    """
    Returns: (family_key, version_token, status_suffix)
    """
    STATUS = {'final','fixed','correct','new','legacy','old','bak'}
    # _v\d+[a-z]? + 可选语义后缀
    m = re.search(r'_v(\d+)([a-z])?(?:_(.+?))?$', stem)
    version_token = None
    semantic_suffix = None
    status = None
    if m:
        version_token = f"v{m.group(1)}{m.group(2) or ''}"
        semantic_suffix = m.group(3)
        if semantic_suffix in STATUS:
            status = semantic_suffix
            semantic_suffix = None
    base = stem[:m.start()] if m else stem
    family_key = f"{base}_{semantic_suffix}" if semantic_suffix else base
    return family_key, version_token, status
```

**示例：**
| 文件 | family_key | version | status |
|---|---|---|---|
| rcs_stacking_v26.py | rcs_stacking | v26 | None |
| rcs_fusion_v25.py | rcs_fusion | v25 | None |
| train_v17_contrastive.py | train_contrastive | v17 | None |
| train_v17_fixed.py | train | v17 | fixed |
| adaptive_fusion_v5b.py | adaptive_fusion | v5b | None |
| Final_inference_final.py | （anomaly） | None | None+anomaly |
| data_loader_new.py | data_loader | None | new |
| compare_v17_v19.py | compare（special） | None | comparison_script |

> **family_key 已知粒度风险**：`train_v17_contrastive.py`（family=`train_contrastive`）和 `train_v19_mstcn_contrastive.py`（family=`train_mstcn_contrastive`）会被识别为两条独立链，但它们语义上可能是同一条 contrastive 实验线的演化。这种"语义近邻但 family 不同"的情况由 L3 质询兜底——interview 会列出 family 相似的文件让用户确认是否合并。**实现 plan 阶段需考虑：是否引入 family_key 别名表（`family_aliases.json`）支持人工合并**。

### 三档 diff 处理

- **L1 自动归并**：同 family_key 跨周对比，"链上最新版"变化 → "实验链 X 推进 v25→v26"
- **L2 自动摘要**：非版本化 modified 文件 → unified diff 前 200 行喂 LLM 出"修改摘要"
- **L3 必须质询**：详见第 8 节

### diff.json schema
```json
{
  "this_week": "2026-W18",
  "last_week": "2026-W17",
  "code": {
    "version_chains_advanced": [
      {"family":"rcs_stacking","from":"v25","to":"v26","diff_summary":"..."}
    ],
    "non_versioned_modified": [...],
    "added_loose_files": [...],
    "deleted_files": [...],
    "anomalies": [...]
  },
  "experiment_data": {
    "metric_changes": [
      {"family":"rcs_stacking_v26","metric":"track_acc",
       "last_week":0.928,"this_week":0.942,"delta":+0.014,"n_seeds":8}
    ],
    "new_result_files": [...],
    "new_unknown_metrics": [...]      // 谨慎处理
  },
  "paper": {
    "section_changes": [...],
    "new_files": [...]
  },
  "reading": {...},
  "theory": {
    "math_blocks_added": [
      {"file":"theory/derivation_v3.md","section":"2.1",
       "formula":"|mean(exp(j\\phi))|","summary_hint":"相位相干性度量"}
    ],
    "math_blocks_modified": [...],
    "math_blocks_deleted": [...]
  },
  "figures": {
    "selected_for_report": [
      {"path":"Forecasting/ppt_figures/mc_robustness.png",
       "caption_draft":"蒙特卡洛 10 seeds 鲁棒性验证",
       "linked_section":"实验工作"}
    ]
  },
  "checkpoint_signal": {
    "newly_active_chains": [...],
    "best_metric_updates": [...]
  }
}
```

---

## 8. Metric 抽取（per-project + 增量学习）

### 三层叠加规则
- **L1 全局默认 hint**：`acc, accuracy, loss, f1, auc, error, err, iou, map, recall, precision, mae, rmse, psnr, ssim, bleu, rouge, perplexity, rate, score`
- **L2 项目级 hint**（`project.toml.metrics.hint_tokens_extra`）：例 radar 项目的 `track, seg, fusion`
- **L3 metric_vocab.json**：人工标注 + 增量

### metric_vocab.json schema
```json
{
  "schema_version": "1.0",
  "project_name": "radar_target_recognition",
  "last_updated": "2026-05-04",
  "metrics": {
    "track_acc": {"category":"metric","direction":"higher_better","unit":"ratio"},
    "seg_acc":   {"category":"metric","direction":"higher_better","unit":"ratio"},
    "phase1_val_acc": {"category":"metric","direction":"higher_better","group":"phase1"},
    "fusion_track_acc": {"category":"metric","direction":"higher_better","aggregate_of":"track_acc"}
  },
  "config_keys": {
    "seed": {"category":"config"},
    "backbone": {"category":"config"},
    "n_params": {"category":"config","unit":"count"}
  },
  "stat_aggregates": ["_mean","_std","_ci","_ci_95","_min","_max","_median"],
  "ignored_keys": []                  # 用户标过"非指标"的字段
}
```

### 新指标谨慎处理流（核心）
```
manifest 生成时遇到 numeric key K：
  if K in metric_vocab.metrics: 计入指标对比
  elif K in metric_vocab.config_keys: 计入实验配置
  elif K in metric_vocab.ignored_keys: 跳过
  else:                                                # 全新 key
    1. 写入 manifest.new_unknown_metrics
    2. 在 interview.md "## ⑥ 本周发现新指标" 列出 K
       附：出现位置、上下文 JSON 片段、自动猜测分类
    3. 不在本周指标对比表中使用（避免污染）
    4. 周报里 flag "本周新增 N 个待确认指标，已写入问卷"
    5. 用户在 interview 里勾选 → metric_vocab.json 更新
```

### 多 seed 聚合
同 family_key 下多 JSON：按 `seed` / `seeds` 字段分组，对每个 metric 出 `mean ± std (n=N)`。

---

## 9. Interview（L3 质询）

### 触发条件 → 进 interview
- 实验链版本号变化（v25→v26）：必问"核心改动是什么、解决了什么"
- 实验指标突变（|Δ|/baseline > 5%）：必问"提升来自哪个改动"
- paper 章节级变更：必问"推进到哪一阶段"
- 新增高占比草稿（同名前缀新文件 ≥ 3 个）：必问
- 新指标出现：必问归类
- 风险提示（用户工程内 .md 含 TODO/FIXME 数 ↑）：必问

### interview.md 结构
```markdown
# 周报质询问卷 · 2026-W18 · radar_target_recognition

## 元数据（自动生成，不要改）
- generated_at: 2026-05-04T...
- diff_signature: <hash>

## ① 实验链进展（必填）
### rcs_stacking 链：v25 → v26
**自动 diff 摘要**：[摘要]
**关键 metric 变化**：track_acc 0.928 → 0.942 (+1.4%)，n_seeds=8
**请填**：
- v26 相对 v25 的核心改动：______
- 改动动机 / 解决的问题：______
- 是否达到预期：______

## ② 实验指标突变（必填）
### track_acc 在 rcs_stacking 链突变 +1.4%
**请填**：
- 提升来自：[ ] 模型结构 [ ] loss 设计 [ ] 数据增强 [ ] 超参 [ ] 其他：____
- 是否本周计划目标：______

## ③ 论文推进（必填）
### paper_writing/.../report.md
**章节变动**：3.2 方法（修改）
**请填**：
- 推进到：[ ] 初稿完成 [ ] 评审中 [ ] 待确认 [ ] 其他：____
- 预计完成时间：______

## ④ 阅读 / 思考类（选填）
（系统不一定能从 mtime 看到，请你简述本周读了什么、有何启发）
**请填**：______

## ⑤ 给老师的 ask（选填）
**请填**：
- 需要的实验器材 / 数据：______
- 需要老师确认的方向：______
- 需要的计算资源：______

## ⑥ 本周发现新指标（必处理）
- `track_mean_per_seed`（在 rcs_stacking_v26/result.json 出现）
  自动猜测：metric / aggregate of track_acc
  - [ ] 确认是指标，方向 higher_better
  - [ ] 不是指标，是配置
  - [ ] 忽略

## ⑦ 理论 / 公式推导（必填如有变化）
### theory/derivation_v3.md 第 2.1 节
**自动检测的新公式块**：
- `|mean(exp(jφ))|` —— 相位相干性度量
- `sum(abs(RD), 1)` —— 距离维幅度求和
**请填**：
- 这个公式背后的物理含义 / 数学动机：______
- 是否打算写进论文？哪一节：______
- 是否需要进一步推导 / 验证：______

## ⑧ 配图建议（半自动）
skill 已根据 mtime + family link 选出候选图：
- [x] Forecasting/ppt_figures/mc_robustness.png（候选标题：蒙特卡洛 10 seeds 鲁棒性验证）
- [ ] Forecasting/ppt_figures/phase_dropout_curve.png
- [x] Forecasting/results/track_acc_box.svg
**请勾选要嵌入周报的图**（默认勾选优先级最高的 3 张），如标题不准请改：______

## ⑨ 风险与阻塞（选填）
**请填**：______
```

### Interview.md 解析容错（已拍板：H1 强 / H2 弱）

- **H1（① ② ③ ... ⑨）是机器解析锚点**：每个 H1 序号严格匹配 `^## [①-⑨]`，序号变 → 报错；用户不要改。
- **H2（### 子节点）允许用户改**：解析器按 H1 块切片，块内提取所有 H2 + 内容；H2 标题文本仅作为人类阅读用，不做精确匹配。
- **填写区域以"**请填**：" 行后的内容为准**：解析器抽取 `**请填**：` 之后到下一个加粗标签或 H1/H2 边界之前的所有文本。
- **checkbox 解析**：`- [x]` / `- [X]` 都识别为 true，`- [ ]` 为 false。
- **冗余兜底**：若 H1 锚点缺失，降级到 LLM 直接读 markdown 全文做语义提取（不阻塞主流程，但 flag warning）。

### 用户填完后
skill 解析 markdown 输出 `interview_parsed.json`，喂给 writer 阶段的 prompt。

---

## 10. Writer 输出（PhD 周报模板）

### 增量周报模板（assets/weekly-report-template.md）

> 参考 `D:\code\github_skill\2026春-3月第1周报-李越.docx` 的实际格式定制：含问候语、开场段、正文（按"主要工作"分 H1）、本周总结、下周任务、结束祝福、签名、日期区间。

```markdown
**{semester}{month}{week_ordinal}周报**

{advisor_title}好：

向您汇报本周的学习情况，本周主要完成了 {N} 项工作：{(1) 工作 A; (2) 工作 B; (3) 工作 C；...}（开场段由 LLM 基于本周 highlights 生成，不超过 3 句）

# {主要工作 1：从 family/实验链 + interview ① 生成标题}

## 实验背景与目的
{从 paper bucket / theory bucket / interview ① 提炼，说清楚为什么做、想验证什么}

## 自动化实验框架 / 方法
{L1 自动归并 + L2 摘要 + checkpoint_signal 整合，说明本周做了什么改动}

## 实验结果
{多 seed 聚合表 + checkpoint_signal best_acc + diff 对比表}

| 模型 | 均值 | 标准差 | 最小值 | 最大值 | 判定 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

{若 figures bucket 选中本节配图，按下方格式嵌入：}
![{caption}]({images/xxx.png})

## 关键发现与分析
{interview ② 的"指标提升来自哪个改动"答案 + LLM 归纳出"为什么"}

## 理论 / 公式（如本周有理论变化才出）
{从 theory bucket math_blocks_added + interview ⑦ 拼出}
$$|mean(exp(j\\phi))|$$ —— 相位相干性度量，用于 ...

# {主要工作 2}
{同上模板}

# {主要工作 3}
{同上模板}

# 本周总结

1. {结论 1：从主要工作 1 提炼}
2. {结论 2：从主要工作 2 提炼}
3. {结论 3：从理论/公式变化 提炼}
4. {若有图工具/可视化产出，单列一条}

# 下周任务安排

1. {可验证的任务 1}
2. {可验证的任务 2}
3. {可验证的任务 3}

# 给老师的 ask（仅在 interview ⑤ 有内容时出此节）
- {资源/数据/方向需求}

祝您工作顺利，身体健康！

{student_name}

{date_range_slash}    <!-- 例：2026/5/4-2026/5/10，跟样例 .docx 一致 -->

---
*本周扫描指纹：{N} 文件 / {M} 实验链 / {K} 指标更新 ｜ 待确认新指标：{count} ｜ 命名异常 flag：{count}*
*Auto-generated by weekly-report-writer v1.0 · diff vs 2026-W17 · {scanned_at}*
```

### 模板字段映射表

| 模板槽位 | 数据来源 |
|---|---|
| `{semester}` | project.toml.semester / 自动判断（春/秋季 + 学期月份） |
| `{advisor_title}` | project.toml.advisor.title （默认"老师"，可为"陈老师"等） |
| `{N} 项工作` | diff.json 中 family_chains_advanced + paper.section_changes 数量 |
| `{主要工作 X 标题}` | LLM 综合 family_key + interview ① 起标题 |
| 实验结果表格 | manifest.metric_aggregates + checkpoint_signal.weekly_best |
| `![]()` 配图 | interview ⑧ 勾选的 figures，拷贝到 `<week>/images/` 后引用 |
| 公式块 | theory.math_blocks_added + interview ⑦ |
| `{date_range_slash}` | week 目录的日期 + 用 `/` 替换 `_`（与样例 docx 格式一致） |

### Baseline 总报告模板（assets/baseline-report-template.md）

比增量详细 3-5 倍，含八节：

1. **项目背景与目标**（带问候语 + 总览开场段）
2. **整体架构概览**（含核心架构图，如 figures bucket 命中"architecture/overview"类）
3. **已完成的核心实验链**（每条链一个 H1，含历史方法演进 V4→V5a→V5b 这种叙事）
4. **当前指标基线**（全工程指标全景表 + 配图 box plot/CI 图）
5. **理论与方法总结**（含核心公式块，从 theory + paper bucket 抽）
6. **推进中的工作**
7. **已识别的风险与未解问题**
8. **未来 3 个月路线图**（重点节，详见第 12.2 路线图 prompt 设计）
9. **给老师的统一汇报点**
10. 结束祝福 + 签名 + 日期

---

## 11. 第一周 baseline 模式

### 触发
`<project>/.weekly_report/` 不存在，或全部历史 manifest 损坏。

### 流程
```
1. 引导用户走 /weekly-report init <project_path>
   - 自动检测 bucket roots 候选（基于子目录文件类型分布）
   - 让用户复核生成 project.toml
2. 全工程 scan，metric 走 hint 自动归类
   - new_unknown_metrics 全部进入首次标注问卷
3. 用户在 metric_vocab.init.md 里一次性标完
4. 生成 baseline 总报告（详细十节式）
5. 落档为 baseline/<date>_baseline.md，作为后续 diff 的起点
```

### baseline 周报与增量周报的区别

| 维度 | baseline | incremental |
|---|---|---|
| 标题 | 项目工作总报告 | 周报 |
| 长度 | 详细，覆盖项目全景 | 紧凑，只讲增量 |
| 路线图节 | 有（重点） | 无 |
| 指标节 | 全工程基线 | 本周 vs 上周 diff |
| 配图 | 多（架构图 / 指标 box plot） | 少（每节最多 1-2 张） |
| 理论公式 | 系统梳理 | 仅 diff |
| metric_vocab | 必须标注 | 增量更新 |
| interview | 长（含路线图） | 短 |

### 11.1 路线图章节的 LLM Prompt（认真打磨，因为可能被写进论文）

借鉴 paper-plan / research-refine / grant-proposal 这三个现成 skill 的风格，路线图 prompt 设计要求：

**结构上四象限（借 grant-proposal 的 4-quad 结构）：**

1. **科学问题** —— 用一句话刻画"这个工程要解决的最高层科学问题"，用 narrowing 公式：「在 X 场景下，由于 Y 约束，导致 Z 问题，本课题旨在从 W 角度提供解法」
2. **方法路线** —— 由近及远列 3 个 milestone，每个 milestone 含：研究子问题、待验证的假设、可衡量的成功标志、风险与备选方案
3. **预期产出** —— 论文（顶会 / 顶刊目标 + 投稿时间）、专利、demo / 数据集开源、答辩与中期/终期节点
4. **资源与协作** —— 计算资源、需要导师协调的事项、可能的合作组

**写作要求**：

- 每条不超过 80 字，便于直接抠到论文 Introduction / 答辩 PPT
- 引用 theory bucket 的核心公式，建立"我已经做的"和"我要做的"的连续性
- 用过去时讲已完成 / 现在时讲推进中 / 将来时讲下一步，不混
- 输出后要让 LLM 自审一次："这段如果直接贴到导师面前，会不会觉得空"

**Prompt 实现**（写进 `references/baseline-roadmap-prompt.md`）：
```
你是一个 PhD 学生的研究路线图起草助手。基于以下 manifest + metric_aggregates +
theory.math_blocks + paper.section_changes，按四象限结构起草未来 3 个月的路线图。

输入：{...}
约束：
- 每个 milestone 必须有可验证的成功标志（数字、文件、章节）
- 引用 theory bucket 中已成立的公式作为"已有基础"
- 风险栏需写明 Plan B（而非笼统"如果不行就重来"）
- 投稿时间点必须落到具体月份

输出格式：
## 8.1 科学问题
（一句话）

## 8.2 方法路线
### Milestone 1（截至 YYYY-MM）
- 子问题 / 假设 / 成功标志 / 风险与 Plan B
### Milestone 2 ...
### Milestone 3 ...

## 8.3 预期产出
- 论文：目标 venue + 投稿日期
- 专利 / 开源 / Demo
- 节点：中期 / 答辩

## 8.4 资源与协作
- 计算 / 导师 / 外部合作
```

skill 在 baseline 模式下：① 自动跑 prompt 出 v0 草稿；② 列入 baseline interview 让用户改；③ 改完后写进 baseline 报告第 8 节。

---

## 12. Skill 文件结构

```
weekly_report/
├── SKILL.md                              # 主流程，<300 行
├── README.md                             # 给师弟师妹的使用说明（必备）
├── scripts/
│   ├── scan_project.py                   # bucket 扫描（ThreadPool）→ manifest.json
│   ├── compute_diff.py                   # manifest 跨周 diff → diff.json
│   ├── extract_metrics.py                # JSON 抽 metric + 多 seed 聚合
│   ├── parse_filename.py                 # 版本链启发式
│   ├── figure_picker.py                  # 配图候选选择 + pHash 去重
│   ├── theory_extractor.py               # 抽取 .md/.tex 中的数学公式块
│   ├── interview_generator.py            # 生成 interview.md
│   ├── parse_interview.py                # 解析填好的 interview.md
│   ├── init_project.py                   # 首跑自动生成 project.toml
│   ├── update_index.py                   # 维护 D:\code\reports\index.md
│   ├── path_guard.py                     # 红线：路径白名单写检查
│   └── README.md                         # 脚本使用说明
├── references/
│   ├── input-guide.md                    # 保留，处理零散输入（精简）
│   ├── writing-rules.md                  # 保留，写作风格
│   ├── version-chain-heuristic.md        # 新增：family_key 算法详解
│   ├── metric-vocab-guide.md             # 新增：metric_vocab 是什么 + 标注步骤
│   ├── project-toml-reference.md         # 新增：每个字段的含义与默认值
│   ├── baseline-roadmap-prompt.md        # 新增：baseline 路线图章节的 LLM prompt
│   ├── theory-extraction-rules.md        # 新增：math 块识别规则
│   ├── greeting-templates.md             # 新增：问候 / 结束语模板，按导师/学校/季节分类
│   └── faq.md                            # 新增：常见问题
├── assets/
│   ├── weekly-report-template.md         # 增量周报模板（含问候 + 结束）
│   ├── baseline-report-template.md       # 首周总报告模板（十节式）
│   ├── interview-template.md             # 问卷骨架（含 ⑦ 理论、⑧ 配图）
│   ├── default-project.toml              # 默认配置（init 时复制）
│   └── default-ignore.toml               # 默认 ignore 规则
└── docs/
    └── superpowers/specs/
        └── 2026-05-04-weekly-report-writer-design.md   # 本文件
```

### SKILL.md 主流程伪代码

```
ENTRY 模式：
  /weekly-report init <project_path>     → 走 init 流程
  /weekly-report run [--project <path>]  → 走主流程
  /weekly-report rebase --week <id>      → 重建某周（可选）

主流程：
  1. 探测 <project>/.weekly_report/，决定 baseline/incremental
  2. **运行时询问（每次必问）**：
     - 「本次汇报覆盖的时间窗口是？」
       默认：上次跑到现在 / 7 天
       可选：自定义 N 天（1-30）/ 指定起止日期
     - 此值即 active_window_days，用于 checkpoint_signal、figures、新增文件的 mtime 过滤
     - 若用户上一次跑距今 < 3 天，提示「距上次跑较近，确认要再写一次？」
  3. 调用 scan_project.py（ThreadPool 并发，按 active_window_days 过滤）→ manifest.json
  4. incremental: 调用 compute_diff.py → diff.json
  5. 调用 figure_picker.py → figures.selected_for_report 候选
  6. 调用 theory_extractor.py → theory bucket 中的 math 块
  7. 调用 interview_generator.py → interview.md（含 ⑦ 理论、⑧ 配图）
  8. 提示用户：「请打开 <path>/interview.md 填写，填完告知」
  9. 用户回信「填完了」/ 把内容贴回来
  10. 调用 parse_interview.py → interview_parsed.json
  11. LLM 把 manifest + diff + interview_parsed 合成 report.md（用第 10 节模板）
  12. 配图拷贝：从工程内 figures.selected_for_report 拷贝到 <week>/images/，引用相对路径
  13. 落档：
      - <project>/.weekly_report/<year>/<month>/<week>/{report.md, manifest.json, diff.json,
        interview.md, interview_parsed.json, images/}
      - D:\code\reports\<year>\<month>\<week>_<short_name>.md（report.md 副本）
      - D:\code\reports\index.md（追加一行）
      - <project>/.weekly_report/latest.txt（更新指针）
  14. 自检：是否有空段、流水账、漏 ask、漏配图、漏公式
  15. 输出周报路径 + 一段简短总结给用户
```

---

## 13. README.md（给师弟师妹的使用说明）

README 必须涵盖：
1. **是什么**：一句话定位 + 截图（周报样例片段）
2. **解决什么问题**：与"每周回忆 + 手写"对比的优劣
3. **第一次怎么用**：`/weekly-report init <path>` + 填 project.toml + 标 metric_vocab
4. **每周怎么跑**：`/weekly-report run`，填 interview，等 report
5. **project.toml 字段说明**：每个 key 是干啥的、默认值、可选值
6. **metric_vocab 怎么改**：手动加 known_keys、改 direction
7. **ignore 规则怎么调**：项目级 vs 全局
8. **常见 FAQ**：
   - 多项目并行：每个项目独立 .weekly_report
   - 跨周缺失（漏写一周）：自动跳过
   - 命名异常修复：先看 anomalies，可手动改 manifest
   - 指标不准：检查 metric_vocab 标注
   - 怎么导出给老师：reports 目录直接拷
9. **怎么复制给师弟师妹**：克隆 `weekly_report/` 整目录到他的 `~/.claude/plugins/`

---

## 14. 边界情况与降级

| 情况 | 行为 |
|---|---|
| 上周 manifest 损坏 | 降级 baseline，flag 警告 |
| 用户跳过 interview | 用 manifest 自动信息生成 80% 周报，剩余 [待补] |
| metric_vocab 撞全新 key | 写入 new_unknown_metrics，不阻塞主流程 |
| 工程目录改名 | 按 project.toml.name 比对而非绝对路径 |
| 一周无改动 | 输出"本周无显著工程变化"，仍提示填阅读/思考类 |
| 跨周缺失 | 自动跳过，对比最近一份可用 manifest |
| 扫描超时（>5 分钟） | 降级 metadata-only，移除 sha1 计算 |
| project.toml 缺失 | 走 init 模式 |
| Windows 路径长度爆 | 用 `\\?\` 长路径前缀 |

---

## 15. 性能预算

| 阶段 | 目标 | 现工程实测预估 |
|---|---|---|
| Scanner（增量，sha1 cache） | < 30s | 71315 文件 metadata + 553 内容文件 sha1 ≈ 20s |
| Differ | < 5s | 集合运算 |
| Interview 生成 | < 10s | LLM 一次调用 |
| Writer | < 60s | LLM 一次调用 |
| 总周报生成（不含用户填问卷） | < 2 分钟 | |
| 用户填 interview | 5-10 分钟 | 占总时间主导 |

---

## 16. 关键设计取舍（为什么这样）

1. **不读训练 ckpt 内容** —— 信息密度低 + 单文件大；文件名 + mtime 已有信号。
2. **不做 AST 级 diff** —— 行级 diff + LLM 摘要够用，AST 是 over-engineering。
3. **Interview 用文件而非对话** —— 工作量大，挨条对话回不动；文件 + 一次提交闭环。
4. **metric_vocab 一次性人工** —— 5 分钟换永久准确率，比纯启发式可靠。
5. **report 落两份** —— 工程内留档 + 汇总区便于翻历史。
6. **Scripts 实现确定性逻辑** —— LLM 不擅长 walk 71315 文件，分工。
7. **per-project 配置** —— 多项目隔离；雷达项目的 hint 不污染论文项目。
8. **新指标谨慎策略** —— 宁可漏一周也不污染周报。
9. **baseline 详细 + incremental 紧凑** —— 信息呈现节奏跟工作节奏对齐。
10. **README 必备** —— 这个 skill 要传给师弟师妹用。

---

## 17. 验收标准（success criteria）

- [ ] `/weekly-report init <radar_path>` 在 60 秒内生成可用 project.toml
- [ ] baseline 模式输出包含 10 节（含理论、配图、路线图），且每节非空
- [ ] incremental 模式准确识别 rcs_stacking_v25→v26 这条链
- [ ] 指标对比表正确呈现 mean ± std (n_seeds)
- [ ] interview.md 涵盖必问的 5 类（实验链 / 指标突变 / 论文 / 新指标 / 理论 / 配图）
- [ ] 跨年汇总目录按 `<year>/<month>/` 分层（工程内 + reports 区均如此）
- [ ] `D:\code\reports\index.md` 自动维护，包含所有历史周报一行一条
- [ ] 周报输出含问候语 + 结束祝福 + 学生签名 + 日期斜杠格式（与样例 docx 对齐）
- [ ] 周报正文含至少 1 张配图（如本周有图）和 1 个公式块（如本周有理论变化）
- [ ] 路径白名单守卫拦截一切对工程目录的写操作
- [ ] README 让师弟师妹零提问完成第一次跑
- [ ] 多项目切换不串数据
- [ ] active_window_days 每次跑都问一次

---

## 18. 待 plan 阶段细化的 open items（更新）

修订后大部分已闭环，剩余进 writing-plans 阶段处理：

| 原 open item | 状态 | 决议 |
| --- | --- | --- |
| scan_project.py 并发模型 | ✅ 已拍板 | ThreadPool walking，max_workers = `min(8, len(roots) * 2)` |
| interview.md 解析容错 | ✅ 已拍板 | H1 强匹配，H2 弱匹配，加 LLM 兜底 |
| metric_vocab 标注 UI | ✅ 已拍板 | markdown checkbox（同 interview.md 风格，参见 `references/metric-vocab-guide.md`） |
| baseline 路线图 prompt | ✅ 已拍板 | 借 grant-proposal 四象限结构，落 `references/baseline-roadmap-prompt.md` |
| 跨工程汇总区 index.md | ✅ 确认需要 | 自动维护，每次跑追加一行 |
| family_aliases.json 是否引入 | ⏳ 进 plan | 需要先跑过 1-2 周看 family_key 拆得是否过细 |
| pHash 配图去重的库选型 | ⏳ 进 plan | imagehash vs 自实现 8x8 dHash |
| init 模式自动检测 bucket roots 的算法 | ⏳ 进 plan | 基于子目录文件类型分布的启发式 |

---

## 19. 关于 metric_vocab 的澄清（用户问）

**问**：metric_vocab.json 是不是第一次工作时候做的表格？

**答**：不是手填表格，是"半自动一次性确认"流程：

1. 你跑 `/weekly-report init <project>` 时，skill 自动扫描所有 output JSON 文件，把所有 numeric top-level key 收集起来。
2. 用 hint tokens（acc/loss 等）自动归类一批；剩下不确定的 key 写进 `metric_vocab_init.md`。
3. 你打开这个 markdown 文件，每个 key 下面有 checkbox：

   ```markdown
   ### track_mean_per_seed
   - 上下文：在 Forecasting/output/inference_results.json 中，与 seeds=[1..10] 同时出现
   - 自动猜测：metric / aggregate of track_acc
   - [ ] 是指标，方向 higher_better
   - [ ] 是指标，方向 lower_better
   - [ ] 是配置（不参与对比）
   - [ ] 忽略
   ```

4. 你勾完保存，skill 解析后写到 `metric_vocab.json`，永远复用。
5. **后续每周如果出现全新 key，进 interview.md ⑥ 节追问，不是再填一次完整表格。**

**所以**：第一次确实是"半自动表格 + 你勾选"，但每条不超过 30 秒，不是从空白表格自己填。预计 30 个 key 总耗时 5-10 分钟。

---

## 20. 下一步

1. ✅ Spec written（v2，本文档）
2. ✅ Spec self-review（已完成，2 处修订）
3. 🟢 **用户审 spec**（你正在做的事）
4. ⏳ `/superpowers writing-plans` 把这个 spec 拆成实现 plan
5. ⏳ 按 plan 执行（脚本一个个写、模板填、跑 radar 项目 baseline 测试）

---
**End of design v3**（已合并 6 条修订 + 路线图 prompt 细化 + theory/figures 双 bucket）
