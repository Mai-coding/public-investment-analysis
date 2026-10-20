# 10 - Final Human QA Checklist

This file contains only checks that require judgment or visual inspection. Mechanical completeness, floors, workbook structure and formula consistency are owned by the audit scripts and must not be duplicated here.

Before this human review, complete the applicable [Stage gates](23_workflow_and_state.md#stage-gates). This checklist assesses meaning and rendered appearance rather than repeating script predicates.

## A. Reader-facing analysis

For each decisive subsection, verify:

- Analytical subsections lead with the takeaway; introductory technology/history/background text explains concepts or events in a readable sequence, without forcing an investment judgment into every paragraph.
- Claims are supported by specific numbers, dates and units; source support appears as superscript numeric markers, not full source lines.
- The mechanism is explained, not merely asserted.
- A material boundary, counterargument or failure condition is stated.
- Tables are interpreted rather than repeated line by line.
- Technical terms are explained on first use and consolidated once at the end of the technical introduction; history uses that foundation.
- User-specified “重点研究问题” are answered directly and consistently across §1, the relevant body section and §16.

- Apply `21_report_editorial_style.md`: verify paragraph-to-paragraph logic, customer-to-product flow, revenue dates/disclosure gaps, meaningful numeric comparisons and explanations of unfamiliar costs. Source comparisons stay in Methods; material uncertainty stays visible.
- All displayed financial numbers obey adaptive precision (≥10: integer; <10: at most one decimal). Large monetary/count values use 万/亿 with explicit currency/units, consistently across prose/tables/charts. Check scaling against the full-precision model.
- Definitions, period bridges, FX, accounting reconciliations and derivations sit in Methods Appendix; material risks and assumptions remain clear in the body.

## B. Investment logic and valuation coherence

- Current Price Band, actionability, 3Y return and weighted score do not contradict each other; any rating is secondary.
- The current market snapshot date is explicit and recent enough for the use case.
- The report distinguishes conditional implied terminal requirements from independently completed operating-continuation references; Market-priced Band and Evidence-supported Band, confidence and decisive evidence gaps are explicit.
- Each Price Band is an Operating State × Valuation Regime with a causal chain; bands are not equal-width, and multiple compression is distinguished from fundamental deterioration.
- Price Bands and the Base midpoint trace to the Central methods in `Valuation Method Manifest`; tail bands needing stacked extreme events are Low robustness; low-price bands caused by a broken thesis are not labelled buy zones.
- Explain material disagreements between central comps and separate terminal references under `05_valuation_methodology.md`. Inspect the economic treatment of cash, interest and distributions; machine weight/link checks do not establish that those assumptions are sensible.
- Public-company diluted shares, SBC/options and buybacks are reflected where material.
- Downside floor, thesis-breaking variables and decision tripwires are explicit.

## C. Charts and images — inspect every file

Generate a contact sheet and open every PNG at readable scale.

- No title/subtitle/annotation/data-label overlap, clipping, hidden labels or tofu boxes. Inspect timeline labels especially at clustered dates.
- Body, tables and charts render Chinese in 楷体 and Latin/numbers in Times New Roman (any fallback disclosed). Inspect every generated image at final DOCX size using the increased chart-font baseline in `09_visual_style_guide.md`; no new overlap, clipping or tiny notes.
- Language, units and dates are consistent with the report; visible charts do not carry long source lines, while `charts_manifest.json` retains provenance.
- Every chart tells one internally consistent story; unrelated sources are not forced onto one axis.
- Dual axes are used only for a defensible causal relationship.
- Percentage/capacity charts do not use misleading truncated axes.
- Pie/stacked-bar segments show absolute values; composition charts also show percentages and totals.
- Dense scatter labels use leader lines/bboxes and remain legible.
- Deep backgrounds use light text; light backgrounds use dark text.
- Football field includes only Manifest `Central` methods.
- Inspect the §4 images for genuine product/asset relevance, readable detail, accurate captions and appropriate rights treatment under `17_product_images.md`.
- Inspect the §8 revenue-mix chart for readability, comparable historical/forecast definitions and agreement with the business narrative.
- Inspect §9 profiles for genuine individual evidence and relevance to management judgment; the card is only a summary.
- §7.1 uses prose to interpret the competitive scores and trade-offs; the `CHART_COMPETITION:` figure is the sole score matrix, with no duplicate matrix table.
- Compare the question-based coverage plan with the report: teaching mechanisms, history/value chain, competitive positioning, guidance delivery, scenario drivers, growth/valuation and real products. Check substantive skip reasons; no quota-filling or silent omissions.
- The competition quadrant has meaningful independent axes, directions, four interpretable regions and defensible splits; the target and relevant rivals are identified. Qualitative positions are visibly labelled, with no invented precise scores. It complements the score matrix; placement is not an investment ranking.

## D. DOCX reading and rendering

- Cover, headings, tables, captions, page breaks, headers/footers and contents render correctly under `21_report_editorial_style.md`; inspect uniform navy/white table headers, centered text and consistent TOC page-number colors. The cover price/return/judgment columns remain readable and show the correct model values.
- Verify the cover logo belongs to the target company and is legible and proportional; inspect the one-page hierarchy under `21_report_editorial_style.md`.
- Native headings and all image-host paragraphs have no unwanted squares or list markers. For marker repairs, inspect the relevant Word view where available and caption/pagination behavior; PDF inspection is not proof of Word UI behavior.
- Click every contents entry and compare its final displayed page with the rendered/native document. Contents entries must not pollute the navigation pane as duplicate body chapters.
- No stranded headings, blank/nearly blank pages caused by stale breaks, or separated figure captions. After layout changes, refresh fields and recheck the affected pages and downstream pagination.
- Methods Appendix follows company appendices and precedes final Sources; it contains exact thresholds when display rounding could change an action.
- Charts/images appear after the supporting subsection prose, not before it.
- No empty placeholders such as “chart to be inserted”, “see model”, or stub sections remain.
- Research logs, coverage matrices, Comments schema, PASS/FAIL output and full calculation trails stay backstage—not in the core narrative.
- Body, cover, tables and captions contain no raw URLs or `来源：/Source:` lines; all numeric citations resolve to the final Sources Appendix.
- Past-12-month share-price attribution and future-12-month outlook are concise and decision-focused.
- Long sentences, repeated qualifiers and dense noun strings have been edited.
- The report preserves passed Task 1–4 analysis; expanding one section has not silently compressed unrelated sections.
- For formatting-only revisions, follow the text/table/source/media/workbook baseline comparison and page-review procedure in `22_docx_layout.md`; explain unexpected differences before delivery.

## E. Cross-artifact consistency

Spot-check the most decision-relevant figures across Excel, tables, charts and prose:

- Revenue, margins, EPS, FCF, diluted shares, net debt, Price Band ranges and 3Y return match.
- Scenario labels and assumptions match.
- Comparable set, roles, snapshot date and multiples match. Terminal observation year, hurdle, distributions and diluted-share bases reconcile; three-year exits do not assume the long-term terminal is reached early.
- Sources, locators and dates match the final cited evidence.
- Any model, comp, valuation-method or palette change has been propagated according to `19_model_provenance_and_consistency.md`.

## F. Delivery package

- Deliver only the outputs specified by the task orchestrator.
- Completion card lists artifact paths, gate results, known gaps and the next required input/state.
- State what changed versus the prior version and whether anything was intentionally removed.
