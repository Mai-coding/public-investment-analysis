# Task 5 — Report Assembly Orchestrator

## Purpose and prerequisites

Assemble the passed Task 1–4 outputs into the final 16-section IC Report DOCX. Task 5 is an **editorial and production task**, not a second research/modeling pass.

All Tasks 1–4 and their gates must be complete. Stop and list missing artifacts rather than inserting placeholders.

## Deliver only

`[Target]_IC_Report_v1.docx`

A 30–40 page report is typical, not a hard cap. Decision usefulness and required analysis take priority over page count.

## Load

Start with the Task 5 bootstrap references in `task_load_map.json`: this orchestrator, `sections/03d_final_sections_1_13_14_16_appendices.md`, `10_final_checklist.md`, `19_model_provenance_and_consistency.md`, `20_citation_and_source_appendix.md` and `17_product_images.md`.

Read the passed Task 1 research document, Task 2/3 workbook and valuation memo, Task 4 chart set, and handoffs. Load a Task 1/2/3 section slice only if a specific section is missing or ambiguous. Do not reload every methodology file.

## Assembly mapping

- §1: synthesize the investment thesis, target price/rating, top risks and user’s重点研究问题.
- §2–9: edit and preserve the passed Task 1 analysis. Do not shorten it merely to meet a page target. Consolidate all terminology in §3, keep guidance credibility in §9, and do not copy Task 1 coverage matrices into the report. In §7.1, retain substantive prose that explains the competitive scores, trade-offs and falsifiers, but remove any duplicate scoring-matrix table; the `CHART_COMPETITION:` figure is the sole matrix.
- §10: extract linked historical/forecast/QoE evidence from Task 2.
- §11–12: use Task 3 valuation, §11.0 past-12-month price attribution, priced-in analysis, scenarios and Manifest-consistent target price.
- §13: build Killer Risk presentation from the passed analysis using `07_killer_risk_framework.md` only if not already structured.
- §14: Why Now / Why This / Why Us.
- §15: score and recommendation consistent with Task 3 and `08_scoring_framework.md`.
- §16: answer all重点研究问题, list key diligence gaps, tripwires and six-month action map.
- Appendices: keep comparable-company Appendices A–D/A–E, then add the unlettered `Appendix｜Sources / 来源索引` required by `20_citation_and_source_appendix.md`. Keep raw logs and full calculation trails backstage.

Insert all applicable Task 4 charts after their supporting subsection prose. §4 must contain 2–3 real product/asset images under `17_product_images.md`; full-report delivery is blocked until they are inserted and tagged with `PRODUCT_IMAGE:` alt text. §8 must contain the revenue-mix chart tagged `CHART_REVENUE_MIX:`.

On the cover, every judgment-card/summary-table text run must be exactly 12 pt, and every non-empty cell must be horizontally and vertically centered. Do not shrink individual labels to force a fit; adjust cell dimensions or wording instead.

## Reader-first editing

- Begin each subsection with the conclusion and its importance.
- Preserve decisive numbers, mechanisms and counterarguments. Convert working-paper source notes into superscript numeric markers; never paste raw URLs or full source lines into the body.
- Do not paste channel-status matrices, Comments schema, audit console output or working-paper instructions into the main narrative.
- Do not write placeholders such as “chart would be inserted” or “see model”.
- Do not silently compress unaffected chapters during revisions. Use the `--prev` audit when a prior DOCX exists.

## Build and validate

Use the current runtime’s document capability or an installed DOCX library. Build from structured blocks rather than one monolithic string. Validate OOXML/rendering when the runtime supports it and visually inspect the rendered document.

Run in order:

```text
python scripts/artifact_audit.py --excel <model.xlsx> --report <report.docx> [--prev <previous.docx>]
python scripts/report_content_audit.py --report <report.docx> --charts-manifest <charts_v1/charts_manifest.json>
python scripts/depth_audit.py --stage final --in <report.docx> [--prev <previous.docx>]
```

All three must PASS. Then complete `10_final_checklist.md` human QA and fix all material issues.

## Handoff and completion card

Record final path, gate outputs, version changes, unresolved limitations and confirmation that cross-artifact numbers match in `handoff_task5.json`. The user-facing completion card should state what changed and whether anything was intentionally removed.
