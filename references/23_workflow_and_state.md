# Workflow, gates and task state

This file owns gate order, handoff eligibility and revision invalidation. Task outputs and analytical policies remain with their existing owners. Commands below are relative to the skill package; artifact paths are examples. Store logs and handoffs in the analysis workspace.

## Stage gates

| Stage | Required checks, in order | Stable gate IDs |
|---|---|---|
| Task 1, full report | `source_coverage_audit.py --in <research.md>`, then `depth_audit.py --stage research --in <research.md> [--dir <entity_filings>]`; inspect the named human-review sample | `source_coverage`, `research_depth`, `research_review` |
| Task 2 | `artifact_audit.py --excel <model.xlsx>`; perform the orchestrator's driver-linkage test | `artifact`, `model_linkage` |
| Task 3 | `artifact_audit.py --excel <model.xlsx>`; perform the orchestrator's central/diagnostic and 3Y sensitivity tests | `artifact`, `valuation_sensitivity` |
| Task 4 | Complete chart overlap checks, per-image inspection and contact-sheet/coverage review in the chart orchestrator | `chart_overlap`, `chart_visual`, `chart_coverage` |
| Task 5 | Run the three commands below, then the human checklist | `artifact`, `report_content`, `final_depth`, `final_review` |

Run Python scripts through `python scripts/<script>` with the arguments shown above. Task 1's coverage-template command remains a collection aid, not a passed gate. For Task 5:

```text
python scripts/artifact_audit.py --excel <model.xlsx> --report <report.docx> [--prev <previous.docx>]
python scripts/report_content_audit.py --report <report.docx> --charts-manifest <charts_v1/charts_manifest.json>
python scripts/depth_audit.py --stage final --in <report.docx> [--prev <previous.docx>]
```

Charts and their visual QA precede assembly. Refresh fields and complete final rendering before the Task 5 gates; then complete `10_final_checklist.md`. Repairs invalidate affected results: rerun the corresponding checks on the repaired artifacts. Preserve full console logs and a specific human-review record. All applicable checks must pass; manual marks cannot override a FAIL.

This consolidation does not add full-report gates to quick memos. Preserve the existing lightweight scope and record which checks were applicable, with a reason for any `NOT_APPLICABLE` result. Never use that status to waive a required full-report gate.

## Handoff and reuse

Use `handoff_schema.json` version 2.0; its `x-required-gates` and `x-upstream-tasks` are the machine-readable gate/dependency lists for the stage table above. Every new handoff records `analysis_id`, confirmed `mode`, monotonic task `revision`, `state`, source snapshot, outputs, SHA-256 `artifacts`, direct `upstream_handoffs`, source/model `inputs`, gate evidence and unresolved gaps. Paths resolve relative to the handoff, not the shell directory. Hash actual file bytes; directories use a deterministic recursive digest. Evidence records include a path and digest, not just the word PASS. The checker validates records; it does not run audits or prove human judgment.

Before a task, validate required upstreams together (repeat `--handoff` for each). This preserves the shared-workbook version chain. After actual checks, write and validate the new handoff:

```text
python scripts/handoff_audit.py --handoff <handoff_taskN.json>
```

Keep the analysis ID and confirmed mode stable; increment revisions on changes. Upstream records identify task, revision, path and SHA-256 of the handoff JSON. Use the schema's dependency list. A user-requested standalone task may omit unavailable predecessors only with `execution_scope=standalone` and a `scope_reason`; its own checks remain required.

Each PASS gate includes `evidence_path`, `evidence_sha256` and `checked_state_sha256`. Obtain the latter with `handoff_audit.py --state-digest <draft_handoff.json>` after the check. It binds the result to the recorded artifact, input and upstream hashes: changing these invalidates the old result. Updating fingerprints alone cannot refresh a gate. Gate logs/review notes must reflect actual checks on those bytes.

The checker follows upstream records, checks identity/mode/revisions, rejects cycles, verifies files and gate evidence, and blocks FAIL/PARTIAL, stale or changed inputs. Older handoffs without version/fingerprints are historical evidence: inspect their artifacts, run applicable checks and issue a new revision before reuse; do not manufacture a retrospective PASS.

Task 3 edits the Task 2 workbook in place. In a validated downstream chain, a later task's verified output may supersede an earlier task's output at the same exact path; this does not waive the earlier gate evidence. Verify predecessors before mutation. For source inputs that will be mutated, retain an internal snapshot and fingerprint that snapshot. Do not fingerprint the pre-edit workbook as an unchanged live input after editing it. Preserve versioned handoff JSON so downstream references do not silently change.

## Revision invalidation

Use the impact matrix in [Model consistency](19_model_provenance_and_consistency.md#五全局影响矩阵) to identify affected outputs. Set affected handoffs to `state=stale`, record `change_reason` and `affected_artifacts`, and preserve the prior handoff revision. An upstream hash mismatch also makes descendants ineligible even if their old status says PASS.

Rebuild only affected work in dependency order: research/model or evidence → valuation → charts → report. Apply the impact matrix to select checks, rerun them on final bytes, write new fingerprints and increment revisions. Refresh direct upstream references only after checking them. Restore `state=current` only when the affected artifacts and applicable gates have been verified; unchanged work can be retained with a documented scope comparison.

## Reading budgets

`task_load_map.json` owns reading routes. Read entrypoint/shared files once, then the current phase. Task 5 loads the human checklist in `reader_qa`, after production gates; every task loads the schema when preparing its handoff. Reuse unchanged references across phases.

`scripts/context_budget_audit.py` includes entrypoint/shared overhead in each phase and reports new additions, deduplicated task totals and named routes. All conditional groups are checked individually and together against the task budget; named combinations can be checked with `--route model_revision --conditional task3.comparable_set_refresh`. Phase budgets retain the original 18,000-token ceiling; cumulative task/route budgets are separate reading-volume limits. Estimates do not represent exact tokens or runtime context occupancy. Quick routing remains unchanged.
