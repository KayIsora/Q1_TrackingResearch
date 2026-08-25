# Stage 4A-E — SpikeTrack external-resource probe protocol

**Date:** 2026-08-25  
**Status:** LOCKED BEFORE RESOURCE PROBE  
**Purpose:** resolve the next decision without silently downloading benchmark datasets or provisioning a new environment.

## Boundary

Stage 4A-R is `PENDING_ENVIRONMENT_OR_DATA`. Stage 4A-E begins with a metadata/resource probe only.

This stage does not:

- start Stage 4B;
- run MRM diagnostic ablations;
- freeze the distractor slice;
- assign `DIAG_PASS` or `DIAG_FAIL`;
- assign S1–S7;
- select a baseline;
- design an architecture;
- download benchmark image datasets;
- provision or rent a server.

## E1 objectives

### E1.1 Official release attribution

Determine whether the released raw predictions used in Stage 4A-R can be unambiguously mapped to:

- SpikeTrack-S256-T1;
- SpikeTrack-S256-T3;
- another configuration;
- or an unresolved release bundle.

Inspect official Google Drive and Hugging Face metadata, filenames, folder hierarchy, file IDs, sizes, checksums/LFS OIDs and any README/manifests. Compare multiple small official raw-result archives where available.

Downloading raw-result or metadata archives is permitted only when:

- no image benchmark data are included;
- each file is at most 100 MiB;
- total new transfer is at most 250 MiB;
- every file hash and source URL are recorded.

### E1.2 Dataset acquisition options

Find primary or author-recognized sources for supported datasets that could satisfy the diagnostic slice requirement, prioritizing:

1. complete OTB100;
2. TNL2K or another moderate supported RGB-SOT benchmark;
3. LaSOT test data only when the storage burden is acceptable.

For each option record:

- official/primary source;
- download structure;
- reported or discoverable compressed and extracted size;
- checksum availability;
- license/access constraints;
- expected number of plausible similar-distractor sequences based only on dataset semantics/attributes, not SpikeTrack outputs.

Do not download benchmark images in E1.

### E1.3 Existing-machine Linux feasibility

Inventory existing WSL/Docker/Linux capability and GPU visibility. Perform resolver/dry-run checks for the nearest valid official stack:

- Python 3.10 or 3.11;
- Torch 2.0.0;
- torchvision 0.15.1;
- CUDA 11.8;
- timm 0.5.4.

Do not install a new full environment in E1. Record estimated disk use and commands for a later authorized E3 run.

### E1.4 Author-contact package

Prepare but do not send a concise technical inquiry requesting:

- exact raw-result archive/config mapping;
- repository commit used for released OTB predictions;
- OTB image/ground-truth source or checksums;
- OS/Python/PyTorch/CUDA/GPU and deterministic settings.

## Decision output

E1 must produce a decision table with:

- `RAW_MAPPING_RESOLVED` / `RAW_MAPPING_UNRESOLVED`;
- candidate dataset options and required storage/transfer;
- Linux comparison feasibility and estimated setup cost;
- exact author questions.

No downstream action is automatic. Manager/User authorization is required before E2 dataset acquisition or E3 environment setup.

## Allowed artifacts

- `screening/codex/2026-08-25_stage4A_E1_resource_probe.md`
- `screening/codex/2026-08-25_stage4A_E1_official_resource_manifest.csv`
- `screening/codex/2026-08-25_stage4A_E1_dataset_options.csv`
- `screening/codex/2026-08-25_stage4A_E1_author_inquiry.md`
- small text/checksum manifests under `screening/codex/artifacts/stage4A_E1/`

No canonical matrix or reference changes are permitted.

## Locked downstream state

- Stage 4A-E1: READY
- Stage 4A-E2/E3: AWAITING USER AUTHORIZATION
- Stage 4B: LOCKED
- diagnostic decision: NOT ASSIGNED
- S1–S7: NOT STARTED
- primary shortlist: NONE
- main baseline: NONE
- proposed architecture: NONE
