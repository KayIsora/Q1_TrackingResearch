# Stage 4A-E2 — Manager review checklist

**Date:** 2026-08-25  
**Status:** LOCKED BEFORE E2 EXECUTION  
**Purpose:** prevent post-hoc changes to the E2 acceptance boundary.

## 1. Download and integrity

Manager will verify:

- exact Figshare DOI record and file ID `42879853`;
- expected filename `OTB2015.zip`;
- exact byte count `2,722,980,405`;
- provider MD5 `342b7dcb81142462b8ae9bb835cba6b4`;
- independently computed SHA-256;
- archive readability and member structure;
- external destination on `F:`;
- no archive/image payload committed to GitHub.

Any byte-count or MD5 mismatch blocks extraction and yields E2 incomplete.

## 2. Source preservation and layout

Manager will verify:

- source JPEG and annotation bytes are not rewritten;
- extraction tool/version and file counts are recorded;
- evaluator-compatible staging uses links/copies without altering source data;
- external free-space before/after values are reported.

## 3. Dataset identity

For the overlapping local sequences, especially Deer, Crossing, Couple, Bolt, Jogging_1 and MotorRolling, Manager will inspect:

- raw image hashes;
- decoded BGR/RGB hashes;
- raw GT hashes;
- normalized parsed-GT hashes;
- sequence-level identity classification.

Dataset identity may be `ESTABLISHED`, `PARTIAL`, or `UNRESOLVED`; no status is inferred from tracker accuracy.

## 4. Bounded reproduction

Only Deer, Crossing and Couple are permitted.

Manager will verify:

- exact pinned source/config/checkpoint contract;
- official runner path;
- one default and one deterministic run per sequence;
- prediction SHA-256 and Success AUC;
- comparison to prior local official-runner outputs;
- comparison to author-released S256-T1 raw predictions;
- whether acquired data change local predictions.

Allowed E2 labels:

- `E2_DATA_IDENTITY_EXPLAINS_MISMATCH`;
- `E2_DATA_IDENTITY_NOT_CAUSE`;
- `E2_REPRODUCTION_PENDING`.

E2 does not assign the final reproduction acceptance state.

## 5. Outcome-independent inventory

Manager will reject any candidate-sequence justification based on:

- SpikeTrack prediction;
- score map;
- released raw result;
- tracker failure frame;
- MRM diagnostic output.

Accepted evidence is limited to official attributes, sequence semantics and direct source-frame visual inspection independent of tracker output.

The target is at least ten complete sequence candidates with independently justified similar-distractor potential, plus enough control candidates for later matching. No interval, ambiguity label, discovery/hold-out split or frozen slice may be created in E2.

## 6. Downstream decision

After E2, Manager will decide one of:

- `E2_ACCEPTED_STAGE4A_SLICE_REVIEW_NEXT` — canonical data and coverage are sufficient, and the reproduction boundary is accepted or no longer blocks slice preparation;
- `E2_ACCEPTED_E3_REQUIRED` — data identity/coverage are addressed but Linux/platform characterization remains necessary;
- `E2_PENDING_DATA_COVERAGE` — OTB100 remains insufficient and a moderate acquisition option must be considered;
- `E2_INCOMPLETE` — integrity, extraction or execution evidence is insufficient.

No outcome automatically starts Stage 4B. A separate Manager-frozen diagnostic slice remains mandatory.

## Locked state

- Stage 4A-E2: AUTHORIZED
- Stage 4A-E3: NOT AUTHORIZED
- Stage 4B: LOCKED
- DIAG decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
