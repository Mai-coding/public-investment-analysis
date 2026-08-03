---
name: public-investment-analysis
description: Build source-backed listed-company public-equity IC analysis through five staged tasks—research, financial modeling, valuation, charts, and final DOCX—or a 2–3 page quick decision memo. Uses DCF plus forward P/E and P/S, public-company dilution modeling, machine audit gates, and just-in-time reference loading.
---

# Public Investment Analysis

Institutional-quality analysis for **listed public companies**. Default language: Chinese; English supported. Return framing is a **12-month price target plus upside/downside**. Do not use private-round MOIC/IRR or PE-stage dilution logic; do model public-company SBC, options, diluted shares and buybacks.

## Start here

1. Read `references/00_rule_ownership.md`.
2. Confirm target/ticker, sector, available documents, output language and mode.
3. Select **quick memo** or **full report**.
4. Read only the current task orchestrator and the phase references listed in `references/task_load_map.json`.
5. Never preload all references. Load only files present in the current package and explicitly routed for the active task.

Do not begin Task 1 without target + sector + at least one of: source documents or a ticker that permits filing retrieval.

## Output modes

- **Quick decision memo**: 2–3 pages covering recommendation/target price, priced-in vs variant view, top risks, tripwires and six-month action map. Run lightweight Task 1–3. Skip Task 4/5 unless requested.
- **Full report**: Task 1→2→3→4→5. A 30–40 page final report is typical, not a cap.

## Workflow

| Task | Orchestrator | Required prior state | User-facing output |
|---|---|---|---|
| 1 Research | `references/task1-company-research.md` | target + sector | research document + entity filing folders |
| 2 Model | `references/task2-financial-modeling.md` | full mode: Task 1 PASS; standalone: complete financials | Excel operating model |
| 3 Valuation | `references/task3-valuation.md` | Task 2 model | valuation memo + valuation tabs in same workbook |
| 4 Charts | `references/task4-chart-creation.md` | Tasks 1–3 | target-driven PNG set |
| 5 Assembly | `references/task5-report-assembly.md` | Tasks 1–4 PASS | final IC Report DOCX |

After each task, create an **internal** handoff conforming to `references/handoff_schema.json`, show a completion card, and stop unless the user explicitly requested continuous execution. Handoff metadata is working state, not an extra user deliverable.

## Global invariants

- Every factual claim and number is traceable; unknown stays unknown. Final DOCX citations use numeric superscripts and a terminal Sources Appendix under `20_citation_and_source_appendix.md`.
- Record actual source and snapshot date for market/consensus data.
- Revenue forecasts are driver-linked; projected EBITDA is derived, not independently hardcoded.
- Task 3 reads Task 2 outputs; charts read model outputs rather than recomputing them.
- `Valuation Method Manifest` is the sole list of central vs diagnostic valuation methods.
- Task 5 assembles passed outputs and must not silently compress unrelated sections.
- Product/asset images follow `17_product_images.md`; §4 requires 2–3 auditable product images. Matplotlib is for data charts, and every chart passes the text-overlap gate.
- Audit scripts must actually run. A prose claim that checks passed is not evidence.

## Gates

- Repository/package validation: run `python` with `scripts/run_repo_checks.py` before publishing or treating the installed package as reproducible.
- Task 1: run `scripts/source_coverage_audit.py`, then `depth_audit.py --stage research`.
- Final delivery: run `scripts/artifact_audit.py`, `scripts/report_content_audit.py`, then `depth_audit.py --stage final`; complete human visual/reader QA in `10_final_checklist.md`.
- Any FAIL blocks progression or delivery.

## Failure handling

Do not fabricate missing filings, consensus, images or prior-task outputs. Follow the fallback order owned by the relevant canonical reference, disclose the gap and record it in the handoff.
