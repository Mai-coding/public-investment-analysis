<sub>🌐 <a href="README.md">中文</a> · <b>English</b></sub>

<div align="center">

# Public Investment Analysis

> *“Do not let a report-shaped answer reach an investment committee before its model, sources, and gates do.”*

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-public--investment--analysis-6f42c1)](SKILL.md)
[![skills.sh](https://skills.sh/b/Mai-coding/public-investment-analysis)](https://skills.sh/Mai-coding/public-investment-analysis)
[![Repository checks](https://img.shields.io/badge/repository%20checks-10%2F10%20pass-2ea44f)](examples/repository-check-2026-08-02.txt)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

**A gated five-stage workflow for listed-company research, modeling, valuation, charts, and IC reports.**

[Showcase](#showcase) · [Deliverables](#what-it-delivers) · [Install](#quick-start) · [Prompts](#example-prompts) · [Validation](#validation-and-showcase-status) · [Safety](#safety-boundaries)

</div>

---

<a id="showcase"></a>

## Real case: MongoDB full report

<p align="center">
  <img src="assets/showcase/mongodb-workflow.gif" alt="MongoDB full-report workflow showcase" width="100%">
</p>

<p align="center"><sub>A real replay: investment conclusion → competitive structure → scenarios and sensitivity → probability weights → valuation cross-check. The market snapshot is 2026-07-26; this is not a current recommendation.</sub></p>

![MongoDB audited report overview](assets/showcase/mongodb-showcase.png)

This is not a mockup. The report passed the current final gates: **44 pages, 38,419 body characters, 23/23 content gates, 14/14 model hard gates, 10/10 repository checks, and an independent PASS**. See the [MongoDB showcase record](examples/mongodb/README.md) and [manifest](examples/mongodb/showcase_manifest.json) for the source-page hashes, generated-asset hashes, gate results, and known limitation.

> The complete PDF is not distributed. The selected pages avoid third-party product-architecture images and retain only project-generated conclusion, competition, scenario, and valuation pages. Rebuild the GIF and cards with the [showcase build script](scripts/build_showcase.py).

---

## Why it exists

Asking an agent to “analyze this stock” is easy. Proving that its sources, forecasts, valuation, charts, and conclusion use the same facts is much harder.

Public Investment Analysis turns listed-company research into a gated workflow. Each stage consumes prior outputs, creates a defined artifact, and stops on failure. It is designed for work that needs DCF, forward P/E and P/S, public-company dilution, buybacks, and traceable evidence—not just a plausible narrative.

## What it delivers

| Mode | Deliverables | Typical use |
|---|---|---|
| Quick memo | A 2–3 page decision memo with recommendation and target, priced-in vs. variant view, risks, tripwires, and a six-month action map | Screening, earnings updates, position reviews |
| Full report | Research document, Excel operating model, valuation analysis, PNG charts, and a typically 30–40 page IC Report DOCX | Initiation, investment committee, deep review |

```text
public sources → research → Excel model → DCF/multiples → charts → IC Report DOCX
                   PASS         PASS            PASS       PASS
```

Every `PASS` must come from an executed check or an explicit human checkpoint.

## Quick start

After the public repository is available:

```bash
npx skills add Mai-coding/public-investment-analysis
```

Validate a local checkout without publishing it:

```bash
cd public-investment-analysis
npx skills add . --list
```

Install Python 3.10+ dependencies for the full-report scripts:

```bash
python -m pip install -r requirements.txt
```

First prompt:

```text
Use public-investment-analysis to prepare a Chinese quick memo on MongoDB (MDB).
Use current public filings, show a 12-month target, priced-in vs. variant view,
three killer risks, and a six-month action map. Do not guess missing data.
```

The first run needs a target company, sector, and either source documents or a ticker whose filings can be retrieved. The core skill does not require a paid API key; retrieval depends on the agent runtime.

## Example prompts

- “Give me a 2–3 page quick decision memo on MDB.”
- “Run a full listed-company IC workflow on MRVL, from research through DOCX.”
- “Turn these 10-Ks, 10-Qs, and earnings calls into an auditable operating model.”
- “Cross-check DCF, forward P/E, and P/S on the same forecast year.”
- “Audit how SBC, options, diluted shares, and buybacks affect per-share value.”
- “Check this model and report for source, period, and citation breaks.”

It is not intended for private-round modeling, venture-stage MOIC/IRR, trade execution, or personalized investment-adviser services.

## What makes it different

| Dimension | Typical one-shot answer | Public Investment Analysis |
|---|---|---|
| Workflow | One generated response | Five staged handoffs with entry and stop conditions |
| Forecasts | Narrative and numbers may diverge | Revenue drives EBITDA; valuation reads model outputs |
| Share count | Often stops at basic shares | Models SBC, options, dilution, and repurchases |
| Valuation | Methods may use inconsistent periods | DCF plus forward P/E/P/S with a shared forecast-year rule |
| Evidence | Links may be decorative | Numbers, snapshot dates, source ledger, and final citations are checked |
| Completion | A polished document may appear done | Machine-audit failures block progression and delivery |
| Context | Loads a large instruction bundle | Loads task-specific references just in time |

## Safety boundaries

- Never fabricate missing filings, consensus data, images, inputs, or prior-task outputs.
- Stop after each task by default unless the user explicitly asks for continuous execution.
- Any machine-audit `FAIL` blocks progression or delivery; human visual and reader QA remain required.
- Do not execute trades, contact companies or brokers, or publish conclusions without instruction.
- Use public research sources and keep secrets, cookies, private paths, and account data out of artifacts.
- Outputs are research workflow artifacts, not investment advice.

## Repository map

```text
SKILL.md                 # Agent entry point, workflow, and global gates
references/              # Task rules, methods, schemas, and load map
scripts/                 # Retrieval helpers, audits, and regression tests
assets/                  # Palette, prompts, and redistributable OFL fonts
examples/                # Copyable prompts and recorded validation evidence
requirements.txt         # Python dependencies
LICENSE / NOTICE         # Apache-2.0 and attribution
```

## Validation and showcase status

```bash
python scripts/run_repo_checks.py
```

The recorded result is **10 PASS / 0 FAIL** across reference integrity, licenses and fonts, context budgets, source coverage, showcase hashes and render specifications, four regression suites, and Python syntax. See the [recorded summary](examples/repository-check-2026-08-02.txt).

The local installer path was also exercised: `npx skills add . --list` found exactly one skill, `public-investment-analysis`.

The first full-report showcase now passes model, content, depth, all-page visual QA, and independent review. See the [MongoDB case](examples/mongodb/README.md); the [showcase manifest](examples/mongodb/showcase_manifest.json) records the validation results and file hashes.

See [`examples/`](examples/README.md) for a copyable quick-memo input and acceptance contract.

## Credits and third-party assets

This project substantially adapts the public workflow ideas in [Anthropic Financial Services](https://github.com/anthropics/financial-services). See [NOTICE](NOTICE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Bundled [LXGW WenKai](https://github.com/lxgw/LxgwWenKai) and [Source Serif 4](https://github.com/adobe-fonts/source-serif) fonts use the SIL Open Font License 1.1. See [`assets/fonts/`](assets/fonts/README.md).

## License

[Apache License 2.0](LICENSE)
