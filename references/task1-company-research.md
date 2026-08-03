# Task 1 — Company Research Orchestrator

## Purpose and prerequisites

Collect the required primary materials and produce the source-backed qualitative analysis for report §2–9.

Required before starting: target company/ticker and sector. Ask the user for available files and the specific questions they most want answered. The user may say “无特别问题，按标准覆盖”.

## Deliver only

1. `[Target]_Research_Document_[Date].md` containing:
   - “重点研究问题清单” at the beginning;
   - §2–9 company analysis;
   - channel coverage matrix;
   - entity coverage matrix;
   - §9 target guidance-evolution and credibility table covering the latest five calls;
   - a backstage past-12-month share-price attribution block for Task 3 §11.0;
   - future-12-month Bear/Base/Bull operating paths;
   - data-collection appendix.

The channel coverage matrix, entity coverage matrix and collection appendix must be wrapped in:

```text
<!-- DEPTH_EXCLUDE_START: RESEARCH_BACKSTAGE -->
...
<!-- DEPTH_EXCLUDE_END: RESEARCH_BACKSTAGE -->
```

They remain mandatory for coverage audits but do **not** count toward §2–9 depth floors.
2. `entity_filings/<ENTITY_TYPE>/<TICKER>/` folders for target, 4–5 competitors, 1–2 upstream leaders and 1–2 downstream leaders, with non-empty raw and parsed material. Target also contains `filing_imgs/` when usable images exist.

Do not create extra summaries or duplicate research documents. The completion card and internal handoff are not additional deliverables.

## Phase 0 — Research questions

Ask one open question using the known target and sector: what does the user most want to understand? Give 3–5 relevant examples such as priced-in growth, second-curve timing, customer concentration, a named competitor, capital allocation/dilution, or regulation/geopolitics.

Record the questions verbatim, map each to a body section, answer them in place, mention them in §1 during Task 5, and answer them one-by-one in §16. If none are specified, record: `重点研究问题：本次用户未提指定的重点研究问题，已按标准尽调全覆盖。`

## Phase 1 — Coverage plan and collection

Load only the Task 1 bootstrap/collection references in `task_load_map.json`.

Run:

```text
python scripts/source_coverage_audit.py --template
```

Use the generated channel and entity tables; do not recreate channel IDs from memory.

### Fixed entity coverage

| entity type | count | annual reports | quarterlies | transcripts |
|---|---:|---:|---:|---:|
| target | 1 | 3 | 2 | 5 |
| competitor | 4–5 | 1 | 2 | 2 |
| upstream | 1–2 | 1 | 1 | 1 |
| downstream | 1–2 | 1 | 1 | 1 |

Select comparable companies globally based on economic similarity, not domicile alone. Identify value-chain leaders using the economically relevant denominator.

### Collection order

1. User-provided files.
2. Applicable regulatory filings and final prospectus/annual/quarterly disclosures.
3. Company website/IR and earnings calls.
4. Current market/consensus data using the fallback order in `01_source_hierarchy.md`.
5. Narrative/qualitative sources: evaluate every registry row, but deep-read only relevance-gated channels that are actually relevant. Record `not_applicable` with a reason rather than performing ritual searches.

Save raw files and parsed summaries into entity folders. Never claim a document was reviewed unless it was retrieved and read.

### Required time-based diagnostics

- **Five-call guidance evolution**: management guidance, actual result, change, explanation and credibility read-through. Write it in **§9**, beside management execution and credibility—not in §3.
- **Past 12 months**: total return and evidence-backed attribution across earnings expectations, valuation multiple, policy/regulation, company events and technical/flow effects. Keep it as a Task 1 backstage diagnostic handed to Task 3 for §11.0; do not place it in §9.
- **Next 12 months**: Bear/Base/Bull operating paths with assumptions, catalysts, risks and measurable KPIs. Valuation numbers are finalized in Task 3.

## Phase 2 — Write §2–9

Load `sections/03a_research_sections_2_9.md`, `14_depth_playbook.md` and `02_hv_analysis_framework.md`. Then load only the needed recipe/module:

- §3: recipes 18a/18b when the company has meaningful technical complexity.
- §2.8: recipe 18c.
- §5: recipe 18d.
- §6 chart specification: recipe 18e.
- §9 profile cards: recipe 18f.
- Supply/share, threat timing or disruption-sensitive companies: `15_industry_modules.md` after triage.
- Real product/asset images: **always load** `17_product_images.md` in full-report mode. Collect 2–3 auditable candidates and record them in the Task 1 handoff; this is not optional merely because §4 prose is complete.
- Maintain an internal `source_ledger.json` conforming to `source_ledger_schema.json` with stable source IDs and full provenance for Task 5 numeric citations.

Write §2 and §7 as HV narrative prose. Use evidence tables before prose, quantify qualitative claims, explain mechanisms and boundaries, and answer only 2–3 genuinely sharp questions per chapter at depth. Do not paste question headings or CEMRI labels into the report.

## Phase 3 — Gate

Run both commands and preserve their output:

```text
python scripts/source_coverage_audit.py --in <Target>_Research_Document_<date>.md
python scripts/depth_audit.py --stage research --in <Target>_Research_Document_<date>.md [--dir <entity_filings_root>]
```

Both must PASS before full-mode Task 2–5. Respond to the audit’s named human-review sample by checking the cited chapters, not by marking them complete without inspection.

## Handoff

Record output paths, market snapshot date, comp/value-chain set, user questions, gate results, unresolved source gaps and inputs needed by Task 2 in an internal `handoff_task1.json` conforming to `handoff_schema.json`.
