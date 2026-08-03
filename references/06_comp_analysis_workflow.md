# 06 - 可比公司分析工作流（SEC EDGAR + A 股 + 港股 + Yahoo Finance）

## 工作流总览

```
Step 1: 识别 4-5 家最可比公司（全球范围 — 美股 + A 股 + 港股）
Step 2: yfinance API 拉实时数据（forward P/E、forward P/S 优先）
Step 3: 下载一手文件
        - competitors：每家近 1 期年报 + 近 2 期季报 + 对应 transcripts
        - 美股：SEC EDGAR 10-K / 10-Q / S-1
        - A 股：巨潮资讯 / 上交所 / 深交所年报 + 季报 + 招股书
        - 港股：HKExnews 年报 + 中期/季度业绩 + 招股章程
Step 4: 解析 HTML/PDF，提取关键章节
Step 5: 正则提取量化数据点
Step 6: 写成 Markdown 摘要 + 集成到主报告附录
```

## Step 1: 识别可比公司

### 优先级
1. **用户指定**（最优先）
2. **直接可比**：同行业 + 同业务模式 + 相近规模 / 增速
3. **间接可比**：同行业 + 不同业务模式
4. **替代型可比**：跨行业但商业模式类似

### 必须全球范围
不能只看 target 所在国家。例：
- 中国 AI 大模型 target → 既看 OpenAI / Anthropic / Google（美股）也看智谱 / 月之暗面 / 阶跃星辰（中国）
- 美国 EV 公司 target → 既看 Tesla / Lucid / Rivian（美股）也看 BYD（港股 + A 股）、蔚来 / 小鹏 / 理想（美股/港股）

### 数量控制
- 上市可比固定 4-5 家
- 中位数计算时剔除两端 outlier（pre-revenue 公司、distressed 公司）

## Step 2: 拉实时市场数据（Yahoo Finance / yfinance 一线；forward 优先）

**一线：yfinance**。每次重新拉实时价格、市值、forward 收入/EPS、forward P/E 与 forward P/S，并记录快照日期。

**字段缺失时的兜底顺序**：公司 IR/最新财报自行计算 → 专业数据 MCP（S&P Capital IQ / FactSet / LSEG / Daloopa）→ 用户研报 consensus。所有兜底值必须写实际来源和日期。

```python
import yfinance as yf
ticker = yf.Ticker('NVDA')
info = ticker.info

# 必要字段
market_cap = info['marketCap'] / 1e9                # 单位：十亿
annual_revenue_past = info['totalRevenue'] / 1e9    # TTM / past year

# ⚠️ 预测值不在 .info 里（info.get('revenueEstimate') 恒为 None——旧写法会静默失败）
# 必须用 Ticker 的 estimate 属性（DataFrame，'+1y' 行 = 次年预测）：
rev_est = ticker.revenue_estimate      # index: 0q / +1q / 0y / +1y
eps_est = ticker.earnings_estimate
revenue_next_year = rev_est.loc['+1y']['avg'] if '+1y' in rev_est.index else None
eps_next_year     = eps_est.loc['+1y']['avg'] if '+1y' in eps_est.index else None

forward_pe = info.get('forwardPE')
trailing_pe = info.get('trailingPE')
revenue_growth_yoy = info.get('revenueGrowth')      # backward YoY，仅参考

# 计算 forward P/S
forward_ps = market_cap * 1e9 / revenue_next_year if revenue_next_year else None

# 不用以下字段（本 skill 偏好 forward P/E / P/S，不用 EV 类倍数）
# ev = info['enterpriseValue']   ← 不用
# ebitda = info['ebitda']         ← 不用
# ev_to_ebitda                    ← 不用
```

**关键 4 字段**：
- market cap
- annual revenue next year (forward)
- net income next year (forward)
- annual revenue in the past year（→ 算 revenue growth rate）

**注意**：每次都重新拉，不要硬编码数字。

### 价格快照纪律 ⚠️ 强制（Redwire 教训）⚠️
v1 曾用 Morgan Stanley Jan 2026 报告的同业价（KTOS 122 / AVAV 382）做估值，但 May 2026 实际 KTOS 56 (-54%) / AVAV 174 (-54%)，结论严重偏离。
- ✅ **估值前必须用当前运行时的网页搜索/市场数据能力拉一次最新实时价**，快照日期标注到具体日（不超过 30 天）。
- ✅ 任何引用的同业倍数都带 "as of YYYY.MM.DD" 标签。
- ✅ 若实时价偏离参考报告 / 模型假设 **> 20%**，在报告里**显著标注**，不能藏着。

### 选 comp 时必须讨论 trade-off ⚠️（Redwire 教训）⚠️
v1 选了 RKLB + KTOS + AVAV，但 RKLB 是 P/S 90x+ 的 "故事股"（市场当 SpaceX 影子），不能直接套到 target，事后才手动剔除 outlier。
- ✅ 向用户提供 comp 选项时，使用当前运行时的用户输入机制，并为**每个选项注释关键特性 + 警告**：如 "RKLB 是 P/S 90x 故事股，可能拉高估值上限"。
- ✅ 推荐组合至少含一个**已盈利的直接对标**（业务最相似且已盈利）。
- ✅ 避免组合全是同质化标的（all 国防 SmidCap / all 故事股）。

## Step 3: 下载一手文件

### 美股：SEC EDGAR

```python
import urllib.request
user_agent = "Investment Research demo@example.com"
# 1. 拿 CIK → submissions JSON
sub_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"
# 2. competitors 下载最近 1 期 10-K + 2 期 10-Q；IPO≤3年再补 S-1/424B4
url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_no_dashes}/{primary_doc}"
```

### A 股：巨潮资讯网 / 上交所 / 深交所

- **巨潮资讯**：http://www.cninfo.com.cn （所有 A 股上市公司公告）
- **上交所**：http://www.sse.com.cn/disclosure/listedinfo/announcement/
- **深交所**：http://www.szse.cn/disclosure/listed/index.html

招股书优先用 2020 年及以后版本。

```python
# A 股招股书 URL 模式（巨潮）
# 通常需要先查询股票代码 → 找到招股书 PDF 链接
# 例：https://www.cninfo.com.cn/new/disclosure/detail?stockCode=600519&announcementId=xxx
```

### 港股：HKExnews

- **HKExnews**：https://www.hkexnews.hk/listedco/listconews/sehk/[year]/[month]/...
- **年报**：每年一份
- **招股章程（IPO Prospectus）**：上市时申报

```python
# 港股年报 URL 模式
# https://www.hkexnews.hk/listedco/listconews/sehk/[year]/[month]/[date]/LTN[lang][docID].htm
```

### SEC User-Agent 要求
必须 set User-Agent header (格式 "Name Email"), 否则被 block。

## Step 4: 解析 HTML / PDF

### HTML 解析（美股 10-K、港股年报英文版）
```python
from bs4 import BeautifulSoup
with open('10K.htm', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'lxml')
text = soup.get_text(separator='\n', strip=True)
```

### PDF 解析（A 股招股书、港股中文年报）
```python
import fitz  # PyMuPDF
doc = fitz.open('prospectus.pdf')
text = ''
for page in doc:
    text += page.get_text() + '\n'
```

### 定位关键章节

```python
markers = {
    # 美股 10-K
    'Item 1 Business': r'Item\s+1\.\s+Business',
    'Item 1A Risk Factors': r'Item\s+1A\.\s+Risk',
    'Item 7 MD&A': r"Item\s+7\.\s+Management",
    # A 股招股书
    '第一节 业务': r'第[一二三]节\s*业务',
    '行业概况': r'行业概况|所处行业',
    '风险因素': r'风险因素|主要风险',
    # 港股招股章程
    'Industry Overview': r'Industry\s+Overview',
    'Business Section': r'Business\s+(?:Section|Overview)',
}
```

### 优先提取的章节
- **业务介绍 / Business**（必备）
- **行业概况 / Industry Overview**（用于 target 行业研究）
- **MD&A / 管理层分析**（用于 target 财务质量评估）
- **风险因素 / Risk Factors**（用于借鉴 Killer Risk）

## Step 5: 正则提取量化数据点

参考 `scripts/parse_sec_filings.py` 的 patterns。每个匹配带 80-120 字符上下文。

## Step 6: 写 Markdown 摘要 + 集成到附录

模板：

```markdown
# {COMPANY} ({TICKER}) 分析摘要

## 一、三年财务全景
- 总收入: FY-3 / FY-2 / FY-1
- 净利润: ...
- R&D: ...
- Capex: ...

## 二、单位经济学
- 关键 KPI 1
- 关键 KPI 2

## 三、政府 / 核心客户深度对比

## 四、市场叙事对比

## 五、自我描述的竞争格局

## 六、给 target 公司的 N 大启示

## 七、关键指标对照表

## 八、原文存档与链接
```

集成到主报告 **附录 A / B / C**。主报告 6.1-6.5 + 10.1 引用附录详细数据。

## 时间预算

| 步骤 | 时间 |
|------|------|
| 识别可比 + 拉 yfinance | 5 分钟 |
| 下载一手文件（美股 / A 股 / 港股）| 3-5 分钟 |
| 解析 HTML / PDF | 3-5 分钟 |
| 正则提取数据点 | 3 分钟 |
| 写 Markdown 摘要 | 10-15 分钟 |
| 集成到 DOCX 附录 | 5-10 分钟 |
| **每家可比合计** | **~35 分钟** |

3 家可比 ≈ 2 小时投入。
