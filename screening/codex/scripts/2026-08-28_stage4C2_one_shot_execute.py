#!/usr/bin/env python3
"""Execute the locked Stage-4C2 one-shot frozen hold-out validation."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import time
from types import MethodType, ModuleType
from typing import Any, Mapping, Sequence

import numpy as np


DATE_PREFIX = "2026-08-28_stage4C2_"
SEED = 20260828
EXPECTED_PAIR_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
EXPECTED_FRAME_ROWS = 326
CONSTANT_PROBABILITY = 0.49409780775716694
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
CONDITIONS = ("baseline", "whole_mrm1_physical_skip")
HOLDOUT_SOURCE_ALIASES = {
    "Human4_2": {
        "path": "Human4/img",
        "anno_path": "Human4/groundtruth_rect.2.txt",
    },
}
SNAPSHOT_SCHEMA = (
    "Stage-4B/C1 accepted complete state: tracker/model/template/retriever "
    "transients, Stage-4A/C1 history, and Python/NumPy/Torch CPU/all-CUDA RNG"
)


class Stage4C2Error(RuntimeError):
    pass


@dataclass(frozen=True)
class Interval:
    pair_id: str
    side: str
    sequence: str
    start: int
    end: int
    source_row_sha256: str
    primary_sequence: str
    control_sequence: str
    broad_superclass: str
    ambiguity_level: str
    sensitivity_stratum: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--dataset-root", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--artifact-root", type=Path)
    parser.add_argument("--external-root", type=Path)
    parser.add_argument("--seed", type=int, default=SEED)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--execute-one-shot", action="store_true")
    return parser.parse_args()


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Stage4C2Error(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_lf_sha256(path: Path) -> str:
    value = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(value).hexdigest()


def git_output(root: Path, *arguments: str) -> str:
    return subprocess.check_output(
        [
            "git", "-c", f"safe.directory={root.as_posix()}",
            "-C", str(root), *arguments,
        ],
        text=True,
    ).rstrip("\r\n")


def runtime_verify_without_sklearn(
    repo_root: Path, source_root: Path, checkpoint: Path, artifact_root: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Recheck all mutable inputs while preserving sklearn-free GPU execution."""
    codex = repo_root / "screening/codex"
    manager = repo_root / "screening/manager"
    manager_seal = json.loads(
        (manager / "2026-08-28_stage4C2_predictor_seal.json").read_text(
            encoding="utf-8"
        )
    )
    seal_verification = json.loads(
        (artifact_root / "manager_seal_verification.json").read_text(
            encoding="utf-8"
        )
    )
    numerical_preflight = json.loads(
        (artifact_root / "frozen_predictor_numerical_preflight.json").read_text(
            encoding="utf-8"
        )
    )
    if seal_verification.get("status") != "PASS":
        raise Stage4C2Error("Persisted Manager seal verification is not PASS")
    if numerical_preflight.get("status") != "PASS":
        raise Stage4C2Error("Persisted frozen predictor preflight is not PASS")
    if float(numerical_preflight["maximum_probability_difference"]) > 1e-12:
        raise Stage4C2Error("Persisted frozen predictor preflight exceeds tolerance")
    if numerical_preflight.get("holdout_outcomes_accessed") is not False:
        raise Stage4C2Error("Numerical preflight hold-out boundary mismatch")
    expected = {
        key: manager_seal[key]
        for key in (
            "source_sha", "checkpoint_sha256", "config_sha256",
            "frozen_slice_sha256_normalized_lf", "physical_skip_patch_sha256",
            "frozen_predictor_sha256", "feature_schema_sha256",
            "stage4c1_holdout_seal_sha256",
        )
    }
    observed = {
        "source_sha": git_output(source_root, "rev-parse", "HEAD"),
        "checkpoint_sha256": sha256_file(checkpoint),
        "config_sha256": sha256_file(
            source_root / "experiments/spiketrack/spiketrack_s256_t1.yaml"
        ),
        "frozen_slice_sha256_normalized_lf": normalized_lf_sha256(
            manager / "2026-08-25_stage4_spiketrack_diagnostic_slice.csv"
        ),
        "physical_skip_patch_sha256": sha256_file(
            codex / "patches/2026-08-28_stage4C1_physical_skip.patch"
        ),
        "frozen_predictor_sha256": sha256_file(
            codex / "2026-08-28_stage4C1_frozen_predictor.json"
        ),
        "feature_schema_sha256": sha256_file(
            codex / "artifacts/stage4C1_discovery/pre_mrm_feature_schema.json"
        ),
        "stage4c1_holdout_seal_sha256": sha256_file(
            codex / "artifacts/stage4C1_discovery/stage4C1_holdout_seal.csv"
        ),
    }
    if observed != expected or seal_verification.get("observed_hashes") != expected:
        raise Stage4C2Error("Runtime seal/hash verification mismatch")
    expected_status = {
        " M lib/models/spiketrack/sdtv3_search_inference.py",
        " M lib/models/spiketrack/spiketrack_inf.py",
        " M lib/test/parameter/spiketrack.py",
        " M lib/test/tracker/spiketrack_inf.py",
        "?? tracking/stage4a_spiketrack_smoke.py",
        "?? tracking/stage4c1_physical_smoke.py",
    }
    observed_status = set(git_output(source_root, "status", "--short").splitlines())
    if observed_status != expected_status:
        raise Stage4C2Error("Runtime sealed source worktree status mismatch")
    return seal_verification, numerical_preflight


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def append_log(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(f"{utc_now()} {line}\n")
        stream.flush()
        os.fsync(stream.fileno())


def csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return value


def write_csv_atomic(path: Path, rows: Sequence[Mapping[str, Any]],
                     fieldnames: Sequence[str] | None = None) -> None:
    if not rows and not fieldnames:
        raise Stage4C2Error(f"Cannot infer header for empty CSV: {path}")
    columns = list(fieldnames or rows[0].keys())
    for row in rows:
        extras = set(row) - set(columns)
        if extras:
            raise Stage4C2Error(f"Unexpected CSV fields in {path}: {sorted(extras)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: csv_value(row.get(name)) for name in columns})
    os.replace(temporary, path)


def stable_sigmoid(value: np.ndarray | float) -> np.ndarray:
    values = np.asarray(value, dtype=np.float64)
    result = np.empty_like(values)
    positive = values >= 0.0
    result[positive] = 1.0 / (1.0 + np.exp(-values[positive]))
    exponent = np.exp(values[~positive])
    result[~positive] = exponent / (1.0 + exponent)
    return result


def manual_probabilities(x: np.ndarray, predictor: Mapping[str, Any]) -> np.ndarray:
    mean = np.asarray(predictor["scaler"]["mean"], dtype=np.float64)
    scale = np.asarray(predictor["scaler"]["scale"], dtype=np.float64)
    coefficients = np.asarray(
        predictor["model"]["coefficients"], dtype=np.float64
    )
    intercept = float(predictor["model"]["intercept"])
    return stable_sigmoid(intercept + ((x - mean) / scale) @ coefficients)


def auroc(labels: np.ndarray, probabilities: np.ndarray) -> float | None:
    y = np.asarray(labels, dtype=np.int64)
    p = np.asarray(probabilities, dtype=np.float64)
    positives = int(y.sum())
    negatives = int(len(y) - positives)
    if positives == 0 or negatives == 0:
        return None
    order = np.argsort(p, kind="mergesort")
    sorted_p = p[order]
    ranks = np.empty(len(p), dtype=np.float64)
    index = 0
    while index < len(p):
        end = index + 1
        while end < len(p) and sorted_p[end] == sorted_p[index]:
            end += 1
        average_rank = 0.5 * ((index + 1) + end)
        ranks[order[index:end]] = average_rank
        index = end
    positive_rank_sum = float(ranks[y == 1].sum())
    return (
        positive_rank_sum - positives * (positives + 1) / 2.0
    ) / (positives * negatives)


def brier(labels: np.ndarray, probabilities: np.ndarray) -> float:
    return float(np.mean(np.square(
        np.asarray(probabilities, dtype=np.float64)
        - np.asarray(labels, dtype=np.float64)
    )))


def summarize_rows(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    labels = np.asarray([int(row["oracle_label"]) for row in rows], dtype=np.int64)
    probabilities = np.asarray(
        [float(row["frozen_predictor_probability"]) for row in rows],
        dtype=np.float64,
    )
    constants = np.full(len(rows), CONSTANT_PROBABILITY, dtype=np.float64)
    benefits = np.asarray(
        [float(row["oracle_skip_benefit"]) for row in rows], dtype=np.float64
    )
    predictor_brier = brier(labels, probabilities)
    constant_brier = brier(labels, constants)
    return {
        "row_count": len(rows),
        "positive_labels": int(labels.sum()),
        "negative_labels": int(len(labels) - labels.sum()),
        "positive_base_rate": float(labels.mean()) if len(labels) else None,
        "frozen_predictor_auroc": auroc(labels, probabilities),
        "frozen_predictor_brier": predictor_brier,
        "constant_comparator_brier": constant_brier,
        "brier_improvement": constant_brier - predictor_brier,
        "mean_oracle_skip_benefit": float(benefits.mean()) if len(benefits) else None,
        "mean_baseline_iou": (
            float(np.mean([float(row["iou_baseline"]) for row in rows]))
            if rows else None
        ),
        "mean_physical_skip_iou": (
            float(np.mean([
                float(row["iou_physical_whole_mrm1_skip"]) for row in rows
            ])) if rows else None
        ),
    }


def calibration_table(rows: Sequence[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], float]:
    labels = np.asarray([int(row["oracle_label"]) for row in rows], dtype=np.int64)
    probabilities = np.asarray(
        [float(row["frozen_predictor_probability"]) for row in rows],
        dtype=np.float64,
    )
    result: list[dict[str, Any]] = []
    weighted_gap = 0.0
    for bin_index in range(10):
        lower = bin_index / 10.0
        upper = (bin_index + 1) / 10.0
        mask = ((probabilities >= lower) & (probabilities < upper))
        if bin_index == 9:
            mask = (probabilities >= lower) & (probabilities <= upper)
        count = int(mask.sum())
        mean_probability = float(probabilities[mask].mean()) if count else None
        observed_rate = float(labels[mask].mean()) if count else None
        absolute_gap = (
            abs(mean_probability - observed_rate) if count else None
        )
        if count:
            weighted_gap += count * float(absolute_gap)
        result.append({
            "bin_index": bin_index,
            "lower_inclusive": lower,
            "upper_exclusive_except_last": upper,
            "count": count,
            "mean_probability": mean_probability,
            "observed_positive_rate": observed_rate,
            "absolute_calibration_gap": absolute_gap,
        })
    return result, weighted_gap / len(rows)


def metric_row(group_type: str, group_value: str,
               rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    summary = summarize_rows(rows)
    return {
        "group_type": group_type,
        "group_value": group_value,
        **summary,
        "physical_whole_mrm1_interaction": summary["mean_oracle_skip_benefit"],
        "descriptive_only": True,
    }


def build_sensitivity(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    specs: list[tuple[str, Any]] = [
        ("side", lambda row: row["side"]),
        ("ambiguity_level", lambda row: row["ambiguity_level"]),
        ("sequence_relation", lambda row: row["sequence_relation"]),
        ("broad_superclass", lambda row: row["broad_superclass"]),
        ("sensitivity_stratum", lambda row: row["sensitivity_stratum"]),
        ("pair_id", lambda row: row["pair_id"]),
        ("pair_side", lambda row: f"{row['pair_id']}:{row['side']}"),
    ]
    output = [metric_row("complete_set", "ALL", rows)]
    for group_type, accessor in specs:
        values = sorted({str(accessor(row)) for row in rows})
        for value in values:
            group_rows = [row for row in rows if str(accessor(row)) == value]
            output.append(metric_row(group_type, value, group_rows))
    return output


def derive_components(pair_rows: Sequence[Mapping[str, str]]) -> dict[str, str]:
    parents = {row["pair_id"]: row["pair_id"] for row in pair_rows}

    def find(item: str) -> str:
        while parents[item] != item:
            parents[item] = parents[parents[item]]
            item = parents[item]
        return item

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parents[max(left_root, right_root)] = min(left_root, right_root)

    for left_index, left in enumerate(pair_rows):
        left_sources = {left["primary_sequence"], left["control_sequence"]}
        for right in pair_rows[left_index + 1:]:
            right_sources = {right["primary_sequence"], right["control_sequence"]}
            if left_sources & right_sources:
                union(left["pair_id"], right["pair_id"])
    roots = sorted({find(pair_id) for pair_id in parents})
    names = {root: f"connected_component_{index:02d}"
             for index, root in enumerate(roots, start=1)}
    return {pair_id: names[find(pair_id)] for pair_id in sorted(parents)}


def bootstrap_summary(
    rows: Sequence[Mapping[str, Any]], cluster_field: str, scheme: str,
    seed: int, resamples: int = 10_000,
) -> list[dict[str, Any]]:
    clusters = sorted({str(row[cluster_field]) for row in rows})
    cluster_indices = {
        cluster: np.asarray([
            index for index, row in enumerate(rows)
            if str(row[cluster_field]) == cluster
        ], dtype=np.int64)
        for cluster in clusters
    }
    labels = np.asarray([int(row["oracle_label"]) for row in rows], dtype=np.int64)
    probabilities = np.asarray(
        [float(row["frozen_predictor_probability"]) for row in rows],
        dtype=np.float64,
    )
    benefits = np.asarray(
        [float(row["oracle_skip_benefit"]) for row in rows], dtype=np.float64
    )
    rng = np.random.default_rng(seed)
    values: dict[str, list[float]] = {
        "auroc": [],
        "frozen_predictor_brier": [],
        "constant_comparator_brier": [],
        "brier_improvement": [],
        "mean_oracle_skip_benefit": [],
    }
    invalid_auroc = 0
    for _ in range(resamples):
        sampled = rng.integers(0, len(clusters), size=len(clusters))
        indices = np.concatenate([cluster_indices[clusters[index]] for index in sampled])
        y = labels[indices]
        p = probabilities[indices]
        frozen_brier = brier(y, p)
        constant_brier = brier(y, np.full(len(y), CONSTANT_PROBABILITY))
        auc = auroc(y, p)
        if auc is None:
            invalid_auroc += 1
        else:
            values["auroc"].append(auc)
        values["frozen_predictor_brier"].append(frozen_brier)
        values["constant_comparator_brier"].append(constant_brier)
        values["brier_improvement"].append(constant_brier - frozen_brier)
        values["mean_oracle_skip_benefit"].append(float(benefits[indices].mean()))
    point = summarize_rows(rows)
    point_map = {
        "auroc": point["frozen_predictor_auroc"],
        "frozen_predictor_brier": point["frozen_predictor_brier"],
        "constant_comparator_brier": point["constant_comparator_brier"],
        "brier_improvement": point["brier_improvement"],
        "mean_oracle_skip_benefit": point["mean_oracle_skip_benefit"],
    }
    result = []
    for metric, samples in values.items():
        sample_array = np.asarray(samples, dtype=np.float64)
        result.append({
            "bootstrap_scheme": scheme,
            "cluster_field": cluster_field,
            "cluster_count": len(clusters),
            "metric": metric,
            "point_estimate": point_map[metric],
            "ci_percentile": 95,
            "ci_low": float(np.quantile(sample_array, 0.025)) if len(samples) else None,
            "ci_high": float(np.quantile(sample_array, 0.975)) if len(samples) else None,
            "resamples": resamples,
            "valid_resamples": len(samples),
            "invalid_one_class_resamples": invalid_auroc if metric == "auroc" else 0,
            "seed": seed,
            "descriptive_only": True,
        })
    return result


def parse_holdout_slice(path: Path) -> tuple[list[dict[str, str]], list[Interval]]:
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    lines = normalized.splitlines(keepends=True)
    rows = list(csv.DictReader(normalized.decode("utf-8-sig").splitlines()))
    if len(lines) != len(rows) + 1:
        raise Stage4C2Error("Unexpected multiline field in frozen slice")
    selected: list[dict[str, str]] = []
    hashes: dict[str, str] = {}
    for index, row in enumerate(rows):
        if row["split"] == "HOLDOUT":
            selected.append(row)
            hashes[row["pair_id"]] = hashlib.sha256(lines[index + 1]).hexdigest()
    if tuple(row["pair_id"] for row in selected) != EXPECTED_PAIR_IDS:
        raise Stage4C2Error("Frozen hold-out ID/order mismatch")
    intervals: list[Interval] = []
    for row in selected:
        shared = row["primary_sequence"] == row["control_sequence"]
        common = {
            "pair_id": row["pair_id"],
            "source_row_sha256": hashes[row["pair_id"]],
            "primary_sequence": row["primary_sequence"],
            "control_sequence": row["control_sequence"],
            "broad_superclass": row["broad_superclass"],
            "ambiguity_level": row["final_ambiguity_level"],
            "sensitivity_stratum": row["sensitivity_stratum"],
        }
        intervals.append(Interval(
            side="primary", sequence=row["primary_sequence"],
            start=int(row["primary_start"]), end=int(row["primary_end"]),
            **common,
        ))
        intervals.append(Interval(
            side="control", sequence=row["control_sequence"],
            start=int(row["control_start"]), end=int(row["control_end"]),
            **common,
        ))
        if shared and row["primary_start"] == row["control_start"]:
            raise Stage4C2Error(f"Degenerate same-sequence pair: {row['pair_id']}")
    observed_rows = sum(item.end - item.start + 1 for item in intervals)
    if len(intervals) != 16 or observed_rows != EXPECTED_FRAME_ROWS:
        raise Stage4C2Error(
            f"Hold-out interval contract mismatch: {len(intervals)}, {observed_rows}"
        )
    return selected, intervals


def frame_path(dataset_root: Path, info: Mapping[str, Any], frame: int) -> Path:
    return dataset_root / str(info["path"]) / (
        f"{frame:0{int(info['nz'])}d}.{info['ext']}"
    )


def read_selected_ground_truth(
    path: Path, official_start: int, requested_frames: set[int]
) -> dict[int, np.ndarray]:
    requested_lines = {frame - official_start: frame for frame in requested_frames}
    result: dict[int, np.ndarray] = {}
    with path.open("r", encoding="utf-8-sig") as stream:
        for line_index, raw_line in enumerate(stream):
            frame = requested_lines.get(line_index)
            if frame is None:
                continue
            fields = raw_line.strip().replace("\t", ",").split(",")
            if len(fields) < 4:
                fields = raw_line.split()
            values = np.asarray([float(value) for value in fields[:4]], dtype=np.float64)
            if values.shape != (4,) or not np.isfinite(values).all():
                raise Stage4C2Error(f"Invalid GT row for {path} frame {frame}")
            result[frame] = values
    missing = sorted(requested_frames - set(result))
    if missing:
        raise Stage4C2Error(f"Missing GT rows in {path}: {missing}")
    return result


def install_feature_timer(tracker: Any) -> None:
    encoder = tracker.network.encoder
    original = encoder._capture_stage4c1_pre_mrm1_features

    def timed_capture(this: Any, search: Any, cross_block_kv: Any) -> Any:
        started = time.perf_counter()
        result = original(search, cross_block_kv)
        this._stage4c2_last_feature_extraction_ms = (
            time.perf_counter() - started
        ) * 1000.0
        return result

    object.__setattr__(
        encoder,
        "_capture_stage4c1_pre_mrm1_features",
        MethodType(timed_capture, encoder),
    )
    encoder._stage4c2_last_feature_extraction_ms = None


def configure_tracker(c1: ModuleType, helper: ModuleType, tracker: Any,
                      physical_mode: str, capture_features: bool) -> None:
    c1.configure_stage4a(helper, tracker, False, "none")
    c1.configure_stage4c1(
        tracker,
        physical_mode=physical_mode,
        capture_features=capture_features,
        timing_enabled=True,
        record_call_counts=True,
    )


def validate_call_counts(rows: Sequence[Mapping[str, Any]]) -> None:
    baseline = [row for row in rows if row["condition"] == "baseline"]
    physical = [
        row for row in rows
        if row["condition"] == "whole_mrm1_physical_skip"
    ]
    if len(baseline) != EXPECTED_FRAME_ROWS or len(physical) != EXPECTED_FRAME_ROWS:
        raise Stage4C2Error("Call-proof coverage mismatch")
    for row in baseline:
        if not (
            int(row["mrm1_forward"]) == 1
            and int(row["mrm1_retriever_forward"]) == 1
            and int(row["mrm1_mlp_forward"]) == 1
            and int(row["mrm1_internal_operator_count"]) == 2
            and all(int(row[f"mrm{index}_forward"]) == 1 for index in range(2, 7))
        ):
            raise Stage4C2Error(f"Baseline call proof failed: {row}")
    for row in physical:
        if not (
            int(row["mrm1_forward"]) == 0
            and int(row["mrm1_retriever_forward"]) == 0
            and int(row["mrm1_mlp_forward"]) == 0
            and int(row["mrm1_internal_operator_count"]) == 0
            and all(int(row[f"mrm{index}_forward"]) == 1 for index in range(2, 7))
        ):
            raise Stage4C2Error(f"Physical call proof failed: {row}")


def make_report(
    *, conclusion: str, criterion: Mapping[str, Any], seal: Mapping[str, Any],
    numerical: Mapping[str, Any], unseal: Mapping[str, Any],
    sequence_manifest: Sequence[Mapping[str, Any]],
    call_rows: Sequence[Mapping[str, Any]], feature_rows: Sequence[Mapping[str, Any]],
    oracle_rows: Sequence[Mapping[str, Any]], sensitivity: Sequence[Mapping[str, Any]],
    bootstrap: Sequence[Mapping[str, Any]], timing: Mapping[str, Any],
    calibration: Sequence[Mapping[str, Any]], files: Sequence[Path],
) -> str:
    auc = criterion["frozen_predictor_auroc"]
    auc_text = "UNDEFINED" if auc is None else f"{float(auc):.12f}"
    sensitivity_lines = "\n".join(
        f"- `{row['group_type']}={row['group_value']}`: n={row['row_count']}, "
        f"AUROC={row['frozen_predictor_auroc']}, "
        f"Brier={float(row['frozen_predictor_brier']):.12f}, "
        f"mean benefit={float(row['mean_oracle_skip_benefit']):.12f}."
        for row in sensitivity
        if row["group_type"] in {"side", "ambiguity_level", "sequence_relation", "broad_superclass"}
    )
    bootstrap_lines = "\n".join(
        f"- `{row['bootstrap_scheme']}/{row['metric']}`: "
        f"95% percentile CI [{row['ci_low']}, {row['ci_high']}], "
        f"valid={row['valid_resamples']}, invalid-one-class={row['invalid_one_class_resamples']}."
        for row in bootstrap
    )
    file_lines = "\n".join(f"- `{path.as_posix()}`" for path in files)
    calibration_lines = "\n".join(
        f"- Bin {row['bin_index']} [{row['lower_inclusive']:.1f}, "
        f"{row['upper_exclusive_except_last']:.1f}]: n={row['count']}, "
        f"mean p={row['mean_probability']}, observed={row['observed_positive_rate']}."
        for row in calibration
    )
    return f"""# Stage 4C2 — one-shot frozen-predictor hold-out execution

## 1. Boundary and one-shot declaration

This run evaluated exactly the sealed Stage-4C2 hold-out once. It used only the official baseline and the sealed physical whole-MRM1 skip; it did not refit, invert, recalibrate, select a threshold, or execute another ablation.

## 2. Manager seal verification

Manager seal: **{seal['status']}**. All source, checkpoint, config, slice, patch, predictor, schema, and Stage-4C1 hold-out-seal hashes matched before any hold-out image was opened.

## 3. Frozen predictor numerical preflight

Preflight: **{numerical['status']}**. Manual stable-sigmoid probabilities and the reconstructed, never-fit sklearn object differed by at most `{numerical['maximum_probability_difference']}` on the existing discovery features (required `<= 1e-12`).

## 4. Unseal timeline

- Command log prepared before image access: `{unseal['command_log_prepared_utc']}`.
- Execution started: `{unseal['execution_started_utc']}`.
- Frozen-frame outcome boundary unsealed: `{unseal['first_frozen_frame_unsealed_utc']}`.
- Execution completed: `{unseal['execution_completed_utc']}`.
- Hold-out evaluation count: **1**.

## 5. Exact hold-out execution coverage

Executed all 8 sealed pairs and 16 frozen intervals. Expected and observed oracle rows were both **326**. Unique source sequences: {len(sequence_manifest)}.

## 6. Sequence and snapshot contract

Each source sequence was initialized once at its official start, advanced by sequential baseline prefix, snapshotted at each `interval_start - 1`, branched from the identical complete state, and restored to the baseline end state for continuation. Snapshot schema: {SNAPSHOT_SCHEMA}.

## 7. Physical call proof

Call proof: **PASS** across {len(call_rows) // 2} physical frames. Every physical frame recorded MRM1 forward/Retriever/MLP/internal-operator counts of `0/0/0/0`; MRM2–MRM6 each remained at one call and matched baseline.

## 8. Feature-schema verification

Exactly {len(feature_rows)} rows used the sealed 12 features in their exact order. Features were captured from the baseline pre-MRM1 state with the frozen cold-start/history semantics, without a second network pass. No GT, IoU, side, pair, sequence, class, stratum, ambiguity, or post-MRM value entered the predictor vector.

## 9. Oracle-label distribution

Positive labels: **{criterion['positive_labels']}**. Negative labels: **{criterion['negative_labels']}**. Base rate: `{criterion['positive_base_rate']}`. Exact ties were assigned label zero.

## 10. Complete-set AUROC

Frozen predictor AUROC: **{auc_text}**. Locked threshold: `0.65`. Probability orientation remained `P(oracle_skip_benefit > 0)` and was not inverted.

## 11. Predictor and constant Brier

- Frozen predictor Brier: `{criterion['frozen_predictor_brier']}`.
- Constant comparator Brier: `{criterion['constant_comparator_brier']}`.
- Brier improvement (constant minus predictor): `{criterion['brier_improvement']}`.
- Descriptive ten-bin ECE: `{criterion['expected_calibration_error']}`.

Fixed-bin calibration:

{calibration_lines}

## 12. Criterion-D decision

Criterion D: **{criterion['criterion_d']}**. Passing required both complete-set AUROC `>= 0.65` and strictly positive Brier improvement; no subgroup or interval was used to rescue the decision.

## 13. Locked sensitivity reports

All following results are descriptive and use only predeclared groups.

{sensitivity_lines}

The complete sensitivity CSV also includes frozen strata, pair, and pair-side rows.

## 14. Bootstrap sensitivity

Both primary-sequence and connected-source-component schemes used 10,000 cluster resamples with seed 20260828. Intervals are descriptive.

{bootstrap_lines}

## 15. Efficiency characterization

- Baseline median model-forward time (feature capture included): `{timing['baseline_median_model_forward_ms']}` ms.
- Physical-skip median model-forward time (call counters included): `{timing['physical_skip_median_model_forward_ms']}` ms.
- Median measured feature-extraction overhead: `{timing['median_feature_extraction_ms']}` ms.
- Approximate feature-adjusted skip-path saving: `{timing['approximate_feature_adjusted_skip_saving_percent']}`%.
- Maximum peak allocated/reserved memory: `{timing['maximum_peak_allocated_bytes']}` / `{timing['maximum_peak_reserved_bytes']}` bytes.

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

{file_lines}

## 18. Stage-4C2 conclusion

**{conclusion}**

Stop at the Manager Stage-4C2 and final diagnostic reconciliation boundary.
"""


def run_self_test() -> None:
    labels = np.asarray([0, 1, 0, 1], dtype=np.int64)
    probabilities = np.asarray([0.1, 0.5, 0.5, 0.9], dtype=np.float64)
    observed = auroc(labels, probabilities)
    expected = 0.875
    if observed is None or abs(observed - expected) > 1e-15:
        raise Stage4C2Error(f"AUROC self-test failed: {observed}, {expected}")
    synthetic = []
    for index, (label, probability) in enumerate(zip(labels, probabilities)):
        synthetic.append({
            "oracle_label": int(label),
            "frozen_predictor_probability": float(probability),
            "oracle_skip_benefit": 0.1 if label else -0.1,
            "iou_baseline": 0.4,
            "iou_physical_whole_mrm1_skip": 0.5 if label else 0.3,
            "side": "primary" if index % 2 == 0 else "control",
            "ambiguity_level": "1",
            "sequence_relation": "CROSS_SEQUENCE",
            "broad_superclass": "PERSON",
            "sensitivity_stratum": "SELF_TEST",
            "pair_id": f"T{index // 2}",
            "primary_sequence_cluster": f"S{index // 2}",
            "connected_source_component": f"C{index // 2}",
        })
    calibration, ece = calibration_table(synthetic)
    if sum(row["count"] for row in calibration) != len(synthetic) or not (0 <= ece <= 1):
        raise Stage4C2Error("Calibration self-test failed")
    if len(build_sensitivity(synthetic)) < 8:
        raise Stage4C2Error("Sensitivity self-test failed")
    boot = bootstrap_summary(
        synthetic, "primary_sequence_cluster", "self_test", SEED, resamples=200
    )
    if len(boot) != 5 or any(row["resamples"] != 200 for row in boot):
        raise Stage4C2Error("Bootstrap self-test failed")
    if auroc(np.zeros(3, dtype=np.int64), np.asarray([0.1, 0.2, 0.3])) is not None:
        raise Stage4C2Error("One-class AUROC self-test failed")
    print(json.dumps({
        "self_test": "PASS",
        "holdout_images_accessed": False,
        "auroc_tie_handling": "PASS",
        "calibration": "PASS",
        "sensitivity": "PASS",
        "bootstrap": "PASS",
    }, indent=2, sort_keys=True))


def run_environment_self_test(args: argparse.Namespace) -> None:
    """Load the sealed model and validate paths without opening any image."""
    required = (
        args.repo_root, args.source_root, args.dataset_root, args.checkpoint,
        args.artifact_root, args.external_root,
    )
    if any(value is None for value in required):
        return
    repo_root = args.repo_root.resolve()
    seal, numerical = runtime_verify_without_sklearn(
        repo_root, args.source_root, args.checkpoint, args.artifact_root
    )
    pair_rows, intervals = parse_holdout_slice(
        repo_root / "screening/manager/2026-08-25_stage4_spiketrack_diagnostic_slice.csv"
    )
    if len(derive_components(pair_rows)) != 8:
        raise Stage4C2Error("Environment self-test component map mismatch")
    codex_root = repo_root / "screening/codex"
    refinement = load_module(
        codex_root / "scripts/2026-08-26_stage4B_execute_refinement.py",
        "stage4c2_environment_refinement_helper",
    )
    sys.path.insert(0, str(args.source_root))
    import torch
    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.evaluation.otbdataset import OTBDataset
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    official = {row["name"]: dict(row) for row in OTBDataset._get_sequence_info_list(None)}
    for interval in intervals:
        info = dict(official[interval.sequence])
        info.update(HOLDOUT_SOURCE_ALIASES.get(interval.sequence, {}))
        for frame in range(int(info["startFrame"]), interval.end + 1):
            if not frame_path(args.dataset_root, info, frame).is_file():
                raise Stage4C2Error(
                    f"Environment self-test missing image path: {interval.sequence}/{frame}"
                )
        if not (args.dataset_root / str(info["anno_path"])).is_file():
            raise Stage4C2Error(
                f"Environment self-test missing GT path: {interval.sequence}"
            )
    tracker = refinement.make_tracker(
        cfg, update_config_from_file, SpikeTrack,
        args.source_root / "experiments/spiketrack/spiketrack_s256_t1.yaml",
        args.checkpoint, 1,
    )
    install_feature_timer(tracker)
    if not callable(tracker.network.encoder._capture_stage4c1_pre_mrm1_features):
        raise Stage4C2Error("Feature timer installation self-test failed")
    del tracker
    torch.cuda.empty_cache()
    print(json.dumps({
        "environment_self_test": "PASS",
        "manager_seal": seal["status"],
        "numerical_preflight": numerical["status"],
        "holdout_pairs": len(pair_rows),
        "holdout_intervals": len(intervals),
        "expected_rows": sum(item.end - item.start + 1 for item in intervals),
        "model_checkpoint_load": "PASS",
        "feature_timer_installation": "PASS",
        "holdout_images_opened": False,
        "holdout_ground_truth_opened": False,
    }, indent=2, sort_keys=True))


def run_one_shot(args: argparse.Namespace) -> None:
    required_args = (
        "repo_root", "source_root", "dataset_root", "checkpoint",
        "artifact_root", "external_root",
    )
    missing_args = [name for name in required_args if getattr(args, name) is None]
    if missing_args:
        raise Stage4C2Error(f"Missing execution arguments: {missing_args}")
    if args.seed != SEED:
        raise Stage4C2Error(f"Locked seed is {SEED}")

    repo_root = args.repo_root.resolve()
    codex_root = repo_root / "screening/codex"
    command_log = codex_root / f"{DATE_PREFIX}command_log.txt"
    unseal_path = args.artifact_root / "one_shot_unseal_manifest.json"
    if not command_log.is_file():
        raise Stage4C2Error("Command log was not prepared before execution")
    command_text = command_log.read_text(encoding="utf-8")
    if "ONE_SHOT_HOLDOUT_NOT_YET_OPENED" not in command_text:
        raise Stage4C2Error("Pre-unseal declaration missing from command log")
    technical_attempt = 1
    if unseal_path.exists():
        previous = json.loads(unseal_path.read_text(encoding="utf-8"))
        if previous.get("status") != "PRE_OUTCOME_FAILURE_ZERO_ROWS":
            raise Stage4C2Error(
                "One-shot guard: a prior unsealed or completed execution exists"
            )
        technical_attempt = int(previous.get("technical_attempt", 1)) + 1

    seal_verification, numerical_preflight = runtime_verify_without_sklearn(
        repo_root, args.source_root, args.checkpoint, args.artifact_root
    )
    if seal_verification["status"] != "PASS" or numerical_preflight["status"] != "PASS":
        raise Stage4C2Error("Seal or numerical preflight changed before execution")

    slice_path = repo_root / "screening/manager/2026-08-25_stage4_spiketrack_diagnostic_slice.csv"
    pair_rows, intervals = parse_holdout_slice(slice_path)
    components = derive_components(pair_rows)
    predictor = json.loads(
        (codex_root / "2026-08-28_stage4C1_frozen_predictor.json").read_text(
            encoding="utf-8"
        )
    )
    if tuple(predictor["feature_order"]) != FEATURE_ORDER:
        raise Stage4C2Error("Frozen predictor feature order changed")

    criterion_b_path = codex_root / "scripts/2026-08-26_stage4B_execute_criterionB.py"
    c1_path = codex_root / "scripts/2026-08-28_stage4C1_execute.py"
    refinement_path = codex_root / "scripts/2026-08-26_stage4B_execute_refinement.py"
    helper = load_module(criterion_b_path, "stage4c2_stage4b_helper")
    c1 = load_module(c1_path, "stage4c2_stage4c1_helper")
    refinement = load_module(refinement_path, "stage4c2_refinement_helper")

    sys.path.insert(0, str(args.source_root))
    import torch
    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.evaluation.otbdataset import OTBDataset
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    helper.torch = torch
    c1.configure_determinism(torch, args.seed)
    official = {row["name"]: dict(row) for row in OTBDataset._get_sequence_info_list(None)}
    for sequence_name, alias in HOLDOUT_SOURCE_ALIASES.items():
        if sequence_name in official:
            official[sequence_name].update(alias)
    intervals_by_sequence: dict[str, list[Interval]] = {}
    for interval in intervals:
        intervals_by_sequence.setdefault(interval.sequence, []).append(interval)
    for sequence_intervals in intervals_by_sequence.values():
        sequence_intervals.sort(key=lambda item: (item.start, item.end, item.pair_id, item.side))
        previous_end = -1
        for interval in sequence_intervals:
            if interval.start <= previous_end:
                raise Stage4C2Error(
                    f"Overlapping/reordered intervals for {interval.sequence}"
                )
            previous_end = interval.end
    if set(intervals_by_sequence) - set(official):
        raise Stage4C2Error("Frozen hold-out source missing from official OTB metadata")

    for sequence_name, sequence_intervals in intervals_by_sequence.items():
        info = official[sequence_name]
        official_start = int(info["startFrame"])
        requested = {official_start}
        for interval in sequence_intervals:
            requested.update(range(interval.start, interval.end + 1))
        if min(requested) < official_start or max(requested) > int(info["endFrame"]):
            raise Stage4C2Error(f"Frozen interval outside official bounds: {sequence_name}")
        missing_images = [
            frame for frame in range(official_start, max(requested) + 1)
            if not frame_path(args.dataset_root, info, frame).is_file()
        ]
        if missing_images:
            raise Stage4C2Error(
                f"Missing source images for {sequence_name}: {missing_images[:5]}"
            )
        if not (args.dataset_root / str(info["anno_path"])).is_file():
            raise Stage4C2Error(f"Missing official GT file: {sequence_name}")

    tracker = refinement.make_tracker(
        cfg, update_config_from_file, SpikeTrack,
        args.source_root / "experiments/spiketrack/spiketrack_s256_t1.yaml",
        args.checkpoint, 1,
    )
    install_feature_timer(tracker)
    args.artifact_root.mkdir(parents=True, exist_ok=True)
    args.external_root.mkdir(parents=True, exist_ok=True)
    command_log_prepared_utc = command_text.splitlines()[1].split("Prepared UTC: ", 1)[-1]
    unseal_manifest: dict[str, Any] = {
        "schema_version": "stage4c2-one-shot-unseal-v1",
        "status": "EXECUTION_STARTED_NO_FROZEN_OUTCOME_ROW",
        "technical_attempt": technical_attempt,
        "holdout_evaluation_count": 1,
        "expected_pair_ids": list(EXPECTED_PAIR_IDS),
        "expected_frame_rows": EXPECTED_FRAME_ROWS,
        "command_log_prepared_utc": command_log_prepared_utc,
        "execution_started_utc": utc_now(),
        "first_frozen_frame_unsealed_utc": None,
        "execution_completed_utc": None,
        "observed_frame_rows": 0,
        "frozen_predictor_mutation": "NONE",
    }
    write_json_atomic(unseal_path, unseal_manifest)
    append_log(command_log, f"ONE_SHOT_EXECUTION_STARTED technical_attempt={technical_attempt}")

    unsealed = False
    metric_rows: list[dict[str, Any]] = []
    feature_rows: list[dict[str, Any]] = []
    call_rows: list[dict[str, Any]] = []
    sequence_manifest: list[dict[str, Any]] = []
    first_outcome_utc: str | None = None

    try:
        for sequence_index, sequence_name in enumerate(sorted(intervals_by_sequence), start=1):
            info = official[sequence_name]
            official_start = int(info["startFrame"])
            sequence_intervals = intervals_by_sequence[sequence_name]
            gt_frames = {official_start}
            for interval in sequence_intervals:
                gt_frames.update(range(interval.start, interval.end + 1))
            ground_truth = read_selected_ground_truth(
                args.dataset_root / str(info["anno_path"]), official_start, gt_frames
            )
            configure_tracker(c1, helper, tracker, "none", False)
            tracker.initialize(
                helper.read_rgb(frame_path(args.dataset_root, info, official_start)),
                {"init_bbox": ground_truth[official_start].tolist()},
            )
            current_frame = official_start
            prefix_frames = 0
            snapshot_count = 0
            for interval in sequence_intervals:
                while current_frame < interval.start - 1:
                    current_frame += 1
                    configure_tracker(c1, helper, tracker, "none", False)
                    tracker.track(helper.read_rgb(
                        frame_path(args.dataset_root, info, current_frame)
                    ), {})
                    prefix_frames += 1
                start_snapshot = c1.capture_state(helper, tracker)
                start_hash = c1.state_hash(helper, start_snapshot)
                snapshot_count += 1
                branch_metrics: dict[str, list[dict[str, Any]]] = {}
                baseline_end_snapshot = None
                baseline_end_hash = None
                skip_end_hash = None
                for condition, physical_mode, capture_features in (
                    ("baseline", "none", True),
                    ("whole_mrm1_physical_skip", "whole_mrm1", False),
                ):
                    c1.restore_state(helper, tracker, start_snapshot)
                    configure_tracker(c1, helper, tracker, physical_mode, capture_features)
                    condition_rows: list[dict[str, Any]] = []
                    for frame in range(interval.start, interval.end + 1):
                        if not unsealed:
                            unsealed = True
                            first_outcome_utc = utc_now()
                            unseal_manifest["status"] = "ONE_SHOT_HOLDOUT_UNSEALED"
                            unseal_manifest["first_frozen_frame_unsealed_utc"] = first_outcome_utc
                            write_json_atomic(unseal_path, unseal_manifest)
                            append_log(
                                command_log,
                                "ONE_SHOT_HOLDOUT_UNSEALED before first frozen-frame forward",
                            )
                        tracker.network.encoder._stage4c2_last_feature_extraction_ms = None
                        output = tracker.track(helper.read_rgb(
                            frame_path(args.dataset_root, info, frame)
                        ), {})[0]
                        float_box = np.asarray(output["target_bbox"], dtype=np.float64)
                        int_box = float_box.astype(np.int64)
                        gt_box = ground_truth[frame]
                        condition_rows.append({
                            "pair_id": interval.pair_id,
                            "side": interval.side,
                            "sequence": interval.sequence,
                            "frame_index": frame,
                            "condition": condition,
                            "iou": helper.inclusive_iou(int_box, gt_box),
                            "iou_float": helper.inclusive_iou(float_box, gt_box),
                            "pred_x_float": float_box[0],
                            "pred_y_float": float_box[1],
                            "pred_w_float": float_box[2],
                            "pred_h_float": float_box[3],
                            "pred_x_int": int_box[0],
                            "pred_y_int": int_box[1],
                            "pred_w_int": int_box[2],
                            "pred_h_int": int_box[3],
                            "gt_x": gt_box[0],
                            "gt_y": gt_box[1],
                            "gt_w": gt_box[2],
                            "gt_h": gt_box[3],
                            "model_forward_ms": tracker.stage4c1_last_model_forward_ms,
                            "peak_allocated_bytes": tracker.stage4c1_last_peak_allocated_bytes,
                            "peak_reserved_bytes": tracker.stage4c1_last_peak_reserved_bytes,
                            "feature_capture_included": capture_features,
                            "call_counter_included": True,
                            "physical_skip": physical_mode == "whole_mrm1",
                        })
                        counts = dict(tracker.stage4c1_last_call_counts)
                        call_rows.append({
                            "pair_id": interval.pair_id,
                            "side": interval.side,
                            "sequence": interval.sequence,
                            "frame_index": frame,
                            "condition": condition,
                            "snapshot_at_frame": interval.start - 1,
                            "start_snapshot_sha256": start_hash,
                            **counts,
                        })
                        if capture_features:
                            records = tracker.consume_stage4c1_feature_records()
                            if len(records) != 1:
                                raise Stage4C2Error(
                                    f"Expected one feature record at {interval.pair_id}/"
                                    f"{interval.side}/{frame}; got {len(records)}"
                                )
                            record = records[0]
                            vector = [float(record[name]) for name in FEATURE_ORDER]
                            if not np.isfinite(np.asarray(vector)).all():
                                raise Stage4C2Error("Non-finite frozen feature")
                            feature_ms = (
                                tracker.network.encoder._stage4c2_last_feature_extraction_ms
                            )
                            if feature_ms is None or not math.isfinite(float(feature_ms)):
                                raise Stage4C2Error("Feature extraction timer missing")
                            feature_rows.append({
                                "pair_id": interval.pair_id,
                                "side": interval.side,
                                "sequence": interval.sequence,
                                "frame_index": frame,
                                "feature_order": list(FEATURE_ORDER),
                                **{name: vector[index] for index, name in enumerate(FEATURE_ORDER)},
                                "feature_extraction_ms": float(feature_ms),
                                "physical_mode": "none",
                                "additional_network_pass": False,
                                "holdout_outcome_input_used": False,
                            })
                    branch_metrics[condition] = condition_rows
                    end_snapshot = c1.normalized_end_state(helper, tracker)
                    end_hash = c1.state_hash(helper, end_snapshot)
                    if condition == "baseline":
                        baseline_end_snapshot = end_snapshot
                        baseline_end_hash = end_hash
                    else:
                        skip_end_hash = end_hash
                if baseline_end_snapshot is None or baseline_end_hash is None:
                    raise Stage4C2Error("Missing baseline continuation state")
                c1.restore_state(helper, tracker, baseline_end_snapshot)
                if c1.state_hash(helper, c1.capture_state(helper, tracker)) != baseline_end_hash:
                    raise Stage4C2Error("Baseline continuation restore mismatch")
                current_frame = interval.end
                metric_rows.extend(branch_metrics["baseline"])
                metric_rows.extend(branch_metrics["whole_mrm1_physical_skip"])
                for row in call_rows[-2 * (interval.end - interval.start + 1):]:
                    row["baseline_end_snapshot_sha256"] = baseline_end_hash
                    row["physical_skip_end_snapshot_sha256"] = skip_end_hash
                    row["snapshot_schema"] = SNAPSHOT_SCHEMA
                print(
                    f"PROGRESS {sequence_index}/{len(intervals_by_sequence)} "
                    f"{interval.pair_id}/{interval.side} {sequence_name} "
                    f"frames={interval.start}-{interval.end}",
                    flush=True,
                )
            sequence_manifest.append({
                "sequence": sequence_name,
                "official_start_frame": official_start,
                "maximum_frozen_frame": max(item.end for item in sequence_intervals),
                "initialized_once": True,
                "initialization_frame": official_start,
                "sequential_prefix_frames_executed": prefix_frames,
                "frozen_intervals_executed": len(sequence_intervals),
                "snapshots_taken": snapshot_count,
                "baseline_continuation_restored": True,
                "non_frozen_metrics_written": 0,
            })

        expected_metric_keys = {
            (interval.pair_id, interval.side, frame, condition)
            for interval in intervals
            for frame in range(interval.start, interval.end + 1)
            for condition in CONDITIONS
        }
        observed_metric_keys = {
            (row["pair_id"], row["side"], int(row["frame_index"]), row["condition"])
            for row in metric_rows
        }
        if len(metric_rows) != 2 * EXPECTED_FRAME_ROWS or observed_metric_keys != expected_metric_keys:
            raise Stage4C2Error("Baseline/skip metric coverage mismatch")
        feature_keys = {
            (row["pair_id"], row["side"], int(row["frame_index"]))
            for row in feature_rows
        }
        expected_feature_keys = {
            (interval.pair_id, interval.side, frame)
            for interval in intervals
            for frame in range(interval.start, interval.end + 1)
        }
        if len(feature_rows) != EXPECTED_FRAME_ROWS or feature_keys != expected_feature_keys:
            raise Stage4C2Error("Frozen feature coverage mismatch")
        validate_call_counts(call_rows)

        metrics_by_key = {
            (row["pair_id"], row["side"], int(row["frame_index"]), row["condition"]): row
            for row in metric_rows
        }
        features_by_key = {
            (row["pair_id"], row["side"], int(row["frame_index"])): row
            for row in feature_rows
        }
        pair_metadata = {row["pair_id"]: row for row in pair_rows}
        x = np.asarray([
            [float(features_by_key[key][name]) for name in FEATURE_ORDER]
            for key in sorted(features_by_key)
        ], dtype=np.float64)
        probabilities = manual_probabilities(x, predictor)
        oracle_rows: list[dict[str, Any]] = []
        for key, probability in zip(sorted(features_by_key), probabilities):
            pair_id, side, frame = key
            baseline = metrics_by_key[(pair_id, side, frame, "baseline")]
            skip = metrics_by_key[(pair_id, side, frame, "whole_mrm1_physical_skip")]
            benefit = float(skip["iou"]) - float(baseline["iou"])
            metadata = pair_metadata[pair_id]
            oracle_rows.append({
                "pair_id": pair_id,
                "side": side,
                "sequence": baseline["sequence"],
                "frame_index": frame,
                "primary_sequence": metadata["primary_sequence"],
                "control_sequence": metadata["control_sequence"],
                "primary_sequence_cluster": metadata["primary_sequence"],
                "connected_source_component": components[pair_id],
                "sequence_relation": (
                    "SAME_SEQUENCE" if metadata["primary_sequence"] == metadata["control_sequence"]
                    else "CROSS_SEQUENCE"
                ),
                "ambiguity_level": metadata["final_ambiguity_level"],
                "broad_superclass": metadata["broad_superclass"],
                "sensitivity_stratum": metadata["sensitivity_stratum"],
                "iou_baseline": baseline["iou"],
                "iou_physical_whole_mrm1_skip": skip["iou"],
                "oracle_skip_benefit": benefit,
                "oracle_label": int(benefit > 0.0),
                "exact_tie_is_negative": benefit == 0.0,
                "frozen_predictor_probability": float(probability),
                "constant_probability": CONSTANT_PROBABILITY,
                "probability_orientation": "P(oracle_skip_benefit > 0)",
                "probability_inverted": False,
                "threshold_selected": False,
                "refit_performed": False,
            })
        if len(oracle_rows) != EXPECTED_FRAME_ROWS:
            raise Stage4C2Error("Oracle/probability coverage mismatch")

        complete = summarize_rows(oracle_rows)
        calibration, ece = calibration_table(oracle_rows)
        complete["expected_calibration_error"] = ece
        complete["auroc_threshold"] = 0.65
        complete["brier_improvement_required_strictly_positive"] = True
        complete["criterion_d"] = (
            "PASS"
            if complete["frozen_predictor_auroc"] is not None
            and float(complete["frozen_predictor_auroc"]) >= 0.65
            and float(complete["brier_improvement"]) > 0.0
            else "FAIL"
        )
        conclusion = (
            "STAGE4C2_CRITERION_D_PASS_READY_FOR_FINAL_DIAGNOSTIC_REVIEW"
            if complete["criterion_d"] == "PASS"
            else "STAGE4C2_CRITERION_D_FAIL"
        )
        complete.update({
            "stage4c2": conclusion,
            "holdout_execution_count": 1,
            "holdout_pairs_executed": 8,
            "expected_frame_rows": EXPECTED_FRAME_ROWS,
            "observed_frame_rows": len(oracle_rows),
            "frozen_predictor_mutation": "NONE",
            "physical_call_proof": "PASS",
            "complete_set_point_estimate_controls_gate": True,
            "subgroups_can_rescue_gate": False,
            "probability_inversion": False,
            "thresholded_policy_executed": False,
            "criterion_c_reselected": False,
            "final_diag_pass_fail": "NOT ASSIGNED",
            "stage4d": "LOCKED PENDING MANAGER REVIEW",
        })
        sensitivity = build_sensitivity(oracle_rows)
        bootstrap = (
            bootstrap_summary(
                oracle_rows, "primary_sequence_cluster",
                "primary_sequence_clustered", args.seed,
            )
            + bootstrap_summary(
                oracle_rows, "connected_source_component",
                "connected_source_component_clustered", args.seed,
            )
        )

        baseline_times = [
            float(row["model_forward_ms"]) for row in metric_rows
            if row["condition"] == "baseline"
        ]
        skip_times = [
            float(row["model_forward_ms"]) for row in metric_rows
            if row["condition"] == "whole_mrm1_physical_skip"
        ]
        feature_times = [float(row["feature_extraction_ms"]) for row in feature_rows]
        baseline_median = statistics.median(baseline_times)
        skip_median = statistics.median(skip_times)
        feature_median = statistics.median(feature_times)
        raw_saving = 1.0 - skip_median / baseline_median
        adjusted_saving = 1.0 - (skip_median + feature_median) / baseline_median
        timing = {
            "schema_version": "stage4c2-timing-characterization-v1",
            "descriptive_only": True,
            "criterion_c_reselected": False,
            "timed_rows_per_condition": EXPECTED_FRAME_ROWS,
            "baseline_median_model_forward_ms": baseline_median,
            "physical_skip_median_model_forward_ms": skip_median,
            "median_feature_extraction_ms": feature_median,
            "raw_physical_skip_saving_percent": raw_saving * 100.0,
            "approximate_feature_adjusted_skip_saving_percent": adjusted_saving * 100.0,
            "feature_adjusted_definition": (
                "1 - (physical-skip model-forward median + separately instrumented "
                "baseline feature-extraction median) / baseline model-forward median"
            ),
            "baseline_timing_includes_feature_capture": True,
            "physical_skip_timing_includes_call_counters": True,
            "maximum_peak_allocated_bytes": max(
                int(row["peak_allocated_bytes"]) for row in metric_rows
            ),
            "maximum_peak_reserved_bytes": max(
                int(row["peak_reserved_bytes"]) for row in metric_rows
            ),
            "thresholded_conditional_policy_executed": False,
        }

        unseal_manifest.update({
            "status": "COMPLETE",
            "execution_completed_utc": utc_now(),
            "observed_frame_rows": len(oracle_rows),
            "holdout_pairs_executed": 8,
            "physical_call_proof": "PASS",
            "criterion_d": complete["criterion_d"],
            "stage4c2": conclusion,
        })
        write_json_atomic(unseal_path, unseal_manifest)

        top_criterion = codex_root / f"{DATE_PREFIX}criterionD_results.csv"
        top_sensitivity = codex_root / f"{DATE_PREFIX}sensitivity_results.csv"
        report_path = codex_root / f"{DATE_PREFIX}execution_report.md"
        sequence_path = args.artifact_root / "sequence_execution_manifest.csv"
        call_path = args.artifact_root / "snapshot_and_call_proof.csv"
        metrics_path = args.artifact_root / "baseline_and_skip_metrics.csv"
        features_path = args.artifact_root / "frozen_feature_rows.csv"
        oracle_path = args.artifact_root / "oracle_labels_and_probabilities.csv"
        criterion_path = args.artifact_root / "criterionD_summary.json"
        bootstrap_path = args.artifact_root / "bootstrap_results.csv"
        sensitivity_path = args.artifact_root / "sensitivity_results.csv"
        timing_path = args.artifact_root / "timing_characterization.json"
        calibration_path = args.artifact_root / "calibration_table.csv"
        artifact_manifest_path = args.artifact_root / "artifact_manifest.csv"

        write_csv_atomic(top_criterion, [complete])
        write_csv_atomic(top_sensitivity, sensitivity)
        write_csv_atomic(sequence_path, sequence_manifest)
        write_csv_atomic(call_path, call_rows)
        write_csv_atomic(metrics_path, metric_rows)
        write_csv_atomic(features_path, feature_rows)
        write_csv_atomic(oracle_path, oracle_rows)
        write_json_atomic(criterion_path, {
            "schema_version": "stage4c2-criterion-d-summary-v1",
            **complete,
            "calibration": calibration,
            "bootstrap_is_descriptive": True,
        })
        write_csv_atomic(bootstrap_path, bootstrap)
        write_csv_atomic(sensitivity_path, sensitivity)
        write_json_atomic(timing_path, timing)
        write_csv_atomic(calibration_path, calibration)
        append_log(
            command_log,
            f"ONE_SHOT_HOLDOUT_COMPLETE observed_rows={len(oracle_rows)} "
            f"criterion_d={complete['criterion_d']} conclusion={conclusion}",
        )
        produced = [
            report_path, top_criterion, top_sensitivity, command_log,
            args.artifact_root / "manager_seal_verification.json",
            args.artifact_root / "frozen_predictor_numerical_preflight.json",
            unseal_path, sequence_path, call_path, metrics_path, features_path,
            oracle_path, criterion_path, bootstrap_path, sensitivity_path,
            timing_path, calibration_path,
            codex_root / "scripts/2026-08-28_stage4C2_preflight.py",
            Path(__file__).resolve(), artifact_manifest_path,
        ]
        report = make_report(
            conclusion=conclusion, criterion=complete, seal=seal_verification,
            numerical=numerical_preflight, unseal=unseal_manifest,
            sequence_manifest=sequence_manifest, call_rows=call_rows,
            feature_rows=feature_rows, oracle_rows=oracle_rows,
            sensitivity=sensitivity, bootstrap=bootstrap, timing=timing,
            calibration=calibration,
            files=[path.relative_to(repo_root) for path in produced],
        )
        write_text_atomic(report_path, report)
        manifest_rows = []
        for path in produced:
            if path == artifact_manifest_path:
                continue
            if not path.is_file():
                raise Stage4C2Error(f"Expected output missing before manifest: {path}")
            manifest_rows.append({
                "path": path.relative_to(repo_root).as_posix(),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "bounded_committable_artifact": True,
            })
        write_csv_atomic(artifact_manifest_path, manifest_rows)
        print(json.dumps(complete, indent=2, sort_keys=True), flush=True)
    except BaseException as exc:
        if unsealed:
            unseal_manifest.update({
                "status": "STAGE4C2_INCOMPLETE_AFTER_UNSEAL",
                "execution_completed_utc": utc_now(),
                "observed_frame_rows": 0,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "rerun_allowed": False,
            })
            write_json_atomic(unseal_path, unseal_manifest)
            append_log(
                command_log,
                f"STAGE4C2_INCOMPLETE_AFTER_UNSEAL error={type(exc).__name__}: {exc}",
            )
        else:
            unseal_manifest.update({
                "status": "PRE_OUTCOME_FAILURE_ZERO_ROWS",
                "execution_completed_utc": utc_now(),
                "observed_frame_rows": 0,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "clean_restart_permitted_by_protocol": True,
            })
            write_json_atomic(unseal_path, unseal_manifest)
            append_log(
                command_log,
                f"PRE_OUTCOME_FAILURE_ZERO_HOLDOUT_OUTCOME_ROWS "
                f"error={type(exc).__name__}: {exc}",
            )
        raise


def main() -> None:
    args = parse_args()
    if args.self_test:
        run_self_test()
        run_environment_self_test(args)
    else:
        run_one_shot(args)


if __name__ == "__main__":
    main()
