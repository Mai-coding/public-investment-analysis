# 00 - Rule Ownership and Conflict Precedence

This file resolves conflicts and prevents duplicate rule maintenance. When two files differ, follow the higher-precedence owner below and update the non-owner to a pointer rather than copying the rule.

## Precedence

1. Runtime/system safety and tool rules.
2. Explicit user requirements within those rules.
3. Canonical owner in the table below, implemented by audit scripts for mechanically testable requirements.
4. Current task orchestrator.
5. Task-specific recipes and lessons learned.

An audit implements the contract; its regex or an old fixture is not an independent design requirement. Fix demonstrated false positives and rerun regression checks; do not silently bypass a real FAIL. Record intentional user overrides and their effect on validation.

## Canonical owners

| Domain | Canonical owner | Notes |
|---|---|---|
| Scope, trigger, task DAG | root `SKILL.md` | Router only; no deep methodology |
| Stage gates, handoff eligibility and revision invalidation | `23_workflow_and_state.md` | Sole gate-command/order owner; `handoff_schema.json` and `scripts/handoff_audit.py` enforce recorded state |
| Reference loading and context budgets | `task_load_map.json` | Entrypoint/shared overhead, phase additions and deduplicated route totals; `scripts/context_budget_audit.py` |
| Source hierarchy, labels, market-data fallback | `01_source_hierarchy.md` | Yahoo Finance/yfinance is default market-data channel; IR/filing self-calculation then professional data/consensus are fallbacks |
| Channel IDs and required status | `source_registry.json` | Only place to add/remove channels or change mode |
| HV industry/competition prose | `02_hv_analysis_framework.md` | Applies to industry history (default §3) and competition (§7) |
| Section deliverables | `sections/03a–03d` | These task slices are the complete public specification |
| Chart selection/data requirements | `04_chart_inventory.md` | Styling is not owned here |
| Public-equity valuation policy | `05_valuation_methodology.md` | 100% forward comps; terminal reference at zero weight → Price Bands, evidence adjudication, 3Y return bridge |
| Comparable selection/retrieval | `06_comp_analysis_workflow.md` | Global set, market snapshot and filings workflow |
| Killer risks | `07_killer_risk_framework.md` | Risk taxonomy and required fields |
| Five-dimension score | `08_scoring_framework.md` | Supports, never decides, the Price Band conclusion; any rating is secondary |
| Chinese prose, display precision/units, cover layout and Methods Appendix | `21_report_editorial_style.md` | Reader-facing layer; models keep full precision |
| Heading/TOC design | `21_report_editorial_style.md` | Native outline, palette colors, numbered linked contents |
| DOCX marker diagnosis and layout-revision procedure | `22_docx_layout.md` | Conditional Task 5 implementation, not a second design source |
| Chart visual system | `09_visual_style_guide.md` | Palette, composition, labels, contrast and visual QA |
| Human final QA | `10_final_checklist.md` | No duplicate machine checks |
| Lesson pointers | `11_lessons_learned.md` | Index only, not a second rule source |
| Runtime/long-task adaptation | `12_long_running_tasks.md` | Tool names are runtime-specific |
| Chart font implementation (KaiTi + Times New Roman) | `13_cjk_charts.md` | Chart font owner; DOCX body font spec lives in `task5-report-assembly.md` and is gated by `report_content_audit.py` |
| Prose depth method | `14_depth_playbook.md` | No company-specific few-shot is bundled; use the active section checklist |
| Industry-dependent deep modules | `15_industry_modules.md` | Apply after triage, not universally |
| Priority narrative-source playbook | `16_priority_sources.md` | Relevance-gated; registry owns channel modes |
| Product/asset and company logo sourcing | `17_product_images.md` | Sole image sourcing/insertion owner; logo does not count toward §4 images |
| Technology/value-chain recipes | `recipes/18a–18f` | Load one recipe at a time |
| Model provenance, Excel layout and cross-artifact consistency | `19_model_provenance_and_consistency.md` | Task 2–5 common hard rules; `assets/excel_model_style.json` owns visual parameters |
| Final DOCX numeric citations and Sources Appendix | `20_citation_and_source_appendix.md` | Sole reader-facing citation owner; working artifacts keep full provenance |
| Reader-facing numeric formatting implementation | `scripts/report_presentation.py` | 万/亿, adaptive precision, display-only formatting and lint |
| Reader-facing report content gate | `scripts/report_content_audit.py` | Content plus cover columns, global tables, TOC page colors and image-paragraph marker checks implemented by `scripts/report_layout_rules.py` |
| Matplotlib text-collision gate | `scripts/chart_text_overlap.py` | Every chart script must call it at final render size |
| Mechanical research/final depth floors | `scripts/depth_audit.py` | Word floors are hard anti-skeleton lower bounds, not writing targets |
| Research coverage counts | `scripts/source_coverage_audit.py` | Target coverage is 3 annual reports / 2 quarterlies / 5 transcripts |
| Model/workbook checks | `scripts/artifact_audit.py` | Mechanically testable workbook/report consistency |

## Applying owners

Use each owner's current rule rather than an old example or copied summary. Section slices own substantive deliverables; depth-audit floors catch skeleton drafts and are not writing targets. The human checklist evaluates reader/visual meaning, while the workflow contract owns commands and gate order. Resolve a demonstrated audit false positive against the owner, retain the regression case and rerun checks.
