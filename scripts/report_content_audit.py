#!/usr/bin/env python3
"""Audit reader-facing DOCX structure introduced in skill v2.1.

Checks numeric citation architecture, source appendix, chapter placement,
cover-table formatting, non-duplicative competition analysis, product/revenue-mix
image markers, and management-profile depth signals.
Uses only the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W, "wp": WP, "a": A}

CHAPTER_RE = re.compile(r"^(?:§\s*)?(\d{1,2})\.\s+\S")
SUB_RE = re.compile(r"^(\d{1,2})\.(\d{1,2})(?:\.(\d{1,2}))?\s+(.+)")
SOURCE_APPENDIX_RE = re.compile(
    r"^(?:Appendix|附录)\s*(?:[｜|:：—\-]\s*)?(?:Sources?|来源索引|参考来源|Source Index)\b",
    re.I,
)
URL_RE = re.compile(r"https?://|www\.", re.I)
VISIBLE_SOURCE_RE = re.compile(r"(?:^|[。；;]\s*)(?:来源|Source)\s*[：:]", re.I)
CITATION_RE = re.compile(r"\[(\d+(?:\s*[,，]\s*\d+)*)\]")
SOURCE_ENTRY_RE = re.compile(r"^\[(\d+)\]\s*\S")
GUIDANCE_RE = re.compile(r"guidance\s*(?:演变|历史|兑现)|指引(?:演变|兑现|可信度)", re.I)
GLOSSARY_RE = re.compile(r"(?:行业)?术语(?:速览|表)|Glossary", re.I)
RISK_WORD_RE = re.compile(r"风险|未验证|局限|依赖|待观察|挑战|隐患|失败")
NUM_RE = re.compile(r"\d")


@dataclass
class Para:
    text: str
    superscript_citations: set[int] = field(default_factory=set)
    image_alts: list[str] = field(default_factory=list)
    kind: str = "p"


@dataclass
class Audit:
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    passes: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.failures.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def ok(self, msg: str) -> None:
        self.passes.append(msg)

    def print(self) -> int:
        for x in self.passes:
            print("[PASS] " + x)
        for x in self.warnings:
            print("[WARN] " + x)
        for x in self.failures:
            print("[FAIL] " + x)
        print(
            f"SUMMARY: {len(self.passes)} PASS / {len(self.warnings)} WARN / "
            f"{len(self.failures)} FAIL"
        )
        return 1 if self.failures else 0


def text_of(el) -> str:
    return "".join(t.text or "" for t in el.iter(f"{{{W}}}t")).strip()


def run_is_superscript(run) -> bool:
    node = run.find(f".//{{{W}}}vertAlign")
    return node is not None and node.attrib.get(f"{{{W}}}val") == "superscript"


def parse_docx(path: Path) -> list[Para]:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{{{W}}}body")
    out: list[Para] = []
    if body is None:
        return out
    for el in list(body):
        tag = el.tag.rsplit("}", 1)[-1]
        if tag not in {"p", "tbl"}:
            continue
        citations: set[int] = set()
        for run in el.findall(f".//{{{W}}}r"):
            if not run_is_superscript(run):
                continue
            run_text = text_of(run)
            for match in CITATION_RE.findall(run_text):
                citations.update(int(x) for x in re.split(r"\s*[,，]\s*", match))
        alts: list[str] = []
        for docpr in el.findall(f".//{{{WP}}}docPr"):
            for key in ("descr", "title", "name"):
                value = (docpr.attrib.get(key) or "").strip()
                if value:
                    alts.append(value)
        out.append(Para(text=text_of(el), superscript_citations=citations, image_alts=alts, kind=tag))
    return out


def audit_cover_tables(path: Path, audit: Audit) -> None:
    """Require every pre-§1 cover table cell to be centered and every text run to be 12 pt."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(f"{{{W}}}body")
    if body is None:
        audit.fail("Cannot locate DOCX body for cover-table formatting audit")
        return
    elements = list(body)
    first_chapter = len(elements)
    for i, el in enumerate(elements):
        if el.tag.rsplit("}", 1)[-1] != "p":
            continue
        text = text_of(el)
        match = CHAPTER_RE.match(text)
        if match and int(match.group(1)) == 1 and not SUB_RE.match(text):
            first_chapter = i
            break
    tables = [el for el in elements[:first_chapter] if el.tag.rsplit("}", 1)[-1] == "tbl"]
    if not tables:
        audit.fail("Cover is missing the judgment-card/summary table")
        return
    alignment_failures = 0
    size_failures = 0
    text_runs = 0
    for table in tables:
        for cell in table.findall(f".//{{{W}}}tc"):
            cell_text = text_of(cell)
            if not cell_text:
                continue
            valign = cell.find(f"./{{{W}}}tcPr/{{{W}}}vAlign")
            if valign is None or valign.attrib.get(f"{{{W}}}val") != "center":
                alignment_failures += 1
            for paragraph in cell.findall(f"./{{{W}}}p"):
                if not text_of(paragraph):
                    continue
                jc = paragraph.find(f"./{{{W}}}pPr/{{{W}}}jc")
                if jc is None or jc.attrib.get(f"{{{W}}}val") != "center":
                    alignment_failures += 1
                for run in paragraph.findall(f"./{{{W}}}r"):
                    if not text_of(run):
                        continue
                    text_runs += 1
                    size = run.find(f"./{{{W}}}rPr/{{{W}}}sz")
                    if size is None or size.attrib.get(f"{{{W}}}val") != "24":
                        size_failures += 1
    if alignment_failures:
        audit.fail(f"Cover table has {alignment_failures} non-centered cell/paragraph setting(s)")
    else:
        audit.ok("Cover table text is horizontally and vertically centered")
    if not text_runs:
        audit.fail("Cover table contains no auditable text runs")
    elif size_failures:
        audit.fail(f"Cover table has {size_failures} text run(s) not explicitly set to 12 pt")
    else:
        audit.ok(f"All {text_runs} cover-table text run(s) are explicitly 12 pt")


def chapter_ranges(paras: list[Para]) -> dict[int, tuple[int, int]]:
    starts: list[tuple[int, int]] = []
    current = 0
    for i, p in enumerate(paras):
        text = p.text.strip()
        match = CHAPTER_RE.match(text)
        if not match or SUB_RE.match(text) or len(text) > 100:
            continue
        n = int(match.group(1))
        if 1 <= n <= 16 and n > current:
            starts.append((n, i))
            current = n
    ranges: dict[int, tuple[int, int]] = {}
    for idx, (n, start) in enumerate(starts):
        end = starts[idx + 1][1] if idx + 1 < len(starts) else len(paras)
        ranges[n] = (start, end)
    return ranges


def range_text(paras: list[Para], bounds: tuple[int, int] | None) -> str:
    if not bounds:
        return ""
    return "\n".join(p.text for p in paras[bounds[0] : bounds[1]])


def image_alts(paras: list[Para], bounds: tuple[int, int] | None) -> list[str]:
    if not bounds:
        return []
    return [alt for p in paras[bounds[0] : bounds[1]] for alt in p.image_alts]


def subsection_range(
    paras: list[Para], chapter_bounds: tuple[int, int] | None, chapter: int, subsection: int
) -> tuple[int, int] | None:
    if not chapter_bounds:
        return None
    ch_start, ch_end = chapter_bounds
    start = None
    for i in range(ch_start, ch_end):
        match = SUB_RE.match(paras[i].text.strip())
        if match and int(match.group(1)) == chapter and int(match.group(2)) == subsection and match.group(3) is None:
            start = i
            break
    if start is None:
        return None
    end = ch_end
    for i in range(start + 1, ch_end):
        match = SUB_RE.match(paras[i].text.strip())
        if match and int(match.group(1)) == chapter and int(match.group(2)) != subsection and match.group(3) is None:
            end = i
            break
    return start, end


def audit_manifest(path: Path | None, audit: Audit) -> None:
    if path is None:
        audit.fail("Full-report gate requires --charts-manifest")
        return
    if not path.exists():
        audit.fail(f"Charts manifest not found: {path}")
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        audit.fail(f"Cannot parse charts manifest: {exc}")
        return
    charts = data.get("charts") if isinstance(data, dict) else None
    if not isinstance(charts, list) or not charts:
        audit.fail("charts_manifest.json must contain a non-empty charts array")
        return
    bad_overlap = [c.get("filename", "<unnamed>") for c in charts if c.get("overlap_check") != "PASS"]
    bad_visual = [c.get("filename", "<unnamed>") for c in charts if c.get("visual_check") != "PASS"]
    missing_sources = [c.get("filename", "<unnamed>") for c in charts if not c.get("source_ids")]
    if bad_overlap:
        audit.fail("Charts without overlap_check=PASS: " + ", ".join(bad_overlap))
    else:
        audit.ok(f"All {len(charts)} charts record overlap_check=PASS")
    if bad_visual:
        audit.fail("Charts without visual_check=PASS: " + ", ".join(bad_visual))
    else:
        audit.ok("All charts record visual_check=PASS")
    if missing_sources:
        audit.fail("Charts missing source_ids: " + ", ".join(missing_sources))
    else:
        audit.ok("All charts retain backstage source IDs")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--charts-manifest", type=Path)
    args = parser.parse_args()
    audit = Audit()

    if not args.report.exists():
        audit.fail(f"Report not found: {args.report}")
        return audit.print()
    try:
        paras = parse_docx(args.report)
    except Exception as exc:
        audit.fail(f"Cannot parse DOCX: {exc}")
        return audit.print()
    if not paras:
        audit.fail("DOCX contains no readable body content")
        return audit.print()

    audit_cover_tables(args.report, audit)

    source_start = next((i for i, p in enumerate(paras) if SOURCE_APPENDIX_RE.match(p.text.strip())), None)
    if source_start is None:
        audit.fail("Missing final top-level 'Appendix｜Sources / 来源索引'")
        source_start = len(paras)
    else:
        audit.ok("Sources Appendix is present")
        comp_positions = [
            i for i, p in enumerate(paras)
            if re.match(r"^(?:Appendix|附录)\s*[A-E]\b", p.text.strip(), re.I)
        ]
        if comp_positions and source_start <= max(comp_positions):
            audit.fail("Sources Appendix must appear after all comparable-company appendices")
        else:
            audit.ok("Sources Appendix appears after comparable-company appendices")

    body = paras[:source_start]
    source_paras = paras[source_start + 1 :]
    body_text = "\n".join(p.text for p in body)
    urls = URL_RE.findall(body_text)
    if urls:
        audit.fail(f"Body contains raw URL(s): {len(urls)} occurrence(s)")
    else:
        audit.ok("Body contains no raw URLs")
    source_lines = [p.text[:100] for p in body if VISIBLE_SOURCE_RE.search(p.text)]
    if source_lines:
        audit.fail("Body contains visible source lines, e.g. " + repr(source_lines[0]))
    else:
        audit.ok("Body uses no visible '来源：/Source:' lines")

    used = set().union(*(p.superscript_citations for p in body)) if body else set()
    entries: dict[int, str] = {}
    for p in source_paras:
        match = SOURCE_ENTRY_RE.match(p.text.strip())
        if match:
            entries[int(match.group(1))] = p.text.strip()
    if not used:
        audit.fail("No superscript numeric citation markers found in body")
    else:
        audit.ok(f"Found {len(used)} unique superscript citation number(s)")
    missing = sorted(used - set(entries))
    if missing:
        audit.fail("Body citation(s) missing from Sources Appendix: " + ", ".join(map(str, missing)))
    elif used:
        audit.ok("Every body citation resolves to a Sources Appendix entry")
    unused = sorted(set(entries) - used)
    if unused:
        audit.warn("Unused Sources Appendix entries: " + ", ".join(map(str, unused[:20])))
    short_entries = [n for n, text in entries.items() if len(re.sub(r"\s", "", text)) < 35]
    if short_entries:
        audit.fail("Source entries lack full provenance: " + ", ".join(map(str, short_entries)))
    elif entries:
        audit.ok("Source Appendix entries contain substantive provenance")

    ranges = chapter_ranges(paras)
    t2 = range_text(paras, ranges.get(2))
    t3 = range_text(paras, ranges.get(3))
    t9 = range_text(paras, ranges.get(9))
    if GLOSSARY_RE.search(t2):
        audit.fail("§2 contains a glossary/terminology table; glossary must be consolidated in §3")
    else:
        audit.ok("§2 has no duplicate glossary section")
    if not GLOSSARY_RE.search(t3):
        audit.fail("§3 is missing the single consolidated glossary")
    else:
        audit.ok("§3 contains the consolidated glossary")
    if GUIDANCE_RE.search(t3):
        audit.fail("Guidance history is in §3; move it to §9")
    else:
        audit.ok("§3 contains no guidance-history block")
    if not GUIDANCE_RE.search(t9):
        audit.fail("§9 is missing five-call guidance evolution/credibility analysis")
    else:
        audit.ok("§9 contains guidance evolution/credibility analysis")

    product = [x for x in image_alts(paras, ranges.get(4)) if x.upper().startswith("PRODUCT_IMAGE:")]
    if not 2 <= len(product) <= 3:
        audit.fail(f"§4 requires 2–3 PRODUCT_IMAGE alt-text markers; found {len(product)}")
    else:
        audit.ok(f"§4 contains {len(product)} auditable product image(s)")

    revenue_mix = [x for x in image_alts(paras, ranges.get(8)) if x.upper().startswith("CHART_REVENUE_MIX:")]
    if not revenue_mix:
        audit.fail("§8 is missing a CHART_REVENUE_MIX alt-text marker")
    else:
        audit.ok("§8 contains the mandatory revenue-mix chart")

    competition = [x for x in image_alts(paras, ranges.get(7)) if x.upper().startswith("CHART_COMPETITION:")]
    if not competition:
        audit.fail("§7 is missing the CHART_COMPETITION score-matrix figure")
    else:
        audit.ok("§7 contains the mandatory competition score-matrix figure")
    s71_bounds = subsection_range(paras, ranges.get(7), 7, 1)
    if s71_bounds is None:
        audit.fail("§7.1 competition interpretation subsection is missing")
    else:
        s71 = paras[s71_bounds[0] + 1 : s71_bounds[1]]
        s71_tables = [p for p in s71 if p.kind == "tbl"]
        prose = "".join(p.text for p in s71 if p.kind == "p" and not p.image_alts)
        prose_chars = len(re.sub(r"\s", "", prose))
        if s71_tables:
            audit.fail("§7.1 contains a duplicate matrix/table; keep only prose plus CHART_COMPETITION")
        else:
            audit.ok("§7.1 contains no duplicate matrix table")
        if prose_chars < 250:
            audit.fail(f"§7.1 competition interpretation is too shallow ({prose_chars}<250 non-space characters)")
        else:
            audit.ok(f"§7.1 provides substantive prose interpretation ({prose_chars} characters)")

    if 9 not in ranges:
        audit.fail("§9 is missing")
    else:
        start, end = ranges[9]
        profiles: list[tuple[str, str]] = []
        local = paras[start:end]
        all_headings: list[int] = []
        profile_starts: list[tuple[int, str]] = []
        for i, p in enumerate(local):
            match = SUB_RE.match(p.text.strip())
            if not match:
                continue
            all_headings.append(i)
            if match.group(1) == "9" and match.group(2) == "3" and match.group(3):
                profile_starts.append((i, p.text.strip()))
        for i, heading in profile_starts:
            stop = next((pos for pos in all_headings if pos > i), len(local))
            content = " ".join(p.text for p in local[i + 1 : stop])
            profiles.append((heading, content))
        if len(profiles) < 5:
            audit.fail(f"§9 requires at least 5 numbered H3 management profiles (9.x.x); found {len(profiles)}")
        else:
            audit.ok(f"§9 contains {len(profiles)} management profile block(s)")
        shallow = [h for h, c in profiles if len(re.sub(r"\s", "", c)) < 120 or not NUM_RE.search(c) or not RISK_WORD_RE.search(c)]
        if shallow:
            audit.fail("Management profiles missing depth/quantification/risk: " + "; ".join(shallow[:8]))
        elif profiles:
            audit.ok("Management profiles include quantified track record and an unresolved risk")

    audit_manifest(args.charts_manifest, audit)
    return audit.print()


if __name__ == "__main__":
    sys.exit(main())
