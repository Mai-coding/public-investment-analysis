# 19 - 模型来源治理、估值清单与全局一致性

本文件是 Task 2-5 的共同硬规范。凡模型、估值、图表或报告发生联动修改，均先读本文件。

## 一、就地来源治理与模型页结构（必须执行）

工作簿不得包含 `Assumption Guide` 或 `Source Library`。治理信息不再集中在两个独立 tab，而是与假设同行记录：

1. `Revenue Model`
2. `Calculation Support`（独立、可见、紧随 Revenue Model）
3. 其他经营模型页与估值页

`Revenue Model` 最右侧固定为 `Comments`，每个可见非空模型行都填写。详细计算、中间变量、历史量价反推、合同去重、年度桥接和公式诊断进入 `Calculation Support`；不得将 support 行隐藏在 Revenue Model，也不得把展示层和中间计算混排。

### Comments 最低字段

采用可解析的单行 schema：

`Class=<Fact|Inference|Assumption|User-provided-unverified|Derived>; Source=<准确文件名或网页标题>; Date=<YYYY-MM-DD>; Locator=<页码/Item/章节/URL/时间戳>; Basis=<公式、推导或校准逻辑>`

| 字段 | 要求 |
|---|---|
| Class | 区分事实、推断、假设、用户文件与派生计算 |
| Source | 最终引用的准确文件名或网页标题；不得只写渠道名 |
| Date | 来源发布日期；动态市场数据另在 Basis 写 snapshot date |
| Locator | 页码、Item、章节、表名、URL或时间戳，确保可复核 |
| Basis | 公式、推导链、校准逻辑、区间与关键验证指标 |

`Derived` 行可写 `Source=N/A; Date=N/A; Locator=N/A`，但 `Basis` 必须给出公式或汇总逻辑。事实、推断和假设必须有准确来源、日期与定位。禁止把 `research estimate`、`company commentary`、`filing`、`web research` 等泛化词作为唯一来源。

不要给每个单元格添加 Excel Note。行级 Comments 是默认治理载体；只有跨行难以解释的复杂或例外计算才添加单元格 Note。

## 二、申报文件引用分工

- `S-1/F-1`：上市前业务、风险、历史财务和拟议发行结构；发行条款仍可能变化。
- `424B4`：最终招股说明书。最终发行价、发行股数、承销折扣、募资额、超额配售、锁定期和条件释放优先引用本文件。
- `10-K`：年度经审计财务、业务、风险和分部口径。
- `10-Q`：最新季度变化、年内财务和流动性。
- `8-K`：重大事件、业绩附件、协议和临时披露；若与后续 10-Q/10-K 冲突，以后者及修订文件为准。

首次出现 `424B4` 时用一句话解释其为向 SEC 提交的最终招股说明书，并说明它为何覆盖 S-1 的拟议发行条款。

## 三、Excel 格式硬规则

- 所有已填充单元格字体为 `Arial`；这是 Excel 全局规则，不改变 DOCX 或中文图表字体。
- 行标题或列标题含 `Growth`、`YoY`、`CAGR` 的指标区域统一用百分比格式（推荐 `0.0%`）；包括首年因无可比基期而为空白的单元格。
- 输入蓝、公式黑、跨表链接绿、错误红；颜色不得代替 Comments 的来源记录。
- 公式不得出现 `#REF!`、`#DIV/0!`、`#VALUE!`、`#N/A`；资产负债表 Balance Check 必须为 0 或在模型设定容差内。

## 四、Valuation Method Manifest（唯一估值方法清单）

在 `Valuation Summary` 建立可机器读取的表，标题精确写为 `Valuation Method Manifest`，字段至少包括：

| Method ID | Method Label | Role | Low | Mid | High | Weight | Source Range / Formula | Notes |
|---|---|---|---:|---:|---:|---:|---|---|
| `VAL-DCF` | DCF | Central | … | … | … | …% | … | … |
| `VAL-COMP-ALL` | Full-universe P/S | Diagnostic | … | … | … | 0% | … | 异质样本 |

`Role` 仅允许 `Central` 或 `Diagnostic`。只有 Central 可以有正权重并进入中央区间、加权目标价、football field和DOCX中央估值表；Diagnostic 权重必须为 0。Comps、Valuation Summary、图表和报告全部读取该清单，不得各自维护方法名或区间。

## 五、全局影响矩阵

| 变更 | 必须重建/复核 |
|---|---|
| 可比公司、可比角色或中央子样本 | Comps、Valuation Summary、Manifest、football field、估值散点/表、DOCX §11-12/§15 |
| 估值方法、权重或目标价 | Manifest、情景表、football field、封面/摘要/§11-12/§15-16 |
| 经营模型数字或关键假设 | Excel全链、所有引用该数值的图表、DOCX表格与叙述、priced-in结论 |
| `assets/color_palette.json` | 全部图表重新生成并扫描旧色值 |
| 来源文件名、URL或定位信息 | Revenue Model/相关假设行 Comments、Calculation Support、source ledger / chart manifest；DOCX 正文仅数字上标，完整信息在 Sources Appendix |

每次迭代先制作本次变更的影响清单，再从 Excel → 全部相关图表 → DOCX 顺序重建；版本号递增。交付前扫描旧方法名、旧数值、旧来源/定位信息和旧色值，不得只改单张图或单一章节。

## 六、交付闸门

按顺序运行：

```text
python scripts/artifact_audit.py --excel <model.xlsx> [--report <report.docx>] [--prev <previous.docx>]
python scripts/depth_audit.py --stage final --in <report.docx> [--prev <previous.docx>]
```

`scripts/artifact_audit.py` 必须确认旧治理 tab 不存在、`Calculation Support` 可见且紧随 `Revenue Model`、Revenue Model Comments 可解析、收入流顺序正确、Arial/百分比/公式/估值年度一致。两道脚本均 PASS 后，再生成图表联系表逐张肉眼核对配色、标签、数据来源和football field。机器闸门验证模型结构与统一清单；人工闸门负责栅格图的视觉语义，二者不可互相替代。
