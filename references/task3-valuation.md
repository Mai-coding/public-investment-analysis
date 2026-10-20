# Task 3 — Valuation Orchestrator

## Purpose and prerequisites

Anchor 100% of central valuation to comparable-company forward multiples; retain operating-continuation terminal cases as zero-weight references; reverse the current price into conditional terminal requirements, and distinguish **Market-priced Band** from **Evidence-supported Band**. Preserve 4–5 Price Bands, 3Y return and conditional actionability. Policy and formulas are owned by `05_valuation_methodology.md`.

Task 2 workbook must contain linked statements, scenarios, per-share metrics, common equity, capital and diluted-share bridges. Do not fabricate prerequisites. Load only Task 3 bootstrap in `task_load_map.json`; refresh comps under `06_comp_analysis_workflow.md` when needed.

## Deliver only

1. `[Target]_Valuation_Analysis_[Date].md`.
2. `Terminal Cases`, `Implied Expectations`, `Sensitivity`, `Comps` and `Valuation Summary` tabs in the existing Task 2 workbook. No second workbook.

## Step 0 — Option-bucket litmus test

Conservatively value the visible business using 100% forward comps, with terminal results shown separately at zero weight, then compare quoted equity value with it. Gap roughly ≤20–25%: normal single-layer framework. A large gap warrants checking separately sourceable long-duration projects. Under the100% comparable policy, option buckets remain zero-weight references and do not widen central bands; comparable-anchored operating SOTP may still sit within the forward family. An unexplained gap is not permission to invent projects. Keep probability and waiting time separate; prevent duplicated projects and retain §12.8 source/assumption tables.

## Core work

1. **Link inputs.** Read Task 2 `Valuation Inputs`: revenue, normalised net income/EPS, common equity/TBV, cash, debt, dividends, buybacks and diluted shares. Preserve the operating model. Extend the operating endpoint into a zero-weight terminal reference under the rules in `05_valuation_methodology.md`.
2. **Forward comps (100%) and terminal references (0%).** Select the suitable forward metric, retrieve at least 3 economic peers and justify the multiple premium/discount; multiply Task 2 same-year per-share metrics. Follow policy P/B→P/S→P/E applicability. Form terminal references by continuing the operating endpoint; use market/share only as a scale check. Explain any alternative method. Source assumptions and test capital/dilution. Record canonical `Terminal Cases` fields and freeze research cases before reverse pricing.
3. **Forward and reverse mapping.** Use common observation year, hurdle scenarios, mature exit anchors, distributions and future shares. Use `scripts/terminal_multiple.py` or identical Excel formulas. `Implied Expectations` compares current-price requirements with independent cases in revenue, share, margin, net income or book/ROE terms. Do not treat current multiple as a unique market forecast, or reuse an elevated current multiple as a mature anchor without evidence.
4. **Evidence and positioning.** Populate `Condition Evidence` from Task 1 with observable/time-bound threshold, dated source locator, status, decisive flag and next signal. Adjudicate Evidence-supported Band and Confidence independently of price. `Decision Position` records both positions and rationale; Robustness/counting favourable conditions cannot substitute for judgment.
5. **Price Bands.** Build 4–5 bands at economic breaks; overlapping case intervals stay in `Terminal Cases`. Each band has causal chain, metric/multiple decomposition, Required Conditions, Key KPIs, Evidence Status, Evidence Ref, Distance, Robustness and conditional Actionability. Challenge/revise once. Disclose prices outside/between bands instead of stretching them.
6. **Manifest and returns.** Maintain `Valuation Method Manifest`: Central weights must sum to Forward Comps=1.00; Terminal must be Diagnostic with zero weight; reverse diagnostics and equivalent P/S/P/E expressions have zero weight. `Valuation Summary` includes `Price Band Map`, `Condition Evidence`, `Decision Position`, `Band Valuation Bridge` (same-case Central endpoints equal forward comps; terminal columns are references), `3Y Return Bridge`. Append `Evidence Status | Evidence Ref` to existing band columns. Compute Base and Disappointment 3Y total return from third-year operating cases, exit prices and distributions; the additive component bridge is approximate.

## Gate

Run this task's checks in [Stage gates](23_workflow_and_state.md#stage-gates).

Fix all FAILs. Flex a terminal growth/margin/cash input and dilution: verify reference value and inverse requirements update while central bands and entry prices remain unchanged. Flex comparable premium and near-term earnings separately to verify central sensitivity, bands and returns update. Separately flex a Task 2 driver through the 3Y bridge. Confirm any market/evidence disagreement is explicit; structural checks cannot prove industry judgments.

## Handoff

Record 100% forward/0% terminal weights, same-case central intervals and separate terminal references, snapshot, selected metric/rationale, base year, horizon/hurdle/exit/distribution/share assumptions, implied requirements, Price Band Map, both positions and confidence, decisive evidence gaps, Attractive entry, Base/Disappointment 3Y returns, method roles, option-bucket conclusion, update signals and actual audit result in `handoff_task3.json` under the common schema. A PASS Task 3 handoff must include its `valuation_assessment` object. Rating is secondary.

Validate the versioned handoff under [Handoff and reuse](23_workflow_and_state.md#handoff-and-reuse) before offering it to the next task.
