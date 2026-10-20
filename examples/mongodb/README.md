# MongoDB full-report showcase

This case is a real replay of the `public-investment-analysis` full-report workflow using a **2026-07-26 market snapshot**. It is included to prove the output shape and validation discipline, not to provide a current recommendation. It predates the Price Band valuation framework, so its valuation pages show the earlier target-price format.

## What is included

- five selected PNG pages from the final 44-page IC report;
- a reproducible GIF, overview image, and result card generated from those pages;
- [`showcase_manifest.json`](showcase_manifest.json), which records the undistributed source-report hash, PDF page mapping, source-page hashes, output hashes, gate results, and the known non-blocking limitation.

The complete report PDF is intentionally not distributed. The selected pages avoid third-party product-architecture images while still showing the conclusion, competition work, scenario analysis, sensitivity tables, and valuation cross-check.

## Validation record

| Gate | Result |
|---|---|
| Report content | 23 PASS / 0 WARN / 0 FAIL |
| Model and artifact | 14 PASS / 2 WARN / 0 FAIL |
| Depth regression | PASS; 38,419 body characters |
| Visual QA | All 44 rendered pages inspected |
| Independent review | PASS; no blocking findings |
| Repository checks | 10 PASS / 0 FAIL, including showcase integrity |

One non-blocking limitation remains: the repurchase cash-floor formulas need an Excel recalculation before the workbook is used for a live investment delivery.

## Rebuild the public assets

From the repository root:

```bash
python scripts/build_showcase.py
```

The script reads [`source-pages/`](source-pages/) and recreates:

- `assets/showcase/mongodb-workflow.gif`
- `assets/showcase/mongodb-showcase.png`
- `assets/showcase/mongodb-result-card.png`
- `examples/mongodb/showcase_manifest.json`

MongoDB and the MDB ticker are used nominatively for an independent research example. This repository is not affiliated with or endorsed by MongoDB, Inc. The material is a research workflow artifact, not investment advice.
