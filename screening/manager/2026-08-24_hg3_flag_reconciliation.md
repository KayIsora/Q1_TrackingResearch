# Manager lane — HG3 flag reconciliation

**Date:** 2026-08-24  
**Status:** MANAGER RESOLUTION COMPLETE; independent Codex cross-check still required before Stage-2 deep gates begin.  
**Governing files:** `RULE/01_EVIDENCE_AND_CITATION_POLICY.md`, `docs/11_systematic_screening_protocol.md`, `screening/reconciliation/2026-08-24_stage1_reconciliation_report.md`, and `screening/codex/2026-08-24_audit_queue_source_normalization_report.md`.

## Purpose

Resolve the six HG3 reconciliation flags raised during source normalization without starting HG4/HG5/HG6 or any soft score. HG3 is interpreted exactly as the locked protocol states: official source code, the pretrained weights actually required by the method, and a usable benchmark evaluation script/protocol or official integration sufficient to make baseline reproduction realistic.

For a training-free method, the checkpoint requirement is applied to the official pretrained foundation weights used at inference; a nonexistent family-trained checkpoint is not required merely to satisfy wording intended for trainable trackers.

## Manager decisions

| Candidate | Decision | Evidence-based rationale |
|---|---|---|
| **SAMURAI (CX020)** | **HG3 PASS** | Official repo is training-free and states it directly uses SAM 2.1 weights. It provides checkpoint download, `scripts/main_inference.py`, and benchmark inference support for LaSOT, LaSOT-ext, GOT-10k, UAV123, TrackingNet, OTB100. VOT-toolkit integration being listed as incoming does not invalidate the generic benchmark runner already released. |
| **DAM4SAM (CX024)** | **HG3 PASS** | Official repo is training-free, downloads SAM 2.1 checkpoints, and provides explicit runners/protocols for LaSOT, LaSOT-ext, GOT-10k, DiDi, VOT2020 and VOT2022. The foundation checkpoint is the inference checkpoint required by the method. |
| **MambaLCT (CX040)** | **HG3 PASS** | Official repo provides model and raw-result links. Although README documentation is sparse, the released tree contains `experiments/mambalct` configs, `tracking/test.py`, analysis code, `lib/test/tracker/mambalct.py`, and `lib/test/parameter/mambalct.py`, which deterministically resolves the tracker checkpoint path. This is sufficient official integration for a realistic reproduction attempt. Documentation quality remains a later reproduction-risk note, not an HG3 blocker. |
| **JDTrack (CX046)** | **HG3 PASS** | The official VisTrack umbrella repo links `Models & Raw Results`, contains JDTrack tracker/parameter code and integrated benchmark toolkits. Crucially, `pytracking/parameter/jdtrack/jdtrack_vit.py` explicitly pins `JDTrack/ViT/JDTrack_online_target_fuse.pth.tar`, resolving the earlier filename ambiguity at the code level. External bundle file existence will still be verified during reproduction. |
| **UMDATrack (CX051)** | **HG3 PASS** | Official README links the authors' weights, specifies checkpoint placement under `output/checkpoints/train/UMDATrack`, provides domain configs and concrete evaluation commands including epoch/run-id selection. The shared bundle contains multiple training-stage assets, but the released protocol is sufficient to identify and execute evaluation. Exact final-file pinning remains a reproduction task. |
| **SiamABC (CX064)** | **HG3 FAIL** | Official repo has tracker code, ten committed models, training instructions and a single-video demo. However, its benchmark evaluator `eval_SiamABC.py` imports `eval_data` and `eval_toolkit` trees that are absent from the pinned released tree, and the README does not provide a complete released dependency/integration path restoring that benchmark evaluator. Under the locked HG3 rule, benchmark reproduction is therefore not realistic from the official bundle as released. SiamABC remains mandatory literature/novelty reference material. |

## Supporting code observations

### SAMURAI
- Repository explicitly says no additional training is required and SAM 2.1 weights are used directly.
- Main inference was released for LaSOT, LaSOT-ext, GOT-10k, UAV123, TrackingNet and OTB100.
- The repository provides an initial-bbox demo and generic benchmark input preparation.

### DAM4SAM
- Repository states the method runs without additional training.
- `download_ckpts.sh` obtains the required SAM 2.1 weights.
- `run_on_box_dataset.py` supports LaSOT, LaSOT-ext and GOT-10k, and VOT workspace commands are documented.

### MambaLCT
- Released model/raw-result links exist.
- `tracking/test.py` is a generic dataset runner.
- `experiments/mambalct/` contains 256/384 and GOT-specific configs.
- `lib/test/parameter/mambalct.py` builds the checkpoint path as `checkpoints/train/mambalct/<yaml>/MambaLCT_epXXXX.pth.tar`.

### JDTrack
- Official umbrella repo explicitly lists JDTrack and a shared models/raw-results resource.
- JDTrack tracker and parameter modules exist.
- The ViT parameter file names `JDTrack_online_target_fuse.pth.tar` explicitly.

### UMDATrack
- Official README provides training and evaluation workflows, authors' weight links, placement directory and concrete commands.
- Exact domain model/config/epoch is part of the test command, which is sufficient to remove the Stage-1 ambiguity for HG3.

### SiamABC
- Official models are bundled and single-video inference is documented.
- The benchmark script exists but depends on absent local trees (`eval_data`, `eval_toolkit`).
- The released repository root does not contain those trees at the pinned SiamABC commit.

## Resulting early-gate queue

Before flag reconciliation, 20 families were in the reconciled scientific-audit queue.

After the Manager HG3 resolution:

- **19 families remain HG1/HG2/HG3 PASS** and are eligible to proceed to the later deep-gate audit;
- **SiamABC (CX064) is removed from the active scientific-audit queue due HG3 FAIL**, but remains in the canonical matrix and literature universe as a reference/excluded candidate.

This is **not a shortlist** and no candidate has been ranked.

## Cross-check boundary

To preserve the parallel-control design, Codex must independently re-check these six flags without reading this manager report or the canonical matrix first. Any disagreement must be reconciled against the pinned official repositories before Stage 2 begins.

Until that cross-check is complete:

- HG4/HG5/HG6: **NOT STARTED**
- soft scoring: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
