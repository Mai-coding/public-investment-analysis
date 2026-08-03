# 04 - 图表清单与数据要求（按标的取舍）

本文件只负责**画什么、放在哪里、需要什么数据**。视觉样式、字号、色板、标签、轴和 QA 统一由 `09_visual_style_guide.md` 管理；字体实现由 `13_cjk_charts.md` 管理；产品实物图由 `17_product_images.md` 管理。

图表数量由标的实际数据决定，通常 14–20 张，不必凑数。缺少可靠数据时跳过，不得伪造。所有引用模型数字的图必须读取 Task 2/3 Excel 输出，不得在图表脚本中重算。

| # | 图表名 | 章节位置 | 数据要求 | 视觉规范 |
|---|--------|---------|---------|---------|
| 1 | 行业发展时间线 | 2.7 | 8–10 个关键节点 + 3 个代际 | Horizontal timeline；拥挤年份使用 3–4 车道/折行/拆图；必须过文字重叠 gate |
| 2 | 产业链 + 目标定位 | 2.8 | 3 层 × 2-3 个细分 | Layered card layout |
| 3 | 市场空间 (饼图 + 柱) | 6.1 | 覆盖率 + 火箭/行业市场预测 | Stacked bar + bar chart |
| 4 | 竞争格局评分矩阵 | 7.1 | 6-8 家 × 7 维度 (1-3 stars) | Heatmap, 维度在顶部；该图是 §7.1 唯一评分矩阵，正文只解读、不复制同款表格；DOCX alt text=`CHART_COMPETITION:` |
| 5 | 股价 + forward 倍数历史 | 11.0 | 5-15 个时间点 + 股价 + forward P/E/P/S | Line chart with annotations |
| 6 | 火箭 / 关键产品成本对比 | 5.2 | 5-8 家产品 + $/单位指标 | Horizontal bar chart, log scale 可选 |
| 7 | 核心用户增长曲线 | 4.3 | 8-15 个时间点 + 用户数 | Line chart with stage shading |
| 8 | ARPU + 市场份额对比 | 4.3 | 4 业务段 × ARPU + 市场份额 (今/未来) | Bar + grouped bar |
| 9 | 政府客户合同明细 | 8.3 | 8-15 个合同 + 金额 + 机构 | Horizontal bar with category color |
| 10 | 产品代际演进 | 4.2 | 4 代 × 3 维度 | Triple-axis bar chart |
| 11A | **收入结构与迁移（强制）** | 8.1 | 3–5 年历史 + 3–5 年预测 × 最有解释力的 segment/product/end-market；金额、占比、总额 | Stacked bar；DOCX alt text=`CHART_REVENUE_MIX:` |
| 11B | 财务预测与利润率 | 10.1 | 7 年 × 收入/利润率 | Stacked bar + line，必要时拆双面板 |
| 12 | 同赛道竞品扩张速度 | 7.4 | 5-7 年 × 5 家公司 | Grouped bar chart |
| 13 | Killer Risk 矩阵 | 13 | 10 风险 × (概率, 影响) | Scatter on 2x2 quadrant + leader lines |
| 14 | 5 维度评分雷达 | 15 | 5 维度评分 + 权重 | Polar/radar chart |
| 15 | 三情景目标价 / 上行空间 | 12 | 3 情景 × (目标价, 上行%) | Grouped bar chart |
| 16 | 创始人商业帝国（如适用）| 9.2 | 多家公司 × 估值 + 行业 | Horizontal bar |
| 17 | 生态位 2x2 矩阵 | 7.5 | 6-10 玩家 × (运力, 业务广度) | Scatter on 2x2 + leader lines |
| 18 | **价值链价值分布图（强制）** | 2.8 | 首选目标公司同口径分部收入/EBITDA/Capex与年份；缺披露时才用跨公司毛利率代理并标 Inference | Bar/stacked bar + value migration annotation；规格见 `recipes/18c_value_chain.md` |
| 19 | **市场分析总览图（强制）** | 6 | TAM/SAM/SOM 金额+口径来源+占比；增长驱动短/中/长各 3 条 | 双面板：左漏斗（SOM 文字放条外）+ 右三色带；副标题放"未计入的增量 TAM"；配方五 |
| 20 | **管理层档案卡（强制）** | 9 | 5-6 位高管 × (头像/姓名缩写、姓名、职务/任期、两行战绩) | 2×3 卡片网格；照片获取顺序与降级方案见配方六 |
| 21 | **可比公司角色与分部锚** | 11.2 | 每家可比角色、五维相似性、分部归属、forward P/E/P/S | Central 与 Diagnostic 分面；全样本统计明确标零权重诊断 |
| 22 | **中央估值 football field** | 12 | `Valuation Method Manifest` 中 Role=Central 的 low/mid/high | 只画中央方法；诊断中位数、先例锚、期权情绪锚不得出现 |
| 23 | **锁定期供给地图（条件触发）** | 11/12 | 释放日期/条件/股数、占流通盘、占20/60日ADV、价格门槛 | 时间轴+供给柱；确定量与条件股分开；标潜在支撑/压力而非确定预测 |

## 放置与选择规则

- “章节位置”只决定归属；图表插在其支撑的小节正文之后，不放在章节或小节开头。
- Chart 11A 为 §8 硬门槛，不得因已有 §10 财务图而省略。
- Chart 4 为 §7.1 唯一评分矩阵；本节正文用 3–5 段分析解释分数、trade-off 和反转条件，不再放重复矩阵表。
- Chart 18、19、20 分别受 `recipes/18c_value_chain.md`、`recipes/18e_market_overview_chart.md`、`recipes/18f_management_profiles.md` 约束。
- Chart 22 只能读取 `Valuation Method Manifest` 中 `Role=Central` 的方法。
- Chart 23 仅在存在实质锁定期/条件释放供给时触发。
- 完成后按 `09_visual_style_guide.md` 逐张检查并生成 contact sheet；最终人审见 `10_final_checklist.md`。


## Chart manifest and collision gate

- Every PNG is registered in `charts_manifest.json` with source IDs, source snapshot, owning section, model ranges, `overlap_check=PASS`, `visual_check=PASS` and DOCX alt text.
- Full source names/URLs do not appear inside the PNG. The report caption uses numeric superscript citations; provenance stays in the manifest and Sources Appendix.
- All annotation Text artists must pass `scripts/chart_text_overlap.py` at final output size. Timeline/chart labels that collide must be re-laid out or split.
