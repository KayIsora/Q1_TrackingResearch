# Stage 2A — Batch D reconciliation and HG4/HG5 gate decisions

**Date:** 2026-08-25  
**Status:** BATCH D RECONCILED; Stage 2A systematic evidence extraction is now complete.  
**Inputs:** Manager scientific audit `screening/manager/2026-08-25_stage2_batchD_scientific_audit.md` and Codex code audit `screening/codex/2026-08-25_stage2_batchD_code_audit.md`.  
**Governing protocol:** `docs/11_systematic_screening_protocol.md`.

## Boundary

This reconciliation decides only **HG4 — RTX 3060 12 GB research feasibility** and **HG5 — Jetson Nano B01 deployment plausibility** where combined paper/code evidence is sufficient. It does **not** begin HG6, assign S1–S7, rank candidates, form a shortlist, select a baseline, or approve a proposed architecture.

`PASS` is a project gate, not an experimental result. HG5 PASS means a credible structural path exists; it is not a Jetson Nano FPS/memory claim. `PENDING` is retained whenever targeted runtime/export evidence can still reverse the decision.

---

## CX053 — UncTrack

**Final HG4: PASS**  
**Final HG5: PENDING**

### Reconciled evidence

- UncTrack has released Base/Large stage-1 and stage-2 checkpoints, explicit two-stage training, and a stage-2 path that trains the PMN/confidence components while the main tracking backbone/localization path is frozen.
- The Base online path uses bounded state: a three-prototype memory, bounded online-template slots, cached template K/V when `online_size>1`, and a fixed Kalman state. No sequence-length-growing feature history was found.
- ULD and PMN execute on every neural attempt. A low-reliability first pass can trigger a second complete ConvMAE+ULD+PMN inference with a 1.5× search factor. This is an important runtime-mode distinction but not yet a measured bottleneck.
- The released online tracker contains a one-character full-width-parenthesis syntax defect and the shell/checkpoint filename ordering differs from the current official model folder. These are reproducibility/engineering defects that must be repaired for execution, but they do not by themselves show that checkpoint-based model research is beyond RTX3060-class resources.
- No complete ONNX/TensorRT path is released. Dynamic `topk`, mutable template K/V, Python branches, `.item()`/`.tolist()` and NumPy Kalman logic require targeted deployment profiling.

### Gate rationale

**HG4 PASS:** checkpoint-based research is structurally plausible. The released two-stage recipe permits the reliability/memory part to be trained with the main model frozen, and the Base architecture does not require reproducing an inaccessible large training farm merely to modify and evaluate a proposed module. A full baseline-from-scratch recipe is not required by project policy.

**HG5 PENDING:** bounded memory and template caching prevent a structural FAIL, but the ordinary path already includes ConvMAE+ULD+PMN and unreliable frames can double the full neural inference. Export/operator support and the frequency/cost of the second-attempt branch are unresolved. Targeted runtime/export evidence is required before Nano plausibility can be promoted to PASS.

---

## CX058 — HiT / DyHiT

**Final HG4: PASS**  
**Final HG5: PASS**

### Reconciled evidence

- The HiT family is explicitly lightweight and supplies Tiny/Small/Base hierarchical LeViT variants. DyHiT trains a lightweight Route1 branch and then a small router over pretrained HiT components; the repository contains single-/multi-GPU launch paths.
- Runtime state is bounded. The released trackers keep the initial raw template and current bbox rather than a growing temporal feature bank.
- The raw template is re-encoded every frame. DyHiT makes an early route decision after partial lightweight computation; hard frames continue deeper. DyOSTrack keeps both lightweight and host models resident, but the host is not executed before the route decision.
- Static HiT uses ordinary Conv/Linear/matmul/softmax/ConvTranspose-style operators and includes an intended ONNX path. The pinned exporter/profiler contains argument/checkpoint-name drift, and dynamic DyHiT/DyOSTrack has no complete official export path; these are engineering risks rather than evidence that the architecture inherently lacks an edge path.
- Paper/device evidence on AGX/NX cannot be transferred to Nano FPS, but together with the very small hierarchical family and route-based early exit it supports structural deployment plausibility.

### Gate rationale

**HG4 PASS:** the architecture and staged dynamic training are small/bounded enough for meaningful checkpoint-based single-3060 experimentation. The project does not require reproducing the paper's original throughput settings at their published batch size.

**HG5 PASS:** this is a structural plausibility decision only. The family was designed for low compute, contains Tiny/Small variants, keeps bounded state, and has a static graph/operator family that already has an intended ONNX route. Dynamic control/export still needs device validation, but reaching Nano does not appear to require replacing the core tracker. No Nano FPS is claimed.

---

## CX125 — MPT

**Final HG4: PASS**  
**Final HG5: FAIL**

### Reconciled evidence

- The reproducible released candidate unit is **OSTrack + MPT**, not a standalone tracker. The pinned release does not provide equivalent reproducible SeqTrack/ARTrack implementation/checkpoint units.
- MPT_MAE256/MPT_MAE384 keep the complete OSTrack ViT-B/16 host and add a motion-prompt encoder/decoder. The constructor-derived MPT-only subtotal is about 13.06M parameters, excluding the full host.
- The released path uses a fixed 30-box trajectory, converts it to 63 motion/prompt tokens, and executes prompt self-attention, prompt-to-image cross-attention, image-to-token cross-attention, adaptive weighting and CENTER prediction every frame. There is no conditional compute branch that avoids the host or MPT on easy frames.
- The host visual tracker still executes fully. MPT is therefore lightweight only as an incremental plug-in relative to the host, not as the complete inference system.
- No complete MPT-specific ONNX/TensorRT export path is released, and the supplied evaluation shell has an argument mismatch with the pinned test script.

### Gate rationale

**HG4 PASS:** training is centered on a relatively small added motion module around a pretrained host, so checkpoint-based research on RTX3060 is plausible under reduced batch/appropriate freezing. This gate says nothing about deployment speed.

**HG5 FAIL:** the main reproducible deployment unit retains a full ViT-B OSTrack and adds ~13M parameters plus always-on motion/fusion computation. The release supplies no lighter host integration that can be treated as the same reproducible candidate. Making the total system Nano-suitable would therefore depend on replacing/compressing the host as a core rescue step rather than applying a bounded optimization to the released candidate. MPT remains important as a mechanism/novelty reference.

---

## Batch-D consequence

| Candidate | HG4 | HG5 | Progression |
|---|---:|---:|---|
| CX053 UncTrack | **PASS** | PENDING | targeted HG5 profiling required before HG6 |
| CX058 HiT-DyHiT | **PASS** | **PASS** | survives HG4/HG5; hold for candidate-specific gap/HG6 |
| CX125 MPT | **PASS** | **FAIL** | excluded from main-baseline progression; mechanism/reference only |

No candidate is shortlisted or scored.

---

## Stage-2A closure state

All predeclared systematic evidence batches A–D are now closed.

### Candidates with HG1–HG5 PASS and eligible to be held for later candidate-specific research-gap/HG6 work

- CX009 — UETrack
- CX013 — FARTrack
- CX024 — DAM4SAM
- CX043 — SUTrack
- CX044 — AsymTrack
- CX058 — HiT-DyHiT

These are **not a shortlist**. HG6 is still PENDING and S1–S7 have not been assigned.

### Candidates with HG4 PASS but HG5 PENDING — targeted deployment evidence required before HG6

- CX007 — SpikeTrack
- CX010 — UTPTrack
- CX020 — SAMURAI
- CX037 — SSTrack-AAAI
- CX038 — MCITrack
- CX053 — UncTrack

### HG5 FAIL / reference-only after deep audit

- CX014 — GOT-Edit
- CX017 — GOT-JEPA
- CX049 — SPMTrack
- CX125 — MPT

### Early-gate exclusions / suspensions

- CX040 — MambaLCT — HG3 FAIL
- CX064 — SiamABC — HG3 FAIL
- CX046 — JDTrack — HG3 PENDING
- CX051 — UMDATrack — HG3 PENDING

## Next gate

The next project action is **targeted HG5 evidence/profile resolution** for the six HG5-PENDING candidates. This is not reproduction, HG6, soft scoring, or baseline selection.

Only after each targeted candidate is resolved to HG5 PASS/FAIL may the project construct candidate-specific research-gap statements and begin mechanism-level HG6 novelty audit.

## Locked non-claims

- HG6: **NOT STARTED**
- S1–S7 soft scoring: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
