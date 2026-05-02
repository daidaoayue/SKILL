# Changelog · thesis-helper

## v0.5.1 (2026-05-02) · 真实 CNKI 实测验证

基于真实雷达毕设项目（D:\code\radar_target_recognition）的端到端实测：

### 🎯 真实 CNKI AIGC 检测对比（同一篇毕设的 baseline vs 降痕版）

| 维度 | baseline | 降痕版 | 差距 |
|------|---------|--------|------|
| 全文 AI 特征值 | 7.1% | 6.7% | -0.4 pp |
| 致谢节（绪论_第5部分）| 30.9% | 0.0% | **-30.9 pp ✅✅✅** |
| 第 3 部分 | 6.0% | 0.0% | -6.0 pp ✅ |
| 第 4 部分 | 0.0% | 14.6% | **+14.6 pp ⚠️ 副作用** |
| 第 1 部分 | 18.5% | 18.5% | 持平（需迭代）|

### 🎯 验证发现

- ✅ 致谢节专项处理（v3 重点）真实有效
- ⚠️ 整体降幅 0.4 pp 弱于预期
- ❌ 部分章节出现"降痕引入新 AI 特征"副作用
- ✅ 6.7% 已远低于北航 8% 红线

### 📌 后续迭代方向

1. Stage 0 去结构化触发模式需扩充（国际团队列举类）
2. 致谢节专项保留为核心抓手
3. 加"降痕后回归测试"机制防副作用

---

## v0.5 (2026-05-02) · Batch 3 完结 · 全工作流闭环

- 4 类型 pipeline 全部覆盖（journal/conference/undergrad/master-thesis）
- 20 integrations 全部接入
- 5 extensions 全部投产（含 latex-to-word/blind-review/format-check 等）
- 4 检测器适配（CNKI 生产 + Turnitin/PaperPass/VIPCS 接口预留）
- 6 平台跨平台编译（Claude/Cursor/Gemini/Cline/ChatGPT/Universal）
- 总规模：68 文件 / 234.5 KB

## v0.4 (2026-05-02) · Batch A · 跨平台编译器 + ChatGPT

- compilers/build.py 跨平台主入口
- 6 个 target 模块（含 ChatGPT 7500 字符压缩）
- 6 个 platform README（安装+使用指南）

## v0.3 (2026-05-02) · Batch B · 5 extensions 全造

- latex-to-word（国内毕设必交 Word）
- thesis-defense-prep（答辩 PPT + Q&A 模拟）
- thesis-blind-review（硕博盲审版）
- bilingual-abstract（中英摘要平行）
- format-compliance-checker（学校格式合规）

## v0.2 (2026-05-02) · Batch 1 · MVP 本科毕设端到端

- scanners/project-scanner.py（智能项目扫描）
- routers/intent-router.md（论文类型路由）
- detectors/cnki/adapter.md（CNKI 适配，调 aigc-reduce）
- pipelines/undergrad-thesis-pipeline.md
- examples/undergrad-thesis-example.yml
- integrations/docx-wrapper.md
- extensions/latex-to-word/SKILL.md

## v0.1 (2026-05-02) · 初始顶层架构

- SKILL.md（Claude 顶层入口）
- README.md（用户指南）
- thesis.config.template.yml（项目配置模板）
- FILE_TREE.md（完整文件树）
