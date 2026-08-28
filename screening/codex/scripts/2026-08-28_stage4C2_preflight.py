#!/usr/bin/env python3
"""Verify the Stage-4C2 seals and frozen predictor before hold-out unsealing."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from typing import Any

import numpy as np
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


DATE_PREFIX = "2026-08-28_stage4C2_"
SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
CHECKPOINT_SHA256 = (
    "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
)
CONFIG_SHA256 = (
    "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
)
SLICE_SHA256_LF = (
    "bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a"
)
PATCH_SHA256 = (
    "c2ccef6b07818ab3d08c99258f9e28abd0e6e7c56679a3573a4ca9e84f3938aa"
)
PREDICTOR_SHA256 = (
    "3be9039dceb2d9db4589edcb419232ec77d45ff36f1d779ae9a617ab03a9d0f2"
)
SCHEMA_SHA256 = (
    "260bdeecf5afa60bd79465863ce07ed194b6b6e327d7f32c8b5f17c75823a677"
)
STAGE4C1_SEAL_SHA256 = (
    "e51ff574e99b06d098987d9e7665939f04b881608083037293fa5774171f7d55"
)
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
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
EXPECTED_PATCHED_STATUS = {
    " M lib/models/spiketrack/sdtv3_search_inference.py",
    " M lib/models/spiketrack/spiketrack_inf.py",
    " M lib/test/parameter/spiketrack.py",
    " M lib/test/tracker/spiketrack_inf.py",
    "?? tracking/stage4a_spiketrack_smoke.py",
    "?? tracking/stage4c1_physical_smoke.py",
}


class PreflightError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--prepare-command-log", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_lf_sha256(path: Path) -> str:
    value = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(value).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_text_atomic(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def git_output(root: Path, *arguments: str) -> str:
    command = [
        "git", "-c", f"safe.directory={root.as_posix()}",
        "-C", str(root), *arguments,
    ]
    return subprocess.check_output(command, text=True).rstrip("\r\n")


def stable_sigmoid(logits: np.ndarray) -> np.ndarray:
    values = np.asarray(logits, dtype=np.float64)
    result = np.empty_like(values)
    positive = values >= 0.0
    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exponent = np.exp(values[~positive])
    result[~positive] = exponent / (1.0 + exponent)
    return result


def manual_probabilities(x: np.ndarray, predictor: dict[str, Any]) -> np.ndarray:
    mean = np.asarray(predictor["scaler"]["mean"], dtype=np.float64)
    scale = np.asarray(predictor["scaler"]["scale"], dtype=np.float64)
    coefficients = np.asarray(
        predictor["model"]["coefficients"], dtype=np.float64
    )
    intercept = float(predictor["model"]["intercept"])
    standardized = (x - mean) / scale
    return stable_sigmoid(intercept + standardized @ coefficients)


def reconstructed_sklearn_probabilities(
    x: np.ndarray, predictor: dict[str, Any]
) -> np.ndarray:
    scaler = StandardScaler(with_mean=True, with_std=True)
    scaler.mean_ = np.asarray(predictor["scaler"]["mean"], dtype=np.float64)
    scaler.scale_ = np.asarray(predictor["scaler"]["scale"], dtype=np.float64)
    scaler.var_ = np.asarray(predictor["scaler"]["var"], dtype=np.float64)
    scaler.n_features_in_ = len(FEATURE_ORDER)
    scaler.n_samples_seen_ = int(predictor["discovery"]["row_count"])

    model = LogisticRegression(
        penalty="l2",
        C=float(predictor["model"]["C"]),
        solver="lbfgs",
        class_weight=None,
        random_state=int(predictor["model"]["random_state"]),
        max_iter=int(predictor["model"]["max_iter"]),
        tol=float(predictor["model"]["tol"]),
    )
    model.classes_ = np.asarray(predictor["model"]["classes"], dtype=np.int64)
    model.coef_ = np.asarray(
        [predictor["model"]["coefficients"]], dtype=np.float64
    )
    model.intercept_ = np.asarray(
        [predictor["model"]["intercept"]], dtype=np.float64
    )
    model.n_features_in_ = len(FEATURE_ORDER)
    model.n_iter_ = np.asarray([predictor["model"]["n_iter"]], dtype=np.int32)
    return model.predict_proba(scaler.transform(x))[:, 1]


def canonical_slice_rows(path: Path) -> tuple[list[dict[str, str]], dict[str, str]]:
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    rows = list(csv.DictReader(normalized.decode("utf-8-sig").splitlines()))
    lines = normalized.splitlines(keepends=True)
    if len(lines) != len(rows) + 1:
        raise PreflightError("Frozen slice contains unexpected multiline CSV fields")
    hashes = {
        row["pair_id"]: hashlib.sha256(lines[index + 1]).hexdigest()
        for index, row in enumerate(rows)
    }
    return rows, hashes


def verify(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    codex = args.repo_root / "screening/codex"
    manager = args.repo_root / "screening/manager"
    predictor_path = codex / "2026-08-28_stage4C1_frozen_predictor.json"
    patch_path = codex / "patches/2026-08-28_stage4C1_physical_skip.patch"
    schema_path = codex / "artifacts/stage4C1_discovery/pre_mrm_feature_schema.json"
    seal_path = codex / "artifacts/stage4C1_discovery/stage4C1_holdout_seal.csv"
    features_path = codex / "artifacts/stage4C1_discovery/pre_mrm_features.csv"
    manager_seal_path = manager / "2026-08-28_stage4C2_predictor_seal.json"
    slice_path = manager / "2026-08-25_stage4_spiketrack_diagnostic_slice.csv"
    config_path = args.source_root / "experiments/spiketrack/spiketrack_s256_t1.yaml"
    for path in (
        predictor_path, patch_path, schema_path, seal_path, features_path,
        manager_seal_path, slice_path, config_path, args.checkpoint,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    manager_seal = json.loads(manager_seal_path.read_text(encoding="utf-8"))
    expected_hashes = {
        "source_sha": SOURCE_SHA,
        "checkpoint_sha256": CHECKPOINT_SHA256,
        "config_sha256": CONFIG_SHA256,
        "frozen_slice_sha256_normalized_lf": SLICE_SHA256_LF,
        "physical_skip_patch_sha256": PATCH_SHA256,
        "frozen_predictor_sha256": PREDICTOR_SHA256,
        "feature_schema_sha256": SCHEMA_SHA256,
        "stage4c1_holdout_seal_sha256": STAGE4C1_SEAL_SHA256,
    }
    for key, expected in expected_hashes.items():
        if manager_seal.get(key) != expected:
            raise PreflightError(f"Manager seal mismatch for {key}")
    observed_hashes = {
        "source_sha": git_output(args.source_root, "rev-parse", "HEAD"),
        "checkpoint_sha256": sha256_file(args.checkpoint),
        "config_sha256": sha256_file(config_path),
        "frozen_slice_sha256_normalized_lf": normalized_lf_sha256(slice_path),
        "physical_skip_patch_sha256": sha256_file(patch_path),
        "frozen_predictor_sha256": sha256_file(predictor_path),
        "feature_schema_sha256": sha256_file(schema_path),
        "stage4c1_holdout_seal_sha256": sha256_file(seal_path),
    }
    if observed_hashes != expected_hashes:
        differences = {
            key: {"expected": expected_hashes[key], "observed": observed_hashes[key]}
            for key in expected_hashes
            if expected_hashes[key] != observed_hashes[key]
        }
        raise PreflightError(f"Observed seal/hash mismatch: {differences}")

    status = set(git_output(args.source_root, "status", "--short").splitlines())
    if status != EXPECTED_PATCHED_STATUS:
        raise PreflightError(f"Patched source status mismatch: {sorted(status)}")
    if tuple(manager_seal["holdout_pair_ids"]) != EXPECTED_HOLDOUT_IDS:
        raise PreflightError("Manager hold-out ID allowlist mismatch")
    if tuple(manager_seal["feature_order"]) != FEATURE_ORDER:
        raise PreflightError("Manager feature order mismatch")

    slice_rows, row_hashes = canonical_slice_rows(slice_path)
    holdout_rows = [row for row in slice_rows if row["split"] == "HOLDOUT"]
    discovery_rows = [row for row in slice_rows if row["split"] == "DISCOVERY"]
    if tuple(row["pair_id"] for row in holdout_rows) != EXPECTED_HOLDOUT_IDS:
        raise PreflightError("Frozen slice hold-out ID/order mismatch")
    if len(discovery_rows) != 12 or len(holdout_rows) != 8:
        raise PreflightError("Frozen slice split counts mismatch")
    if sum(
        int(row["primary_end"]) - int(row["primary_start"]) + 1
        + int(row["control_end"]) - int(row["control_start"]) + 1
        for row in holdout_rows
    ) != 326:
        raise PreflightError("Frozen hold-out row total is not 326")
    discovery_sequences = {
        row[key] for row in discovery_rows
        for key in ("primary_sequence", "control_sequence")
    }
    holdout_sequences = {
        row[key] for row in holdout_rows
        for key in ("primary_sequence", "control_sequence")
    }
    if discovery_sequences & holdout_sequences:
        raise PreflightError("Discovery and hold-out sequences are not disjoint")

    prior_seal_rows = read_csv(seal_path)
    if tuple(row["pair_id"] for row in prior_seal_rows) != EXPECTED_HOLDOUT_IDS:
        raise PreflightError("Stage-4C1 seal ID/order mismatch")
    for row in prior_seal_rows:
        if row["status"] != "NOT_EXECUTED_STAGE4C1":
            raise PreflightError("Stage-4C1 hold-out seal is not intact")
        if row["frozen_row_sha256"] != row_hashes[row["pair_id"]]:
            raise PreflightError("Stage-4C1 frozen row hash mismatch")
        if row["frozen_slice_sha256"] != SLICE_SHA256_LF:
            raise PreflightError("Stage-4C1 slice hash mismatch")
        if row["physical_skip_patch_sha256"] != PATCH_SHA256:
            raise PreflightError("Stage-4C1 patch hash mismatch")
        if row["predictor_artifact_sha256"] != PREDICTOR_SHA256:
            raise PreflightError("Stage-4C1 predictor hash mismatch")
        if row["feature_schema_sha256"] != SCHEMA_SHA256:
            raise PreflightError("Stage-4C1 schema hash mismatch")

    predictor = json.loads(predictor_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if tuple(predictor["feature_order"]) != FEATURE_ORDER:
        raise PreflightError("Frozen predictor feature order mismatch")
    if tuple(schema["feature_order"]) != FEATURE_ORDER:
        raise PreflightError("Frozen schema feature order mismatch")
    if predictor["feature_schema"] != schema:
        raise PreflightError("Embedded/external feature schema mismatch")
    if float(predictor["model"]["C"]) != 0.01:
        raise PreflightError("Frozen C mutation")
    if float(predictor["constant_comparator_for_stage4c2"]["probability"]) != (
        0.49409780775716694
    ):
        raise PreflightError("Frozen constant comparator mutation")
    if len(predictor["scaler"]["mean"]) != 12:
        raise PreflightError("Frozen scaler mean length mismatch")
    if len(predictor["scaler"]["scale"]) != 12:
        raise PreflightError("Frozen scaler scale length mismatch")
    if len(predictor["model"]["coefficients"]) != 12:
        raise PreflightError("Frozen coefficient length mismatch")

    feature_rows = read_csv(features_path)
    if len(feature_rows) != 593:
        raise PreflightError("Discovery preflight feature row count mismatch")
    x = np.asarray(
        [[float(row[name]) for name in FEATURE_ORDER] for row in feature_rows],
        dtype=np.float64,
    )
    if not np.isfinite(x).all():
        raise PreflightError("Non-finite discovery preflight feature")
    manual = manual_probabilities(x, predictor)
    reconstructed = reconstructed_sklearn_probabilities(x, predictor)
    maximum_difference = float(np.max(np.abs(manual - reconstructed)))
    if maximum_difference > 1e-12:
        raise PreflightError(
            f"Frozen predictor numerical preflight failed: {maximum_difference}"
        )

    seal_verification = {
        "schema_version": "stage4c2-manager-seal-verification-v1",
        "status": "PASS",
        "manager_seal_status": manager_seal["status"],
        "manager_seal_path": str(manager_seal_path),
        "manager_seal_sha256": sha256_file(manager_seal_path),
        "expected_hashes": expected_hashes,
        "observed_hashes": observed_hashes,
        "source_patch_status": sorted(status),
        "expected_holdout_pair_ids": list(EXPECTED_HOLDOUT_IDS),
        "expected_holdout_frame_rows": 326,
        "discovery_holdout_sequence_disjoint": True,
        "holdout_outcomes_accessed": False,
    }
    numerical_preflight = {
        "schema_version": "stage4c2-frozen-predictor-preflight-v1",
        "status": "PASS",
        "implementation": "manual stable sigmoid versus reconstructed sklearn objects; no fit",
        "discovery_feature_rows": len(feature_rows),
        "feature_order": list(FEATURE_ORDER),
        "maximum_probability_difference": maximum_difference,
        "required_maximum_probability_difference": 1e-12,
        "manual_probability_minimum": float(manual.min()),
        "manual_probability_maximum": float(manual.max()),
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "refit_performed": False,
        "probability_inverted": False,
        "threshold_selected": False,
        "holdout_outcomes_accessed": False,
    }
    return seal_verification, numerical_preflight


def prepare_command_log(
    args: argparse.Namespace,
    seal_verification: dict[str, Any],
    numerical_preflight: dict[str, Any],
) -> None:
    codex = args.repo_root / "screening/codex"
    output_paths = [
        codex / "2026-08-28_stage4C2_execution_report.md",
        codex / "2026-08-28_stage4C2_criterionD_results.csv",
        codex / "2026-08-28_stage4C2_sensitivity_results.csv",
        codex / "2026-08-28_stage4C2_command_log.txt",
        args.artifact_root / "manager_seal_verification.json",
        args.artifact_root / "frozen_predictor_numerical_preflight.json",
        args.artifact_root / "one_shot_unseal_manifest.json",
        args.artifact_root / "sequence_execution_manifest.csv",
        args.artifact_root / "snapshot_and_call_proof.csv",
        args.artifact_root / "baseline_and_skip_metrics.csv",
        args.artifact_root / "frozen_feature_rows.csv",
        args.artifact_root / "oracle_labels_and_probabilities.csv",
        args.artifact_root / "criterionD_summary.json",
        args.artifact_root / "bootstrap_results.csv",
        args.artifact_root / "sensitivity_results.csv",
        args.artifact_root / "timing_characterization.json",
        args.artifact_root / "calibration_table.csv",
        args.artifact_root / "artifact_manifest.csv",
        codex / "scripts/2026-08-28_stage4C2_preflight.py",
        codex / "scripts/2026-08-28_stage4C2_one_shot_execute.py",
    ]
    execute_script = codex / "scripts/2026-08-28_stage4C2_one_shot_execute.py"
    command = (
        f"E:\\Robot_Backup\\tmp\\stage2B_spiketrack_env\\Scripts\\python.exe "
        f"{execute_script} --repo-root {args.repo_root} --source-root {args.source_root} "
        f"--dataset-root F:\\Q1_TrackingResearch_Data\\OTB100_Figshare_24427468_v1\\extracted\\OTB2015 "
        f"--checkpoint {args.checkpoint} --artifact-root {args.artifact_root} "
        f"--external-root {args.external_root} --seed 20260828 --execute-one-shot"
    )
    lines = [
        "Stage 4C2 one-shot command log",
        f"Prepared UTC: {datetime.now(timezone.utc).isoformat()}",
        "Scope: exact sealed eight-pair hold-out; execution count locked to one",
        "",
        "[Manager seal verification]",
        json.dumps(seal_verification, sort_keys=True),
        "",
        "[Frozen predictor numerical preflight]",
        json.dumps(numerical_preflight, sort_keys=True),
        "",
        "[Expected hold-out IDs]",
        ",".join(EXPECTED_HOLDOUT_IDS),
        "Expected complete frame rows: 326",
        "",
        "[Exact one-shot command]",
        command,
        "",
        "[Expected output paths]",
        *[str(path) for path in output_paths],
        "",
        "ONE_SHOT_HOLDOUT_NOT_YET_OPENED",
        "",
    ]
    write_text_atomic(codex / f"{DATE_PREFIX}command_log.txt", "\n".join(lines))


def main() -> None:
    args = parse_args()
    seal_verification, numerical_preflight = verify(args)
    args.artifact_root.mkdir(parents=True, exist_ok=True)
    args.external_root.mkdir(parents=True, exist_ok=True)
    write_json_atomic(
        args.artifact_root / "manager_seal_verification.json",
        seal_verification,
    )
    write_json_atomic(
        args.artifact_root / "frozen_predictor_numerical_preflight.json",
        numerical_preflight,
    )
    if args.prepare_command_log:
        prepare_command_log(args, seal_verification, numerical_preflight)
    print(json.dumps({
        "manager_seal": "PASS",
        "frozen_predictor_numerical_preflight": "PASS",
        "maximum_probability_difference": numerical_preflight[
            "maximum_probability_difference"
        ],
        "command_log_prepared": args.prepare_command_log,
        "holdout_outcomes_accessed": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
