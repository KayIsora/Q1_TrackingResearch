# Reconciled audit-queue source normalization report

Date: **2026-08-24**

Lane: **Codex worker**

Stage: **source normalization only**

## 1. Scope and stopping boundary

This report normalizes the primary publication and official reproducibility sources for the **19 Codex-origin families** in the reconciled scientific-audit queue. The reconciled universe remains 128 families, and the full scientific-audit queue remains 20 families after the Manager's MPT addition. The queue is **not a shortlist**.

Only publisher/proceedings pages, DOI records linked to the official article, official repositories, and assets linked by those repositories were used for factual registration. No new search-engine query was run. Repository observations are RESOURCE AVAILABILITY FACT / CODE FACT; no reproduction run was performed.

This task did not modify the canonical candidate matrix or any Stage-1 gate. It did not begin HG4, HG5, HG6, soft scoring, shortlist selection, baseline selection, or architecture design.

## 2. Completion summary

| Required item | Result |
|---|---:|
| Codex-origin families processed | **19 / 19** |
| Primary publication sources verified | **19 / 19** |
| Official repository sources verified | **19 / 19 families; 18 unique repositories** |
| Explicit family-trained tracker artifact available | **15 families** |
| Training-free family; SAM 2.1 base weights available but no family-trained checkpoint exists | **2 families: SAMURAI, DAM4SAM** |
| Exact final/family checkpoint identity ambiguous in an official mixed/shared bundle | **2 families: JDTrack, UMDATrack** |
| Usable documented evaluation workflow verified | **16 families** |
| Evaluation support incomplete or not usable from the inspected official repository alone | **3 families: SAMURAI, MambaLCT, SiamABC** |
| HG3 reconciliation flags raised for Manager review | **6** |

The counts above describe source state, not benchmark quality, hardware feasibility, novelty, rank, or preference.

## 3. Family-by-family normalized source state

Legend: **yes** means availability was verified from the official repository; it does not mean successful reproduction. **Base only** means that the method is training-free and downloads SAM 2.1 foundation weights rather than a family-trained tracker checkpoint. **Ambiguous** means the official repository points to assets but does not identify the exact family/final checkpoint file sufficiently.

| Family | Publication | Official repository and audited ref | Code | Tracker checkpoint | Evaluator / protocol | Normalized limit or anomaly |
|---|---|---|---|---|---|---|
| SpikeTrack | [R18](../../references/references.md#r18) | [R19](../../references/references.md#r19), `faicaiwawa/SpikeTrack`, `main@1537db51…` | yes | yes; six tracker models | yes | SDTV3 backbone is separate; GitHub/Hugging Face owner spellings differ. |
| UETrack | [R20](../../references/references.md#r20) | [R21](../../references/references.md#r21), `kangben258/UETrack`, `main@fd13b0ea…` | yes | yes; Base/Small/Tiny | yes; RGB and multimodal | Backbone and teacher assets are separate; multimodal training/results must not be collapsed into RGB-only evidence. |
| UTPTrack | [R22](../../references/references.md#r22) | [R23](../../references/references.md#r23), `EIT-NLP/UTPTrack`, `main@84e0f497…` | yes | yes; O/S at 224/384 | yes | Monorepo contains OSTrack-derived O and SUTrack-derived S implementations; model/config pair must be pinned. |
| FARTrack | [R11](../../references/references.md#r11) | [R12](../../references/references.md#r12), `MIV-XJTU/FARTrack`, `main@5d3e4b90…` | yes | yes; FARTrack/Distill/Sparse resources | yes | R11/R12 were reused, not duplicated; MAE backbone is separate; published speed hardware is not Jetson Nano. |
| GOT-Edit | [R24](../../references/references.md#r24) | [R25](../../references/references.md#r25), `chenshihfang/GOT`, `main@b2ee0b97…` | yes | yes; official model link | yes; family script | Shared mutable repository; RGB-derived geometry still requires a separate geometry backbone. |
| GOT-JEPA | [R26](../../references/references.md#r26) | [R25](../../references/references.md#r25), relevant historical commit `84e93243…` | yes | yes; official model link | yes; family script | The README pins a historical commit; current default HEAD alone is insufficient provenance. |
| SAMURAI | [R27](../../references/references.md#r27) | [R28](../../references/references.md#r28), `yangchris11/samurai`, `master@76ba1959…` | yes | **base only** | partial; VOT integration marked incoming | Training-free method; SAM 2.1 weights are not a trained SAMURAI checkpoint; live/streaming input is unsupported in the inspected README. **HG3 RECONCILIATION FLAG.** |
| DAM4SAM | [R29](../../references/references.md#r29) | [R30](../../references/references.md#r30), `jovanavidenovic/DAM4SAM`, `master@9c954504…` | yes | **base only** | yes | Training-free SAM 2.1 memory modification; bbox runners obtain initial masks from the ground-truth box. **HG3 RECONCILIATION FLAG.** |
| SSTrack-AAAI | [R31](../../references/references.md#r31) | [R32](../../references/references.md#r32), `GXNU-ZhongLab/SSTrack`, `main@5dcf04cc…` | yes | yes | yes | DropMAE backbone pretraining is distinct from the tracker model; RTX 2080 Ti speed is not Nano evidence. |
| MCITrack | [R33](../../references/references.md#r33) | [R34](../../references/references.md#r34), `kangben258/MCITrack`, `main@e667193e…` | yes | yes | yes | Official README separates tracker models from backbone-pretraining weights. |
| MambaLCT | [R35](../../references/references.md#r35) | [R36](../../references/references.md#r36), `GXNU-ZhongLab/MambaLCT`, `main@0457044f…` | yes | yes; model link | **incomplete** | Test/analysis code exists, but the README lacks installation, checkpoint-placement, invocation, and end-to-end protocol. **HG3 RECONCILIATION FLAG.** |
| SUTrack | [R37](../../references/references.md#r37) | [R38](../../references/references.md#r38), `chenxin-dlut/SUTrack`, `main@d65052d1…` | yes | yes; five explicit tracker files | yes; RGB and multimodal | Unified multimodal training is distinct from RGB inference; raw results are pending; AGX speed is not Nano speed. |
| AsymTrack | [R39](../../references/references.md#r39) | [R40](../../references/references.md#r40), `jiawen-zhu/AsymTrack`, `main@a7b05e0c…` | yes | yes; official model folder | yes | Backbone assets are separate; model-folder availability is not reproduction. |
| JDTrack | [R41](../../references/references.md#r41) | [R42](../../references/references.md#r42), `hexdjx/VisTrack`, `master@f07acc94…` | yes | **ambiguous** | yes; integrated generic evaluator | Multi-method umbrella repository; the shared Drive folder is not mapped to a JDTrack checkpoint filename in the README. **HG3 RECONCILIATION FLAG.** |
| SPMTrack | [R43](../../references/references.md#r43) | [R44](../../references/references.md#r44), `WenRuiCai/SPMTrack`, `main@c581fe27…` | yes | **SPMTrack-B yes; L/G not verified** | yes | Repository explicitly marks release of all variants as pending. |
| UMDATrack | [R45](../../references/references.md#r45) | [R46](../../references/references.md#r46), `Z-Z188/UMDATrack`, `main@5d609bfc…` | yes | **ambiguous** | yes; domain-specific workflows | Bundle mixes pretraining, pseudo-label, stage-1 and stage-2 assets without naming the final evaluation file; offline adaptation cost is distinct from RGB inference. **HG3 RECONCILIATION FLAG.** |
| UncTrack | [R47](../../references/references.md#r47) | [R48](../../references/references.md#r48), `ManOfStory/UncTrack`, `main@61bd4be6…` | yes | yes | yes | `UncTrack+AR` additionally requires Alpha-Refine and VOT toolkit integration. |
| HiT–DyHiT | [R49](../../references/references.md#r49) | [R50](../../references/references.md#r50), `kangben258/HiT`, `main@ca806400…` | yes | yes; mixed variant/result folder | yes | Exact model/threshold must be pinned; AGX/NX evidence is not Jetson Nano evidence. |
| SiamABC | [R10](../../references/references.md#r10) | [R51](../../references/references.md#r51), `wvuvl/SiamABC`, `master@b1c94e06…` | yes | yes; ten committed model files | **not verified usable** | Separate `main@ba22faee…` is unrelated AEVT. Benchmark script imports absent `eval_data` and `eval_toolkit` trees. **HG3 RECONCILIATION FLAG.** |

## 4. HG3 reconciliation flags — Manager decision required

No candidate gate was changed. The following official-source findings may conflict with an unconditional Stage-1 HG3 PASS and are therefore escalated exactly as reconciliation flags:

1. **SAMURAI:** the repository downloads SAM 2.1 base checkpoints, not a SAMURAI-trained tracker checkpoint; VOT-toolkit integration is marked incoming.
2. **DAM4SAM:** the repository downloads SAM 2.1 base checkpoints; DAM4SAM is training-free, so the Manager must decide how HG3's checkpoint clause applies.
3. **MambaLCT:** model and evaluator-related code exist, but a usable documented end-to-end evaluation protocol was not verified.
4. **JDTrack:** the umbrella VisTrack repository contains JDTrack code and evaluator infrastructure, but the shared external folder is not mapped to an identifiable JDTrack checkpoint filename in the README.
5. **UMDATrack:** the official bundle contains several resource classes, but the README does not identify the exact final evaluation checkpoint file.
6. **SiamABC:** tracker models and a single-video demo exist, but the benchmark evaluator imports two absent local trees; no submodule or requirement supplies them.

These flags are not automatic FAIL decisions. They preserve the source discrepancy for Manager reconciliation under the locked protocol.

## 5. Repository anomalies and normalization decisions

- **GOT shared provenance:** GOT-Edit and GOT-JEPA are separate paper families in one repository. One repository source ID is used, with both the current GOT-Edit commit and the historical GOT-JEPA-relevant commit recorded.
- **SiamABC branch provenance:** current default `master` contains SiamABC; a separate `main` branch contains unrelated AEVT material. The SiamABC commit is pinned explicitly.
- **Umbrella/mixed asset bundles:** JDTrack, UMDATrack and HiT–DyHiT require variant/file-level pinning before reproduction.
- **Training-free checkpoint semantics:** SAMURAI and DAM4SAM use SAM 2.1 foundation weights rather than family-trained checkpoints.
- **Partial release:** SPMTrack-B is released; SPMTrack-L/G checkpoints were not verified and remain marked pending by the repository.
- **Backbone versus tracker checkpoint:** SpikeTrack, UETrack, UTPTrack, FARTrack, SSTrack-AAAI, MCITrack, SUTrack and AsymTrack expose separate backbone/pretraining and tracker-model resources; these were not conflated.
- **Runtime evidence boundary:** desktop GPU, CPU, Jetson AGX or Jetson NX figures were not converted into Jetson Nano claims.

## 6. Reference registration

- Existing source IDs reused and normalized: **R10** (SiamABC publication), **R11** (FARTrack publication), **R12** (FARTrack repository).
- Existing Manager-owned IDs **R13–R17** were not renumbered or repurposed.
- New source IDs added: **R18–R51** (34 sources).
- GOT-Edit and GOT-JEPA share repository source **R25**; no duplicate repository reference was created.
- FARTrack did not receive duplicate publication or repository IDs.

## 7. Files modified

1. `references/references.md`
2. `references/source_manifest.csv`
3. `screening/codex/2026-08-24_audit_queue_source_normalization_report.md`

No other project file is part of this source-normalization change. The exact commit SHA is reported in the final worker handoff after commit creation; a commit cannot contain its own resulting SHA.

## 8. Locked final state

- SOURCE NORMALIZATION: **COMPLETE**
- CANONICAL MATRIX: **NOT MODIFIED**
- HG4-HG5-HG6: **NOT STARTED**
- SOFT SCORING: **NOT STARTED**
- PRIMARY SHORTLIST: **NONE**
- MAIN BASELINE: **NONE**
- PROPOSED ARCHITECTURE: **NONE**
