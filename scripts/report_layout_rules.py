"""Report tables, cover semantics, TOC page colors and image paragraph markers.

Mechanical checks only. Source values, image typography and actual Word UI
appearance still require model reconciliation and visual review.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from docx_structure import NS, Structure, q, text_of

NAVY = json.loads((Path(__file__).resolve().parents[1] / 'assets/color_palette.json').read_text(encoding='utf-8'))['primary']['NAVY'].lstrip('#').upper()


def run_color(structure: Structure, paragraph, run):
    direct = run.find('w:rPr/w:color', NS)
    if direct is not None:
        return direct
    style = run.find('w:rPr/w:rStyle', NS)
    key = style.get(q('val')) if style is not None else None
    seen = set()
    while key in structure.styles and key not in seen:
        seen.add(key)
        current = structure.styles[key]
        color = current.find('w:rPr/w:color', NS)
        if color is not None:
            return color
        parent = current.find('w:basedOn', NS)
        key = parent.get(q('val')) if parent is not None else None
    color = structure.effective(paragraph, 'w:rPr/w:color')
    return color if color is not None else structure.styles_root.find('w:docDefaults/w:rPrDefault/w:rPr/w:color', NS)


def matches_color(node, expected: str) -> bool:
    return node is not None and node.get(q('val'), '').upper() == expected and not node.get(q('themeColor'))


def audit_cover_columns(table, audit) -> None:
    rows = table.findall('w:tr', NS)
    if len(rows) != 2 or any(len(row.findall('w:tc', NS)) != 3 for row in rows):
        return  # The existing cover-shape audit reports this failure.
    headings = [re.sub(r'\s+', '', text_of(cell)).lower() for cell in rows[0].findall('w:tc', NS)]
    allowed = ({'价格', 'price'}, {'回报', 'return', 'returns'}, {'综合判断', 'overalljudgment', 'overalljudgement'})
    if any(label not in choices for label, choices in zip(headings, allowed)):
        audit.fail('Cover columns must be Price / Return / Overall judgment in that order')
    price, returns, judgment = [text_of(cell) for cell in rows[1].findall('w:tc', NS)]
    missing = re.compile(r'[—–].*(?:不足|未取得|缺失|未知|unavailable|unknown)', re.I)
    current = re.search(r'(?:现价|当前价|current\s+price|spot\s+price)\s*[:：]?\s*([^\n;；]*)', price, re.I)
    base = re.search(r'(?:基准(?:情形|情景)?(?:价格带|价格|价)?|base(?:\s+case)?(?:\s+price)?)\s*[:：]?\s*([^\n;；]*)', price, re.I)
    def has_value(match):
        return match is not None and bool(re.search(r'\d', match[1]) or missing.search(match[1]))
    if not has_value(current) or not has_value(base):
        audit.fail('Cover price column must show current price and Base-case price/band with values')
    base_return = re.search(r'基准|\bBase\b', returns, re.I)
    return_value = re.search(r'[-+−]?\d+(?:\.\d+)?\s*%', returns) or missing.search(returns)
    forbidden = re.search(r'失望|悲观|乐观|熊市|牛市|入场|买入价|门槛价|\bBear\b|\bBull\b|Disappointment|Upside|Attractive\s+entry', returns, re.I)
    if not base_return or not return_value or forbidden:
        audit.fail('Cover return column must contain only the Base-case return; no other scenario or entry price')
    if not judgment:
        audit.fail('Cover overall judgment is empty')


def audit_report_tables(path: Path, audit) -> None:
    structure = Structure(path)
    bad_headers, bad_alignment, count = [], [], 0
    for index, table in enumerate(structure.document.iter(q('tbl')), 1):
        rows = table.findall('w:tr', NS)
        if not rows:
            continue
        # A row made only of embedded media is a layout container, not a header.
        header_cells = rows[0].findall('w:tc', NS)
        if any(text_of(cell) for cell in header_cells):
            count += 1
            for cell in header_cells:
                shade = cell.find('w:tcPr/w:shd', NS)
                if shade is None or shade.get(q('fill'), '').upper() != NAVY or shade.get(q('themeFill')):
                    bad_headers.append(f'table {index}: header fill')
                for p in cell.findall('.//w:p', NS):
                    for run in p.findall('.//w:r', NS):
                        if text_of(run) and not matches_color(run_color(structure, p, run), 'FFFFFF'):
                            bad_headers.append(f'table {index}: header text')
        for row in rows:
            for cell in row.findall('w:tc', NS):
                if not text_of(cell):
                    continue
                valign = cell.find('w:tcPr/w:vAlign', NS)
                if valign is None or valign.get(q('val')) != 'center':
                    bad_alignment.append(f'table {index}: vertical')
                for p in cell.findall('.//w:p', NS):
                    align = structure.effective(p, 'w:pPr/w:jc')
                    if text_of(p) and (align is None or align.get(q('val')) != 'center'):
                        bad_alignment.append(f'table {index}: horizontal')
    if bad_headers:
        audit.fail('Report table headers must be NAVY/white without theme overrides: ' + '; '.join(sorted(set(bad_headers))[:6]))
    else:
        audit.ok(f'All {count} report data-table headers use NAVY and white text')
    if bad_alignment:
        audit.fail('Report table text must be horizontally and vertically centered: ' + '; '.join(sorted(set(bad_alignment))[:6]))
    else:
        audit.ok('All report table text is horizontally and vertically centered')


def page_number_runs(paragraph) -> list:
    """Find PAGEREF results and tab-delimited native TOC page text, not chapter labels."""
    parents = {child: parent for parent in paragraph.iter() for child in parent}
    result = set()
    def add_text(node):
        current = node
        while current in parents and current.tag != q('r'):
            current = parents[current]
        if current.tag == q('r') and (node.text or '').strip():
            result.add(current)
    for field in paragraph.findall('.//w:fldSimple', NS):
        if re.search(r'\bPAGEREF\b', field.get(q('instr'), ''), re.I):
            for node in field.iter(q('t')):
                add_text(node)
    fields = []
    for node in paragraph.iter():
        if node.tag == q('fldChar'):
            kind = node.get(q('fldCharType'))
            if kind == 'begin':
                fields.append({'instruction': '', 'result': False})
            elif kind == 'separate' and fields:
                fields[-1]['result'] = True
            elif kind == 'end' and fields:
                fields.pop()
        elif node.tag == q('instrText') and fields:
            fields[-1]['instruction'] += node.text or ''
        elif node.tag == q('t') and fields and fields[-1]['result'] and re.search(r'\bPAGEREF\b', fields[-1]['instruction'], re.I):
            add_text(node)
    nodes = list(paragraph.iter())
    tabs = [i for i, node in enumerate(nodes) if node.tag == q('tab')]
    if tabs:
        tail = [n for n in nodes[tabs[-1] + 1:] if n.tag == q('t')]
        if re.fullmatch(r'\d+', ''.join(n.text or '' for n in tail).strip()):
            for node in tail:
                add_text(node)
    return list(result)


def audit_toc_page_colors(path: Path, audit) -> None:
    structure = Structure(path)
    bad, count = [], 0
    for block in structure.blocks:
        if not block.navigation:
            continue
        for run in page_number_runs(block.element):
            count += 1
            if not matches_color(run_color(structure, block.element, run), NAVY):
                bad.append(text_of(block.element)[:55])
    if bad:
        audit.fail('TOC page-number colors must all be NAVY without theme overrides: ' + '; '.join(bad[:6]))
    elif count:
        audit.ok(f'All {count} TOC page-number runs use consistent NAVY')


def audit_image_paragraphs(path: Path, audit) -> None:
    structure = Structure(path)
    flags = ('keepNext', 'keepLines', 'pageBreakBefore', 'suppressLineNumbers')
    failures, count = [], 0
    for paragraph in structure.document.iter(q('p')):
        if paragraph.find('.//' + q('drawing')) is None and paragraph.find('.//' + q('pict')) is None:
            continue
        count += 1
        if re.match(r'^[\s\u200b]*[■▪●•◆□◼]', text_of(paragraph)):
            failures.append('literal square/bullet')
        num = structure.effective(paragraph, 'w:pPr/w:numPr/w:numId')
        if num is not None and num.get(q('val')) != '0':
            failures.append('inherited/direct list numbering')
        for flag in flags:
            node = structure.effective(paragraph, f'w:pPr/w:{flag}')
            if node is None:
                node = structure.styles_root.find(f'w:docDefaults/w:pPrDefault/w:pPr/w:{flag}', NS)
            if node is not None and node.get(q('val'), 'true').lower() not in {'0', 'false', 'off'}:
                failures.append(flag)
    if failures:
        audit.fail('Image paragraphs contain square-marker causes: ' + ', '.join(sorted(set(failures))))
    elif count:
        audit.ok(f'All {count} image-host paragraphs are free of known square/list marker causes')
        audit.warn('Image paragraph markers still require native Word UI and caption/pagination review')
