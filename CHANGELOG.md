# Changelog

## 2026-10-20

Sync the installed skill to the existing public repository so GitHub installs receive the current research workflow and audit tools.

- Frame investment conclusions as a Price Band Decision Map with expected three-year returns and market-priced versus evidence-supported assumptions.
- Ask for quick memo or full report mode at the start of a new analysis; retain the choice during continuation and revisions.
- Add workflow state, versioned handoff validation, revision invalidation and phase-level context routing.
- Expand financial-model, terminal-multiple, report-content, table, image-marker, presentation and DOCX-layout checks.
- Keep the historical MongoDB showcase and its original validation metrics distinct from current package checks.

Validation: the [repository check runner](scripts/run_repo_checks.py) completed with **16 PASS / 0 FAIL** on Windows / Python 3.13.12. `npx skills add . --list` detected exactly one skill, `public-investment-analysis`. The Luban structure check recorded **11 PASS / 3 WARN / 0 FAIL**; optional marketplace metadata and a skills.sh badge are absent, and the shell checker does not recognize the existing Python showcase builder as a recording script.

This is a package synchronization, not a new end-to-end research validation. See [the check log](examples/repository-check-2026-10-20.txt).
