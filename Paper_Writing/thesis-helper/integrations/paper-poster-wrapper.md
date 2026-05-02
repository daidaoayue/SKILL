# paper-poster Integration Wrapper

> **包装的 skill**：`/paper-poster` (LaTeX beamerposter / tcbposter A0/A1 PDF + PPTX)
> **触发**：会议接收后 / 学术海报展示

## Input
```yaml
paper_dir: <project>/paper/
size: A0 | A1
orientation: portrait | landscape
template: tcbposter | beamerposter
include_qr_code: true                # 链到论文 PDF
sections:
  - intro_with_one_image
  - contribution_bullets
  - method_diagram
  - main_results_table
  - qualitative_examples
  - conclusion + qr_code
```

## Output
```text
<project>/poster/
├── poster.tex               # LaTeX 源
├── poster.pdf               # A0 PDF（打印用）
├── poster.pptx              # 编辑版（活动方可能要 PPTX）
└── poster.svg               # 矢量 SVG
```

## thesis-helper 调用条件

```text
config.integrations.paper_poster: true
   或
thesis_type == conference 且 venue.auto_generate_poster: true
   →  Phase 6 (conference) 触发
```

## 设计原则（基于 academic poster 最佳实践）

```text
1. 5 米外能看清标题 → 标题字号 ≥ 100pt
2. 1 米外能看清 contribution bullets → 18-24pt
3. 视觉密度合规（≤ 5 分钟阅读完）
4. 图表占比 ≥ 50%（人不爱读字）
5. 颜色对比 colorblind-safe
6. QR code 链 paper PDF / GitHub
```

## 与会议规格对齐

```text
NeurIPS / ICLR / ICML  通常 A0 portrait
CVPR / ICCV            通常 A0 landscape
IEEE Conf              通常 A1
ACL / EMNLP            通常 A0 portrait
```

## 相关

- 同级：[`paper-slides-wrapper.md`](paper-slides-wrapper.md)
- pipeline：conference Phase 6
