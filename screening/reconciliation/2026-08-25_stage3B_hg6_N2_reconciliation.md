# Stage 3B — HG6 Novelty Batch N2 final reconciliation

**Date:** 2026-08-25  
**Status:** N2 CLOSED; Stage 3B HG6 novelty audit is complete.  
**Inputs:**

- `screening/manager/2026-08-25_stage3B_hg6_N2_manager.md`
- `screening/codex/2026-08-25_stage3B_hg6_N2_codex.md`
- `screening/codex/2026-08-25_stage3B_hg6_N2_source_registration_report.md`
- canonical sources R66–R77, together with the already registered baseline and comparison sources.

**Governing plan:** `screening/manager/2026-08-25_stage3B_hg6_execution_plan.md`.

## Boundary

This reconciliation makes the final project HG6 decision for N2 only. It does not assign S1–S7, rank candidates, create a shortlist, select a main baseline, authorize proposed-architecture design, or claim that any diagnostic hypothesis is true.

Manager and Codex independently reached the same provisional decisions. Canonical source registration is complete with no flags. The final decisions therefore rest on primary-source evidence agreement rather than voting, tracker familiarity, or the absence of an implementation with the same name.

---

## CX044 — AsymTrack

**Final HG6: FAIL**

### Exact audited question

The audited question was whether stronger AsymTrack family operating points could provide disproportionate benefit under low resolution, viewpoint change, and fast motion while adding little marginal value on ordinary frames, thereby creating a condition-specific capacity-allocation opportunity.

The intended core was AsymTrack's template-once/search-online asymmetry, Efficient Template Modulation, re-parameterized Object Perception Enhancement, and corner localization.

### Cumulative collision

The allocation relation is already extensively occupied:

- Learning Policies for Adaptive Tracking With Deep Feature Cascades selects feature depth according to frame difficulty in SOT [R66].
- Depth-Adaptive Computational Policies learns cost-aware tracker depth under object/frame difficulty [R67].
- Exploring Dynamic Transformer for Efficient Object Tracking performs easy/hard route allocation with attribute-conditioned computation [R68].
- ABTrack performs target- and scene-conditioned Transformer-block bypassing in generic SOT [R69].
- AVTrack combines adaptive block activation with view-invariant representation learning [R70].
- SGLATrack performs layer-adaptive capacity selection using representation similarity [R71].
- BDTrack combines dynamic early exit with motion-blur and fast-motion robustness [R72].
- Efficient Early Exit SOT via General Distribution uses object/background distinguishability to control exit depth [R73].
- ARTrack-AC already switches low/high tracking capacity from temporal difficulty [R56].
- HiT-DyHiT itself supplies easy/hard shallow/deep routing [R49/R50].

### Why the residual distinction is insufficient

No registered source uses AsymTrack-T/S/B as the exact controlled family, and no source reproduces the exact proposed factorial over low resolution, viewpoint change, and fast motion. That remaining difference is implementation-specific.

The scientific relation remains:

> infer frame/challenge difficulty and allocate a stronger tracker capacity, depth, layer set, resolution, or route only when it is useful.

That relation predates AsymTrack and is also directly coupled to viewpoint and motion robustness in recent work. Substituting AsymTrack's family variants for the capacity points, or adding challenge detectors to select among them, is an application of established adaptive-capacity mechanisms rather than a materially new algorithmic relation.

Low resolution alone does not rescue the claim: attaching one more challenge classifier or dynamic-resolution controller to a known capacity policy would remain an ordinary combination unless a qualitatively new causal variable is demonstrated.

### Consequence

AsymTrack does not progress to S1–S7 scoring or shortlist consideration under this gap. It remains valuable as:

- a lightweight and template-once reference;
- an embedded-deployment comparator;
- a controlled T/S/B accuracy–efficiency family;
- a possible host for engineering studies that do not claim new adaptive-capacity science.

Reopening requires a relation not reducible to difficulty/challenge classification, dynamic depth, early exit, block/layer routing, dynamic resolution, family switching, view-invariant adaptation, or motion-robust routing.

---

## CX058 — HiT-DyHiT

**Final HG6: FAIL**

### Exact audited question

The audited question was whether distractor/clutter failures correspond to router misallocation—hard frames exiting through Route1 and easy frames unnecessarily entering Route2—and whether a better calibrated route policy could jointly improve robustness and reduce wasted computation.

The intended core was standalone DyHiT with the hierarchical HiT backbone, Bridge Module, Route1, Route2, and its easy/hard router.

### Cumulative collision

The proposed relation is already occupied by tracking and adjacent dynamic-inference work:

- foundational and recent SOT methods already select tracker depth/routes from frame or target difficulty [R66–R69].
- Efficient Early Exit SOT via General Distribution controls tracking depth using object/background distinguishability, including clutter-sensitive evidence [R73].
- Adaptive Depth Lightweight RGB-T Tracking uses a confidence-calibrated policy to choose the earliest reliable tracking depth [R74].
- UncL-STARK uses uncertainty and temporal feedback to adapt Transformer tracking depth [R75].
- MVLM uses target–competitor margin and temporal memory to switch compact local versus global tracking modes under ambiguity [R76].
- ARTrack-AC switches low/high capacity from predicted temporal difficulty [R56].
- calibration of overconfident dynamic exit decisions is established in adjacent dynamic-network literature [R77].
- easy/hard routing is already the defining contribution of HiT-DyHiT itself [R49/R50].

### Why the residual distinction is insufficient

Forcing Route1 and Route2 on identical frames and comparing the released router with an oracle route is a useful diagnostic. It can reveal false-shallow and false-deep decisions. However, using that oracle to recalibrate the existing router with confidence, uncertainty, target–distractor margin, or correctness labels is not a new scientific relation after the registered prior art.

The exact phrase `router misallocation under distractor/clutter` is an evaluation framing. The underlying mechanism remains confidence/uncertainty/difficulty-conditioned early exit or branch routing, potentially using an ambiguity signal already public in tracking.

Changing the route names, keeping the HiT Bridge, or training a new threshold against oracle labels does not create sufficient novelty under the project's Q1-oriented gate.

### Consequence

HiT-DyHiT does not progress to S1–S7 scoring or shortlist consideration under this gap. It remains valuable as:

- an adaptive-computation novelty adversary;
- a lightweight/edge tracking reference;
- a route-oracle diagnostic baseline;
- a comparison system for future conditional-compute proposals.

Reopening requires a qualitatively new relation beyond confidence/uncertainty calibration, difficulty estimation, distractor-margin gating, early exit, dynamic depth, branch routing, or oracle-label supervision.

---

## N2 outcome

| Candidate | Final HG6 | Progression |
|---|---:|---|
| CX044 AsymTrack | **FAIL** | excluded from main-baseline progression; reference only |
| CX058 HiT-DyHiT | **FAIL** | excluded from main-baseline progression; reference only |

These rows are not ranked, and their exclusion does not imply that the published trackers are scientifically weak.

## Stage-3B closure

Across both novelty batches:

- CX007 SpikeTrack — **HG6 PASS**, but diagnostic falsification is mandatory before soft scoring.
- CX013 FARTrack — **HG6 FAIL**.
- CX044 AsymTrack — **HG6 FAIL**.
- CX058 HiT-DyHiT — **HG6 FAIL**.

SpikeTrack is therefore the **sole diagnostic-eligible candidate**, not a shortlist winner and not the selected baseline.

## Locked state

- Stage 3A gap formulation: **COMPLETE**
- Stage 3B HG6 novelty audit: **COMPLETE**
- canonical N2 matrix synchronization: **PENDING MECHANICAL UPDATE**
- SpikeTrack diagnostic falsification: **READY, NOT YET STARTED**
- S1–S7: **NOT STARTED**
- primary shortlist: **NONE**
- main baseline: **NONE**
- proposed architecture: **NONE**
