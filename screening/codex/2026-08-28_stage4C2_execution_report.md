# Stage 4C2 — one-shot frozen-predictor hold-out execution

## 1. Boundary and one-shot declaration

This run evaluated exactly the sealed Stage-4C2 hold-out once. It used only the official baseline and the sealed physical whole-MRM1 skip; it did not refit, invert, recalibrate, select a threshold, or execute another ablation.

## 2. Manager seal verification

Manager seal: **PASS**. All source, checkpoint, config, slice, patch, predictor, schema, and Stage-4C1 hold-out-seal hashes matched before any hold-out image was opened.

## 3. Frozen predictor numerical preflight

Preflight: **PASS**. Manual stable-sigmoid probabilities and the reconstructed, never-fit sklearn object differed by at most `1.1102230246251565e-16` on the existing discovery features (required `<= 1e-12`).

## 4. Unseal timeline

- Command log prepared before image access: `2026-08-28T16:34:48.363307+00:00`.
- Execution started: `2026-08-28T16:35:19.145853+00:00`.
- Frozen-frame outcome boundary unsealed: `2026-08-28T16:36:28.753048+00:00`.
- Execution completed: `2026-08-28T16:56:47.604146+00:00`.
- Hold-out evaluation count: **1**.

## 5. Exact hold-out execution coverage

Executed all 8 sealed pairs and 16 frozen intervals. Expected and observed oracle rows were both **326**. Unique source sequences: 9.

## 6. Sequence and snapshot contract

Each source sequence was initialized once at its official start, advanced by sequential baseline prefix, snapshotted at each `interval_start - 1`, branched from the identical complete state, and restored to the baseline end state for continuation. Snapshot schema: Stage-4B/C1 accepted complete state: tracker/model/template/retriever transients, Stage-4A/C1 history, and Python/NumPy/Torch CPU/all-CUDA RNG.

## 7. Physical call proof

Call proof: **PASS** across 326 physical frames. Every physical frame recorded MRM1 forward/Retriever/MLP/internal-operator counts of `0/0/0/0`; MRM2–MRM6 each remained at one call and matched baseline.

## 8. Feature-schema verification

Exactly 326 rows used the sealed 12 features in their exact order. Features were captured from the baseline pre-MRM1 state with the frozen cold-start/history semantics, without a second network pass. No GT, IoU, side, pair, sequence, class, stratum, ambiguity, or post-MRM value entered the predictor vector.

## 9. Oracle-label distribution

Positive labels: **161**. Negative labels: **165**. Base rate: `0.4938650306748466`. Exact ties were assigned label zero.

## 10. Complete-set AUROC

Frozen predictor AUROC: **0.481535855449**. Locked threshold: `0.65`. Probability orientation remained `P(oracle_skip_benefit > 0)` and was not inverted.

## 11. Predictor and constant Brier

- Frozen predictor Brier: `0.2575449361739645`.
- Constant comparator Brier: `0.24996241633654945`.
- Brier improvement (constant minus predictor): `-0.007582519837415064`.
- Descriptive ten-bin ECE: `0.05658282247976071`.

Fixed-bin calibration:

- Bin 0 [0.0, 0.1]: n=0, mean p=None, observed=None.
- Bin 1 [0.1, 0.2]: n=2, mean p=0.17833956771467857, observed=0.5.
- Bin 2 [0.2, 0.3]: n=2, mean p=0.23822222526361142, observed=0.5.
- Bin 3 [0.3, 0.4]: n=22, mean p=0.39408487394381436, observed=0.5454545454545454.
- Bin 4 [0.4, 0.5]: n=146, mean p=0.4494628426032055, observed=0.4931506849315068.
- Bin 5 [0.5, 0.6]: n=149, mean p=0.5309539443485439, observed=0.5033557046979866.
- Bin 6 [0.6, 0.7]: n=3, mean p=0.6183261991167327, observed=0.0.
- Bin 7 [0.7, 0.8]: n=1, mean p=0.7200293816220628, observed=0.0.
- Bin 8 [0.8, 0.9]: n=1, mean p=0.8834202742851996, observed=0.0.
- Bin 9 [0.9, 1.0]: n=0, mean p=None, observed=None.

## 12. Criterion-D decision

Criterion D: **FAIL**. Passing required both complete-set AUROC `>= 0.65` and strictly positive Brier improvement; no subgroup or interval was used to rescue the decision.

## 13. Locked sensitivity reports

All following results are descriptive and use only predeclared groups.

- `side=control`: n=163, AUROC=0.5959048479373683, Brier=0.246294460062, mean benefit=0.002695347198.
- `side=primary`: n=163, AUROC=0.3795961422543701, Brier=0.268795412286, mean benefit=-0.015415432214.
- `ambiguity_level=1`: n=132, AUROC=0.41470864661654133, Brier=0.255393240344, mean benefit=0.011935033670.
- `ambiguity_level=2`: n=194, AUROC=0.44954128440366975, Brier=0.259008976636, mean benefit=-0.018808238670.
- `sequence_relation=CROSS_SEQUENCE`: n=122, AUROC=0.44908405172413796, Brier=0.252043497067, mean benefit=-0.014107026230.
- `sequence_relation=SAME_SEQUENCE`: n=204, AUROC=0.4847640103816207, Brier=0.260835012503, mean benefit=-0.001727042439.
- `broad_superclass=FACE_HEAD`: n=60, AUROC=0.3382352941176471, Brier=0.260517064063, mean benefit=-0.042420072473.
- `broad_superclass=PERSON`: n=160, AUROC=0.44971804511278196, Brier=0.261914497042, mean benefit=0.003864474705.
- `broad_superclass=VEHICLE`: n=106, AUROC=0.542602495543672, Brier=0.249267036058, mean benefit=-0.001381938321.

The complete sensitivity CSV also includes frozen strata, pair, and pair-side rows.

## 14. Bootstrap sensitivity

Both primary-sequence and connected-source-component schemes used 10,000 cluster resamples with seed 20260828. Intervals are descriptive.

- `primary_sequence_clustered/auroc`: 95% percentile CI [0.395854462474645, 0.5365867077464789], valid=10000, invalid-one-class=0.
- `primary_sequence_clustered/frozen_predictor_brier`: 95% percentile CI [0.25082846158100974, 0.26393471460250584], valid=10000, invalid-one-class=0.
- `primary_sequence_clustered/constant_comparator_brier`: 95% percentile CI [0.24949827294210472, 0.25057687393638867], valid=10000, invalid-one-class=0.
- `primary_sequence_clustered/brier_improvement`: 95% percentile CI [-0.013718306169805239, -0.0009802549977089002], valid=10000, invalid-one-class=0.
- `primary_sequence_clustered/mean_oracle_skip_benefit`: 95% percentile CI [-0.023821167744002412, 0.013735786586579538], valid=10000, invalid-one-class=0.
- `connected_source_component_clustered/auroc`: 95% percentile CI [0.3520137784843667, 0.5314812367864693], valid=10000, invalid-one-class=0.
- `connected_source_component_clustered/frozen_predictor_brier`: 95% percentile CI [0.25212367447053685, 0.26583620245853085], valid=10000, invalid-one-class=0.
- `connected_source_component_clustered/constant_comparator_brier`: 95% percentile CI [0.2494832291216047, 0.2506846185055098], valid=10000, invalid-one-class=0.
- `connected_source_component_clustered/brier_improvement`: 95% percentile CI [-0.015918241679176937, -0.002365210620350915], valid=10000, invalid-one-class=0.
- `connected_source_component_clustered/mean_oracle_skip_benefit`: 95% percentile CI [-0.026681348774125917, 0.014983305825743974], valid=10000, invalid-one-class=0.

## 15. Efficiency characterization

- Baseline median model-forward time (feature capture included): `232.05159999633906` ms.
- Physical-skip median model-forward time (call counters included): `232.83005000121193` ms.
- Median measured feature-extraction overhead: `6.138349999673665` ms.
- Approximate feature-adjusted skip-path saving: `-2.9807163599197883`%.
- Maximum peak allocated/reserved memory: `139509248` / `165675008` bytes.

This is descriptive replication only; Criterion C was not reselected and no thresholded policy was executed.

## 16. Exact non-claims

- Final `DIAG_PASS`/`DIAG_FAIL`: **NOT ASSIGNED**.
- Stage 4D: **LOCKED PENDING MANAGER REVIEW**.
- S1–S7: **NOT STARTED**.
- Primary shortlist: **NONE**.
- Main baseline: **NONE**.
- Proposed architecture: **NONE**.
- Jetson claim: **NONE**.

## 17. Files produced

- `screening/codex/2026-08-28_stage4C2_execution_report.md`
- `screening/codex/2026-08-28_stage4C2_criterionD_results.csv`
- `screening/codex/2026-08-28_stage4C2_sensitivity_results.csv`
- `screening/codex/2026-08-28_stage4C2_command_log.txt`
- `screening/codex/artifacts/stage4C2_holdout/manager_seal_verification.json`
- `screening/codex/artifacts/stage4C2_holdout/frozen_predictor_numerical_preflight.json`
- `screening/codex/artifacts/stage4C2_holdout/one_shot_unseal_manifest.json`
- `screening/codex/artifacts/stage4C2_holdout/sequence_execution_manifest.csv`
- `screening/codex/artifacts/stage4C2_holdout/snapshot_and_call_proof.csv`
- `screening/codex/artifacts/stage4C2_holdout/baseline_and_skip_metrics.csv`
- `screening/codex/artifacts/stage4C2_holdout/frozen_feature_rows.csv`
- `screening/codex/artifacts/stage4C2_holdout/oracle_labels_and_probabilities.csv`
- `screening/codex/artifacts/stage4C2_holdout/criterionD_summary.json`
- `screening/codex/artifacts/stage4C2_holdout/bootstrap_results.csv`
- `screening/codex/artifacts/stage4C2_holdout/sensitivity_results.csv`
- `screening/codex/artifacts/stage4C2_holdout/timing_characterization.json`
- `screening/codex/artifacts/stage4C2_holdout/calibration_table.csv`
- `screening/codex/scripts/2026-08-28_stage4C2_preflight.py`
- `screening/codex/scripts/2026-08-28_stage4C2_one_shot_execute.py`
- `screening/codex/artifacts/stage4C2_holdout/artifact_manifest.csv`

## 18. Stage-4C2 conclusion

**STAGE4C2_CRITERION_D_FAIL**

Stop at the Manager Stage-4C2 and final diagnostic reconciliation boundary.
