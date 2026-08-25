# Stage 4A-S1-R2 — Manager final pair review

**Date:** 2026-08-26  
**Status:** `S1_R2_REWORK_REQUIRED_COVERAGE_AND_CONTROL_VALIDITY`  
**Source commit reviewed:** `fa3b349b9942d3ad7f4dc51ae41751219e3617eb`

## Boundary

This review evaluates the source/GT-only R2 proposal, control, pair-audit and visual packages. It does not run SpikeTrack, inspect tracker outcomes, freeze the diagnostic slice, start Stage 4B, assign `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, select a baseline, or authorize architecture design.

For visual review, Manager exported the exact ten pair sheets and machine-readable R2 tables from the source commit through a temporary non-main GitHub Actions branch. Artifact ID `9580758712` had digest `sha256:0bec0b049da09dec12eb29b36956f950c956973e1a85b0fd66bc660da8857823`. The temporary branch was reset to the source commit after export; no scientific artifact on `main` was altered by the export.

## 1. Process acceptance

R2 process integrity is accepted:

- no tracker outcome, score, divergence, MRM result or checkpoint was accessed;
- Deer, Crossing and Couple remained quarantined and unopened;
- exactly ten Manager-retained primaries were processed;
- P06/P08 remained excluded;
- P03 bounds were source-confirmed;
- P12 remained Tier B;
- full primary/control sequence sets are disjoint across discovery and hold-out;
- no control sequence is reused more than once;
- all pair sheets contain only source frames, GT, nominal search context, manual distractor aids and GT-derived matching metrics.

The R2 package is scientifically usable evidence. It is not sufficient to freeze the diagnostic slice.

## 2. Critical coverage finding

The locked Stage-4 diagnostic protocol requires:

- discovery: at least **12 distractor intervals and 12 matched controls** from at least 6 sequences;
- hold-out: at least **8 distractor intervals and 8 matched controls** from at least 4 additional sequences.

R2 contains:

- discovery: 6 distractor intervals and 6 controls from 6 primary sequences;
- hold-out: 4 distractor intervals and 4 controls from 4 primary sequences.

It satisfies the **sequence-count floor** but only half of the locked **interval-count floor**. This alone prevents frozen-slice creation, even if all ten controls were valid.

The interval minimum remains in force. It is not revised after seeing the source-only package.

## 3. Pair-level Manager decisions

### 3.1 Provisionally accepted pair anchors

The following six pairs may be retained as source-only anchors for the expanded slice, subject to final full-slice review:

| Proposal | Control | Manager state | Notes |
|---|---|---|---|
| R1-P01 Basketball | R2-C01 David3 | `PAIR_ANCHOR_ACCEPTED` | Class, length, area, motion and scale gates pass. Scene/activity differs; preserve a domain-shift note and later sensitivity analysis. |
| R1-P02 Bolt | R2-C02 Human8 | `PAIR_ANCHOR_ACCEPTED` | Full-body person subtype and all numeric gates pass. Sprint versus isolated-person context differs but does not violate the locked gate. |
| R1-P03 Crowds | R2-C03 Crowds | `PAIR_ANCHOR_ACCEPTED_STRONG` | Same sequence/target/scene, equal length and near-identical GT dynamics. Partial-versus-none visibility difference remains disclosed. |
| R1-P05 BlurCar4 | R2-C05 Suv | `PAIR_ANCHOR_ACCEPTED_WITH_DOMAIN_NOTE` | Vehicle/SUV subtype and numeric gates pass. Color/rear-view versus grayscale rear/side-view domain difference requires sensitivity reporting. |
| R1-P09 Liquor | R2-C09 Liquor | `PAIR_ANCHOR_ACCEPTED_STRONG` | Same sequence, same target/scene and no similar bottle. Preferred matched-control design. R3 should equalize interval length if a clean 25-frame control remains available. |
| R1-P12 Soccer | R2-C12 Man | `PAIR_ANCHOR_ACCEPTED_WITH_OCCLUSION_NOTE` | Real face/head subtype and all numeric gates pass; crowd/clutter partial visibility versus clean indoor face is disclosed. Tier remains B. |

These anchors are not frozen intervals and do not authorize tracker execution.

### 3.2 Controls rejected for primary matched analysis

The following controls are not accepted as final primary matched controls and do not count toward the locked interval minimum:

| Proposal | Rejected control | Reason |
|---|---|---|
| R1-P04 BlurCar2 | R2-C04 CarScale | Normalized p90 motion differs by factor `9.870092`; the control is visually and dynamically too static relative to the urban traffic interval. |
| R1-P07 Bird1 | R2-C07 Panda | Bird-to-panda is not a compatible visual subtype. Broad `ANIMAL` membership cannot isolate a similar-bird distractor effect. |
| R1-P10 Football | R2-C10 Biker | Football helmet versus novelty mask/headgear is not a compatible subtype or scene. |
| R1-P11 Football1 | R2-C11 Surfer | Football helmet/head in a scrum versus bare surfer head is not a compatible subtype or context. |

The four primary intervals remain source-valid distractor leads, but their status becomes:

`HELD_NO_ACCEPTED_CONTROL`.

They may be rematched once under the R3 protocol. If no valid control exists, they must be replaced or retained only as secondary exploratory intervals outside Criteria A/B.

## 4. MATCH_PASS count after semantic review

Machine audit reported 6 `MATCH_PASS` and 4 exceptions. Manager semantic review preserves exactly six acceptable primary pair anchors and rejects all four exceptions from the primary matched analysis.

Therefore:

- accepted pair anchors: 6;
- held primaries without accepted controls: 4;
- final frozen pairs: 0;
- required final pairs: 20.

## 5. Expansion and independence requirements

The next source-only step must construct at least:

- 12 discovery pairs from at least 6 primary sequences;
- 8 hold-out pairs from at least 4 different primary sequences.

Multiple intervals from one sequence are allowed because the final statistics are sequence-clustered, but they must represent distinct source events rather than adjacent subdivisions of one continuous event.

A second interval from the same primary sequence must:

- be non-overlapping;
- have a visibly distinct distractor episode;
- be separated from another selected interval by at least 10 frames or by an unambiguous event boundary approved in the source record;
- have its own matched control;
- not reuse the identical control interval.

No more than three primary intervals may come from one sequence.

## 6. Control rules for the expanded package

Only `MATCH_PASS` pairs count toward the locked 12/8 minimum.

For the primary analysis:

- `EXCEPTION_PENDING_MANAGER` does not count;
- `MATCH_FAIL` does not count;
- exact control intervals may not be reused;
- one control sequence may support at most two distinct controls within one split;
- no source sequence—primary or control—may appear in both discovery and hold-out;
- same-sequence controls remain preferred;
- subtype compatibility remains mandatory for `ANIMAL` and `FACE_HEAD`;
- motion, area, scale, interval-length, visibility and no-distractor gates remain unchanged.

Exception pairs may be preserved separately as exploratory sensitivity material but cannot determine Criteria A/B.

## 7. Replacement reserve boundary

If one of the four held primaries cannot obtain a `MATCH_PASS` control, R3 may replace it using only source-only candidates already identified in R1 and the canonical OTB inventory.

Permitted reserve pool:

- PERSON: `Girl`, `Human3`, `Human4_2`, `Jogging_1`, `Skating1`, `Subway`, `Walking2`;
- VEHICLE: `Car4`, `CarDark`, `Suv`;
- FACE_HEAD: `Freeman3`, `Freeman4`, `Girl`, `Shaking`, `Singer1`;
- additional previously accepted coarse leads: `Ironman`, when its target/non-target independence and superclass are explicitly resolved.

Excluded reserve leads:

- `Coupon` because the lookalikes are printed/depicted;
- `Jogging_2` when it duplicates the same underlying source event as `Jogging_1`;
- `Bolt2` when it duplicates the same race event already represented by Bolt;
- `Matrix` while the distractor remains outside the nominal search context;
- rejected P06/P08 unless Manager explicitly reopens them in a later source-only review.

Replacement selection must not use tracker results and must preserve split diversity.

## 8. Decision

**R2 execution:** ACCEPTED  
**R2 control package:** PARTIALLY ACCEPTED  
**Frozen diagnostic slice:** NOT CREATED  
**Next task:** `Stage 4A-S1-R3 — interval-count expansion and control-validity resolution`  
**Stage 4B:** LOCKED

## Locked state

- provisionally accepted pair anchors: 6;
- held primaries without accepted control: P04, P07, P10, P11;
- required final discovery pairs: 12;
- required final hold-out pairs: 8;
- Stage 4A-S1-R3: READY;
- final source-only review: PENDING;
- frozen diagnostic slice: NOT CREATED;
- Stage 4B: LOCKED;
- diagnostic decision: NOT ASSIGNED;
- S1–S7: NOT STARTED;
- primary shortlist: NONE;
- main baseline: NONE;
- proposed architecture: NONE.
