#!/usr/bin/env python3
"""Rebuild Intel preview assets exclusively from the five approved report pages."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

from build_showcase import FONT, SERIF, font, paste_card, sha256, wrap_pixels

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'examples/intel/source-pages'
OUTPUT = ROOT / 'assets/showcase'
MANIFEST = ROOT / 'examples/intel/showcase_manifest.json'
NAVY = '#002B49'
BLUE = '#0071C5'
PALE = '#EFF5FA'
SLATE = '#516579'
SLIDES = [
    ('cover.png', 1, '报告封面', 'Report cover', '经营复苏已有证据，现价仍需更强的每股兑现'),
    ('investment-summary.png', 3, '投资摘要', 'Investment summary', '先给结论，再区分市场定价与证据支持'),
    ('competition-quadrant.png', 23, '竞争象限', 'Competitive positioning', '产品平台控制力与外部制造能力分开判断'),
    ('price-bands.png', 40, '价格区间', 'Price bands', '把经营状态、估值条件与当前价格放在一起'),
    ('valuation-sensitivity.png', 41, '估值敏感性', 'Valuation sensitivity', '盈利与倍数同时变化，观察结论是否稳健'),
]
APPROVED_PAGE_HASHES = {
    'cover.png': 'c1c087a697b37bac4cb192c3581b0dc9222531822588b713d4a1d40b48c39ade',
    'investment-summary.png': 'eb97f5f7bc7239f37c3b6b014556c97606bda56d49a225342966365a63c6d612',
    'competition-quadrant.png': 'b2763f16fc72797babf6eafbc9846bc69ab78902a5a99c8f251ef310ec4034a6',
    'price-bands.png': '522ef4fb84422798d107fb64a7b3b0394e581cfac967f37e9f5c213492d00229',
    'valuation-sensitivity.png': '877df4eb0ef3ebe19e355171c037e47e84ebd88e2fee5a75033c3a30273584da',
}


def build_gif() -> Path:
    frames = []
    for i, (name, page, title, english, detail) in enumerate(SLIDES, 1):
        canvas = Image.new('RGB', (1600, 1000), PALE)
        d = ImageDraw.Draw(canvas)
        d.rectangle((0, 0, 470, 1000), fill=NAVY)
        d.text((42, 48), f'INTEL  /  {i:02d} OF 05', font=font(SERIF, 26), fill='#A8D8FF')
        d.text((40, 133), title, font=font(FONT, 53), fill='white')
        d.text((42, 211), english, font=font(SERIF, 31), fill='#D4EAFE')
        d.multiline_text((42, 315), wrap_pixels(d, detail, font(FONT, 30), 370),
                         font=font(FONT, 30), fill='white', spacing=18)
        d.text((42, 690), f'原报告第 {page} 页 / 58 页', font=font(FONT, 26), fill='#D4EAFE')
        d.text((42, 748), '仅公开五页精选', font=font(FONT, 29), fill='white')
        d.text((42, 800), 'Report: 2026-10-19', font=font(SERIF, 25), fill='#A8D8FF')
        d.text((42, 843), 'Market: 2026-10-16 close', font=font(SERIF, 25), fill='#A8D8FF')
        d.text((42, 929), 'Research example', font=font(SERIF, 23), fill='#D4EAFE')
        with Image.open(SOURCE / name) as im:
            paste_card(canvas, im, (655, 35, 1306, 955))
        d.text((1380, 480), f'{i:02d}', font=font(SERIF, 52), fill=BLUE)
        frames.append(canvas)
    path = OUTPUT / 'intel-workflow.gif'
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=2400,
                   loop=0, optimize=True, disposal=2)
    return path


def build_overview() -> Path:
    canvas = Image.new('RGB', (2000, 960), PALE)
    d = ImageDraw.Draw(canvas)
    d.text((52, 32), 'Intel | Five pages. One traceable research workflow.', font=font(SERIF, 48), fill=NAVY)
    d.text((55, 107), '58-page report / 5 selected pages / 2026-10-19 report / 2026-10-16 market close',
           font=font(SERIF, 26), fill=SLATE)
    for i, (name, page, title, _, _) in enumerate(SLIDES):
        x = 48 + i * 392
        with Image.open(SOURCE / name) as im:
            paste_card(canvas, im, (x, 195, x + 350, 690))
        d.text((x, 726), f'{i + 1:02d}  {title}', font=font(FONT, 32), fill=NAVY)
        d.text((x, 777), f'Original page {page}', font=font(SERIF, 26), fill=SLATE)
    d.text((53, 877), 'Open the individual PNG pages for readable detail. The complete report is not distributed.',
           font=font(SERIF, 29), fill=SLATE)
    path = OUTPUT / 'intel-showcase.png'
    canvas.save(path, optimize=True)
    return path


def build_result_card() -> Path:
    canvas = Image.new('RGB', (1200, 675), NAVY)
    d = ImageDraw.Draw(canvas)
    d.text((62, 45), 'PUBLIC INVESTMENT ANALYSIS', font=font(SERIF, 26), fill='#A8D8FF')
    d.text((62, 104), 'Intel | Selected report pages', font=font(SERIF, 48), fill='white')
    d.text((65, 182), 'Report 2026-10-19 / Market close 2026-10-16', font=font(SERIF, 25), fill='#D4EAFE')
    metrics = [('5 / 58', '公开页数 / pages shared'), ('38 / 2 / 0', '内容审计 / pass-warn-fail'),
               ('18 / 1 / 0', '模型审计 / pass-warn-fail'), ('20', '完整报告图表 / report charts')]
    for i, (value, label) in enumerate(metrics):
        x = 62 + i % 2 * 550
        y = 258 + i // 2 * 136
        d.rounded_rectangle((x, y, x + 520, y + 113), 12, fill='white')
        d.text((x + 24, y + 12), value, font=font(SERIF, 39), fill=BLUE)
        d.text((x + 24, y + 70), label, font=font(FONT, 21), fill=NAVY)
    d.text((65, 568), 'Known review limits are recorded with the case. No complete report is included.',
           font=font(SERIF, 23), fill='#D4EAFE')
    d.text((65, 615), 'A historical research workflow example, not a current recommendation.',
           font=font(SERIF, 23), fill='#D4EAFE')
    path = OUTPUT / 'intel-result-card.png'
    canvas.save(path, optimize=True)
    return path


def main() -> None:
    assert {p.name for p in SOURCE.iterdir()} == set(APPROVED_PAGE_HASHES), 'Only five approved PNG pages are allowed'
    for name, expected in APPROVED_PAGE_HASHES.items():
        assert sha256(SOURCE / name) == expected, f'Approved page changed: {name}'
    OUTPUT.mkdir(parents=True, exist_ok=True)
    outputs = [build_gif(), build_overview(), build_result_card()]
    payload = {
        'case': 'Intel (NASDAQ: INTC)', 'report_date': '2026-10-19',
        'market_snapshot': '2026-10-16', 'report_pages': 58, 'published_pages': 5,
        'body_characters': 42896, 'report_charts': 20,
        'source_report': {'filename': 'Intel_IC_Report_v1.pdf',
                          'sha256': '073b7af82a740da3aa9a718942d135ec29ae8ceb14ec8929a5ffbc9639e0749c',
                          'distributed': False},
        'source_page_map': {s[0]: s[1] for s in SLIDES},
        'source_pages': APPROVED_PAGE_HASHES,
        'generated_assets': {p.name: sha256(p) for p in outputs},
        'validation': {'artifact_audit': '18 PASS / 1 WARN / 0 FAIL',
                       'report_content_audit': '38 PASS / 2 WARN / 0 FAIL',
                       'depth_audit': 'PASS', 'recorded_final_review': 'PASS',
                       'selected_page_pdf_pixel_comparison': 'PASS'},
        'known_limits': ['Native Excel desktop recalculation was not independently inspected.',
                        'Word editing-marker UI was not independently inspected; printed output and native pagination were reviewed.',
                        'The selected pages are excerpts and do not include the full methods, assumptions or Sources appendix.'],
        'rebuild': 'python scripts/build_intel_showcase.py',
    }
    MANIFEST.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for p in [*outputs, MANIFEST]:
        print(p.relative_to(ROOT))


if __name__ == '__main__':
    main()
