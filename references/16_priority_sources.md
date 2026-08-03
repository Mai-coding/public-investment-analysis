# 16 · 指定优先信源渠道（文章 hub）— 抓取 playbook

> **本文件是操作 playbook**；这些渠道在信源层级里的**排序**（#6，定性/叙事层最先扫、排在通用「权威第三方研究」之前、仍在一手硬数据之下）见 `01_source_hierarchy.md`。
> Task 1 数据搜集时，在「web 研究 / 定性叙事」层先做**相关性门控**；仅对相关渠道深挖，再做通用搜索。每个 registry 行仍需进入终态。

---

## (a) 指定优先信源执行视图

| # | 渠道 | URL | 类型 | 何时相关 |
|---|------|-----|------|---------|
| 1 | a16z | https://www.a16z.news/ | VC 文章 hub | 科技/AI/创投、赛道趋势、技术叙事 |
| 2 | Bessemer Venture Partners Atlas | https://www.bvp.com/atlas | VC 研究 hub | 云软件、AI、SaaS benchmark、投资路线图 |
| 3 | Sequoia Capital | https://sequoiacap.com/ | VC 观点 hub | 科技趋势、投资观点、公司建设、创始人案例 |
| 4 | First Round Review | https://review.firstround.com/ | 创业运营 hub | 产品、增长、招聘、组织与运营方法论 |
| 5 | Greylock Greymatter | https://greylock.com/blog/greymatter/ | VC 博客 hub | 企业软件、AI、网络安全、公司建设 |
| 6 | Index Ventures Perspectives | https://www.indexventures.com/perspectives/ | VC 观点 hub | 全球科技趋势、市场地图、创始人案例 |
| 7 | Not Boring | https://www.notboring.co/ | 独立科技媒体 | 科技公司、商业模式、新兴赛道、长期主题 |
| 8 | Stratechery | https://stratechery.com/ | 独立战略媒体 | 科技/媒体战略、商业模式与产业结构 |
| 9 | Bain Insights | https://www.bain.com/insights/ | 咨询研究 hub | 行业、战略、运营、PE 与技术研究 |
| 10 | McKinsey Featured Insights | https://www.mckinsey.com/featured-insights | 咨询研究 hub | 行业规模、宏观趋势、价值链研究 |
| 11 | Stanford HAI AI Index | https://hai.stanford.edu/ai-index | 学术/数据报告 | AI 技术、投资、采用、人才、政策、全球竞争 |

> 唯一渠道真源是 `source_registry.json`；渠道增删只改 registry。本表只维护这些指定渠道的抓取方法，每个渠道是否深挖由 (b) 的相关性门控决定。

---

## (b) 总原则

1. **相关性门控（不强制深挖全部渠道）**：每个渠道先快速判断与本标的 / 行业 / 主题是否相关。
   - 相关 → 进入 (c) 深挖。
   - 不相关 → 不深挖，在 (f) 覆盖日志里记 `已扫·无命中`。
   - 例：消费品公司若在多数科技 VC 平台没有相关内容，逐一记 `no_hit` 即可，不要硬塞。
2. **叙事层优先，硬数据不越位**：本层产出喂 §2 行业纵向叙事 / §6 增长驱动 / §7 竞争观点。
   **财务数字、市场份额、估值倍数仍以招股书 / 年报 / Yahoo Finance 为准**（见 `01_source_hierarchy.md`）。
   VC 平台与独立媒体的判断通常标 **专家观点（analyst-opinion 类，非 Fact）**；与一手文件冲突时以一手文件为准并显式说明。
3. **使用当前运行时的网页研究能力**：优先用可用的搜索、页面打开和浏览器自动化能力。不要假定特定 browser skill、CDP、Node 版本或 Chrome 远程调试一定存在；能力不足时走 (e) fallback。Claude 与 ChatGPT/Codex 的具体映射见 `12_long_running_tasks.md`。
4. **扫描定义（关键）**：每个相关渠道必须
   - **先枚举候选清单**：文章 hub 列近期文章 + 关键词命中项。
   - **逐条标 relevant / skip**。
   - 仅对 relevant 项做**全文提取**，不是只读标题简介。

---

## (c) 渠道 playbook（文章 hub）

### 通用枚举与读取
1. 在每个 hub 内用「标的公司名 / 竞品名 / 行业 / 核心技术 / 商业模式」检索，并浏览近期列表；先记录枚举数量，再逐条标 relevant / skip。
2. 命中文章逐篇**全文提取**（优先当前运行时的页面打开/正文提取能力；必要时使用浏览器自动化，Jina 仅作允许联网时的可选 fallback）。只取得摘要或付费预览时标 `partial / paywalled`，不得记作全文。
3. 摘出数字、事实、观点和反方证据，每条保留标题、作者/机构、发布日期、URL；数字尽量回溯原始报告或公司披露。

### VC 与创业运营平台
- **a16z / BVP Atlas / Sequoia / Greylock / Index Ventures**：优先找行业路线图、市场地图、技术拐点、投资框架、portfolio 案例和公开 benchmark。投资机构对自身 portfolio 存在选择性偏差，默认标专家观点；自有调查数字须记录样本、时间和方法。
- **First Round Review**：用于产品、增长、招聘、组织设计和创始人执行力的机制性分析；案例不能直接外推为行业普遍事实。

### 独立科技战略媒体
- **Not Boring**：用于新兴赛道、公司叙事和商业模式假设，优先提取可验证的因果链；乐观叙事需主动寻找反方和原始数据。
- **Stratechery**：用于聚合理论、平台战略、价值链控制点和科技/媒体商业模式；免费文章可全文读，订阅内容仅使用实际可见部分并标付费限制。

### 咨询与权威数据
- **Bain Insights / McKinsey Featured Insights**：行业规模、价值链、运营 benchmark 和宏观趋势可作为强二手证据，但必须记录报告年份、地域、样本和定义；预测仍遵守最新 vintage 规则。
- **Stanford HAI AI Index**：AI 主题研究必须查看最新年度报告及相应章节；技术表现、投资、采用、人才、政策等数字按报告年份引用。需要趋势时至少对照上一年度，避免把单年变化写成长期趋势。

---

## (d) 引用格式

| 来源类型 | 引用格式 |
|---------|---------|
| 文章 hub | `[机构/媒体] "[标题]" [日期] [URL]` |

---

## (e) 依赖与 fallback

- 当前运行时缺少浏览器自动化或动态页面无法访问时：
  - 退到公开搜索结果、静态页面、机构 PDF/报告、RSS/API 或用户上传文件；若允许联网，可尝试 Jina（`r.jina.ai/<url>`）等正文代理。
  - 仅取得摘要、搜索片段或付费预览时，明确标 `partial / paywalled`，不得记作全文。
- **绝不臆造**：未取得的内容不得编造；该渠道按「数据不全」记录，说明缺口。

---

## (f) 覆盖记录（写入 Task 1 的统一“渠道覆盖矩阵”）

不要另建一套名单。使用 `source_registry.json` 中的 channel ID，在统一矩阵填入 status、searched_at、query_scope、evidence、note。

> 无命中渠道也要记 `no_hit`；fallback 情况注明实际取得的内容范围。

### 🔴 覆盖日志不得伪造（Talen 教训 A · 闸门 1 硬校验）

教训：曾在没真正读列表、没 fetch 任何内容的情况下，先凭印象填了一份"已扫·命中"的覆盖日志；实扫后才发现优先渠道直接点名标的并给出关键行业数据——本该第一轮就进报告。**覆盖日志若能被凭印象填 ✅，就失去意义。** 故：

1. **命中必须带证据**：每个声称「命中」的渠道，研究文档里必须附该来源 **≥1 条带数字的事实 + URL**（写进上表「命中项链接」列或紧邻的摘录段）。**没有具体事实 + 链接的"命中"一律视为未扫，闸门 1 FAIL。**
2. **最低阅读量**：相关渠道命中后至少精读 ≥6 篇（枚举 ≥10）。
