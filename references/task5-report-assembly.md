# Task 5 — Report Assembly Orchestrator

## Purpose and prerequisites

Assemble the passed Task 1–4 outputs into the final 16-section IC Report DOCX. Task 5 is an **editorial and production task**, not a second research/modeling pass.

All Tasks 1–4 and their gates must be complete. Stop and list missing artifacts rather than inserting placeholders.

## Deliver only

`[Target]_IC_Report_v1.docx`

A 30–40 page report is typical, not a hard cap. Decision usefulness and required analysis take priority over page count.

## Load

Load the Task 5 bootstrap, then its `presentation` phase before assembly; use its conditional layout route for marker/TOC revisions and its `reader_qa` phase for final human review.

Read the passed Task 1 research document, Task 2/3 workbook and valuation memo, Task 4 chart set, and handoffs. Load a Task 1/2/3 section slice only if a specific section is missing or ambiguous. Do not reload every methodology file.

## Presentation contract

Apply `21_report_editorial_style.md` to prose, display formatting, cover and headings; apply `17_product_images.md` to the genuine company logo and product images, and `20_citation_and_source_appendix.md` to numeric citations. Keep full-precision calculations in the model.

## Assembly mapping

- §1: synthesize the investment thesis, current Price Band/actionability/3Y return, top risks and user’s重点研究问题.
- §2–9: edit and preserve the passed Task 1 analysis. Do not shorten it merely to meet a page target. Consolidate terminology in the technical introduction (default §2), keep guidance credibility in §9, and do not copy Task 1 coverage matrices into the report. In §7.1, retain substantive prose that explains the competitive scores, trade-offs and falsifiers, but remove any duplicate scoring-matrix table; the `CHART_COMPETITION:` figure is the sole matrix.
- §10: extract linked historical/forecast/QoE evidence from Task 2.
- §11–12: use Task 3 valuation, §11.0 past-12-month price attribution, priced-in analysis and the Price Band Map/3Y bridge. Price Bands replace, not add to, the old target-price and probability-weighted scenario content.
- §13: build Killer Risk presentation from the passed analysis using `07_killer_risk_framework.md` only if not already structured.
- §14: Why Now / Why This / Why Us.
- §15: score consistent with the Price Band conclusion and `08_scoring_framework.md`.
- §16: answer all重点研究问题, list key diligence gaps, tripwires and six-month action map.
- Appendices: keep comparable-company Appendices A–D/A–E, then `Appendix｜Methods / 定义与方法` under `21_report_editorial_style.md`, then add the unlettered `Appendix｜Sources / 来源索引` required by `20_citation_and_source_appendix.md`. Keep raw logs and full calculation trails backstage.

Insert all applicable Task 4 charts after their supporting subsection prose. §4 must contain 2–3 real product/asset images under `17_product_images.md`; full-report delivery is blocked until they are inserted and tagged with `PRODUCT_IMAGE:` alt text. §8 must contain the revenue-mix chart tagged `CHART_REVENUE_MIX:`.

Reconcile the Task 4 coverage plan against embedded images, including the distinct competition quadrant `CHART_COMPETITION_QUADRANT:` (or evidenced skip). Follow `21_report_editorial_style.md` for the two-row cover, colored native headings and numbered linked TOC; do not duplicate design rules here. Update and verify all TOC/PAGEREF/footer fields after final pagination. For heading or image-paragraph markers, TOC repairs and layout revisions, load `22_docx_layout.md` and preserve the prior version as the regression baseline. Apply its image-paragraph rules to every embedded figure; report tables and TOC page-number colors follow `21_report_editorial_style.md`.

Fonts: Chinese `楷体` (`w:eastAsia`; `KaiTi` also accepted), Latin/numbers `Times New Roman` (`w:ascii`/`w:hAnsi`/`w:cs`) in document defaults, Normal and every style/run that defines fonts. Theme-font attributes (`w:asciiTheme` etc.) override explicit names in Word, so strip them. With python-docx, after all content is added:

```python
from docx.oxml.ns import qn
doc.styles['Normal'].element.get_or_add_rPr().get_or_add_rFonts()
for root in (doc.styles.element, doc.element.body):
    for rf in root.iter(qn('w:rFonts')):
        for k in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
            rf.attrib.pop(qn('w:' + k), None)
        for k in ('ascii', 'hAnsi', 'cs'):
            rf.set(qn('w:' + k), 'Times New Roman')
        rf.set(qn('w:eastAsia'), '楷体')
```

Apply the cover typography and alignment contract in `21_report_editorial_style.md`; adjust layout or wording to fit it.

## Reader-first editing

Apply the prose, units and rounding rules in `21_report_editorial_style.md` to all reader-facing text, table cells, captions and chart labels. Never apply display rounding to model formulas.

- Follow `21_report_editorial_style.md` by paragraph function: introductory technology/history/background prose builds understanding in a natural sequence; analytical subsections begin with the investment takeaway. Do not force numbers, counterarguments or valuation/action statements into each introductory paragraph.
- Preserve decisive numbers, mechanisms and counterarguments. Convert working-paper source notes into superscript numeric markers; never paste raw URLs or full source lines into the body.
- Do not paste channel-status matrices, Comments schema, audit console output or working-paper instructions into the main narrative.
- Do not write placeholders such as “chart would be inserted” or “see model”.
- Do not silently compress unaffected chapters during revisions. Use the `--prev` audit when a prior DOCX exists.

## Build and validate

Use the current runtime’s document capability or an installed DOCX library. Build from structured blocks rather than one monolithic string. Validate OOXML/rendering when the runtime supports it and visually inspect the rendered document.

Use native chapter headings with `§N` or `N. Title`. Keep numbered body lists distinct (`（1）` or `①`) so depth parsing cannot mistake list items for chapters.

Run all Task 5 checks in [Stage gates](23_workflow_and_state.md#stage-gates), then complete `10_final_checklist.md`. Any repair requires rechecking affected artifacts.

## Handoff and completion card

Record final path, gate outputs, version changes, unresolved limitations and confirmation that cross-artifact numbers match in `handoff_task5.json`. The user-facing completion card should state what changed and whether anything was intentionally removed.

Validate the final handoff under [Handoff and reuse](23_workflow_and_state.md#handoff-and-reuse), including all required upstream revisions and actual gate evidence.
