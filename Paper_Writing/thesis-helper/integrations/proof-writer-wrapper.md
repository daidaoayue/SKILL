# proof-writer Integration Wrapper

> **包装的 skill**：`/proof-writer` (rigorous mathematical proofs for ML/AI theory)
> **触发**：理论章节有 theorem/lemma 需要严谨证明

## Input
```yaml
theorem_statement: <one-paragraph-formulation>
assumptions: <list>
proof_sketch: <high-level-idea>      # 可选；无则 AI 自由发挥
target_audience: ml_theory | applied_ml | engineering
```

## Output
```text
<project>/.thesis-helper/proofs/<theorem_id>/
├── theorem_with_proof.tex          # 完整 LaTeX (theorem/proof 环境)
├── proof_sketch_zh.md              # 中文思路（毕设用）
└── verification_checklist.md       # 假设 / 推导 / 边界条件 自查
```

## thesis-helper 调用条件

```text
config.integrations.proof_writer: true
   且 paper 含 \begin{theorem} 或 \begin{lemma} 或类似环境
   →  Phase 4 (master-thesis) / Phase 4 (journal) 触发
```

## 触发流程

```text
1. 用户提供 theorem 陈述
2. /proof-writer 输出完整证明（LaTeX）
3. 自动加入 sections/theory.tex
4. paper-writing 编译时验证证明排版
```

## 何时使用

- ✅ 硕博毕设的理论章
- ✅ 期刊投稿（理论充足度审稿必查）
- ✅ NeurIPS / ICLR 的理论 track
- ❌ 本科毕设（通常无需严谨证明）
- ❌ 工程类期刊

## 与 formula-derivation 的差异

```text
formula-derivation   把现有公式整理成清晰推导链
proof-writer         给 theorem/lemma 写完整数学证明
```

两者通常配合：先 formula-derivation 整理推导，再 proof-writer 加 theorem 证明。

## 相关

- 同级：[`formula-derivation-wrapper.md`](formula-derivation-wrapper.md)
- pipeline：journal / master-thesis Phase 4
