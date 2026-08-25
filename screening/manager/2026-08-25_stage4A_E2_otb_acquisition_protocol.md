# Stage 4A-E2 — SpikeTrack author-attributed OTB100 acquisition protocol

**Date:** 2026-08-25  
**Status:** LOCKED BEFORE DOWNLOAD; AWAITING EXPLICIT USER AUTHORIZATION  
**Purpose:** establish one consistent OTB100 source, resolve local file identity as far as possible, expand outcome-independent diagnostic coverage, and rerun only the three predeclared reproduction sequences.

## Boundary

This protocol authorizes no transfer by itself. Execution begins only after explicit User approval.

Stage 4A-E2 does not:

- start Stage 4B;
- run per-MRM diagnostic ablations;
- inspect tracker outputs to select distractor intervals;
- freeze discovery/hold-out splits;
- install a Linux environment;
- assign `DIAG_PASS` or `DIAG_FAIL`;
- assign S1–S7;
- score, rank, shortlist, select a baseline, or design an architecture.

## 1. Fixed acquisition source

Acquire exactly one archive:

- dataset: OTB100 / OTB-2015;
- source record: `https://doi.org/10.6084/m9.figshare.24427468.v1`;
- Figshare file ID: `42879853`;
- expected display name: `OTB2015.zip`;
- expected bytes: `2,722,980,405`;
- expected provider MD5: `342b7dcb81142462b8ae9bb835cba6b4`;
- recorded provider licence: CC BY 4.0.

Do not substitute another mirror or archive in this task.

## 2. Destination contract

Use a new isolated external directory on `F:`:

`F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\`

Subdirectories:

- `archive\`
- `extracted\`
- `manifests\`
- `stage4a_e2_results\`

Do not overwrite, merge into, or delete the existing fragmented local OTB copies.

Required planning reserve: at least `6.127 GB` before transfer. Record free space before and after download/extraction.

## 3. Download and integrity

Before download record:

- resolved direct URL;
- provider file ID;
- HTTP headers where exposed;
- expected bytes;
- expected MD5;
- start time and destination.

After download verify:

1. exact byte count;
2. provider MD5;
3. independently computed SHA-256;
4. archive readability;
5. member count and top-level structure.

On any byte-count or MD5 mismatch:

- stop;
- do not extract;
- report `E2_DOWNLOAD_INTEGRITY_FAIL`.

Do not commit the archive or extracted images to GitHub.

## 4. Extraction and canonicalized layout

Extract without rewriting JPEGs or annotation files.

Record:

- extraction tool/version;
- archive-member paths;
- extracted file count;
- extracted byte total;
- sequence directory names;
- ground-truth filenames;
- any layout differences from the pinned SpikeTrack `OTBDataset` contract.

Create a temporary external evaluator-compatible OTB root only through copies, directory junctions, or symlinks that do not alter source bytes.

## 5. Hash comparison

For every sequence that exists in both the acquired package and the current workspace, compare:

- number of official-range frames;
- raw image SHA-256;
- decoded BGR SHA-256;
- decoded RGB SHA-256;
- raw ground-truth SHA-256;
- normalized parsed ground-truth SHA-256.

At minimum, complete this for:

- Deer;
- Crossing;
- Couple;
- Bolt;
- Jogging_1;
- MotorRolling.

Classify each sequence:

- `BYTE_IDENTICAL_TO_ACQUIRED`;
- `PIXEL_IDENTICAL_GT_IDENTICAL`;
- `IMAGE_DIFFERENT_GT_IDENTICAL`;
- `IMAGE_IDENTICAL_GT_DIFFERENT`;
- `DIFFERENT`;
- `NO_EXISTING_COMPARISON`.

Do not select a source copy based on tracker accuracy.

## 6. Three-sequence reproduction rerun

Use only the acquired OTB package for:

- Deer;
- Crossing;
- Couple.

Use:

- pinned source commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`;
- exact `spiketrack_s256_t1.yaml`;
- checkpoint SHA-256 `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`;
- official `tracking/test.py -> Tracker.run_sequence` path;
- Windows environment already characterized in Stage 4A-R.

Run:

- one official-default execution per sequence;
- one deterministic execution per sequence.

No full OTB benchmark is permitted.

Compare against:

- previously committed local official-runner outputs;
- author-released S256-T1 raw predictions;
- acquired-source ground truth.

Report:

- prediction SHA-256;
- Success AUC;
- difference from released AUC;
- first prediction divergence;
- whether acquired data changes local predictions.

## 7. Reproduction interpretation states

Allowed E2 reproduction labels:

### `E2_DATA_IDENTITY_EXPLAINS_MISMATCH`

The acquired package differs from prior local bytes and the acquired-source official run materially moves toward or exactly reproduces released output.

### `E2_DATA_IDENTITY_NOT_CAUSE`

The acquired package is byte/pixel/GT-identical to prior local inputs, or the acquired-source run remains byte-identical to the prior local run and still differs from released output.

### `E2_REPRODUCTION_PENDING`

Execution or package-layout evidence is insufficient.

Do not assign the final Stage-4 reproduction acceptance state; Manager reconciliation decides whether E3 is needed.

## 8. Outcome-independent inventory expansion

Review the complete acquired OTB package without consulting:

- SpikeTrack predictions;
- raw-result accuracy;
- score maps;
- failure frames;
- MRM diagnostics.

Use only:

- official sequence metadata and attributes;
- object class/sequence semantics;
- direct source-frame visual inspection.

Create candidate sequence records for similar-distractor review.

A candidate reason must identify visible or semantically supported non-target similarity. Blank reasons remain blank.

Do not yet:

- choose final frame intervals;
- assign ambiguity levels;
- create discovery/hold-out splits;
- freeze the diagnostic slice.

Target evidence:

- at least ten complete sequence candidates with independently justified similar-distractor potential;
- enough additional control candidates to support later matching.

If fewer than ten are found, report `OTB_COVERAGE_INSUFFICIENT` and recommend—but do not download—the smallest next dataset option.

## 9. Required external artifacts

Under the external `manifests` and result directories preserve:

- download headers/log;
- archive MD5/SHA-256;
- archive member manifest;
- extracted file manifest;
- free-space report;
- sequence hash comparison;
- official-runner predictions;
- reproduction metrics;
- candidate-inventory working notes.

Do not commit image data or the archive.

## 10. Required Q1 repository artifacts

Create only small text files:

- `screening/codex/2026-08-25_stage4A_E2_otb_acquisition_report.md`
- `screening/codex/2026-08-25_stage4A_E2_otb_source_manifest.csv`
- `screening/codex/2026-08-25_stage4A_E2_otb_hash_comparison.csv`
- `screening/codex/2026-08-25_stage4A_E2_reproduction.csv`
- `screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv`
- optional small command/checksum manifests under `screening/codex/artifacts/stage4A_E2/`.

Do not modify:

- canonical candidate matrix;
- references;
- Manager/reconciliation files;
- existing Stage-4 artifacts;
- rules or documentation.

## 11. Validation

Before completion verify:

- exact Figshare file ID and byte count;
- MD5 equals `342b7dcb81142462b8ae9bb835cba6b4`;
- SHA-256 recorded;
- no source JPEG/GT mutation;
- three-sequence official rerun uses acquired package only;
- no full benchmark run;
- no tracker-output-based sequence selection;
- no diagnostic interval or split frozen;
- no MRM ablation campaign;
- no score, shortlist, baseline or architecture decision.

## 12. E2 output states

Report:

- download: `PASS` / `FAIL`;
- integrity: `PASS` / `FAIL`;
- extracted layout: `READY` / `BLOCKED`;
- dataset identity: `ESTABLISHED` / `PARTIAL` / `UNRESOLVED`;
- reproduction: one E2 label from Section 7;
- candidate inventory: `SUFFICIENT` / `INSUFFICIENT`;
- Stage 4A-E2: `COMPLETE_FOR_MANAGER_REVIEW` / `INCOMPLETE`.

Then stop.

## 13. Locked downstream state

- execution: `AWAITING_USER_AUTHORIZATION`
- Stage 4A-E3: `DEFERRED_PENDING_E2_REVIEW`
- Stage 4B: `LOCKED`
- diagnostic decision: `NOT_ASSIGNED`
- S1–S7: `NOT_STARTED`
- primary shortlist: `NONE`
- main baseline: `NONE`
- proposed architecture: `NONE`
