# Stage 4A-E2 — OTB100 acquisition and bounded-reproduction reconciliation

**Date:** 2026-08-26  
**Status:** `E2_ACCEPTED_STAGE4A_SLICE_REVIEW_NEXT`  
**Inputs:**

- `screening/codex/2026-08-25_stage4A_E2_otb_acquisition_report.md`
- `screening/codex/2026-08-25_stage4A_E2_otb_source_manifest.csv`
- `screening/codex/2026-08-25_stage4A_E2_otb_hash_comparison.csv`
- `screening/codex/2026-08-25_stage4A_E2_reproduction.csv`
- `screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv`
- bounded text artifacts under `screening/codex/artifacts/stage4A_E2/`
- `screening/manager/2026-08-25_stage4A_E2_otb_acquisition_protocol.md`
- `screening/manager/2026-08-25_stage4A_E2_review_checklist.md`
- `screening/manager/2026-08-25_stage4_spiketrack_diagnostic_protocol.md`

## Boundary

This reconciliation accepts the E2 dataset acquisition, identity audit, bounded reproduction evidence and outcome-independent sequence inventory. It does not start Stage 4B, freeze frame intervals, assign `DIAG_PASS` or `DIAG_FAIL`, assign S1–S7, form a shortlist, select a main baseline, or authorize proposed-architecture design.

## 1. Download and integrity

The authorized Figshare file ID `42879853` was downloaded to the isolated `F:` destination with the exact expected byte count and provider MD5:

- bytes: `2,722,980,405`;
- MD5: `342b7dcb81142462b8ae9bb835cba6b4`;
- SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`.

ZIP readability, central-directory listing and full CRC streaming passed. The extraction command returned a non-zero status only because exFAT did not preserve source timestamps. Independent post-extraction validation established:

- all `58,764` file members present;
- exact extracted byte total;
- no missing or extra files;
- no size, CRC32 or byte mismatches;
- no source JPEG or annotation rewrite.

**Manager decision:** download, integrity and extracted-content evidence are accepted. The timestamp metadata warning is not a content-integrity blocker.

## 2. Dataset identity

All `100` logical OTB evaluator entries are source-ready from the acquired package. For the existing local comparison universe:

- all `31/31` compared image streams match the acquired package in raw bytes over the declared comparison window and in decoded BGR/RGB pixels;
- normalized parsed ground truth matches for `29/31` rows;
- the remaining two rows are incomplete `Human3` copies and are not treated as complete comparisons.

For the predeclared reproduction sequences `Deer`, `Crossing` and `Couple`, image bytes and parsed GT values match the acquired source.

**Final E2 dataset-identity state:** `ESTABLISHED`.

## 3. Bounded reproduction evidence

The acquired-source official-default run, acquired-source deterministic run and prior local official-runner output are byte-identical for all three predeclared sequences. Therefore canonical data acquisition did not change the local predictions.

The local versus author-released S256-T1 Success-AUC differences remain:

- Deer: `29.912810` percentage points;
- Crossing: `0.476190` percentage points;
- Couple: `1.462585` percentage points.

**Final E2 label:** `E2_DATA_IDENTITY_NOT_CAUSE`.

The author-released OTB raw result still lacks a complete source-commit and runtime manifest. Exact paper/release prediction reproduction therefore remains unresolved.

## 4. Scoped operational-baseline decision

**PROJECT DECISION — diagnostic-only boundary accepted:**

The exact official source commit, official S256-T1 config, author-linked checkpoint, canonical OTB bytes, official runner, image loader and local runtime behavior are now fixed and independently auditable. Local default and deterministic runs are stable and identical. The unexplained difference is confined to the provenance of the author-released prediction run, not to an unstable or unauditable local execution path.

For **paired Stage-4 diagnostic experiments only**, the project accepts the current local official-runner output as the `LOCAL_OPERATIONAL_BASELINE`.

This acceptance is deliberately narrower than official reproduction:

- it does not claim that the project reproduced the author-released OTB predictions;
- it does not replace the author raw result with the local result in paper comparisons;
- it does not allow claims about official benchmark parity;
- it applies only to within-source, within-checkpoint, paired baseline-versus-diagnostic controls on the frozen slice;
- a future main-baseline selection still requires controlled reproduction/evaluation on the mandatory LaSOT, GOT-10k and TrackingNet protocols;
- the raw-result mismatch remains a declared release-provenance limitation.

This scoped boundary is accepted before any Stage-4B result is inspected. It avoids treating an unresolved author-side release manifest as either a scientific failure or an unlimited blocker for paired mechanism diagnostics.

## 5. Linux E3 decision

A Linux comparison may still provide useful platform characterization, but it is not required before outcome-independent slice preparation or the paired Stage-4B diagnostic under the scoped operational baseline.

**Stage 4A-E3 state:** `OPTIONAL_DEFERRED_NOT_AUTHORIZED`.

E3 may be reconsidered if:

- the author provides an environment contract that makes Linux matching scientifically decisive;
- Stage-4B results are sensitive to platform or numerical mode;
- or later reproduction on mandatory benchmarks requires it.

No Linux environment setup is authorized by this reconciliation.

## 6. Outcome-independent inventory

The E2 inventory contains:

- all 100 logical OTB entries;
- 47 independently justified candidate-distractor rows;
- 50 potential-control rows;
- no tracker-output-based selection language;
- no final interval, ambiguity label, control pair or split assignment.

The count exceeds the locked minimum for moving to interval-level review. However, the inventory was based on fixed first/lower-middle/last samples and is not itself a frozen diagnostic slice.

**Inventory state:** `SUFFICIENT_FOR_MANAGER_SLICE_REVIEW`, not `SLICE_FROZEN`.

## 7. Next stage

The next step is **Stage 4A-S1 — outcome-independent interval proposal and visual review package**.

Stage 4A-S1 may:

- scan source frames without tracker outputs;
- identify candidate distractor and matched-control intervals;
- produce GT-only contact sheets and proposal tables;
- prepare sequence-disjoint split options for Manager review.

Stage 4A-S1 may not:

- run SpikeTrack;
- use released or local predictions;
- assign final splits or ambiguity labels;
- freeze the diagnostic slice;
- start MRM ablations.

Stage 4B remains locked until the Manager commits a final frozen diagnostic slice.

## Final decision

**Stage 4A-E2:** `ACCEPTED`  
**Downstream state:** `E2_ACCEPTED_STAGE4A_SLICE_REVIEW_NEXT`

## Locked state

- canonical OTB source: `ESTABLISHED`
- local operational diagnostic baseline: `ACCEPTED_WITH_RELEASE_PROVENANCE_LIMIT`
- exact author raw-result reproduction: `UNRESOLVED`
- Stage 4A-E3 Linux comparison: `OPTIONAL_DEFERRED_NOT_AUTHORIZED`
- Stage 4A-S1 slice proposal: `READY`
- frozen diagnostic slice: `NOT_CREATED`
- Stage 4B: `LOCKED`
- diagnostic decision: `NOT_ASSIGNED`
- S1–S7: `NOT_STARTED`
- primary shortlist: `NONE`
- main baseline: `NONE`
- proposed architecture: `NONE`
