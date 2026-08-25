# Stage 4A-S1-R0 — Clean-room setup protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE CLEAN-ROOM SETUP  
**Purpose:** create a physically isolated, hash-audited input bundle for a fresh outcome-independent interval-proposal lane.

## 1. Boundary

R0 creates the clean-room bundle only. It does not scan candidate sequences, propose intervals or controls, create contact sheets, assign tiers or splits, freeze the diagnostic slice, run SpikeTrack, or start Stage 4B.

The previous S1 lane is invalidated by `screening/reconciliation/2026-08-26_stage4A_S1_outcome_independence_incident.md`.

## 2. Fresh-lane requirement

R0 must run in a new Codex window/session that has not inspected the prohibited reproduction files during the current task.

The new lane may know that an incident occurred, but it must not read or reuse any uncommitted notes, selections, scripts, temporary outputs or memory from the invalidated S1 attempt.

## 3. External clean-room root

Create a new directory that must not preexist:

`F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26\`

Subdirectories:

- `inputs\project\`
- `inputs\spiketrack_contract\`
- `inputs\dataset_pointer\`
- `outputs\`
- `logs\`

If the root already exists, stop and report a clean-room collision. Do not reuse or delete it silently.

## 4. Exact allowed project inputs

Copy by exact path only:

1. `screening/manager/2026-08-26_stage4A_S1_slice_proposal_protocol.md`
2. `screening/reconciliation/2026-08-26_stage4A_E2_otb_reconciliation.md`
3. `screening/reconciliation/2026-08-26_stage4A_S1_outcome_independence_incident.md`
4. `screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv`
5. `screening/codex/2026-08-25_stage4A_E2_otb_source_manifest.csv`
6. `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`
7. `docs/00_claim_taxonomy.md`

No other Q1 repository file may be copied into the clean room.

## 5. Exact allowed SpikeTrack-contract inputs

From the pinned official SpikeTrack checkout at commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`, copy by exact path only:

1. `lib/test/evaluation/otbdataset.py`
2. `experiments/spiketrack/spiketrack_s256_t1.yaml`
3. `lib/test/tracker/seqtrack_utils.py`

Record the checkout path, Git commit, Git status and SHA-256 of each copied file.

Do not copy tracker predictions, result files, model code, instrumentation, checkpoints or logs.

## 6. Canonical dataset pointer

Do not duplicate OTB100 into the clean room.

Create a text pointer/manifest that records the read-only source root:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

Record:

- archive SHA-256 `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`;
- extracted-file manifest SHA-256 `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`;
- source-root existence;
- physical sequence-directory count;
- read-only intent.

Do not alter source bytes or permissions.

## 7. Prohibited repository operations

Inside the Q1 repository, do not use:

- `git grep`;
- `rg` or `ripgrep` without an exact single-file path;
- recursive `grep`;
- `findstr /s`;
- `Get-ChildItem -Recurse`;
- repository-wide `Select-String`;
- IDE/global code search;
- GitHub repository code search;
- `git log -S`, `git log -G` or history search;
- broad `find`, `where`, filename wildcard or content search;
- scripts that recursively enumerate the repository.

Allowed repository operations are limited to:

- `git status`;
- `git pull origin main`;
- `git log -1 --oneline`;
- exact-path file reads;
- exact-path file copies;
- final exact-path additions of R0 artifacts.

A prohibited operation triggers immediate stop and invalidates R0.

## 8. Prohibited source paths

The clean-room bundle must not contain any path or content from:

- `screening/codex/2026-08-25_stage4A_E2_reproduction.csv`;
- `screening/codex/2026-08-25_stage4A_R_spiketrack_resolution.md`;
- `screening/codex/artifacts/stage4A_reproduction/`;
- `screening/codex/artifacts/stage4A_E2/reproduction/`;
- any prediction, metric, divergence, score, confidence or MRM-log artifact;
- any artifact from the invalidated S1 attempt.

## 9. Clean-room inventory and attestation

Create externally:

- `logs\commands.txt` containing every command executed in R0;
- `inputs\cleanroom_manifest.csv` with one row per input file/pointer;
- `inputs\cleanroom_tree.txt` containing only the clean-room relative tree;
- `outputs\cleanroom_attestation.md`.

Manifest columns:

- `input_id`
- `category`
- `source_exact_path`
- `cleanroom_relative_path`
- `byte_size`
- `sha256`
- `allowed_by_protocol`
- `notes`

The attestation must state:

- fresh Codex window/session used;
- no prohibited repository operation executed;
- no prohibited source file read or copied;
- no sequence frame inspected;
- no tracker output or metric accessed;
- no proposal or contact sheet created;
- clean room contains only the approved inputs.

## 10. Contamination scan

Perform a clean-room-only filename and text scan after the bundle is created. This scan may recurse only within the new clean-room root.

Reject the bundle if it contains terms/paths identifying:

- `reproduction` prediction directories;
- `first_divergence`;
- `released_raw`;
- `official_runner_default`;
- `success_auc`;
- `prediction_sha256`;
- MRM diagnostic outputs;
- Deer/Crossing/Couple outcome data beyond their quarantine names in the protocol.

The presence of the words `prediction` or `reproduction` in protocol prohibitions alone is not contamination; the report must distinguish policy text from evidence payload.

## 11. Required Q1 artifacts

Create only:

- `screening/codex/2026-08-26_stage4A_S1_R0_cleanroom_report.md`
- `screening/codex/2026-08-26_stage4A_S1_R0_cleanroom_manifest.csv`
- `screening/codex/2026-08-26_stage4A_S1_R0_command_log.txt`

Do not commit the external clean-room copy itself.

The Q1 manifest must reproduce the external input manifest and include the external root path and clean-room manifest SHA-256.

## 12. Allowed conclusion

- `S1_R0_COMPLETE_CLEANROOM_READY_FOR_MANAGER_REVIEW`
- `S1_R0_INVALID_CONTAMINATION`
- `S1_R0_INCOMPLETE`

R0 does not authorize R1 automatically.

## 13. Locked downstream state

- Stage 4A-S1-R0: READY
- Stage 4A-S1-R1: LOCKED PENDING R0 REVIEW
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
