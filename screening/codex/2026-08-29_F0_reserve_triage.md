# F0 — independent lean reserve triage

**Date:** 2026-08-29
**Lane:** Codex worker — independent lean reserve-triage lane
**Status:** `F0_COMPLETE_DESK_ONLY`
**Next gate:** `F1_MANAGER_CODEX_RECONCILIATION_PENDING`

## 1. Boundary and blindness declaration

This report performs the locked F0 desk triage for exactly CX009, CX010, CX024, CX037, and CX038. Candidate order follows the canonical reserve queue and is not a ranking.

- The Manager provisional reserve-triage artifact was not read, searched, grepped, diffed, or inspected through history or patch content.
- Blindness declaration: **PRESERVED**.
- Only the required policy, protocol, canonical matrix, allowed Manager contracts, Stage-3 reconciliations/formulations, and existing Stage-2 audits were used.
- Existing evidence was sufficient to assign the F0 states. No official repository received a new broad audit.
- No tracker or model was run or instantiated; no checkpoint or dataset was downloaded; no experiment, novelty search, score, ranking, shortlist, baseline selection, or architecture work was performed.
- `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` means desk-ready for F1 consideration only. It does not authorize F2 execution and is not `GAP_READY` or HG6 `PASS`.

The governing limits and three allowed F0 states are in `screening/manager/2026-08-29_post_spiketrack_lean_execution_plan.md:44-67,73-106`. The reserve questions are inherited from `screening/manager/2026-08-28_post_spiketrack_reserve_queue.csv:1-6`.

## 2. Canonical CX007 matrix synchronization

The CX007 row was synchronized mechanically under `screening/manager/2026-08-28_spiketrack_diag_fail_matrix_sync_contract.md` and the accepted Stage-4D result in `screening/reconciliation/2026-08-28_stage4C2_final_diagnostic_reconciliation.md:29-53,114-134`.

- `hg1_publication` through `hg6_novelty`: unchanged at `PASS`;
- all S1-S7 fields and `total_score_100`: blank;
- `decision_state`: `EXCLUDED_DIAGNOSTIC_CRITERION_D_FAIL_REFERENCE_ONLY`;
- evidence note records A/B/C locked passes, frozen one-shot D failure, AUROC `0.48153585544889893 < 0.65`, predictor Brier `0.2575449361739645`, constant Brier `0.24996241633654945`, no soft scoring, and reference/null-result-only status;
- `last_verified`: `2026-08-28`.

Canonical CX007 sync: **PASS**.

## 3. F0 disposition summary

| Candidate | Single missing-evidence question | Cheapest inference-only control | F2-cap estimate | F0 state |
|---|---|---|---|---|
| CX009 UETrack | Does a residual final-model RGB failure interact causally with frame-dependent TP-MoE expert utility? | Fixed predeclared expert-output mask versus full TP-MoE | Unknown; resource/slice blockers remain | `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE` |
| CX010 UTPTrack | Does static-guided removed-token identity cause error rather than a different keep ratio? | Same-count GT-target-token rescue oracle | Strong arithmetic fit | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` |
| CX024 DAM4SAM | Does DRM admission prevent a residual annotated distractor failure, and what DAM-only cost does that impose? | Same-host `DRM_NO_WRITE` | Unknown; data/resource/smoke blockers remain | `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE` |
| CX037 SSTrack-AAAI | Does independently verified historical-template validity causally affect final error and CE/query behavior? | Same-count invalid-history-slot neutralization | Arithmetic fit | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` |
| CX038 MCITrack | Does carried contextual state have condition-specific benefit or harm apart from five-template cost? | All previous carried states zeroed with current work/templates retained | Arithmetic fit | `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC` |

These states neither select nor prioritize candidates. F1 may authorize at most two later probes and may authorize none.

## 4. Candidate triage

### CX009 — UETrack

**Concise evidence summary**

- **Pinned source/config:** `kangben258/UETrack@fd13b0eaf16d51536008295f3b27807c69eaad50`, `experiments/uetrack/uetrack_base.yaml`, UETrack-B / `fastitpnt_layer6`, eight experts, TP-MoE in final-stage block 5, 112-square template and 224-square search (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:109-117`).
- **Checkpoint/evaluator:** canonical status is available, but the authorized evidence does not identify an exact tracker-checkpoint filename/hash or a sealed evaluator invocation. The normal builder also has an unresolved empty `PRETRAIN_TYPE` bootstrap path (`screening/candidate_screening_matrix.csv:1,3`; `screening/codex/2026-08-24_stage2_batchA_code_audit.md:335-360`). These facts remain **UNKNOWN**, not optimistic passes.
- **Compute/state site:** TP-MoE pads 247 tokens to 248, creates dense 248-by-248 routing, and executes all eight experts on every frame. The template pixels and zero-text token persist, while template features are recomputed; no online template bank grows (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:119-130`; `screening/codex/2026-08-24_stage2_batchA_code_audit.md:305-310`).
- **Missing evidence:** final UETrack-B has no established residual generic-RGB failure. Blur, occlusion, distraction, and deformation motivate TAD training and cannot be inverted into a released-model weakness (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:132-151`).
- **Data selection:** not yet validly selectable. A source-selected generic challenge slice would not by itself establish a candidate-specific UETrack failure. No new large dataset is intrinsically required, but the exact existing source/GT-only failure/control slice is unknown.
- **State-matched fork:** frame-local branching is structurally feasible from the same box/crop, cached template pixels, and cached text token. A control prediction must not be committed; multi-frame intervention would require a new common-prefix fork.
- **Budget/resource:** at most 1,500 frames with one control means no more than 3,000 model calls, but no trustworthy synchronized latency, clean startup, or peak-resource bound exists. F2 fit is unknown.
- **Collision/deployment:** UETrack already owns TP-MoE and compares gated MoE. Generic expert gating/pruning, resident cleanup, duplicated-input cleanup, duplicate decoding, template caching, export, or quantization cannot constitute the scientific result. HG4/HG5 are canonically `PASS`, but no Nano engine, parity, latency, memory, power, or thermal result exists (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:161-182`; `screening/codex/2026-08-24_stage2_batchA_code_audit.md:351-372`).

**Proposed minimum probe after the hold is lifted:** on a source/GT-predeclared final-model challenge/control slice, replay each frame from the identical baseline prefix and compare full TP-MoE with one fixed, predeclared expert output masked after expert execution and combine weights renormalized. Log pre-execution routing/expert-disagreement summaries and localization delta. Do not remove CLIP/task residents, duplicated RGB construction, duplicate decoding, or template re-encoding in the scientific branch.

**Exact falsification rule:** reject the current gap if no released-model residual RGB failure slice is established; or expert disagreement/routing does not predict bypass sensitivity; or bypass effects do not differ between challenge/error and stable/control conditions; or the apparent result is explained only by ordinary cleanup. The F1 protocol must freeze the numeric materiality threshold before any outcome is viewed.

**F0 state:** `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`.

### CX010 — UTPTrack

**Concise evidence summary**

- **Pinned source/checkpoint/config/evaluator:** `EIT-NLP/UTPTrack@84e0f49711254a44f5308faaa9a2405db1964dd7`; `UTPTrack-O/experiments/ostrackcmp/ceatetta_256_r7_all.yaml`; official Hugging Face snapshot `4372a928e4bf58615ecb217fe5010d2e3212e627`, `UTPTrack-O-224/OSTrackCMP_ep0300.pth.tar`, SHA-256 `E4EE630CD0E88E41CDBC55BD727C16CA5A4BE3756ADED65F2506B8F670ED0FEF`; `ostrackcmp` parameter/tracker adapter. Strict loading and an exact released forward succeeded (`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:548-570`). The precise evaluator CLI/dataset invocation remains for F1 sealing.
- **Compute/state site:** search CE is configured at blocks 3/6/9; DTE/STE at 4/7/10. Attention executes before pruning. The 0.7 retained counts are fixed while identities depend on content. State is the current box/frame, initial static template, confidence-updated dynamic template, and static foreground mask (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:196-205`; `screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:572-587`).
- **Missing evidence:** no final-model robustness failure is yet causally tied to static-guided removed/retained token identity (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:207-226`).
- **Data selection:** conditionally feasible without broad outcome mining. Freeze source/GT-defined low static-to-current appearance-agreement intervals and matched stable controls; tracker error must not select or expand the slice. No training or new large dataset is required.
- **State-matched fork:** feasible by snapshotting the current box, frame ID, static template, dynamic template, static mask/annotation, and current search crop. Counterfactual state is not committed.
- **Budget:** recorded MX250 model-only median and maximum were 174.167 ms and 318.647 ms. For 1,500 frames with one control, arithmetic neural time is about 0.145 or 0.266 model-hours respectively. Evaluator, replay, crop, and hook overhead are excluded, but substantial headroom remains below six hours (`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:589-607`).
- **Collision/deployment:** UTPTrack already owns unified physical search/static/dynamic pruning and restoration. Another keep ratio, generic adaptive pruning, template caching, TopK replacement, export work, or quantization is insufficient. Fixed-shape ONNX retained the pruning/restoration graph with ORT parity, but TensorRT, reduced precision, controller integration, and all Nano measurements remain unknown (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:236-256`; `screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:616-642`).

**Proposed minimum probe:** from each identical pre-frame state, compare the released path with one same-cardinality search-token identity oracle. At every search-CE site, retain any removed patch that overlaps the GT target and evict the lowest-ranked retained non-target patch, preserving the exact 0.7 count, DTE/STE behavior, checkpoint, templates, and head. This tests removed/retained identity and is not another keep-ratio sweep.

**Exact falsification rule:** reject unless the frozen low-agreement condition both reduces GT target-token recall and worsens localization relative to matched controls, and the same-count identity-rescue branch improves localization preferentially in that condition. A condition-independent effect, latency-only effect, or effect obtainable only by changing the keep count is negative for this gap.

**F0 state:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.

### CX024 — DAM4SAM

**Concise evidence summary**

- **Pinned source/checkpoint/config/evaluator:** `jovanavidenovic/DAM4SAM@9c954504b39ebca4c412f207be0787c26bfac85a`; default `DAM4SAMTracker(tracker_name="sam21pp-L")`; `sam2/sam21pp_hiera_l.yaml`; external `checkpoints/sam2.1_hiera_large.pt`. The checkpoint hash/load is not sealed. `run_on_box_dataset.py`, direct-box initialization, and VOT/DiDi mask initialization do not yet form one exact interchangeable evaluation contract (`screening/codex/2026-08-25_stage2_batchB_code_audit.md:307-319,380-388`).
- **Compute/state site:** Hiera-L image encoding, memory attention, decoding, and memory encoding are host work. DAM-specific work is three-mask handling, quality/size/cooldown gates, CPU connected components/box IoU, and conditional promotion into DRM. Active attention is bounded, while retained dictionaries and `object_sizes` can grow (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:348-362`).
- **Missing evidence:** no residual final-DAM distractor failure or same-host split of DAM incremental cost versus host cost is established (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:364-386`).
- **Data selection:** not yet validly selectable. DiDi or another annotated distractor source is suggested, but exact IDs, annotation source, initialization contract, and verified local availability are unknown. Any future IDs must be selected from annotations/source metadata before outcomes.
- **State-matched fork:** plausible but unverified. Two official tracker instances should replay lockstep from identical initialization and demonstrate exact prefix output/state parity before one branch suppresses a DRM write.
- **Budget:** with 1,500 frames and one control, the 3,000 branch-frame upper envelope requires below 7.2 seconds per branch-frame before overhead. No Hiera-L/RTX-3060 latency or memory bound exists, so six-hour fit is unknown.
- **Collision/deployment:** distractor-aware mask introspection, gates, DRM promotion, and RAM sampling already define DAM4SAM; SAMURAI constrains adjacent reliable-memory ideas. Host substitution, streaming wrappers, memory caps, export, and compression are not the scientific result. The lighter-host path is publication-level only; runnable EfficientTAM/EdgeTAM integration and Nano evidence are absent in the pinned release (`screening/codex/2026-08-25_stage3_gap_G1_code_formulation.md:397-418`).

**Proposed minimum probe after the hold is lifted:** on frozen annotated target-distractor events, compare the released path with a same-host `DRM_NO_WRITE` branch. Keep Hiera-L, RAM, three-mask generation, selected host mask, fixed gates, and logging unchanged; make only `add_to_drm` a logged no-op. Separately time host components and DAM inspection/consolidation work.

**Exact falsification rule:** reject if, over every frozen annotated event horizon, DRM-on prevents no additional failure or identity switch and yields no overlap improvement over `DRM_NO_WRITE`; or if the observed failure is unchanged because host segmentation is limiting. Additional cost without a condition-specific outcome benefit is negative.

**F0 state:** `TRIAGE_HOLD_MISSING_DATA_OR_RESOURCE`.

### CX037 — SSTrack-AAAI

**Concise evidence summary**

- **Pinned source/checkpoint/config/evaluator:** `GXNU-ZhongLab/SSTrack@5dcf04ccb04f10ca4d78035373c8b8684bb8c4f5`; `experiments/sstrack/dropmae_256_150ep.yaml`; official `Models/Full_Data/SSTrack_256_ep0150.pth.tar`, Drive ID `1_lUg8saCyHQk83ni5CANoDzAe3yt95_y`, SHA-256 `4C39C1F695F3F02521E90A3B169796399AF78F5E43CF649A614ADDACA0C4006D`. The full checkpoint strict-loaded; the canonical evaluator is available, but its exact CLI/dataset invocation remains unknown for F1 sealing (`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:60-86`; `screening/candidate_screening_matrix.csv:1,10`).
- **Compute/state site:** every selected raw template is embedded each frame; mature execution can use four active templates. CE pays the scheduled block attention and then reduces search tokens 256 to 180 to 126 to 89 before scatter restoration. State is the current box/controller, raw history, selected identities, and one persistent query token (`screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md:47-59`).
- **Missing evidence:** unconditional self-predicted history admission is a reliability lead, not proof. Final SSTrack has no established failure causally tied to historical-template validity, CE, or query behavior (`screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md:61-86`).
- **Data selection:** conditionally feasible using source/GT-only stable/redundant-history intervals and occlusion/reappearance or appearance-change intervals. Exact already-available sequences and validity rules must be frozen before tracker outputs. No training or new large dataset is required.
- **State-matched fork:** structurally feasible by snapshotting the current box, frame index, raw history/controller, selected source identities, and persistent query. Full-controller clone/replay parity must pass before scientific outcomes.
- **Budget:** the four-template CPU model-only median was 1,423.985 ms. At 1,500 frames with one control, arithmetic model time is about 1.19 hours, excluding controller, replay, crop, and instrumentation overhead (`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:88-121`).
- **Collision/deployment:** SSTrack already owns its self-supervised formulation, CE, persistent query, and multi-template selection. FARTrack constrains template-validity/physical-compute claims and UTPTrack constrains physical token pruning. Caching, history bounding, fixed keep-rate tuning, TopK replacement, export repair, and quantization are engineering. Nano plausibility requires bounded controller and TensorRT parity; no Nano measurement exists (`screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md:99-120`; `screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:123-147`).

**Proposed minimum probe:** from the same pre-frame state, keep four template slots and compare the released selected history with one same-count invalid-slot neutralization: replace one independently GT-invalid selected history crop with the initial template while keeping CE count, query input, checkpoint, search crop, and head fixed. Log source validity, template contribution, CE retained/removed identities, query change, and localization.

**Exact falsification rule:** reject if independently verified source validity/redundancy does not interact with marginal template contribution; invalid-slot neutralization has a condition-independent effect or affects only latency; CE/query behavior is insensitive to valid versus invalid history; or the remaining result is only caching or history capping.

**F0 state:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.

### CX038 — MCITrack

**Concise evidence summary**

- **Pinned source/checkpoint/config/evaluator:** `kangben258/MCITrack@e667193eaec4c8a73d4bdd856a662aecdb844b43`; `experiments/mcitrack/mcitrack_b224.yaml`; official `mcitrack_b224/MCITRACK_ep0300.pth.tar`, Drive ID `1F179L7zP2v8dj8at6c-agXo1fQjQEFt8`, SHA-256 `6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9`. The full checkpoint strict-loaded after a construction-only Fast-iTPN bootstrap bypass; the exact bootstrap/evaluator/data contract remains for F1 sealing (`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:149-173`; `screening/candidate_screening_matrix.csv:1,11`).
- **Compute/state site:** each frame re-encodes five templates and executes four Mamba blocks, four Injectors, six Extractors, and all configured backbone slices. Four FP32 carried states total 49 MiB, are replaced each frame, and reset after low confidence; the raw template bank is bounded at 200-500 crops (`screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md:135-146`).
- **Missing evidence:** confidence reset and template admission are existing safeguards, not residual failures. No final B224 disruption condition or condition-specific carried-state contribution is established (`screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md:148-175`).
- **Data selection:** conditionally feasible using only source/GT-defined stable intervals versus occlusion/reappearance or abrupt motion/appearance disruption. Exact sequences and rules must be frozen before outputs; confidence/reset events may be analyzed only after the data lock. No training or new large dataset is required.
- **State-matched fork:** structurally feasible by snapshotting current box, four hidden tensors, frame counter, active templates/boxes, raw bank, confidence/reset status, and RNG state. Full-controller and long-sequence parity remain unverified.
- **Budget:** the complete-frame CPU model-only median was 2,184.557 ms. At 1,500 frames with one zero-state control, arithmetic model time is about 1.82 hours, excluding controller, state-copy, replay, bootstrap, and instrumentation overhead (`screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:175-218`).
- **Collision/deployment:** MCITrack already owns Mamba contextual propagation, Injector/Extractor fusion, confidence reset, gated template admission, bounded bank, and refresh. MambaLCT and generic conditional SSM computation are direct collision risks. Wrapper removal, precision reduction, caching, fixed pruning, bank work, and export are engineering absent a condition-specific robustness interaction. Explicit-state ONNX parity is encouraging, but TensorRT, reduced-precision state, controller integration, and Nano measurements remain unknown (`screening/codex/2026-08-25_stage3_gap_G2_code_formulation.md:188-208`; `screening/codex/2026-08-25_stage2B_targeted_hg5_evidence.md:220-234`).

**Proposed minimum probe:** from each identical baseline pre-frame state, compare the released path with all four previous carried states set to zero. Retain current Mamba/contextual computation, all five templates, checkpoint, crop, and head. Checkpoint-wrapper on/off remains an engineering control and is excluded from the scientific comparison.

**Exact falsification rule:** reject if released-state versus zero-state effects do not interact with stable versus disruption conditions; state norms/reset timing do not predict marginal contribution; the released reset already removes the suspected harmful state with no residual failure; or the only remaining differences are wrapper, precision, caching, bank, or export cleanup.

**F0 state:** `TRIAGE_READY_FOR_BOUNDED_DIAGNOSTIC`.

## 5. Locked next state

- F0 lean triage: **COMPLETE**;
- F1 Manager-Codex reconciliation: **PENDING**;
- authorized mini-probes: **NONE**;
- F2 maximum candidates: **2**;
- HG6: **NOT STARTED for these F0 candidates**;
- S1-S7: **NOT STARTED**;
- primary shortlist: **NONE**;
- main baseline: **NONE**;
- proposed architecture: **NONE**.

Stop at the F1 reconciliation boundary.
