# Stage 4A-S1-R2 — Proposal correction and matched-control remapping protocol

**Date:** 2026-08-26  
**Status:** LOCKED BEFORE R2 EXECUTION  
**Prerequisite:** `screening/reconciliation/2026-08-26_stage4A_S1_R1_visual_review.md`

## 1. Purpose

R2 corrects the visually reviewed R1 proposal set and constructs quantitatively auditable controls for the ten surviving distractor intervals. It remains an outcome-independent source/GT task.

R2 does not freeze the diagnostic slice, run SpikeTrack, inspect tracker outcomes, start Stage 4B, assign `DIAG_PASS`/`DIAG_FAIL`, score a candidate, or design an architecture.

## 2. Accepted candidate set

R2 must retain exactly these candidate IDs unless a source-only integrity problem is found and reported:

### Discovery candidate group

- R1-P01 Basketball
- R1-P02 Bolt
- R1-P04 BlurCar2
- R1-P07 Bird1
- R1-P09 Liquor
- R1-P10 Football

### Hold-out candidate group

- R1-P03 Crowds
- R1-P05 BlurCar4
- R1-P11 Football1
- R1-P12 Soccer

Corrections:

- R1-P12 tier becomes `TIER_B`.
- R1-P03 bounds must be rescanned and either confirmed or adjusted using source frames only.
- R1-P06 and R1-P08 are rejected and must not count toward coverage or return as primaries.

## 3. Working boundary

Use only:

- the accepted v2 clean room;
- canonical OTB100 source frames and GT;
- source-only R1 outputs/contact sheets;
- this protocol and the Manager R1 visual-review decision.

Do not access prediction, AUC/IoU outcome, score/confidence, divergence, MRM or reproduction artifacts.

The quarantine remains:

- Deer
- Crossing
- Couple

They are excluded from proposal/control scanning and coverage.

## 4. Proposal-side numeric summaries

For every retained proposal, calculate the same GT-derived metrics already present for controls:

- interval length;
- median/min/max target-area ratio;
- median and p90 GT center displacement in pixels;
- p90 center displacement normalized by target scale;
- end-to-start area ratio;
- max-to-min area ratio;
- median absolute log area step;
- visibility/occlusion category;
- fast-motion flag;
- low-resolution flag;
- official attributes;
- broad superclass and object class.

No tracker output may enter these summaries.

## 5. Control search order

For every retained proposal:

1. search the same sequence for a clean interval of equal length with no similar distractor;
2. if unavailable, search a non-quarantined same-class sequence;
3. then search a visually compatible subtype within the same broad superclass;
4. use only a broader-superclass match as a declared last resort.

The full canonical OTB source may be searched visually/with GT. Candidate selection must remain independent of tracker behavior.

For `ANIMAL`, the control must be a real animate animal or visually equivalent real animal target. Plush, toy, printed or depicted objects are not valid.

For `FACE_HEAD`, prefer the same subtype: helmet/head for helmet proposals and human face/head for face proposals. Cross-subtype controls require an explicit exception.

## 6. Pair-level quantitative targets

Unless a same-sequence control is used, each pair should satisfy:

- interval length equal where possible, otherwise within `±2` frames;
- median target-area ratio within a factor of `2`;
- normalized p90 motion within a factor of `2`; if both values are below `0.03`, absolute difference `<=0.03` is acceptable;
- max-to-min area ratio within a factor of `2`;
- no full-occlusion mismatch;
- same broad superclass and compatible visual subtype;
- no similar distractor throughout the control interval;
- no control sequence appearing in both discovery and hold-out groups;
- no control sequence linked to more than two primaries.

A failed target may be retained only as `EXCEPTION_PENDING_MANAGER`, with the failed fields and the best rejected alternatives documented.

## 7. Split accounting

Every control inherits the group of its linked proposal.

The complete sequence sets—including both primary and control sequences—must remain disjoint between discovery and hold-out.

A same-sequence control remains in the same group by definition.

## 8. Required revised proposal table

Create:

`screening/codex/2026-08-26_stage4A_S1_R2_revised_distractor_intervals.csv`

Use the ten retained proposal IDs and include:

- all R1 proposal fields;
- Manager decision;
- corrected tier;
- corrected bounds where applicable;
- all proposal-side numeric summaries from Section 4;
- final provisional group;
- `manager_review_status=PENDING_R2_REVIEW`.

## 9. Required revised control table

Create:

`screening/codex/2026-08-26_stage4A_S1_R2_revised_controls.csv`

For every retained proposal include exactly one preferred control and optionally one alternate. Record:

- control ID and linked proposal;
- sequence/bounds/length;
- group;
- same-sequence status;
- visual/subtype matching basis;
- no-distractor evidence;
- all GT-derived metrics;
- reuse count;
- exception state;
- `manager_review_status=PENDING_R2_REVIEW`.

R1-C09 may be retained as the preferred control for R1-P09 if revalidation passes.

## 10. Pair-audit table

Create:

`screening/codex/2026-08-26_stage4A_S1_R2_pair_matching_audit.csv`

Columns must include:

- linked proposal/control IDs;
- group;
- proposal/control sequence;
- proposal/control length and difference;
- proposal/control median area and ratio;
- proposal/control normalized p90 motion and ratio/difference;
- proposal/control max-to-min area and ratio;
- occlusion match;
- fast-motion match;
- low-resolution match;
- broad-class match;
- subtype match;
- attribute overlap;
- control-sequence reuse count;
- cross-group leakage flag;
- each quantitative target pass/fail;
- overall state: `MATCH_PASS`, `EXCEPTION_PENDING_MANAGER`, or `MATCH_FAIL`;
- notes.

## 11. Pair-review images

Create one compact pair-review sheet for each retained proposal:

- top row: five source-only distractor frames;
- bottom row: five source-only control frames;
- allowed GT/search/distractor overlays only;
- display proposal/control metrics and pass/fail badges in a side or footer panel;
- no tracker output.

Store under:

`screening/codex/artifacts/stage4A_S1_R2/pair_sheets/`

Total committed image payload must remain below `25 MiB`.

## 12. Report

Create:

`screening/codex/2026-08-26_stage4A_S1_R2_control_rematch_report.md`

Report:

- outcome-independence declaration;
- accepted/rejected R1 proposal traceability;
- P03 bound result;
- P12 tier correction;
- control search coverage;
- preferred and rejected alternatives per proposal;
- quantitative match results;
- split-disjoint validation including controls;
- exception list;
- image package size;
- readiness conclusion.

Allowed conclusions:

- `S1_R2_COMPLETE_READY_FOR_MANAGER_FINAL_SLICE_REVIEW`
- `S1_R2_CONTROL_MATCHING_INSUFFICIENT`
- `S1_R2_INVALID_OUTCOME_EXPOSURE`
- `S1_R2_INCOMPLETE`

## 13. Required Q1 artifacts

Create only:

- revised distractor CSV;
- revised control CSV;
- pair-matching audit CSV;
- R2 report;
- pair-sheet manifest;
- pair sheets;
- optional exact reproducibility script;
- exact R2 command log.

Do not modify existing R1 or Manager files.

## 14. Validation

Before commit verify:

- exactly ten retained proposals;
- P06/P08 absent;
- P12 is Tier B;
- P03 bounds confirmed/adjusted;
- each proposal has one preferred control;
- proposal-side metrics present;
- pair-level targets computed;
- no control crosses discovery/hold-out;
- no control sequence used more than twice;
- Bird1 control is a real/compatible animal;
- quarantine respected;
- no tracker outcome accessed;
- no final slice frozen;
- no Stage 4B or DIAG/scoring work.

## 15. Locked downstream state

- Stage 4A-S1-R2: READY
- Manager final slice review: LOCKED PENDING R2
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1-S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
