# 17 — Product / Asset Images (§4 hard requirement)

This file is the sole owner of product-image sourcing and insertion. Full-report §4 must contain **2–3 real product/asset images**; data charts do not count.

## Cover company logo (required for final reports and covered quick memos)

Collect the target company’s genuine logo during Task 1: prefer the company’s official brand/media page or IR material, then a user-provided official asset. Record source ID, exact URL/file and page, retrieval date, rights status and local asset path in the source ledger/handoff. Verify the mark belongs to the target company; do not use a broker logo or generate/redraw a brand mark.

Embed it on the first page as an actual DOCX image, preserve aspect ratio and readable resolution, and set the image description to `COMPANY_LOGO: <company name>`. Use a transparent/white-background official variant suited to the page. A text name, placeholder box, empty relationship or hotlink does not count. Source it with a superscript number resolving in Sources; methods and download metadata stay backstage.

The logo does not count toward §4’s 2–3 product/asset images. If no reliable asset can be retrieved, report the specific missing asset and request it; preserve the draft, but do not declare the final cover complete. Layout is owned by `21_report_editorial_style.md`.

## What qualifies

- product/package/board/device photo;
- core physical asset/facility/equipment;
- official product-family or product-architecture image where a product is not meaningfully photographed (common for semiconductors/software infrastructure).

A financial chart, text-heavy slide, generic stock photo or Matplotlib schematic does not qualify.

## Selection order

Choose by economic importance → subsection relevance → authority → recency → clarity. Prefer user material, SEC filing graphics, company IR/official media, then public-domain/appropriately licensed sources. Avoid watermarked or unclear-rights images.

## Task 1 collection

Collect 2–3 candidates covering the main profit pool, the core product and at least one second-curve product/asset. Record exact source ID, document/page or URL, date, rights status and intended §4 subsection in the handoff/source ledger. Do not treat this as an optional conditional reference in full-report mode.

## DOCX insertion

- Insert after the supporting subsection prose, preserving aspect ratio.
- Each image must have complete DOCX alt text whose description begins `PRODUCT_IMAGE:` followed by a useful description.
- Caption: `图 X｜<what the reader should notice>` plus **numeric superscript citation marker(s) only**. Do not print a full source name or URL in the caption.
- Full provenance appears in `Appendix｜Sources / 来源索引` under `20_citation_and_source_appendix.md`.
- Two images may be placed in a 1×2 borderless table when legible at final DOCX size.

## Retrieval and rights

Use permitted browser/fetch/file tools. For SEC filings, retrieve embedded images from the official filing archive with an appropriate user agent. Prefer official/public-domain materials. AI-generated fallback is allowed only when no reliable real/official image exists, must be labeled `示意图，非实拍`, and does **not** satisfy the default two-real-image minimum unless the user explicitly accepts the exception.

## Gate

`report_content_audit.py` counts `PRODUCT_IMAGE:` alt-text markers inside §4. Full-report delivery fails unless the count is 2–3.
