"""Read native DOCX outline and TOC membership without treating contents as chapters.

Standard-library only. Shared by content/layout and depth audits.
"""
from __future__ import annotations

import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


def q(name: str) -> str:
    return f"{{{W}}}{name}"


def text_of(el) -> str:
    return "".join(t.text or "" for t in el.iter(q("t"))).strip()


def chapter_number(text: str) -> int | None:
    # Delimiters belong to display style, not chapter semantics. Never match 2.1.
    match = re.match(r"^(?:§\s*)?(\d{1,2})(?:[.．、]\s+|\s+)(\S.*)$", text.strip())
    if match:
        number = int(match.group(1))
        return number if 1 <= number <= 16 else None
    match = re.match(r"^第\s*([\d一二三四五六七八九十]+)\s*章\s*\S", text.strip())
    if match:
        value = match.group(1)
        nums = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6,
                "七": 7, "八": 8, "九": 9, "十": 10}
        number = int(value) if value.isdigit() else (
            10 + nums.get(value[1:], 0) if value.startswith("十") else nums.get(value, 0))
        return number if 1 <= number <= 16 else None
    return None


@dataclass
class Block:
    element: ET.Element
    heading_level: int | None
    navigation: bool


class Structure:
    def __init__(self, path: Path):
        with zipfile.ZipFile(path) as z:
            self.document = ET.fromstring(z.read("word/document.xml"))
            self.styles_root = ET.fromstring(z.read("word/styles.xml"))
            self.numbering = ET.fromstring(z.read("word/numbering.xml")) if "word/numbering.xml" in z.namelist() else ET.Element("numbering")
        self.styles = {s.get(q("styleId")): s for s in self.styles_root.findall("w:style", NS)}
        self.body = self.document.find("w:body", NS)
        self.blocks: list[Block] = []
        stack: list[dict] = []

        def walk(parent, inherited_nav=False):
            for el in parent:
                if el.tag == q("sdt"):
                    gallery = el.find("w:sdtPr/w:docPartObj/w:docPartGallery", NS)
                    nav = inherited_nav or (gallery is not None and "contents" in (gallery.get(q("val")) or "").lower())
                    content = el.find("w:sdtContent", NS)
                    if content is not None:
                        yield from walk(content, nav)
                elif el.tag in {q("p"), q("tbl")}:
                    yield el, inherited_nav

        for el, inherited_nav in walk(self.body if self.body is not None else []):
            nav = inherited_nav or any(x['toc'] for x in stack)
            for node in el.iter():
                if node.tag == q("fldChar"):
                    kind = node.get(q("fldCharType"))
                    if kind == "begin":
                        stack.append({'instruction': '', 'toc': False})
                    elif kind == "end" and stack:
                        stack.pop()
                elif node.tag == q("instrText") and stack:
                    stack[-1]['instruction'] += node.text or ''
                    if re.match(r"\s*TOC\b", stack[-1]['instruction'], re.I):
                        stack[-1]['toc'] = True
                        nav = True
            chain = self.style_chain(el)
            names = [s.get(q("styleId"), "") for s in chain]
            names += [(s.find("w:name", NS).get(q("val"), "")) for s in chain if s.find("w:name", NS) is not None]
            if any(re.match(r"^(?:TOC\s*\d+|ReportTOC|目录\s*\d*)$", n, re.I) for n in names):
                nav = True
            # Custom linked contents often use Normal + PAGEREF, without a TOC field.
            instructions = " ".join((n.text or "") for n in el.iter(q("instrText")))
            instructions += " " + " ".join(n.get(q("instr"), "") for n in el.iter(q("fldSimple")))
            numbered_label = re.match(r'^(?:§\s*)?(?:\d{1,2}(?:[.．、]\s+|\s+)|[A-EMS](?:[.．、｜|]\s*|\s+)|Appendix\b|附录)', text_of(el), re.I)
            if numbered_label and el.find(".//w:hyperlink[@w:anchor]", NS) is not None and re.search(r"\bPAGEREF\b", instructions, re.I) and self.heading_level(el) is None:
                nav = True
            self.blocks.append(Block(el, self.heading_level(el), nav))

    def style_chain(self, paragraph) -> list[ET.Element]:
        sid = paragraph.find("w:pPr/w:pStyle", NS)
        key = sid.get(q("val")) if sid is not None else "Normal"
        chain = []
        seen = set()
        while key and key not in seen and key in self.styles:
            seen.add(key)
            st = self.styles[key]
            chain.append(st)
            base = st.find("w:basedOn", NS)
            key = base.get(q("val")) if base is not None else None
        return chain

    def effective(self, paragraph, path: str):
        for root in [paragraph] + self.style_chain(paragraph):
            node = root.find(path, NS)
            if node is not None:
                return node
        return None

    def heading_level(self, paragraph) -> int | None:
        if paragraph.tag != q("p"):
            return None
        level = self.effective(paragraph, "w:pPr/w:outlineLvl")
        if level is not None:
            value = level.get(q("val"), "9")
            return int(value) + 1 if value.isdigit() and int(value) < 9 else None
        for st in self.style_chain(paragraph):
            name = st.find("w:name", NS)
            for label in (st.get(q("styleId"), ""), name.get(q("val"), "") if name is not None else ""):
                match = re.match(r"^(?:Heading|标题)\s*([1-9])$", label, re.I)
                if match:
                    return int(match.group(1))
        return None

    def is_bullet(self, paragraph) -> bool:
        # numId and ilvl inherit independently; numId=0 explicitly cancels a list.
        num = self.effective(paragraph, "w:pPr/w:numPr/w:numId")
        if num is None or num.get(q("val")) == "0":
            return False
        level = self.effective(paragraph, "w:pPr/w:numPr/w:ilvl")
        ilvl = level.get(q("val"), "0") if level is not None else "0"
        item = self.numbering.find(f"w:num[@w:numId='{num.get(q('val'))}']", NS)
        if item is None:
            return False
        override = item.find(f"w:lvlOverride[@w:ilvl='{ilvl}']/w:lvl/w:numFmt", NS)
        if override is not None:
            return override.get(q("val")) == "bullet"
        abstract = item.find("w:abstractNumId", NS)
        if abstract is None:
            return False
        fmt = self.numbering.find(f"w:abstractNum[@w:abstractNumId='{abstract.get(q('val'))}']/w:lvl[@w:ilvl='{ilvl}']/w:numFmt", NS)
        return fmt is not None and fmt.get(q("val")) == "bullet"
