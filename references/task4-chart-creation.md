# Task 4 — Chart Creation Orchestrator

## Purpose and prerequisites

Generate the target-driven McKinsey-style chart set after substantive research, the operating model and valuation are complete.

Required: Task 1–3 PASS plus any needed historical share-price/multiple data. Do not create placeholder charts.

## Deliver only

Chart PNGs in `charts_v1/` plus an internal contact sheet and `charts_manifest.json` used for QA/handoff. The number is driven by available data, typically 14–20.

## Load

Load the current Task 4 phase in `task_load_map.json`: bootstrap for selection/data; render before the first image. Keep already-read unchanged references in context rather than rereading them.

Do not reload research/valuation methodology unless a chart exposes a documented data gap.

## Rules

1. Charts come after Excel. Any model/valuation figure must be read from Task 2/3 output, not recomputed in chart code.
2. Each chart tells one internally consistent story. Full source/date provenance is recorded in `charts_manifest.json`; the visible PNG does not print long source names or URLs.
3. Every script reads `assets/color_palette.json`; no private replacement palette.
4. Follow renderer boundaries in `09_visual_style_guide.md`; conceptual diagrams are not cartoon product drawings. Real product/asset images are handled under `17_product_images.md` during research/assembly.
5. Apply `13_cjk_charts.md` and the updated font sizes in `09_visual_style_guide.md` before the first chart; inspect it at final DOCX size immediately. Regenerate source text at the new sizes and rerun overlap checks; do not merely resample the bitmap.
6. Skip charts without reliable data rather than filling them with estimates that are not part of the model/research record.
7. Every Matplotlib script collects all title, annotation and data-label Text artists and calls `scripts/chart_text_overlap.py::assert_no_text_overlap` at the **final PNG size** immediately before save. For other renderers record a renderer-appropriate bounds/overlap inspection; do not claim the Matplotlib checker ran on them. A failure must be fixed by lanes, wrapping, offsets, leader lines, larger canvas or splitting—not ignored.
8. Chinese chart labels, axes and table-like annotations use 万/亿 and display precision from `21_report_editorial_style.md`; use `scripts/report_presentation.py` or equivalent formatting after reading full-precision model values. Move detailed definitions to Methods; retain concise metric names, units and decision-relevant limitations.
9. Timeline charts with clustered dates use 3–4 alternating lanes. If labels still collide, split the timeline or add a zoom panel; never stack unreadable labels around one year.

## Workflow

1. Build the question-based coverage plan from `04_chart_inventory.md`, including reference-report gap assessment when supplied, source ranges, owning section and skip reasons. Plan the competition quadrant separately from the score matrix.
2. Generate charts in small reproducible scripts with data inputs separated from rendering.
3. Open every PNG and inspect title, subtitle, axes, labels, units, clipping, contrast and font rendering. Inspect at the dimensions at which the chart will appear in the DOCX.
4. Generate a contact sheet and inspect the full set for inconsistent palette, duplicated stories and old values.
5. Write `charts_manifest.json` conforming to `charts_manifest_schema.json`, with, for every PNG: `filename`, owning `section`, `source_ids`, `source_snapshot`, `model_ranges`, `overlap_check=PASS`, `visual_check=PASS`, and DOCX alt-text marker. Chart 11A uses `CHART_REVENUE_MIX:`.
6. Verify Chart 22 reads only Manifest Central methods and that any model/comp change has propagated.
7. For Chart 17 use `CHART_COMPETITION_QUADRANT:` and the axes/positioning-evidence manifest fields in `04_chart_inventory.md`. If unsupported after trying defensible axes, record chart_id `17`, status `skipped` and a substantive reason in manifest `coverage`.

Use the chart/image portion of `10_final_checklist.md` for human QA; it does not replace visual inspection.

## Handoff

Record chart paths, skipped charts and reasons, model ranges used, snapshot dates, contact-sheet result and open visual issues in `handoff_task4.json`.

Validate the handoff under [Handoff and reuse](23_workflow_and_state.md#handoff-and-reuse), including model inputs and recorded chart-review evidence.
