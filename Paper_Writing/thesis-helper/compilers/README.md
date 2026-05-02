# Compilers · thesis-helper 跨平台编译器

> 把 Claude SKILL.md 真源编译到各 AI 平台的对应入口格式。
> **底层逻辑：单一真源 + 多端编译**——只维护 thesis-helper/ 一份，发到 6 个平台。

## 6 个 target

| Target | 输出 | 平台 |
|--------|------|------|
| `claude` | `~/.claude/skills/thesis-helper/`（整目录） | Claude Code |
| `cursor` | `<project>/.cursorrules` | Cursor IDE |
| `gemini` | `<project>/GEMINI.md` | Gemini CLI |
| `cline` | `<project>/.clinerules` | Cline / Continue / Roo Code |
| `chatgpt` | `gpt-instructions.md`（≤ 7500 字符） | ChatGPT 自定义 GPTs |
| `universal` | `thesis-prompt-pack.md` | 任意 AI 复制粘贴 |

## 用法

```bash
# 单 target
python build.py --target cursor --output D:/my-project/.cursorrules
python build.py --target gemini --output D:/my-project/GEMINI.md
python build.py --target chatgpt --output gpt-instructions.md

# Claude 直接装到 ~/.claude/skills/
python build.py --target claude --install

# 一次编译全部 target 到一个目录
python build.py --target all --output-dir D:/my-project/dist/
```

## 文件结构

```text
compilers/
├── README.md          ← 本文件
├── build.py           ← 主入口（路由到 targets/<name>.py）
└── targets/
    ├── __init__.py
    ├── _common.py     ← 共享工具（frontmatter 解析、压缩等）
    ├── claude.py      ← 整目录复制
    ├── cursor.py      ← .cursorrules
    ├── gemini.py      ← GEMINI.md
    ├── cline.py       ← .clinerules
    ├── chatgpt.py     ← ChatGPT 7500 字符压缩版
    └── universal.py   ← 通用 prompt 包
```

## 设计原则

1. **单一真源**：所有平台输出从 `thesis-helper/SKILL.md` 派生。
   修改主 SKILL.md 后跑一次 build → 所有平台自动同步。

2. **target 模块独立**：每个 target 一个 .py，不共享状态。
   新增平台只加一个文件。

3. **不修改源文件**：build.py 只读不写源目录。

4. **平台限制硬约束**：
   - ChatGPT Instructions ≤ 8000 字符 → 用 `_common.compress_markdown()` 压缩
   - Cursor / Gemini / Cline 无字符上限 → 全文 + 平台特定 header/footer
   - Claude 是整目录复制 → 不损失任何信息

## 添加新平台

要支持新 AI 平台（如 Cody / Aider / Windsurf）：

```python
# compilers/targets/<new>.py
from . import _common

def build(source_dir, output_path, install=False):
    fm, body = _common.read_skill_md(source_dir)
    # ... 平台特定转换
    output_path.write_text(content, encoding="utf-8")
    return output_path
```

然后在 `build.py` 的 `SUPPORTED_TARGETS` 里加 `"<new>"`。

## 验证

每次修改 SKILL.md 后跑：

```bash
python build.py --target all --output-dir /tmp/thesis-helper-dist/
```

检查 6 个文件都生成了。
