# 10 - Final Human QA Checklist

This file contains only checks that require judgment or visual inspection. Mechanical completeness, floors, workbook structure and formula consistency are owned by the audit scripts and must not be duplicated here.

## 0. Required machine gates

Run in order and retain the console output:

```text
python scripts/artifact_audit.py --excel <model.xlsx> [--report <report.docx>] [--prev <previous.docx>]
python scripts/report_content_audit.py --report <report.docx> --charts-manifest <charts_v1/charts_manifest.json>
python scripts/depth_audit.py --stage final --in <report.docx> [--prev <previous.docx>]
```

All three must exit with code 0. A manual checkmark does not override a FAIL.

## A. Reader-facing analysis

For each decisive subsection, verify:

- The first 1–2 sentences state the takeaway and why it matters.
- Claims are supported by specific numbers, dates and units; source support appears as superscript numeric markers, not full source lines.
- The mechanism is explained, not merely asserted.
- A material boundary, counterargument or failure condition is stated.
- Tables are interpreted rather than repeated line by line.
- Technical terms are explained on first use and consolidated once at the end of §3; §2 contains no duplicate terminology table.
- User-specified “重点研究问题” are answered directly and consistently across §1, the relevant body section and §16.

## B. Investment logic and valuation coherence

- Recommendation, weighted score and target-price upside do not contradict each other.
- The current market snapshot date is explicit and recent enough for the use case.
- The report distinguishes what is already priced in from the variant view.
- Bull/Base/Bear cases are causal business paths, not only different multiples.
- The target price is traceable to the same central methods and weights recorded in `Valuation Method Manifest`.
- Diagnostic comps, historical precedents and sentiment anchors are clearly labelled and carry zero central weight.
- Public-company diluted shares, SBC/options and buybacks are reflected where material.
- Downside floor, thesis-breaking variables and decision tripwires are explicit.

## C. Charts and images — inspect every file

Generate a contact sheet and open every PNG at readable scale.

- No title/subtitle/annotation/data-label overlap, clipping, hidden labels or tofu boxes. Inspect timeline labels especially at clustered dates.
- Language, units and dates are consistent with the report; visible charts do not carry long source lines, while `charts_manifest.json` retains provenance.
- Every chart tells one internally consistent story; unrelated sources are not forced onto one axis.
- Dual axes are used only for a defensible causal relationship.
- Percentage/capacity charts do not use misleading truncated axes.
- Pie/stacked-bar segments show absolute values; composition charts also show percentages and totals.
- Dense scatter labels use leader lines/bboxes and remain legible.
- Deep backgrounds use light text; light backgrounds use dark text.
- Football field includes only Manifest `Central` methods.
- §4 includes 2–3 real/official product or asset images, each tagged `PRODUCT_IMAGE:` with numeric citation markers and appropriate rights treatment.
- §8 contains a readable historical/forecast revenue-mix chart tagged `CHART_REVENUE_MIX:`.
- §9 contains 5–7 genuine individual profiles; the management card is only a summary.
- §7.1 uses prose to interpret the competitive scores and trade-offs; the `CHART_COMPETITION:` figure is the sole score matrix, with no duplicate matrix table.

## D. DOCX reading and rendering

- Cover, headings, tables, captions, page breaks, headers/footers and table of contents render correctly; every cover judgment-card/summary-table run is 12 pt and every cell is horizontally and vertically centered.
- Charts/images appear after the supporting subsection prose, not before it.
- No empty placeholders such as “chart to be inserted”, “see model”, or stub sections remain.
- Research logs, coverage matrices, Comments schema, PASS/FAIL output and full calculation trails stay backstage—not in the core narrative.
- Body, cover, tables and captions contain no raw URLs or `来源：/Source:` lines; all numeric citations resolve to the final Sources Appendix.
- Past-12-month share-price attribution and future-12-month outlook are concise and decision-focused.
- Long sentences, repeated qualifiers and dense noun strings have been edited.
- The report preserves passed Task 1–4 analysis; expanding one section has not silently compressed unrelated sections.

## E. Cross-artifact consistency

Spot-check the most decision-relevant figures across Excel, tables, charts and prose:

- Revenue, margins, EPS, FCF, diluted shares, net debt and target price match.
- Scenario labels and assumptions match.
- Comparable set, roles, snapshot date and multiples match.
- Sources, locators and dates match the final cited evidence.
- Any model, comp, valuation-method or palette change has been propagated according to `19_model_provenance_and_consistency.md`.

## F. Delivery package

- Deliver only the outputs specified by the task orchestrator.
- Completion card lists artifact paths, gate results, known gaps and the next required input/state.
- State what changed versus the prior version and whether anything was intentionally removed.
