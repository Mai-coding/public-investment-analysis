"""
fetch_comp_data.py - 拉研究对象实时市场数据 + SEC 文件（yfinance 一线通道）

口径纪律（与 skill 一致）：
  - 只产出 forward P/E 与 forward P/S —— **不抓取、不打印 EV/EBITDA、EV/Sales**（skill 明令禁用）。
  - forward P/S = market cap ÷ 次年收入预测（Ticker.revenue_estimate 的 '+1y' avg）。
  - 市场数据一线走 yfinance；字段缺失时再用公司 IR/最新财报、专业数据 MCP、用户研报兜底。

覆盖范围（诚实声明）：
  - Yahoo Finance：美股 + 部分港股（xxxx.HK）/ A 股（xxxxxx.SS/.SZ）可拉行情与预测，预测覆盖率视标的而定。
  - SEC EDGAR：仅美股 filings；按 --entity_type 自动选择年报/季报数量。
  - 巨潮（A 股）/ HKExnews（港股）filings 本脚本 **不支持自动下载**，
    请按 references/06_comp_analysis_workflow.md Step 3 手动/网页下载。

用法：
    python3 fetch_comp_data.py --entity_type competitor --tickers AAA BBB CCC DDD --out_dir ./entity_filings
    python3 fetch_comp_data.py --entity_type target --tickers AAA --ciks 0001234567 --out_dir ./entity_filings
"""
import argparse
import json
import sys
import time
from pathlib import Path


for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def _estimate_next_year(ticker_obj, attr):
    """从 Ticker.revenue_estimate / Ticker.earnings_estimate 取 '+1y' 行的 avg。

    注意：估计值不在 Ticker.info 里（info.get('revenueEstimate') 恒为 None），
    必须用 Ticker.revenue_estimate / Ticker.earnings_estimate 属性（DataFrame）。
    """
    try:
        df = getattr(ticker_obj, attr)
        if df is None or df.empty:
            return None
        if '+1y' in df.index:
            return df.loc['+1y'].get('avg')
        return None
    except Exception:
        return None


def fetch_yfinance(tickers):
    """从 Yahoo Finance 拉实时数据（forward P/E + forward P/S，无 EV 类倍数）"""
    import yfinance as yf

    results = {}
    for t in tickers:
        try:
            s = yf.Ticker(t)
            info = s.info

            market_cap = info.get('marketCap', 0) or 0
            rev_next = _estimate_next_year(s, 'revenue_estimate')      # 次年收入预测（绝对额）
            eps_next = _estimate_next_year(s, 'earnings_estimate')     # 次年 EPS 预测
            rev_ttm = info.get('totalRevenue', 0) or 0

            forward_ps = (market_cap / rev_next) if (market_cap and rev_next) else None
            fwd_rev_growth = (rev_next / rev_ttm - 1) if (rev_next and rev_ttm) else None

            results[t] = {
                'ticker': t,
                'name': info.get('longName', t),
                'price': info.get('currentPrice') or info.get('regularMarketPrice', 0),
                'marketCap_B': market_cap / 1e9,
                'revenue_TTM_B': rev_ttm / 1e9,
                'revenue_next_FY_B': (rev_next / 1e9) if rev_next else None,
                'eps_next_FY': eps_next,
                'pe_trailing': info.get('trailingPE'),
                'pe_forward': info.get('forwardPE'),
                'ps_forward': forward_ps,
                'revenue_growth_TTM': info.get('revenueGrowth'),
                'revenue_growth_forward': fwd_rev_growth,
                'net_margin': info.get('profitMargins'),
                'data_date': info.get('regularMarketTime'),
            }
            fpe = results[t]['pe_forward']
            fps = results[t]['ps_forward']
            print(f"✓ {t}: MktCap ${results[t]['marketCap_B']:.1f}B / "
                  f"fwd P/E {f'{fpe:.1f}x' if fpe else 'N/A'} / "
                  f"fwd P/S {f'{fps:.1f}x' if fps else 'N/A(缺次年收入预测,需研报或MCP补)'}")
            time.sleep(0.5)
        except Exception as e:
            print(f"✗ {t}: {e}")
            results[t] = {'error': str(e)}
    return results


def fetch_sec_filings(ticker, cik, out_dir, n_annual=1, n_quarterly=2):
    """从 SEC EDGAR 下载指定数量的 10-K、10-Q，再补 2020+ S-1。仅美股。"""
    import urllib.request

    user_agent = "Investment Research demo@example.com"
    out = Path(out_dir) / ticker
    out.mkdir(parents=True, exist_ok=True)

    cik_padded = str(cik).zfill(10)
    sub_url = f"https://data.sec.gov/submissions/CIK{cik_padded}.json"

    req = urllib.request.Request(sub_url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(req) as r:
        data = json.load(r)

    forms = data['filings']['recent']['form']
    dates = data['filings']['recent']['filingDate']
    accs = data['filings']['recent']['accessionNumber']
    docs = data['filings']['recent']['primaryDocument']

    downloaded = []

    # 指定数量的 10-K
    count_10k = 0
    for f, d, a, doc in zip(forms, dates, accs, docs):
        if f == '10-K' and count_10k < n_annual:
            year = d[:4]
            acc_clean = a.replace('-', '')
            url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                   f"{acc_clean}/{doc}")
            target = out / f"10K_FY{int(year)-1}.htm"
            print(f"  下载 10-K FY{int(year)-1}: {url}")
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req) as r:
                with open(target, 'wb') as f_out:
                    f_out.write(r.read())
            downloaded.append(str(target))
            count_10k += 1
            time.sleep(0.3)
    if count_10k < n_annual:
        print(f"  ⚠ 仅找到 {count_10k} 份 10-K（要求 {n_annual} 份）——"
              f"上市不足 {n_annual} 年属正常，否则在 Appendix 注明缺哪几期")

    # 指定数量的 10-Q
    count_10q = 0
    for f, d, a, doc in zip(forms, dates, accs, docs):
        if f == '10-Q' and count_10q < n_quarterly:
            acc_clean = a.replace('-', '')
            url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                   f"{acc_clean}/{doc}")
            target = out / f"10Q_{d}.htm"
            print(f"  下载 10-Q {d}: {url}")
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req) as r:
                with open(target, 'wb') as f_out:
                    f_out.write(r.read())
            downloaded.append(str(target))
            count_10q += 1
            time.sleep(0.3)
    if count_10q < n_quarterly:
        print(f"  ⚠ 仅找到 {count_10q} 份 10-Q（要求 {n_quarterly} 份）")

    # S-1 (2020+)
    for f, d, a, doc in zip(forms, dates, accs, docs):
        if f in ('S-1', 'S-1/A') and d >= '2020-01-01':
            year = d[:4]
            acc_clean = a.replace('-', '')
            url = (f"https://www.sec.gov/Archives/edgar/data/{cik}/"
                   f"{acc_clean}/{doc}")
            target = out / f"S1_{year}.htm"
            print(f"  下载 S-1 {year}: {url}")
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req) as r:
                with open(target, 'wb') as f_out:
                    f_out.write(r.read())
            downloaded.append(str(target))
            break

    return downloaded


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', nargs='+', required=True,
                        help='Research entity tickers (e.g., AAA BBB CCC)')
    parser.add_argument('--out_dir', default='./entity_filings')
    parser.add_argument('--entity_type', choices=['target', 'competitor', 'upstream', 'downstream'],
                        default='competitor', help='决定 SEC 年报/季报下载数量')
    parser.add_argument('--ciks', nargs='+', default=[],
                        help='Optional CIK 对应每个 ticker（若不指定则需手动 lookup）')
    parser.add_argument('--yfinance_only', action='store_true',
                        help='只拉 yfinance，不下载 SEC')
    args = parser.parse_args()

    # 1. Yahoo Finance 数据
    print("=" * 60)
    print("Step 1: Yahoo Finance 数据 (forward P/E + forward P/S)")
    print("=" * 60)
    yf_data = fetch_yfinance(args.tickers)

    # 保存
    Path(args.out_dir).mkdir(parents=True, exist_ok=True)
    with open(Path(args.out_dir) / 'yfinance_snapshot.json', 'w') as f:
        json.dump(yf_data, f, indent=2, default=str)
    print(f"\n✓ Yahoo 数据保存至 {args.out_dir}/yfinance_snapshot.json")
    print("  （记录数据快照日期；ps_forward 为 None 的标的需用研报 consensus 或专业 MCP 补全）")

    # 2. SEC EDGAR（仅美股；A 股巨潮 / 港股 HKEx 走 06_comp_analysis_workflow.md Step 3 手动下载）
    if not args.yfinance_only and args.ciks:
        print("\n" + "=" * 60)
        scope = {
            'target': (3, 2),
            'competitor': (1, 2),
            'upstream': (1, 1),
            'downstream': (1, 1),
        }[args.entity_type]
        print(f"Step 2: SEC EDGAR 下载（{scope[0]} 期 10-K + {scope[1]} 期 10-Q + S-1）")
        print("=" * 60)
        for ticker, cik in zip(args.tickers, args.ciks):
            print(f"\n--- {ticker} (CIK {cik}) ---")
            try:
                files = fetch_sec_filings(ticker, cik, args.out_dir,
                                          n_annual=scope[0], n_quarterly=scope[1])
                print(f"  下载完成: {len(files)} 个文件")
            except Exception as e:
                print(f"  ✗ {ticker}: {e}")


if __name__ == "__main__":
    main()
