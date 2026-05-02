# comm-lit-review Integration Wrapper

> **包装的 skill**：`/comm-lit-review` (Communications domain literature review)
> **触发**：通信 / 无线 / 雷达 / 卫星 NTN / Wi-Fi / cellular / 传输协议 方向

## Input
```yaml
topic: <comm-direction>
sub_field:
  - radar
  - wireless_communication
  - satellite_ntn
  - wifi_802_11
  - cellular_5g_6g
  - transport_protocol
seed_papers: <optional>
```

## Output
```text
<project>/.thesis-helper/lit/comm-lit/
├── related_work_draft.md       # 中文/英文可选
├── benchmark_table.md          # 主流方法对比表
├── citation_pool.bib
└── tech_taxonomy.md            # 通信领域专属技术分类
```

## thesis-helper 调用条件

```text
config.integrations.comm_lit_review: true
   或
thesis_type ∈ {undergrad-thesis, master-thesis} 且 venue ∈ {北航, 西电, 北邮, ...}
   →  Phase 1 触发（取代 research-lit）
```

## 通信领域特化

- 知识库优先：通信经典综述（Sklar / Tse / Goldsmith）+ 近 5 年 IEEE Trans
- 技术词汇：MIMO / OFDM / NOMA / mmWave / Beamforming / Channel Estimation
- 数据集：5G NR / LoRa / WiFi-6/7 / Sentinel SAR / TUM-Radar
- 标准引用：3GPP TS 38.x / IEEE 802.11x / ITU-R

## 与 research-lit 的差异

```text
research-lit         通用，AI 自由发挥分类
comm-lit-review      专家知识库优先 + 通信术语强约束 + 标准引用
```

## 与雷达毕设的对接

适配你的雷达目标识别项目（来自 `memory/project_radar.md`）：
- 自动包含 ATR (Automatic Target Recognition) 综述
- HRRP / SAR / ISAR / MicroDoppler 经典工作
- Time-Frequency 联合特征 + Deep Learning 路线对比

## 相关

- 同级：[`research-lit-wrapper.md`](research-lit-wrapper.md)
- pipeline：undergrad / master-thesis Phase 1
