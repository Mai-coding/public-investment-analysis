# Section Specifications — Task Slice

> This is the authoritative task-specific slice of the public 16-section specification; no legacy monolith is required.
> Mechanical floors and required markers are owned by `scripts/depth_audit.py`; page and word ranges below are planning guidance only. Images/charts appear after the supporting subsection prose, never at the subsection opening.

## 第 11 章 估值与融资（3-4 页）

### 必含子节 checklist
- [ ] **11.0 过去 12 个月股价与预期归因**：总回报、关键拐点，以及盈利预期/估值倍数/政策监管/公司事件/技术资金面的证据链；使用 Task 1 后台诊断，不强行精确拆分
- [ ] 11.1 可比公司估值（含**数据快照日期段落**）⚠️
- [ ] 11.2 可比角色分类与分部估值锚（全样本统计仅作诊断；中央子样本至少3家经济属性相近）
- [ ] **11.3 市场已 price in 什么（multiple 隐含终局要求）** ⚠️ 必含 ⚠️
- [ ] 11.4 估值位置结论（现价相对自身历史、中央可比锚与 11.3 priced-in 的位置；不给单一目标价）
- [ ] 11.5 IPO/锁定期供给地图（上市三年内或仍有锁定安排时强制）

### 11.2 可比角色与中央估值锚

逐家公司标 `中央主锚 / 次级诊断 / 硬件或估值下限 / 期权参照`，并比较业务模式、资本强度、成熟度、利润率和客户结构。保留全样本 max/75th/median/25th/min，但异质样本全部为零权重诊断。多分部标的用分部可比 SOTP；中央子样本中位数至少需要三家经济属性相近公司。报告方法表、football field 与模型共同读取 `Valuation Method Manifest`。

### 11.3 市场已 price in 什么 ⚠️ 强制 ⚠️

用当前价格及 P/E、P/S、P/B 等适用指标，按 `05_valuation_methodology.md` 的有限期限映射反推所需终局。先独立完成经营延续终局参考，再作现价诊断；现金与分配定义按方法owner。

展示共同观察年、门槛回报、成熟退出倍数、分配及未来股本假设；与研究终局在同一时间、币种与权益口径比较。底稿保留公式，不把条件反推称为唯一市场共识。

| 变量 | 支撑现价的条件要求 | 独立研究 Base | 差距 | 关键证据/瓶颈 |
|---|---|---|---|---|
| 终局净利润/收入/净资产（适用项） | … | … | … | … |
| 市场份额、成熟净利率或可持续 ROE | … | … | … | … |
| 未来摊薄股本与必要融资 | … | … | … | … |

回答：当前买入实际需要相信什么？现价计入哪档，研究证据支持哪档，差异在哪个变量、置信度如何？

### 11.1 数据快照日期 ⚠️ 强制 ⚠️

每张可比公司表的上方或下方必须有数据日期段落：

```
数据快照日期：Yahoo Finance YYYY.M.D（美股）；
东方财富 YYYY.M.D（A 股）；HKEx YYYY.M.D（港股）；
研报机构 YYYY.M.D（forward 倍数预测）。
```

---

## 第 12 章 Price Band 与情景（3-5 页）

规则 owner：`05_valuation_methodology.md`。Price Band 替代旧"三情景目标价 + 概率加权目标价"，不得在其之外再保留一套目标价章节。

### 必含子节 checklist
- [ ] 12.1 Forward comps主估值（100%）：同年每股指标×可比倍数，列明龙头/增长/质量的净溢折价；经营延续终局仅作零权重参考，给退出锚与期限、现金、门槛、分配及摊薄桥
- [ ] 12.2 Price Band 构建（4–5 带，非等宽；每带一条 causal chain；标注 E 贡献 vs 倍数贡献、`Fundamental deterioration` / `Multiple compression`）+ Chart 15 band ladder
- [ ] 12.3 敏感性热力图（可比倍数×近期每股适用指标；终局倍数×远期指标另画零权重参考，不能混成主估值）
- [ ] 12.4 Robustness Check 与 Distance to Band（每个主要带一行：Causality / Magnitude / Timing / Market Pricing / Counterforces → High/Medium/Low；修正记录一句话）
- [ ] **12.5 Price Band Decision Map + Condition Evidence + Decision Position + 3Y Expected Return Bridge** ⚠️ 必含 ⚠️
- [ ] 12.6 催化剂时间轴（标注各催化剂推动股价移向哪个 band）
- [ ] 12.7 投资结论（5 条：Market-priced Band 与 Evidence-supported Band（含 Confidence）/ Expected 3Y Return / Risk-Reward / Actionability 与 Attractive entry / What would change the conclusion）
- [ ] 12.8 期权桶来源双表（仅当 Task 3 litmus 启用两层估值时强制）

### 12.2 每带写法（约 60–100 字）

```
[Band 名] $X–Y（Distance: L/M/H；Robustness: H/M/L）
业务事件 → 预测每股经营指标 → 市场预期变化
→ 可比倍数及净溢折价依据 → 主价格带；终局仅为长期合理性参考。
条件证据状态与定位：已有支持/部分支持/未验证/反证；来源、阈值和下一信号。
驱动：E 贡献 ±a% / 倍数贡献 ±b%（Fundamental deterioration / Multiple compression / Both）。
```
需要多个极端事件叠加的带标为尾部压力情形（Robustness = Low），不写成普通 Bear case。

### 12.5 Price Band Decision Map ⚠️ 强制 ⚠️

正文须出现标题 `Price Band Decision Map`，并标出现价位置（▶ Market）及证据支持档位（◆ Evidence）；带外/间隙如实说明：

| Price Band | What the market is pricing | Fundamental condition / Evidence Status | Distance | Robustness | Actionability |
|---|---|---|---|---|---|

表后必须有 **Condition Evidence（条件验证表）**：Band、Condition、Threshold、Current Evidence、Evidence Date、Source / Locator、Status、Decisive、Next Signal；以及 **Decision Position（档位判断）**：Market-priced Band、Evidence-supported Band、Confidence、Rationale。研究裁决可为 Mixed/Unresolved；不能按利好数量或股价位置判档。一个决定性条件有反证，不能被其他利好抵消。

价格、含义与 actionability 全部动态生成。低价带若源于 thesis 被证伪，只能是 Conditional（写明需先验证的 KPI）或 Avoid。表下写 Attractive entry 价格与门槛回报。

紧接着给 `Expected 3Y Return` bridge（一行表即可）：适用每股指标 CAGR + 股东回报收益率 + 年化倍数变化 ≈ 3 年预期回报 CAGR；最终值按三年退出价格和分配时点计算，不能将长期终局提前兑现；Base 为主，附 Disappointment 路径。用每股口径时不重复加回购。

### 12.8 期权桶来源双表（条件触发）

按 `21_report_editorial_style.md`，下述统计边界、换算、去重检查与 Fact/Inference/Assumption 标签只保留在底稿及 Methods Appendix；正文两张表展示金额、预测年份、关键假设、情景范围与估值影响，用自然文字说明预测性质。第一张表逐桶给 TAM/SAM 数值、数字上标来源、基准年/目标年、地域和口径边界、换算公式及重复计算检查；准确文件/文章名、发布方、日期、URL/本地路径和页码/章节只在 Source Ledger 与 Sources Appendix 展开。第二张表给成熟份额、退出倍数、成功概率、兑现年数、折现率、low/base/high、理由、对零权重上行参考的影响和验证KPI，不把期权金额加进可比主价格带。逐项标 Fact/Inference/Assumption，禁止把 `research estimate` 当作来源名。

---


---

## 第 15 章 投资判断（1-2 页）

### 必含子节 checklist
- [ ] 15.1 5 维度评分（含 chart 14 雷达 + 评分表）
- [ ] 15.2 评分依据
- [ ] 15.3 投资结论（与 12.7 一致：市场计入与证据支持档位及置信度、3 年回报、Actionability、改变结论的条件；评级如保留仅作 secondary）

---


---

## §11–§12 估值与 Price Band —— 追加
**最低产出物**：过去 12 个月股价与预期归因；可比表（带快照日期）；forward 可比倍数与成熟退出倍数锚定（不从目标价格倒推）、100%可比的Band Valuation Bridge及独立零权重终局参考；终局正推与现价隐含要求对照、条件验证及两种档位判断；4–5 个 Price Band（causal chain + E/倍数拆分 + robustness + distance）；敏感性热力图；Price Band Decision Map + 3Y return bridge。
**预答追问**：①现价计入哪档、证据支持哪档、差距为何？②下跌到下一带是基本面恶化还是倍数压缩？③thesis 仍成立时，什么价位风险收益变得有吸引力？
