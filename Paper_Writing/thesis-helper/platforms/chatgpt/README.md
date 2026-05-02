# thesis-helper · ChatGPT 自定义 GPTs 平台

## 编译

```bash
python /path/to/thesis-helper/compilers/build.py \
    --target chatgpt \
    --output thesis-helper-gpt-instructions.md
```

输出 `thesis-helper-gpt-instructions.md`，**严格控制在 7500 字符以内**
（OpenAI 限制 8000 字符，留 buffer）。

## 创建自定义 GPT

1. 打开 [ChatGPT - My GPTs](https://chatgpt.com/gpts/mine)
2. 点击 "Create a GPT"
3. 切到 "Configure" 标签
4. **Name**: `thesis-helper`
5. **Description**: 学生论文写作一站式工作流
6. **Instructions**: 把 `thesis-helper-gpt-instructions.md` 内容复制粘贴进去
7. **Conversation starters**（建议 4 个）：
   - 我要写本科毕设
   - 我要写期刊论文
   - 帮我做答辩 PPT
   - 帮我降 AIGC 率
8. **Capabilities**: 打开 Code Interpreter（处理 .tex / .docx 必需）+ Web Browsing
9. **Knowledge**（可选）：上传 thesis-helper 整个目录的 zip

## 使用

进入你创建的 GPT，输入：

```text
我要写本科毕设
我的 LaTeX 文件附在下面（粘贴主要章节）
学校：北航
检测器：CNKI
```

GPT 会按 thesis-helper 工作流给出 LaTeX 修改建议、AIGC 降痕方案等。

## 平台限制（必读）

```text
1. 无文件系统访问 → 用户必须粘贴/上传文件
2. Code Interpreter 沙箱 → 可跑 Python (project-scanner / latex-to-word
   等需要在沙箱里手动重建)
3. Instructions ≤ 8000 字符 → 已自动压缩，关键章节保留
4. 长流程会话超时 → 7 步 aigc-reduce 建议拆 2-3 个对话跑
5. 无 sub-skill 嵌套 → 需要细节时 GPT 会引导用户去 GitHub 看完整 SKILL.md
```

## 知识库增强（推荐）

为了让 GPT 调用完整 sub-skill 内容：

1. 打 zip：`zip -r thesis-helper.zip thesis-helper/`
2. 在 GPT Configure 的 Knowledge 区上传
3. GPT 会自动检索完整 SKILL/README 文件

这样可以绕过 7500 字符限制，让 GPT 实际具备完整能力。

## 升级

```bash
cd /path/to/SKILL && git pull
python /path/to/thesis-helper/compilers/build.py --target chatgpt \
    --output thesis-helper-gpt-instructions.md
# 然后回 ChatGPT GPT 编辑页粘贴更新
```
