"""
parse_sec_filings.py - 解析 SEC 10-K / S-1 HTML，提取关键章节 + 量化数据点

用法：
    python3 parse_sec_filings.py --file 10K_FY2025.htm --out_dir ./parsed
"""
import argparse
import json
import re
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")


def parse_html(html_path):
    """HTML → 纯文本"""
    from bs4 import BeautifulSoup
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'lxml')
    return soup.get_text(separator='\n', strip=True)


def find_section(text, start_marker, end_markers):
    """从 text 中提取 start_marker 到任一 end_marker 之间的内容"""
    start_pat = re.compile(start_marker, re.IGNORECASE)
    starts = list(start_pat.finditer(text))
    if not starts:
        return None
    # 通常 ToC 里有第一次，正文是第二次
    start_pos = starts[-1].start() if len(starts) > 1 else starts[0].start()
    end_pos = len(text)
    for end_marker in end_markers:
        end_pat = re.compile(end_marker, re.IGNORECASE)
        ends = [m for m in end_pat.finditer(text) if m.start() > start_pos]
        if ends:
            end_pos = min(end_pos, ends[0].start())
    return text[start_pos:end_pos]


def extract_quantitative_data(text):
    """提取关键量化数据点"""
    patterns = {
        'dollar_amounts': r'\$[\d,]+\.?\d*\s*(?:million|billion|trillion|M|B|T)\b',
        'percentages': r'\b\d+(?:\.\d+)?%\b',
        'growth_yoy': r'(?:increased|grew|grew\s+by|rose|jumped)\s+(?:by\s+)?\d+(?:\.\d+)?%',
        'revenue_per_unit': r'\$[\d,]+(?:\.\d+)?\s+per\s+(?:kg|launch|unit|customer)',
        'employee_count': r'(?:approximately\s+)?[\d,]+\s+(?:employees|full-time)',
        'launches': r'\d+\s+(?:successful\s+)?launches?',
        'satellites': r'\d+(?:,\d+)*\s+satellites?',
        'years_of_operation': r'(?:since|in)\s+\d{4}',
    }
    results = {}
    for name, pat in patterns.items():
        matches = []
        for m in re.finditer(pat, text):
            ctx_start = max(0, m.start() - 100)
            ctx_end = min(len(text), m.end() + 80)
            context = text[ctx_start:ctx_end].replace('\n', ' ')
            matches.append({
                'match': m.group(),
                'context': context[-200:].strip()
            })
        results[name] = matches[:30]  # 限制每类最多 30 个
    return results


def parse_filing(html_path, out_dir):
    """主解析流程"""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    base = Path(html_path).stem

    # 1. HTML → 纯文本
    print(f"[1/4] 解析 HTML: {html_path}")
    text = parse_html(html_path)
    text_path = out / f"{base}_text.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"  ✓ 文本保存：{text_path} ({len(text):,} chars)")

    # 2. 提取 Item 1 Business
    print("[2/4] 提取 Item 1 Business")
    biz = find_section(text, r'Item\s+1\.\s+Business',
                       [r'Item\s+1A\.', r'Item\s+2\.'])
    if biz:
        biz_path = out / f"{base}_business.txt"
        with open(biz_path, 'w', encoding='utf-8') as f:
            f.write(biz)
        print(f"  ✓ Business 章节：{biz_path} ({len(biz):,} chars)")

    # 3. 提取 Competition (在 Business 内)
    if biz:
        comp_pos = biz.find('Competition')
        if comp_pos > 0:
            comp_text = biz[comp_pos:comp_pos + 25000]
            # Try to truncate at next major section
            for end_keyword in ['Manufacturing', 'Properties', 'Employees',
                                'Item 1A', 'Intellectual Property']:
                end_pos = comp_text.find(end_keyword, 100)
                if end_pos > 0:
                    comp_text = comp_text[:end_pos]
                    break
            comp_path = out / f"{base}_competition.txt"
            with open(comp_path, 'w', encoding='utf-8') as f:
                f.write(comp_text)
            print(f"  ✓ Competition 子章节：{comp_path} ({len(comp_text):,} chars)")

    # 4. 提取 Item 7 MD&A
    print("[3/4] 提取 Item 7 MD&A")
    mda = find_section(text, r"Item\s+7\.\s+Management",
                       [r"Item\s+7A\.", r"Item\s+8\."])
    if mda:
        mda_path = out / f"{base}_mda.txt"
        with open(mda_path, 'w', encoding='utf-8') as f:
            f.write(mda)
        print(f"  ✓ MD&A 章节：{mda_path} ({len(mda):,} chars)")

    # 5. 量化数据提取
    print("[4/4] 提取量化数据")
    quants = extract_quantitative_data(text)
    quants_path = out / f"{base}_quants.json"
    with open(quants_path, 'w', encoding='utf-8') as f:
        json.dump(quants, f, indent=2, ensure_ascii=False)
    total_quants = sum(len(v) for v in quants.values())
    print(f"  ✓ 量化数据：{quants_path} ({total_quants} 个数据点)")

    return {
        'text_path': str(text_path),
        'business_path': str(out / f"{base}_business.txt") if biz else None,
        'competition_path': str(out / f"{base}_competition.txt") if biz and comp_pos > 0 else None,
        'mda_path': str(mda_path) if mda else None,
        'quants_path': str(quants_path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help='HTML SEC filing path')
    parser.add_argument('--out_dir', default='./parsed')
    args = parser.parse_args()
    result = parse_filing(args.file, args.out_dir)
    print("\n=== 解析完成 ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
