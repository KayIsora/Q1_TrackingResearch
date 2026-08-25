# Stage 4A-S1-R1 — Clean-room interval-proposal execution protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE R1 EXECUTION  
**Prerequisite:** `screening/reconciliation/2026-08-26_stage4A_S1_R0v2_semantic_reconciliation.md`.

## 1. Purpose

R1 converts the accepted outcome-independent OTB sequence inventory into proposed distractor and matched-control intervals with source-only contact sheets for Manager review.

R1 does not freeze the final diagnostic slice and does not start Stage 4B.

## 2. Working boundary

Use the accepted external clean room:

`F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2\`

and the canonical read-only OTB source:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

The invalid v1 clean room and all earlier temporary S1 outputs remain prohibited.

## 3. Repository boundary

At task start, R1 may read by exact path only:

- this protocol;
- `screening/reconciliation/2026-08-26_stage4A_S1_R0v2_semantic_reconciliation.md`.

After that, all scientific selection work must use only the accepted v2 clean-room inputs and canonical OTB source.

Repository-wide search, recursive Q1 enumeration and history search remain prohibited.

## 4. Outcome prohibition

R1 may not access or use:

- local or author-released tracker predictions;
- AUC, IoU, success or failure records;
- first-divergence evidence;
- score/confidence maps;
- MRM logs or ablation results;
- tracker-derived hard-frame rankings.

The occurrence of a quarantined sequence name in source/evaluator mapping is allowed. Association with tracker-outcome evidence is prohibited.

## 5. Mandatory quarantine filter

Before inspecting any source frame, create:

`outputs\r1\quarantine_filter.csv`

with rows for:

- Deer
- Crossing
- Couple

and columns:

- `sequence`
- `source_inventory_present`
- `candidate_pool_excluded`
- `control_pool_excluded`
- `coverage_excluded`
- `frames_opened`
- `notes`

Required values:

- all three excluded fields = `true`;
- `frames_opened = false`.

The R1 script/process must remove these rows before creating the candidate/control scan lists. They must not be scanned, proposed or counted.

## 6. Starting pool

Use the clean-room copy of:

`inputs\project\2026-08-25_stage4A_E2_slice_inventory.csv`.

Candidate scan pool:

- non-empty `candidate_distractor_reason`;
- sequence not in the mandatory quarantine.

Potential-control pool:

- non-empty `potential_control_sequence_reason`;
- sequence not in the mandatory quarantine.

Every lead must be rescanned from source frames. No E2 lead is automatically accepted.

## 7. Scan procedure

Follow the clean-room copy of:

`inputs\project\2026-08-26_stage4A_S1_slice_proposal_protocol.md`.

For each candidate sequence:

- inspect at least 25 uniformly spaced frames when the evaluator range has 125 or more frames;
- inspect every frame when it has fewer than 125 frames;
- refine plausible events frame-by-frame;
- record continuous co-occurrence intervals from source content only;
- record rejected/ambiguous events.

GT may be used only to locate the target and derive target scale, motion and nominal search geometry.

## 8. Proposal requirements

Primary proposals must normally be `TIER_A` or strong `TIER_B` and must satisfy:

- valid target GT;
- visible target;
- visually/semantically similar non-target;
- at least five consecutive co-occurrence frames;
- distractor inside or near the GT-derived nominal search context;
- source-content-based interval bounds;
- clear similarity/confusion rationale.

Preferred core length: 5–40 frames.

No more than three primary intervals from one sequence.

## 9. Controls

Every primary proposal requires at least one proposed control, preferring:

1. same-sequence interval without a similar distractor;
2. same-class cross-sequence interval with similar target scale/motion;
3. comparable-attribute interval.

Controls may not be chosen from tracker performance.

## 10. Diversity and provisional split

The proposal package must support later Manager selection of:

- at least 10 unique distractor-bearing sequences;
- at least three broad superclasses;
- no broad superclass over 60% when avoidable;
- at least six discovery-candidate sequences;
- at least four additional hold-out-candidate sequences;
- sequence-disjoint proposed groups.

The split remains provisional.

## 11. Contact sheets

For every primary proposal and control, create a five-frame source-only contact sheet with:

- target GT box in green;
- manually annotated distractor box in red when applicable;
- GT-derived nominal search context in blue when useful;
- sequence/frame and proposal/control ID.

No tracker output may appear.

Store externally during construction under:

`outputs\r1\contact_sheets\`

and commit bounded copies under the authorized Q1 artifact path after completion.

Total committed contact-sheet payload must not exceed 30 MiB.

## 12. External R1 artifacts

Create under the accepted v2 root:

- `outputs\r1\quarantine_filter.csv`
- `outputs\r1\distractor_interval_proposals.csv`
- `outputs\r1\control_interval_proposals.csv`
- `outputs\r1\contact_sheet_manifest.csv`
- `outputs\r1\slice_proposal_report.md`
- `outputs\r1\contact_sheets\...`
- `logs\r1_commands.txt`

Every command must be logged.

## 13. Q1 artifacts

Create only:

- `screening/codex/2026-08-26_stage4A_S1_R1_quarantine_filter.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_distractor_interval_proposals.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_control_interval_proposals.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_contact_sheet_manifest.csv`
- `screening/codex/2026-08-26_stage4A_S1_R1_slice_proposal_report.md`
- `screening/codex/2026-08-26_stage4A_S1_R1_command_log.txt`
- contact sheets under `screening/codex/artifacts/stage4A_S1_R1/contact_sheets/`
- optional exact reproducibility script under `screening/codex/scripts/2026-08-26_stage4A_S1_R1_build_proposals.py`.

No existing file may be modified.

## 14. Validation

Before commit verify:

- quarantine filter created before frame inspection;
- Deer/Crossing/Couple frames were never opened;
- no tracker-outcome source was accessed;
- all candidate leads were rescanned from zero;
- primary intervals satisfy duration/search-context requirements;
- every primary proposal has a control;
- coverage/diversity requirements are satisfied or the exact gap is reported;
- proposed split is sequence-disjoint;
- contact sheets contain only allowed overlays;
- no final interval/split/ambiguity decision is claimed;
- no Stage 4B, DIAG or soft scoring occurred.

## 15. Allowed conclusions

- `S1_R1_COMPLETE_READY_FOR_MANAGER_VISUAL_REVIEW`
- `S1_R1_INSUFFICIENT_INTERVAL_COVERAGE`
- `S1_R1_INVALID_OUTCOME_EXPOSURE`
- `S1_R1_INCOMPLETE`

## 16. Locked downstream state

- Stage 4A-S1-R1: READY
- Manager visual review: LOCKED PENDING R1
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
