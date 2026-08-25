# Stage 3B — HG6 Novelty Batch N2 Manager audit

**Date:** 2026-08-25  
**Lane:** Manager — primary-source scientific novelty audit  
**Batch:** N2 — CX044 AsymTrack, CX058 HiT-DyHiT  
**Status:** MANAGER AUDIT COMPLETE; independent Codex N2 audit and source registration/reconciliation are required.  
**Governing plan:** `screening/manager/2026-08-25_stage3B_hg6_execution_plan.md`.

## Boundary

This document independently audits whether the two reconciled G2 questions remain materially distinct after mechanism-level prior-art search. It does not assign S1–S7, rank candidates, form a shortlist, select a baseline, or design a proposed architecture.

The decisions below are Manager-lane provisional HG6 decisions. They are not final project decisions until Codex completes an independent audit, serious sources are registered, and Manager↔Codex reconciliation is closed.

Search covered peer-reviewed tracking work, arXiv-only novelty references, and foundational adaptive-inference literature. Search-result summaries were used only as leads; collision reasoning relies on official proceedings, official publisher pages or official preprints when no reviewed version was identified.

---

# 1. Search log

| # | Exact query | Candidate/mechanism family | Main disposition |
|---:|---|---|---|
| 1 | `2023 2024 2025 2026 visual object tracking adaptive capacity dynamic routing easy hard frames low resolution fast motion viewpoint change tracker` | AsymTrack broad recall | Adaptive-depth/capacity families found |
| 2 | `visual tracking dynamic resolution adaptive computation low resolution fast motion viewpoint change 2025 2026` | AsymTrack precision | AVTrack, BDTrack, ARTrack-AC and adaptive-search work found |
| 3 | `visual tracking early exit router calibration distractor clutter uncertainty dynamic depth 2025 2026` | HiT-DyHiT precision | AEE, UncL-STARK, MVLM and dynamic trackers found |
| 4 | `single object tracking oracle routing deep path shallow path confidence calibration distractor clutter` | HiT-DyHiT precision | No unique DyHiT oracle-calibration method, but close mechanism halves found |
| 5 | `site:openaccess.thecvf.com visual tracking adaptive capacity fast motion motion blur dynamic early exit tracker` | AsymTrack robustness/compute | ARTrack-AC and related CVF work verified |
| 6 | `site:arxiv.org visual tracking uncertainty guided depth adaptation transformer tracker 2026` | HiT-DyHiT uncertainty | UncL-STARK found |
| 7 | `site:openaccess.thecvf.com visual tracking competitor margin confidence memory gated local global search distractor 2026` | HiT-DyHiT distractor routing | MVLM found |
| 8 | `"Learning Motion Blur Robust Vision Transformers with Dynamic Early Exit for Real-Time UAV Tracking" publication venue` | AsymTrack fast motion | BDTrack journal publication found |
| 9 | `"Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking" publication venue` | Adaptive block routing | ABTrack journal publication found |
| 10 | `"Similarity-Guided Layer-Adaptive Vision Transformer for UAV Tracking" CVPR 2025` | Adaptive layers | SGLATrack verified |
| 11 | `"Learning Adaptive and View-Invariant Vision Transformer with Multi-Teacher Knowledge Distillation for Real-Time UAV Tracking"` | AsymTrack viewpoint | AVTrack/AVTrack-MD family found |
| 12 | `view-invariant adaptive visual tracking efficiency viewpoint change UAV tracker publication` | AsymTrack viewpoint | ICML AVTrack and TCSVT extension verified |
| 13 | `low resolution adaptive capacity visual tracking dynamic resolution tracker 2024 2025 2026` | AsymTrack low resolution | Dynamic capacity/search/resolution families found; no AsymTrack-specific exception |
| 14 | `"confidence-calibrated early-exit" visual tracking` | HiT-DyHiT calibration | Adaptive Depth RGB-T tracker found |
| 15 | `"uncertainty-guided" depth adaptation visual tracking early exit` | HiT-DyHiT uncertainty | UncL-STARK verified |
| 16 | `visual tracking router calibration distractor clutter early exit confidence margin` | HiT-DyHiT coupling | MVLM and calibrated early-exit families found |
| 17 | `"Adaptive Depth Lightweight RGB-T Tracking with Holistic Token Routing" official paper` | HiT-DyHiT calibration | CVPR 2026 official source verified |
| 18 | `"Learning an Adaptive and View-Invariant Vision Transformer for Real-Time UAV Tracking" IEEE TCSVT` | AsymTrack chronology | Journal extension metadata verified |

Detailed proposed sources are listed in `screening/manager/2026-08-25_stage3B_hg6_N2_source_candidates.csv`.

---

# 2. CX044 — AsymTrack

## A. Reconciled gap statement

The anchor is AsymTrack-T, with S/B variants serving as controlled capacity/resolution references. The reconciled question is:

> Do stronger AsymTrack family operating points provide disproportionate benefit under low resolution, viewpoint change and fast motion while offering little marginal value on ordinary frames, thereby creating a defensible condition-specific capacity-allocation opportunity?

The template-once asymmetric core, ETM, re-parameterized OPE and corner localization must remain.

## B. Serious novelty adversaries

| Prior work | Year / venue | Mechanism | Relation to the exact gap | Collision class |
|---|---|---|---|---|
| **Depth-Adaptive Computational Policies for Efficient Visual Tracking** | 2018, EMMCVPR/arXiv | Learns frame/object-difficulty gates that choose feature-extractor depth under cost and tracking loss | Foundational same-setting conditional capacity; predates AsymTrack by years | `PARTIAL_COLLISION` |
| **ABTrack: Adaptively Bypassing Vision Transformer Blocks for Efficient Visual Tracking** | 2025, Pattern Recognition | Target/scene-dependent block bypassing plus latent-dimension pruning | Directly covers frame/scene-dependent ViT capacity allocation in generic SOT | `PARTIAL_COLLISION` |
| **SGLATrack** | 2025, CVPR | Dynamically disables representation-similar ViT layers and retains an optimal layer for accuracy-speed trade-off | Covers layer-adaptive tracker capacity and redundancy | `PARTIAL_COLLISION` |
| **HiT-DyHiT** | 2025, IJCV | Easy/hard routing between shallow and deeper tracking paths | Directly covers condition-dependent capacity routing in lightweight SOT | `PARTIAL_COLLISION` |
| **ARTrack-AC** | 2026, CVPR | Temporal-difficulty estimator switches low/high-capacity autoregressive modes | Closest generic-SOT capacity controller; directly covers stronger mode on hard temporal segments | `DIRECT_COLLISION` at the allocation-question level |
| **BDTrack: Learning motion blur robust vision transformers for real-time UAV tracking** | 2026, Expert Systems with Applications | Dynamic early exit for easy/hard frames plus motion-blur-invariant feature learning | Directly couples adaptive computation with a fast-motion/motion-blur robustness target | `DIRECT_COLLISION` for the fast-motion part |
| **AVTrack / AVTrack-MD** | 2024 ICML; 2026 TCSVT extension | Selective activation of Transformer blocks plus view-invariant representation and multi-teacher distillation | Directly couples adaptive computation with extreme viewpoint-change robustness | `DIRECT_COLLISION` for the viewpoint part |
| **SAMViTrack** | 2025, Sensors | Motion/environment-conditioned search-region adaptation under fast motion, occlusion and scale variation | Covers adaptive compute/search allocation tied to fast-motion robustness, though lower venue and different backbone | `PARTIAL_COLLISION` |

## C. Chronology

Depth-adaptive tracking predates AsymTrack by seven years. AVTrack, ABTrack, SGLATrack and HiT-DyHiT all predate or are contemporaneous with the 2025 AsymTrack baseline. ARTrack-AC, BDTrack's journal version and other 2026 works are prior art for any future project contribution.

The project therefore cannot claim first dynamic tracker capacity, first adaptive depth, first block activation/bypass, first easy–hard routing, first view-robust adaptive tracker, or first motion-blur/fast-motion-aware dynamic tracker.

## D. Collision analysis

The intended gap is cumulatively occupied:

1. Conditional tracker capacity is already established by Depth-Adaptive Policies, ABTrack, SGLATrack, HiT-DyHiT and ARTrack-AC.
2. Viewpoint-specific robustness combined with adaptive Transformer activation is already central to AVTrack.
3. Motion-blur/fast-motion robustness combined with dynamic early exit is already central to BDTrack.
4. Motion-conditioned adaptive search allocation is also public in SAMViTrack.

The remaining distinction would be to use the AsymTrack T/S/B family as the low/high-capacity implementation and perhaps add a detector for low resolution, viewpoint change or fast motion. That is an AsymTrack-specific integration/operating-point placement of known adaptive-capacity and attribute-robustness mechanisms.

Low resolution is not enough to rescue the claim: pairing one additional challenge detector with a known capacity controller does not create a materially new efficiency–robustness relation after viewpoint and fast-motion parts are directly occupied.

## E. Manager HG6 decision

**Manager provisional HG6: FAIL**

The candidate-specific oracle-capacity question is scientifically testable, but its mechanism is not sufficiently distinct for the project's novelty gate. Positive diagnostics could show that AsymTrack benefits from conditional capacity, yet that would establish efficacy of applying known adaptive-capacity ideas to AsymTrack rather than a new algorithmic principle.

### Consequence

AsymTrack remains a valuable lightweight baseline/reference and possible deployment comparator. It does not progress to soft scoring or shortlist status under this gap.

Reopening would require a qualitatively new variable or relation not reducible to challenge classification, uncertainty/difficulty estimation, dynamic depth/resolution, branch routing, motion-blur/view-invariant training or switching between existing family variants.

---

# 3. CX058 — HiT-DyHiT

## A. Reconciled gap statement

The anchor is standalone DyHiT Route1/Route2. The question is:

> Do distractor/clutter failures correspond to router misallocation—hard frames exiting through Route1 and easy frames unnecessarily entering Route2—and can a better calibrated route policy jointly improve robustness and reduce wasted compute?

The hierarchical HiT backbone, Bridge Module, lightweight/deeper routes and dynamic router must remain.

## B. Serious novelty adversaries

| Prior work | Year / venue/status | Mechanism | Relation to the exact gap | Collision class |
|---|---|---|---|---|
| **Depth-Adaptive Computational Policies for Efficient Visual Tracking** | 2018, EMMCVPR/arXiv | Difficulty-conditioned tracker-depth gating under joint tracking/cost loss | Foundational route-allocation prior art | `PARTIAL_COLLISION` |
| **ABTrack** | 2025, Pattern Recognition | Target/scene-dependent block bypass decisions | Covers adaptive route/depth based on current target/scene | `PARTIAL_COLLISION` |
| **ARTrack-AC** | 2026, CVPR | Learned temporal-difficulty estimator switches high/low capacity | Direct difficulty-to-capacity allocation in RGB SOT | `PARTIAL_COLLISION` |
| **Adaptive Depth Lightweight RGB-T Tracking with Holistic Token Routing** | 2026, CVPR | Anytime heads plus a confidence-calibrated early-exit policy selecting the earliest reliable layer | Directly covers confidence calibration of tracking early exits | `DIRECT_COLLISION` for the route-calibration subclaim |
| **UncL-STARK: Uncertainty-Guided Inference-Time Depth Adaptation for Transformer-Based Visual Tracking** | 2026, arXiv-only | Output uncertainty and temporal feedback select encoder/decoder depth without changing the tracker core | Directly covers uncertainty-guided calibrated depth adaptation in RGB SOT | `PARTIAL_COLLISION` / strong novelty reference |
| **MVLM** | 2026, CVPR | Competitor-margin confidence and temporal memory gate compact local search versus global relocalization | Directly connects distractor/competitor ambiguity to conditional tracking mode selection | `DIRECT_COLLISION` for the ambiguity-conditioned mode-gating half |
| **BDTrack** | 2026, Expert Systems with Applications | Dynamic early exit allocates deeper computation to harder frames while robustness training targets motion blur | Demonstrates condition-specific robustness plus early-exit compute allocation | `PARTIAL_COLLISION` |
| **AVTrack** | 2024, ICML | Selective Transformer-block activation plus view-invariant learning | Demonstrates joint adaptive capacity and robustness-oriented representation learning | `PARTIAL_COLLISION` |

## C. Chronology

Difficulty-conditioned depth policies predate DyHiT. ABTrack and AVTrack predate or coincide with the 2025 journal family. AEE, UncL-STARK, MVLM, ARTrack-AC and BDTrack are public before any future project method and therefore constrain novelty regardless of whether they appeared after DyHiT itself.

## D. Collision analysis

The proposed HiT-DyHiT gap is cumulatively occupied:

1. Easy/hard route allocation is the baseline's own main contribution.
2. Confidence-calibrated early exit in tracking is implemented by the 2026 Adaptive Depth RGB-T tracker.
3. Uncertainty-guided inference-time depth adaptation in generic RGB SOT is implemented by UncL-STARK.
4. Competitor/distractor margin confidence driving a conditional tracking mode is implemented by MVLM.
5. Difficulty-conditioned high/low capacity is implemented by ARTrack-AC and earlier route/depth trackers.

The residual proposal would combine an existing confidence/uncertainty or target–distractor margin with DyHiT's existing Route1/Route2 router, possibly trained against an oracle deep-path-benefit label. Oracle-route analysis is an appropriate diagnostic, but using it to recalibrate a known early-exit controller is not a sufficiently new algorithmic relation under the project's Q1-oriented gate.

The exact phrase `false-shallow versus false-deep under clutter` is not itself a new mechanism. It is an evaluation/calibration framing of already public conditional-depth and ambiguity-conditioned mode-selection methods.

## E. Manager HG6 decision

**Manager provisional HG6: FAIL**

The route-calibration gap does not survive mechanism-level novelty review at the required ambition. The remaining work is a DyHiT-specific recalibration or integration of known uncertainty/margin/difficulty signals with an existing router.

### Consequence

HiT-DyHiT remains important as:

- an adaptive-computation reference;
- a comparison tracker;
- an edge-oriented deployment baseline;
- a source of route-oracle diagnostic methodology.

It does not progress to soft scoring or shortlist status under this gap.

Reopening requires a qualitatively new relation beyond confidence/uncertainty calibration, difficulty prediction, distractor-margin gating, early exit, branch routing or oracle-label supervision.

---

# 4. Manager N2 summary

| Candidate | Manager provisional HG6 | Closest collision | Manager conclusion |
|---|---:|---|---|
| CX044 AsymTrack | **FAIL** | ARTrack-AC; AVTrack; BDTrack; HiT-DyHiT | Attribute-conditioned capacity allocation is cumulatively occupied |
| CX058 HiT-DyHiT | **FAIL** | Adaptive Depth RGB-T; UncL-STARK; MVLM; ARTrack-AC | Router calibration under ambiguity is cumulatively occupied |

## Locked non-claims

- These are not final HG6 decisions until independent Codex N2 audit and source registration/reconciliation.
- No S1–S7 score is assigned.
- No candidate is ranked or shortlisted.
- No baseline is selected.
- No architecture is proposed.
