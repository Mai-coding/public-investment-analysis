# Section Specifications — Task Slice

> This is the authoritative task-specific slice of the public 16-section specification; no legacy monolith is required.
> Mechanical floors and required markers are owned by `scripts/depth_audit.py`; page and word ranges below are planning guidance only. Images/charts appear after the supporting subsection prose, never at the subsection opening.

## 第 11 章 估值与融资（3-4 页）

### 必含子节 checklist
- [ ] **11.0 过去 12 个月股价与预期归因**：总回报、关键拐点，以及盈利预期/估值倍数/政策监管/公司事件/技术资金面的证据链；使用 Task 1 后台诊断，不强行精确拆分
- [ ] 11.1 可比公司估值（含**数据快照日期段落**）⚠️
- [ ] 11.2 可比角色分类与分部估值锚（全样本统计仅作诊断；中央子样本至少3家经济属性相近）
- [ ] **11.3 市场已 price in 什么（reverse DCF 反推）** ⚠️ 必含 ⚠️
- [ ] 11.4 估值结论（明确高/低/区间内，须引用 11.3 的 priced-in 对照）
- [ ] 11.5 IPO/锁定期供给地图（上市三年内或仍有锁定安排时强制）

### 11.2 可比角色与中央估值锚

逐家公司标 `中央主锚 / 次级诊断 / 硬件或估值下限 / 期权参照`，并比较业务模式、资本强度、成熟度、利润率和客户结构。保留全样本 max/75th/median/25th/min，但异质样本全部为零权重诊断。多分部标的用分部可比 SOTP；中央子样本中位数至少需要三家经济属性相近公司。报告方法表、football field 与模型共同读取 `Valuation Method Manifest`。

### 11.3 市场已 price in 什么 ⚠️ 强制（比"目标价 vs 现价"更有判别力）⚠️

用 reverse DCF 从**当前股价**反推市场隐含假设，再与自己的判断对照：

1. 固定 WACC 与终值方法（与 Task 3 DCF 一致），反解出"要支撑现价，需要怎样的收入 CAGR × 终端利润率组合"。
2. 输出一张 **priced-in 对照表**：

| 变量 | 现价隐含 | 我的 Base 判断 | 差距 | 解读 |
|------|---------|---------------|------|------|
| 收入 CAGR (5y) | X% | Y% | ±pp | 市场比我乐观/悲观 |
| 终端净利率/FCF 利润率 | X% | Y% | ±pp | … |
| 隐含 forward 倍数 | X× | 选定中央锚 Y× | … | 全样本中位数仅作诊断 |

3. 结论必须回答：**当前价格买入，实际是在赌什么**；我的差异化判断（variant view）落在哪个变量上、置信度多高。

### 11.1 数据快照日期 ⚠️ 强制 ⚠️

每张可比公司表的上方或下方必须有数据日期段落：

```
数据快照日期：Yahoo Finance YYYY.M.D（美股）；
东方财富 YYYY.M.D（A 股）；HKEx YYYY.M.D（港股）；
研报机构 YYYY.M.D（forward 倍数预测）。
```

---

## 第 12 章 情景分析与目标价（4-6 页）

### 必含子节 checklist
- [ ] 12.1 forward P/E / P/S 倍数选择（可比分位）+ 调整逻辑
- [ ] 12.2 三情景目标价测算（Bull/Base/Bear，含 chart 5）
- [ ] 12.3 敏感性热力图（forward P/E × EPS 或 P/S × Revenue）
- [ ] 12.4 目标价对 forward growth / 倍数分位的敏感性
- [ ] **12.5 概率加权目标价 + 权重敏感性表** ⚠️ 每个情景必须有具体业务场景；权重敏感性表对**所有标的**强制（不限登月型）⚠️
- [ ] 12.6 催化剂时间轴
- [ ] 12.7 投资结论（6 条 bullet）
- [ ] 12.8 期权桶来源双表（仅当 Task 3 litmus 启用两层估值时强制）

### 12.8 期权桶来源双表（条件触发）

第一张表逐桶给 TAM/SAM 数值、数字上标来源、基准年/目标年、地域和口径边界、换算公式及重复计算检查；准确文件/文章名、发布方、日期、URL/本地路径和页码/章节只在 Source Ledger 与 Sources Appendix 展开。第二张表给成熟份额、退出 P/S、成功概率、兑现年数、折现率、low/base/high、理由、目标价敏感性和验证 KPI。逐项标 Fact/Inference/Assumption，禁止把 `research estimate` 当作来源名。

### 12.5 概率加权目标价情景的写法 ⚠️ 重要 ⚠️

每个情景**必须**包含一段具体业务事件链（causal chain）：

模板：
```
情景 X：[名称] (概率 X%, 目标价 $X / 上行 X%)

具体业务场景：(a) [触发事件 1]，公司 [影响 1]；(b) [触发事件 2]，
[影响 2]；(c) 次年实际收入 $X、净利 $Y、EPS $Z；(d) forward
倍数因 [事件影响估值的逻辑] 而 [上/下] 调至 X×；(e) 隐含目标价 $X，
相对现价上行/下行 X%。这一情景的关键导火索是 [核心风险]。
```

5 个情景必含场景：
- 极端下行
- 严重不及预期
- 保守
- 基准
- 乐观

每段约 100-150 字。

---


---

## 第 15 章 投资判断（1-2 页）

### 必含子节 checklist
- [ ] 15.1 5 维度评分（含 chart 14 雷达 + 评分表）
- [ ] 15.2 评分依据
- [ ] 15.3 投资结论（4 条明确决策）

---


---

## §11–§12 估值与目标价 —— 追加
**最低产出物**：过去 12 个月股价与预期归因；可比表（带快照日期）；倍数锚定逻辑（不反推）；**reverse DCF "市场已 price in 什么"分析**（见 11.4）；3 情景"业务事件链"；敏感性热力图 + **概率权重敏感性表**（所有标的强制）。
**预答追问**：①目标价的上行来自 E 还是 P/E？②下行地板是什么、在哪个价位？③当前股价已隐含（priced in）多激进的增速/利润率假设、与我的判断差多少？
