# HG3 flag recheck — source-derived worker pass

**Date:** 2026-08-24  
**Scope:** HG3 only for the six source-normalization flags.  
**Stop boundary:** HG4/HG5/HG6, soft scoring, shortlist selection, baseline selection, and architecture design are not started.

> **Independence limitation:** this artifact was produced in the same ChatGPT conversation that previously contained Manager-side HG3 conclusions. During this recheck, the prohibited Manager files and canonical matrix were not opened before the report was written, and every decision below was re-derived from the pinned official repositories. However, because prior conversational exposure cannot be erased, this is **not a fully blind independent Codex cross-check in the strict experimental sense**. It should be treated as a second source inspection. The true Manager↔Codex independent reconciliation remains pending until the external Codex worker performs the same check without prior exposure.

## Governing HG3 rule

Under `docs/11_systematic_screening_protocol.md`, HG3 passes only when the official authors/project provide:

1. source code;
2. the pretrained checkpoint(s) actually required by the method;
3. a usable evaluation script/protocol or official integration sufficient to make benchmark reproduction realistic.

For a genuinely training-free method, a nonexistent family-trained checkpoint is not required if the released tracker is defined by code around an officially available pretrained foundation model and those inference weights are available.

`PASS` here means a realistic reproduction attempt is supported by the official release. It does **not** mean successful local reproduction has already occurred.

---

## CX020 — SAMURAI

**Decision: PASS**

- **Source code:** official `yangchris11/samurai@76ba1959` ([R28]) contains the SAMURAI-modified SAM2 implementation plus `scripts/main_inference.py` and `scripts/demo.py`.
- **Checkpoint:** the official README explicitly states SAMURAI is zero-shot/training-free and directly uses SAM 2.1 weights; the release provides the SAM 2.1 checkpoint-download path.
- **Evaluation:** the official release documents inference support for LaSOT, LaSOT-ext, GOT-10k, UAV123, TrackingNet and OTB100. `scripts/main_inference.py` reads the first-frame bbox, runs the tracker and writes sequence bbox predictions.
- **Risk note:** VOT-toolkit integration is separately marked incoming; exact post-processing/submission still needs reproduction-time verification.

**Rationale:** official code + the actual required foundation weights + a released generic benchmark runner make reproduction realistic.

---

## CX024 — DAM4SAM

**Decision: PASS**

- **Source code:** official `jovanavidenovic/DAM4SAM@9c954504` ([R30]) contains the DAM4SAM memory implementation, bbox runners, VOT integration and configs.
- **Checkpoint:** DAM4SAM is training-free on SAM 2.1. `checkpoints/download_ckpts.sh` downloads the official SAM 2.1 tiny/small/base-plus/large weights used by the method.
- **Evaluation:** the README documents `run_on_box_dataset.py` for LaSOT, LaSOT-ext and GOT-10k, plus DiDi/VOT evaluation workflows and VOT2020/VOT2022 workspace commands.
- **Risk note:** bbox initialization is converted to an initial SAM2 mask and must be preserved exactly later.

**Rationale:** all three HG3 components are officially released; no family-trained checkpoint is required by this training-free design.

---

## CX040 — MambaLCT

**Decision: PASS**

- **Source code:** official `GXNU-ZhongLab/MambaLCT@0457044f` ([R36]) contains `experiments/mambalct/`, `tracking/test.py`, `tracking/analysis_results.py`, `lib/test/tracker/mambalct.py`, and `lib/test/parameter/mambalct.py`.
- **Checkpoint:** the README provides Models and Raw Results links. `lib/test/parameter/mambalct.py` deterministically resolves `checkpoints/train/mambalct/<yaml>/MambaLCT_epXXXX.pth.tar`; the tracker implementation loads the `net` state from that path.
- **Evaluation:** `tracking/test.py` is a released dataset runner and the analysis path is present.
- **Risk note:** documentation is sparse and inherited example names remain in some scripts, so reproduction risk is higher than for cleaner releases.

**Rationale:** the official model link + deterministic checkpoint path + configs + tracker + test/analysis chain are sufficient for a realistic reproduction attempt.

---

## CX046 — JDTrack

**Decision: PASS**

- **Source code:** official umbrella repository `hexdjx/VisTrack@f07acc94` ([R42]) explicitly lists JDTrack and contains `pytracking/tracker/jdtrack/`, `pytracking/parameter/jdtrack/`, and `pytracking/run_tracker.py`.
- **Checkpoint:** the official README links the authors' `Models & Raw Results` resource. More importantly, `pytracking/parameter/jdtrack/jdtrack_vit.py` explicitly requests `JDTrack/ViT/JDTrack_online_target_fuse.pth.tar`, resolving the expected family checkpoint filename at code level.
- **Evaluation:** `pytracking/run_tracker.py` defaults to JDTrack/`jdtrack_vit` and runs through the integrated PyTracking dataset/evaluation layer.
- **Risk note:** the external model bundle still needs to be downloaded during actual reproduction to verify that the named file is present and intact.

**Rationale:** official models release + exact code-level checkpoint identity + official evaluator integration satisfy HG3 at the eligibility stage.

---

## CX051 — UMDATrack

**Decision: PASS**

- **Source code:** official `Z-Z188/UMDATrack@5d609bfc` ([R46]) contains the model, configs, training code, `tracking/test.py`, test parameter loader and result-analysis utilities.
- **Checkpoint:** the README provides author weight links, checkpoint placement instructions, and distinguishes foundation/pseudo-label resources from trained evaluation weights. `lib/test/parameter/UMDATrack.py` constructs the checkpoint path from config and epoch.
- **Evaluation:** the README supplies concrete test commands with tracker, config, dataset, run-id and epoch; `tracking/test.py` forwards these into the released evaluation framework.
- **Risk note:** the resource bundle mixes multiple training stages and the parameter code uses a domain-specific `UMDATrack_extreme_prompt_dark_epXXXX.pth.tar` naming pattern; haze/rainy variant mapping must be checked during reproduction.

**Rationale:** at least one concrete official evaluation path is sufficiently specified to make baseline reproduction realistic; variant-level pinning is a later reproduction task.

---

## CX064 — SiamABC

**Decision: FAIL**

- **Source code:** official `wvuvl/SiamABC@b1c94e06` ([R51]) contains tracker/training code, `realtime_test.py`, committed model assets and `eval_SiamABC.py`.
- **Checkpoint:** the README states the SiamABC models are in `assets`; checkpoint availability is not the blocker.
- **Evaluation:** `eval_SiamABC.py` imports local trees `eval_data` and `eval_toolkit.pysot`, but neither tree exists in the pinned repository root. No `.gitmodules` exists at that ref, `requirements.txt` does not restore those local trees, and the README gives no complete official benchmark-evaluator restoration procedure.
- **Blocking issue:** the released benchmark evaluator is incomplete. The single-video demo is not a substitute for a usable benchmark protocol under HG3.

**Rationale:** source and models exist, but official benchmark reproduction is not realistic from the released bundle without reconstructing undocumented missing evaluator dependencies.

---

## Summary

| Candidate | Source-derived HG3 decision |
|---|---|
| SAMURAI | PASS |
| DAM4SAM | PASS |
| MambaLCT | PASS |
| JDTrack | PASS |
| UMDATrack | PASS |
| SiamABC | FAIL |

- **PASS:** 5
- **FAIL:** 1
- **PENDING:** 0

If these source-derived decisions are applied to the **20-family pre-flag scientific-audit queue**, the active queue would contain **19 families**. This is an unranked audit queue, not a shortlist.

## Locked stop state

- **HG3 SOURCE-DERIVED RECHECK: COMPLETE**
- **TRUE MANAGER/CODEX INDEPENDENT RECONCILIATION: PENDING**
- **HG4-HG5-HG6: NOT STARTED**
- **SOFT SCORING: NOT STARTED**
- **PRIMARY SHORTLIST: NONE**
- **MAIN BASELINE: NONE**
- **PROPOSED ARCHITECTURE: NONE**
