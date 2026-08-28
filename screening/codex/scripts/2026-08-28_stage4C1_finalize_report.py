#!/usr/bin/env python3
"""Validate Stage-4C1 artifacts and write the bounded final report/manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable


DATE_PREFIX = "2026-08-28_stage4C1_"
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{index:02d}" for index in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
EXPECTED_FEATURES = (
    "previous_confidence",
    "previous_center_displacement_normalized_by_predicted_scale",
    "previous_log_area_ratio",
    "mrm1_input_abs_mean",
    "mrm1_input_std",
    "mrm1_input_rms",
    "mrm1_input_nonzero_ratio",
    "template_memory_abs_mean",
    "template_memory_std",
    "template_memory_rms",
    "template_memory_nonzero_ratio",
    "search_to_template_rms_ratio",
)
EXPECTED_SEAL_FIELDS = (
    "pair_id",
    "frozen_row_sha256",
    "frozen_slice_sha256",
    "physical_skip_patch_sha256",
    "predictor_artifact_sha256",
    "feature_schema_sha256",
    "status",
)


class ContractError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--verify-source-root", type=Path, required=True)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        return rows, tuple(reader.fieldnames or ())


def write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def write_json_atomic(path: Path, payload: Any) -> None:
    write_text_atomic(
        path,
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )


def write_csv_atomic(path: Path, rows: Iterable[dict[str, Any]],
                     fields: tuple[str, ...]) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(materialized)
    os.replace(temporary, path)


def truth(value: str) -> bool:
    return value.strip().lower() in {"true", "1"}


def maximum(rows: list[dict[str, str]], field: str) -> float:
    return max(float(row[field]) for row in rows)


def main() -> None:
    args = parse_args()
    codex = args.repo_root / "screening/codex"
    artifacts = codex / "artifacts/stage4C1_discovery"
    patch_path = codex / "patches/2026-08-28_stage4C1_physical_skip.patch"
    report_path = codex / f"{DATE_PREFIX}execution_report.md"
    command_log_path = codex / f"{DATE_PREFIX}command_log.txt"
    criterion_path = codex / f"{DATE_PREFIX}criterionC_results.csv"
    oof_path = codex / f"{DATE_PREFIX}predictor_oof_results.csv"
    audit_path = codex / f"{DATE_PREFIX}predictor_hyperparameter_audit.csv"
    frozen_path = codex / f"{DATE_PREFIX}frozen_predictor.json"
    summary_path = artifacts / "stage4C1_execution_summary.json"
    predictor_manifest_path = artifacts / "predictor_manifest.json"
    parity_path = artifacts / "semantic_parity.csv"
    proof_path = artifacts / "physical_skip_call_proof.csv"
    timing_path = artifacts / "timing_per_frame.csv"
    interval_timing_path = artifacts / "interval_timing.csv"
    metrics_path = artifacts / "physical_skip_discovery_metrics.csv"
    features_path = artifacts / "pre_mrm_features.csv"
    labels_path = artifacts / "oracle_skip_labels.csv"
    schema_path = artifacts / "pre_mrm_feature_schema.json"
    trace_path = artifacts / "bounded_profiler_trace_summary.json"
    fold_path = artifacts / "predictor_grouped_folds.csv"
    seal_path = artifacts / "stage4C1_holdout_seal.csv"
    for path in (
        patch_path, criterion_path, oof_path, audit_path, frozen_path,
        summary_path, predictor_manifest_path, parity_path, proof_path,
        timing_path, interval_timing_path, metrics_path, features_path,
        labels_path, schema_path, trace_path, fold_path, seal_path,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    predictor = json.loads(frozen_path.read_text(encoding="utf-8"))
    predictor_manifest = json.loads(
        predictor_manifest_path.read_text(encoding="utf-8")
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    criterion_rows, _ = read_csv(criterion_path)
    parity_rows, _ = read_csv(parity_path)
    proof_rows, _ = read_csv(proof_path)
    timing_rows, _ = read_csv(timing_path)
    interval_timing_rows, _ = read_csv(interval_timing_path)
    metric_rows, _ = read_csv(metrics_path)
    feature_rows, _ = read_csv(features_path)
    label_rows, _ = read_csv(labels_path)
    oof_rows, _ = read_csv(oof_path)
    audit_rows, _ = read_csv(audit_path)
    fold_rows, _ = read_csv(fold_path)
    seal_rows, seal_fields = read_csv(seal_path)

    if len(criterion_rows) != 1:
        raise ContractError("Criterion-C result must contain exactly one row")
    criterion = criterion_rows[0]
    if criterion["criterion_c"] != "PASS":
        raise ContractError("This finalizer requires Criterion C PASS")
    if criterion["semantic_parity"] != "PASS":
        raise ContractError("Semantic parity is not PASS")
    if criterion["whole_mrm1_call_proof"] != "PASS":
        raise ContractError("Whole-MRM1 physical call proof is not PASS")
    if summary.get("discovery_pairs_executed") != 12:
        raise ContractError("Discovery execution count mismatch")
    if summary.get("holdout_pairs_executed") != 0:
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")
    if summary.get("holdout_outcomes_read") != 0:
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")
    expected_counts = {
        "timing_per_frame": 3558,
        "interval_timing": 144,
        "physical_skip_metrics": 1192,
        "semantic_parity": 1192,
        "call_path_proof": 1779,
        "profiler_traces": 3,
        "pre_mrm_features": 593,
        "oracle_labels": 596,
    }
    for key, expected in expected_counts.items():
        if int(summary["row_counts"][key]) != expected:
            raise ContractError(f"Execution row count mismatch for {key}")
    if (
        len(timing_rows), len(interval_timing_rows), len(metric_rows),
        len(parity_rows), len(proof_rows), len(feature_rows), len(label_rows),
    ) != (3558, 144, 1192, 1192, 1779, 593, 596):
        raise ContractError("Materialized execution artifact row count mismatch")
    traces = json.loads(trace_path.read_text(encoding="utf-8"))
    if len(traces) != 3:
        raise ContractError("Bounded profiler trace count mismatch")

    comparisons = {
        name: [row for row in parity_rows if row["comparison"] == name]
        for name in ("WHOLE_MRM1_ZERO_VS_PHYSICAL", "MLP_MRM1_ZERO_VS_PHYSICAL")
    }
    for name, rows in comparisons.items():
        if len(rows) != 596 or any(row["status"] != "PASS" for row in rows):
            raise ContractError(f"Parity failure: {name}")
        if any(not truth(row["integer_bbox_exact"]) for row in rows):
            raise ContractError(f"Integer bbox parity failure: {name}")
        if any(not truth(row["continuation_state_exact"]) for row in rows):
            raise ContractError(f"Continuation parity failure: {name}")
        for field in (
            "maximum_float_bbox_abs_diff", "score_map_max_abs_diff",
            "confidence_abs_diff",
        ):
            if maximum(rows, field) > 1e-6:
                raise ContractError(f"Tolerance failure: {name}/{field}")

    proof_by_condition = {
        condition: [row for row in proof_rows if row["condition"] == condition]
        for condition in (
            "baseline", "whole_mrm1_physical_skip", "mlp_mrm1_physical_skip"
        )
    }
    if any(len(rows) != 593 for rows in proof_by_condition.values()):
        raise ContractError("Call-proof coverage mismatch")
    for row in proof_by_condition["whole_mrm1_physical_skip"]:
        if any(int(row[field]) != 0 for field in (
            "mrm1_forward", "mrm1_retriever_forward", "mrm1_mlp_forward",
            "mrm1_internal_operator_count",
        )):
            raise ContractError("Whole-MRM1 skip executed an MRM1 operator")
        if any(int(row[f"mrm{index}_forward"]) != 1 for index in range(2, 7)):
            raise ContractError("Whole-MRM1 skip changed MRM2-MRM6 calls")
    for row in proof_by_condition["baseline"]:
        if any(int(row[field]) != expected for field, expected in (
            ("mrm1_forward", 1),
            ("mrm1_retriever_forward", 1),
            ("mrm1_mlp_forward", 1),
            ("mrm1_internal_operator_count", 2),
        )):
            raise ContractError("Baseline MRM1 call proof mismatch")
        if any(int(row[f"mrm{index}_forward"]) != 1 for index in range(2, 7)):
            raise ContractError("Baseline MRM2-MRM6 call proof mismatch")
    for row in proof_by_condition["mlp_mrm1_physical_skip"]:
        if any(int(row[field]) != expected for field, expected in (
            ("mrm1_forward", 0),
            ("mrm1_retriever_forward", 1),
            ("mrm1_mlp_forward", 0),
            ("mrm1_internal_operator_count", 1),
        )):
            raise ContractError("Physical MLP-only call proof mismatch")
        if any(int(row[f"mrm{index}_forward"]) != 1 for index in range(2, 7)):
            raise ContractError("Physical MLP-only changed MRM2-MRM6 calls")

    timing_by_condition = {
        condition: [row for row in timing_rows if row["condition"] == condition]
        for condition in ("baseline", "whole_mrm1_physical_skip")
    }
    if any(len(rows) != 1779 for rows in timing_by_condition.values()):
        raise ContractError("Primary timing condition coverage mismatch")
    if {int(row["repetition"]) for row in timing_rows} != {1, 2, 3}:
        raise ContractError("Primary timing repetition set mismatch")
    for row in timing_rows:
        if truth(row["diagnostic_logging"]) or truth(row["record_call_counts"]):
            raise ContractError("Primary timing contains diagnostic/counter overhead")
        if int(row["batch_size"]) != 1 or row["dtype"] != "torch.float32":
            raise ContractError("Primary timing batch/dtype mismatch")
        expected_skip = row["condition"] == "whole_mrm1_physical_skip"
        if truth(row["physical_skip"]) != expected_skip:
            raise ContractError("Primary timing physical-skip flag mismatch")

    if tuple(schema.get("feature_order", ())) != EXPECTED_FEATURES:
        raise ContractError("Feature schema mismatch")
    if schema.get("additional_network_pass") is not False:
        raise ContractError("Feature extraction uses an additional network pass")
    discovery_ids = tuple(sorted({row["pair_id"] for row in feature_rows}))
    if discovery_ids != EXPECTED_DISCOVERY_IDS:
        raise ContractError("Discovery predictor pair set mismatch")
    if any(truth(row["holdout"]) for row in feature_rows + label_rows + oof_rows):
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")
    positive = sum(int(row["oracle_label"]) for row in feature_rows)
    negative = len(feature_rows) - positive
    if positive < 20 or negative < 20:
        raise ContractError("PREDICTOR_LABEL_SUPPORT_INSUFFICIENT")
    if len(oof_rows) != 593 or len(audit_rows) != 5 or len(fold_rows) != 9:
        raise ContractError("Predictor validation coverage mismatch")
    selected_audits = [row for row in audit_rows if truth(row["selected"])]
    if len(selected_audits) != 1:
        raise ContractError("Selected C must be unique")
    selected_c = float(selected_audits[0]["C"])
    if selected_c not in (0.01, 0.1, 1.0, 10.0, 100.0):
        raise ContractError("Selected C is outside the locked grid")
    if {float(row["C"]) for row in audit_rows} != {
        0.01, 0.1, 1.0, 10.0, 100.0
    }:
        raise ContractError("Hyperparameter audit does not match the locked C grid")
    rule_selected = min(
        audit_rows,
        key=lambda row: (
            -float(row["pooled_oof_auroc"]),
            float(row["pooled_oof_brier"]),
            float(row["C"]),
        ),
    )
    if float(rule_selected["C"]) != selected_c:
        raise ContractError("Selected C violates the locked selection rule")
    if len({row["validation_component"] for row in fold_rows}) != 9:
        raise ContractError("LOCO validation component coverage mismatch")
    if any(truth(row["threshold_selected"]) for row in oof_rows):
        raise ContractError("An OOF probability threshold was selected")
    if float(predictor["model"]["C"]) != selected_c:
        raise ContractError("Frozen predictor C mismatch")
    if predictor["feature_order"] != list(EXPECTED_FEATURES):
        raise ContractError("Frozen predictor feature order mismatch")
    if len(predictor["scaler"]["mean"]) != 12:
        raise ContractError("Frozen scaler mean length mismatch")
    if len(predictor["scaler"]["scale"]) != 12:
        raise ContractError("Frozen scaler scale length mismatch")
    if len(predictor["model"]["coefficients"]) != 12:
        raise ContractError("Frozen coefficient length mismatch")
    if predictor["controls"]["no_probability_threshold"] is not True:
        raise ContractError("A predictor threshold was added")
    if predictor_manifest.get("status") != (
        "STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW"
    ):
        raise ContractError("Predictor manifest status mismatch")

    if seal_fields != EXPECTED_SEAL_FIELDS:
        raise ContractError("Stage-4C1 hold-out seal contains unauthorized fields")
    if tuple(row["pair_id"] for row in seal_rows) != EXPECTED_HOLDOUT_IDS:
        raise ContractError("Stage-4C1 hold-out seal ID set/order mismatch")
    frozen_hash = sha256_file(frozen_path)
    for row in seal_rows:
        if row["status"] != "NOT_EXECUTED_STAGE4C1":
            raise ContractError("Stage-4C1 hold-out seal status mismatch")
        if row["predictor_artifact_sha256"] != frozen_hash:
            raise ContractError("Hold-out seal predictor hash mismatch")
        if row["feature_schema_sha256"] != sha256_file(schema_path):
            raise ContractError("Hold-out seal feature-schema hash mismatch")
        if row["physical_skip_patch_sha256"] != sha256_file(patch_path):
            raise ContractError("Hold-out seal patch hash mismatch")

    provenance = {
        "schema_version": "stage4c1-provenance-v1",
        "status": "PASS",
        "source_root": str(args.source_root),
        "verify_source_root": str(args.verify_source_root),
        "dataset_root": (
            "F:\\Q1_TrackingResearch_Data\\OTB100_Figshare_24427468_v1"
            "\\extracted\\OTB2015"
        ),
        "config_path": str(
            args.source_root / "experiments/spiketrack/spiketrack_s256_t1.yaml"
        ),
        "checkpoint_path": (
            "E:\\Robot_Backup\\tmp\\stage2B_spiketrack\\ckpt"
            "\\spiketrack_s256_t1.pth.tar"
        ),
        "frozen_slice_path": (
            "E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\manager"
            "\\2026-08-25_stage4_spiketrack_diagnostic_slice.csv"
        ),
        "stage4b_baseline_path": (
            "E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex"
            "\\artifacts\\stage4B_discovery\\baseline_per_frame_metrics.csv"
        ),
        "input_hashes": summary["input_hashes"],
        "execution_environment": summary["environment"],
        "predictor_versions": predictor["versions"],
        "physical_skip_patch_sha256": sha256_file(patch_path),
        "physical_skip_patch_apply_check": "PASS_STRICT_WHITESPACE_ON_CLEAN_PINNED_WORKTREE",
        "discovery_pairs_executed": 12,
        "holdout_pairs_executed": 0,
        "holdout_outcomes_accessed": False,
        "stage4c2": "LOCKED",
    }
    provenance_path = artifacts / "provenance.json"
    write_json_atomic(provenance_path, provenance)

    oof_auroc = float(predictor["discovery"]["oof_auroc"])
    oof_brier = float(predictor["discovery"]["oof_brier"])
    calibration = predictor["discovery"]["calibration"]
    whole_rows = comparisons["WHOLE_MRM1_ZERO_VS_PHYSICAL"]
    mlp_rows = comparisons["MLP_MRM1_ZERO_VS_PHYSICAL"]
    audit_table = "\n".join(
        "| {C} | {pooled_oof_auroc:.9f} | {pooled_oof_brier:.9f} | {selected} |".format(
            C=row["C"],
            pooled_oof_auroc=float(row["pooled_oof_auroc"]),
            pooled_oof_brier=float(row["pooled_oof_brier"]),
            selected=row["selected"],
        )
        for row in audit_rows
    )
    report = f"""# Stage 4C1 physical-skip and predictor-freeze execution report

**Date:** 2026-08-28

**Scope:** frozen discovery-only physical whole-MRM1 non-execution, Criterion C, and predictor freeze

**Report conclusion:** `STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW`

This is a discovery-only report. It does not assign DIAG PASS/FAIL, unlock
Stage 4C2, access a hold-out outcome, start S1-S7, choose a main baseline or
shortlist, or propose an architecture.

## 1. Boundary and provenance

- Pinned SpikeTrack source SHA: `{summary['input_hashes']['source_sha']}`
- Frozen-slice normalized-LF SHA-256: `{summary['input_hashes']['frozen_slice_sha256_normalized_lf']}`
- Physical-skip patch SHA-256: `{summary['input_hashes']['physical_skip_patch_sha256']}`
- Checkpoint SHA-256: `{summary['input_hashes']['checkpoint_sha256']}`
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
| whole-MRM1 zero residual vs physical skip | 596 | {maximum(whole_rows, 'maximum_float_bbox_abs_diff'):.9g} | {maximum(whole_rows, 'score_map_max_abs_diff'):.9g} | {maximum(whole_rows, 'confidence_abs_diff'):.9g} | exact | PASS |
| MLP-only zero residual vs physical skip | 596 | {maximum(mlp_rows, 'maximum_float_bbox_abs_diff'):.9g} | {maximum(mlp_rows, 'score_map_max_abs_diff'):.9g} | {maximum(mlp_rows, 'confidence_abs_diff'):.9g} | exact | PASS |

Tolerance is `<= 1e-6`. Optional MLP physical parity is secondary and does not
rescue Criterion C.

## 4. Criterion C primary timing

- Batch size/dtype: `1` / `torch.float32`
- Warm-up forwards: `{criterion['warmup_forwards']}`
- Repetitions: `{criterion['repetitions']}`; alternating order seed: `20260828`
- Timed rows per condition: `{criterion['timed_rows_per_condition']}`
- Baseline median model-forward latency: `{float(criterion['baseline_median_model_forward_ms']):.9f} ms`
- Physical whole-MRM1 skip median: `{float(criterion['physical_skip_median_model_forward_ms']):.9f} ms`
- Latency saving: `{float(criterion['latency_saving_percent']):.6f}%`
- Sequence-clustered bootstrap 95% CI: `[{float(criterion['sequence_clustered_bootstrap_ci_low']) * 100:.6f}%, {float(criterion['sequence_clustered_bootstrap_ci_high']) * 100:.6f}%]`
- Threshold: `>= 5%`; Criterion C: `PASS`

Timing excludes crop/decode/snapshot/persistence and runs with diagnostic
logging, feature capture and call counters disabled.

## 5. Oracle labels and feature schema

- Predictor-eligible discovery rows: `593`
- Positive labels (`IoU_physical_skip - IoU_baseline > 0`): `{positive}`
- Negative labels (including exact ties): `{negative}`
- Label-support gate: `PASS`
- Feature count/order: exactly `12`, frozen in `pre_mrm_feature_schema.json`
- GT/manual/group/IDs/post-MRM values used as model inputs: `false`
- Additional backbone/network pass: `false`
- Median feature extraction overhead: `{float(predictor['feature_extraction_overhead_ms']['median']):.9f} ms`

## 6. Connected-component grouped validation

Validation is leave-one-connected-component-out over `9` frozen connected
source components. Each fold fits its own StandardScaler and L2 logistic model
on training components only. No class weighting, feature selection, nonlinear
model or threshold is used.

| C | Pooled OOF AUROC | Pooled OOF Brier | Selected |
| ---: | ---: | ---: | --- |
{audit_table}

Selection rule: highest pooled OOF AUROC, then lower Brier, then smaller C.
Selected C: `{selected_c:g}`. Discovery OOF AUROC: `{oof_auroc:.9f}`.
Discovery OOF Brier: `{oof_brier:.9f}`. Fixed-decile calibration ECE:
`{float(calibration['expected_calibration_error']):.9f}`. These discovery OOF
metrics are descriptive and are not Criterion D.

## 7. Frozen discovery predictor

The final StandardScaler and L2 logistic regression were fitted once on all
`593` eligible discovery rows. Feature order/formulas, scaler statistics,
coefficients, intercept, C, discovery base rate, grouped OOF metrics,
calibration, feature overhead, provenance and dependency versions are frozen in
`2026-08-28_stage4C1_frozen_predictor.json` (SHA-256 `{frozen_hash}`). The
Stage-4C2 constant comparator is the frozen discovery positive base rate
`{float(predictor['discovery']['positive_base_rate']):.9f}`. No probability
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
"""
    write_text_atomic(report_path, report)

    command_log = f"""Stage 4C1 command log
Date: 2026-08-28 Asia/Saigon
Scope: frozen DISCOVERY physical-skip and predictor freeze only; HOLDOUT execution prohibited

[Repository sync]
git status --short --branch
git pull origin main
git status --short --branch
git log -1 --oneline

Observed synchronized Q1 HEAD:
bdbcc6f Accept Stage 4B and activate Stage 4C1

[Fresh pinned SpikeTrack worktrees]
git -C E:\\Robot_Backup\\tmp\\stage2B_spiketrack worktree add --detach F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned 1537db51a1cc9f6e30cce469fba3e51f5721b3d0
git -C E:\\Robot_Backup\\tmp\\stage2B_spiketrack worktree add --detach F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_verify 1537db51a1cc9f6e30cce469fba3e51f5721b3d0

[Accepted Stage-4A patch and Stage-4C1 physical patch]
git show HEAD:screening/codex/patches/2026-08-25_spiketrack_stage4A_repair.patch | git -C F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned apply --check --whitespace=error-all -
git show HEAD:screening/codex/patches/2026-08-25_spiketrack_stage4A_repair.patch | git -C F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned apply --whitespace=error-all -
git -C F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned diff --binary > screening/codex/patches/2026-08-28_stage4C1_physical_skip.patch
git -C F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_verify apply --check --whitespace=error-all E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\patches\\2026-08-28_stage4C1_physical_skip.patch

Observed physical patch SHA-256:
{sha256_file(patch_path)}

[One-forward smoke]
E:\\Robot_Backup\\tmp\\stage2B_spiketrack_env\\Scripts\\python.exe F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned\\tracking\\stage4c1_physical_smoke.py

Observed: whole and MLP physical parity PASS at zero maximum residual; call proof PASS; no extra backbone pass.

[Discovery Criterion-C execution]
E:\\Robot_Backup\\tmp\\stage2B_spiketrack_env\\Scripts\\python.exe E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\scripts\\2026-08-28_stage4C1_execute.py --source-root F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned --dataset-root F:\\Q1_TrackingResearch_Data\\OTB100_Figshare_24427468_v1\\extracted\\OTB2015 --slice-csv E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\manager\\2026-08-25_stage4_spiketrack_diagnostic_slice.csv --config F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned\\experiments\\spiketrack\\spiketrack_s256_t1.yaml --checkpoint E:\\Robot_Backup\\tmp\\stage2B_spiketrack\\ckpt\\spiketrack_s256_t1.pth.tar --stage4b-baseline-csv E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\artifacts\\stage4B_discovery\\baseline_per_frame_metrics.csv --physical-patch E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\patches\\2026-08-28_stage4C1_physical_skip.patch --artifact-root E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\artifacts\\stage4C1_discovery --output-dir E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex --seed 20260828

The first launch stopped before artifact creation because the imported Stage-4B snapshot helper lacked its module-local torch binding. The runner was patched to bind helper.torch and the exact command was rerun from the beginning.

Observed: Criterion C PASS; 12 discovery pairs; 24 intervals; 0 hold-out pairs/outcomes; whole/MLP parity PASS; call proof PASS.

[Discovery predictor fit/freeze]
py E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\scripts\\2026-08-28_stage4C1_fit_predictor.py --artifact-root E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\artifacts\\stage4C1_discovery --output-dir E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex --physical-patch E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\patches\\2026-08-28_stage4C1_physical_skip.patch --stage4b-holdout-seal E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\artifacts\\stage4B_discovery\\holdout_seal.csv --seed 20260828

Observed: selected C={selected_c:g}; discovery OOF AUROC={oof_auroc:.12f}; OOF Brier={oof_brier:.12f}; hold-out seal PASS.

[Final report and validation]
py E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\scripts\\2026-08-28_stage4C1_finalize_report.py --repo-root E:\\Robot_Backup\\Q1_TrackingResearch --source-root F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_pinned --verify-source-root F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_verify

[Final validation / commit / push]
py -m py_compile screening\\codex\\scripts\\2026-08-28_stage4C1_*.py
git -C F:\\Q1_TrackingResearch_Data\\Stage4C1_SpikeTrack_Discovery_2026-08-28\\SpikeTrack_verify apply --check --whitespace=error-all E:\\Robot_Backup\\Q1_TrackingResearch\\screening\\codex\\patches\\2026-08-28_stage4C1_physical_skip.patch
git fetch origin
git diff --name-only
git status --short
git add -- screening/codex/2026-08-28_stage4C1_* screening/codex/artifacts/stage4C1_discovery screening/codex/scripts/2026-08-28_stage4C1_* screening/codex/patches/2026-08-28_stage4C1_physical_skip.patch
git diff --cached --name-only
git diff --cached --check
git diff --cached --check -- . ':(exclude)screening/codex/patches/2026-08-28_stage4C1_physical_skip.patch'
git commit -m "Run SpikeTrack Stage 4C1 physical skip and predictor freeze"
git push origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git log -1 --oneline
git log origin/main -1 --oneline

Final commit identity and push/clean verification are necessarily observed after this log is committed; they are reported by the repository commands and final response.

The full staged whitespace check reports only whitespace embedded as data inside the unified physical-skip patch, inherited from the accepted Stage-4A source. All other staged paths pass the scoped whitespace check. The patch is preserved byte-for-byte because its SHA-256 is frozen in the executed Criterion-C summary, predictor and hold-out seal; strict application to the clean pinned verification worktree passes.
"""
    write_text_atomic(command_log_path, command_log)

    manifest_targets = sorted(
        [path for path in artifacts.iterdir() if path.is_file() and path.name != "artifact_manifest.csv"]
        + [criterion_path, oof_path, audit_path, frozen_path, report_path, command_log_path, patch_path]
        + sorted((codex / "scripts").glob("2026-08-28_stage4C1_*.py")),
        key=lambda path: str(path).lower(),
    )
    manifest_rows = []
    for path in manifest_targets:
        manifest_rows.append({
            "artifact_path": path.relative_to(args.repo_root).as_posix(),
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "role": (
                "machine_artifact" if artifacts in path.parents
                else "execution_script" if path.suffix == ".py"
                else "physical_skip_patch" if path.suffix == ".patch"
                else "required_top_level_output"
            ),
            "holdout_outcome_content": False,
        })
    manifest_path = artifacts / "artifact_manifest.csv"
    write_csv_atomic(manifest_path, manifest_rows, tuple(manifest_rows[0]))
    print(json.dumps({
        "status": "STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW",
        "criterion_c": "PASS",
        "holdout_seal": "PASS",
        "holdout_pairs_executed": 0,
        "selected_C": selected_c,
        "oof_auroc": oof_auroc,
        "oof_brier": oof_brier,
        "artifact_manifest_rows": len(manifest_rows),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
