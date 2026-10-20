# 19 - 模型来源治理、估值清单与全局一致性

本文件是 Task 2-5 的共同硬规范。凡模型、估值、图表或报告发生联动修改，均先读本文件。

## 一、就地来源治理与模型页结构（必须执行）

工作簿不得包含 `Assumption Guide` 或 `Source Library`。治理信息不再集中在两个独立 tab，而是与假设同行记录：

1. `Revenue Model`
2. `Calculation Support`（独立、可见、紧随 Revenue Model）
3. 其他经营模型页与估值页

`Revenue Model` 最右侧固定为 `Comments`，每个可见非空模型行都填写。详细计算、中间变量、有披露支持的历史量价核验、合同去重、年度桥接和公式诊断进入 `Calculation Support`；不得将 support 行隐藏在 Revenue Model，也不得把展示层和中间计算混排。

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
- 模型视觉参考用户提供的机构模型格式，通用参数见 `assets/excel_model_style.json`：白底、Arial 8 pt 正文、10 pt 标题，紧凑缩进；深蓝仅用于必要标题，浅绿小计、浅蓝重点预测，少量横线，不铺满网格。数据右对齐、标签左对齐，期间居中。金额千分位、负数括号、零值短横；百分比通常 0%，需要辨别差异时用 0.0%。显示格式不改变真实数值。
- 标签列约 32–35、期间列 9–11、空隔列 1–2；历史与预测期间按时间对齐，以 A/E 区分。关闭网格线，多期表冻结表头和标签。默认行高约 13.5，必要时调整防截断；Comments 在最右侧用宽列/合理换行，复杂解释进入 Calculation Support，不把每行撑成大段文字。
- 只提取附件的视觉规则，不复制任何公司名称、数据、预测、公式、估值方法、整套 sheet 名或隐藏行列。保留本 skill 的工作簿顺序、可见 support、Comments、三表联动及 100%可比主估值及零权重终局参考结构；DOCX 与图表字体不受影响。
- 量价仅在财报有足够披露时采用，否则直接用增长率、占比或利润率。Revenue Comments 的 Basis 标 `Model=QuantityPrice|GrowthPercent|RevenueShare`，量价同时写 `Disclosure=...`。情景只对 Scenarios 的 Scenario Drivers 登记表中至多 5 个关键经济驱动变化，其他输入共享基准路径。

- 公式不得出现 `#REF!`、`#DIV/0!`、`#VALUE!`、`#N/A`；资产负债表 Balance Check 必须为 0 或在模型设定容差内。

## 展示层与计算层

模型原始单位、公式及全精度值保持不变。输出报告/图表时才按 `21_report_editorial_style.md` 换为万/亿、应用展示精度；正文与表格不能直接粘贴百万/十亿模型数。跨产物校验先归一单位，再按显示精度容差核对，不能把舍入尾差判成模型冲突。定义、对账、汇率、推导与精确决策阈值进入 Methods Appendix；正文保留关键假设和投资影响。

## 四、Valuation Method Manifest（唯一估值方法清单）

在 `Valuation Summary` 建立可机器读取的表，标题精确写为 `Valuation Method Manifest`，字段至少包括：

| Method ID | Method Label | Role | Low | Mid | High | Weight | Source Range / Formula | Notes | Method Family |
|---|---|---|---:|---:|---:|---:|---|---|---|
| `VAL-FWD-PE` | N+1 Forward P/E | Central | … | … | … | 100% | Comps! | 同年每股指标 × 中央可比锚 | Forward Comps |
| `VAL-TERMINAL-PE` | Terminal P/E reference | Diagnostic | … | … | … | 0% | Terminal Cases! | 经营延续与现金参考 | Terminal |
| `VAL-COMP-ALL` | Full-universe P/S | Diagnostic | … | … | … | 0% | … | 异质样本 | Diagnostic |

`Role` 仅允许 `Central` 或 `Diagnostic`。只有 Central 可以有正权重并进入中央区间、Base midpoint（仅参考）、Price Band、football field和DOCX中央估值表；Diagnostic 权重必须为 0。Comps、Valuation Summary、图表和报告全部读取该清单，不得各自维护方法名或区间。正推与反推是同一方法的两种用途，反推为零权重诊断；等价 P/S/P/E 改写不得重复加权，Forward Comps Central权重合计100%；Terminal必须Diagnostic且零权重。Band Valuation Bridge保留Comps、Terminal参考及Central三组端点，Central逐项等于Comps；更改终局不能通过公式改变主价格带或入场价。终局缺数据时参考列标n.a.，不能填零冒充计算结果。

## 五、全局影响矩阵

| 变更 | 必须重建/复核 |
|---|---|
| 可比公司、可比角色或中央子样本 | Comps、Valuation Summary、Manifest、football field、估值散点/表、DOCX §11-12/§15 |
| 终局延续、现金、倍数、门槛、期限、分配或股本 | Terminal Cases、Implied Expectations、零权重参考图及正文；核验主价格带/入场价未通过公式受终局影响；若据此修改可比判断，单列证据与修订理由 |
| 可比溢折价、近期每股指标、三年退出倍数或Price Band | Comps、Manifest、Band Valuation Bridge、Price Band Map、3Y Return Bridge、相关敏感性与football field、封面/摘要/§11-12/§15-16 |
| 条件证据、关键反证或置信度 | Condition Evidence、Decision Position、逐带证据状态、Actionability、摘要/§12/§15-16 |
| 经营模型数字或关键假设 | Excel全链、所有引用该数值的图表、DOCX表格与叙述、priced-in结论 |
| `assets/color_palette.json` | 全部图表重新生成并扫描旧色值 |
| 来源文件名、URL或定位信息 | Revenue Model/相关假设行 Comments、Calculation Support、source ledger / chart manifest；DOCX 正文仅数字上标，完整信息在 Sources Appendix |

每次迭代先制作本次变更的影响清单，再从 Excel → 全部相关图表 → DOCX 顺序重建；版本号递增。交付前扫描旧方法名、旧数值、旧来源/定位信息和旧色值，不得只改单张图或单一章节。

## 六、交付闸门

按 [Stage gates](23_workflow_and_state.md#stage-gates) 执行当前任务的检查。Task 2/3 完成模型检查及联动测试后进入图表阶段；图表完成视觉检查后再装配 DOCX，最后执行 Task 5 三项机器审计与人工终稿检查。

变更后按上述影响矩阵和 [Revision invalidation](23_workflow_and_state.md#revision-invalidation) 更新交接状态、版本和指纹。结构审计与人工视觉/经济判断各有分工，不能互相替代。
