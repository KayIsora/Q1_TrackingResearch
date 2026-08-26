# Stage 4A-S1-R3 — Manager freeze review

**Date:** 2026-08-26  
**Status:** `R3_ACCEPTED_DIAGNOSTIC_SLICE_FROZEN`  
**Source commit reviewed:** `b747065de2f2c39db5aafb37231bef53d9568cac`

## Boundary

This review evaluates only the source/GT-derived R3 interval, control, matching, split and visual-review package. It does not run SpikeTrack, inspect tracker outcomes, assign `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, select a main baseline, or approve a proposed architecture.

Manager reviewed the R3 tables and all 20 source-only pair sheets exported from the exact source commit through a temporary non-main GitHub Actions branch. Artifact ID `9589771189` had digest `sha256:93e7e6edf476e183adb1ffb0d88aad78692ac1769bd5fcc48ad713d0f28060c6`. The temporary branch was reset to the source commit after export; no scientific artifact on `main` was changed by the export.

## 1. Process decision

R3 process integrity is accepted:

- no tracker prediction, metric, score, divergence, MRM result, model or checkpoint was accessed;
- `Deer`, `Crossing` and `Couple` remained quarantined and unopened;
- the six accepted R2 anchors were preserved;
- the four held R2 primaries were rematched once, failed the locked control requirements, and were replaced rather than forced into the primary analysis;
- all 20 final pairs are `MATCH_PASS` under the locked numeric, subtype, no-distractor, split and reuse gates;
- discovery and hold-out complete source-sequence sets are disjoint;
- event distinctness, interval overlap and control reuse audits pass;
- all review images contain source frames and permitted source/GT annotations only.

## 2. Coverage decision

The locked coverage floor is satisfied:

- discovery: **12 distractor intervals + 12 matched controls**, from **11 primary sequences**;
- hold-out: **8 distractor intervals + 8 matched controls**, from **7 primary sequences**;
- maximum primary intervals per sequence: **2**;
- maximum controls per control sequence: **2**;
- cross-group sequence intersection: **empty**;
- broad-superclass distribution: PERSON 10/20, FACE_HEAD 4/20, VEHICLE 4/20, OBJECT_OTHER 2/20.

The loss of the ANIMAL superclass is accepted. A scientifically incompatible animal control is not retained merely to preserve class count. The final package still exceeds the locked minimum of three broad superclasses.

## 3. Singer1 governance decision

`R3-D12 Singer1` is accepted as `PERSON`.

The reserve-pool heading that listed Singer1 under `FACE_HEAD` was an organizational classification, not a binding target-extent annotation. Canonical OTB ground truth and direct source review show a full-body performer target, and the matched Dancer control is likewise a full-body performer. Therefore:

- broad superclass: `PERSON`;
- object class: `person`;
- final tier: `TIER_B`;
- ambiguity level: `1`;
- analysis eligibility: retained.

This decision resolves the only governance-dependent coverage slot; discovery remains at 12 pairs.

## 4. Manager tier corrections

Two R3 source intervals remain valid but are downgraded to avoid overstating visual similarity:

- `R3-D05 Car4`: `TIER_A -> TIER_B`, ambiguity `2 -> 1`, because the distractor differs materially in color despite matching passenger-car shape, viewpoint, scale and road role.
- `R3-D07 Shaking`: `TIER_A -> TIER_B`, ambiguity `2 -> 1`, because the adjacent pianist and tracked guitarist are same-role adult heads at comparable scale but differ visibly in hair/appearance.

All other R3 tiers are accepted as proposed.

## 5. Frozen pair set

The project freezes the exact 20 pairs recorded in:

`screening/manager/2026-08-25_stage4_spiketrack_diagnostic_slice.csv`

The file is pair-level and is the sole execution allowlist for Stage 4B/4C. It records:

- exact primary and control sequence/frame bounds;
- discovery versus hold-out group;
- event ID;
- final tier and ambiguity level;
- search-context status;
- sensitivity stratum;
- source commit and pair-sheet evidence.

No pair, bound, split, control or ambiguity level may be changed after tracker results are inspected. Any source-integrity defect discovered during execution must stop the affected pair and produce a Manager reconciliation; it may not be silently replaced.

## 6. Sensitivity strata locked before outcomes

The full discovery package remains the primary Stage-4B analysis. The following source-design strata are additionally locked for sensitivity reporting, not candidate mining:

- `STRONG_SAME_SEQUENCE`;
- `CROSS_SCENE_ACTIVITY`;
- `COLOR_DIFFERENCE`;
- `APPEARANCE_DIFFERENCE`;
- `LOW_LIGHT_MULTI_TRAFFIC`;
- `CONTROL_PARTIAL_OCCLUSION`;
- `MULTI_FACE_BACKGROUND`;
- `COSTUME_DIFFERENCE_CLASS_RESOLVED_PERSON`;
- hold-out-only domain notes such as `GRAYSCALE_COLOR_DOMAIN` and `CROWD_CLUTTER_VS_CLEAN`.

A result may not be declared positive solely by selecting a favorable stratum after seeing outcomes. The locked Criterion A/B decision uses the complete discovery set; sensitivity strata explain robustness or confounding only.

## 7. Hold-out seal

The eight hold-out pairs are frozen now but remain outcome-sealed during Stage 4B.

Stage 4B may read their identifiers and hashes only to verify the seal. It must not:

- run SpikeTrack on their primary or control sequences for the held-out intervals;
- compute their IoU, score, MRM contribution or route utility;
- use them to select an MRM/path, threshold, predictor feature or analysis subgroup.

Hold-out execution is reserved for the predeclared Stage 4C validation path if Stage 4B passes Criteria A and B.

## 8. Decision

**R3 execution:** ACCEPTED  
**R3 pair package:** ACCEPTED WITH TWO MANAGER TIER CORRECTIONS  
**Frozen diagnostic slice:** CREATED  
**Stage 4A source-selection pipeline:** COMPLETE  
**Next task:** Stage 4B discovery diagnostic under the locked analysis protocol  
**Stage 4B result:** NOT YET ASSIGNED

## Locked state

- discovery frozen pairs: 12;
- hold-out frozen pairs: 8;
- Stage 4B: READY;
- Stage 4C: LOCKED;
- diagnostic decision: NOT ASSIGNED;
- S1–S7: NOT STARTED;
- primary shortlist: NONE;
- main baseline: NONE;
- proposed architecture: NONE.
