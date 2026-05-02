# thesis-helper · Cursor IDE 平台

## 安装

```bash
python /path/to/thesis-helper/compilers/build.py \
    --target cursor \
    --output D:/my-thesis-project/.cursorrules
```

会在你的项目根目录生成 `.cursorrules`。Cursor 打开项目时自动加载。

## 触发方式

打开 Cursor 的 Composer (Ctrl+I)，输入：

```text
我要用 thesis-helper 写本科毕设，项目就是当前目录
```

或：

```text
@thesis-helper /thesis-helper .
```

## 平台特性

- **工具映射**：Cursor 用自家工具替代 Claude tool。
  - `Read` → 文件查看
  - `Write` / `Edit` → 文件编辑（带 diff 预览）
  - `Bash` → 内置终端
- **Agent 模式**：建议开启 Cursor Agent，让 AI 自主多步执行。
- **YOLO 模式**：跑 aigc-reduce / latex-to-word 这类长流程时建议开。

## 依赖

- Cursor ≥ 0.40
- Python ≥ 3.9
- 其他依赖同 Claude 平台

## 升级

```bash
cd /path/to/SKILL && git pull
python /path/to/thesis-helper/compilers/build.py \
    --target cursor \
    --output D:/my-thesis-project/.cursorrules
```

## 已知限制

- Cursor 不支持 Claude 的 Skill 工具（无 sub-skill 嵌套）。
  workaround：让 Cursor 直接读取 `thesis-helper/{integrations,extensions}/<name>/SKILL.md`
  并按其 pipeline 执行（cursor.py 编译时已注入此说明）。
