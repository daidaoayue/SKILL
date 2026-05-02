# CNKI Detector Adapter · 知网检测器适配

> **状态：✅ 生产可用** —— 已通过 aigc-reduce v3 实测（北航 7 万字毕设：15.1% → 2.8%）
> **底层依赖：** `../../../aigc-reduce-skills/aigc-reduce/` (8 个 stage skills)

## 调用契约

### Input
```yaml
input:
  file_path: <project>/paper/main.tex     # 必填，待处理 LaTeX 源文件
  thesis_type: undergrad-thesis            # 决定阈值
  targets:
    aigc_rate_max: 8                       # 上限 (%)
    duplicate_rate_max: 8                  # 上限 (%)
  school_rules:                            # 可选学校特殊规则
    aigc_hidden_redline: true              # 北航 AIGC 隐红线
```

### Output
```yaml
output:
  reduced_file: <project>/paper/main_aigc-reduced.tex
  reports:
    - <project>/paper/aigc-reduce-report.md
    - <project>/paper/aigc-reduce-trace.md
    - <project>/paper/aigc-scan-results/results_baseline.json
    - <project>/paper/aigc-scan-results/results_after_reduce.json
  cnki_validation:
    required: true                          # 必须人工上传 CNKI 验证
    record_path: <project>/paper/cnki-aigc-round*.md
  metrics:
    aigc_rate_local_before: <float>%
    aigc_rate_local_after: <float>%
    duplicate_rate: <float>% (本地估算)
    cnki_aigc_rate: <user-填> (人工填入)
```

## 调用方式（thesis-helper 内部）

```text
1. thesis-helper 解析 thesis.config.yml
2. detector == "CNKI" → 加载本 adapter
3. 触发 Skill: /aigc降低 <input.file_path>
4. 等待 aigc-reduce 全部 7 stage 完成
5. 解析 aigc-reduce 输出的 trace 和 report
6. 检查 metrics 是否满足 targets
   ├── 满足 → 提示用户上传 CNKI 验证
   └── 未满足 → 触发二次处理（aigc-reduce 自循环）
```

## 阈值映射（thesis_type → CNKI 实战阈值）

依据：北航 v3 实战 + 用户的 `feedback_data_anomaly_audit` 经验

| thesis_type | aigc_rate_max | duplicate_rate_max | cnki_validation_required |
|-------------|:-------------:|:------------------:|:------------------------:|
| undergrad-thesis | 8% | 8% | ✓ |
| master-thesis | 5% | 5% | ✓ |
| journal | n/a | n/a | ✗ (跳过 CNKI) |
| conference | n/a | n/a | ✗ |

⚠️ **CNKI 永远是终审。本地 detector 仅参考。**

## 二次处理触发条件

```text
本地 ai_prob > thesis_type 阈值
   或 任意 section ai_prob > 20% (本地)
   → 自动二次处理：
     - 对超阈 section 重跑 aigc-reduce 7 stage
     - 重点强化：思维痕迹注入（Stage 5）+ 致谢节专项（Stage 0）
     - 输出 round2 报告
```

## CNKI 实战经验（继承自 aigc-reduce v3）

### 必修高危区（按优先级）

```text
1. 致谢节            （v3 实测 13.5%）
2. 软件系统/架构层级 （v3 实测 8.4%）
3. 三段式结论        （v3 实测 7.x%）
4. 文献综述（密集 cite）
5. 方法对比段（"代价是 X，优势在于 Y"）
6. 引言"凸显了... 共同特征是"列举公式
```

### 不要做的事（避免学术规范违规）

- ❌ 用文学化语言降 AIGC（"撞墙"/"主流算子库的舒适区"）→ 学术规范违规
- ❌ 过度 hedging（"在...条件下"/"暗示了"过密）→ 反被标 AI
- ❌ 只信本地 detector → 第一版本地 2.4% 但 CNKI 15.1% 的差距真实存在

## 与其他检测器的关系

```text
本 adapter (CNKI)            生产可用 ✅
├── ../turnitin/adapter.md   占位 🚧
├── ../paperpass/adapter.md  占位 🚧（算法相近 CNKI，可复用部分规则）
└── ../vipcs/adapter.md      占位 🚧（部分高校使用）
```

后续若用户切换 detector，路由器会加载对应 adapter，aigc-reduce 的 7 stage
会按目标检测器调整规则（占位文件实现后）。

## 相关文件

- 上游：[`../../../aigc-reduce-skills/aigc-reduce/SKILL.md`](../../../aigc-reduce-skills/aigc-reduce/SKILL.md)
- 上游：[`../../../aigc-reduce-skills/detect_aigc/detect_aigc.py`](../../../aigc-reduce-skills/detect_aigc/detect_aigc.py)
- 同级：[`../turnitin/`](../turnitin/) [`../paperpass/`](../paperpass/) [`../vipcs/`](../vipcs/)
- pipeline：[`../../pipelines/undergrad-thesis-pipeline.md`](../../pipelines/undergrad-thesis-pipeline.md)
