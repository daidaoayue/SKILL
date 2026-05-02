# thesis-helper · Universal Prompt Pack 平台

> 适用：任意 AI 聊天机器人（Claude.ai / ChatGPT 网页 / Gemini 网页 / 文心 / 豆包 / Qwen / DeepSeek / Kimi / 智谱 ...）

## 编译

```bash
python /path/to/thesis-helper/compilers/build.py \
    --target universal \
    --output thesis-prompt-pack.md
```

输出 `thesis-prompt-pack.md`（全文 prompt 包，无字符压缩）。

## 使用

### 第一步：复制全文

打开 `thesis-prompt-pack.md`，**全选 + 复制**。

### 第二步：粘贴到任意 AI 对话窗口

把内容粘贴到你常用的 AI（无论是 Claude.ai 网页、ChatGPT 网页、文心一言、
豆包、Qwen、DeepSeek、Kimi、智谱清言...任意都行）。

### 第三步：告诉 AI 你的项目和论文类型

```text
我要用 thesis-helper。
我的项目目录：D:/my-thesis-project
论文类型：本科毕设   (或 期刊 / 会议 / 硕士毕设)
学校/期刊：北航       (或 IEEE_JOURNAL / NeurIPS / 清华 ...)
```

AI 会按照 thesis-helper 工作流执行。

## 各 AI 平台适配

```text
Claude.ai 网页    无文件系统  →  你粘贴 LaTeX，AI 输出修改版你复制回去
ChatGPT 网页      Code Interp →  可上传 .tex .docx，AI 用 Python 处理
Gemini 网页       多模态      →  可上传 PDF + 论文截图
文心 / 豆包       网页对话    →  你贴文本，AI 给方案+代码
DeepSeek         网页对话    →  同上
Kimi             长上下文    →  适合 7 万字毕设（完整粘贴）
Qwen / 智谱      网页对话    →  同上
```

## 平台特性

- **零依赖安装**：不需要装 Cline / Cursor / Claude Code，开浏览器就用。
- **跨语言模型**：你今天用 Claude，明天换 GPT，都是同一套 prompt。
- **降级能力**：无工具能力的 AI 也能给出文字方案，你手动执行。

## 限制

- 无法直接读写磁盘 → 用户需手动复制粘贴
- AI 上下文窗口可能不够装 prompt + 整本论文 → 分章节处理
- 无 sub-skill 嵌套 → 需要细节时手动让 AI 读对应 SKILL.md

## 推荐用法（对学生最友好）

```text
1. 你电脑上不装任何东西
2. 把 thesis-prompt-pack.md 收藏到云笔记
3. 每次写论文：
   a. 打开任意免费 AI 网页
   b. 粘贴 prompt-pack
   c. 告诉它你的论文情况
   d. AI 给你 LaTeX 修改 / 降 AIGC 方案 / 答辩 PPT 大纲
```

## 升级

```bash
cd /path/to/SKILL && git pull
python /path/to/thesis-helper/compilers/build.py \
    --target universal \
    --output thesis-prompt-pack.md
```
