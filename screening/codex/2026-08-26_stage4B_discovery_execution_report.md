# Stage 4B frozen discovery diagnostic execution report

**Date:** 2026-08-26

**Scope:** frozen 12-pair discovery execution only

**Report conclusion:** `STAGE4B_AB_PASS_READY_FOR_MANAGER_REVIEW`

This report is generated deterministically from bounded execution and analysis
artifacts. It does not assign a final diagnostic decision, does not unlock
Stage 4C, and contains no held-out outcome.

## 1. Boundary and frozen-slice verification

- Frozen-slice normalized-LF SHA-256: `bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a`
- Locked expected SHA-256: `bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a`
- Frozen-slice validation: `PASS`
- Frozen discovery IDs: `R3-D01, R3-D02, R3-D03, R3-D04, R3-D05, R3-D06, R3-D07, R3-D08, R3-D09, R3-D10, R3-D11, R3-D12`
- Discovery pairs represented in the execution manifest: `12`
- Discovery intervals represented: `24` (expected 24 primary/control intervals)
- Held-out outcome rows consumed by this reporting lane: `0`

## 2. Hold-out seal declaration

The eight held-out pairs remain frozen metadata only. Their tracker outcomes,
IoU, failures, scores, contributions, utilities, and labels were not opened or
computed by this reporting lane. Maximum hold-out execution/access count
reported by the input summaries: `0`. Seal status:
`PASS`.

| Pair ID | Frozen primary | Frozen control | Row SHA-256 | Status |
| --- | --- | --- | --- | --- |
| R3-H01 | Crowds 33-37 | Crowds 161-165 | c69fb8eb6d10416be59c5af8e2533cc867111f1349306d0a207f6a055572a0ba | NOT_EXECUTED_STAGE4B |
| R3-H02 | BlurCar4 255-279 | Suv 726-750 | ab83352c49421774d85636d0ff4eac44fc5fd1fd42590fd3eec5549935629387 | NOT_EXECUTED_STAGE4B |
| R3-H03 | Soccer 170-180 | Man 106-116 | 2134fb0eafd1ff5cfb19b62c6bedd47f09c2a920f7881159906a9f8898a70566 | NOT_EXECUTED_STAGE4B |
| R3-H04 | Girl 411-429 | Girl 363-381 | 82e21cb5bb6d65b103b619c96681eb3da4376655304f699a597c632565df22ca | NOT_EXECUTED_STAGE4B |
| R3-H05 | Human3 57-81 | Human3 264-288 | ca6c3222618623760b63322d4fd5dda505ed2aaa7fa97c95000a1acf0e22a187 | NOT_EXECUTED_STAGE4B |
| R3-H06 | Human3 1564-1588 | Human3 1418-1442 | 1876e5cbd53e31029ae3d23a16ff3f401278595cc0d5dfc5203013a5e6ded481 | NOT_EXECUTED_STAGE4B |
| R3-H07 | Human4_2 73-97 | Walking2 393-417 | 82e4bcf887a31d0c19eb11ab774a4588818b3bf45100d8bbc4216ab4bbe30052 | NOT_EXECUTED_STAGE4B |
| R3-H08 | Suv 372-399 | Suv 410-437 | 17817efdd398ec470596a2bf705bf0af176f6552ef302520606c7e1c16e29553 | NOT_EXECUTED_STAGE4B |

## 3. Source/config/checkpoint/patch provenance

- Official source: `faicaiwawa/SpikeTrack`
- Clean pinned source SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`
- Config: `F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26\SpikeTrack_pinned\experiments\spiketrack\spiketrack_s256_t1.yaml`
- Config SHA-256: `9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8`
- Checkpoint: `E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar`
- Checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`
- Canonical OTB2015 dataset root: `F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015`
- Accepted Stage-4A-E2 source-manifest SHA-256: `35638156ef0f069978ee6e13daa9095be528bde1244b085e230170726a21956d`
- Accepted patch SHA-256 (canonical LF): `d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a`
- Patch application: `PASS_CANONICAL_GIT_BLOB_STRICT_WHITESPACE`
- Patched files: `lib/models/spiketrack/sdtv3_search_inference.py, lib/models/spiketrack/spiketrack_inf.py, lib/test/parameter/spiketrack.py, lib/test/tracker/spiketrack_inf.py, tracking/stage4a_spiketrack_smoke.py`
- Patched-file SHA-256 map: `{"lib/models/spiketrack/sdtv3_search_inference.py": "77b01cb252919c5a9e50500cc567f8c2766ac86ccd343dfcc7d3af7e95b72931", "lib/models/spiketrack/spiketrack_inf.py": "01a1f891ff10542ce32cbffafd820e0338c5ea4ff67f59065ea3a7e044aa71f8", "lib/test/parameter/spiketrack.py": "fcd53eb2f88e38f673dbb81d6b5c2e83b7b2b2f956d1105f4980a7890aa5af81", "lib/test/tracker/spiketrack_inf.py": "56c0a985cdf5905e7e1c16383b4e9ad41406c3718e066bdf4a6f0701dc427471", "tracking/stage4a_spiketrack_smoke.py": "477730db506c43e31cf8161b770c9479c1e611fc825affe85dfdee5ed947c002"}`
- Operational boundary: `local paired diagnostic baseline only; no author-released raw-result parity claim`

## 4. Environment

| Field | Recorded value |
| --- | --- |
| OS | Windows-10-10.0.26200-SP0 |
| CPU | Intel64 Family 6 Model 126 Stepping 5, GenuineIntel |
| RAM bytes | 16951066624 |
| GPU | NVIDIA GeForce MX250 |
| VRAM bytes | 2147352576 |
| Python | 3.11.7 (tags/v3.11.7:fa7a6f2, Dec  4 2023, 19:24:49) [MSC v.1937 64 bit (AMD64)] |
| PyTorch | 2.0.0+cu118 |
| CUDA | 11.8 |
| cuDNN | 8700 |
| timm | 0.5.4 |
| key dependency versions | {"einops": null, "numpy": "1.26.4", "opencv-python": null, "pandas": "2.2.3", "scipy": null, "spikingjelly": null, "timm": "0.5.4", "torchvision": "0.15.1+cu118", "yacs": "0.1.8"} |
| dtype | torch.float32 |
| seed | 20260826 |
| deterministic settings | {"CUBLAS_WORKSPACE_CONFIG": ":4096:8", "cudnn_benchmark": false, "cudnn_deterministic": true, "torch_deterministic_algorithms": true} |

## 5. No-ablation parity

- Status: `PASS`
- Maximum observed absolute difference: `0.000000000`
- Required tolerance: `<= 0.000001`
- Recorded tolerance: `0.000001000`
- Prediction, encoded state, score map, and head fingerprints are retained in
  `screening/codex/artifacts/stage4B_discovery/no_ablation_parity.json`.

## 6. Sequence execution contract

Every unique discovery source sequence was required to initialize once through
the official sequence start and run sequentially through its maximum frozen
frame. No interval-level GT reinitialization is accepted. Contract validation:
`PASS`.

| Sequence | Official start | Executed through | Initialized once | Status | External prediction SHA-256 |
| --- | --- | --- | --- | --- | --- |
| Basketball | 1 | 435 | True | COMPLETE | 878b0b8ee75e2a00edec5c991a5a4b02f1d692eb64aae5aae3cf33d7e4c2ef9c |
| Bolt | 1 | 49 | True | COMPLETE | b25fe4f9c427bf87d446b7ac576b50e19d7e6777d081d059eeb0f0bd70968e69 |
| Car4 | 1 | 245 | True | COMPLETE | 26cb763cac4380e2565edbabcd92d64b29e22c315fbc2921140c20fdb6fd5f7c |
| CarDark | 1 | 145 | True | COMPLETE | 65017dbf93fa83b409c141d2b19c55984064c2c2fb5ba6f6f15fff8b96a14f95 |
| CarScale | 1 | 105 | True | COMPLETE | 31b9da7e95a55ad7e106ee15a7fdeb58c722f7c079371cad9db3b9cb64db5292 |
| Dancer | 1 | 95 | True | COMPLETE | 305da1fa63297e1dc85c3018e6ba36db7652e0db29e61ae9c5dddd8e496038ed |
| David2 | 1 | 285 | True | COMPLETE | 4b99a85f5cd99a1afa00cbcc672cba29d8762c7da5fe990886e66241fd3e2eff |
| David3 | 1 | 233 | True | COMPLETE | a70a909e1365f303158a9a8d3cacd58be5aca29cd57e1ebbe6026699f73e7d2a |
| Freeman3 | 1 | 269 | True | COMPLETE | 9f5dce8721b43f5c0f6bdae3ac27283d36fc83d8b287c3ab2aed757edd7f5b16 |
| Human7 | 1 | 37 | True | COMPLETE | a20ca52b25e05aba6181662912046ead5e85e4f07a05645faee128d069e7f2d1 |
| Human8 | 1 | 126 | True | COMPLETE | d13a543f42a4dcfe38f7183e658d29886e9eca0c52ef51af686c9c295d594cf9 |
| Jogging_1 | 1 | 174 | True | COMPLETE | 12019c05e5f0759154b81702b77d90b25910d5de6dd1ef78098b49d5e7672f75 |
| Liquor | 1 | 589 | True | COMPLETE | f3dc00c703f41f96c71c261c18b3d887759ec60076c82443ff4e43015fdfe74b |
| Shaking | 1 | 25 | True | COMPLETE | a30b2d074521210d0648c9e9b5e4eb3185392547e705817fce6ae99c43d16504 |
| Singer1 | 1 | 25 | True | COMPLETE | e385b4f4a075a55027e3f238505fb863cf330cae6a1bb04159e4497876a37595 |
| Skating1 | 1 | 137 | True | COMPLETE | 66ab7eaecb3a5b5309851842d52930d10a6771afd61e4dcb6cdf95d0d839afc2 |
| Subway | 1 | 45 | True | COMPLETE | e54bb27466e2173e8b7a13eab22f98ca052fa66794008a9782727cfff0030c12 |
| Woman | 1 | 207 | True | COMPLETE | 18deb4c625c5e88e9f62c5f06bbf796cf6cec972553c095b92e5fd4ab585cebe |

## 7. Snapshot/restore implementation

Criterion-B branches must restore the same prefix snapshot at
`interval_start - 1`, clone it into baseline and each of the nine predeclared
ablation controls, then continue over identical frames. Reinitializing from GT
is prohibited. Recorded start/restore branches:
`240`; recorded
continuation/restore intervals:
`24`.

## 8. Snapshot parity results

- State snapshot parity: `PASS`
- State-parity rows: `240`
- Summary state status: `PASS`
- Baseline branch status: `PASS`
- Integer prediction parity: `True`
- Maximum floating prediction difference: `0.000000000`
- Maximum score-map difference: `0.000000000`
- Maximum confidence difference: `0.000000000`

Absence of state-parity evidence is acceptable only when Criterion A failed and
the protocol stopped before MRM execution.

## 9. Criterion A complete-set result

Criterion A: `PASS`. Pair effects are equally weighted after
within-interval frame means; the primary bootstrap clusters by unique primary
sequence and retains all pairs belonging to a sampled sequence.

| Metric | Estimate | Primary 95% CI | Threshold | Primary p | Pass | Component 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| iou_weakness | 0.136999 | [0.001888, 0.317117] | 0.050000 | 0.047395 | true | [-0.013529, 0.307374] |
| failure_weakness | 0.153333 | [-0.030000, 0.418182] | 0.100000 | 0.172183 | false | [-0.036364, 0.384000] |

## 10. Criterion A sensitivity results

These locked strata are descriptive only. They do not change the complete-set
decision and no positive conclusion relies on a favorable subgroup.

| Dimension | Group | Metric | n pairs | Estimate | Primary 95% CI | Component 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| final_ambiguity_level | AMBIGUITY_LEVEL_2 | iou_weakness | 4 | 0.194151 | [0.025360, 0.532036] | [0.025360, 0.532036] |
| final_ambiguity_level | AMBIGUITY_LEVEL_2 | failure_weakness | 4 | 0.260000 | [0.000000, 1.000000] | [0.000000, 1.000000] |
| final_ambiguity_level | AMBIGUITY_LEVEL_1 | iou_weakness | 8 | 0.108423 | [-0.058570, 0.327744] | [-0.059047, 0.348169] |
| final_ambiguity_level | AMBIGUITY_LEVEL_1 | failure_weakness | 8 | 0.100000 | [-0.075000, 0.375000] | [-0.075000, 0.400000] |
| control_sequence_relation | SAME_SEQUENCE_CONTROL | iou_weakness | 3 | 0.018108 | [0.003606, 0.025360] | [0.003606, 0.025360] |
| control_sequence_relation | SAME_SEQUENCE_CONTROL | failure_weakness | 3 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| control_sequence_relation | CROSS_SEQUENCE_CONTROL | iou_weakness | 9 | 0.176629 | [-0.004802, 0.391424] | [-0.027572, 0.372993] |
| control_sequence_relation | CROSS_SEQUENCE_CONTROL | failure_weakness | 9 | 0.204444 | [-0.040000, 0.533333] | [-0.050000, 0.480000] |
| sensitivity_stratum | STRONG_SAME_SEQUENCE | iou_weakness | 2 | 0.025360 | [0.025360, 0.025360] | [0.025360, 0.025360] |
| sensitivity_stratum | STRONG_SAME_SEQUENCE | failure_weakness | 2 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| sensitivity_stratum | CROSS_SCENE_ACTIVITY | iou_weakness | 4 | 0.445521 | [0.222324, 0.668717] | [0.250799, 0.532036] |
| sensitivity_stratum | CROSS_SCENE_ACTIVITY | failure_weakness | 4 | 0.510000 | [0.020000, 1.000000] | [0.000000, 1.000000] |
| sensitivity_stratum | COLOR_DIFFERENCE | iou_weakness | 1 | 0.003606 | [0.003606, 0.003606] | [0.003606, 0.003606] |
| sensitivity_stratum | COLOR_DIFFERENCE | failure_weakness | 1 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| sensitivity_stratum | APPEARANCE_DIFFERENCE | iou_weakness | 1 | 0.117311 | [0.117311, 0.117311] | [0.117311, 0.117311] |
| sensitivity_stratum | APPEARANCE_DIFFERENCE | failure_weakness | 1 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| sensitivity_stratum | LOW_LIGHT_MULTI_TRAFFIC | iou_weakness | 1 | 0.021784 | [0.021784, 0.021784] | [0.021784, 0.021784] |
| sensitivity_stratum | LOW_LIGHT_MULTI_TRAFFIC | failure_weakness | 1 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| sensitivity_stratum | CONTROL_PARTIAL_OCCLUSION | iou_weakness | 1 | -0.169647 | [-0.169647, -0.169647] | [-0.169647, -0.169647] |
| sensitivity_stratum | CONTROL_PARTIAL_OCCLUSION | failure_weakness | 1 | -0.200000 | [-0.200000, -0.200000] | [-0.200000, -0.200000] |
| sensitivity_stratum | MULTI_FACE_BACKGROUND | iou_weakness | 1 | -0.036073 | [-0.036073, -0.036073] | [-0.036073, -0.036073] |
| sensitivity_stratum | MULTI_FACE_BACKGROUND | failure_weakness | 1 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| sensitivity_stratum | COSTUME_DIFFERENCE_CLASS_RESOLVED_PERSON | iou_weakness | 1 | -0.125797 | [-0.125797, -0.125797] | [-0.125797, -0.125797] |
| sensitivity_stratum | COSTUME_DIFFERENCE_CLASS_RESOLVED_PERSON | failure_weakness | 1 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| broad_superclass | PERSON | iou_weakness | 6 | 0.247773 | [-0.024373, 0.519919] | [-0.068018, 0.473338] |
| broad_superclass | PERSON | failure_weakness | 6 | 0.306667 | [-0.060000, 0.673333] | [-0.080000, 0.640000] |
| broad_superclass | VEHICLE | iou_weakness | 2 | 0.012695 | [0.003606, 0.021784] | [0.003606, 0.021784] |
| broad_superclass | VEHICLE | failure_weakness | 2 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| broad_superclass | FACE_HEAD | iou_weakness | 2 | 0.040619 | [-0.036073, 0.117311] | [0.040619, 0.040619] |
| broad_superclass | FACE_HEAD | failure_weakness | 2 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |
| broad_superclass | OBJECT_OTHER | iou_weakness | 2 | 0.025360 | [0.025360, 0.025360] | [0.025360, 0.025360] |
| broad_superclass | OBJECT_OTHER | failure_weakness | 2 | 0.000000 | [0.000000, 0.000000] | [0.000000, 0.000000] |

## 11. Stop/proceed decision after Criterion A

`Proceed to exactly nine predeclared Criterion-B controls`.

## 12. Criterion B nine-test results, if run

Criterion B: `PASS`. Exactly the six individual MRMs and three locked
groups are admissible. All controls remain `physical_skip=false`.

| Order | Mode | Mean interaction | Primary 95% CI | p | Holm p | Direction | Pass | Selected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | mrm1 | -0.027884 | [-0.056570, -0.008070] | 0.001400 | 0.012599 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | true | true |
| 2 | mrm2 | -0.001926 | [-0.039017, 0.033750] | 0.960504 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 3 | mrm3 | -0.013228 | [-0.043432, 0.011435] | 0.360764 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 4 | mrm4 | -0.028700 | [-0.093256, 0.016271] | 0.305769 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 5 | mrm5 | -0.067583 | [-0.181183, 0.044430] | 0.232177 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 6 | mrm6 | -0.023350 | [-0.110035, 0.046328] | 0.583342 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 7 | early | -0.009654 | [-0.041740, 0.019440] | 0.544946 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 8 | middle | -0.007911 | [-0.064307, 0.041602] | 0.821718 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |
| 9 | late | -0.082248 | [-0.264460, 0.066816] | 0.311569 | 1.000000 | RELATIVE_UTILITY_LOWER_UNDER_DISTRACTOR_AMBIGUITY | false | false |

The machine sensitivity table retains `144` locked
Criterion-B descriptive rows. Those rows do not create extra tests and cannot
rescue the primary nine-test family.

## 13. Holm correction and clustered bootstrap

- Bootstrap resamples: `10000`
- Bootstrap seed: `20260826`
- Primary cluster unit: `unique primary_sequence`
- Required dependency sensitivity: connected source components
- Criterion-A primary/component bootstrap rows: `4`
- Criterion-B primary/component bootstrap rows: `18`
- Holm correction: `PASS` across `9` rows; familywise alpha `0.05`

## 14. Criterion B stop/proceed decision

`Proceed only to the selected bounded refinement path`. Selected refinement path: `mrm1`.

## 15. Retriever/MLP refinement, if permitted

Retriever-only and MLP-only bypasses are permitted only after the primary
nine-test Criterion-B family passes, and only for the locked selected path.

| Component | Status |
| --- | --- |
| mlp_only_bypass | COMPLETE |
| retriever_only_bypass | COMPLETE |
| t3_baseline | COMPLETE |
| t3_selected_path_controls | COMPLETE |

No refinement result creates a new Criterion-B test or rescues a failed primary
family.

## 16. T3 controlled comparison, if permitted

T3 is secondary and is permitted only after Criterion B passes. A complete
refinement package requires the T3 baseline on all frozen discovery pairs and,
when technically valid, the three selected-path template/time controls. An
explicit technical-validity blocker is accepted for unavailable controls; a
missing artifact is not. T3 never replaces the T1 Criterion-A/B decision.
The required controlled config is `experiments/spiketrack/spiketrack_s256_t3.yaml`
and the pinned T3 checkpoint SHA-256 is `ccf04aa90521b21a78b12f4b978c03d8a69b5f6de3ee3498a3594e13e98aa491`.

Selected-path T3 controls executed: `3` of `3`.

| T3 condition | Status | Discovery pairs | Frozen intervals |
| --- | --- | --- | --- |
| t3_baseline | COMPLETE | 12 | 24 |
| t3_template_path_1_zero_contribution | COMPLETE | 12 | 24 |
| t3_template_path_2_zero_contribution | COMPLETE | 12 | 24 |
| t3_template_path_3_zero_contribution | COMPLETE | 12 | 24 |

## 17. Timing characterization and non-claims

- Baseline timing rows: `3558`
- Criterion-B mode timing rows: `54`
- Timing physical-skip flag validation: `PASS`

| Mode/control | MRM | n | Retriever mean ms | MLP mean ms | MRM compute mean ms | Instrumented mean ms |
| --- | --- | --- | --- | --- | --- | --- |
| none | MRM1 | 593 | 10.855 | 2.564 | 13.795 | 15.598 |
| none | MRM2 | 593 | 9.763 | 2.397 | 12.474 | 13.904 |
| none | MRM3 | 593 | 9.228 | 2.377 | 11.921 | 13.318 |
| none | MRM4 | 593 | 8.893 | 2.442 | 11.640 | 13.064 |
| none | MRM5 | 593 | 9.203 | 2.472 | 12.002 | 13.548 |
| none | MRM6 | 593 | 9.523 | 2.782 | 12.645 | 14.232 |
| early | MRM1 | 593 | 14.956 | 3.800 | 19.317 | 21.795 |
| early | MRM2 | 593 | 14.825 | 3.609 | 18.874 | 20.903 |
| early | MRM3 | 593 | 14.123 | 3.740 | 18.359 | 20.530 |
| early | MRM4 | 593 | 14.821 | 4.132 | 19.426 | 21.677 |
| early | MRM5 | 593 | 15.324 | 4.266 | 20.105 | 22.628 |
| early | MRM6 | 593 | 15.159 | 4.270 | 19.952 | 22.334 |
| late | MRM1 | 593 | 15.101 | 3.930 | 19.570 | 22.208 |
| late | MRM2 | 593 | 14.676 | 3.611 | 18.784 | 20.866 |
| late | MRM3 | 593 | 14.391 | 3.920 | 18.799 | 21.031 |
| late | MRM4 | 593 | 15.672 | 4.279 | 20.518 | 23.066 |
| late | MRM5 | 593 | 15.325 | 4.327 | 20.174 | 22.660 |
| late | MRM6 | 593 | 14.903 | 4.124 | 19.590 | 22.141 |
| middle | MRM1 | 593 | 15.497 | 4.059 | 20.097 | 22.636 |
| middle | MRM2 | 593 | 15.177 | 3.664 | 19.299 | 21.463 |
| middle | MRM3 | 593 | 15.014 | 3.858 | 19.362 | 21.652 |
| middle | MRM4 | 593 | 14.904 | 4.132 | 19.550 | 21.976 |
| middle | MRM5 | 593 | 14.662 | 4.158 | 19.329 | 21.913 |
| middle | MRM6 | 593 | 15.839 | 4.351 | 20.806 | 23.349 |
| mrm1 | MRM1 | 593 | 15.707 | 3.930 | 20.169 | 22.685 |
| mrm1 | MRM2 | 593 | 15.655 | 4.070 | 20.220 | 22.322 |
| mrm1 | MRM3 | 593 | 14.688 | 4.116 | 19.353 | 21.626 |
| mrm1 | MRM4 | 593 | 15.133 | 4.250 | 19.886 | 22.238 |
| mrm1 | MRM5 | 593 | 15.929 | 4.336 | 20.825 | 23.401 |
| mrm1 | MRM6 | 593 | 15.892 | 4.319 | 20.798 | 23.309 |
| mrm2 | MRM1 | 593 | 16.493 | 4.009 | 21.067 | 23.617 |
| mrm2 | MRM2 | 593 | 15.943 | 3.927 | 20.351 | 22.522 |
| mrm2 | MRM3 | 593 | 15.461 | 4.356 | 20.327 | 22.619 |
| mrm2 | MRM4 | 593 | 16.095 | 4.420 | 21.065 | 23.486 |
| mrm2 | MRM5 | 593 | 16.439 | 4.275 | 21.304 | 23.739 |
| mrm2 | MRM6 | 593 | 16.355 | 4.324 | 21.196 | 23.544 |
| mrm3 | MRM1 | 593 | 15.910 | 4.126 | 20.605 | 23.262 |
| mrm3 | MRM2 | 593 | 15.671 | 3.810 | 19.998 | 22.131 |
| mrm3 | MRM3 | 593 | 15.366 | 4.305 | 20.195 | 22.600 |
| mrm3 | MRM4 | 593 | 15.283 | 4.203 | 20.026 | 22.414 |
| mrm3 | MRM5 | 593 | 16.009 | 4.342 | 20.958 | 23.607 |
| mrm3 | MRM6 | 593 | 16.043 | 4.462 | 21.039 | 23.552 |
| mrm4 | MRM1 | 593 | 15.378 | 4.078 | 20.007 | 22.465 |
| mrm4 | MRM2 | 593 | 15.587 | 3.998 | 20.126 | 22.358 |
| mrm4 | MRM3 | 593 | 15.222 | 4.252 | 19.980 | 22.332 |
| mrm4 | MRM4 | 593 | 16.052 | 4.420 | 20.990 | 23.458 |
| mrm4 | MRM5 | 593 | 15.557 | 4.213 | 20.273 | 22.659 |
| mrm4 | MRM6 | 593 | 16.003 | 4.328 | 20.866 | 23.367 |
| mrm5 | MRM1 | 593 | 15.198 | 4.049 | 19.769 | 22.260 |
| mrm5 | MRM2 | 593 | 14.660 | 3.616 | 18.753 | 20.740 |
| mrm5 | MRM3 | 593 | 14.095 | 3.947 | 18.560 | 20.730 |
| mrm5 | MRM4 | 593 | 15.233 | 4.075 | 19.830 | 22.177 |
| mrm5 | MRM5 | 593 | 15.698 | 4.138 | 20.357 | 22.855 |
| mrm5 | MRM6 | 593 | 15.274 | 4.105 | 19.905 | 22.309 |
| mrm6 | MRM1 | 593 | 15.604 | 3.918 | 20.050 | 22.608 |
| mrm6 | MRM2 | 593 | 15.479 | 3.760 | 19.756 | 21.841 |
| mrm6 | MRM3 | 593 | 14.972 | 4.173 | 19.712 | 22.027 |
| mrm6 | MRM4 | 593 | 15.432 | 4.382 | 20.359 | 22.736 |
| mrm6 | MRM5 | 593 | 15.680 | 4.277 | 20.616 | 23.125 |
| mrm6 | MRM6 | 593 | 16.236 | 4.362 | 21.148 | 23.690 |

These desktop measurements characterize instrumented execution only. They are
not physical-skipping savings, not end-to-end deployment latency, and not
Jetson Nano evidence. No parity with author-released raw OTB predictions is
claimed.

External raw logs and their recorded/observed hashes:

| Kind | Path | Size bytes | SHA-256 | Verification |
| --- | --- | --- | --- | --- |
| external_raw_log | F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26\bounded_refinement\t1_retriever_mlp_raw_mrm.jsonl | 23582085 | fcfefb21999b1b460479000ce0e8cb9c7e16d8ea93bdbe401be954b3925aa13a | RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE |
| external_raw_log | F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26\bounded_refinement\t3_baseline_template_controls_raw_mrm.jsonl | 56532981 | b9c83c4fe73aa54f303738af3cba3b2a7f954f13c719551b4b73a26e797d6e70 | RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE |
| external_raw_log | F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26\criterionA\baseline_raw_mrm.jsonl | 10953239 | 9c48b8256309dd1127942befa79188b1b1547445263190dea7906fa8c3845696 | RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE |
| external_raw_log | F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26\criterionB\criterionB_raw_mrm.jsonl | 113160575 | 35957fe4b6a010ce5d0d40ff7c67d71c217f631ffd1da91f94ee9bc69dce148d | RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE |
| external_raw_log | F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26\parity_instrumented.json | 52236 | 4ada12ec9fdf6fa3be1d9e675de2028acc5d5e3c7584605219d32bb52ec04345 | RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE |

## 18. Exact blockers

Blocking or invalidating conditions:

- None.

Secondary non-gating limitations:

- SECONDARY_DISTRACTOR_MARGIN_NOT_AVAILABLE: accepted instrumentation exposes only the global score-map output and supplies no validated mapping from frozen manual distractor boxes to the tracker head grid; therefore no target-versus-distractor margin was approximated

## 19. Files produced

| Path | Role |
| --- | --- |
| screening/codex/2026-08-26_stage4B_analysis_summary.json | stage4b_analysis_summary |
| screening/codex/2026-08-26_stage4B_bootstrap_results.csv | stage4b_required_or_analysis_csv |
| screening/codex/2026-08-26_stage4B_command_log.txt | stage4b_command_log |
| screening/codex/2026-08-26_stage4B_criterionA_results.csv | stage4b_required_or_analysis_csv |
| screening/codex/2026-08-26_stage4B_criterionB_results.csv | stage4b_required_or_analysis_csv |
| screening/codex/2026-08-26_stage4B_discovery_execution_report.md | generated report |
| screening/codex/2026-08-26_stage4B_holm_adjusted_tests.csv | stage4b_required_or_analysis_csv |
| screening/codex/2026-08-26_stage4B_pair_level_A.csv | stage4b_required_or_analysis_csv |
| screening/codex/2026-08-26_stage4B_pair_level_B.csv | stage4b_required_or_analysis_csv |
| screening/codex/2026-08-26_stage4B_sensitivity_results.csv | stage4b_required_or_analysis_csv |
| screening/codex/artifacts/stage4B_discovery/analysis_summary.json | stage4b_execution_or_analysis_summary |
| screening/codex/artifacts/stage4B_discovery/artifact_manifest.csv | artifact manifest |
| screening/codex/artifacts/stage4B_discovery/baseline_per_frame_metrics.csv | stage4b_bounded_per_frame_metrics |
| screening/codex/artifacts/stage4B_discovery/baseline_sequence_execution.csv | stage4b_machine_artifact |
| screening/codex/artifacts/stage4B_discovery/bootstrap_results.csv | stage4b_bounded_analysis_machine_file |
| screening/codex/artifacts/stage4B_discovery/bounded_refinement_execution_manifest.csv | stage4b_machine_manifest |
| screening/codex/artifacts/stage4B_discovery/bounded_refinement_execution_summary.json | stage4b_execution_or_analysis_summary |
| screening/codex/artifacts/stage4B_discovery/bounded_refinement_timing_characterization.csv | stage4b_timing_characterization |
| screening/codex/artifacts/stage4B_discovery/criterionA_execution_summary.json | stage4b_execution_or_analysis_summary |
| screening/codex/artifacts/stage4B_discovery/criterionA_results.csv | stage4b_bounded_analysis_machine_file |
| screening/codex/artifacts/stage4B_discovery/criterionB_execution_summary.json | stage4b_execution_or_analysis_summary |
| screening/codex/artifacts/stage4B_discovery/criterionB_results.csv | stage4b_bounded_analysis_machine_file |
| screening/codex/artifacts/stage4B_discovery/discovery_execution_manifest.csv | stage4b_machine_manifest |
| screening/codex/artifacts/stage4B_discovery/external_evidence_registry.csv | stage4b_machine_artifact |
| screening/codex/artifacts/stage4B_discovery/holdout_seal.csv | stage4b_machine_artifact |
| screening/codex/artifacts/stage4B_discovery/holm_adjusted_tests.csv | stage4b_bounded_analysis_machine_file |
| screening/codex/artifacts/stage4B_discovery/mode_execution_manifest.csv | stage4b_machine_manifest |
| screening/codex/artifacts/stage4B_discovery/mode_module_timing_characterization.csv | stage4b_timing_characterization |
| screening/codex/artifacts/stage4B_discovery/mode_per_frame_metrics.csv | stage4b_bounded_per_frame_metrics |
| screening/codex/artifacts/stage4B_discovery/module_timing_characterization.csv | stage4b_timing_characterization |
| screening/codex/artifacts/stage4B_discovery/no_ablation_parity.json | stage4b_parity_evidence |
| screening/codex/artifacts/stage4B_discovery/pair_level_A.csv | stage4b_bounded_analysis_machine_file |
| screening/codex/artifacts/stage4B_discovery/pair_level_B.csv | stage4b_bounded_analysis_machine_file |
| screening/codex/artifacts/stage4B_discovery/provenance_environment.json | stage4b_machine_artifact |
| screening/codex/artifacts/stage4B_discovery/retriever_mlp_per_frame_metrics.csv | stage4b_bounded_per_frame_metrics |
| screening/codex/artifacts/stage4B_discovery/sensitivity_results.csv | stage4b_machine_artifact |
| screening/codex/artifacts/stage4B_discovery/state_snapshot_parity.csv | stage4b_parity_evidence |
| screening/codex/artifacts/stage4B_discovery/t3_per_frame_metrics.csv | stage4b_bounded_per_frame_metrics |
| screening/codex/scripts/2026-08-26_stage4B_analyze.py | stage4b_reproducibility_script |
| screening/codex/scripts/2026-08-26_stage4B_execute_criterionA.py | stage4b_reproducibility_script |
| screening/codex/scripts/2026-08-26_stage4B_execute_criterionB.py | stage4b_reproducibility_script |
| screening/codex/scripts/2026-08-26_stage4B_execute_refinement.py | stage4b_reproducibility_script |
| screening/codex/scripts/2026-08-26_stage4B_finalize_report.py | stage4b_reproducibility_script |

The complete repository/external inventory is written to
`screening/codex/artifacts/stage4B_discovery/artifact_manifest.csv` with path,
scope, size, SHA-256, and committed/external classification. The manifest
excludes its own row because a stable file cannot contain its own SHA-256.
`COMMITTED` is used only for a clean tracked path at generation time;
new/staged/modified bounded paths are labeled `COMMIT_CANDIDATE`. Commit and
push state are reconciled separately after this report is generated.

## 20. Stage 4B conclusion

| Final field | Value |
| --- | --- |
| Frozen-slice validation | PASS |
| Discovery pairs executed | 12 |
| Hold-out pairs executed/accessed (maximum reported count) | 0 |
| Hold-out seal | PASS |
| No-ablation parity | PASS |
| State snapshot parity | PASS |
| Criterion A | PASS |
| IoU weakness | 0.136999 [0.001888, 0.317117] |
| Failure-rate weakness | 0.153333 [-0.030000, 0.418182] |
| Criterion B | PASS |
| Passing MRM/group | mrm1 |
| Holm correction | PASS |
| Selected refinement path | mrm1 |
| Stage 4B | `STAGE4B_AB_PASS_READY_FOR_MANAGER_REVIEW` |
| Stage 4C | `LOCKED` |
| Diagnostic decision | `NOT ASSIGNED` |
| S1-S7 | `NOT STARTED` |
| Primary shortlist | `NONE` |
| Main baseline | `NONE` |
| Proposed architecture | `NONE` |

STOP. Wait for Manager Stage-4B reconciliation.
