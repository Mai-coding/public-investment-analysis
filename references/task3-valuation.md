# Task 3 — Valuation Orchestrator

## Purpose and prerequisites

Value the listed company using DCF plus forward P/E and forward P/S and produce a defensible 12-month price target, upside/downside and BUY/HOLD/SELL rating.

Task 2 workbook must exist and contain linked projections, FCF, net debt, diluted shares and scenarios. Do not build a placeholder valuation.

## Deliver only

1. `[Target]_Valuation_Analysis_[Date].md`.
2. DCF, sensitivity, comps and valuation-summary tabs added to the existing Task 2 workbook. Do not create a second workbook.

## Load

Read the Task 3 bootstrap references in `task_load_map.json`. `05_valuation_methodology.md` owns valuation policy; `19_model_provenance_and_consistency.md` owns the Manifest and consistency. Load `06_comp_analysis_workflow.md` only when the comp set or market snapshot must be refreshed. No generic valuation textbook is required or bundled.

## Step 0 — Option-bucket litmus test

First value the visible operating business conservatively. Calculate the gap between quoted value and this operating value.

- Gap roughly ≤20–25%: use the normal single-layer DCF + forward-multiple framework.
- Large gap tied to identifiable, binary, long-duration projects with separately anchorable TAM and mature exit multiples: use an operating SOTP plus explicit option buckets.
- Large gap without separable, sourceable projects: do not invent option precision; revisit operating assumptions or express uncertainty through scenarios/sensitivities.

Record the conclusion and inputs. Success probability and time discounting are separate; do not hide delay inside probability. Precedent/sentiment anchors remain diagnostic.

## Core work

### 1. Pull model outputs

Green-link projected revenue, EPS/net income, UFCF, tax, D&A, CapEx, NWC, net debt and diluted shares from Task 2. Do not hardcode a second forecast in the valuation tabs.

### 2. DCF

Build WACC, terminal value, present value, EV-to-equity bridge and per-share value. Run WACC/growth sensitivities and sanity-check terminal-value share of EV.

### 3. Forward trading comps

Use global public comps selected for economic similarity. Use forward P/E and forward P/S only; do not use EV/EBITDA or EV/Sales as trading-multiple anchors. Clearly separate Central and Diagnostic roles. Multi-segment companies may use segment-specific SOTP anchors.

Record the exact next fiscal year, market snapshot date, source and selected multiple rationale. Do not start from a desired target price and back-solve a multiple.

### 4. Reverse DCF and scenarios

Show what current price implies for growth/margin/FCF and compare it with the analyst view. Build Bear/Base/Bull business-event chains with linked model outputs, valuation assumptions, catalysts and risks.

### 5. Reconciliation and rating

Create `Valuation Method Manifest` in `Valuation Summary`. Only Central methods may have positive weight or enter the football field and target price. Reconcile to a 12-month target price and apply the rating thresholds in `08_scoring_framework.md`.

Public-company SBC/options and diluted shares must flow into per-share value. Only private-round dilution/MOIC logic is excluded.

## Gate

After adding valuation tabs, run:

```text
python scripts/artifact_audit.py --excel <model_with_valuation.xlsx>
```

Fix all FAILs. Confirm that changing a model driver propagates through DCF/comps/scenarios/target price.

## Handoff

Record target price, rating, current price/snapshot date, central methods/weights, diagnostic methods, scenario prices/probabilities, option-bucket conclusion, key sensitivities and audit result in `handoff_task3.json`.
