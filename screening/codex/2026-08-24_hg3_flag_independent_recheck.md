# Independent HG3 flag recheck

**Date:** 2026-08-24  
**Lane:** Codex/worker independent recheck  
**Scope:** HG3 only for the six source-normalization flags.  
**Stop boundary:** HG4/HG5/HG6, soft scoring, shortlist selection, baseline selection, and architecture design are not started.

## Governing rule

HG3 is evaluated under `docs/11_systematic_screening_protocol.md`: an eligible project must provide official source code, the pretrained checkpoint(s) actually required by the method, and a usable evaluation script/protocol or official integration sufficient to make benchmark reproduction realistic.

For a genuinely training-free tracker, a method-specific trained checkpoint is not required if the released method is defined by source-code changes around an officially available pretrained foundation model and the exact foundation weights used for inference are available.

`PASS` means the official release is sufficient to attempt baseline reproduction realistically. It does **not** mean successful local reproduction has already been demonstrated.

---

## CX020 — SAMURAI

**Decision: PASS**

### Source-code evidence

Official pinned repository: `yangchris11/samurai@76ba1959` ([R28]). The release contains the SAMURAI-modified SAM2 code and benchmark/demo scripts, including `scripts/main_inference.py` and `scripts/demo.py`.

### Checkpoint evidence

The official README explicitly states that SAMURAI is a **zero-shot / training-free** method and directly uses **SAM 2.1 weights**. The repository provides `checkpoints/download_ckpts.sh` to obtain the SAM 2.1 checkpoints. Therefore, SAM 2.1 is the pretrained checkpoint actually required by the released method; a separate SAMURAI-trained checkpoint is not part of the method design.

### Evaluation evidence

The official README records released inference support for LaSOT, LaSOT-ext, GOT-10k, UAV123, TrackingNet, and OTB100. `scripts/main_inference.py` is a real LaSOT dataset runner: it reads the first-frame ground-truth box as the prompt, builds the SAMURAI predictor from the SAM 2.1 checkpoint/config, propagates through the sequence, and writes per-sequence bbox predictions.

The README separately marks VOT-toolkit integration as incoming. That missing toolkit integration does not remove the already released generic bbox benchmark runner/output path.

### Blocking issue

No HG3 blocker. Full local reproduction still requires verifying the exact environment and benchmark post-processing/submission path.

### Rationale

Official code + required inference weights + released generic benchmark runner are sufficient for a realistic reproduction attempt. HG3 therefore passes.

---

## CX024 — DAM4SAM

**Decision: PASS**

### Source-code evidence

Official pinned repository: `jovanavidenovic/DAM4SAM@9c954504` ([R30]). The repository contains the DAM4SAM memory-management implementation, bbox dataset runners, VOT integration, configs, and checkpoint downloader.

### Checkpoint evidence

DAM4SAM is explicitly presented as a **training-free** modification of SAM2.1. `checkpoints/download_ckpts.sh` downloads the official SAM 2.1 tiny/small/base-plus/large checkpoints from Meta's public checkpoint host. Those are the pretrained weights used by the method; no DAM4SAM-trained tracker checkpoint is required by the released design.

### Evaluation evidence

The official README documents:

- `run_on_box_dataset.py` for LaSOT, LaSOT-ext, and GOT-10k;
- DiDi evaluation plus VOT-toolkit analysis/report commands;
- VOT2020 and VOT2022 workspace initialization and tracker integration;
- bbox initialization converted to the initial SAM2 mask through the released pipeline.

### Blocking issue

No HG3 blocker. The bbox-to-mask initialization behavior must later be preserved exactly during reproduction.

### Rationale

The release contains official code, the actual required foundation checkpoints, and explicit benchmark-running/evaluation protocols. HG3 passes.

---

## CX040 — MambaLCT

**Decision: PASS**

### Source-code evidence

Official pinned repository: `GXNU-ZhongLab/MambaLCT@0457044f` ([R36]). The release includes:

- `experiments/mambalct/` with 256/384 and GOT-specific YAML configs;
- `tracking/test.py` generic dataset runner;
- `tracking/analysis_results.py` analysis entry point;
- `lib/test/tracker/mambalct.py` tracker implementation;
- `lib/test/parameter/mambalct.py` test configuration/checkpoint resolver.

### Checkpoint evidence

The official README provides a **Models** link and raw-results link. `lib/test/parameter/mambalct.py` deterministically constructs the expected tracker checkpoint path as:

`checkpoints/train/mambalct/<yaml_name>/MambaLCT_epXXXX.pth.tar`

and `lib/test/tracker/mambalct.py` loads the `net` state dictionary from that path.

### Evaluation evidence

`tracking/test.py` invokes the released dataset/evaluation framework and supports the standard tracking dataset path. `tracking/analysis_results.py` connects results to the released analysis module. The README is sparse, but the official code tree provides the config + checkpoint-resolution + tracker + test-runner chain needed for a realistic reproduction attempt.

### Blocking issue

Documentation is incomplete and some example comments retain inherited tracker names. This increases reproduction risk but does not make the official evaluation integration absent.

### Rationale

The official model link plus deterministic checkpoint path, configs, tracker implementation, dataset runner, and analysis code jointly satisfy HG3. PASS does not imply the code has already been run locally.

---

## CX046 — JDTrack

**Decision: PASS**

### Source-code evidence

Official pinned umbrella repository: `hexdjx/VisTrack@f07acc94` ([R42]). The README explicitly lists JDTrack and official `Models & Raw Results` links. The pinned tree contains:

- `pytracking/tracker/jdtrack/jdtrack.py`;
- `pytracking/parameter/jdtrack/`;
- `pytracking/run_tracker.py`;
- integrated `got10k` and evaluation tooling described by the authors.

### Checkpoint evidence

The earlier README-level ambiguity is materially reduced by the released parameter code. `pytracking/parameter/jdtrack/jdtrack_vit.py` explicitly requests:

`JDTrack/ViT/JDTrack_online_target_fuse.pth.tar`

through `NetWithBackbone(...)`.

The official repository also links the authors' shared **Models & Raw Results** resource. Thus the released code identifies the exact JDTrack checkpoint filename/path expected by the evaluator, rather than leaving the family checkpoint unnamed.

### Evaluation evidence

`pytracking/run_tracker.py` defaults to `tracker_name='jdtrack'` and `tracker_param='jdtrack_vit'`, resolves datasets through the integrated PyTracking evaluation layer, and runs the tracker through `run_dataset(...)`.

### Blocking issue

The external models bundle itself must still be checked/downloaded during actual reproduction to verify that the named checkpoint is present and intact. This is a reproduction-time verification risk, not enough by itself to negate the official authors' models release plus exact code-level filename mapping.

### Rationale

Official source, official models resource, explicit expected checkpoint filename, and integrated benchmark runner make reproduction realistic. HG3 passes.

---

## CX051 — UMDATrack

**Decision: PASS**

### Source-code evidence

Official pinned repository: `Z-Z188/UMDATrack@5d609bfc` ([R46]). The release contains the UMDATrack model, configs, training code, test runner, test parameter loader, and analysis utilities.

### Checkpoint evidence

The official README provides authors' pretrained/weight links and explicitly instructs users to place evaluation weights under the UMDATrack checkpoint tree. It also distinguishes the pretrained foundation/pseudo-label resources from the train/evaluation weights.

`lib/test/parameter/UMDATrack.py` constructs the test checkpoint path from the save directory, YAML config, and requested epoch. The current parameter file contains a method-specific filename pattern ending in `UMDATrack_extreme_prompt_dark_epXXXX.pth.tar`; this should be pinned and checked during reproduction.

### Evaluation evidence

The README supplies concrete evaluation commands, including tracker name, config, dataset, run-id, epoch, and save directory. `tracking/test.py` forwards the epoch/config/run-id into the released evaluation framework; `tracking/analysis_results.py` is present for result analysis.

### Blocking issue

The official resource bundle mixes foundation, pseudo-label, stage-1, and stage-2 assets, and the pinned parameter file has a domain-specific checkpoint naming pattern that warrants careful reproduction-time validation for haze/rainy variants. However, at least the released dark-domain evaluation path is concretely specified by the official repository.

### Rationale

Official code, authors' model links, checkpoint placement/naming logic, configs, and concrete evaluation commands are sufficient to attempt baseline reproduction realistically. HG3 passes, with variant-level pinning deferred to reproduction.

---

## CX064 — SiamABC

**Decision: FAIL**

### Source-code evidence

Official pinned repository: `wvuvl/SiamABC@b1c94e06` ([R51]). The repository includes SiamABC code, training code, `realtime_test.py`, committed models under `assets`, and `eval_SiamABC.py`.

### Checkpoint evidence

The official README states that SiamABC models are available in the `assets` folder, and the pinned tree contains those model assets. Checkpoint availability itself is therefore not the blocker.

### Evaluation evidence

The benchmark evaluator `eval_SiamABC.py` imports:

- `eval_data...`
- `eval_toolkit.pysot...`

but neither `eval_data` nor `eval_toolkit` exists in the pinned repository root. There is no `.gitmodules` file at the pinned ref, and `requirements.txt` does not install packages or repositories that restore those local import trees. The README documents single-video evaluation and training, but does not provide an official benchmark-evaluator restoration/integration procedure.

### Blocking issue

The released benchmark evaluator is incomplete from the official pinned release because required local dependency trees are absent. A single-video demo is not a substitute for a usable benchmark evaluation protocol under HG3.

### Rationale

Source code and tracker models are present, but official benchmark reproduction is not realistic from the released bundle without reconstructing missing evaluator dependencies from outside the documented release. HG3 therefore fails.

---

## Summary

| Candidate | Independent HG3 decision |
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

Applying these independent decisions to the **20-family pre-flag scientific-audit queue** yields:

- **ACTIVE SCIENTIFIC-AUDIT QUEUE SIZE: 19 families**

This remains an unranked audit queue, not a shortlist.

## Locked stop state

- **HG3 INDEPENDENT RECHECK: COMPLETE**
- **MANAGER/CODEX RECONCILIATION: PENDING**
- **HG4-HG5-HG6: NOT STARTED**
- **SOFT SCORING: NOT STARTED**
- **PRIMARY SHORTLIST: NONE**
- **MAIN BASELINE: NONE**
- **PROPOSED ARCHITECTURE: NONE**
