"""Mechanical house-layout checks. Rendering and native Word UI remain human QA."""
from __future__ import annotations

import json
import re
from pathlib import Path

from docx_structure import NS, Structure, chapter_number, q, text_of


def has_page_cache(el) -> bool:
    found = False
    for fld in el.iter(q('fldSimple')):
        if re.search(r'\bPAGEREF\b', fld.get(q('instr'), ''), re.I):
            found = True
            if not re.fullmatch(r'\d+', text_of(fld)):
                return False
    fields = []
    for node in el.iter():
        if node.tag == q('fldChar'):
            kind = node.get(q('fldCharType'))
            if kind == 'begin':
                fields.append({'instruction': '', 'result': '', 'separate': False})
            elif kind == 'separate' and fields:
                fields[-1]['separate'] = True
            elif kind == 'end' and fields:
                fld = fields.pop()
                if re.search(r'\bPAGEREF\b', fld['instruction'], re.I):
                    found = True
                    if not re.fullmatch(r'\d+', fld['result'].strip()):
                        return False
        elif fields and node.tag == q('instrText'):
            fields[-1]['instruction'] += node.text or ''
        elif fields and node.tag == q('t') and fields[-1]['separate']:
            fields[-1]['result'] += node.text or ''
    if found:
        return True
    # Native TOC output can store a tab-separated page inside its hyperlink.
    return el.find('.//w:tab', NS) is not None and bool(re.search(r'\d+\s*$', text_of(el)))


def audit_layout(path: Path, audit) -> None:
    structure = Structure(path)
    palette = json.loads((Path(__file__).resolve().parents[1] / "assets/color_palette.json").read_text(encoding="utf-8"))["primary"]
    colors = {1: palette["NAVY"], 2: palette["BLUE"], 3: palette["SLATE"]}
    headings = [b for b in structure.blocks if not b.navigation and b.heading_level in colors and text_of(b.element)]
    bad_color, bullets = [], []
    for b in headings:
        p = b.element
        label = text_of(p)
        if re.match(r"^[\s\u200b]*[■▪●•◆□◼]\s*", label) or structure.is_bullet(p):
            bullets.append(label[:60])
        expected = colors[b.heading_level].lstrip("#").upper()
        base = structure.effective(p, "w:rPr/w:color")
        for run in p.findall(".//w:r", NS):
            if not text_of(run):
                continue
            direct = run.find("w:rPr/w:color", NS)
            character_style = run.find("w:rPr/w:rStyle", NS)
            styled = None
            key = character_style.get(q("val")) if character_style is not None else None
            seen = set()
            while key in structure.styles and key not in seen:
                seen.add(key)
                st = structure.styles[key]
                styled = st.find("w:rPr/w:color", NS)
                if styled is not None:
                    break
                parent = st.find("w:basedOn", NS)
                key = parent.get(q("val")) if parent is not None else None
            color = direct if direct is not None else styled if styled is not None else base
            if color is None or color.get(q("val"), "").upper() != expected or color.get(q("themeColor")):
                bad_color.append(label[:60])
                break
    if bad_color:
        audit.fail("Heading palette mismatch (including inherited/run/theme overrides): " + "; ".join(bad_color[:6]))
    elif headings:
        audit.ok(f"All {len(headings)} native H1–H3 headings use the house colors")
    if bullets:
        audit.fail("Headings contain unwanted literal or inherited list bullets: " + "; ".join(bullets[:6]))
    else:
        audit.ok("No literal square/bullet or effective bullet list found in headings")

    # Evaluate actual top-level headings, never TOC entries or plain numbered prose.
    top = [b for b in headings if b.heading_level == 1]
    bookmarks = {}
    heading_text = {id(b.element): text_of(b.element) for b in top}
    pending = []
    for b in structure.blocks:
        if b.navigation:
            continue
        names = [n.get(q("name")) for n in b.element.iter(q("bookmarkStart")) if n.get(q("name"))]
        if b.heading_level == 1:
            for name in pending + names:
                bookmarks[name] = id(b.element)
        pending = (pending + names) if not text_of(b.element) else []
    entries = [b for b in structure.blocks if b.navigation and b.element.find(".//w:hyperlink[@w:anchor]", NS) is not None]
    if not entries:
        audit.fail("Missing numbered linked TOC entries with cached page numbers")
        return
    seen = {}
    problems = []
    for b in entries:
        el = b.element
        label = text_of(el)
        # Decimal chapter labels, § labels and explicit appendix A–E/M/S labels.
        if chapter_number(label) is None and not re.match(r"^(?:§\s*)?(?:\d{1,2}(?:[.．、]|\s)|[A-EMS](?:[.．、｜|]|\s)|(?:附录|Appendix)\b)", label, re.I):
            problems.append("unnumbered entry: " + label[:50])
        if b.heading_level is not None:
            problems.append("contents entry uses a native heading style: " + label[:50])
        anchors = {h.get(q("anchor")) for h in el.findall(".//w:hyperlink", NS) if h.get(q("anchor"))}
        targets = {bookmarks[a] for a in anchors if a in bookmarks}
        if len(targets) != 1 or any(a not in bookmarks for a in anchors):
            problems.append("broken/ambiguous heading target: " + label[:50])
        else:
            target = next(iter(targets))
            seen[target] = seen.get(target, 0) + 1
            expected_chapter = chapter_number(heading_text.get(target, ''))
            if expected_chapter is not None and chapter_number(label) != expected_chapter:
                problems.append('chapter label differs from target: ' + label[:50])
        # A visible cached page may be inside a native TOC hyperlink without PAGEREF.
        if not has_page_cache(el):
            problems.append("missing cached page: " + label[:50])
        for node in list(el.iter(q("instrText"))) + list(el.iter(q("fldSimple"))):
            instruction = node.get(q("instr"), node.text or "")
            match = re.search(r'\bPAGEREF\s+(?:"([^"]+)"|(\S+))', instruction, re.I)
            if match and (match.group(1) or match.group(2)) not in anchors:
                problems.append("PAGEREF target differs from hyperlink: " + label[:50])
    required = {id(b.element) for b in top}
    if required - seen.keys():
        problems.append(f"{len(required - seen.keys())} top-level heading(s) absent from contents")
    if any(n != 1 for n in seen.values()) or seen.keys() - required:
        problems.append("duplicate or non-heading TOC destinations")
    if problems:
        audit.fail("TOC structure: " + "; ".join(problems[:10]))
    else:
        audit.ok(f"TOC covers all {len(required)} top-level headings once with numbered links and page caches")
        audit.warn("TOC page caches require final rendered/native page comparison; XML cannot prove freshness")
