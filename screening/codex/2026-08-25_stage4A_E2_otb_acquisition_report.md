# Stage 4A-E2 — Author-attributed OTB100 acquisition, data identity, bounded reproduction, and inventory expansion

Protocol date: 2026-08-25. Acquisition occurred on 2026-08-25; the six bounded runs crossed local midnight and completed on 2026-08-26 (ICT). The protocol-dated artifact names are unchanged.

## 1. Authorization boundary

This lane acquired only Figshare file `42879853` (`OTB2015.zip`) and retained it under the authorized isolated `F:` destination. The only tracker executions were the six predeclared combinations `Deer`, `Crossing`, and `Couple` × official-default/deterministic. The complete OTB inventory was finished and hashed before the first tracker process started.

The Q1 repository was clean after synchronization to `1d34580c627e8529a9d714e3059f0df58c3d1c89` (`Lock Stage 4A-E2 review checklist`). This work did not download another dataset, install an environment or Linux/WSL, execute Stage 4A-E3 or Stage 4B, run full OTB100, perform an MRM ablation, use tracker output to select inventory records, freeze intervals/splits/labels, assign DIAG or S1–S7, score/rank/shortlist, select a baseline, design an architecture, or modify the candidate matrix/references.

## 2. Download source and destination

- DOI: `https://doi.org/10.6084/m9.figshare.24427468.v1`
- Public API record: `https://api.figshare.com/v2/articles/24427468`
- Author attribution in the record: Yi Wu, Jongwoo Lim, and Ming-Hsuan Yang
- Figshare file ID/name: `42879853` / `OTB2015.zip`
- Recorded licence: CC BY 4.0
- Resolved download URL: `https://ndownloader.figshare.com/files/42879853`
- Archive destination: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\archive\OTB2015.zip`
- External roots: `archive`, `extracted`, `manifests`, and `stage4a_e2_results`
- Transfer interval: `2026-08-25T16:14:44.8792044Z` to `2026-08-25T16:24:47.7905837Z`
- Transfer result: `curl` exit `0`, HTTP `200`, `602.911` seconds

The exact destination did not preexist at the planning probe; the four empty authorized directories were then created without merging with a fragmented local copy. Only the authorized file was transferred. The response headers identify `42879853/OTB2015.zip` and a final `Content-Length` of `2,722,980,405` bytes.

## 3. Free-space evidence

`F:` is a `999,058,046,976`-byte exFAT volume. The planning probe before destination creation observed `984,562,270,208` free bytes at `2026-08-25T16:13:35.9741325Z`; the destination-state record shortly afterward observed `984,560,697,344` bytes. These are two time-separated observations, differing by `1,572,864` bytes, and both exceed the required `6.127 GB` reserve.

Free space was `966,346,670,080` bytes after extraction, `966,337,495,040` bytes after the full preservation audit, and `966,180,470,784` bytes at the final acquisition/identity observation after bounded staging artifacts had also been written.

## 4. Download byte-count/MD5/SHA-256 verification

| Check | Expected | Observed | Result |
|---|---:|---:|---|
| Byte count | `2,722,980,405` | `2,722,980,405` | PASS |
| MD5 | `342b7dcb81142462b8ae9bb835cba6b4` | `342b7dcb81142462b8ae9bb835cba6b4` | PASS |
| SHA-256 | independently computed | `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5` | RECORDED |
| ZIP central directory | readable | readable | PASS |
| Full ZIP CRC stream | no bad member | no bad member | PASS |

The archive contains `58,961` members: `58,764` files and `197` explicit directory entries. Its uncompressed file total is `2,730,715,850` bytes. The top level contains `OTB2015` and `Dataset credit.docx`; unsafe rooted/traversal entries are `0`. An independent `bsdtar -tf` listed all `58,961` members with exit `0` and empty stderr.

## 5. Extraction evidence

Extraction used Windows `tar.exe`, reporting `bsdtar 3.8.4` / `libarchive 3.8.4`, with no recompression, conversion, rename, or annotation rewrite. The command returned exit `1` because exFAT rejected timestamp restoration: stderr contains `58,764` instances of `Can't restore time: Invalid argument` plus the delayed-error summary and no other error category. This non-clean metadata exit is preserved rather than hidden.

An independent post-extraction audit compared every file with its ZIP member:

- files: `58,764 / 58,764`;
- bytes: `2,730,715,850 / 2,730,715,850`;
- missing/extra files: `0 / 0`;
- size/CRC32/byte mismatches: `0 / 0 / 0`;
- external per-file manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`.

The extraction state is `CONTENT_COMPLETE_BYTE_VERIFIED_WITH_TIMESTAMP_METADATA_WARNINGS`. The archive, extracted payload, source JPEGs/GT, `Dataset credit.docx`, and full per-file manifest remain external and are not committed.

## 6. Dataset layout

The acquired `OTB2015` tree has `98` physical sequence directories and `102` ground-truth files. All `100` logical entries in the pinned SpikeTrack `OTBDataset` are source-ready: `95` direct layout matches and five nonmutating staging aliases (`Human4_2`, `Jogging_1`, `Jogging_2`, `Skating2_1`, `Skating2_2`). The evaluator references `59,035` frames through `58,255` unique JPEG paths. Every unique canonical JPEG decoded successfully and every evaluator GT mapping/row count was validated.

`F:` does not support reparse points, so the first PowerShell junction attempt failed with `Incorrect function` before any tracker output. The protocol expressly allows staging copies. The bounded fallback copied only `Deer`, `Crossing`, and `Couple` under `stage4a_e2_results\evaluator_otb3`; relative file sets and every staged file SHA-256 match the acquired source. The other 97 eager-loader records contain metadata-only GT stubs and no images. No extracted-source byte was changed.

## 7. Acquired versus local hash comparison

The comparison covers all `31` included reasonable local copies across `11` sequences. Ordered raw-JPEG streams, decoded OpenCV BGR streams, decoded RGB streams, raw GT bytes, normalized parsed GT, evaluator counts/ranges, and first/last boxes were compared without using tracker output.

| Classification | Rows |
|---|---:|
| `BYTE_IDENTICAL_TO_ACQUIRED` | 11 |
| `PIXEL_IDENTICAL_GT_IDENTICAL` | 18 |
| `DIFFERENT` | 2 |

All `31/31` comparison-window raw image streams and decoded BGR/RGB streams match the acquired package. Raw GT bytes match `11/31`; normalized GT matches `29/31`, with textual newline/format differences accounting for the non-byte-identical complete copies. The two `DIFFERENT` rows are explicitly incomplete `Human3` copies (`199` local versus `1,698` acquired frames); their shared `1–199` image prefix matches but they are not treated as complete. `Diving` uses the pinned evaluator window `1–215`, and the disclosed local/acquired physical tail `216–231` is excluded from that evaluator-window comparison.

For `Deer`, `Crossing`, and `Couple`, acquired and prior input image bytes match, and parsed GT values match. The author-attributed package therefore establishes the dataset identity needed for E2: `ESTABLISHED`.

## 8. Three-sequence official-runner contract

- Repository/commit: `faicaiwawa/SpikeTrack` at `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`
- Config: `experiments/spiketrack/spiketrack_s256_t1.yaml`
- Config SHA-256: `9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8`
- Checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`
- Released raw archive SHA-256: `7e9f8e40d069f73a7b33edfc9593946af478caa3206670847ebde78cbc545c25`
- Runner path: `tracking/test.py → OTBDataset → Tracker.run_sequence → Tracker._read_image → lib/test/tracker/spiketrack_inf.py → official integer persistence`

The runtime was the prior locked Windows environment: Python `3.11.7`, PyTorch `2.0.0+cu118`, torchvision `0.15.1+cu118`, timm `0.5.4`, OpenCV `4.11.0`, NumPy `1.26.4`, CUDA build `11.8`, cuDNN `8700`, NVIDIA GeForce MX250 `2048 MiB`, and `torch.float32`. This is desktop reproduction evidence only.

Official-default child processes had `PYTHONPATH`, `PYTHONHASHSEED`, and `CUBLAS_WORKSPACE_CONFIG` removed. Deterministic processes used seed/Python hash seed `20260825`, `CUBLAS_WORKSPACE_CONFIG=:4096:8`, deterministic PyTorch algorithms, cuDNN deterministic `true`, and benchmark `false`. Each of the six processes exited `0`; result and timing files exist with exact row counts `71/120/140`. Timing files stay external and support no speed claim. The temporary runtime config was removed afterward; the original untracked `local.py` was restored to SHA-256 `e76f5713bac3f31b3b587f4fe869aea25aeceeab5cb45b2800c46a76d7aff6fb`, and the pinned source has no tracked diff.

Every run used a fresh sequence-specific output root that was required not to exist before launch; reuse was refused rather than silently accepted.

## 9. Default/deterministic result comparison

| Sequence | Rows | Acquired default/deterministic SHA-256 | Default = deterministic | Default = prior local | Acquired data changed local prediction |
|---|---:|---|---:|---:|---:|
| Deer | 71 | `88a49dcd23393584e5b7a42061a9a3b89dcb851ae308694a130b3f24e54fdf5d` | True | True | False |
| Crossing | 120 | `039d9ca96e1ecf9f0714c88337e4eebd826e2cb78842984e33c5de775f28f65f` | True | True | False |
| Couple | 140 | `ced31cb5af587bbe069415163ef0d9a3d47779e5b116e4f619b5a0b80b7efe38` | True | True | False |

The newly acquired-source official-default, acquired-source deterministic, and previously committed local official-runner predictions are byte-for-byte identical for every predeclared sequence.

## 10. Released-result comparison

Success AUC and divergence fields were recomputed with the exact prior Stage-4A-R method against the acquired GT. Differences are absolute percentage points; frame indices are one-based.

| Sequence | Acquired/local AUC (%) | Released AUC (%) | Difference (pp) | First different frame | First IoU < 0.95 | First IoU < 0.75 | Maximum component divergence (frame) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Deer | 47.9543930248156 | 18.0415828303152 | 29.9128101945003 | 2 | 2 | 6 | 363 (17) |
| Crossing | 80.0000000000000 | 79.5238095238095 | 0.476190476190467 | 2 | 2 | 41 | 7 (43) |
| Couple | 77.6530612244898 | 76.1904761904762 | 1.4625850340136 | 2 | 2 | 6 | 16 (116) |

The author-released prediction hashes remain distinct for all three sequences. The released archive does not provide an author runtime manifest, so E2 does not attribute the remaining difference to a specific environment or execution factor.

## 11. E2 reproduction label

`E2_DATA_IDENTITY_NOT_CAUSE`

The canonical acquired input images/parsed GT match the relevant prior local inputs, and rerunning from the acquired package reproduces the prior local predictions exactly in both runtime modes. The released mismatch persists unchanged. This is the permitted E2 evidence label only; it is not `REPRO_EXACT_PASS`, a DIAG decision, or Stage 4B authorization.

## 12. Outcome-independent inventory summary

The inventory was completed before any E2 tracker result existed. It contains all `100` pinned evaluator entries in exact evaluator order; all are `COMPLETE` and `manager_review_status=PENDING`. It records object class, official attributes, canonical frame count, candidate-distractor reason, possible-control reason, inspection basis, and source/GT completeness.

- independently justified candidate-distractor rows: `47`;
- possible-control rows: `50`;
- fixed direct-inspection samples: first/lower-middle/last for every logical entry (`300` observations);
- full canonical image decode checks: `58,255/58,255` unique JPEG paths;
- prohibited tracker-derived/split/scoring language findings: `0`;
- inventory SHA-256: `8cd2ab115a361fb99afd24a1aa6e1bc1931c48de3ed050fb3f53893d2a32bcc6`.

No final interval, ambiguity label, discovery/hold-out split, control pairing, or frozen slice was assigned.

## 13. Coverage status

`SUFFICIENT`

The inventory exceeds the target of ten complete, independently justified OTB candidates and includes enough possible-control records for later Manager matching. This status does not freeze or approve any candidate.

## 14. Exact blockers

No unresolved E2 blocker remains.

- The extraction tool's timestamp-restoration error is a documented exFAT metadata limitation; independent all-file byte/CRC verification passed.
- exFAT junction creation is unsupported; the expressly authorized three-directory copy fallback passed file-set and per-file SHA-256 verification.
- The author release's runtime/configuration manifest remains unavailable. That is the documented boundary on explaining the residual released-result mismatch, not a blocker to the E2 dataset-identity conclusion.

## 15. External files retained

Key retained evidence under `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1` includes:

- `archive\OTB2015.zip` and the byte-preserved `extracted` tree;
- provider/API metadata, response headers, timestamps, ZIP listings/tests, extraction logs, and `manifests\extracted_file_manifest.csv`;
- `manifests\otb_evaluator_sequence_inventory.csv`, `manifests\local_copy_allowlist.csv`, and `manifests\acquired_vs_local_hash_comparison.csv`;
- `stage4a_e2_results\evaluator_otb3`, copy-verification manifests, run preconditions, exact commands/environment, six logs, six result files, and six timing files.

The archive, images, GT payload, checkpoint, timing files, and large full-dataset manifests are not in Git.

## 16. Q1 files committed

The single E2 commit contains only the five required top-level evidence files and bounded text artifacts:

- `screening/codex/2026-08-25_stage4A_E2_otb_acquisition_report.md`
- `screening/codex/2026-08-25_stage4A_E2_otb_source_manifest.csv`
- `screening/codex/2026-08-25_stage4A_E2_otb_hash_comparison.csv`
- `screening/codex/2026-08-25_stage4A_E2_reproduction.csv`
- `screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv`
- small acquisition/identity methodology and bounded reproduction text/checksum/result artifacts under `screening/codex/artifacts/stage4A_E2/`

## 17. E2 conclusion

| State | Conclusion |
|---|---|
| Download | PASS |
| Integrity | PASS |
| Extracted layout | READY |
| Dataset identity | ESTABLISHED |
| Reproduction | `E2_DATA_IDENTITY_NOT_CAUSE` |
| Candidate inventory | SUFFICIENT |
| Stage 4A-E2 | `COMPLETE_FOR_MANAGER_REVIEW` |

Linux setup was not performed. Stage 4A-E3 is not authorized. Stage 4B remains locked. DIAG PASS/FAIL is not assigned; S1–S7 are not started; no primary shortlist, main baseline, or proposed architecture exists. Stop at Manager E2 reconciliation.
