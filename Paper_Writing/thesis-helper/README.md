# Thesis Helper · 学生论文写作一站式工作流

> **造福学生群体**：一个 skill 包，跨 AI 通用，告诉它项目目录在哪，自动写论文 + 降 AIGC + 闭环验证。

## ✨ 一句话价值

```
告诉我： 你的工程目录 + 论文类型 (期刊 / 本科毕设 / 硕士毕设)
我交付： LaTeX 源 + PDF + (可选) AIGC 降痕版 + 检测报告
```

不要求你整理"数据/结果"目录——**主动扫描** + **自动配置** + **端到端闭环**。

---

## 🎯 它解决什么问题

学生写论文的真实痛点：

1. **不知道用什么 skill** —— Claude/Cursor/Gemini 各家 skill 系统不一样，一头雾水
2. **数据和代码混在一起** —— 没有"论文项目"专门目录，全是 `train.py / results/` 散在 repo 里
3. **格式要求文档难塞** —— 每个学校/期刊一套模板，手动复制粘贴
4. **降查重 vs 降 AIGC 分不清** —— AI 写的查重天然低，但 AIGC 检测器（CNKI）会标红
5. **跨 AI 不通用** —— 学生今天用 Claude，明天换 Cursor，skill 要重新学

本 skill 把这 5 个痛点全部闭环。

---

## 📦 包含什么

```
thesis-helper/
├── SKILL.md                     ← 顶层入口（Claude 直接读这个）
├── README.md                    ← 你正在看的文件
├── thesis.config.template.yml   ← 项目配置模板（用户复制到自己项目根目录）
│
├── routers/                     ← 路由逻辑（论文类型/期刊/检测器）
├── scanners/                    ← 项目扫描器（数据代码混合目录）
├── compilers/                   ← 跨平台编译器（Claude → Cursor/Gemini/...）
├── detectors/                   ← AIGC 检测器适配（CNKI 已通，其他占位）
├── pipelines/                   ← 三种论文类型的详细 pipeline
├── platforms/                   ← 各 AI 平台的安装目标
└── examples/                    ← 三种论文类型的 config 示例
```

---

## 🚀 安装

### 前置依赖

本 skill 调用以下两个已有 skill 包，请先确认安装：

1. **paper-writing**（必装）—— [`../PaperWriting/`](../PaperWriting/)
2. **aigc-reduce-skills**（毕设流程必装）—— [`../aigc-reduce-skills/`](../aigc-reduce-skills/)

### 各 AI 平台安装方法

#### 🤖 Claude Code

```powershell
# Windows
Copy-Item -Recurse C:\path\to\thesis-helper $env:USERPROFILE\.claude\skills\

# macOS / Linux
cp -r /path/to/thesis-helper ~/.claude/skills/
```

重启 Claude Code，输入 `/thesis-helper` 即可。

#### ✂️ Cursor

```bash
python compilers/build.py --target cursor --output <your-project>/.cursorrules
```

会在你的项目根目录生成 `.cursorrules`，Cursor 自动加载。

#### 💎 Gemini CLI

```bash
python compilers/build.py --target gemini --output <your-project>/GEMINI.md
```

会在你的项目根目录生成 `GEMINI.md`，Gemini CLI 自动激活。

#### 🌊 Cline / Continue

```bash
python compilers/build.py --target cline --output <your-project>/.clinerules
```

#### 🌐 通用方案（任意 AI）

不会用上面任何一种？没关系：

```bash
python compilers/build.py --target universal --output thesis-prompt.md
```

生成一个 `thesis-prompt.md`，你打开任意 AI 聊天框（ChatGPT / Claude.ai / 文心 / 豆包），把内容复制粘贴，再告诉它你的项目目录，就能用。

---

## 🎬 使用

### 第一步：在你的论文项目根目录放一个 config

参考 [`thesis.config.template.yml`](thesis.config.template.yml)，复制到你的项目根目录，改两三个字段：

```yaml
thesis_type: undergrad-thesis    # 三选一：journal | undergrad-thesis | master-thesis
venue: 北航                       # 学校名 / 期刊名
language: zh                     # zh 中文 / en 英文
detector: CNKI                   # CNKI 知网 / Turnitin / PaperPass / VIPCS / none
```

### 第二步：（可选）放一个"格式要求/"文件夹

如果你的学校/期刊给了 LaTeX 模板、Word 模板、字数要求文档：

```
你的项目/
├── 格式要求/                  ← 放这里
│   ├── thesis_template.tex
│   ├── 字数要求.md
│   └── 评分标准.pdf
├── train.py                  ← 你的代码
├── results/exp1.csv          ← 你的数据
└── thesis.config.yml         ← 配置
```

skill 会自动扫描，提取约束注入到论文写作流程。

### 第三步：跑

**Claude Code 用户**：
```text
/thesis-helper D:\my-thesis-project
```

**其他 AI 用户**：
```text
我要用 thesis-helper，我的项目目录是 D:\my-thesis-project，请开始
```

---

## 🧠 三种论文类型 · 三条 pipeline

| 类型 | 调用链 | 检测器 | 默认阈值 |
|------|-------|-------|---------|
| 期刊论文 | `/paper-writing` | Turnitin (可选) | 跳过 AIGC 降痕 |
| 本科毕设 | `/paper-writing` → `/aigc降低` | CNKI | AIGC < 8% / 查重 < 8% |
| 硕士毕设 | `/paper-writing` → `/aigc降低` (严格) | CNKI | AIGC < 5% / 查重 < 5% |

阈值可在 `thesis.config.yml` 的 `targets:` 字段覆盖。

---

## 🔍 智能项目扫描

不要求你单独整理数据和代码。skill 自动识别：

| 资产类型 | 自动识别规则 |
|---------|-------------|
| 工程代码 | `.py` `.cpp` `.m` `.ipynb` `.cu` 等 |
| 数据文件 | `.csv` `.json` `.npz` `.h5` `.mat` 等 |
| 图表源 | `figs/` `figures/` 下的脚本和图片 |
| 实验日志 | `logs/` `wandb/` `runs/` 下的日志 |
| 已有写作 | `.tex` `.md` `.docx` |
| 参考文献 | `refs/` `references/` 或 `.bib` `.enl` |
| 格式要求 | `格式要求/` `format/` `template/` |

扫描结果存在 `<project>/.thesis-helper/project_map.json`。

---

## 🔌 检测器接口（v0.1 状态）

| 检测器 | 状态 | 说明 |
|--------|------|------|
| ✅ CNKI 知网 | **生产可用** | 已通过 aigc-reduce v3 实测 (15.1%→2.8%) |
| 🟡 Turnitin | 接口预留 | 海外期刊主流，待实测数据 |
| 🟡 PaperPass | 接口预留 | 国内备查，算法相近 CNKI |
| 🟡 维普 VIPCS | 接口预留 | 部分高校使用 |

每个检测器有独立的 `detectors/<name>/adapter.md`，定义检测规则、降痕策略、阈值映射。后续基于实测数据迭代填充。

---

## 🛡️ 学术伦理（写在前面）

**论文绝不上传任何外部服务。** 所有处理 100% 本地：

- AIGC 检测：本地 Hello-SimpleAI 模型 + 人工 CNKI 上传（用户自己上传）
- AI 写作：调用你已配置的 AI（Claude/GPT/Gemini）
- 数据：始终在你的本地磁盘

skill 不会把你的论文发送到任何遥测端点。

---

## 🤝 贡献

欢迎 PR：
- 新增检测器适配 → `detectors/<name>/`
- 新增 AI 平台编译目标 → `compilers/targets/`
- 新增学校规则集 → `examples/`

---

## 📜 License

MIT — 随便用，造福学生群体。

---

## 关联仓库

- 上游：[daidaoayue/SKILL](https://github.com/daidaoayue/SKILL)
- 同级：
  - [`../PaperWriting/`](../PaperWriting/) — paper-writing 9 个 skill
  - [`../aigc-reduce-skills/`](../aigc-reduce-skills/) — aigc-reduce 8 个 skill + CNKI 实战经验
