# rebuttal Integration Wrapper

> **包装的 skill**：`/rebuttal` (parse reviews + draft author response)
> **触发**：投稿后收到审稿意见 / NeurIPS-ICLR Author Response 阶段

## Input
```yaml
review_files:
  - reviewer1.md
  - reviewer2.md
  - reviewer3.md
  - meta_review.md            # AC / SAC 元审稿
paper_dir: <project>/paper/
char_limit: 5000              # 会议常见 5000 字符/审稿人
mode: journal | conference
```

## Output
```text
<project>/rebuttal/
├── response_to_reviewer1.md      # 逐条回应
├── response_to_reviewer2.md
├── response_to_reviewer3.md
├── response_to_meta.md
├── revised_paper_diff.md         # 修改追踪
└── rebuttal_compilation.pdf      # 最终上传版（PDF）
```

## thesis-helper 调用条件

```text
config.integrations.rebuttal: true
   且 thesis_type ∈ {journal, conference}
   →  Phase 8 (journal) / Phase 8 (conference) 触发
```

## 触发流程

```text
1. 用户上传/粘贴审稿意见
2. /rebuttal 自动按"审稿人 x 问题点"切分
3. 对每个问题：
   ├── 直面承认（"Reviewer raises a valid concern...")
   ├── 数据支撑（引 paper Section / Figure / Table）
   ├── 修改承诺（"In revised version, we...")
   └── 必要时拒绝（"We respectfully disagree because...")
4. 字符限制下自动压缩
5. 输出 PDF 兼容 OpenReview / CMT / HotCRP 上传格式
```

## 安全网（grounding）

- ❌ 绝不 fabricate 数据 / 引用不存在的 figure
- ❌ 绝不承诺做不到的实验
- ✅ 每条回应必须 ground 到 paper 已有内容或可执行修改

## 何时跳过

```text
thesis_type == undergrad-thesis     # 毕设无审稿
thesis_type == master-thesis        # 国内毕设无审稿（预审 ≠ 期刊审稿）
```

## 相关

- 同级：[`paper-reviewer-wrapper.md`](paper-reviewer-wrapper.md)
- pipeline：journal Phase 8 / conference Phase 8
