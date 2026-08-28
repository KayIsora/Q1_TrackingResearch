# F6 — lean resource and 2026 candidate-universe refresh

**Date:** 2026-08-29  
**Status:** `LOCKED_BEFORE_REFRESH`  
**Prerequisite:** `screening/reconciliation/2026-08-29_F2_final_reconciliation.md`

## 1. Purpose

The current F2 cycle ended without a scientific result because both authorized candidates stopped before model execution on resource/runtime blockers. The next step is not another compatibility attempt and not automatic substitution with SSTrack. It is a bounded desk-only refresh to answer two questions:

1. Have the exact blocked official resources or release contracts changed enough to permit a later clean preflight?
2. Has a newly accepted/published 2026 generic RGB-SOT tracker or official release been missed since Stage-1 discovery?

This stage preserves the scientific gates while preventing more time from being spent on dependency-by-dependency execution repair.

## 2. Hard limits

- desk/repository/web evidence only;
- no model/checkpoint instantiation;
- no model forward;
- no package or environment installation;
- no dataset/checkpoint/pretrain download;
- no profiling;
- no benchmark execution;
- no new diagnostic slice;
- no HG6, scoring, shortlist, baseline selection or architecture design;
- one Markdown report and one CSV only;
- at most 12 resource/candidate records;
- at most 90 minutes of active refresh work;
- no repeat of the 409-query Stage-1 campaign.

## 3. Resource-refresh queue

Check these exact blockers first:

### CX010 — UTPTrack

Determine from official author-controlled sources:

- official dependency/environment contract;
- whether `visdom`, `jpeg4py` and legacy `torch._six` compatibility are documented requirements or release defects;
- whether an official environment file/container/lock now reaches tracker import and strict-load conceptually;
- whether the checkpoint/config/evaluator mapping has changed.

Do not install or test the environment.

### CX038 — MCITrack

Determine from official author-controlled sources:

- exact official location and identity of `fast_itpn_base_clipl_e1600.pt`;
- whether the asset is required even when a released full tracker checkpoint is used;
- whether an official construction/evaluation path bypasses bootstrap loading before strict-loading the final checkpoint;
- whether the checkpoint/config/evaluator mapping has changed.

Do not download the asset.

### Evidence-gated candidates

Check only for official changes to the existing blockers:

- CX046 JDTrack — required final tracker checkpoint availability/mapping;
- CX051 UMDATrack — official asset/config/evaluator coherence;
- CX053 UncTrack — PMN mask and mutable K/V export/runtime contract.

No deep audit is permitted when no official delta exists.

## 4. Narrow 2026 universe refresh

Search only for:

- peer-reviewed/accepted 2026 generic RGB box-SOT trackers;
- top conferences or Q1 journals under the project's accepted venue policy;
- official code, tracker checkpoint and evaluator availability;
- candidates not already represented in the canonical matrix or Stage-1 universe;
- publication or official-resource changes after the last verified Stage-1/Stage-2 evidence.

Exclude:

- arXiv-only methods as main candidates;
- multimodal-only trackers without a valid generic RGB core;
- segmentation-only/video-object-segmentation systems without a box-SOT core;
- papers already present under another family name;
- methods whose only visible opportunity is standard compression/porting.

The refresh is a delta search, not a new systematic screening campaign.

## 5. Allowed record states

For resource records:

- `RESOURCE_REENTRY_READY_FOR_F0`;
- `RESOURCE_HOLD_NO_CHANGE`;
- `RESOURCE_CONFLICT_REQUIRES_AUTHOR_CLARIFICATION`.

For newly found candidate families:

- `NEW_CANDIDATE_F0_READY`;
- `NEW_CANDIDATE_REFERENCE_ONLY`;
- `DUPLICATE_OR_OUT_OF_SCOPE`.

A ready state does not authorize model execution, mini-probe, HG6, score or baseline selection.

## 6. Re-entry requirements

### UTPTrack

`RESOURCE_REENTRY_READY_FOR_F0` requires an official, auditable environment/dependency contract that accounts for the import chain through tracker construction and leaves no known unresolved dependency before strict load.

### MCITrack

`RESOURCE_REENTRY_READY_FOR_F0` requires an exact official bootstrap asset or official documented build path, with stable URL/file identity and a coherent relation to the released full tracker checkpoint.

### JDTrack / UMDATrack / UncTrack

A ready state requires the exact earlier HG3/HG5 blocker to be resolved by an official release delta, not a community workaround or Manager inference.

## 7. Decision after refresh

- If at least one resource becomes re-entry-ready, run a new desk F0 contract before any execution.
- If a genuinely new 2026 candidate is F0-ready, add it to a small delta-audit queue; do not insert it directly into the canonical shortlist.
- If no actionable delta exists, conclude `NO_ACTIONABLE_REFRESH` and stop for strategic review rather than spending more time on the same candidates.

## 8. Required outputs

Create:

- `screening/codex/2026-08-29_F6_resource_universe_refresh.md`;
- `screening/codex/2026-08-29_F6_resource_universe_refresh.csv`.

CSV columns:

`record_id,record_type,candidate_id_or_new,method_or_resource,official_source,previous_blocker_or_scope,observed_delta,evidence_date,code_status,checkpoint_status,evaluator_status,task_modality_fit,resource_or_candidate_state,next_minimum_action,notes`

## 9. Locked non-claims

- UTPTrack and MCITrack are not scientifically rejected;
- neither candidate is active;
- SSTrack is not automatically authorized;
- the refresh queue is not a shortlist;
- no S1–S7 score exists;
- no main baseline or proposed architecture exists.

## Locked state

- F2: `COMPLETE / NO SCIENTIFIC OUTCOME`;
- F3: `NOT OPENED`;
- F6 refresh: `READY`;
- active main-baseline candidate: `NONE`;
- S1–S7: `NOT STARTED`;
- primary shortlist: `NONE`;
- main baseline: `NONE`;
- proposed architecture: `NONE`.
