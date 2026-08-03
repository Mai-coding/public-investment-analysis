# 05 - 估值方法论：Forward P/E / P/S 可比 + DCF → 12 个月目标价

本 skill 只分析**上市公司**。估值目的是得出一个有依据的 **12 个月目标价 + 相对现价的上行/下行空间** 和 BUY/HOLD/SELL 评级。执行步骤见 `task3-valuation.md`；公开包不附带通用长版估值教材，公式与方法只按本文件及 Task 3 的现行规则执行。

## 核心原则

1. **倍数偏好 forward P/E 与 forward P/S**——本 skill **不使用 EV/EBITDA、EV/Sales** 等 EV 类倍数。
2. **正推法，禁止反推**：先观察真实可比 forward P/E / P/S，再套到 target 业绩上算隐含价；绝不先定目标价再回算倍数。
3. **两条腿走路**：(a) 经角色筛选的可比公司 forward P/E / P/S（多分部用分部 SOTP）→ 隐含股价；(b) DCF → 隐含股价。两者交叉验证后加权出目标价。
4. **没有私募轮次 dilution、没有 MOIC/IRR、没有入场/退出估值；但上市公司 SBC、期权、摊薄股本与回购必须进入每股价值**——这些是私募/基金口径，本 skill 不用。上市公司用 **目标价 + 上行空间** 衡量回报。

---

## 第 1 步：拉可比公司 forward 数据（带快照日期）

每次都重新拉，不要用记忆中的数据。

**数据源优先级**：**一线走 Yahoo Finance / yfinance**。若 forward 收入、EPS 或倍数缺失，依次用公司 IR/最新财报自行计算、专业数据 MCP、用户研报 consensus 兜底。工作底稿与 Source Ledger 写明实际渠道和快照日期；最终 DOCX 使用数字上标。

yfinance 一线通道（可直接跑 `scripts/fetch_comp_data.py`）：

```python
import yfinance as yf
for ticker in comp_tickers:
    s = yf.Ticker(ticker); info = s.info
    forward_pe   = info.get('forwardPE')       # forward P/E
    forward_eps  = info.get('forwardEps')
    market_cap   = info.get('marketCap')
    # ⚠️ 次年收入预测不在 .info 里（info.get('revenueEstimate') 恒为 None，forward P/S 会静默失败）
    # 必须用 Ticker.revenue_estimate 属性（DataFrame，'+1y' 行 = 次年预测）：
    rev_est      = s.revenue_estimate          # index: 0q/+1q/0y/+1y
    rev_next     = rev_est.loc['+1y']['avg'] if (rev_est is not None
                       and not rev_est.empty and '+1y' in rev_est.index) else None
    forward_ps   = market_cap / rev_next if (market_cap and rev_next) else None
    rev_growth   = info.get('revenueGrowth')   # backward TTM 增速，仅参考；forward 增速用 rev_next/totalRevenue−1
    # 不取 EV / EBITDA / EV-EBITDA（本 skill 不用）
```

`rev_next` 拉不到时（小盘股/A股/港股常见），按 fallback：研报 consensus（标 User-provided-unverified）→ 自算（最新季报年化 × 增速假设，标 Assumption）。

A 股 / 港股：东方财富 / 巨潮 / HKEx（+ 用户研报的 forward 预测）。
记录数据快照日期段落（实际渠道 YYYY.M.D 美股；东方财富 YYYY.M.D A 股；HKEx YYYY.M.D 港股；研报机构 YYYY.M.D forward 预测）。

## 第 2 步：可比统计 + 套用倍数

- 每家公司先分类为中央主锚、次级诊断、硬件/估值下限或期权参照，并比较业务模式、资本强度、成熟度、利润率与客户结构。
- 全样本 **max / 75th / median / 25th / min** 必须保留；异质样本统计只能作零权重诊断。
- 只有至少三家经济属性相近的中央子样本，才可使用其 low/median/high 倍数。多分部 target 必须按分部选择可比锚并做 SOTP。
- 套到 target（来自 Task 2 模型的预测）：
  - 隐含价(P/E) = target 次年预测 EPS × 选定中央子样本 forward P/E
  - 隐含价(P/S) = Σ（target 分部次年预测收入 × 对应分部 forward P/S）/ 摊薄股数
- P/E 与 P/S 两条结果交叉验证；若分歧大，说明利润率与同业差异，需用陈述句解释取舍。

## 第 3 步：相对增速调整（forward PEG，可选）

当 target 与可比的 forward 增速差距大时，用 forward PEG 对齐：
```
PEG = 可比 forward P/E / 可比 forward 增速(%)
Target forward P/E = PEG × Target forward 增速(%)
```
仅在 target 与可比成熟度接近时有意义；差距过大时以 DCF 为主。

## 第 4 步：DCF 交叉验证

按 `task3-valuation.md` 做 DCF（WACC、终值、折现 → EV → 减净债 → 股权价值 ÷ 摊薄股数 → 隐含股价）。检查终值 < EV 的 60-70%。

## 第 4.5 步：Reverse DCF —— 市场已 price in 什么（强制）

DCF 建好后，把它倒过来用：固定 WACC 与终值方法，从**当前股价**反解出"要支撑现价需要怎样的收入 CAGR × 终端利润率组合"，并与自己的 Base 判断对照（输出 §11.3 的 priced-in 对照表，格式见 `sections/03c_valuation_sections_11_12_15.md` §11.3）。

- 这比"目标价 vs 现价"更有判别力：它直接回答**当前价格买入实际是在赌什么**。
- 结论必须落到 variant view：我与市场的分歧在哪个变量、置信度多高、什么数据能验证。

## 第 5 步：三情景目标价（Bull / Base / Bear）

不是退出 MOIC，而是三档**目标价**。每档组合两个变量：
1. 业绩（收入 / EPS）：保守 / 基准 / 乐观
2. 倍数区间：选定中央子样本或分部锚的 low / base / high；禁止用异质全样本分位

| 情景 | 业绩 | 中央倍数区间 |
|------|------|----------|
| 保守 | 偏低 | 选定中央锚 low |
| 基准 | 中位（与卖方/研报一致）| 选定中央锚 base |
| 乐观 | 偏高 | 选定中央锚 high |

## 第 6 步：reconcile → 目标价 + 上行空间

- 在 `Valuation Method Manifest` 登记所有方法；只给 Role=`Central` 的 DCF/可比/SOTP 分配权重，Diagnostic 权重为0，得到 low/base/high 与加权目标价。
- 上行空间 = 目标价 / 现价 − 1。
- **评级由上行空间决定**（映射表见 `08_scoring_framework.md`）；第 15 章评分作交叉支撑，冲突时以上行空间为准并解释分歧。
- 输出推荐：现价、12 个月目标价、上行/下行%、评级（BUY/HOLD/SELL）、priced-in 对照结论（第 4.5 步）、方法权重、3-5 个催化剂、3-5 个对目标价的风险。

## 第 7 步：敏感性表

固定基准业绩，看不同 forward P/E / P/S 分位对目标价与上行空间的影响：

| 中央倍数情景 | 隐含目标价 | 上行空间 | 评估 |
|---------|-----------|---------|------|
| Selected low | ... | ... | 偏保守 |
| Selected base | ... | ... | **基准** |
| Selected high | ... | ... | 偏乐观 |

让读者清楚看到：目标价对倍数假设的敏感程度。

## 第 8 步：结论必须明确

明确给出：基准目标价与上行空间；要让上行空间转正/达标需要多大倍数或业绩假设；当前是 BUY/HOLD/SELL。不要写"估值合理"这种含糊话。

## 常见错误（必须避免）

1. **反推法**：先定目标价再算倍数。
2. **stale 数据**：用记忆中的市值；必须每次重新拉。
3. **混淆 forward 与 backward growth**：估值看 forward。
4. **用 EV/EBITDA 或 EV/Sales**：本 skill 一律用 forward P/E / P/S。
5. **不做敏感性**：必须展示倍数假设的影响范围。
6. **P/E 与 P/S 互相矛盾却不解释**：必须说明利润率差异。
7. **异质全样本中位数作中央锚**：全样本统计只作诊断；中央子样本至少三家相近公司，多分部走SOTP。

## 业绩预测的拍法（次年 / 预测期）

```
预测 EPS 或收入 = 预计市场规模 × 预计市场份额 × 预计净利率（或单价×销量）
```
每个变量给保守/基准/乐观三档，并标 Assumption + 区间 + 理由 + 敏感性（口径见 `01_source_hierarchy.md`）。
