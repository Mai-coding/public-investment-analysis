# 05 - 估值方法论：可比主估值与终局参考 → Price Band Decision Map

本 skill 分析上市公司。主估值100%来自可比公司支持的 forward multiples，终局估值仅作零权重参考，并反推现价要求、核验条件。使用有限期限的倍数与总回报关系；不搭建逐年自由现金流折现、加权资本成本或永续增长模型。研究、近期经营预测、财务质量和来源治理保留。

核心输出保留 4–5 个 Price Bands、3 年回报、Risk/Reward、Actionability 和改变判断的条件。分别说明 **Market-priced Band（现价计入哪档）** 与 **Evidence-supported Band（证据支持哪档）**。Base midpoint 仅为参考。

## 1. 按经济属性选择主指标

| 类型 | 默认主指标 | 必须检验 |
|---|---|---|
| 银行、净资产可代表经营资本的重资产企业 | P/B；商誉重要时 P/TBV | 可持续 ROE/ROTCE、资产质量、资本约束、融资及摊薄 |
| 尚未盈利但收入有经济意义的企业 | P/S | 可服务市场、份额、成熟净利率、实现盈利的条件 |
| 具有代表性利润的其他企业 | P/E | 正常化利润、终局收入与净利率、壁垒持续性 |

先判断净资产法是否适用，再判断利润是否有代表性。晶圆厂不能仅凭固定资产多就套 P/B：检查工艺、利用率、经济折旧和维护投入。周期谷底亏损先检查正常化利润，不自动切 P/S。P/S 排除收入总额/净额错配；P/E 不用负数或接近零的分母；负净资产不强套 P/B。无可靠锚就披露无法可靠估值。

REIT 等有明确行业经济指标时保留 P/AFFO、P/NAV；多分部可 SOTP。其他倍数仅作有理由的交叉检验，不凑方法数量。直接采用整体股权P/E、P/S、P/B时，不再扣一次净债务或额外加现金；若明确使用剔除现金收益的核心盈利倍数，按第4节单列现金桥；EV 指标如确需采用，明确 EV→股权桥、租赁和少数股东口径。

## 2. 主估值：Forward Comps 100%

当前及预测市场快照按来源层级刷新。筛选至少 3 家经济属性相近的中央可比，比较商业模式、资本强度、成熟度、利润率/ROE、客户结构和增长持续性；异质全样本中位数只作零权重诊断，多分部用有依据的分部锚。每种主指标给中央子样本区间/中位数与目标公司的溢折价理由，不能由想要的价格倒推。龙头溢价的证据、可比内已含优势和避免重复加价按`06_comp_analysis_workflow.md`处理。

按统一 N+1（或有理由的 N+2）年度，将 peer-anchored P/E × 预测 EPS、P/S × 预测每股收入、P/B × 预测每股净资产转换为价格区间；同年度口径与摊薄股数来自 Task 2。每个经营情景都有对应指标和有依据的可比倍数，不能只复制一套固定价格折扣。最新披露 P/B 若替代 forward，必须标 Diagnostic，不冒充同年中央预测；缺可靠 forward book 时先补足或披露主估值未完成。

Manifest 的 `Method Family` 为 `Forward Comps`、`Terminal` 或 `Diagnostic`。Forward Comps 的 Central 权重合计 **1.00**；Terminal 必须为 `Role=Diagnostic`、`Weight=0`，其他诊断也为零。可比族内有理由时可细分，终局不参与主价格区间、Base中点或入场价的加权。缺可靠可比输入时停止最终主估值；缺终局输入则标参考未完成及原因，不用终局替代可比，也不阻断已有依据的主估值。

同一经营情景的主估值 low/mid/high 等于相应可比结果。在 `Valuation Summary` 的 `Band Valuation Bridge` 保留 Case、Comps Low/Mid/High、Terminal Low/Mid/High、Central Low/Mid/High；Terminal列为零权重参考，缺失时可标n.a.。Central三端须与Comps逐项相等，不允许终局输入通过公式进入主价格带。终局与可比显著分歧时解释期限、盈利定义和资本差异，不平均消除分歧，也不倒校可比倍数。

## 3. 零权重终局参考：延续经营预测

市场快照和可比遵守 `01_source_hierarchy.md`、`06_comp_analysis_workflow.md`。当前/近期主倍数采用同一明确基期（通常 N+1）；P/B 基数标明最新披露或同年预测；用于主估值的中央倍数须满足前述同年 forward 口径，不伪造数据。

先独立完成经营延续参考，再反推现价。默认从Task 2显性期末延续：各业务按自身增长依据逐年滚动，随成熟度逐步减速后相加，利润率、再投资、营运资本、现金和股本同步衔接。TAM×份额仅检查规模合理性，不重设收入终点；资产型企业衔接资本与可持续ROE。若采用其他终局方法须说明理由和与经营模型的差异。观察年仍高增长时，明确它不是永续稳定状态；不因年份较远就称已成熟。

`Terminal Cases` 位于原工作簿，记录 Case、Metric、Base Year、Current Price、Horizon、Required Return、Exit Multiple、Terminal Total、Terminal Shares、Distributions FV、Terminal Cash、Cash Treatment、Supported Price、Implied Terminal Total、Basis。每行按 `19_model_provenance_and_consistency.md` 记录来源、日期、定位和推导。

延续计算在原工作簿中链接Task 2末年，复用同一经营构建，不复制独立模型。减速幅度及费用/资本强度的保持或变化均须有依据；不把某家公司年份、增长率或净利率写成通用默认。

## 4. 终局正推与反推：统一有限期限关系

Terminal参考情景采用共同终局观察年，H 为距估值快照的年数；H 不等于三年持有期。要求回报 h 是投资门槛，不是已观察到的市场折现率。退出倍数 M_H 从成熟可比的质量、资本回报、增长余量及风险独立锚定，历史分位仅作诊断；不得由想要的价格反算。少量 H、h、M_H 情景均须有依据，不默认所有市场适用 10%。

令X_H为终局所选总量，S_H为终局摊薄股数，D_H为每股当前股份收到的中间股息等外部分配在H年的累积值；C_H为需单列的终局现金股权调整总额（已扣必要运营现金及债务，可为负），整体股权倍数已含现金时C_H=0：

```text
V_H = (X_H × M_H + C_H) / S_H
今天可支持价格 P* = (V_H + D_H) / (1+h)^H
现价要求终局总量 X_implied = {[P0 × (1+h)^H − D_H] × S_H − C_H} / M_H
当前倍数隐含要求：将 P0 = 当前倍数 × 同基期每股指标代入上式。
```

这是终局售价与持有期回报映射，不声称当前 multiple 唯一识别市场共识。H、h、退出倍数、分配均须展示，反推称“在这些假设下支撑现价的要求”。反推总量以零为下限；若现金与分配已覆盖门槛，说明无需正经营退出价值，不解释为负市场规模。计算可用 `scripts/terminal_multiple.py`；Excel 使用相同公式，图表只读模型输出。

- P/E：反推净利润，再除以可持续净利率得收入、除以行业收入得份额。
- P/S：反推收入，再核验成熟利润率。到 H 已成熟盈利时，退出 P/S 可由成熟 P/E × 成熟净利率得到；两者为同一估值，不可重复作为独立 Central 方法加权。
- P/B：反推净资产，结合可持续 ROE 得净利润；或固定可融资资本路径，求所需退出 P/B/ROE 条件组合。P/B 本身不唯一决定 ROE。检查留存利润、分红、资本补充与 S_H 一致，不把新股东投入免费算给原股东。

D_H 不得悄悄取零：采用简单有依据的分配假设，或标“零分配保守简化”及影响；分配重要时做敏感性。分红尊重现金与资本约束，不能全额分红又靠同一利润扩张净资产。S_H 纳入 SBC、期权、回购和必要融资；回购影响每股价值后不再计入 D_H。超额现金只能计一次；成功概率和等待时间分开，不重复惩罚同一风险。

现金处理必须二选一：`Cash Treatment=Included`表示整体股权倍数，`Terminal Cash=0`；`Separate`表示核心盈利倍数加独立现金调整，P/E分母先剔除对应税后利息并保留持续SBC，再加现金、合格金融投资减债务及运营储备。核心倍数须匹配剔现金定义，或明确近似及局限；不能无说明移用含现金的P/E。融资应收款不是现金。`Terminal Cash`是公司总额，不能塞入每股`Distributions FV`；现金已分配则从期末余额扣除。经营预测已承担研发、资本开支和营运资本，不能再扣同一笔再投资；对尚未明确用途的额外现金，可声明未来公允价值再投资净现值为零，不预先奖励再投资收益，也不对所有公司假设无限留存。

跨年份比较统一观察时点与回报门槛。分别列公司整体股权现值、每股现值及每股现值×较早年份股数的原股东等值；持续摊薄时三者不可混用。终局现金与分配桥随经营路径更新，反推采用同一套定义。

## 5. Price Bands 与方法清单

保留 Upside/Re-rating、Base+、Base、Disappointment、Thesis Impairment 等 4–5 档，按经营断点调整。各档100%来自同情景forward comps，列 `业务事件 → 预测每股经营指标 → 预期变化 → 可比倍数与价格`；终局只解释长期合理性与条件要求。盈利增长可能消耗剩余空间，不机械叠加盈利增长和倍数扩张。

`Terminal Cases` 情景区间可重叠；`Price Band Map` 为行动价格区间，按有依据的断点排列，不能把重叠情景强行一一对应，不能为了覆盖现价扩大估值。现价在带外或间隙时标 Above/Below/Between。市场隐含经营要求由反推表解释，不以价格位置证明公司已实现该状态。

保留原 band 字段，增加 `Evidence Status`、`Evidence Ref`。E/Multiple 拆分为算术解释；P/S/P/B 改用适用每股基数。股本、分配、期限或门槛变化另列贡献，不把所有残差归 multiple。价格带、Base midpoint 和 football field 均读取 Manifest Central 的模型来源。反推与同一估值的代数改写是零权重 Diagnostic；一种有依据的可比主指标足够就不凑数；不把不同情景作为独立方法平均。终局参考单独标零权重，不进入中央football field。

## 6. 条件验证与两种定位

在 `Valuation Summary` 增加 `Condition Evidence`：

| Band | Condition | Threshold | Current Evidence | Evidence Date | Source / Locator | Status | Decisive | Next Signal |
|---|---|---|---|---|---|---|---|---|

Status = Supported / Partial / Unverified / Contradicted；Decisive = Yes/No。复用已有研究，Threshold 可观察且有时间窗口。未来终局未实现不等于失败，区分领先证据与结果。缺证据保持未知，不把管理层愿景填为 Supported。

同页 `Decision Position` 两行：`Market-priced Band`、`Evidence-supported Band`，各含 Band、Confidence、Rationale。前者为价格位置与反推要求，后者为独立研究裁决；可用 Mixed/Unresolved。逐带 Evidence Status 汇总证据，Evidence Ref 定位条件表行/来源。决定性条件被反证，不能靠其他利好多认定该档受支持；若反证不适用，先解释并修正底稿。

Robustness 衡量推演稳定性，Confidence 衡量证据把握，发生概率另行表达；不互换，不强制精确概率。

## 7. 稳健性与实际行动

逐带 challenge 一次：Causality、Magnitude、Timing、Market Pricing、Counterforces，输出 High/Medium/Low 与修正记录。极端条件叠加为 Low 尾部压力，不是普通 Bear。

Distance：Low = 已有条件或 1–2 个正常季度证据可支持；Medium = 需要明显经营验证/重估；High = 需要多项重大突破或 thesis 改变。波动可越过任何带，Distance 不是到价时间预测。

每档给 Actionability、条件和上/下调信号。下跌先更新证据再判断加仓，上涨先看终局是否上修再判断减仓。Thesis 破坏后的低价只能 Conditional/Avoid，下沿不保证托底。Attractive entry 是证据仍支持 thesis 且达到声明门槛的最高买价，不机械取 Base 折扣；仓位还受组合集中度与可承受损失约束。

## 8. 三年回报与最终结论

保留 `3Y Return Bridge`。三年退出经营基数来自 Task 2，退出倍数反映届时剩余终局空间，不能把 H 年终局提前搬到第三年。退出价格与实际分配时点计算总回报：可用逐笔现金收益率，或声明分红再投资约定后算终值 CAGR。每股基数 CAGR + 股东收益率 + 年化倍数变化仅为近似解释，最终值须按总回报核对。P/S/P/B 使用每股收入/账面值，无正盈利不强算 EPS CAGR；回购不重复计。

至少展示 Base 与 Disappointment。结论包括两种 band 定位及 Confidence、Expected 3Y Return、Risk/Reward、Actionability、Attractive entry 和 2–3 个可观察更新信号。评级仍为 secondary；详细公式与来源进入底稿/Methods Appendix。
