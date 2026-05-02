# thesis-helper · Cline / Continue / Roo Code 平台

## 安装

```bash
python /path/to/thesis-helper/compilers/build.py \
    --target cline \
    --output D:/my-thesis-project/.clinerules
```

会在项目根生成 `.clinerules`。Cline (VSCode 插件) 打开项目时自动加载。

兼容 **Continue** / **Roo Code** —— 它们都读取 `.clinerules` 或类似文件。

## 触发方式

打开 VSCode 的 Cline 面板，输入：

```text
帮我写本科毕设，按 thesis-helper 流程来
```

## 平台特性

- **Plan + Act 双模式**：建议先用 Plan 模式让 AI 出 pipeline 摘要，
  确认后切 Act 模式真跑。
- **Auto-approve**：跑 aigc-reduce / latex-to-word 这类长流程建议开
  auto-approve（read/write/run 全开）。
- **多 LLM**：Cline 后端可以是 Claude / GPT / Gemini / 本地模型——
  本 skill 的 prompt 是平台无关的。

## 依赖

- Cline ≥ 2.0（或 Continue / Roo Code 最新版）
- VSCode
- Python ≥ 3.9
- 其他依赖同 Claude 平台

## 已知限制

- Cline 不支持 Claude Skill 嵌套，`/sub-skill` 调用要 Cline 自行读取
  `thesis-helper/{integrations,extensions}/<name>/SKILL.md` 并执行。
  cline.py 编译时已注入此 fallback 说明。

## 升级

```bash
cd /path/to/SKILL && git pull
python /path/to/thesis-helper/compilers/build.py \
    --target cline \
    --output D:/my-thesis-project/.clinerules
```
