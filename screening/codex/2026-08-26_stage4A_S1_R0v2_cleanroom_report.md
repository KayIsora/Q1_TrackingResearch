# Stage 4A-S1-R0V2 Corrected Clean-Room Report

**Date:** 2026-08-26  
**Q1 repository:** `E:\Robot_Backup\Embodied-Tracking-Problem-Research`  
**External v2 root:** `F:\Q1_TrackingResearch_Data\Stage4A_S1_Cleanroom_2026-08-26_v2\`  
**Conclusion:** `S1_R0V2_INVALID_CONTAMINATION`

## 1. Fresh-lane declaration

R0V2 ran in a new Codex window/session. No sequence inspection occurred in this lane.

## 2. Prior-work non-reuse declaration

No scan, note, selection, sequence judgment, temporary script, or external output from either invalidated S1 attempt was reused. A non-recursive parent-directory listing displayed the name `stage4A_S1_scan`; that directory was not opened, enumerated internally, copied, compared, or used.

## 3. Q1 synchronization evidence

The required synchronization sequence completed:

- pre-pull `git status`: clean on `main`;
- `git pull origin main`: fast-forward `6ac470f` to `b2f9537`;
- post-pull `git status`: clean and current with `origin/main`;
- `git log -1 --oneline`: `b2f9537 Record clean-room contradiction and activate corrected R0V2`.

The mandatory pull output incidentally displayed a prohibited reconciliation filename as changed-path metadata. Its contents were never opened or read.

## 4. V1 root non-access declaration

The invalid v1 clean-room root was not referenced by any command and was not opened, enumerated, copied, compared, deleted, or otherwise accessed. The exact v2 root did not preexist and was created successfully.

## 5. Exact six project inputs

| Input | Bytes | SHA-256 | Source/copy |
|---|---:|---|---|
| `2026-08-26_stage4A_S1_slice_proposal_protocol.md` | 13,257 | `0590819ece897720976aefdf4c76f87470b2699f40943f786590d45468628b44` | equal |
| `2026-08-26_stage4A_S1_cleanroom_safe_source_summary.md` | 3,877 | `2827e382d63f475ef6930c429eb20216f8fbc119311345b30e8741eb27c49971` | equal |
| `2026-08-25_stage4A_E2_slice_inventory.csv` | 62,970 | `8cd2ab115a361fb99afd24a1aa6e1bc1931c48de3ed050fb3f53893d2a32bcc6` | equal |
| `2026-08-25_stage4A_E2_otb_source_manifest.csv` | 68,448 | `e887a4bff1e06e947d32fea627257dcc585514e5b7d8b7a95bf28519c4f21de7` | equal |
| `01_EVIDENCE_AND_CITATION_POLICY.md` | 2,548 | `f55ed2ed18039fa371fa66f7789a4479377b7df0651d08a6136f3c6f091296a3` | equal |
| `00_claim_taxonomy.md` | 4,660 | `b53c758cfed34c3e7da83c9fd207bcc64619c8da2cd0a7879434802fa8ef1b81` | equal |

## 6. Exact three SpikeTrack contract inputs

Checkout: `E:\Robot_Backup\tmp\stage4A_spiketrack_worktree`  
Pinned HEAD: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`

`git status --short` reported five modified/added paths outside the contract whitelist. None of the three copied paths appeared in status output.

| Input | Bytes | SHA-256 | Source/copy |
|---|---:|---|---|
| `lib/test/evaluation/otbdataset.py` | 21,722 | `31adc2a151f32edef7308cb164f127e00240f2f5ed1a26518080874ea700fcad` | equal |
| `experiments/spiketrack/spiketrack_s256_t1.yaml` | 1,299 | `9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8` | equal |
| `lib/test/tracker/seqtrack_utils.py` | 4,458 | `b478bdbc1995ef18914245646ccfd1e5e7df19cfefdddb51670f44925ec91763` | equal |

No model code, checkpoint, tracker output, instrumentation, raw result, test log, or invalid-attempt script was copied.

## 7. Dataset pointer

- source root: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015\`;
- source-root existence: true;
- physical sequence-directory count: 98;
- archive SHA-256: `aad6be170d417777a5cee0b99bdd367e540b81f9020ac08b5c96d4d5d5094be5`;
- extracted-file manifest SHA-256: `a58329bea07dc96f9d35ad5d2a22785e23198f90c451da6369f7eaa985625032`;
- pointer: `inputs\dataset_pointer\OTB2015_read_only_pointer.txt`, 423 bytes, SHA-256 `0263f037e53a1102157509d55f208e3e599a46dc4bcd6bdd1ac2d946db7e7518`;
- intent: read-only; dataset not duplicated; no frame inspected.

## 8. Expected and observed input count

| Category | Expected | Observed |
|---|---:|---:|
| Project | 6 | 6 |
| SpikeTrack contract | 3 | 3 |
| Dataset pointer | 1 | 1 |
| **Total inputs** | **10** | **10** |

The complete external root contained 14 files: ten inputs plus the four generated R0V2 audit files (`cleanroom_manifest.csv`, `cleanroom_tree.txt`, `cleanroom_attestation.md`, and `commands.txt`). No unauthorized or missing filename was detected.

## 9. Hash equality

All nine copied files matched their exact source SHA-256. All ten manifest rows matched the observed clean-room byte size and SHA-256.

External audit hashes:

- external manifest: `23977c233c77ce9852d70c730d43db7551703f23c45882405c0e113031047ded`;
- clean-room tree: `df9c9602a755be95b3bb6c494440326932103cf1ec12cc85603cfaacae8c37a6`;
- invalid-contamination attestation: `68da8dc02864cafb7f1a9c3930204af46111bebe6c8a217a96f4c6b560e8ffa8`.

## 10. Command-log validation

All shell commands used for bundle construction and validation are recorded with timestamp, working directory, exact command, exit code, and purpose. Failed commands are retained. Commands executed before the log existed use an explicitly marked retrospective record timestamp. Non-shell `apply_patch` actions are listed separately. Publication commands occur after the audit-log artifact is frozen.

Command-log validation: **PASS**.

## 11. Contamination-scan result

The recursive scan was confined to the new v2 root.

Passed checks:

- exact file allowlist: 14 observed / 14 allowed;
- exact input count: 10;
- no `success_auc_percent`, `released_success_auc`, `prediction_sha256`, or `first_divergence` token in the ten inputs;
- no tracker performance value, prediction row, score/confidence payload, MRM output, or invalid-v1 file detected.

Failed literal protocol condition:

- `Couple`, `Crossing`, and `Deer` occur in `2026-08-25_stage4A_E2_otb_source_manifest.csv` at lines 33, 35, and 42;
- the same names occur in `2026-08-25_stage4A_E2_slice_inventory.csv` at lines 26, 28, and 35;
- the same names occur in `otbdataset.py` at lines 98, 102, and 116.

These occurrences carry source mapping, frame-range, or source-observation facts and no tracker outcome values. Nevertheless, they are outside protocol/safe-summary policy text and therefore violate the literal R0V2 rule that these quarantine names may appear only in protocol/safe-summary text.

Contamination scan: **FAIL**. The bundle is rejected.

## 12. Prohibited-operation attestation

- prohibited Q1 repository operation: none;
- prohibited Q1 file read/copied: none;
- invalid v1 root access: none;
- OTB frame inspection: none;
- tracker output/metric access: none;
- sequence proposal/control/contact sheet: none;
- SpikeTrack execution/model instantiation: none;
- Stage 4B, DIAG, S1-S7, ranking, shortlist, baseline, and architecture work: not started.

The `rg` and non-recursive directory listings recorded in the log targeted files/directories outside the Q1 repository; no prohibited search was executed inside Q1.

## 13. Files produced

External:

- `inputs\cleanroom_manifest.csv`;
- `inputs\cleanroom_tree.txt`;
- `outputs\cleanroom_attestation.md`;
- `logs\commands.txt`.

Q1 audit artifacts:

- `screening/codex/2026-08-26_stage4A_S1_R0v2_cleanroom_report.md`;
- `screening/codex/2026-08-26_stage4A_S1_R0v2_cleanroom_manifest.csv`;
- `screening/codex/2026-08-26_stage4A_S1_R0v2_command_log.txt`.

## 14. R0V2 conclusion

`S1_R0V2_INVALID_CONTAMINATION`

Sequence scanning was not started. Stage 4A-S1-R1 remains locked. No frozen diagnostic slice was created. Stage 4B remains locked. DIAG and S1-S7 were not assigned or started. The primary shortlist, main baseline, and proposed architecture remain `NONE`.
