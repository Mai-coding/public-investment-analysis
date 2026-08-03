# 11 - 踩坑清单（Lessons Learned）· 指针索引

**目的**：往期 IC 报告的具体踩坑**索引**。每条教训的**正文已下沉到对应 topical 归宿**（一处维护、避免漂移），本文件只保留“一句话教训 → 详见哪里”的指针；不作为第二套规则来源。

> 🧭 **怎么用**：动笔/出图/交付前，按下表跳到对应文件读细节。**章节完整性 + 深度核查的可执行权威是 `scripts/depth_audit.py`（闸门 1/2）**，交付自检清单是 `10_final_checklist.md`——这两处不在本文件重复。

---

## 一、按教训查归宿（指针表）

| 教训（一句话） | 详见 |
|---|---|
| **图表数据逻辑一致性**：多 source 不硬塞一张图、双 Y 轴默认改双子图、每张图能独立讲一个故事（driver decomposition） | `09_visual_style_guide.md` §一 |
| **时间线标年份 / 饼图标"绝对值+%" / 源注释禁用 `fig.add_axes` 占位（改 `fig.text`）** | `09_visual_style_guide.md` §十三；自检 `10` §B |
| **matplotlib 中文字体 fallback chain（含 ASCII）+ 出第 1 张图立即肉眼 sanity check** | `13_cjk_charts.md`；`09` §二 |
| **雷达图标题用 `fig.suptitle` 防遮挡 / 密集 scatter 用 leader line + bbox** | `09_visual_style_guide.md` §三、§四 |
| **副标题禁裸 `$`（触发 mathtext）/ 数字单位不写 "$X 亿美元"** | `09_visual_style_guide.md` §十、§九 |
| **必答/指导性问题写成陈述句，不把问号搬进报告**（§4.5/6.3/8.5/8.6/9.2–9.4） | `14_depth_playbook.md` §1.1；自检 `10` §3；题目 `03` §4.5 |
| **fabless 半导体团队规模用"几百人级"，不套互联网"万人级"**（含规模参考表） | `15_industry_modules.md` 末"行业团队规模口径参考表"；自检 `10` §12 |
| **每个 `Fact：` 句必须紧跟来源 / 可比数据点必须带快照日期（§11 须有快照日期段落）** | `01_source_hierarchy.md` "两条硬规则"；自检 `10` §5、§8 |
| **概率加权情景必须写具体业务事件链（触发→传导→回算目标价），不给孤零零一个数字** | `task3-valuation.md` Step 4；自检 `10` §4 |
| **章节/子节完整性**（§4 必含 4.1–4.5；§2 八子节；§7 每家 5 段；附录 A–C 四节 + 字数下限） | `sections/03a–03d` + `14_depth_playbook.md`；**强制由 `scripts/depth_audit.py` 闸门 1/2 判** |
| **内容深度 ≠ 字数**：证据表先行 + 定性词挂数字 + 写清因果与反面（自然散文，不贴 CEMRI 标签）+ 每章 2–3 个预答追问 | `14_depth_playbook.md`（动笔前必读）；自检 `10` §A |
| **两层估值法（运营 SOTP + 登月期权桶）/ 隐含期权溢价 + 先例锚 / 退出 P/S 取成熟期常态 / 概率≠时间风险不重复计 / DCF 仅作下限 / 情景权重稳健性表** | `task3-valuation.md`（Step 0 litmus + 末"两层估值法"节）|
| **DOCX 构建机制**（字节钉死/静默截断绕法、`<w:p>` 不嵌套、static TOC、US Letter、表格 DXA、ImageRun altText、validate.py 0 错误、三方数字一致、Python 锚点转换脚本 block_replace/insert + node --check、招股书 PDF 产品图抽取、重构后旧值扫雷） | `task5-report-assembly.md` "DOCX 构建机制"节 |
| **图片放在所支撑小节正文之后（小节末尾），不放小节/章节开头**（Talen 教训：图位置） | `04_chart_inventory.md`「共通规范·图片位置」+ `task5-report-assembly.md` Build #4 + `17_product_images.md` §五 |
| **黑/深底色图 → 全部文字白色/浅色，禁黑底黑字**（Talen 教训：配色） | `09_visual_style_guide.md` §六 + `13_cjk_charts.md` §三代码 |
| **市场预测优先用 ≥2025-01-01 发布的 vintage，标发布日期**（Talen 教训：数据新鲜度） | `01_source_hierarchy.md` 信源使用规则 + `task1-company-research.md` §1a + `15_industry_modules.md` 模块2 |
| **A 研究诚信**：覆盖日志"命中"必带 ≥1 事实+URL/时间戳、精读 ≥6 篇、视频无字幕须声明（否则闸门1 FAIL） | `16_priority_sources.md` (f) + `task1-company-research.md` 三件硬产出物；脚本判 `depth_audit.py --stage research` |
| **B 财务模型真 bottom-up**：收入量×价驱动·大客户长约 carve-out·EBITDA=收入−成本·实物量反算·改驱动全链联动·压力面板 | `task2-financial-modeling.md` Step 2/4/9 |
| **C 假设锚一手披露**：价格/单价假设先在 10-K 找锚再 calibrate；calibrate-to-guidance 标 plug；引 hedge book 解释实现价≠现货价 | `task2-financial-modeling.md` Step 2 + `01_source_hierarchy.md` |
| **D 估值层联动模型**：Comps 隐含价/Valuation Summary/情景目标价 green-link 回 IS，改模型目标价自动联动 | `task3-valuation.md` Step 5 |
| **异质可比组中位数不能作中央锚**：逐家分角色；至少3家经济属性相近才可用子样本中位数；多分部走分部SOTP | `task3-valuation.md` Step 3 + `19_model_provenance_and_consistency.md` Manifest |
| **来源不能写泛化描述**：所有硬编码逐格映射准确文件/文章名、URL/路径和页码/Item；424B4优先支持最终发行与锁定条款 | `01_source_hierarchy.md` + `19_model_provenance_and_consistency.md` |
| **价值迁移结论优先用同公司分部数据**：分部收入/EBITDA/Capex/利用率同口径验证；跨公司毛利率只能作代理 | `recipes/18a–18f` 配方三 |
| **全局修改不能只修一张图**：可比组/方法/数字/色板变化后重建Excel→全部相关图→DOCX，扫旧标签/值/颜色 | `19_model_provenance_and_consistency.md` 全局影响矩阵 + `task5-report-assembly.md` |
| **E1 大文件写入与运行时差异（全局，不止 DOCX）**：结构化编辑/确定性构建/临时文件原子替换/写后验证 | `SKILL.md`「大文件与运行时兼容纪律」；运行时映射见 `12_long_running_tasks.md`；DOCX 细节见 `task5-report-assembly.md` |
| **E2/E3 openpyxl**：绝不 `cell.fill=None`（损坏 xlsx）；失败 save 会损坏源文件，手术前先 cp 快照分版本 | `task2-financial-modeling.md`「Excel 手术安全」 |
| **E4 闸门切分对标题敏感**：章标题用 `§N　…`/`N. …`（句点+空格）；正文别用 `N. ` 有序列表，改 `（1）`/`①` | `task5-report-assembly.md` + `sections/03a–03d` |

---

## 二、跨 task 流程小贴士（仍只在本文件保留）

这几条太小、不值得单独立家，留在此处：

1. **复杂报告必须维护可检查的执行计划**：5 个 task、20+ 子任务，没有计划跟踪极易漏子节。Task 1 前把 16 章 + 附录逐项列入当前运行时的计划工具；每章完成后更新状态，进入下一章前检查 pending。（能力映射见 `12_long_running_tasks.md`，并与 `SKILL.md` “逐 task 跑 + 完成确认卡”纪律配套。）
2. **中文渲染尽早 sanity check**：不要等 14 张图全出完才发现字体问题——第 1 张图出来立即用当前运行时的图片查看能力肉眼看（细节见 `13_cjk_charts.md`）。
3. **用户说"数据有逻辑问题"时，第一反应是查 source 而非改数字**：多半是多 source 数据被强行塞进一张图（口径不一致），回到 `09` §一 driver decomposition。
4. **生成顺序固定**：研究 → Excel → 图 → DOCX；图未出齐不建 DOCX。

---

## 三、交付前

不要在本文件维护 Pre-flight checklist——**交付自检的唯一清单是 `10_final_checklist.md`**（含 §0 Pre-flight + §A 深度自检 + §B 图表自检 + §C DOCX 校验），章节完整性/字数/问句标题=0/版本防回退由 `scripts/depth_audit.py` 闸门 2 强制。
