# 04 - 图表清单与数据要求（按标的取舍）

本文件只负责**画什么、放在哪里、需要什么数据**。视觉样式、字号、色板、标签、轴和 QA 统一由 `09_visual_style_guide.md` 管理；字体实现由 `13_cjk_charts.md` 管理；产品实物图由 `17_product_images.md` 管理。

图表数量由标的实际数据决定，通常 14–20 张，不必凑数。缺少可靠数据时跳过，不得伪造。所有引用模型数字的图必须读取 Task 2/3 Excel 输出，不得在图表脚本中重算。

| # | 图表名 | 章节位置 | 数据要求 | 视觉规范 |
|---|--------|---------|---------|---------|
| 1 | 行业发展时间线 | 3.7 | 8–10 个关键节点 + 3 个代际 | Horizontal timeline；拥挤年份使用 3–4 车道/折行/拆图；必须过文字重叠 gate |
| 2 | 产业链 + 目标定位 | 3.8 | 3 层 × 2-3 个细分 | Layered card layout |
| 3 | 市场空间 (饼图 + 柱) | 6.1 | 覆盖率 + 目标行业市场预测 | Stacked bar + bar chart |
| 4 | 竞争格局评分矩阵 | 7.1 | 6-8 家 × 7 维度 (1-3 stars) | Heatmap, 维度在顶部；该图是 §7.1 唯一评分矩阵，正文只解读、不复制同款表格；DOCX alt text=`CHART_COMPETITION:` |
| 5 | 股价 + forward 倍数历史 | 11.0 | 5-15 个时间点 + 股价 + 所选 forward 倍数 | Line chart with annotations |
| 6 | 关键产品成本对比 | 5.2 | 5-8 家产品 + 可比单位成本 | Horizontal bar chart, log scale 可选 |
| 7 | 核心用户增长曲线 | 4.4 | 8-15 个时间点 + 用户数 | Line chart with stage shading |
| 8 | ARPU + 市场份额对比 | 4.4 | 4 业务段 × ARPU + 市场份额 (今/未来) | Bar + grouped bar |
| 9 | 政府客户合同明细 | 8.3 | 8-15 个合同 + 金额 + 机构 | Horizontal bar with category color |
| 10 | 产品代际演进 | 4.3 | 4 代 × 3 维度 | Triple-axis bar chart |
| 11A | **收入结构与迁移（强制）** | 8.1 | 3–5 年历史 + 3–5 年预测 × 最有解释力的 segment/product/end-market；金额、占比、总额 | Stacked bar；DOCX alt text=`CHART_REVENUE_MIX:` |
| 11B | 财务预测与利润率 | 10.1 | 7 年 × 收入/利润率 | Stacked bar + line，必要时拆双面板 |
| 12 | 同赛道竞品扩张速度 | 7.4 | 5-7 年 × 5 家公司 | Grouped bar chart |
| 13 | Killer Risk 矩阵 | 13 | 有证据的风险发生可能性/影响；无可靠概率则用有定义的定性等级，不编精确百分比 | 2x2 定性矩阵或有数据的 scatter + leader lines |
| 14 | 5 维度评分雷达 | 15 | 5 维度评分 + 权重 | Polar/radar chart |
| 15 | Price Band ladder | 12 | Price Band Map 4–5 带 × (区间, 状态, actionability) + 现价线 + 证据支持档位标记 | Horizontal band ladder；带宽按实际区间，不等宽 |
| 16 | 创始人商业帝国（如适用）| 9.2 | 多家公司 × 估值 + 行业 | Horizontal bar |
| 17 | **竞争格局四象限坐标轴对比图** | 7.5（或 §7 解释竞争定位的小节） | 标的 + 相关直接对手/替代方案；两条有行业含义且可区分玩家的轴，定位证据及截止日期；详见下文 | 2x2 position map；DOCX alt text=`CHART_COMPETITION_QUADRANT:`；与 chart 4 互补，不重复综合评分 |
| 18 | **价值链价值分布图（强制）** | 3.8 | 首选目标公司同口径分部收入/EBITDA/Capex与年份；缺披露时才用跨公司毛利率代理并标 Inference | Bar/stacked bar + value migration annotation；规格见 `recipes/18c_value_chain.md` |
| 19 | **市场分析总览图（强制）** | 6 | TAM/SAM/SOM 金额+年份+占比；详细定义与来源按 `21_report_editorial_style.md` 及 `20_citation_and_source_appendix.md` 分流；增长驱动短/中/长各 3 条 | 双面板：左漏斗（SOM 文字放条外）+ 右三色带；副标题放"未计入的增量 TAM"；配方五 |
| 20 | **管理层档案卡（强制）** | 9 | 5-6 位高管 × (头像/姓名缩写、姓名、职务/任期、两行战绩) | 2×3 卡片网格；照片获取顺序与降级方案见配方六 |
| 21 | **可比公司角色与分部锚** | 11.2 | 每家可比角色、五维相似性、分部归属、所选 forward 倍数 | Central 与 Diagnostic 分面；全样本统计明确标零权重诊断 |
| 22 | **中央估值 football field** | 12 | `Valuation Method Manifest` 中 Role=Central 的 low/mid/high | 只画Forward Comps中央方法（合计100%）；一种足够不凑数量，不把情景当方法。Terminal及其他零权重诊断单独展示，不进入中央football field |
| 23 | **锁定期供给地图（条件触发）** | 11/12 | 释放日期/条件/股数、占流通盘、占20/60日ADV、价格门槛 | 时间轴+供给柱；确定量与条件股分开；标潜在支撑/压力而非确定预测 |
| 24 | 技术/业务教学图（按理解障碍选取） | 2/4/8 | 已通过研究中的流程、参与方、资金/信息/责任关系；不编未披露的分部利润 | Mermaid 或矢量框箭头；不是产品实物图 |
| 25 | 指引演变与兑现图 | 9 | 五次电话会指引、对应期间实际值/待兑现状态、可比指标和日期 | 时间线或可比区间图；不是把长期目标冒充季度承诺 |
| 26 | 经营情景驱动对比 | 10/12 | 同一预测年 Bear/Base/Bull 的最多五项核心经济驱动，读取模型输出 | 分面条形/驱动表图；不替代完整情景模型 |
| 27 | 增长 × 估值散点图（数据可比时） | 11 | 同快照、同 forward 期间的增长和倍数；注明分部/会计/净现金等限制 | 数据 scatter；不机械用回归线推目标价，不混同 chart 17 |

## 竞争格局四象限：轴与证据

- Full report 默认规划并交付 chart 17。两轴回答一个竞争问题，例如“产品/服务广度 × 客户关系控制力”“单位成本 × 交付能力”；按行业选择，不沿用航天运力或固定用市值、增长/P/E。不同轴可有取舍，右上角不自动等于最佳投资。
- 图上写清 X/Y 轴名称、方向、低/高端点、四个象限的含义、标的和主要对手。分割线基于经济门槛/样本中位数/明确的定性边界，并解释依据；不为让标的落在右上角调整坐标。
- `positioning_mode=quantitative`：使用同期间、同定义数据，记录单位、变换和分割阈值；公司级与产品级比较不能混用。气泡大小有可靠第三变量及图例才启用。
- `positioning_mode=qualitative`：以披露和产品能力支持相对位置，工作底稿逐家说明定位依据。图内写“定性定位示意”，轴用有定义的低/中/高或窄/广等等级；不显示伪精确 0–100 分或精确距离，不声称客观排名。可以用 Matplotlib 的 scatter 布局渲染位置图，但这不使定性坐标成为测量数据。
- 定位不足时先更换有证据的轴/收窄玩家集合。仍不能支持时在覆盖计划与 handoff 写清跳过理由；不能画无来源占位图。不能因已有评分热力图就跳过。评分矩阵解释多维强弱，四象限解释战略位置和替代路径，两图结论须相容。
- Manifest 记录 `positioning_mode`、`target_name`、`axes`（x/y 各含 label、definition、scale、split_basis）、`positioning_evidence`（逐家 name、basis、source_ids）；点位有不确定性时用区域或文字说明。

## 配图覆盖计划（先于制作）

逐项记录读者问题、章节、拟用图、证据/模型位置、included/skipped 及理由：①业务/技术机制；②历史与价值链；③竞争评分与四象限；④指引兑现；⑤经营情景；⑥增长与估值；⑦官方产品图。已有表格/正文是否足够也要解释；不按张数凑齐。

用户给参考报告时先比较它承担的解释功能，再选择本标的缺失的图。只借鉴版式/表达，不复制他公司的数据、行业轴、估值权重或事实。历史时间线已在清单中，不能默默漏掉；历史价格/基准曲线无完整可验证序列则跳过。

Task 1 留下概念与竞争定位证据，Task 4 形成覆盖计划并制作，Task 5 对照计划检查插入。后期发现实质证据缺口时回到对应研究/模型步骤，不在排版脚本中临时编数据。

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
- Matplotlib Text artists must pass `scripts/chart_text_overlap.py` at final output size; other renderers use the bounds/overlap procedure in `09_visual_style_guide.md`. Labels that collide must be re-laid out or split.
