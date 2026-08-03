# 00 - Rule Ownership and Conflict Precedence

This file resolves conflicts and prevents duplicate rule maintenance. When two files differ, follow the higher-precedence owner below and update the non-owner to a pointer rather than copying the rule.

## Precedence

1. Runtime/system safety and tool rules.
2. Machine-readable audit scripts for mechanically testable requirements.
3. Canonical owner in the table below.
4. Current task orchestrator.
5. Task-specific recipes and lessons learned.

## Canonical owners

| Domain | Canonical owner | Notes |
|---|---|---|
| Scope, trigger, task DAG | root `SKILL.md` | Router only; no deep methodology |
| Source hierarchy, labels, market-data fallback | `01_source_hierarchy.md` | Yahoo Finance/yfinance is default market-data channel; IR/filing self-calculation then professional data/consensus are fallbacks |
| Channel IDs and required status | `source_registry.json` | Only place to add/remove channels or change mode |
| HV industry/competition prose | `02_hv_analysis_framework.md` | Applies to §2 and §7 |
| Section deliverables | `sections/03a–03d` | These task slices are the complete public specification |
| Chart selection/data requirements | `04_chart_inventory.md` | Styling is not owned here |
| Public-equity valuation policy | `05_valuation_methodology.md` | Forward P/E and P/S + DCF; no EV-based trading multiples |
| Comparable selection/retrieval | `06_comp_analysis_workflow.md` | Global set, market snapshot and filings workflow |
| Killer risks | `07_killer_risk_framework.md` | Risk taxonomy and required fields |
| Score and BUY/HOLD/SELL mapping | `08_scoring_framework.md` | Rating follows target-price upside; score supports it |
| Chart visual system | `09_visual_style_guide.md` | Palette, composition, labels, contrast and visual QA |
| Human final QA | `10_final_checklist.md` | No duplicate machine checks |
| Lesson pointers | `11_lessons_learned.md` | Index only, not a second rule source |
| Runtime/long-task adaptation | `12_long_running_tasks.md` | Tool names are runtime-specific |
| CJK/Times font implementation | `13_cjk_charts.md` | Sole font implementation owner |
| Prose depth method | `14_depth_playbook.md` | No company-specific few-shot is bundled; use the active section checklist |
| Industry-dependent deep modules | `15_industry_modules.md` | Apply after triage, not universally |
| Priority narrative-source playbook | `16_priority_sources.md` | Relevance-gated; registry owns channel modes |
| Product/asset image rules | `17_product_images.md` | Sole image sourcing/insertion owner |
| Technology/value-chain recipes | `recipes/18a–18f` | Load one recipe at a time |
| Model provenance and cross-artifact consistency | `19_model_provenance_and_consistency.md` | Task 2–5 common hard rules |
| Final DOCX numeric citations and Sources Appendix | `20_citation_and_source_appendix.md` | Sole reader-facing citation owner; working artifacts keep full provenance |
| Reader-facing report content gate | `scripts/report_content_audit.py` | Citation, glossary/guidance placement, product images, §8 revenue mix and §9 profiles |
| Matplotlib text-collision gate | `scripts/chart_text_overlap.py` | Every chart script must call it at final render size |
| Mechanical research/final depth floors | `scripts/depth_audit.py` | Word floors are hard anti-skeleton lower bounds, not writing targets |
| Research coverage counts | `scripts/source_coverage_audit.py` | Target coverage is 3 annual reports / 2 quarterlies / 5 transcripts |
| Model/workbook checks | `scripts/artifact_audit.py` | Mechanically testable workbook/report consistency |

## Resolved conflicts

- **Market data**: yfinance/Yahoo Finance is the default market-data channel. When unavailable, calculate from IR/latest filing, then use connected professional data, then user-provided consensus with explicit status/date.
- **Transcript coverage**: target 3 annual reports + 2 quarterlies + 5 transcripts; competitors 1/2/2; upstream/downstream 1/1/1.
- **Depth floors**: script floors are hard lower bounds to catch skeleton drafts. Reference page/word ranges are planning guidance, not alternative gates.
- **Competitor narrative length**: use the section slice and audit floor; do not maintain a second number in the final checklist.
- **Fonts**: `13_cjk_charts.md` controls implementation. Other files may state visual intent but must not provide competing code paths.
- **Dilution**: private-round dilution/MOIC logic is out of scope; public-company SBC, options, diluted share count and buybacks are mandatory where material.
- **Page count**: 30–40 pages is a planning range only. Completeness and decision usefulness take priority.
- **Final citations**: the final DOCX body uses superscript numeric markers only; exact source metadata lives in the unlettered Sources Appendix. Research/model artifacts retain full source strings.
- **Glossary/guidance placement**: one consolidated glossary at the end of §3; no duplicate §2 terminology table. Five-call guidance history and credibility analysis belong in §9.
- **Depth-count exclusions**: Task 1 coverage matrices and backstage collection logs are excluded from chapter floors through explicit `DEPTH_EXCLUDE` markers.
