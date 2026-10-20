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
7. `Valuation Inputs`

Do not create `Assumption Guide` or `Source Library`. Valuation tabs are added to the same workbook in Task 3.

## Load

Read only the Task 2 bootstrap references in `task_load_map.json`. `19_model_provenance_and_consistency.md` owns source comments, workbook structure, formatting, the Manifest and cross-artifact propagation.

## Build sequence

### 1. Historical extraction and reconciliation

Extract all material income-statement, cash-flow and balance-sheet lines for 3–5 years, including segment data, one-time items, accounting/non-GAAP differences, fiscal dates and filing locators. Reconcile net income across statements and balance the balance sheet.

For public tech or other equity-compensated companies, include SBC amount and SBC/revenue, diluted-share bridge, option/award dilution and buyback offset.

### 2. Driver-linked revenue model

Choose the simplest driver supported by the financial statements. Do not force every stream into quantity × price.

- **QuantityPrice**: only when filings disclose comparable, economically meaningful quantity and price data sufficient for the relationship. Order: `Revenue → YoY growth → disclosed quantity → disclosed price/yield/ARPU`. Record both disclosure locators in Comments. Do not invent customer counts, volumes or prices to fill a template.
- **GrowthPercent**: when quantity/price disclosure is absent or insufficient, use `Revenue → YoY growth`, with `forecast revenue = prior revenue × (1 + growth assumption)`.
- **RevenueShare**: where disclosed mix supports it, use a revenue-share percentage of a clearly identified parent total. Keep the parent independently modelled to avoid circularity.

Mark the revenue row's Comments Basis with `Model=QuantityPrice`, `Model=GrowthPercent` or `Model=RevenueShare`; the first also includes `Disclosure=...` identifying filing quantity/price disclosure. These are calculation/provenance metadata, not extra reader-facing prose. Costs can use margins or percentages of revenue when appropriate. Projected figures remain formula-linked; a percentage input is a valid driver, not an unmodelled revenue hardcode.

Record the following forecast reasoning in existing Comments or `Calculation Support`; no additional deliverable is required:

- **Research to assumptions.** Map material Task 1 findings to the affected business drivers, revenue/cost assumptions and observable verification signals. Explain material findings left unquantified. Standalone models use the available business evidence and disclose missing research context.
- **Business build before company total.** Forecast each material business from its own historical base and supported drivers, then sum company revenue. Do not set company growth first and back-solve a core business as total less other streams, including through helper formulas. Guidance and consensus are cross-checks; retain and explain differences. Use `RevenueShare` only for a supported mix allocation, identified as an allocation rather than independent business evidence.
- **Why this assumption.** For each material growth, mix or margin assumption, identify comparable historical anchors, forward evidence, the rationale for the Base choice and a plausible range. Distinguish disclosed facts from analyst judgment; a citation alone does not justify the selected number. Explain scope/timing differences when using leading indicators such as ARR to inform recognized revenue. Reuse scenario ranges where applicable rather than adding independent case drivers.
- **Scale-check material new drivers.** When a structural driver such as AI could materially affect revenue but separate revenue disclosure is insufficient, estimate a top-down opportunity with explicit market scope, addressability, achievable share and monetization assumptions as relevant. Cross-check against available product revenue, orders or adoption evidence; disclose uncertainty where that evidence is weak. Select one estimate for the operating build and use the other as a check, not another additive revenue stream. Do not require a separate AI line for every company.

Use the same financial statement grain and reporting units. Historical actuals may be hardcoded. Separate material contracts/PPA-like arrangements and prevent double counting. Detailed bridges and physical checks, when relevant, belong in `Calculation Support`.

### 3. Costs, statements and cash flow

Build COGS and operating expenses from drivers or documented ratios. Projected EBITDA/EBIT/net income must derive from revenue and costs. Complete the three statements, debt/interest, tax, working capital, CapEx, acquisitions, financing, buybacks and diluted shares.

CapEx should distinguish maintenance, growth and acquisition/integration where relevant. Buybacks must respect authorization, minimum cash, liquidity and leverage constraints.

### 4. Scenarios and valuation inputs

Create coherent Bear/Base/Bull outcomes by varying only the **most important 1–5 distinct economic drivers**. Select them by contribution to revenue, profit, cash flow or valuation and material uncertainty; use fewer when sufficient. A driver series across forecast years counts once. Do not disguise many independently adjustable drivers under one grouped label.

In `Scenarios`, use one validated `Case Selector` (1=Bear, 2=Base, 3=Bull). For each selected driver, show Active followed by Bear/Base/Bull assumptions using aligned period columns; one build links to Active. Other assumptions use a single shared base path across cases, not duplicated three-case inputs. Dependent outputs still change through formulas. Separately label long-term valuation states; the 4–5 Price Bands do not require 4–5 complete operating models or additional independent case drivers.

Add a compact `Scenario Drivers` register in `Scenarios`: `Driver ID | Driver | Reason | Active Ref | Bear Ref | Base Ref | Bull Ref | Output Ref`. Register one row per independently varied economic driver (maximum 5), not one per year. References identify real cells/ranges; Output Ref is the immediate consuming build input. Scenario inputs and their rationale remain visible. Verify that each Active input selects the correct case and feeds its output; no cosmetic selector or finished-output multiplier.

Link all Task 3 base metrics (revenue, normalised income/EPS, common equity/TBV, cash/debt, distributions and diluted shares) to the operating model. Retain cash-flow forecasting for quality/funding analysis. Task 3 continues this operating endpoint for a zero-weight terminal reference; central valuation is100% forward comps under `05_valuation_methodology.md`.

### 5. End-to-end linkage test

Change one major driver and verify that revenue, EBITDA, EPS, FCF and all existing valuation outputs update. A cosmetic assumption row with no downstream linkage is a FAIL. Trace material business-revenue dependencies to confirm company totals/growth are not upstream inputs to independently forecast businesses; distinguish any supported mix allocation.

## Workbook edits

Before editing an existing workbook, retain a versioned copy; write to a temporary file and verify it opens before replacing the active file. A failed save must not overwrite the last working version. With openpyxl, never set `cell.fill=None`; use a valid fill object.

## Model QA and gate

Follow `19_model_provenance_and_consistency.md` for row-level Comments, Arial, percentage formats, input/formula/link colors and error checks.

Run this task's checks in [Stage gates](23_workflow_and_state.md#stage-gates).

Fix all FAILs before completion. Record any warning that reflects a real limitation in the handoff.

## Handoff

Record workbook path, historical/forecast periods, key drivers, scenario names, source gaps, audit result and Task 3-required ranges in `handoff_task2.json`.

Validate the versioned handoff under [Handoff and reuse](23_workflow_and_state.md#handoff-and-reuse) before offering it to the next task.
