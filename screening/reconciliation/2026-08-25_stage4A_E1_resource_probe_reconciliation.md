# Stage 4A-E1 — SpikeTrack external-resource probe reconciliation

**Date:** 2026-08-25  
**Status:** E1 COMPLETE; E2 dataset acquisition recommended but awaiting explicit User authorization.  
**Inputs:**

- `screening/codex/2026-08-25_stage4A_E1_resource_probe.md`
- `screening/codex/2026-08-25_stage4A_E1_official_resource_manifest.csv`
- `screening/codex/2026-08-25_stage4A_E1_dataset_options.csv`
- `screening/codex/2026-08-25_stage4A_E1_author_inquiry.md`
- small manifests under `screening/codex/artifacts/stage4A_E1/`
- `screening/reconciliation/2026-08-25_stage4A_R_spiketrack_resolution_reconciliation.md`
- `screening/manager/2026-08-25_stage4A_E_resource_probe_protocol.md`

## Boundary

This reconciliation reviews metadata/resource evidence only. It does not authorize a benchmark-image download, install a Linux environment, start Stage 4B, freeze a diagnostic slice, assign `DIAG_PASS`/`DIAG_FAIL`, assign S1–S7, create a shortlist, select a baseline, or approve an architecture.

## Accepted E1 evidence

### 1. Official raw-result mapping is resolved

The author-linked Google Drive release hierarchy contains a `raw_results` folder with six variant-named archives. File ID `1QAST-IzBr2rhAteZq_vc0GZszinIOxbD` is publicly named `spiketrack_s256_t1.zip` under that author-controlled hierarchy.

The previously used archive therefore maps unambiguously to:

`SpikeTrack-S256-T1`.

The mapping is based on author-controlled filename and parent hierarchy, not on prediction accuracy. The corresponding S256-T1 checkpoint is independently identified by the exact Drive filename and matching Hugging Face LFS SHA-256.

**Accepted mapping state:** `RAW_MAPPING_RESOLVED`.

### 2. Reproduction mismatch remains unresolved

Resolving the archive identity removes the possibility that the project accidentally compared the local S256-T1 run with an unnamed or different released variant. It does not resolve the numerical mismatch.

The local official runner remains byte-identical to the preserved adapter and repeatable across local default/deterministic modes, but differs from the now-confirmed official S256-T1 raw output on Deer and Couple.

The remaining unknowns are:

- exact author-side source commit used for the raw run;
- exact OTB package/image and annotation bytes;
- author OS/GPU/Python/PyTorch/CUDA/cuDNN stack;
- author deterministic/runtime settings.

The reproduction state remains:

`REPRO_UNRESOLVED`.

This is not a scientific failure of SpikeTrack.

### 3. Dataset-option inventory is accepted

The preferred first acquisition is the author-attributed OTB100 Figshare package:

- DOI record: `https://doi.org/10.6084/m9.figshare.24427468.v1`;
- Figshare file ID: `42879853`;
- expected archive bytes: `2,722,980,405`;
- provider MD5: `342b7dcb81142462b8ae9bb835cba6b4`;
- licence recorded by the provider: CC BY 4.0;
- planning reserve: approximately `6.127 GB`;
- recommended storage target: Windows `F:`.

This acquisition is preferred because it is the smallest option that simultaneously addresses:

1. canonical/author-attributed OTB identity;
2. completion of the current fragmented OTB holding;
3. expansion of the outcome-independent similar-distractor inventory;
4. rerunning the same predeclared Deer/Crossing/Couple reproduction check on one consistent package.

UAV123 is retained as a conditional second acquisition because its official `SOB` Similar Object attribute is highly relevant, but its approximately 13.7-GB transfer is unnecessary until the complete OTB package has been reviewed.

TNL2K and LaSOT are not authorized at this checkpoint because their transfer/storage cost is much larger than the immediate evidence need.

### 4. Linux feasibility is accepted as setup-required

The existing Ubuntu WSL2 installation exposes the current MX250 GPU. A compatible Python 3.11 plus Torch 2.0.0/CUDA-11.8 environment is feasible without new hardware, but it requires a new isolated setup with an estimated 2.6–3.1-GiB transfer and 7–10-GiB local budget.

The README's Python 3.12 request is not directly compatible with the pinned Torch 2.0.0 wheel contract. No environment was installed in E1.

**Accepted state:** `LINUX_RUN_FEASIBLE_BUT_SETUP_REQUIRED`.

### 5. Author inquiry

The inquiry is technically usable, but raw archive/config questions 1 and 10 are now answered by author-controlled release metadata. Before sending, the message should be narrowed to the unresolved items:

- exact source commit;
- OTB source/version or checksums;
- OS/GPU/Python/PyTorch/CUDA/cuDNN;
- deterministic settings.

No inquiry is sent by this reconciliation.

## Sequencing decision

**PROJECT DECISION — locked sequential resource use:**

1. Run `Stage 4A-E2` first using only the complete author-attributed OTB100 package.
2. Compare the canonical acquired Deer/Crossing/Couple files with all existing local copies by raw/decoded/GT hashes.
3. Rerun only the same three predeclared sequences through the official Windows runner.
4. Expand the outcome-independent OTB candidate inventory.
5. Review E2 before authorizing `Stage 4A-E3` Linux setup.

Rationale: E2 is required for diagnostic data coverage regardless of whether a Linux rerun is later useful. If the acquired OTB bytes explain the prediction mismatch, E3 may be unnecessary. If they do not, E3 becomes the next bounded platform-characterization step.

## Resource authorization boundary

The Manager recommends **Package A / E2 only** at this checkpoint:

- transfer approximately 2.723 GB;
- planning reserve approximately 6.127 GB;
- destination on `F:`;
- exact MD5 verification before extraction;
- no tracker-output-based sequence selection;
- no Stage 4B run.

Execution still requires explicit User authorization.

Package B / E3 Linux setup remains deferred until E2 reconciliation.

## Decision

**Stage 4A-E1 final state: COMPLETE.**

**Next state:** `STAGE4A_E2_AWAITING_USER_AUTHORIZATION`.

## Locked downstream state

- Stage 4A-E2 OTB acquisition: `AWAITING_USER_AUTHORIZATION`
- Stage 4A-E3 Linux comparison: `DEFERRED_PENDING_E2_REVIEW`
- Stage 4A-E4 inventory expansion: `LOCKED_TO_E2`
- Stage 4B: `LOCKED`
- diagnostic decision: `NOT_ASSIGNED`
- S1–S7: `NOT_STARTED`
- primary shortlist: `NONE`
- main baseline: `NONE`
- proposed architecture: `NONE`
