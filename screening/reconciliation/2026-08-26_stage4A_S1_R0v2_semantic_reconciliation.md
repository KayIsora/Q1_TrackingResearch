# Stage 4A-S1-R0V2 — Semantic contamination reconciliation

**Date:** 2026-08-26  
**Status:** `R0V2_ACCEPTED_AFTER_SEMANTIC_REVIEW`; Stage 4A-S1-R1 may be prepared.  
**Inputs:**

- `screening/codex/2026-08-26_stage4A_S1_R0v2_cleanroom_report.md`
- `screening/codex/2026-08-26_stage4A_S1_R0v2_cleanroom_manifest.csv`
- `screening/codex/2026-08-26_stage4A_S1_R0v2_command_log.txt`
- `screening/manager/2026-08-26_stage4A_S1_R0v2_cleanroom_setup_protocol.md`
- `screening/manager/2026-08-26_stage4A_S1_cleanroom_safe_source_summary.md`

## Boundary

This reconciliation decides only whether the v2 clean-room input bundle is scientifically outcome-independent. It does not scan any OTB frame, propose an interval/control, freeze a slice, start Stage 4B, assign `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, select a baseline, or authorize architecture design.

## What Codex detected

Codex correctly stopped under the literal R0V2 wording because the names:

- `Deer`
- `Crossing`
- `Couple`

occur in the copied outcome-independent OTB inventory, OTB source manifest and pinned `otbdataset.py`, whereas the protocol stated that those names could occur only in protocol/safe-summary policy text.

Codex also established that:

- exactly 10 whitelisted inputs were copied;
- all source/copy hashes match;
- the invalid v1 root was not accessed;
- no OTB frame was inspected;
- no tracker output, prediction row, metric, divergence record, score/confidence value or MRM diagnostic payload was present;
- no sequence proposal, control, split or contact sheet was produced;
- tokens/fields such as `success_auc_percent`, `released_success_auc`, `prediction_sha256` and `first_divergence` were absent from the ten inputs;
- the only failed condition was quarantine-name placement.

## Manager protocol error

The literal name-placement rule was over-constrained.

A sequence name appearing in:

- an outcome-independent source inventory;
- an evaluator mapping;
- a source-path manifest;
- or an explicit quarantine/exclusion rule

is **not tracker-outcome evidence**. The names are required to identify and exclude the three sequences. Treating their mere appearance as contamination conflated source identity with performance exposure.

The scientifically relevant boundary is whether a sequence name is associated with tracker-derived evidence, for example:

- prediction rows or hashes;
- AUC/IoU/success values;
- first-divergence or failure-frame data;
- score/confidence maps;
- MRM logs or ablation outcomes;
- local-versus-released result comparisons.

No such association exists in the v2 bundle.

## Semantic correction — locked before R1

For all subsequent clean-room work:

### Allowed quarantine-name occurrence

`Deer`, `Crossing` and `Couple` may appear only as:

- sequence identifiers in the outcome-independent inventory/source/evaluator mapping;
- explicit quarantine names;
- exclusion-log entries confirming that they were filtered before scanning.

### Prohibited outcome association

The same names may not appear together with or be linked to:

- tracker predictions;
- performance values;
- divergence/failure evidence;
- result-directory paths;
- score/confidence output;
- MRM diagnostic output;
- any ranking based on tracker behavior.

### Mandatory R1 filter

Before any source-frame scan, the R1 lane must create a machine-readable quarantine filter that removes the three sequence rows from:

- the candidate scan pool;
- the control pool;
- all coverage counts;
- all proposed split logic.

R1 must not open source frames for the three sequences.

## Clean-room decision

The external v2 root:

`F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2\`

is accepted as **outcome-free and scientifically usable** for R1.

This decision supersedes only the lexical contamination conclusion in the Codex report. It does not alter any file/hash fact recorded by Codex and does not excuse future access to outcome evidence.

The invalid v1 root remains permanently prohibited.

## Why a v3 rebuild is unnecessary

A new bundle would copy the same outcome-independent inventory and evaluator mapping. Removing all three names from source/evaluator inputs would either:

- make quarantine auditing less transparent; or
- require derived/sanitized copies that add transformation risk without reducing outcome exposure.

The v2 bundle already contains no outcome payload. A semantic correction and mandatory pre-scan filter provide the stronger, auditable boundary.

## Decision

**Final R0V2 state:** `ACCEPTED_AFTER_SEMANTIC_REVIEW`.

**Next stage:** `Stage 4A-S1-R1 — outcome-independent interval proposals`, using only the accepted v2 clean room and canonical OTB source.

## Locked state

- Stage 4A-S1 attempt 1: INVALIDATED
- Stage 4A-S1-R0 v1: INVALIDATED
- Stage 4A-S1-R0V2: ACCEPTED AFTER SEMANTIC REVIEW
- Stage 4A-S1-R1: READY
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
