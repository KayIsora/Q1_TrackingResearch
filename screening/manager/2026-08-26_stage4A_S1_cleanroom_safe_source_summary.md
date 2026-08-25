# Stage 4A-S1 — Clean-room-safe source summary

**Date:** 2026-08-26  
**Purpose:** provide only the source-selection facts required for outcome-independent interval proposal.  
**Sanitization status:** MANAGER-REVIEWED; NO TRACKER-OUTCOME PAYLOAD.

## 1. Canonical source

Use only the acquired OTB100 / OTB-2015 source tree:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`

Source record:

- Figshare DOI: `https://doi.org/10.6084/m9.figshare.24427468.v1`
- Figshare file ID: `42879853`
- archive filename: `OTB2015.zip`
- archive byte count: `2,722,980,405`
- provider MD5: `342b7dcb81142462b8ae9bb835cba6b4`
- archive SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`
- extracted-file manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`

The source payload passed archive and extracted-content integrity review. Source JPEGs and annotation bytes must remain unchanged.

## 2. Evaluator/source readiness

The acquired package supports all 100 logical entries used by the pinned SpikeTrack OTB evaluator. The exact logical mapping must come from:

`faicaiwawa/SpikeTrack` at commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`

using:

`lib/test/evaluation/otbdataset.py`.

The S256-T1 source-selection geometry may use only:

- `experiments/spiketrack/spiketrack_s256_t1.yaml`
- `lib/test/tracker/seqtrack_utils.py`

as non-executing contract references.

## 3. Outcome-independent inventory

The allowed starting inventory is:

`screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv`.

It was produced from official attributes, object/sequence semantics and direct inspection of fixed source-frame samples before the bounded E2 tracker executions. It contains:

- 100 complete logical OTB entries;
- 47 rows with a non-empty candidate-distractor lead;
- 50 rows with a possible-control lead;
- no final interval bounds;
- no ambiguity labels;
- no discovery/hold-out assignment;
- no frozen control pairing.

Every lead must be rescanned at interval level. A non-empty lead does not automatically qualify a sequence.

## 4. Existing quarantine

The following sequences are outcome-exposed from earlier reproduction work and are excluded from primary/control selection and coverage counts:

- Deer
- Crossing
- Couple

They must not be scanned for interval proposals in the outcome-independent lane.

## 5. Prohibited evidence

The clean room must not contain or access:

- tracker prediction files;
- author-released or local result files;
- performance metrics;
- sequence-level tracker outcome values;
- divergence or failure records;
- score maps or confidence values;
- MRM logs or ablation results;
- any artifact from either invalidated S1 attempt.

The full E2 reconciliation is deliberately not an allowed clean-room input because it contains tracker-outcome evidence. This sanitized summary replaces it for source-selection purposes.

## 6. Allowed stage action

After a corrected clean room is approved, the next lane may only:

- inspect canonical source frames and ground truth;
- propose continuous distractor and control intervals;
- derive nominal search context from ground truth and the static config contract;
- create source-only contact sheets;
- propose a provisional sequence-disjoint split for Manager review.

It may not run SpikeTrack, inspect outcomes, freeze the slice or start Stage 4B.

## 7. Locked state

- canonical OTB source: ESTABLISHED
- outcome-independent inventory: SUFFICIENT FOR INTERVAL PROPOSAL
- corrected clean-room setup: REQUIRED
- frozen diagnostic slice: NOT CREATED
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
