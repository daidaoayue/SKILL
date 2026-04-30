---
name: aigc-scan
description: "AIGC率预扫描工具（v1）。在运行 aigc-reduce 流水线之前，用 Hello-SimpleAI/chatgpt-detector-roberta (NeurIPS 2023) 对论文做 section-level 扫描，输出模型驱动的风险排序队列，替代 aigc-reduce Phase 0 的启发式优先级。支持 before/after 对比验证 aigc-reduce 效果。Triggers on: '/aigc-scan', 'aigc扫描', '预扫描', 'aigc检测', '扫描aigc', 'before/after验证', 'aigc风险排序'."
argument-hint: [file-path] [--compare results/results_before.json]
allowed-tools: Read, Write, Bash, Glob
---

# AIGC预扫描工具（aigc-scan · v1）

## Role

在 `/aigc降低` 流水线启动**之前**运行，用真实模型评分代替启发式规则对 section 排优先级。也可在流水线**完成之后**运行，与 baseline 对比，量化 aigc-reduce 的降低效果。

## 两种使用场景

### 场景 A：流水线前预扫描（推荐）

```
/aigc-scan path/to/paper.tex
```

输出模型驱动的处理优先级队列，直接交给 `/aigc降低` 使用。

### 场景 B：before/after 效果验证

```
/aigc-scan path/to/paper_reduced.tex --compare path/to/results_before.json
```

输出 section-level delta 报告，确认哪些 section 已降下来、哪些还需要继续处理。

## Workflow

### Step 0: 检查 detect_aigc.py 可用性

用 Glob 找到 `detect_aigc.py` 的绝对路径：

```python
# 优先搜索顺序：
# 1. 与当前 skill 同级目录（aigc-reduce-skills/detect_aigc/detect_aigc.py）
# 2. ~/.claude/skills/detect_aigc/detect_aigc.py
# 3. 用户当前工作目录下的 detect_aigc.py
```

如果找不到 `detect_aigc.py`，输出降级提示并切换到启发式模式（见下文"降级路径"）。

### Step 1: 运行预扫描

**场景 A（仅预扫描）**：

```bash
python /path/to/detect_aigc.py \
    "$FILE_PATH" \
    --section-split \
    --label baseline \
    --out ./aigc-scan-results \
    --stdout-json
```

将 stdout JSON 捕获到变量 `SCAN_RESULT`。

**场景 B（含对比）**：

```bash
python /path/to/detect_aigc.py \
    "$FILE_PATH_REDUCED" \
    --section-split \
    --label after_reduce \
    --compare "$COMPARE_JSON" \
    --out ./aigc-scan-results
```

### Step 2: 解析扫描结果

从 `SCAN_RESULT` JSON 中提取 `section_scores` 数组：

```json
{
  "section_scores": [
    {"section_title": "致谢", "ai_prob": 0.52, "risk_label": "🚨 极高", "char_len": 412},
    {"section_title": "软件系统架构", "ai_prob": 0.38, "risk_label": "🔴 显著", "char_len": 1203},
    ...
  ]
}
```

### Step 3: 输出优先级处理队列

输出 `aigc-scan-report.md`，格式如下：

````markdown
# AIGC 预扫描报告

**文件**: `paper.tex`  
**扫描时间**: YYYY-MM-DD HH:MM  
**模型**: Hello-SimpleAI/chatgpt-detector-roberta (NeurIPS 2023)  
**全文加权 AIGC 概率**: X.X%  {_bar}  {_risk}

⚠️ 本地检测仅供参考，CNKI 是终审。

## Section 风险排序（模型评分驱动）

| 优先级 | section | ai_prob | 风险 | 建议动作 |
|-------|---------|---------|------|---------|
| #1 | 致谢 | 52.1% | 🚨 极高 | Stage 0 致谢专项重写 |
| #2 | 软件系统架构 | 38.4% | 🔴 显著 | Stage 0 去结构化 |
| #3 | 引言 | 24.7% | 🟡 偏高 | Stage 1 词汇 + Stage 5 思维痕迹 |
| #4 | 实验结果 | 8.2% | ✅ 安全 | 可跳过或最后处理 |
| ... | ... | ... | ... | ... |

## aigc-reduce 处理顺序建议

按以下顺序执行 `/aigc降低`，高风险 section 优先：

1. [ ] **致谢节** (52.1%) — Stage 0 致谢专项重写（CNKI 实测最高风险区）
2. [ ] **软件系统架构** (38.4%) — Stage 0 去结构化（列表式分层架构）
3. [ ] **第三章 相位特征** (24.7%) — Stage 1+5（词汇 + 思维痕迹注入）
...

## 可跳过（ai_prob < 10%，本地模型评为安全）

- 实验结果 (8.2%) — 含具体数字，已有足够 specificity
- 参考文献 — 不检测
````

创建 `aigc-scan-todos.md`（供 aigc-reduce 的 Phase 0 直接消费）：

````markdown
# aigc-scan 生成的处理队列
# 由 detect_aigc.py --section-split 的模型评分驱动
# 格式：[ ] PRIORITY | SECTION_TITLE | AI_PROB | RECOMMENDED_STAGES

- [ ] #1 | 致谢 | 52.1% | Stage-0-致谢专项
- [ ] #2 | 软件系统架构 | 38.4% | Stage-0-去结构化
- [ ] #3 | 第三章 相位特征设计 | 24.7% | Stage-1,5
- [skip] #4 | 实验结果分析 | 8.2% | —
````

### Step 4: Before/After 对比报告（场景 B）

如果运行了 `--compare`，额外输出 `aigc-scan-delta.md`：

````markdown
# Before/After 对比报告

**Before**: paper_baseline.tex  全文 15.1%
**After**:  paper_reduced.tex   全文  2.8%
**净降低**: ↓12.3%

| section | before | after | delta | 状态 |
|---------|--------|-------|-------|------|
| 致谢 | 52.1% | 4.2% | ↓47.9% | ✅ 已修 |
| 软件架构 | 38.4% | 6.1% | ↓32.3% | ✅ 已修 |
| 相位特征 | 24.7% | 18.2% | ↓6.5% | 🟡 仍偏高，建议继续处理 |
| 实验结果 | 8.2% | 7.9% | ↓0.3% | ✅ 安全 |

## 仍需处理的 section

- 🟡 **相位特征** (18.2%) — 建议再跑 Stage 5 困惑度重构
````

## 降级路径（detect_aigc.py 不可用时）

如果 Python 不可用或 `detect_aigc.py` 找不到，输出降级提示，并切换到启发式优先级：

```
⚠️ detect_aigc.py 不可用，切换到启发式优先级模式

启发式优先级（基于两次 CNKI 实测反向工程）：
#1 致谢节（acknowledgement）— CNKI 实测最高风险区
#2 软件系统/架构层级描述
#3 三段式结论/展望
#4 文献综述
#5 方法论对比
#6 引言
#7 方法描述
#8 实验结果/数字段（最低风险）
```

## 输出文件

| 文件 | 内容 |
|------|------|
| `aigc-scan-report.md` | 人可读的扫描报告 + 优先级队列 |
| `aigc-scan-todos.md` | 机器可读的处理队列（供 aigc-reduce 消费） |
| `aigc-scan-results/results_*.json` | detect_aigc.py 原始 JSON 输出 |
| `aigc-scan-delta.md` | Before/after 对比报告（场景 B 专用） |

## 与 aigc-reduce 的集成

aigc-reduce Phase 0 会**自动检查** `aigc-scan-todos.md` 是否存在：

- **存在**：直接读取模型评分驱动的优先级队列，跳过启发式排序
- **不存在**：使用原有启发式优先级（致谢 > 软件架构 > 三段结论 > ...）

推荐工作流：

```
/aigc-scan paper.tex          # 1. 预扫描，生成 aigc-scan-todos.md
/aigc降低 paper.tex            # 2. aigc-reduce 自动读取扫描结果，按模型评分处理
/aigc-scan paper_reduced.tex --compare aigc-scan-results/results_paper_baseline.json
                               # 3. 验证降低效果
```

## 三条红线

- ❌ 本地模型评分仅供优先级排序，不能代替 CNKI 做最终判断
- ❌ ai_prob < 10% 的 section 也不能保证 CNKI 安全（模型与 CNKI 存在差距）
- ❌ 运行失败时必须切换降级路径，不能静默跳过

## Owner 闭环

- 必须输出 `aigc-scan-report.md` + `aigc-scan-todos.md`
- 如果是场景 B，必须输出 `aigc-scan-delta.md`
- 必须在报告末尾标注"⚠️ CNKI 是终审"
