# 01 - 信源优先级 + Fact 标签规范

## 信源优先级（从高到低）

1. **用户提供的任何文件**
2. **监管文件 + 招股书 + 年报 + 财报电话会**（SEC EDGAR、HKEx、巨潮、ESMA；earnings call transcript 属一手管理层口径，但前瞻性陈述标 management claim）
   - 招股书仅用 2020 年及以后版本
   - 研究范围按对象区分：target = 3 年报 + 2 季报 + 5 transcripts；4-5 家 competitors = 各 1 年报 + 2 季报 + 2 transcripts；上下游各 1-2 家龙头 = 各 1 年报 + 1 季报 + 1 transcript。
3. **Yahoo Finance / yfinance（一线市场数据）**：实时价格、市值、forward revenue/EPS、forward P/E、forward P/S；每次重拉并标快照日期。
4. **公司官网 + IR 官方材料**：产品、技术、新闻稿、财报演示、webcast 与 transcript。
5. **专业数据与研报兜底**：yfinance 缺字段时，先用 IR/最新财报自算，再使用专业数据 MCP 或用户研报 consensus；明确标实际渠道和数据日期。
6. **定性/叙事研究**：逐行执行 `source_registry.json` 的唯一渠道名单；指定优先渠道先做相关性扫描，再进入咨询、研究机构、媒体与 KOL。

> **唯一渠道真源**：渠道增删、名称和强制程度只维护在 `source_registry.json`。本文件只定义可信度和使用规则，其他工作流不得复制完整名单。

视频 / 播客内容标 **专家观点（analyst-opinion 类，非 Fact）**；与一手文件冲突时以一手文件为准。需要引用具体数字时回溯其一手来源再改标 Fact。

## 信源使用规则

- **不允许臆测**：凡无可靠来源支持的数字或结论，一律标注"未知/未披露"，并说明如何验证
- **不得伪造已查阅文件**：未找到就明确写"未获取到/无符合条件文件"
- **信息冲突时必须显式说明**，并统一时间口径、地域口径、市场口径
- **若发现新信息影响前文结论**，必须更新前文，不得只在后文补充
- **市场预测 vintage**：第三方市场规模/增长/渗透率等**预测**数据优先用**发布日期 ≥ 2025-01-01** 的版本，引用必标报告发布日期；旧 vintage（2024 及更早）仅在确无更新版本时用，并显式标 stale + 说明。
- **建模假设须锚一手披露**：每个价格/单价/利润率假设先在一手 filing 找锚（10-K 常披露 hub 价/实现价/全成本/对冲均价/清算量价）再 calibrate；calibrate-to-guidance 须标为 plug。详见 `task2-financial-modeling.md`。
- **最终来源名必须可定位**：研究工作底稿、模型 Comments、`source_ledger.json` 和 Sources Appendix 必须保存准确文件名或网络文章名、发布方、日期、URL/本地路径及页码/Item/章节/时间戳。**最终 DOCX 正文不展开这些信息，只用数字上标，格式以 `20_citation_and_source_appendix.md` 为准。**`research estimate`、`company commentary`、`filing`、`web research` 只能描述判断性质，不能作为唯一 Source。
- **申报文件按用途引用**：S-1/F-1 支持上市前业务、风险与拟议条款；424B4 是最终招股说明书，最终发行价、发行股数、承销、募资、超额配售和锁定期优先引用 424B4；10-K 支持年度经审计数据；10-Q 支持最新季度变化；8-K 支持重大事件和附件。后续修订/定期报告与早期文件冲突时，使用更新文件并解释差异。
- **Derived 数字写推导链**：同时给准确原始来源、定位信息、分子、分母、公式、年份和单位；不得只写“作者测算”。完整模型字段见 `19_model_provenance_and_consistency.md`。

## Fact 4 类标签（研究工作底稿/模型/Source Ledger 使用）

每个关键陈述在工作底稿中必须标注其中一类；最终 DOCX 转为自然语言 + 数字上标，不直接展示这些模板标签：

### Fact （事实）
**定义**：一手来源直接支持
**标注格式**：`Fact：[陈述]。来源：[BP 第 X 页 / SEC 10-K Item Y / Yahoo Finance 2026/5/8]`
**示例**：
- "Fact：截至 2025 年 11 月，Starlink 全球用户 800 万（来源：SpaceX BP 第 27 页）"

### User-provided but unverified（用户/BP 声明但未独立验证）
**定义**：用户或 BP 中写明，但当前模型未独立来源验证
**标注格式**：`Company disclosure / management claim, not independently verified`
**示例**：
- "Starshield 卫星制造毛利率 80%+（公司管理层口径，未独立验证）"

### Assumption（测算假设）
**定义**：本报告测算所使用的假设
**标注格式**：`Assumption：[假设值]。区间：[low - high]。理由：[逻辑]。敏感性：[影响范围]`
**示例**：
- "Assumption：保守情景 SpaceX 2030 用户数 1.5 亿。区间：1.2-1.8 亿。理由：MS 基准 3.6 亿打 4 折反映 DTC 不及预期。敏感性：每减 1,000 万用户对应基准估值下修 ~3%"

### Inference（推导结论）
**定义**：基于多个 Fact + Assumption 推导得出
**标注格式**：`Inference：[结论]。Based on：Fact A + Fact B + Assumption C`
**示例**：
- "Inference：SpaceX 在卫星互联网市场属于近独占。Based on：Starlink 800 万用户 (Fact) + Kuiper 2025 仅 153 颗 (Fact) + 中国玩家受地缘隔离 (Inference)"

## 两条硬规则（最易漏，交付前必查）

### 工作底稿中每个 `Fact：` 句必须紧跟完整来源
凡以 `Fact：` 开头的句子，**必须**紧跟一个 `来源：` 标注或下方 NOTE——没有来源的"事实"一律视为未验证。最易漏的是市场集中度 / 份额类（如 §7.4 "CR3 = 53%"）。

```
Fact：2024 年全球硅光芯片市场 CR3 = 53%。
来源：Silith BP 2026.4 第 6 页表格 + LightCounting 2024 + 自下而上推算。
```

### 每个市场/可比数据点必须带日期；最终正文用数字上标，Sources Appendix 保存完整快照
- 任何市值 / 股价 / 倍数（如"Credo 市值 $31.8B"）**必须注明是哪一天的价格**，否则不可用。
- 可比公司章（§11）**必须有一段"数据快照日期"**，逐渠道列日期，工作底稿/Source Ledger 记录完整明细；最终可比表附近用数字上标，Sources Appendix 展开：

```
数据快照日期：Yahoo Finance 2026.5.14（美股 CRDO/COHR/ALAB）；
东方财富 2026.4.16-30（A 股 688498/688313/300308/300502/002281）；
高盛研报 2026.4.27（中际旭创 / 新易盛 forward P/E 预测）。
```

> 交付自检见 `10_final_checklist.md` 的分析与估值一致性检查。

## 工作底稿 / Sources Appendix 引用规范

| 来源类型 | 引用格式 |
|---------|---------|
| 附件（用户 BP） | `BP 第 X 页` 或 `BP 第 X 页 + 第 Y 页` |
| SEC 文件 | `[公司] [S-1/424B4/10-K/10-Q/8-K] [日期或FY] [页码/Item/章节]` |
| 年报/招股书 | `[公司] 招股书 [年份] 第 [章] 节` |
| 专业数据 MCP | `[渠道名] [日期]`（如 `FactSet 2026.6.10` / `Capital IQ 2026.6.10`）|
| 财报电话会 | `[公司] Q[X] FY[年] Earnings Call [日期]`（引用具体发言时加 发言人 + @[mm:ss]）|
| Yahoo Finance | `Yahoo Finance [日期]` |
| 公司官网 | `[公司] 官网 [日期]` |
| 媒体 | `[媒体名] [日期] "[标题]"` |
| 研究机构 | `[机构] [报告名] [日期]` |
| 播客 | `[节目名]《[单集标题]》[日期] @[mm:ss]` |
| 视频 | `[频道名]《[视频标题]》[日期] @[mm:ss]` |
| A 股招股书 | `[公司] 招股说明书 [日期] 第 [章] 节` |
| 港股年报 | `[公司] [年份] Annual Report Item [号]` |
