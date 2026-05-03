# thesis-helper · 工作流图三种风格选项

> v0.6.5 用 canvas-design / frontend-design / matplotlib 三个 skill 并行渲染了 3 张架构图，按汇报场景挑选。

## 🅰️ Variant A · 海报版（古典杂志/制图年鉴风）

![A](variant-A-canvas.png)

- **风格**：PLATE I · QUEST CARTOGRAPHY 古典制图年鉴
- **配色**：米黄底 + 深红 + 海军蓝 + 黑白 serif
- **适合**：学术海报、毕设成果展、有"匠气"的汇报
- **文件**：`variant-A-canvas.png` (362 KB · 1920×1080)

## 🅱️ Variant B · Dashboard 版（Vercel/Linear/Stripe 风）

![B](variant-B-frontend.png)

- **风格**：现代 SaaS 控制台
- **配色**：靛蓝 #4F46E5 + 中性灰 + 软阴影
- **排版**：顶部命令栏 + 横向 10 卡片流 + 底部黑色交付物 band
- **适合**：工程汇报、行业大会、给老板/投资人看
- **文件**：`variant-B-frontend.png` (202 KB · 1920×1080) + `variant-B-frontend.html`（可改色）

## 🅲 Variant C · 学术 paper figure 版（顶会论文风）

![C](variant-C-academic.png)

- **风格**：顶会论文 architecture diagram 严谨黑白
- **配色**：纯黑白 + 深海军蓝 #1f3a5f 标 4 处关键里程碑
- **排版**：左 L1/L2 纵向流 + 右 L3 网格 + 底部 Figure 1 caption
- **适合**：答辩 PPT、毕业论文插图、给评审看
- **文件**：`variant-C-academic.png` (418 KB) + `variant-C-academic.svg`（可放大无损）

## 选用建议

| 汇报场景 | 推荐 |
|---------|------|
| 给老师汇报项目进展 | **C** 严谨可信 |
| 答辩 PPT 第一页 | **C** 或 **B** |
| 给同学/学弟妹推广 | **B** 视觉冲击强 |
| 学术海报 / 比赛 | **A** 独特设计感 |
| 投稿论文配图 | **C** 唯一适合直接放进 .tex |

## 重新渲染

- A: `python variant-A-render.py`
- B: 在浏览器打开 `variant-B-frontend.html` 改 CSS，再用 `chrome --headless --window-size=1920,1080 --screenshot=variant-B-frontend.png variant-B-frontend.html` 重导
- C: `python draw_workflow_v2.py`
