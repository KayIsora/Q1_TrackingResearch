# Stage 4A-S1-R0V2 — Corrected clean-room setup protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE CORRECTED CLEAN-ROOM SETUP  
**Purpose:** create a physically isolated, hash-audited and outcome-free input bundle for a fresh interval-proposal lane.

## 1. Boundary

R0V2 creates and verifies the corrected clean-room bundle only. It does not inspect OTB frames, scan candidate sequences, propose intervals or controls, create contact sheets, assign tiers or splits, freeze a diagnostic slice, run SpikeTrack or start Stage 4B.

The first S1 lane and the first R0 bundle are invalidated by:

- `screening/reconciliation/2026-08-26_stage4A_S1_outcome_independence_incident.md`
- `screening/reconciliation/2026-08-26_stage4A_S1_R0_contamination_reconciliation.md`

Neither incident file is copied into the corrected clean room.

## 2. Fresh-lane requirement

R0V2 must run in a new Codex window/session. The lane must not reuse any notes, selections, temporary files, scripts or external outputs from either invalidated attempt.

## 3. New external root

Create exactly:

`F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2\`

The root must not preexist. The invalid first root must not be read, reused, copied, compared or deleted as part of R0V2.

Create:

- `inputs\project\`
- `inputs\spiketrack_contract\`
- `inputs\dataset_pointer\`
- `outputs\`
- `logs\`

## 4. Exact allowed project inputs

Copy by exact path only:

1. `screening/manager/2026-08-26_stage4A_S1_slice_proposal_protocol.md`
2. `screening/manager/2026-08-26_stage4A_S1_cleanroom_safe_source_summary.md`
3. `screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv`
4. `screening/codex/2026-08-25_stage4A_E2_otb_source_manifest.csv`
5. `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`
6. `docs/00_claim_taxonomy.md`

No other Q1 file may be copied.

Specifically prohibited from copying or reading during R0V2:

- the full E2 reconciliation;
- either S1 incident/reconciliation file beyond the exact R0V2 protocol already supplied by Manager;
- E2 reproduction CSVs;
- Stage 4A-R resolution reports;
- any result, prediction, metric, divergence, score, confidence or MRM artifact.

## 5. Exact allowed SpikeTrack-contract inputs

From the official SpikeTrack checkout pinned at commit:

`1537db51a1cc9f6e30cce469fba3e51f5721b3d0`

copy by exact path only:

1. `lib/test/evaluation/otbdataset.py`
2. `experiments/spiketrack/spiketrack_s256_t1.yaml`
3. `lib/test/tracker/seqtrack_utils.py`

Record the checkout path, `git rev-parse HEAD`, `git status --short`, byte size and SHA-256 of each source and copy.

Do not copy model code, checkpoints, result files, raw archives, instrumentation, logs or scripts from earlier S1 attempts.

## 6. Canonical dataset pointer

Do not duplicate the dataset into the clean room.

Create a text pointer under `inputs\dataset_pointer\` for the read-only source root:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

Record only source-selection facts:

- archive SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`
- extracted-file manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`
- source-root existence
- physical sequence-directory count
- read-only intent

Do not inspect sequence frames during R0V2.

## 7. Prohibited repository operations

Inside the Q1 repository, do not use:

- `git grep`
- `rg` or `ripgrep`
- recursive `grep`
- `findstr /s`
- `Get-ChildItem -Recurse`
- repository-wide `Select-String`
- IDE/global search
- GitHub repository code search
- `git log -S` or `git log -G`
- history/patch search
- broad filename wildcard searches
- scripts that recursively enumerate the repository

Allowed repository operations are limited to:

- `git status`
- `git pull origin main`
- `git log -1 --oneline`
- exact-path reads
- exact-path copies
- final exact-path additions of the three R0V2 artifacts

Any prohibited repository operation invalidates R0V2 immediately.

## 8. Expected bundle composition

Before generated audit files, the corrected bundle must contain exactly ten allowed inputs:

- 6 project files
- 3 SpikeTrack contract files
- 1 dataset pointer

No outcome evidence is permitted.

## 9. Command log

Record every R0V2 command in:

`logs\commands.txt`

Each entry must include:

- timestamp
- working directory
- exact command
- exit code
- purpose

Failed commands must remain in the log.

## 10. Input manifest and tree

Create externally:

- `inputs\cleanroom_manifest.csv`
- `inputs\cleanroom_tree.txt`

Manifest columns:

- `input_id`
- `category`
- `source_exact_path`
- `cleanroom_relative_path`
- `byte_size`
- `sha256`
- `allowed_by_protocol`
- `notes`

The tree command may recurse only inside the new v2 clean-room root.

## 11. Corrected contamination scan

A recursive filename/content scan is permitted only inside the new v2 clean-room root.

The scan must reject:

- any file outside the exact ten-input whitelist plus generated R0V2 audit files;
- filenames or payload records from reproduction/result directories;
- fields such as `success_auc_percent`, `released_success_auc`, `prediction_sha256`, `first_divergence` or equivalent outcome tables;
- sequence-level performance values;
- raw/local prediction rows;
- score, confidence or MRM diagnostic payloads;
- any content copied from either invalidated clean-room root.

Policy text may mention prohibited concepts abstractly. The scan report must distinguish policy prohibitions from actual outcome-data payload.

The quarantine names Deer, Crossing and Couple may appear only as sequence names in protocol/safe-summary policy text, with no associated performance values or prediction data.

## 12. Attestation

Create externally:

`outputs\cleanroom_attestation.md`

It must state:

- fresh Codex window/session used;
- no prior S1 work reused;
- invalid v1 clean-room root not accessed;
- no prohibited repository operation executed;
- no prohibited Q1 file read or copied;
- no OTB frame inspected;
- no tracker output or metric accessed;
- no sequence proposal or contact sheet created;
- exactly the approved inputs are present;
- R1 must restart all scanning from zero.

## 13. Required Q1 artifacts

Create only:

- `screening/codex/2026-08-26_stage4A_S1_R0v2_cleanroom_report.md`
- `screening/codex/2026-08-26_stage4A_S1_R0v2_cleanroom_manifest.csv`
- `screening/codex/2026-08-26_stage4A_S1_R0v2_command_log.txt`

The Q1 manifest must reproduce the external input manifest and record:

- external clean-room root
- external manifest SHA-256
- clean-room tree SHA-256
- attestation SHA-256
- expected input count and observed input count

Do not commit the external clean-room directory.

## 14. Validation

Before completion verify:

- new v2 root did not preexist
- invalid v1 root was not accessed
- exactly six project inputs copied
- exactly three SpikeTrack contract inputs copied
- exactly one dataset pointer created
- all source/copy hashes match
- no OTB frame inspected
- no outcome evidence present
- no proposal/control/contact sheet exists
- command log is complete
- repository changes are limited to the three R0V2 files

## 15. Allowed conclusion

- `S1_R0V2_COMPLETE_CLEANROOM_READY_FOR_MANAGER_REVIEW`
- `S1_R0V2_INVALID_CONTAMINATION`
- `S1_R0V2_INCOMPLETE`

R0V2 does not authorize R1 automatically.

## 16. Locked state

- Stage 4A-S1-R0V2: READY
- Stage 4A-S1-R1: LOCKED PENDING R0V2 REVIEW
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
