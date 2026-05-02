# paper-slides Integration Wrapper

> **包装的 skill**：`/paper-slides` (Beamer + PPTX + speaker notes)
> **触发**：会议汇报 / 组会汇报 / 通用学术汇报

## Input
```yaml
paper_dir: <project>/paper/
duration_min: 12 | 15 | 20 | 30
mode: conference | lab_meeting | tutorial
beamer_theme: metropolis | madrid | berlin
include_pptx: true             # 备选 PPTX 格式
speaker_notes: true            # 完整演讲稿
```

## Output
```text
<project>/slides/
├── slides.tex              # Beamer 源
├── slides.pdf              # PDF
├── slides.pptx             # PPTX 备选
└── speaker_notes.md        # 每页 speaker note
```

## thesis-helper 调用条件

```text
config.integrations.paper_slides: true
   或
thesis_type == conference 且 venue.auto_generate_slides: true
   →  Phase 5 (conference) 触发
```

## 与 thesis-defense-prep 的差异

```text
paper-slides              通用会议汇报
   - 节奏：12-30 分钟
   - 受众：peer researchers
   - 风格：methodology-first

thesis-defense-prep       毕设答辩特化
   - 节奏：15-30 分钟
   - 受众：评委（多角度）
   - 风格：contribution + limitation 突出
   - 强制 Q&A 模拟 + 备查 PPT
```

毕设答辩选 thesis-defense-prep，会议汇报选 paper-slides。

## 触发流程（会议场景）

```text
1. /paper-slides paper/ --duration 12 --mode conference
2. 输出 Beamer 源 + 编译 PDF
3. 自动 /pptx 转 PPTX 备选
4. speaker_notes.md 含每页口播 + 转场
5. 用户演练 + 微调
```

## 相关

- 同级：[`paper-poster-wrapper.md`](paper-poster-wrapper.md) [`pptx-wrapper.md`](pptx-wrapper.md)
- 区别：[`../extensions/thesis-defense-prep/SKILL.md`](../extensions/thesis-defense-prep/SKILL.md)
- pipeline：conference Phase 5
