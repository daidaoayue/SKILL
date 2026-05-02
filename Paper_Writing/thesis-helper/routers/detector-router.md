# Detector Router · 检测器路由

> 输入：`thesis.config.yml` 的 `detector` 字段
> 输出：加载对应 `detectors/<name>/adapter.md` + 阈值

## 决策树

```text
读 detector 字段
   │
   ├── "CNKI"      → detectors/cnki/adapter.md       ✅ 生产可用
   ├── "Turnitin"  → detectors/turnitin/adapter.md   🟡 接口预留
   ├── "PaperPass" → detectors/paperpass/adapter.md  🟡 接口预留
   ├── "VIPCS"     → detectors/vipcs/adapter.md      🟡 接口预留
   ├── "none"      → 跳过 AIGC 降痕（期刊/会议默认）
   └── 缺失         → 按 thesis_type 默认（见下表）
```

## 默认 detector（按 thesis_type）

```text
┌────────────────────────────────────────────────────────────────────┐
│ thesis_type      │ 默认 detector │ 理由                              │
├──────────────────┼──────────────┼──────────────────────────────────┤
│ undergrad-thesis │ CNKI          │ 国内学位论文唯一终审               │
│ master-thesis    │ CNKI          │ 同上                              │
│ phd-thesis       │ CNKI          │ 同上                              │
│ journal          │ none          │ 期刊不查 CNKI（除非作者要求自查） │
│ conference       │ none          │ 会议不查 CNKI                     │
└────────────────────────────────────────────────────────────────────┘
```

## 多 detector 串行（高级用法）

如果用户要"先用 PaperPass 自查，再用 CNKI 终审"：

```yaml
detector: CNKI                       # 主 detector
secondary_detectors:
  - PaperPass                        # 投稿前自查
  - VIPCS                            # 比对
```

执行顺序：

```text
1. /aigc降低（基于 CNKI adapter，主流程）
2. 跑完 CNKI round 1 后
3. 提示用户上传到 PaperPass + VIPCS 做交叉验证
4. 任一不达标 → round 2
```

## 跨语言场景（中英混合论文）

```text
language=zh + 中文为主              → CNKI
language=en + 海外投稿              → Turnitin
language=mix（中英章节都有）         → 双 detector：
   detector: CNKI
   secondary_detectors: [Turnitin]
```

## 阈值传递规则

```text
config.targets.aigc_rate_max
   ↓ 优先级最高，覆盖一切默认
school_rules.<venue>.aigc_rate_max
   ↓ 第二优先
detector adapter 内置默认
   ↓ 兜底
```

示例：

```yaml
thesis_type: master-thesis           # detector 默认推 CNKI
venue: 清华大学                       # school_rules.tsinghua_master.aigc_rate_max=5
detector: CNKI
targets:
  aigc_rate_max: 3                   # 用户更严，覆盖一切
```

→ 实际生效阈值：3%（user override）

## 检测器能力矩阵

```text
┌──────────────┬───────┬────────┬─────┬───────────────────────────┐
│ 检测器       │ AIGC  │ 重复率 │ AI  │ 适用场景                  │
├──────────────┼───────┼────────┼─────┼───────────────────────────┤
│ CNKI         │ 强    │ 强     │ 强  │ 国内学位论文（终审）       │
│ Turnitin     │ 中    │ 强     │ 中  │ 海外学位 + 期刊            │
│ PaperPass    │ 弱    │ 中     │ 弱  │ 国内备查（便宜）            │
│ VIPCS        │ 中    │ 中     │ 中  │ 部分高校采用                │
└──────────────┴───────┴────────┴─────┴───────────────────────────┘
```

## 添加新检测器（开发者指南）

```text
1. 创建 detectors/<name>/adapter.md   照 cnki/adapter.md 模板
2. 实现 7 个章节：
   - Input
   - Output
   - 与其他 detector 的差异
   - 降痕策略
   - Pipeline 调用方式
   - 阈值映射
   - 与 aigc-reduce 的复用关系
3. 在 thesis.config.template.yml 的 detector 字段注释中加入新选项
4. 在本路由的决策树和能力矩阵中加一行
```

## 与其他 router 的关系

```text
intent-router (论文类型)
   ├── 委托 venue-router        → 学校规则
   └── 委托 detector-router (本文件)  → 检测器选择
```
