# Venue Router · 学校/期刊/会议规则路由

> 输入：`thesis.config.yml` 的 `venue` 字段
> 输出：加载对应 `school_rules.<key>` 覆盖默认 targets/integrations

## 决策树

```text
读 venue 字段
   │
   ├── 北航 / BUAA / Beihang        → school_rules.buaa_<level>
   ├── 清华 / Tsinghua              → school_rules.tsinghua_<level>
   ├── 北大 / PKU / Peking          → school_rules.pku_<level>
   ├── 复旦 / Fudan                 → school_rules.fudan_<level>
   ├── 上交 / SJTU                  → school_rules.sjtu_<level>
   │
   ├── IEEE_JOURNAL / IEEE_TRANS    → school_rules.ieee_journal
   ├── IEEE_CONF / ICASSP / ICRA    → school_rules.ieee_conf
   │
   ├── NeurIPS                      → school_rules.neurips_conference
   ├── ICLR                         → school_rules.iclr_conference
   ├── ICML                         → school_rules.icml_conference
   ├── CVPR / ICCV / ECCV           → school_rules.cv_conference
   ├── ACL / EMNLP / NAACL          → school_rules.nlp_conference
   ├── AAAI                         → school_rules.aaai_conference
   │
   └── 未匹配                        → 用默认值 + 警告用户
```

## 学校规则字段（覆盖优先级 > config.targets）

```yaml
school_rules:
  <venue_key>:
    # 必填
    venue_code: <official-name>          # 完整官方名

    # AIGC / 查重 阈值
    aigc_rate_max: <int>%
    duplicate_rate_max: <int>%
    aigc_hidden_redline: <bool>           # 学校是否隐含 AIGC 红线

    # 字数/页数
    word_count_min: <int>
    word_count_max: <int>
    page_count_max: <int>
    references_count_in_pages: <bool>     # 期刊用

    # 摘要
    abstract_word_limits:
      zh_chars_min: <int>
      zh_chars_max: <int>
      en_words_min: <int>
      en_words_max: <int>

    # 投递格式
    require_word_submission: <bool>       # 国内毕设
    require_blind_review: <bool>          # 硕博毕设
    figure_format: <vector_pdf | png_300dpi>
    cite_style: <gb_t_7714 | ieee | acm | natbib | ...>

    # 自动化
    skip_aigc_reduce: <bool>              # 期刊跳过
    auto_generate_slides: <bool>          # 会议接收后必做
    auto_generate_poster: <bool>
```

## 别名表（用户友好输入）

| 用户写 | 解析为 |
|--------|--------|
| `北航` / `BUAA` / `Beihang University` | `buaa_<level>`（用 thesis_type 推 level） |
| `清华` / `Tsinghua` | `tsinghua_<level>` |
| `IEEE Trans` / `IEEE Transactions` / `IEEE_JOURNAL` | `ieee_journal` |
| `NeurIPS 2025` / `Neural Information Processing` | `neurips_conference` |
| `ICLR 2026` | `iclr_conference` |
| `CVPR 2026` / `ICCV` / `ECCV` | `cv_conference` |

匹配不区分大小写，去除空格/标点后比对。

## 加载顺序（优先级 高→低）

```text
1. config.school_rules.<key>            最高 — 用户在 config 显式定义
2. 内置 examples/<venue>-example.yml    第二 — 复制内置示例
3. 通用规范（GB/T 7713-2006 等）         最低 — 兜底
```

## 缺失情况处理

```text
venue == "西交利物浦" 等非内置学校
   → 触发交互：
     "我没找到 venue=西交利物浦 的内置规则。要不要：
      [1] 用 buaa_undergrad 作为模板生成 + 让你修订
      [2] 从 <project>/格式要求/ 自动解析（如有 PDF/Word 模板）
      [3] 手动定义 school_rules.xjtlu_undergrad（我给你模板）
     "
```

## 与 intent-router / detector-router 的关系

```text
intent-router (论文类型) → 决定 pipeline 文件
   │
   ├── 委托 venue-router (本文件) → 加载学校规则
   │      └── 覆盖 targets / integrations / extensions
   │
   └── 委托 detector-router → 选 detector adapter
```

## 内置学校规则示例（thesis.config.template.yml 已含部分）

- ✅ buaa_undergrad
- ✅ tsinghua_master
- ✅ ieee_journal
- ✅ neurips_conference
- ✅ iclr_conference
- 🚧 待补：pku / fudan / sjtu / hkust / nus / cv_conference / nlp_conference

欢迎 PR 添加更多学校 / venue 规则到 thesis.config.template.yml 的 school_rules 区段。
