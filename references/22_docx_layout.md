# DOCX layout diagnosis and revision verification

Load for heading/image-paragraph markers, TOC repairs or layout revisions in Task 5. Reader-facing design is owned by `21_report_editorial_style.md`; this file owns diagnosis and repair mechanics.

## Heading squares: establish the cause

1. Inspect text and runs for literal squares/bullets, missing-glyph boxes and unsupported fonts. Remove only unwanted characters; preserve real punctuation and content.
2. Inspect paragraph `numPr`, style inheritance, numbering definitions and list level. A bullet inherited through a parent style is different from a literal character. Preserve legitimate chapter numbering.
3. Inspect effective paragraph properties on both the paragraph and its full style chain: `keepNext`, `keepLines`, `pageBreakBefore`, `suppressLineNumbers`. Some Word display indicators reflect paragraph settings and are separate from list bullets. Do not assume a shortcut toggles every kind of square.
4. Apply the smallest repair justified by the observed cause. `keepNext` normally protects headings from being stranded: do not disable it across all reports by default. If an explicit marker-free layout requires disabling inherited settings, set an explicit false override rather than removing a node and re-enabling inheritance.
5. Preserve Heading/outline levels, color, numbering and navigation. PDF/rendered PNG QA proves printed appearance, not the absence of Word UI indicators. Verify the relevant Word view when available; otherwise state that UI behavior remains unverified.

## Image-paragraph squares

Apply the same diagnosis to every paragraph containing `w:drawing` or legacy `w:pict`, including logos, charts and product images. A square in the page margin outside the image may be a Word paragraph indicator; do not erase or crop image pixels to hide it.

- Remove an actual unwanted prefix character only after checking its text run. Cancel inherited image-paragraph numbering with `w:numId=0`; changing only the paragraph style may leave a list active.
- Resolve the full paragraph/style chain. For image-host paragraphs, explicitly set `keepNext`, `keepLines`, `pageBreakBefore` and `suppressLineNumbers` false where inherited or direct flags would display a square. An absent property can re-enable inheritance. Do not clear these flags globally from unrelated prose or headings.
- Preserve caption association with an appropriate figure/caption container, placement or explicit breaks outside the image paragraph; then re-render and inspect for orphan captions, new blank pages or pagination changes. Keep image bytes and source citations unchanged during a marker-only repair.
- Verify the relevant Word view when available. OOXML checks inspect known causes; PDF inspection and hiding editing marks cannot prove that the Word indicator is gone.

## Pagination after changing heading properties

- Re-render after each material layout change. Keep a heading with at least its first substantive paragraph/table/figure; move adjacent parent and child headings together.
- Where explicit page starts are necessary, insert a page-break run in a separate preceding paragraph. Do not accumulate hard breaks to chase downstream symptoms before upstream pagination stabilizes.
- Recheck orphan headings, blank/nearly blank pages, chart/caption separation and broken tables. Remove obsolete breaks. Page count is an observation, not a requirement to match the prior version.
- Refresh TOC/PAGEREF and footer fields only after layout settles. Validate each destination and actual page; a nonempty cached number or a successful XML audit alone does not prove accuracy.

## Revision baseline

- Save a new version and retain the prior DOCX. Record the requested scope and a compact before/after change list in the working handoff.
- Run existing `--prev` gates. For a formatting-only revision additionally compare paragraph/table text, citations/source entries, image counts/media hashes and workbook hash. Investigate any unexpected change; do not promise byte-identical DOCX packages after Word saves.
- Inspect every page or document which pages are pixel-identical to an already inspected baseline and open every changed page. Native Word checks supplement, rather than replace, rendered layout review.
