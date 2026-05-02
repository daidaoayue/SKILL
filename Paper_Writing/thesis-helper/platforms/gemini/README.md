# thesis-helper · Gemini CLI 平台

## 安装

```bash
python /path/to/thesis-helper/compilers/build.py \
    --target gemini \
    --output D:/my-thesis-project/GEMINI.md
```

会在项目根生成 `GEMINI.md`。Gemini CLI 启动时自动加载该文件元数据。

## 触发方式

```bash
cd D:/my-thesis-project
gemini
```

进入 Gemini CLI 交互后输入：

```text
activate the thesis-helper skill, my project is the current directory
```

或直接：

```text
帮我写本科毕设
```

会自动激活 `thesis-helper` 跑流程。

## 工具映射

GEMINI.md 编译时已注入完整映射表：

| Claude | Gemini CLI |
|--------|------------|
| Read | read_file |
| Write | write_file |
| Edit | edit_file (or write_file) |
| Glob | list_files / search_files |
| Grep | grep / search_text |
| Bash | run_shell_command |
| Skill | activate_skill |

## 平台特性

- **Skill 系统**：Gemini CLI 原生支持 `activate_skill`，sub-skill 调用顺畅。
- **大上下文**：Gemini Pro 1.5 / 2.0 上下文极大，可一次处理整本毕设。
- **Multi-modal**：可直接读图（论文 figure 截图分析）。

## 依赖

- Gemini CLI（最新版）
- Python ≥ 3.9
- 其他依赖同 Claude 平台

## 升级

```bash
cd /path/to/SKILL && git pull
python /path/to/thesis-helper/compilers/build.py \
    --target gemini \
    --output D:/my-thesis-project/GEMINI.md
```
