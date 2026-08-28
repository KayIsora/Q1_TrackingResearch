# Stage 4C1 physical-skip and predictor-freeze execution report

**Date:** 2026-08-28

**Scope:** frozen discovery-only physical whole-MRM1 non-execution, Criterion C, and predictor freeze

**Report conclusion:** `STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW`

This is a discovery-only report. It does not assign DIAG PASS/FAIL, unlock
Stage 4C2, access a hold-out outcome, start S1-S7, choose a main baseline or
shortlist, or propose an architecture.

## 1. Boundary and provenance

- Pinned SpikeTrack source SHA: `1537db51a1cc9f6e30cce469fba3e51f5721b3d0`
- Frozen-slice normalized-LF SHA-256: `bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a`
- Physical-skip patch SHA-256: `c2ccef6b07818ab3d08c99258f9e28abd0e6e7c56679a3573a4ca9e84f3938aa`
- Checkpoint SHA-256: `cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df`
- Discovery pairs executed: `12`; frozen intervals: `24`
- Hold-out pairs executed: `0`; hold-out outcomes accessed: `false`

## 2. Physical whole-MRM1 call proof

Call proof is `PASS` over `593` tracked discovery frames. In the physical
whole-MRM1 branch, MRM1 forward, Retriever, MLP and internal-operator counts
are all exactly zero. MRM2-MRM6 each execute exactly once. The return occurs
before MRM1 Retriever/MLP execution. Three bounded profiler summaries are
retained, one per baseline/whole-skip/MLP-skip condition.

## 3. Semantic parity

| Comparison | Rows | Max float bbox diff | Max score diff | Max confidence diff | Integer/state parity | Status |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| whole-MRM1 zero residual vs physical skip | 596 | 0 | 0 | 0 | exact | PASS |
| MLP-only zero residual vs physical skip | 596 | 0 | 0 | 0 | exact | PASS |

Tolerance is `<= 1e-6`. Optional MLP physical parity is secondary and does not
rescue Criterion C.

## 4. Criterion C primary timing

- Batch size/dtype: `1` / `torch.float32`
- Warm-up forwards: `30`
- Repetitions: `3`; alternating order seed: `20260828`
- Timed rows per condition: `1779`
- Baseline median model-forward latency: `261.152799998 ms`
- Physical whole-MRM1 skip median: `246.887699999 ms`
- Latency saving: `5.462358%`
- Sequence-clustered bootstrap 95% CI: `[2.493581%, 8.461938%]`
- Threshold: `>= 5%`; Criterion C: `PASS`

Timing excludes crop/decode/snapshot/persistence and runs with diagnostic
logging, feature capture and call counters disabled.

## 5. Oracle labels and feature schema

- Predictor-eligible discovery rows: `593`
- Positive labels (`IoU_physical_skip - IoU_baseline > 0`): `293`
- Negative labels (including exact ties): `300`
- Label-support gate: `PASS`
- Feature count/order: exactly `12`, frozen in `pre_mrm_feature_schema.json`
- GT/manual/group/IDs/post-MRM values used as model inputs: `false`
- Additional backbone/network pass: `false`
- Median feature extraction overhead: `1.698000000 ms`

## 6. Connected-component grouped validation

Validation is leave-one-connected-component-out over `9` frozen connected
source components. Each fold fits its own StandardScaler and L2 logistic model
on training components only. No class weighting, feature selection, nonlinear
model or threshold is used.

| C | Pooled OOF AUROC | Pooled OOF Brier | Selected |
| ---: | ---: | ---: | --- |
| 0.01 | 0.471877133 | 0.257919686 | True |
| 0.1 | 0.468077361 | 0.261317155 | False |
| 1.0 | 0.459920364 | 0.266624362 | False |
| 10.0 | 0.462571104 | 0.270050000 | False |
| 100.0 | 0.464891923 | 0.273177580 | False |

Selection rule: highest pooled OOF AUROC, then lower Brier, then smaller C.
Selected C: `0.01`. Discovery OOF AUROC: `0.471877133`.
Discovery OOF Brier: `0.257919686`. Fixed-decile calibration ECE:
`0.049609807`. These discovery OOF
metrics are descriptive and are not Criterion D.

## 7. Frozen discovery predictor

The final StandardScaler and L2 logistic regression were fitted once on all
`593` eligible discovery rows. Feature order/formulas, scaler statistics,
coefficients, intercept, C, discovery base rate, grouped OOF metrics,
calibration, feature overhead, provenance and dependency versions are frozen in
`2026-08-28_stage4C1_frozen_predictor.json` (SHA-256 `3be9039dceb2d9db4589edcb419232ec77d45ff36f1d779ae9a617ab03a9d0f2`). The
Stage-4C2 constant comparator is the frozen discovery positive base rate
`0.494097808`. No probability
threshold is frozen.

## 8. Hold-out seal

The Stage-4C1 seal is `PASS`: exactly eight IDs and their frozen row hashes,
frozen-slice hash, physical-skip patch hash, predictor hash, feature-schema
hash and `NOT_EXECUTED_STAGE4C1` status. It contains no held-out prediction,
feature, IoU, label or timing result.

## 9. Artifact validation

- Timing rows: `3558`; interval timing rows: `144`
- Physical-skip metric rows: `1192`; parity rows: `1192`
- Call-proof rows: `1779`; profiler summaries: `3`
- Feature rows: `593`; oracle rows: `596`; selected OOF rows: `593`
- Grouped folds: `9`; hyperparameter rows: `5`
- Predictor manifest: `PASS`; provenance: `PASS`; artifact manifest: generated
- Repository whitespace check excluding the archival `.patch` payload: `PASS`.
  The full staged check reports whitespace preserved inside the unified patch
  from the accepted Stage-4A source; the patch is retained byte-for-byte because
  its SHA-256 is an executed/frozen provenance input, and strict clean-worktree
  patch-application validation passes.

## 10. Governance conclusion

`STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW`

- Stage 4C2: `LOCKED`
- Hold-out outcomes: `NOT ACCESSED`
- DIAG PASS/FAIL: `NOT ASSIGNED`
- S1-S7: `NOT STARTED`
- Primary shortlist: `NONE`
- Main baseline: `NONE`
- Proposed architecture: `NONE`

STOP. Wait for Manager Stage-4C1 reconciliation.
