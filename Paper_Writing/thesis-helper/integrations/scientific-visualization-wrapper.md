# scientific-visualization Integration Wrapper

> **包装的 skill**：`/scientific-visualization` (publication-quality figures)
> **触发**：期刊/会议投稿前 / 图表升级 vector PDF

## Input
```yaml
data_source: <csv | json | npz | py_script>
figure_type: line | bar | heatmap | scatter | confusion_matrix | roc | ablation
target_format: vector_pdf | eps | tiff_300dpi
colorblind_safe: true                  # 期刊默认必开
multi_panel: true                      # a/b/c/d 子图
significance_markers: true             # **，*** 显著性标记
error_bars: true                       # 误差棒
font_family: serif                     # 与正文字体一致
```

## Output
```text
<project>/figures/journal/
├── fig_<name>.pdf                # vector
├── fig_<name>.eps                # 兼容旧期刊
├── fig_<name>_300dpi.tiff        # IEEE 推荐
└── latex_includes.tex            # 自动更新 \input{}
```

## thesis-helper 调用条件

```text
config.integrations.scientific_visualization: true
   且 thesis_type ∈ {journal, conference, master-thesis}
   →  Phase 3 触发
```

## 触发流程

```text
1. 扫描 <project>/results/ 找 csv/json/npz 数据
2. 扫描 <project>/figures/ 找现有 .py 画图脚本
3. /scientific-visualization 升级每张图：
   ├── 替换字体为 serif
   ├── 调色板换 colorblind-safe (cubehelix / ColorBrewer)
   ├── 加误差棒（如有 multiple seeds）
   ├── 加 *** 显著性标记（如有 t-test）
   └── 输出 vector PDF
4. 更新 figures/latex_includes.tex
5. paper-write 阶段直接 \input{} 即可
```

## 与 paper-figure 的差异

```text
paper-figure              快速生成图（开发中用）
scientific-visualization  投稿就绪升级（投稿前一次性跑）
```

## 与 matplotlib-tvhahn 的差异

```text
scientific-visualization  期刊通用风格 (serif / vector / colorblind)
matplotlib-tvhahn         Tim Hahn 个人风格（whitegrid / cubehelix / despined）
```

## 相关

- 同级：[`matplotlib-tvhahn-wrapper.md`](matplotlib-tvhahn-wrapper.md) [`paper-illustration-wrapper.md`](paper-illustration-wrapper.md)
- pipeline：journal / conference / master-thesis Phase 3
