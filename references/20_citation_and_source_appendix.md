# 20 — Final Report Citations and Sources Appendix

This file is the sole owner of **reader-facing citation format** in the final DOCX. Research working papers and model comments retain full provenance; the final report uses compact numeric citations.

## 1. Two-layer source architecture

### Backstage / working artifacts

Task 1 research documents, source ledgers, model Comments and chart manifests keep the full evidence trail:

- exact issuer/author and title;
- document type and publication date;
- page / Item / section / timestamp;
- URL or local filename;
- access or market-snapshot date;
- Fact / management claim / inference / assumption classification;
- derivation where applicable.

### Reader-facing final DOCX

- The body, cover, tables, chart captions and image captions use **numeric superscript markers only**, for example `增长 42%[12]` where `[12]` is formatted as superscript.
- Do **not** print raw URLs, full source titles, `来源：...`, `Source: ...`, or filing locators in the body.
- Multiple sources use one superscript marker such as `[4,7]`; reuse the same number whenever the same source is cited again.
- A factual table or paragraph needs citations at the smallest useful unit. One marker may support several adjacent sentences only when the source and scope are unambiguous.
- Fact/Inference/Assumption tags stay backstage unless the distinction itself is decision-relevant. The final prose should read naturally.

## 2. Sources Appendix

After all comparable-company appendices and `Appendix｜Methods / 定义与方法` (owned by `21_report_editorial_style.md`), add the final top-level chapter:

`Appendix｜Sources / 来源索引`

It is unlettered so it does not collide with comparable-company Appendices A–D/A–E. Number entries by **first appearance in the report**.

Each entry follows:

`[n] Issuer/author. Exact title. Document type, publication date. Locator: page/Item/section/timestamp. URL or local filename. Accessed/snapshot date.`

Rules:

1. Deduplicate identical sources. Different filing periods or different reports are separate entries.
2. User-provided files cite the exact filename and page(s); do not invent an external URL.
3. Market/consensus data include channel and snapshot date.
4. Derived figures cite the underlying source entry/entries; derivation stays in the model or working paper unless it is central to the investment argument.
5. Every body citation number must resolve to exactly one Appendix entry. Unused Appendix entries should be removed.
6. The source appendix is an audit trail, not a narrative chapter; it is excluded from report depth/word-count floors.

## 3. Charts and product images

- Standalone PNGs contain no long visible source line. Full provenance is stored in `charts_manifest.json`.
- The DOCX figure caption carries numeric superscript citation markers only.
- Product images use the same citation system. Their DOCX alt text begins with `PRODUCT_IMAGE:` so the report audit can distinguish them from data charts.
- Cover logo images use `COMPANY_LOGO:` alt text and the same numeric citation/source registry; a logo is not a §4 product image.
- The required §8 revenue-mix chart uses alt text beginning with `CHART_REVENUE_MIX:`.

## 4. Mechanical gate

See [Stage gates](23_workflow_and_state.md#stage-gates) for the content audit command and final-delivery order.

The audit fails on body URLs/source lines, missing or unresolved numeric citations, missing Sources Appendix, wrong guidance placement, duplicated glossary placement, missing §4 product images, missing §8 revenue-mix chart, or insufficient §9 management-profile blocks.
