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
from docx.shared import Inches, Pt

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


def build(path: Path, image: Path) -> None:
    doc = Document()
    cover = doc.add_table(rows=1, cols=2)
    for cell, text in zip(cover.rows[0].cells, ("Rating: BUY", "Target price: $100")):
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(text)
        run.font.size = Pt(12)
    doc.add_heading("1. 投资概要", level=1)
    doc.add_paragraph("核心判断、目标价和主要风险在此汇总。")
    doc.add_heading("2. 行业纵向叙事", level=1)
    p = doc.add_paragraph("行业变化有量化证据。")
    add_citation(p, 1)
    doc.add_heading("3. 核心技术入门", level=1)
    doc.add_heading("3.1 技术机制", level=2)
    doc.add_paragraph("技术解释。")
    doc.add_heading("3.2 术语表", level=2)
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
    doc.add_heading("9.7 Guidance 演变与可信度", level=2)
    doc.add_paragraph("最近五次指引与实际逐期比较，区分短期兑现和长期目标。")
    doc.add_heading("Appendix｜Sources / 来源索引", level=1)
    doc.add_paragraph(
        "[1] Test Company. FY2026 Annual Report. Form 10-K, 2026-03-01. "
        "Locator: Item 7, page 42. https://example.com/report. Accessed 2026-07-26."
    )
    doc.save(path)


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
        }]}), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(AUDIT), "--report", str(report), "--charts-manifest", str(manifest)],
            text=True, capture_output=True
        )
        if result.returncode:
            print(result.stdout)
            print(result.stderr)
            return result.returncode
        assert "SUMMARY:" in result.stdout and "0 FAIL" in result.stdout
        print("REPORT CONTENT AUDIT TEST: PASS")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
