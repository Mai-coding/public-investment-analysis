#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
AUDIT = HERE / "report_content_audit.py"
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Y9ZQMcAAAAASUVORK5CYII="
)


def add_citation(paragraph, number: int) -> None:
    run = paragraph.add_run(f"[{number}]")
    run.font.superscript = True


def add_image(doc: Document, image: Path, alt: str) -> None:
    run = doc.add_paragraph().add_run()
    inline = run.add_picture(str(image), width=Inches(0.2))
    inline._inline.docPr.set("descr", alt)


def apply_house_fonts(doc: Document) -> None:
    doc.styles["Normal"].element.get_or_add_rPr().get_or_add_rFonts()
    for root in (doc.styles.element, doc.element.body):
        for rf in root.iter(qn("w:rFonts")):
            for k in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
                rf.attrib.pop(qn("w:" + k), None)
            for k in ("ascii", "hAnsi", "cs"):
                rf.set(qn("w:" + k), "Times New Roman")
            rf.set(qn("w:eastAsia"), "楷体")


def apply_layout(doc: Document) -> None:
    for level, color in enumerate(('061F32', '2F80ED', '5B6573'), 1):
        doc.styles[f'Heading {level}'].font.color.rgb = RGBColor.from_string(color)
    style = doc.styles.add_style('ReportTOC', 1)
    style.base_style = doc.styles['Normal']
    headings = [p for p in doc.paragraphs if p.style.name == 'Heading 1']
    for i, heading in enumerate(headings):
        anchor = f'report_heading_{i}'
        start = OxmlElement('w:bookmarkStart')
        start.set(qn('w:id'), str(i + 100))
        start.set(qn('w:name'), anchor)
        heading._p.insert(1, start)
        end = OxmlElement('w:bookmarkEnd'); end.set(qn('w:id'), str(i + 100)); heading._p.append(end)
        entry = headings[0].insert_paragraph_before(style='ReportTOC')
        link = OxmlElement('w:hyperlink'); link.set(qn('w:anchor'), anchor)
        run = OxmlElement('w:r'); text = OxmlElement('w:t')
        prefix = 'M' if 'Methods' in heading.text else 'S' if 'Sources' in heading.text else f'{int(heading.text.split(".")[0]):02d}'
        text.text = f'{prefix} {heading.text} '; run.append(text); link.append(run)
        fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), f'PAGEREF {anchor} \\h')
        run = OxmlElement('w:r'); props = OxmlElement('w:rPr'); color = OxmlElement('w:color'); color.set(qn('w:val'), '061F32'); props.append(color); run.append(props); text = OxmlElement('w:t'); text.text = str(i + 2); run.append(text); fld.append(run); link.append(fld)
        entry._p.append(link)


def build(path: Path, image: Path, legacy_order: bool = False) -> None:
    doc = Document()
    add_image(doc, image, 'COMPANY_LOGO: Test Company')
    cover = doc.add_table(rows=2, cols=3)
    for row, texts in zip(cover.rows, (("Price", "Return", "Overall judgment"), ("Current price: 57 USD; Base case: 65–82 USD", "Base 12% CAGR", "Wait｜7.5/10"))):
        for cell, text in zip(row.cells, texts):
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = paragraph.add_run(text)
            run.font.size = Pt(12)
    doc.add_heading("1. 投资概要", level=1)
    doc.add_paragraph("现价所在 Price Band、3 年预期回报和主要风险在此汇总。")
    for number, role in enumerate(("history", "technical") if legacy_order else ("technical", "history"), 2):
        if role == "history":
            doc.add_heading(f"{number}. 行业纵向叙事", level=1)
            p = doc.add_paragraph("行业变化有量化证据。")
            add_citation(p, 1)
        else:
            doc.add_heading(f"{number}. 核心技术入门", level=1)
            doc.add_heading(f"{number}.1 技术机制", level=2)
            doc.add_paragraph("技术解释。")
            doc.add_heading(f"{number}.2 术语表", level=2)
            doc.add_paragraph("DSP：信号处理。")
    doc.add_heading("4. 产品分析", level=1)
    doc.add_heading("4.1 主力产品", level=2)
    doc.add_paragraph("产品说明。")
    add_image(doc, image, "PRODUCT_IMAGE: core product")
    add_image(doc, image, "PRODUCT_IMAGE: second-curve product")
    doc.add_heading("7. 竞争横向叙事", level=1)
    doc.add_heading("7.1 竞争格局解释", level=2)
    doc.add_paragraph(
        "竞争评分的意义不在于宣布一家公司在所有维度都领先，而在于解释优势能否转化为持续回报。"
        "测试公司在产品完整度和客户粘性上得分较高，因为过去三年续约率稳定、核心产品迭代速度更快，"
        "但渠道覆盖和单位成本仍落后于规模最大的对手。该差距意味着基准情景需要持续投入销售和基础设施，"
        "不能把较高毛利率直接外推为份额扩张。若未来四个季度新增客户放缓、销售效率下降或竞争对手通过"
        "捆绑定价缩小功能差异，当前评分应下调并同步降低收入增速与估值倍数；反之，若续约、交叉销售和"
        "单位成本连续改善，优势才算通过经营数据验证。图中的分数因此是待证伪的研究假设，不是静态排名。"
    )
    add_image(doc, image, "CHART_COMPETITION: score matrix")
    doc.add_heading('7.5 竞争格局四象限', level=2)
    doc.add_paragraph('定性定位示意：服务广度与客户关系控制力两轴解释替代路径。')
    add_image(doc, image, 'CHART_COMPETITION_QUADRANT: positioning')
    doc.add_heading("8. 商业模式", level=1)
    doc.add_heading("8.1 收入结构", level=2)
    doc.add_paragraph("收入结构与迁移。")
    add_image(doc, image, "CHART_REVENUE_MIX: history and forecast")
    doc.add_heading("9. 管理层、治理与执行可信度", level=1)
    for i, role in enumerate(("CEO", "CFO", "COO", "CTO", "President"), 1):
        doc.add_heading(f"9.3.{i} Executive {i}｜{role}", level=3)
        doc.add_paragraph(
            f"201{i} 年加入，负责关键业务、客户交付和资源配置，并在 3 年内推动收入增长 25%、"
            "经营利润率提升 4 个百分点。他通过聚焦核心产品、削减低协同项目和建立季度复盘机制形成"
            "较强执行风格；未来两年负责把新产品从设计赢单推进到规模量产。风险是关键项目仍未验证，"
            "客户续约与供应链交付存在依赖，若下一代收入延迟两个季度，其历史能力未必足以抵消。"
        )
    doc.add_heading("9.5 Guidance 演变与可信度", level=2)
    doc.add_paragraph("最近五次指引与实际逐期比较，区分短期兑现和长期目标。")
    doc.add_heading("12. Price Band 与情景", level=1)
    doc.add_heading("12.5 Price Band Decision Map", level=2)
    band_table = doc.add_table(rows=2, cols=4)
    for cell, text in zip(band_table.rows[0].cells, ("Price Band", "Distance", "Robustness", "Actionability")):
        cell.text = text
    for cell, text in zip(band_table.rows[1].cells, ("$80–95 Base", "Low", "High", "Initiate")):
        cell.text = text
    doc.add_paragraph("Expected 3Y Return：每股 EPS CAGR 10% + 股息率 1% + 年化倍数变化 1% ≈ 12%。")
    doc.add_heading('12.5.1 Condition Evidence', level=3)
    doc.add_paragraph('条件验证：未来两季留存率稳定；已披露来源支持基准，份额提升仅部分验证。')
    doc.add_heading('12.5.2 Decision Position', level=3)
    doc.add_paragraph('Market-priced Band: Base+; Evidence-supported Band: Base; Confidence: Medium. 市场比已有证据更乐观。')
    doc.add_heading('Appendix｜Methods / 定义与方法', level=1)
    doc.add_paragraph('精确值与定义：原始口径 EPS 11.52347；模型单位为百万美元。')
    doc.add_heading("Appendix｜Sources / 来源索引", level=1)
    doc.add_paragraph(
        "[1] Test Company. FY2026 Annual Report. Form 10-K, 2026-03-01. "
        "Locator: Item 7, page 42. https://example.com/report. Accessed 2026-07-26."
    )
    for table in doc.tables:
        for row_index, row in enumerate(table.rows):
            for cell in row.cells:
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                if row_index == 0:
                    shading = OxmlElement('w:shd'); shading.set(qn('w:fill'), '061F32')
                    cell._tc.get_or_add_tcPr().append(shading)
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.color.rgb = RGBColor.from_string('FFFFFF')
    apply_layout(doc)
    apply_house_fonts(doc)
    doc.save(path)


def run_audit(report, manifest):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(AUDIT), "--report", str(report), "--charts-manifest", str(manifest)],
        text=True, capture_output=True, encoding="utf-8",
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        image = root / "pixel.png"
        image.write_bytes(PNG)
        report = root / "pass.docx"
        build(report, image)
        manifest = root / "charts_manifest.json"
        manifest.write_text(json.dumps({"charts": [{
            "filename": "revenue_mix.png",
            "source_ids": ["SRC-1"],
            "overlap_check": "PASS",
            "visual_check": "PASS"
        }, {
            'filename': 'quadrant.png', 'section': '7.5', 'source_ids': ['SRC-1'],
            'source_snapshot': '2026-10-18', 'model_ranges': [],
            'overlap_check': 'PASS', 'visual_check': 'PASS',
            'alt_text': 'CHART_COMPETITION_QUADRANT: positioning',
            'positioning_mode': 'qualitative', 'target_name': 'Target',
            'axes': {a: {'label': label, 'definition': 'Defined relative product capability',
                         'scale': 'narrow / broad', 'split_basis': 'disclosed capability boundary'}
                     for a, label in (('x', 'Breadth'), ('y', 'Customer control'))},
            'positioning_evidence': [{'name': name, 'basis': 'Disclosed product capabilities', 'source_ids': ['SRC-1']}
                                     for name in ('Target', 'Rival')]
        }]}), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(AUDIT), "--report", str(report), "--charts-manifest", str(manifest)],
            text=True, capture_output=True, encoding="utf-8"
        )
        if result.returncode:
            print(result.stdout)
            print(result.stderr)
            return result.returncode
        assert "SUMMARY:" in result.stdout and "0 FAIL" in result.stdout
        # Real prior reports remain valid when chapter roles swap numbers.
        old_order = root / "old_order.docx"
        build(old_order, image, legacy_order=True)
        result = run_audit(old_order, manifest)
        assert result.returncode == 0, result.stdout
        for name, mutation, expected in [
            ("missing_glossary", lambda d: setattr(next(p for p in d.paragraphs if p.text == "2.2 术语表"), "text", "2.2 技术索引"), "missing the single consolidated glossary"),
            ("duplicate_glossary", lambda d: next(p for p in d.paragraphs if p.text == "行业变化有量化证据。[1]").insert_paragraph_before("3.1 术语表"), "History contains a glossary"),
            ("wrong_guidance", lambda d: next(p for p in d.paragraphs if p.text == "3. 行业纵向叙事").insert_paragraph_before("指引演变与可信度"), "Guidance history is in the technical introduction"),
            ("missing_role", lambda d: setattr(next(p for p in d.paragraphs if p.text == "2. 核心技术入门"), "text", "2. 背景概览"), "Expected one technical"),
            ("ambiguous_role", lambda d: setattr(next(p for p in d.paragraphs if p.text == "3. 行业纵向叙事"), "text", "3. 技术基础"), "Expected one technical introduction chapter; found 2"),
        ]:
            changed = Document(str(report)); mutation(changed)
            path = root / f"{name}.docx"; changed.save(path)
            failed = run_audit(path, manifest)
            assert failed.returncode and expected in failed.stdout, (name, failed.stdout)
        legacy = root / "legacy.docx"
        doc = Document(str(report))
        for p in doc.paragraphs:
            if p.text.startswith("Expected 3Y") or p.text == "12.5 Price Band Decision Map":
                p.text = "12-month target price $100, upside 20%, BUY"
        doc.save(legacy)
        failed = subprocess.run(
            [sys.executable, "-X", "utf8", str(AUDIT), "--report", str(legacy), "--charts-manifest", str(manifest)],
            text=True, capture_output=True, encoding="utf-8"
        )
        assert failed.returncode and "Price Band Decision Map incomplete" in failed.stdout, failed.stdout
        assert "Expected 3Y Return bridge" in failed.stdout, failed.stdout

        missing_evidence = root / 'missing_evidence.docx'
        changed = Document(str(report))
        for p in changed.paragraphs:
            if 'Evidence-supported Band:' in p.text:
                p.text = 'Only current price position is stated.'
        changed.save(missing_evidence)
        failed = run_audit(missing_evidence, manifest)
        assert failed.returncode and 'Evidence-supported Band' in failed.stdout, failed.stdout

        wrong_font = root / "wrong_font.docx"
        doc = Document(str(report))
        doc.paragraphs[0].runs[0].font.name = "Calibri" if doc.paragraphs[0].runs else None
        doc.add_paragraph().add_run("Arial text").font.name = "Arial"
        doc.save(wrong_font)
        failed = subprocess.run(
            [sys.executable, "-X", "utf8", str(AUDIT), "--report", str(wrong_font), "--charts-manifest", str(manifest)],
            text=True, capture_output=True, encoding="utf-8"
        )
        assert failed.returncode and "ascii=Arial" in failed.stdout, failed.stdout

        default_font = root / "default_font.docx"
        build_plain = Document()
        build_plain.add_paragraph("默认模板")
        build_plain.save(default_font)
        failed = subprocess.run(
            [sys.executable, "-X", "utf8", str(AUDIT), "--report", str(default_font), "--charts-manifest", str(manifest)],
            text=True, capture_output=True, encoding="utf-8"
        )
        assert "Normal/default fonts must be Times New Roman" in failed.stdout, failed.stdout
        print("REPORT CONTENT AUDIT TEST: PASS")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
