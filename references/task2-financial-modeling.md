# Task 2 — Financial Modeling Orchestrator

## Purpose and prerequisites

Build a fully dynamic public-company Excel model with 3–5 years of history, five-year projections and Bull/Base/Bear scenarios.

Full-report mode requires Task 1 PASS. Standalone model mode may proceed from complete user-provided financial statements, but the missing research context must be disclosed. Stop if reliable historical financials are unavailable.

## Deliver only

`[Target]_Financial_Model_[Date].xlsx`, with this operating order:

1. `Revenue Model`
2. `Calculation Support` — separate, visible and immediately after Revenue Model
3. `Income Statement`
4. `Cash Flow Statement`
5. `Balance Sheet`
6. `Scenarios`
7. `DCF Inputs`

Do not create `Assumption Guide` or `Source Library`. Valuation tabs are added to the same workbook in Task 3.

## Load

Read only the Task 2 bootstrap references in `task_load_map.json`. `19_model_provenance_and_consistency.md` owns source comments, workbook structure, formatting, the Manifest and cross-artifact propagation.

## Build sequence

### 1. Historical extraction and reconciliation

Extract all material income-statement, cash-flow and balance-sheet lines for 3–5 years, including segment data, one-time items, accounting/non-GAAP differences, fiscal dates and filing locators. Reconcile net income across statements and balance the balance sheet.

For public tech or other equity-compensated companies, include SBC amount and SBC/revenue, diluted-share bridge, option/award dilution and buyback offset.

### 2. Driver-linked revenue model

Model each revenue stream in presentation order:

`Revenue → YoY growth → Quantity/volume/capacity/users → Price/yield/ARPU`

Forecast revenue from operating drivers. Historical actuals may be hardcoded; projected revenue rows may not be independently hardcoded. Separate material long-term contracts/PPA-like arrangements and prevent double counting against base revenue.

Anchor each unit-price, volume, utilization or margin assumption to a specific filing/IR disclosure before calibrating to guidance. Place reverse-engineering, bridges, contract de-duplication and physical sanity checks in `Calculation Support`.

### 3. Costs, statements and cash flow

Build COGS and operating expenses from drivers or documented ratios. Projected EBITDA/EBIT/net income must derive from revenue and costs. Complete the three statements, debt/interest, tax, working capital, CapEx, acquisitions, financing, buybacks and diluted shares.

CapEx should distinguish maintenance, growth and acquisition/integration where relevant. Buybacks must respect authorization, minimum cash, liquidity and leverage constraints.

### 4. Scenarios and DCF inputs

Create coherent Bull/Base/Bear operating cases. Each case changes causal drivers, not only valuation multiples. Populate unlevered FCF and all Task 3 inputs through links to the operating model.

### 5. End-to-end linkage test

Change one major driver and verify that revenue, EBITDA, EPS, FCF and all existing valuation outputs update. A cosmetic assumption row with no downstream linkage is a FAIL.

## Model QA and gate

Follow `19_model_provenance_and_consistency.md` for row-level Comments, Arial, percentage formats, input/formula/link colors and error checks.

Run:

```text
python scripts/artifact_audit.py --excel <Target>_Financial_Model_<date>.xlsx
```

Fix all FAILs before completion. Record any warning that reflects a real limitation in the handoff.

## Handoff

Record workbook path, historical/forecast periods, key drivers, scenario names, source gaps, audit result and Task 3-required ranges in `handoff_task2.json`.
