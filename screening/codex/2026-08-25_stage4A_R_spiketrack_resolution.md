# SpikeTrack Stage 4A-R preflight repair and reproduction resolution

**Date:** 2026-08-25
**Candidate:** CX007 SpikeTrack
**Scope:** R1 evidence preservation, R2 three-sequence official-runner comparison, R3 retrieval-specific instrumentation repair, and R4 outcome-independent local inventory only
**Stage 4A-R conclusion:** `STAGE4A_R_PENDING_ENVIRONMENT_OR_DATA`

This report does not run Stage 4B, freeze a diagnostic slice, assign `DIAG_PASS` or `DIAG_FAIL`, assign S1-S7, score or rank a candidate, form a shortlist, select a baseline, or propose an architecture.

## 1. Exact previous-adapter preservation status

**FACT — local file identity:** the extant script associated with the prior definitive Stage-4A bounded adapter run still existed at `E:\Robot_Backup\tmp\stage4a_bounded_repro.py`. It is preserved byte-for-byte as `screening/codex/artifacts/stage4A_reproduction/previous_adapter_exact.py`.

| Item | SHA-256 | Status |
|---|---|---|
| Previous temporary source | `7106a80bb6e015e653e2caae1438fbd7abefd3116ac00c4e114a7e1b83e2ef63` | found |
| Committed exact preservation copy | `7106a80bb6e015e653e2caae1438fbd7abefd3116ac00c4e114a7e1b83e2ef63` | byte-identical |

**Previous adapter: `PRESERVED`.**

The source-to-old-run association is strongly corroborated by filesystem timestamp order, the sequence/output paths embedded in the old run JSON, and identical old/new metric and prediction hashes. It is not cryptographically attested because the old run JSON did not embed its executing script hash; that limitation is retained in `manifest.json` rather than silently upgraded to certainty.

The required `screening/codex/scripts/2026-08-25_stage4A_spiketrack_reproduce3.py` is explicitly labeled `NEW AUDITABLE ADAPTER EXTENSION`; it is not presented as the exact old source. It retains the fixed three-sequence tracking, BGR-to-RGB loading, initialization, frame loop, integer persistence, and metric logic, while exposing `--runtime-mode {deterministic,default}`. It also declares the prior adapter's information contract: initialization receives `init_bbox`; each subsequent direct call receives an empty information dictionary; `previous_output` is not propagated. The official-runner comparison below tests the consequence of that difference directly.

## 2. Reproduction artifact inventory

`screening/codex/artifacts/stage4A_reproduction/` contains the required text evidence:

- `manifest.json`, `commands.txt`, and `environment.json`;
- `raw_archive_manifest.csv`, `sequence_copy_manifest.csv`, `frame_hashes.csv`, `ground_truth_hashes.csv`, `metrics.csv`, and `first_divergence.csv`;
- the exact old adapter source and old run JSON noted above, plus byte-preserved old predictions in `previous_adapter_preserved/`;
- six prediction directories: `released_raw`, `adapter_deterministic`, `official_runner_deterministic`, and `official_runner_default_run1` through `official_runner_default_run3`, each containing only the three requested prediction text files `Deer.txt`, `Crossing.txt`, and `Couple.txt`.

Small audit helpers, the exact temporary official-runner `local.py` and deterministic bootstrap, image-loader parity/runtime summaries, and the bounded mini-root setup errors are also preserved as text so the command record has no dangling dependency on temporary files.

The artifact manifest records file hashes and provenance. A directory-local `.gitattributes` disables line-ending filters so Git stores every audited artifact byte-for-byte; filtered and raw Git blob inputs match for all 41 files. No image, video, checkpoint, raw-result ZIP, tensor, Python bytecode, or other binary payload is committed.

## 3. Dataset-copy/hash comparison

The predeclared sources remained Deer (71 frames), Crossing (120), and Couple (140). Copy selection used evaluator range, image/annotation completeness, annotation consistency, and file/pixel identity only—not tracker accuracy or released-result closeness.

| Sequence | Reasonable local copies audited | Raw/decoded identity | Ground-truth identity | Upstream canonical provenance |
|---|---:|---|---|---|
| Deer | 4 | all official-range frame files byte-identical; decoded BGR and RGB hashes agree | normalized parsed values identical | not established |
| Crossing | 2 | all official-range frame files byte-identical; decoded BGR and RGB hashes agree | normalized parsed values identical | not established |
| Couple | 2 | all official-range frame files byte-identical; decoded BGR and RGB hashes agree | normalized parsed values identical | not established |

For every frame in every audited copy, `frame_hashes.csv` records 1,135 rows spanning 331 unique sequence/frame identities: absolute source path, source-copy identifier, raw SHA-256, dimensions, decoded BGR SHA-256, decoded RGB SHA-256, and the official `Tracker._read_image` RGB comparison. Adapter and official-loader decoded RGB values are identical for every audited frame copy. `ground_truth_hashes.csv` records raw and normalized hashes, row counts, and first/last boxes for each of the 11 audited annotation copies.

The local copies establish repeatable workspace identity, but no canonical official OTB100 archive/checksum was available. **Dataset identity: `PARTIAL`.**

## 4. Official runner versus adapter

The source was an isolated `faicaiwawa/SpikeTrack` worktree at pinned commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`, with no tracked modifications, exact config `experiments/spiketrack/spiketrack_s256_t1.yaml`, and checkpoint SHA-256 `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`. The only worktree addition was the required untracked temporary `lib/test/evaluation/local.py`, preserved in the text artifacts.

A temporary external OTB mini-root contained the three real sequences. Metadata-only annotation stubs for non-target OTB entries were required because the pinned loader eagerly parses its 100-sequence declaration before applying `--sequence`; the stubs were never executed, evaluated, or committed. A temporary external `lib/test/evaluation/local.py` pointed the official evaluator and result paths at this staging area.

The executed path was:

`tracking/test.py -> OTBDataset -> Tracker.run_sequence -> Tracker._read_image -> lib/test/tracker/spiketrack_inf.py -> official integer result persistence`

Each official command used `--dataset_name otb --sequence <name> --threads 0 --num_gpus 1 --inference_mode True`. All three official-default repetitions, the official deterministic run, the new adapter deterministic run, and the preserved prior adapter output are byte-identical sequence by sequence.

| Sequence | Common local prediction SHA-256 |
|---|---|
| Deer | `88a49dcd23393584e5b7a42061a9a3b89dcb851ae308694a130b3f24e54fdf5d` |
| Crossing | `039d9ca96e1ecf9f0714c88337e4eebd826e2cb78842984e33c5de775f28f65f` |
| Couple | `ced31cb5af587bbe069415163ef0d9a3d47779e5b116e4f619b5a0b80b7efe38` |

**Official runner: `PASS`. Adapter versus official runner: `EXACT`.** The adapter's empty per-frame information dictionary does not change SpikeTrack outputs on these runs even though the official wrapper propagates `previous_output`.

## 5. Default versus deterministic runtime

The three official-default repetitions were isolated and are mutually byte-identical. The deterministic characterization set seed `20260825`, CuBLAS workspace `:4096:8` before Torch import, deterministic algorithms on, cuDNN deterministic on, and cuDNN benchmark off. Its predictions are also byte-identical to every default repetition. Therefore local default-versus-deterministic mode does not explain the released-result difference. No inference is made about the authors' unrecorded runtime mode.

## 6. Linux/GPU environment result

**FACT — bounded local check:** WSL2 Ubuntu 24.04.3 is installed and Linux CUDA access works, but it exposes only the same NVIDIA GeForce MX250 with 2,048 MiB used by Windows. WSL has Python 3.12.3 only; it has no pip, Python 3.11/3.10, Conda, Mamba, or existing Linux Torch environment. Docker 29.3.1 is installed but its Linux daemon is not running. Noninteractive probes of configured remote GPU aliases did not establish access to an RTX 3060 server. No server was provisioned or rented.

The bounded official CUDA 11.8 wheel-index check found Linux x86-64 CPython 3.11 wheels for `torch 2.0.0+cu118` and `torchvision 0.15.1+cu118`, but no CPython 3.12 counterparts. This confirms that the README's Python 3.12 request cannot be combined directly with the pinned Torch/Torchvision versions. A compatible Linux Python 3.11 GPU environment was not already available, so no Linux rerun was made.

**`LINUX/GPU REPRODUCTION BLOCKER`.** This is an environment/resource boundary, not a model modification request. The smallest next action is access to an already provisioned Linux Python 3.11, Torch 2.0.0, Torchvision 0.15.1, CUDA 11.8, timm 0.5.4 GPU environment; only the same three sequences should then be rerun.

## 7. Released raw comparison

The released archive is 15,632,995 bytes with SHA-256 `7e9f8e40d069f73a7b33edfc9593946af478caa3206670847ebde78cbc545c25`. It has 4,095 ZIP entries (4,088 text files). The exact selected members are `otb/Deer.txt`, `otb/Crossing.txt`, and `otb/Couple.txt`. The archive contains no commit, environment, requirements, README, or other internal provenance manifest, and the `otb` member path does not itself encode the model config. Variant attribution therefore depends on the released archive context recorded in the prior preflight, not an internal archive manifest.

All five freshly characterized local modes give the same accuracy values and the same prediction-to-prediction divergence against the released files:

| Sequence | Released Success AUC | Local Success AUC | Absolute difference (pp) | Protocol target |
|---|---:|---:|---:|---|
| Deer | 18.041583% | 47.954393% | 29.912810 | FAIL |
| Crossing | 79.523810% | 80.000000% | 0.476190 | PASS |
| Couple | 76.190476% | 77.653061% | 1.462585 | FAIL |

`first_divergence.csv` gives these fields for every local mode using one-based frame indices and the pinned evaluator's inclusive-coordinate box IoU. Because all local prediction files are identical, the compact sequence-level values are:

| Sequence | First different frame; max component delta | First IoU <0.95 / <0.75 | Maximum later delta and frame | Released box / local box at maximum |
|---|---|---|---|---|
| Deer | 2; 6 px | 2 / 6 | 363 px at frame 17 | `[236,21,457,226]` / `[207,16,94,88]` |
| Crossing | 2; 1 px | 2 / 41 | 7 px at frame 43 | `[156,123,23,47]` / `[154,120,25,54]` |
| Couple | 2; 2 px | 2 / 6 | 16 px at frame 116 | `[113,39,36,101]` / `[116,42,32,85]` |

The exact pinned source/config/checkpoint, official runner, adapter parity, local default repeatability, deterministic-mode equality, loader RGB identity, local duplicate identity, integer persistence, and evaluator semantics have all been checked. None explains the released difference. The missing author environment and canonical OTB source checksums prevent an exact attribution.

## 8. Reproduction label

`REPRO_UNRESOLVED`

The stricter `REPRO_DOCUMENTED_ENVIRONMENT_BOUNDARY` label is not assigned: although official runner and adapter agree and local execution is repeatable, no tested runtime/platform mode systematically explains the released archive difference, and upstream dataset identity is only partial. Manager retains the acceptance decision.

## 9. Retriever/MLP instrumentation refinement

The unified repair patch is `screening/codex/patches/2026-08-25_spiketrack_stage4A_repair.patch`, generated against exact pinned commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`. It retains the accepted Stage-4A hooks and adds, for every MRM:

- whole-MRM contribution control;
- Retriever-only control: Retriever executes, its residual is withheld, and MLP executes on the unchanged MRM input;
- MLP-only control: Retriever remains applied, MLP executes, and only its residual is withheld;
- Retriever input/output shapes and residual norm;
- MLP input/residual shapes and residual norm;
- whole-MRM residual norm;
- synchronized Retriever, MLP, and total MRM timings, with diagnostic synchronization/norm/fingerprint overhead separately labeled.

Every control declares `physical_skip=false`; these are contribution controls and make no compute-saving claim. **Retriever/MLP controls: `COMPLETE`.**

## 10. T3 gate/path refinement

For every T3 MRM, the patch records all three raw and applied pre-gate response norms, per-path gate-weight mean/population-standard-deviation/minimum/maximum, and a SHA-256 fingerprint of the complete `[batch, channel, template/time]` gate tensor.

All 18 selectors `mrm1_template1` through `mrm6_template3` execute the complete upstream response computation, zero exactly one already-computed pre-gate path, and then execute the normal gate/projection. No approximate substitute and no physical path skip is used. **T3 gate/path instrumentation: `COMPLETE`.**

## 11. Refined parity results

Clean pinned versus refined/logging-on/no-ablation parity passed at tolerance `max_abs <= 1e-6`:

The exact released checkpoints were T1 SHA-256 `cf5c078ef7741109b8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df` and T3 SHA-256 `ccf04aa90521b21a78b12f4b978c03d8a69b5f6de3ee3498a3594e13e98aa491`; both full tracker-network loads had zero missing and zero unexpected keys.

| Case | Maximum observed absolute difference |
|---|---:|
| T1 synthetic | 0.0 |
| T3 synthetic | 0.0 |
| T1 real image, Deer initialization 0001 and search 0002 | 0.0 |
| T3 real image, same bounded frame contract with three initial template states | 0.0 |

Internal refined default-off versus logging-on/no-ablation parity is also 0.0 in all four cases. T1 exercised 21 controls; T3 exercised 39 controls, including all 18 template-path selectors. Every smoke produced finite head outputs and executed all six MRMs. An additional tracker-level T1 frame smoke emitted six ordered MRM records and one frame record with box, score, and template-age fields.

The 57,074-byte patch has SHA-256 `d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a`, contains only five approved SpikeTrack instrumentation/runner files, and passes `git apply --check --whitespace=error-all` on a clean pinned tree. **Refined parity: `PASS`.**

## 12. Expanded slice-inventory coverage

`screening/codex/2026-08-25_stage4A_spiketrack_slice_inventory_v2.csv` has the prior schema plus the three required duplicate/canonical-identity fields. It contains 11 OTB100 sequence records and one explicit blocker record; all 12 have `manager_review_status=PENDING`.

- Ten sequences have their complete pinned-evaluator ranges; Human3 is partial at 199 of 1,698 frames.
- Duplicate counts are two except Deer, Jogging_1, and MotorRolling, which have four; all audited duplicate raw frames and normalized GT values agree.
- Seven sequences have direct outcome-independent visual distractor reasons: Bolt, Couple, Crossing, Deer, Human3, Jogging_1, and MotorRolling. Only six of those are complete evaluator-range sequences because Human3 is partial.
- Local LaSOT-named paths contain result/evaluation artifacts, not source frames plus GT. No usable source-data markers were found for LaSOT, GOT-10k, TrackingNet, UAV123, TNL2K, NFS, or LaSOT Extension.
- No tracker prediction, score, raw-result value, or failure frame was opened or used for R4 selection. No interval, split, or ambiguity label was assigned, and no dataset was downloaded.

Fewer than ten independently supported complete distractor-containing sequences are available. **Expanded inventory: `INSUFFICIENT`; `DATA COVERAGE BLOCKER`.** The smallest next action is a Manager-approved complete official OTB100 image/annotation download, which would first complete Human3, followed by independent visual review for at least three additional unique candidates; if OTB100 remains insufficient, add official UAV123 or TNL2K source data and annotations. No download was performed.

## 13. Remaining blockers

| Blocker | Classification | Evidence | Smallest next action |
|---|---|---|---|
| Released predictions remain different on Deer and Couple | reproduction provenance | official runner, adapter, three defaults, deterministic mode, loader pixels, and local copies agree; archive has no run manifest | obtain author environment plus source-data checksums, or rerun only the same three sequences in an already available compatible Linux GPU environment |
| Official upstream OTB source identity is not established | data provenance | all workspace duplicates agree, but no canonical official archive/checksum was available | Manager-approved official OTB100 acquisition and checksum comparison |
| Compatible Linux GPU runtime is unavailable | environment/resource | WSL exposes MX250 only; Python 3.12 has no pinned Torch/Torchvision wheels; Docker daemon and RTX 3060 access unavailable | use an existing Python 3.11/CUDA 11.8 environment; do not provision without approval |
| Fewer than ten complete independently supported distractor sequences | data coverage | six complete reasoned candidates plus one partial candidate | Manager-approved official OTB100, then UAV123/TNL2K only if needed |

The prior Retriever/MLP and T3 instrumentation blockers are resolved. No scientific diagnostic outcome is inferred from the remaining reproduction/data blockers.

## 14. Stage-4A-R conclusion

`STAGE4A_R_PENDING_ENVIRONMENT_OR_DATA`

R1 evidence preservation and audit, the bounded Windows official-runner comparison, R3 instrumentation repair, exact refined parity, and the outcome-independent local inventory are complete. Stage 4A-R cannot be promoted to ready because the released-result difference remains unexplained without a compatible Linux/author-provenance boundary and the local candidate inventory remains below the locked coverage minimum.

- `STAGE 4B: LOCKED`
- `DIAG PASS/FAIL: NOT ASSIGNED`
- `S1-S7: NOT STARTED`
- `PRIMARY SHORTLIST: NONE`
- `MAIN BASELINE: NONE`
- `PROPOSED ARCHITECTURE: NONE`

STOP. Wait for Manager Stage-4A-R reconciliation.
