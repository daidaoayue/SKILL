# formula-derivation Integration Wrapper

> **包装的 skill**：`/formula-derivation` (structure and derive research formulas)
> **触发**：方法章 / 理论章 有公式推导需要整理 / 把散乱推导写成连贯方程组

## Input
```yaml
scattered_equations: <user-provided-formulas-or-notes>
assumptions: <list>
target_section: method | theory | analysis
output_lang: zh | en
```

## Output
```text
<project>/.thesis-helper/derivations/<section>/
├── derivation_chain.tex         # 完整 LaTeX 推导链
├── assumptions_table.md         # 假设清单
├── notation_table.md            # 符号表
└── verification.md              # 关键 step 单独验证
```

## thesis-helper 调用条件

```text
config.integrations.formula_derivation: true
   且 paper 中存在 ≥ 5 个 \begin{equation}
   →  Phase 4 (master-thesis) / Phase 4 (journal) 触发
```

## 触发流程

```text
1. 用户给散乱公式 + 思路
2. /formula-derivation 整理成连贯推导链：
   - 编号 (1) (2) (3) ...
   - 每步注明依据（假设 X / 引理 Y / 性质 Z）
   - 关键 step 用 \intertext{} 加文字解释
3. 输出 derivation_chain.tex 注入 sections/<section>.tex
4. notation_table.md 自动加到 nomenclature 区
```

## 何时使用

- ✅ 任何含数学推导的论文（信号处理 / 优化 / 控制 / 通信）
- ✅ 雷达毕设（Range-Doppler 推导、CFAR 推导）
- ✅ 通信毕设（容量上界推导、误码率推导）

## 与 proof-writer 的协作

```text
formula-derivation      整理推导链
   ↓ 关键 lemma/theorem 调
proof-writer            写严谨证明
   ↓ 都注入到
sections/theory.tex 或 method.tex
```

## 相关

- 同级：[`proof-writer-wrapper.md`](proof-writer-wrapper.md)
- pipeline：master-thesis / journal Phase 4
