# thesis-helper · Claude Code 平台

## 安装

### 方式 1 · 自动装到默认位置

```bash
python /path/to/thesis-helper/compilers/build.py --target claude --install
```

会复制到 `~/.claude/skills/thesis-helper/`。重启 Claude Code 后，输入
`/thesis-helper` 即可触发。

### 方式 2 · 手动复制

**Windows (PowerShell):**

```powershell
Copy-Item -Recurse C:\path\to\thesis-helper $env:USERPROFILE\.claude\skills\
```

**macOS / Linux:**

```bash
cp -r /path/to/thesis-helper ~/.claude/skills/
```

## 验证安装

启动 Claude Code，在任意项目下输入：

```text
/thesis-helper D:\my-thesis-project
```

如果触发并开始扫描项目，说明安装成功。

## 平台特性

- **原生支持**：所有 Claude tool（Read/Write/Edit/Glob/Grep/Bash/Skill/Agent）可用。
- **零损失**：整个 thesis-helper/ 目录完整复制，所有 sub-skill 链接有效。
- **MCP 集成**：可配合 codex MCP 使用 paper-writing 全流程。

## 依赖检查

确保已安装：

- Claude Code CLI
- Python ≥ 3.9（scanner 需要）
- LaTeX 全套（paper-compile 需要）
- pandoc / tex4ht / libreoffice（latex-to-word 需要）

## 升级

```bash
cd /path/to/SKILL && git pull
python /path/to/thesis-helper/compilers/build.py --target claude --install
```
