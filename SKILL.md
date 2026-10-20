---
name: public-investment-analysis
description: Research listed companies and produce an auditable operating model, valuation, charts and IC report, or a concise decision memo. Use for public-equity research, modeling, valuation and revisions to those artifacts.
---

# Public Investment Analysis

Institutional-quality analysis for **listed public companies**. Default language: Chinese; English supported. Investment conclusion is a **Price Band Decision Map**: market-priced and evidence-supported bands, expected 3-year return, risk/reward, actionability and what would change the view — not a single target price or mechanical BUY/HOLD/SELL. Do not use private-round MOIC/IRR or PE-stage dilution logic; do model public-company SBC, options, diluted shares and buybacks.

## Start here

1. Read `references/00_rule_ownership.md`.
2. Confirm target/ticker, sector, available documents and output language.
3. Before starting each new analysis, **open a user-input dialog** and let the user choose **投资简报 / Quick decision memo** (2–3 pages; lightweight Task 1–3) or **深度投资报告 / Full report** (staged Task 1–5). Use `request_user_input_async`, or `request_user_input` when available in the active mode. Wait for the user's submitted choice before research or drafting; do not infer the mode from wording, auto-select it, or treat a preselected option or timeout as confirmation.
4. Use `references/task_load_map.json`: read shared instructions once, then only the current task phase. Reuse unchanged references across phases; conditional groups are opt-in.
5. Never preload all references. Load only files present in the current package and explicitly routed for the active task.

Do not begin Task 1 without target + sector + at least one of: source documents or a ticker that permits filing retrieval.

## Output modes

The dialog choice governs the current analysis; retain it when continuing its tasks or revising its outputs, without asking again. An explicit request for only a particular task still limits execution to that task. Skill maintenance alone does not trigger the report-mode dialog. If no dialog tool is available, disclose that limitation, ask the same two-option question in chat and wait; never silently default.

- **Quick decision memo**: 2–3 pages covering the Price Band Decision Map and 3Y return, priced-in vs variant view, top risks, tripwires and six-month action map. Run lightweight Task 1–3. Skip Task 4/5 unless requested.
- **Full report**: Task 1→2→3→4→5. A 30–40 page final report is typical, not a cap.

## Workflow

| Task | Orchestrator | Required prior state | User-facing output |
|---|---|---|---|
| 1 Research | `references/task1-company-research.md` | target + sector | research document + entity filing folders |
| 2 Model | `references/task2-financial-modeling.md` | full mode: Task 1 PASS; standalone: complete financials | Excel operating model |
| 3 Valuation | `references/task3-valuation.md` | Task 2 model | valuation memo + valuation tabs in same workbook |
| 4 Charts | `references/task4-chart-creation.md` | Tasks 1–3 | target-driven PNG set |
| 5 Assembly | `references/task5-report-assembly.md` | Tasks 1–4 PASS | final IC Report DOCX |

After each task, validate an **internal** versioned handoff under [Workflow and state](references/23_workflow_and_state.md#handoff-and-reuse), show a completion card, and stop unless the user explicitly requested continuous execution. Handoffs and audit logs are working state, not extra user deliverables.

## Global invariants

- Every factual claim and number is traceable; unknown stays unknown. Record actual sources and market/consensus snapshot dates under `01_source_hierarchy.md`.
- Forecasts, scenarios, source Comments and cross-artifact propagation follow `19_model_provenance_and_consistency.md`; charts read model outputs.
- Central valuation remains 100% forward comps, with zero-weight terminal references under `05_valuation_methodology.md`. `Valuation Method Manifest` is the sole method list.
- Reader-facing prose, precision, units, cover and headings follow `21_report_editorial_style.md`; model calculations retain full precision. Chart coverage, rendering, product images and citations follow their owners in `00_rule_ownership.md`.
- Task 5 preserves passed analysis and unaffected sections during revisions.

## Gates

Use [Stage gates](references/23_workflow_and_state.md#stage-gates) for the authoritative commands and order, and [Revision invalidation](references/23_workflow_and_state.md#revision-invalidation) before reusing earlier outputs. Run audits and retain their evidence; a prose assertion is not a PASS. Any applicable FAIL blocks progression or delivery.

Run `scripts/run_repo_checks.py` before publishing or treating the installed package as reproducible.

## Failure handling

Do not fabricate missing filings, consensus, images or prior-task outputs. Follow the fallback order owned by the relevant canonical reference, disclose the gap and record it in the handoff.
