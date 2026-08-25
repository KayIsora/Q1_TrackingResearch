# SpikeTrack Stage 4A-E1 external-resource probe

**Date:** 2026-08-25
**Candidate:** CX007 SpikeTrack
**Pinned source:** `faicaiwawa/SpikeTrack` at `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`
**Scope:** official release attribution, bounded raw-result comparison, canonical dataset acquisition options, existing-machine Linux feasibility, and an unsent author inquiry
**Conclusion:** `STAGE4A_E1_COMPLETE`

This metadata/resource probe did not download benchmark images, install an environment, rerun the neural tracker, run Stage 4B, execute MRM ablations, select or freeze diagnostic intervals, assign `DIAG_PASS`/`DIAG_FAIL`, assign S1-S7, score or rank a candidate, form a shortlist, select a baseline, or propose an architecture.

## 1. Governing evidence and source boundary

The Q1 repository was synchronized cleanly to Manager activation commit `36c23f5` before the probe. The Stage 4A-R reconciliation retains `REPRO_UNRESOLVED` and `STAGE4A_R_PENDING_ENVIRONMENT_OR_DATA`; the accepted source, checkpoint, local-run, adapter/official-runner, and instrumentation evidence was not modified.

The external attribution chain was restricted to author-controlled or author-linked resources:

- the [pinned SpikeTrack readme](https://github.com/faicaiwawa/SpikeTrack/blob/1537db51a1cc9f6e30cce469fba3e51f5721b3d0/readme.md), which links the release Drive and the `facaiwawa/SpikeTrack` Hugging Face repository;
- the author-linked [Google Drive release root](https://drive.google.com/drive/folders/1G9DhjfhmiRz_9JxxlbHbOnuYZBAmhLOG), including its `model_weight` and `raw_results` children;
- the author-linked [Hugging Face model repository](https://huggingface.co/facaiwawa/SpikeTrack/tree/b234055d3afd766e1b37f309bf2878dba247aa10);
- the official [SpikeTrack paper record](https://arxiv.org/abs/2602.23963).

All web resources in this report were accessed on 2026-08-25. Exact IDs, names, sizes, timestamps, stable URLs, hashes/LFS OIDs, variant labels, and evidence sources are recorded in `2026-08-25_stage4A_E1_official_resource_manifest.csv`.

## 2. Official checkpoint and configuration attribution

The pinned repository contains exact S256-T1 and S256-T3 configuration files. The author-linked Drive and Hugging Face repositories independently expose matching variant-named checkpoints.

| Variant | Pinned config | Checkpoint bytes | SHA-256 / LFS OID | Status |
|---|---|---:|---|---|
| S256-T1 | `experiments/spiketrack/spiketrack_s256_t1.yaml` | 47,912,371 | `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df` | `S256_T1_CONFIRMED` |
| S256-T3 | `experiments/spiketrack/spiketrack_s256_t3.yaml` | 51,865,011 | `ccf04aa90521b21a78b12f4b978c03d8a69b5f6de3ee3498a3594e13e98aa491` | `S256_T3_CONFIRMED` |

The Hugging Face LFS OIDs equal the already resolved local checkpoint SHA-256 values. No checkpoint was downloaded in E1.

## 3. Official raw-result attribution

The pinned README links the public Drive root. That root contains a child folder named `raw_results` with ID `1HNd8EdpHLf3Ly1leuDVQDOBsDg3uaSsq`. The folder publicly lists six variant-named ZIPs:

| Official archive | Drive file ID | Bytes | Variant label |
|---|---|---:|---|
| `spiketrack_b256_t1.zip` | `1mMY05kMEeWY_rGHlGkQOKRXTTy7UpKm6` | 17,396,075 | `OTHER_VARIANT_CONFIRMED` |
| `spiketrack_b256_t3.zip` | `1Ghv_94IPAJzjjn2PtOIGsC6v8HuixQ_z` | 17,876,961 | `OTHER_VARIANT_CONFIRMED` |
| `spiketrack_b384_t1.zip` | `1MrjAyf3uVrj1KdX6d0wnpCsECQZ6OKWf` | 17,678,354 | `OTHER_VARIANT_CONFIRMED` |
| `spiketrack_b384_t3.zip` | `1Hf5CHN3WbBGBxQnmQ2kgU2fkRPPRUDVN` | 17,430,510 | `OTHER_VARIANT_CONFIRMED` |
| `spiketrack_s256_t1.zip` | `1QAST-IzBr2rhAteZq_vc0GZszinIOxbD` | 15,632,995 | `S256_T1_CONFIRMED` |
| `spiketrack_s256_t3.zip` | `1J3i1ViwIHuHBieUPhnuMeVn_gPXjaYgP` | 17,958,764 | `S256_T3_CONFIRMED` |

The prior archive lead, file ID `1QAST-IzBr2rhAteZq_vc0GZszinIOxbD`, is therefore unambiguously the author-released `spiketrack_s256_t1.zip`. Its existing local bytes remain 15,632,995 with SHA-256 `7e9f8e40d069f73a7b33edfc9593946af478caa3206670847ebde78cbc545c25`. This attribution comes from the author-linked parent hierarchy and public filename, not from prediction accuracy.

## 4. Bounded transfer and archive inventory

The existing S256-T1 ZIP was reused. The other five official raw-result ZIPs were downloaded temporarily for metadata and text comparison:

- new transfer: 88,340,664 bytes (84.248 MiB);
- largest individual file: 17,958,764 bytes;
- six archives inspected: 103,973,659 bytes total;
- image/video members: 0;
- data files: 24,528 text raw-result files, comprising 12,264 prediction files and 12,264 `_time.txt` timing files;
- committed ZIP archives: 0.

Each download was below 100 MiB and the total new transfer was below 250 MiB. The temporary ZIPs are excluded from the Q1 repository. `raw_archive_inventory.csv`, `transfer_log.csv`, and three complete unique member lists preserve the source URLs, IDs, sizes, timestamps, hashes, member counts, and internal paths. No dataset image, checkpoint, or other large binary was downloaded.

## 5. Three-sequence raw-result comparison

For every official archive, `raw_three_sequence_evidence.csv` records the exact internal member path, row count, first five rows, last row, raw byte size, text SHA-256, line ending, and coordinate format for Deer, Crossing, and Couple. All required members are present with 71, 120, and 140 rows respectively.

The most relevant comparison is:

| Sequence | Official S256-T1 text SHA-256 | Official S256-T3 text SHA-256 | Existing local T1 SHA-256 | S256-T1 vs local first difference | S256-T1 vs S256-T3 first difference |
|---|---|---|---|---:|---:|
| Deer | `ad1f83563b33df88524358c5d5e2f6bf7eb59c6d90b083a95ad6d8a5bbd618c7` | `cd19199ffd72778640edeb6e6474dc6f03faa094e4bcb2c77b1d357f36ae2aa4` | `88a49dcd23393584e5b7a42061a9a3b89dcb851ae308694a130b3f24e54fdf5d` | 2 | 2 |
| Crossing | `db3a37edc91171fc1572533c89ee879f33e2e19851039a7f7ac59e7548458aff` | `634fdc7c4de41726b3eae42fa459033358229d4fd1469067eb3747a79e18d7a6` | `039d9ca96e1ecf9f0714c88337e4eebd826e2cb78842984e33c5de775f28f65f` | 2 | 2 |
| Couple | `37307157d9ff3f30b83bfe96c362bfe66ccbccc5dad00c97ad64e77d3537ad34` | `58f9428093a10ddac66efe43da0b6c0cc4dfc70818e4975e882e9f680efe3ca1` | `ced31cb5af587bbe069415163ef0d9a3d47779e5b116e4f619b5a0b80b7efe38` | 2 | 2 |

The exhaustive `raw_pairwise_comparison.csv` contains 45 official-to-official and 108 official-to-existing-local-T1 rows. Every comparison is unequal. Official pairs first differ at frame 2 except Couple B256-T1 versus B384-T1 and Crossing B384-T3 versus S256-T3, which first differ at frame 3. All six official archives differ from the identical local T1 prediction sets.

Prediction differences were used only to describe file identity. They were not used to infer which variant generated an archive and were not evaluated against ground truth to choose a mapping.

## 6. Raw-mapping decision

`RAW_MAPPING_RESOLVED`

The author-controlled metadata chain resolves the prior raw archive as S256-T1 and separately identifies the S256-T3 archive. The six official archives' mutually different outputs are consistent with distinct released variant files, but the decision does not depend on that similarity evidence.

This mapping decision does **not** resolve the numerical reproduction mismatch. The local official runner still differs from the now-confirmed official S256-T1 output, while the authors' exact commit, OTB source/checksums, OS, GPU, Python, PyTorch, CUDA/cuDNN, and deterministic settings for that release remain unknown.

## 7. Canonical dataset options

The pinned evaluator directly supports `otb`, `uav`, `tnl2k`, and `lasot`. No benchmark payload was downloaded. Source sizes and access constraints were taken from primary/official or author-attributed records, independent of SpikeTrack predictions.

| Option | Official/primary evidence | Transfer | Sequences | Checksum/access | Outcome-independent diagnostic basis |
|---|---|---:|---:|---|---|
| OTB100 | [author-attributed Figshare record](https://doi.org/10.6084/m9.figshare.24427468.v1) and [pinned evaluator](https://github.com/faicaiwawa/SpikeTrack/blob/1537db51a1cc9f6e30cce469fba3e51f5721b3d0/lib/test/evaluation/otbdataset.py) | 2,722,980,405 bytes | 100 evaluator entries | MD5 `342b7dcb81142462b8ae9bb835cba6b4`; CC BY 4.0 | 11 official challenge attributes including background clutter and occlusion; person/animal/vehicle semantics |
| UAV123 | [official KAUST IVUL page](https://ivul.kaust.edu.sa/benchmark-and-simulator-uav-tracking-dataset) and [pinned evaluator](https://github.com/faicaiwawa/SpikeTrack/blob/1537db51a1cc9f6e30cce469fba3e51f5721b3d0/lib/test/evaluation/uavdataset.py) | approximately 13.7 GB | 123 | checksum and explicit standard licence not exposed | official `SOB` Similar Object attribute plus background clutter and occlusion attributes |
| TNL2K test | [author toolkit](https://github.com/wangxiao5791509/TNL2K_evaluation_toolkit/blob/1a96f6eb1fcf59afc3978f5714e22c75c02e9fb4/README.md#how-to-download-tnl2k-dataset), [CVPR paper](https://openaccess.thecvf.com/content/CVPR2021/html/Wang_Towards_More_Flexible_and_Accurate_Object_Tracking_With_Natural_Language_CVPR_2021_paper.html), and [pinned evaluator](https://github.com/faicaiwawa/SpikeTrack/blob/1537db51a1cc9f6e30cce469fba3e51f5721b3d0/lib/test/evaluation/tnl2kdataset.py) | 282,701,995,360 bytes | 700 test | 34 split ZIP parts; archive checksums/licence not exposed | dense boxes and language descriptions; author-declared adversarial and modality-switch contexts |
| LaSOT test | [official download page](http://vision.cs.stonybrook.edu/~lasot/download.html), [CVPR paper](https://openaccess.thecvf.com/content_CVPR_2019/html/Fan_LaSOT_A_High-Quality_Benchmark_for_Large-Scale_Single_Object_Tracking_CVPR_2019_paper.html), and [pinned evaluator](https://github.com/faicaiwawa/SpikeTrack/blob/1537db51a1cc9f6e30cce469fba3e51f5721b3d0/lib/test/evaluation/lasotdataset.py) | 50,001,606,775 bytes | 280 test | MD5 `a9038384fd94d30e7ad6a1b7cf32ec73`; personal/academic/educational-use terms | long sequences, 70 categories, background clutter and partial/full occlusion attributes |

Exact uncompressed sizes were not exposed by the inspected providers. The complete 17-column inventory, download structure, annotations, attributes, checksum and licence limits, evaluator compatibility, confidence, and storage decision are in `2026-08-25_stage4A_E1_dataset_options.csv`.

## 8. Storage and acquisition choices

The storage snapshot is:

| Target | Reported free bytes | Interpretation |
|---|---:|---|
| Windows C: | 64,963,244,032 | also physically backs the Ubuntu WSL VHDX |
| Windows E: | 42,526,715,904 | sufficient for minimal/moderate planning only, with limited remaining headroom after moderate |
| Windows F: | 984,562,270,208 | preferred large-data target |
| WSL ext4 logical filesystem | 1,023,223,029,760 | logical free space only; effective growth is bounded by C: host free space |

The WSL logical filesystem must not be treated as an independent 1-TB physical store because its VHDX resides on C:.

| Acquisition choice | Contents | Estimated transfer | Planning storage reserve | Current sufficiency |
|---|---|---:|---:|---|
| `E1-ACQ-MINIMAL` | complete OTB100 | 2.723 GB | 6.127 GB | C:/E:/F:/WSL fit; F: preferred |
| `E1-ACQ-MODERATE` | OTB100 + UAV123 | approximately 16.423 GB | approximately 36.952 GB | C:/E:/F:/WSL fit; F: preferred to preserve headroom |
| `E1-ACQ-FULL` | OTB100 + UAV123 + TNL2K test + LaSOT test | approximately 349.127 GB | approximately 785.535 GB | conditional on F: only; exact extracted sizes remain unknown |

The planning reserve is archive size plus an equal-size extraction proxy plus a 25% transfer margin. It is explicitly not a measured uncompressed size.

`E1-ACQ-MINIMAL` is preferred because it is the smallest author-attributed package that can establish canonical OTB identity, complete the current partial OTB holding, and expand outcome-independent review before any broader acquisition. If independent review still cannot meet the locked coverage minimum, `E1-ACQ-MODERATE` adds UAV123's official Similar Object attribute without the much larger TNL2K or LaSOT transfer.

## 9. WSL/Linux feasibility

Read-only inventory and resolver evidence are preserved under `artifacts/stage4A_E1/linux_feasibility/`.

| Item | Observed result |
|---|---|
| WSL | 2.4.13.0; default WSL 2 |
| Distribution/kernel | Ubuntu 24.04.3 LTS; `5.15.167.4-microsoft-standard-WSL2` |
| GPU | NVIDIA GeForce MX250 visible through `/dev/dxg` and `nvidia-smi`; compute capability 6.1; 2,048 MiB |
| Driver | 581.83; `nvidia-smi` reports CUDA driver capability 13.0, not an installed Linux toolkit |
| Python | 3.12.3 only; no Python 3.10/3.11 executable |
| Environment tools | no pip, Conda, Mamba, Micromamba, uv, virtualenv, or Linux Torch stack |
| Docker | client 29.3.1 visible; daemon unavailable and `docker-desktop` stopped |
| Storage | WSL ext4 logically has about 953 GiB free; C: backing volume has about 60.5 GiB free |

The official CUDA 11.8 indexes expose exact Linux x86-64 wheels for `torch==2.0.0+cu118` and `torchvision==0.15.1+cu118` on CPython 3.10 and 3.11. They expose no compatible CPython 3.12 wheels for those pinned versions. `timm==0.5.4` is a universal Python wheel, but it cannot make the pinned Torch/Torchvision pair compatible with Python 3.12. Evidence comes from the official [Torch CUDA 11.8 index](https://download.pytorch.org/whl/cu118/torch/), [Torchvision CUDA 11.8 index](https://download.pytorch.org/whl/cu118/torchvision/), and [timm 0.5.4 metadata](https://pypi.org/pypi/timm/0.5.4/json).

The nearest setup target is an isolated Miniforge environment with Python 3.11.7, Torch 2.0.0+cu118, Torchvision 0.15.1+cu118, timm 0.5.4, Ubuntu `libturbojpeg`, `jpeg4py==0.1.4`, `lmdb==1.7.3`, and `matplotlib==3.11.1`. These include the unconditional import-time requirements found by the pinned-source closure audit. Exact future-only commands and validation assertions are in `future_setup_commands.md`.

- directly inspected core payload floor: 2.276 GiB;
- planning transfer: 2.6-3.1 GiB;
- installed/cache/output budget: 7-10 GiB;
- setup and import/GPU validation estimate: 30-90 minutes;
- three-sequence WSL runtime: `UNKNOWN` until an authorized E3 measurement.

The same 2-GiB MX250 successfully supported the bounded Windows characterization, and WSL exposes it at the driver/device level. A Linux run is therefore technically plausible on existing hardware, but the stack and CUDA allocation remain untested in WSL and the VRAM margin is small.

**Linux feasibility: `LINUX_RUN_FEASIBLE_BUT_SETUP_REQUIRED`.**

No package, environment, CUDA toolkit, container, or server was installed or provisioned, and the tracker was not executed in E1.

## 10. Author inquiry

`2026-08-25_stage4A_E1_author_inquiry.md` is `READY` and was not sent. It neutrally asks the authors for exactly the ten requested facts: the S256-T1 OTB archive, source commit, OTB source/checksums, OS, GPU, Python, PyTorch, CUDA/cuDNN, deterministic settings, and exact T1/T3/other configuration.

## 11. Residual blockers and interpretation

| Item | E1 result | Remaining action |
|---|---|---|
| Released raw-result/config attribution | resolved as official S256-T1 | no mapping action; retain the separate reproduction mismatch |
| Canonical OTB image/GT identity | source, size, checksum, and licence option identified; bytes not acquired | requires Package A authorization and E2 acquisition/hash comparison |
| Linux official-stack comparison | feasible on existing hardware but no valid stack installed/run | requires Package B authorization and E3 setup/rerun |
| Diagnostic dataset coverage | acquisition choices identified; current local coverage remains insufficient | acquire minimal OTB first, then perform independent review; do not inspect tracker outputs for selection |
| Author runtime/source details | inquiry ready but not sent | Manager/User decides whether and how to contact authors |

`RAW_MAPPING_RESOLVED` is a release-provenance result, not a reproduction pass and not a diagnostic result. `REPRO_UNRESOLVED` remains unchanged pending canonical-data and/or Linux/author-environment evidence.

## 12. Files produced

- `screening/codex/2026-08-25_stage4A_E1_resource_probe.md`
- `screening/codex/2026-08-25_stage4A_E1_official_resource_manifest.csv`
- `screening/codex/2026-08-25_stage4A_E1_dataset_options.csv`
- `screening/codex/2026-08-25_stage4A_E1_author_inquiry.md`
- small metadata, member-list, comparison, storage, resolver, and future-command evidence under `screening/codex/artifacts/stage4A_E1/`

No downloaded raw-result ZIP, benchmark image, checkpoint, environment, or other large binary is included.

## 13. Stage boundary

**Stage 4A-E1: `COMPLETE`.**

- Stage 4A-E2/E3: `AWAITING USER AUTHORIZATION`
- Stage 4B: `LOCKED`
- diagnostic decision: `NOT ASSIGNED`
- S1-S7: `NOT STARTED`
- primary shortlist: `NONE`
- main baseline: `NONE`
- proposed architecture: `NONE`

## 14. Decision table

| Decision | Result |
|---|---|
| Raw result mapping | `RAW_MAPPING_RESOLVED` |
| Preferred dataset acquisition | `E1-ACQ-MINIMAL` — complete author-attributed OTB100 first, because it is the smallest option that addresses canonical identity and current coverage |
| Minimum estimated transfer | 2,722,980,405 bytes (2.723 GB / 2.536 GiB) |
| Minimum estimated storage | 6.127 GB planning reserve; exact extracted size remains unknown |
| Linux comparison | `LINUX_RUN_FEASIBLE_BUT_SETUP_REQUIRED` |
| Author inquiry | `READY` — prepared, not sent |

## PACKAGE A — dataset acquisition

**Status:** `AWAITING USER AUTHORIZATION`; do not execute automatically.

Authorize Stage 4A-E2 to download only Figshare file ID `42879853` from `https://doi.org/10.6084/m9.figshare.24427468.v1` to a predeclared directory on F:, with expected transfer 2,722,980,405 bytes and a 6.127-GB planning reserve. Verify provider MD5 `342b7dcb81142462b8ae9bb835cba6b4` and calculate SHA-256 before extraction; preserve the archive/source manifest; calculate image and GT hashes; compare the three existing sequence copies against the acquired source; then expand the candidate inventory using official attributes, sequence semantics, or direct visual inspection only. Do not use SpikeTrack predictions, scores, or failure frames, and do not freeze intervals or splits.

## PACKAGE B — Linux environment setup and three-sequence rerun

**Status:** `AWAITING USER AUTHORIZATION`; do not execute automatically.

Authorize Stage 4A-E3 to use the existing Ubuntu WSL2 distribution and MX250 only. Install the isolated, pinned Python 3.11.7/CUDA-11.8 PyTorch stack exactly as recorded in `artifacts/stage4A_E1/linux_feasibility/future_setup_commands.md`; expected transfer is 2.6-3.1 GiB, installed/cache/output budget is 7-10 GiB, and setup/validation time is estimated at 30-90 minutes. Validate imports, versions, GPU visibility, and allocation before copying the exact pinned source/config/checkpoint contract. If validation passes, rerun only Deer, Crossing, and Couple through the official evaluator and preserve raw outputs/environment evidence. Stop on dependency, CUDA, or VRAM failure; do not modify the scientific model, run a full benchmark, or start Stage 4B.
