# matplotlib-tvhahn Integration Wrapper

> **包装的 skill**：`/matplotlib-tvhahn` (Tim Hahn 风格出版级图)
> **触发**：偏好 whitegrid + cubehelix 风格 / Notebook 演示图

## Input
```yaml
data: <csv | dict | dataframe>
chart_type: line | bar | violin | regression | timeseries
style: tvhahn_default | tvhahn_dark
annotations: true       # 丰富注释
despined: true          # 去顶/右框线
```

## Output
```text
<project>/figures/tvhahn/<name>.{png,pdf,svg}
+ generation script: <project>/figures/tvhahn/<name>_gen.py  # 复用
```

## thesis-helper 调用条件

```text
config.integrations.matplotlib_tvhahn: true
   →  Phase 3 备选风格（与 scientific-visualization 二选一）
```

## 风格特点

- whitegrid 背景
- DejaVu Sans 字体
- cubehelix / ColorBrewer 调色板
- despined 轴（去顶部/右侧框线）
- 注释丰富（标注关键点 + 参考线）
- colorblind-safe

## 何时选 tvhahn 而非 scientific-visualization

```text
scientific-visualization   IEEE/Nature serif 严肃风
matplotlib-tvhahn          Talk/Slide/Notebook 现代风
```

会议汇报 / 海报 / Slack 分享建议 tvhahn；期刊投稿建议 scientific-visualization。

## 相关

- 同级：[`scientific-visualization-wrapper.md`](scientific-visualization-wrapper.md)
- pipeline：conference Phase 3 + 答辩 PPT 配图
