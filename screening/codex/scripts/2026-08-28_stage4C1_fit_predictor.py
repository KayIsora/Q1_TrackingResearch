#!/usr/bin/env python3
"""Fit and freeze the locked Stage-4C1 discovery-only predictor."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import sys
import warnings
from typing import Any, Iterable

import numpy as np
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.preprocessing import StandardScaler


DATE_PREFIX = "2026-08-28_stage4C1_"
SEED = 20260828
C_GRID = (0.01, 0.1, 1.0, 10.0, 100.0)
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{index:02d}" for index in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
EXPECTED_COMPONENTS = {
    "component_01": ("R3-D01",),
    "component_02": ("R3-D02", "R3-D06"),
    "component_03": ("R3-D03", "R3-D04"),
    "component_04": ("R3-D05",),
    "component_05": ("R3-D07", "R3-D11"),
    "component_06": ("R3-D08",),
    "component_07": ("R3-D09",),
    "component_08": ("R3-D10",),
    "component_09": ("R3-D12",),
}
FEATURE_ORDER = (
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


class ContractError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--physical-patch", type=Path, required=True)
    parser.add_argument("--stage4b-holdout-seal", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv_atomic(path: Path, rows: Iterable[dict[str, Any]],
                     fields: tuple[str, ...]) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in materialized:
            writer.writerow({key: row.get(key) for key in fields})
    os.replace(temporary, path)


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1"}:
        return True
    if normalized in {"false", "0"}:
        return False
    raise ContractError(f"Invalid boolean value: {value!r}")


def fit_model(x: np.ndarray, y: np.ndarray, c_value: float) -> tuple[
    StandardScaler, LogisticRegression, list[str]
]:
    scaler = StandardScaler(with_mean=True, with_std=True)
    transformed = scaler.fit_transform(x)
    model = LogisticRegression(
        penalty="l2",
        C=c_value,
        solver="lbfgs",
        class_weight=None,
        random_state=SEED,
        max_iter=10000,
        tol=1e-12,
        fit_intercept=True,
    )
    messages: list[str] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(transformed, y)
    for item in caught:
        if issubclass(item.category, ConvergenceWarning):
            messages.append(str(item.message))
    if messages:
        raise ContractError(
            f"Logistic regression did not converge for C={c_value}: {messages}"
        )
    return scaler, model, messages


def calibration_summary(y: np.ndarray, probabilities: np.ndarray) -> dict[str, Any]:
    bins = []
    ece = 0.0
    for index in range(10):
        lower = index / 10.0
        upper = (index + 1) / 10.0
        if index == 9:
            mask = (probabilities >= lower) & (probabilities <= upper)
        else:
            mask = (probabilities >= lower) & (probabilities < upper)
        count = int(mask.sum())
        mean_probability = float(probabilities[mask].mean()) if count else None
        observed_rate = float(y[mask].mean()) if count else None
        if count:
            ece += (count / len(y)) * abs(mean_probability - observed_rate)
        bins.append({
            "bin_index": index,
            "lower_inclusive": lower,
            "upper_inclusive_only_for_last_bin": upper,
            "count": count,
            "mean_probability": mean_probability,
            "observed_positive_rate": observed_rate,
        })
    return {
        "method": "ten fixed equal-width probability bins",
        "expected_calibration_error": ece,
        "bins": bins,
    }


def numeric_vector(values: np.ndarray) -> list[float]:
    return [float(value) for value in np.asarray(values).reshape(-1)]


def main() -> None:
    args = parse_args()
    if args.seed != SEED:
        raise ContractError(f"Locked seed is {SEED}")
    features_path = args.artifact_root / "pre_mrm_features.csv"
    labels_path = args.artifact_root / "oracle_skip_labels.csv"
    schema_path = args.artifact_root / "pre_mrm_feature_schema.json"
    execution_path = args.artifact_root / "stage4C1_execution_summary.json"
    criterion_path = args.output_dir / f"{DATE_PREFIX}criterionC_results.csv"
    required = (
        features_path, labels_path, schema_path, execution_path, criterion_path,
        args.physical_patch, args.stage4b_holdout_seal,
    )
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(path)

    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    if execution.get("criterion_c", {}).get("criterion_c") != "PASS":
        raise ContractError("Criterion C is not PASS; predictor phase remains locked")
    if execution.get("holdout_pairs_executed") != 0:
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")
    if execution.get("holdout_outcomes_read") != 0:
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")
    if execution.get("feature_rows") != 593 or execution.get("oracle_rows") != 596:
        raise ContractError("Locked discovery feature/oracle coverage mismatch")
    for name, expected_hash in execution.get("output_hashes", {}).items():
        path = args.artifact_root / name
        if path.is_file() and sha256_file(path) != expected_hash:
            raise ContractError(f"Execution artifact hash mismatch: {name}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if tuple(schema.get("feature_order", ())) != FEATURE_ORDER:
        raise ContractError("Locked feature order mismatch")
    if schema.get("additional_network_pass") is not False:
        raise ContractError("Feature schema permits an additional network pass")

    feature_rows = read_csv(features_path)
    oracle_rows = read_csv(labels_path)
    if len(feature_rows) != 593 or len(oracle_rows) != 596:
        raise ContractError("Discovery row count mismatch")
    if any(parse_bool(row["holdout"]) for row in feature_rows + oracle_rows):
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")
    if tuple(sorted({row["pair_id"] for row in feature_rows})) != EXPECTED_DISCOVERY_IDS:
        raise ContractError("Discovery pair ID set mismatch")
    observed_components = {
        component: tuple(sorted({
            row["pair_id"] for row in feature_rows
            if row["connected_component"] == component
        }))
        for component in sorted({row["connected_component"] for row in feature_rows})
    }
    if observed_components != EXPECTED_COMPONENTS:
        raise ContractError("Locked connected-component assignment mismatch")

    oracle_by_key = {
        (row["pair_id"], row["side"], int(row["frame_index"])): row
        for row in oracle_rows if parse_bool(row["predictor_eligible"])
    }
    if len(oracle_by_key) != 593:
        raise ContractError("Predictor-eligible oracle key count mismatch")
    keys = [(row["pair_id"], row["side"], int(row["frame_index"]))
            for row in feature_rows]
    if len(set(keys)) != 593 or set(keys) != set(oracle_by_key):
        raise ContractError("Feature/oracle key coverage mismatch")
    for row, key in zip(feature_rows, keys):
        oracle = oracle_by_key[key]
        if int(row["oracle_label"]) != int(oracle["oracle_label"]):
            raise ContractError(f"Feature/oracle label mismatch at {key}")
        if float(row["oracle_skip_benefit"]) != float(oracle["oracle_skip_benefit"]):
            raise ContractError(f"Feature/oracle benefit mismatch at {key}")

    x = np.asarray([
        [float(row[name]) for name in FEATURE_ORDER] for row in feature_rows
    ], dtype=np.float64)
    y = np.asarray([int(row["oracle_label"]) for row in feature_rows], dtype=np.int64)
    groups = np.asarray(
        [row["connected_component"] for row in feature_rows], dtype=object
    )
    if not np.isfinite(x).all():
        raise ContractError("Non-finite locked predictor feature")
    positive_count = int(y.sum())
    negative_count = int(len(y) - positive_count)
    if positive_count < 20 or negative_count < 20:
        raise ContractError("PREDICTOR_LABEL_SUPPORT_INSUFFICIENT")

    results_by_c: dict[float, dict[str, Any]] = {}
    fold_records_by_c: dict[float, list[dict[str, Any]]] = {}
    components = tuple(sorted(EXPECTED_COMPONENTS))
    for c_value in C_GRID:
        probabilities = np.full(len(y), np.nan, dtype=np.float64)
        folds: list[dict[str, Any]] = []
        for fold_index, validation_component in enumerate(components, start=1):
            validation = groups == validation_component
            training = ~validation
            if len(np.unique(y[training])) != 2:
                raise ContractError(
                    f"Training fold lacks both labels: {validation_component}"
                )
            scaler, model, convergence_messages = fit_model(
                x[training], y[training], c_value
            )
            fold_probabilities = model.predict_proba(
                scaler.transform(x[validation])
            )[:, 1]
            probabilities[validation] = fold_probabilities
            folds.append({
                "fold_index": fold_index,
                "validation_component": validation_component,
                "validation_pair_ids": ";".join(EXPECTED_COMPONENTS[validation_component]),
                "training_rows": int(training.sum()),
                "validation_rows": int(validation.sum()),
                "training_positive": int(y[training].sum()),
                "training_negative": int(training.sum() - y[training].sum()),
                "validation_positive": int(y[validation].sum()),
                "validation_negative": int(validation.sum() - y[validation].sum()),
                "C": c_value,
                "solver": "lbfgs",
                "penalty": "l2",
                "class_weight": "NONE",
                "random_state": SEED,
                "n_iter": int(model.n_iter_[0]),
                "convergence_warnings": len(convergence_messages),
                "scaler_mean": json.dumps(numeric_vector(scaler.mean_)),
                "scaler_scale": json.dumps(numeric_vector(scaler.scale_)),
                "coefficients": json.dumps(numeric_vector(model.coef_[0])),
                "intercept": float(model.intercept_[0]),
            })
        if not np.isfinite(probabilities).all():
            raise ContractError(f"Incomplete OOF probabilities for C={c_value}")
        results_by_c[c_value] = {
            "probabilities": probabilities,
            "auroc": float(roc_auc_score(y, probabilities)),
            "brier": float(brier_score_loss(y, probabilities)),
        }
        fold_records_by_c[c_value] = folds

    selected_c = min(
        C_GRID,
        key=lambda value: (
            -results_by_c[value]["auroc"],
            results_by_c[value]["brier"],
            value,
        ),
    )
    selected_probabilities = results_by_c[selected_c]["probabilities"]
    hyperparameter_rows = []
    for c_value in C_GRID:
        result = results_by_c[c_value]
        hyperparameter_rows.append({
            "C": c_value,
            "pooled_oof_auroc": result["auroc"],
            "pooled_oof_brier": result["brier"],
            "fold_count": len(components),
            "oof_rows": len(y),
            "positive_rows": positive_count,
            "negative_rows": negative_count,
            "scaler": "StandardScaler",
            "model": "LogisticRegression",
            "solver": "lbfgs",
            "penalty": "l2",
            "class_weight": "NONE",
            "random_state": SEED,
            "selected": c_value == selected_c,
            "selection_rule": "max AUROC; tie min Brier; tie smaller C",
        })
    hyper_fields = tuple(hyperparameter_rows[0])
    hyper_path = args.output_dir / f"{DATE_PREFIX}predictor_hyperparameter_audit.csv"
    write_csv_atomic(hyper_path, hyperparameter_rows, hyper_fields)

    oof_rows = []
    for row, probability in zip(feature_rows, selected_probabilities):
        oof_rows.append({
            "pair_id": row["pair_id"],
            "side": row["side"],
            "sequence": row["sequence"],
            "frame_index": int(row["frame_index"]),
            "connected_component": row["connected_component"],
            "oracle_label": int(row["oracle_label"]),
            "oracle_skip_benefit": float(row["oracle_skip_benefit"]),
            "oof_skip_probability": float(probability),
            "selected_C": selected_c,
            "validation_scheme": "leave-one-connected-component-out",
            "threshold_selected": False,
            "holdout": False,
        })
    oof_fields = tuple(oof_rows[0])
    oof_path = args.output_dir / f"{DATE_PREFIX}predictor_oof_results.csv"
    write_csv_atomic(oof_path, oof_rows, oof_fields)

    fold_rows = fold_records_by_c[selected_c]
    fold_path = args.artifact_root / "predictor_grouped_folds.csv"
    write_csv_atomic(fold_path, fold_rows, tuple(fold_rows[0]))
    artifact_oof_path = args.artifact_root / "predictor_oof_probabilities.csv"
    artifact_hyper_path = args.artifact_root / "predictor_hyperparameter_audit.csv"
    write_csv_atomic(artifact_oof_path, oof_rows, oof_fields)
    write_csv_atomic(artifact_hyper_path, hyperparameter_rows, hyper_fields)

    final_scaler, final_model, _ = fit_model(x, y, selected_c)
    feature_overheads = np.asarray(
        [float(row["feature_extraction_ms"]) for row in feature_rows],
        dtype=np.float64,
    )
    input_hashes = execution["input_hashes"]
    frozen_payload = {
        "schema_version": "stage4c1-frozen-predictor-v1",
        "status": "FROZEN_DISCOVERY_ONLY_READY_FOR_MANAGER_REVIEW",
        "feature_schema": schema,
        "feature_schema_sha256": sha256_file(schema_path),
        "feature_order": list(FEATURE_ORDER),
        "scaler": {
            "class": "sklearn.preprocessing.StandardScaler",
            "with_mean": True,
            "with_std": True,
            "mean": numeric_vector(final_scaler.mean_),
            "scale": numeric_vector(final_scaler.scale_),
            "var": numeric_vector(final_scaler.var_),
        },
        "model": {
            "class": "sklearn.linear_model.LogisticRegression",
            "penalty": "l2",
            "solver": "lbfgs",
            "class_weight": None,
            "fit_intercept": True,
            "C": selected_c,
            "random_state": SEED,
            "max_iter": 10000,
            "tol": 1e-12,
            "coefficients": numeric_vector(final_model.coef_[0]),
            "intercept": float(final_model.intercept_[0]),
            "n_iter": int(final_model.n_iter_[0]),
            "classes": [int(value) for value in final_model.classes_],
        },
        "discovery": {
            "row_count": len(y),
            "group_count": len(components),
            "pair_count": len(EXPECTED_DISCOVERY_IDS),
            "positive_labels": positive_count,
            "negative_labels": negative_count,
            "positive_base_rate": float(y.mean()),
            "validation": "leave-one-connected-component-out",
            "oof_auroc": results_by_c[selected_c]["auroc"],
            "oof_brier": results_by_c[selected_c]["brier"],
            "calibration": calibration_summary(y, selected_probabilities),
        },
        "constant_comparator_for_stage4c2": {
            "probability": float(y.mean()),
            "definition": "frozen discovery positive base rate",
        },
        "feature_extraction_overhead_ms": {
            "row_count": len(feature_overheads),
            "mean": float(feature_overheads.mean()),
            "median": float(np.median(feature_overheads)),
            "p95": float(np.quantile(feature_overheads, 0.95)),
            "maximum": float(feature_overheads.max()),
            "additional_network_pass": False,
        },
        "provenance": {
            **input_hashes,
            "feature_csv_sha256": sha256_file(features_path),
            "oracle_csv_sha256": sha256_file(labels_path),
            "feature_schema_sha256": sha256_file(schema_path),
            "criterion_c_csv_sha256": sha256_file(criterion_path),
            "predictor_oof_csv_sha256": sha256_file(oof_path),
            "hyperparameter_audit_csv_sha256": sha256_file(hyper_path),
            "grouped_folds_csv_sha256": sha256_file(fold_path),
        },
        "versions": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "controls": {
            "no_class_weighting": True,
            "no_feature_selection": True,
            "no_nonlinear_model": True,
            "no_probability_threshold": True,
            "holdout_pairs_executed": 0,
            "holdout_outcomes_accessed": False,
            "stage4c2": "LOCKED",
        },
    }
    frozen_path = args.output_dir / f"{DATE_PREFIX}frozen_predictor.json"
    write_json_atomic(frozen_path, frozen_payload)
    predictor_hash = sha256_file(frozen_path)

    prior_seal_rows = read_csv(args.stage4b_holdout_seal)
    if tuple(row["pair_id"] for row in prior_seal_rows) != EXPECTED_HOLDOUT_IDS:
        raise ContractError("Stage-4B hold-out seal ID set/order mismatch")
    frozen_slice_hash = input_hashes["frozen_slice_sha256_normalized_lf"]
    patch_hash = sha256_file(args.physical_patch)
    if patch_hash != input_hashes["physical_skip_patch_sha256"]:
        raise ContractError("Physical-skip patch hash drift")
    holdout_rows = []
    for row in prior_seal_rows:
        if row["status"] != "NOT_EXECUTED_STAGE4B":
            raise ContractError("Prior hold-out seal is not intact")
        if row["frozen_slice_sha256_canonical_lf"] != frozen_slice_hash:
            raise ContractError("Prior hold-out seal slice hash mismatch")
        holdout_rows.append({
            "pair_id": row["pair_id"],
            "frozen_row_sha256": row["row_sha256_canonical_lf"],
            "frozen_slice_sha256": frozen_slice_hash,
            "physical_skip_patch_sha256": patch_hash,
            "predictor_artifact_sha256": predictor_hash,
            "feature_schema_sha256": sha256_file(schema_path),
            "status": "NOT_EXECUTED_STAGE4C1",
        })
    seal_path = args.artifact_root / "stage4C1_holdout_seal.csv"
    write_csv_atomic(seal_path, holdout_rows, tuple(holdout_rows[0]))

    manifest_payload = {
        "schema_version": "stage4c1-predictor-manifest-v1",
        "status": "STAGE4C1_PREDICTOR_FREEZE_READY_FOR_MANAGER_REVIEW",
        "selected_C": selected_c,
        "discovery_positive_labels": positive_count,
        "discovery_negative_labels": negative_count,
        "discovery_oof_auroc": results_by_c[selected_c]["auroc"],
        "discovery_oof_brier": results_by_c[selected_c]["brier"],
        "holdout_pairs_executed": 0,
        "holdout_outcomes_accessed": False,
        "holdout_seal": "PASS",
        "stage4c2": "LOCKED",
        "artifact_hashes": {
            path.name: sha256_file(path) for path in (
                features_path, labels_path, schema_path, execution_path,
                criterion_path, oof_path, hyper_path, frozen_path, fold_path,
                artifact_oof_path, artifact_hyper_path, seal_path,
                args.physical_patch,
            )
        },
    }
    manifest_path = args.artifact_root / "predictor_manifest.json"
    write_json_atomic(manifest_path, manifest_payload)
    print(json.dumps(manifest_payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
