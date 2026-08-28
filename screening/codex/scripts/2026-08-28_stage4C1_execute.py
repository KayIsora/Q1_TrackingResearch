#!/usr/bin/env python3
"""Execute the locked Stage-4C1 discovery-only physical-skip contract."""

from __future__ import annotations

import argparse
import csv
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
from types import ModuleType
from typing import Any, Mapping, Sequence

import numpy as np


DATE_PREFIX = "2026-08-28_stage4C1_"
SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
CHECKPOINT_SHA256 = (
    "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
)
SLICE_SHA256_LF = (
    "bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a"
)
SEED = 20260828
PARITY_TOLERANCE = 1e-6
WARMUP_FORWARDS = 30
REPETITIONS = 3
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{index:02d}" for index in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
DISCOVERY_SOURCE_ALIASES = {
    "Jogging_1": {
        "path": "Jogging/img",
        "anno_path": "Jogging/groundtruth_rect.1.txt",
    }
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
COMPONENTS = {
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
PAIR_TO_COMPONENT = {
    pair_id: component
    for component, pair_ids in COMPONENTS.items()
    for pair_id in pair_ids
}


class ContractError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--slice-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--stage4b-baseline-csv", type=Path, required=True)
    parser.add_argument("--physical-patch", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def load_module(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ContractError(f"Cannot load helper module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_lf_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def git_output(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={root.as_posix()}", "-C", str(root), *args],
        text=True,
    ).strip()


def configure_stage4a(helper: ModuleType, tracker: Any, enabled: bool,
                      selector: str = "none") -> None:
    helper.configure_diagnostics(tracker, enabled, selector)


def configure_stage4c1(tracker: Any, physical_mode: str = "none",
                       capture_features: bool = False,
                       timing_enabled: bool = False,
                       record_call_counts: bool = False) -> None:
    tracker.configure_stage4c1(
        physical_mode=physical_mode,
        capture_features=capture_features,
        timing_enabled=timing_enabled,
        record_call_counts=record_call_counts,
    )


def capture_state(helper: ModuleType, tracker: Any) -> dict[str, Any]:
    state = helper.capture_tracker_state(tracker)
    state["stage4c1_history"] = {
        "last_confidence": helper.clone_state_value(
            tracker.stage4c1_last_confidence
        ),
        "last_predicted_state": helper.clone_state_value(
            tracker.stage4c1_last_predicted_state
        ),
        "previous_predicted_state": helper.clone_state_value(
            tracker.stage4c1_previous_predicted_state
        ),
    }
    return state


def restore_state(helper: ModuleType, tracker: Any, state: Mapping[str, Any]) -> None:
    helper.restore_tracker_state(tracker, dict(state))
    history = state["stage4c1_history"]
    tracker.stage4c1_last_confidence = helper.clone_state_value(
        history["last_confidence"]
    )
    tracker.stage4c1_last_predicted_state = helper.clone_state_value(
        history["last_predicted_state"]
    )
    tracker.stage4c1_previous_predicted_state = helper.clone_state_value(
        history["previous_predicted_state"]
    )
    tracker.stage4c1_feature_records = []
    tracker.stage4c1_last_call_counts = {}


def state_hash(helper: ModuleType, state: Mapping[str, Any]) -> str:
    return helper.snapshot_sha256(dict(state))


def normalized_end_state(helper: ModuleType, tracker: Any) -> dict[str, Any]:
    tracker.stage4a_diagnostic_records = []
    tracker.stage4c1_feature_records = []
    encoder = tracker.network.encoder
    encoder._stage4a_current_records = []
    encoder._stage4a_diagnostic_records = []
    encoder._stage4c1_feature_records = []
    encoder._stage4c1_current_call_counts = {}
    encoder._stage4c1_last_call_counts = {}
    return capture_state(helper, tracker)


def configure_determinism(torch: Any, seed: int) -> None:
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def branch_frame_indices(interval: Any) -> range:
    return range(max(int(interval.start), 2), int(interval.end) + 1)


def initialization_metric(helper: ModuleType, tracker: Any, interval: Any,
                          gt: np.ndarray, condition: str,
                          repetition: int | None = None) -> dict[str, Any]:
    float_box = np.asarray(tracker.state, dtype=np.float64)
    int_box = float_box.astype(np.int64)
    gt_box = gt[0]
    iou = helper.inclusive_iou(int_box, gt_box)
    return {
        "pair_id": interval.pair_id,
        "side": interval.side,
        "sequence": interval.sequence,
        "frame_index": 1,
        "condition": condition,
        "repetition": repetition,
        "iou": iou,
        "iou_float": helper.inclusive_iou(float_box, gt_box),
        "physical_skip": condition == "whole_mrm1_physical_skip",
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
        "initialization_frame": True,
        "branch_frame_executed": False,
    }


def output_metrics(helper: ModuleType, output: Mapping[str, Any], gt_box: np.ndarray,
                   interval: Any, frame_index: int, condition: str,
                   repetition: int | None) -> dict[str, Any]:
    float_box = np.asarray(output["target_bbox"], dtype=np.float64)
    int_box = float_box.astype(np.int64)
    iou = helper.inclusive_iou(int_box, gt_box)
    return {
        "pair_id": interval.pair_id,
        "side": interval.side,
        "sequence": interval.sequence,
        "frame_index": frame_index,
        "condition": condition,
        "repetition": repetition,
        "iou": iou,
        "iou_float": helper.inclusive_iou(float_box, gt_box),
        "physical_skip": condition in {
            "whole_mrm1_physical_skip", "mlp_mrm1_physical_skip"
        },
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
        "initialization_frame": False,
        "branch_frame_executed": True,
    }


def profiler_summary(torch: Any, callback: Any) -> tuple[Any, list[dict[str, Any]]]:
    activities = [torch.profiler.ProfilerActivity.CPU]
    if torch.cuda.is_available():
        activities.append(torch.profiler.ProfilerActivity.CUDA)
    with torch.profiler.profile(
        activities=activities,
        record_shapes=True,
        profile_memory=True,
    ) as profile:
        result = callback()
        profile.step()
    rows = []
    for item in profile.key_averages():
        rows.append({
            "operator": item.key,
            "count": int(item.count),
            "cpu_time_total_us": float(item.cpu_time_total),
            "cuda_time_total_us": float(getattr(item, "cuda_time_total", 0.0)),
            "self_cpu_memory_usage": int(item.self_cpu_memory_usage),
            "self_cuda_memory_usage": int(
                getattr(item, "self_cuda_memory_usage", 0)
            ),
        })
    rows.sort(
        key=lambda row: (row["cuda_time_total_us"], row["cpu_time_total_us"]),
        reverse=True,
    )
    return result, rows[:100]


def run_branch(
    *, helper: ModuleType, torch: Any, tracker: Any, interval: Any,
    frame_paths: Sequence[Path], ground_truth: np.ndarray, condition: str,
    physical_mode: str, stage4a_selector: str = "none",
    stage4a_enabled: bool = False, timing_enabled: bool = False,
    record_call_counts: bool = False, capture_features: bool = False,
    repetition: int | None = None, execution_order: int | None = None,
    profile_first_frame: bool = False,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]],
           list[dict[str, Any]], dict[str, Any]]:
    configure_stage4a(helper, tracker, stage4a_enabled, stage4a_selector)
    configure_stage4c1(
        tracker,
        physical_mode=physical_mode,
        capture_features=capture_features,
        timing_enabled=timing_enabled,
        record_call_counts=record_call_counts,
    )
    metrics: list[dict[str, Any]] = []
    timing: list[dict[str, Any]] = []
    proof: list[dict[str, Any]] = []
    features: list[dict[str, Any]] = []
    trace: dict[str, Any] = {}
    if int(interval.start) == 1:
        metrics.append(
            initialization_metric(
                helper, tracker, interval, ground_truth, condition, repetition
            )
        )
    interval_started = time.perf_counter()
    for frame_index in branch_frame_indices(interval):
        callback = lambda: tracker.track(
            helper.read_rgb(frame_paths[frame_index - 1]), {}
        )
        if profile_first_frame and not trace:
            output_tuple, trace_rows = profiler_summary(torch, callback)
            trace = {
                "pair_id": interval.pair_id,
                "side": interval.side,
                "sequence": interval.sequence,
                "frame_index": frame_index,
                "condition": condition,
                "operators": trace_rows,
            }
        else:
            output_tuple = callback()
        output = output_tuple[0]
        metric = output_metrics(
            helper, output, ground_truth[frame_index - 1], interval,
            frame_index, condition, repetition,
        )
        metrics.append(metric)
        if timing_enabled:
            timing.append({
                "pair_id": interval.pair_id,
                "side": interval.side,
                "sequence": interval.sequence,
                "frame_index": frame_index,
                "condition": condition,
                "repetition": repetition,
                "execution_order": execution_order,
                "model_forward_ms": tracker.stage4c1_last_model_forward_ms,
                "peak_allocated_bytes": (
                    tracker.stage4c1_last_peak_allocated_bytes
                ),
                "peak_reserved_bytes": tracker.stage4c1_last_peak_reserved_bytes,
                "batch_size": 1,
                "dtype": "torch.float32",
                "diagnostic_logging": False,
                "record_call_counts": False,
                "physical_skip": physical_mode != "none",
            })
        if record_call_counts:
            counts = dict(tracker.stage4c1_last_call_counts)
            proof.append({
                "pair_id": interval.pair_id,
                "side": interval.side,
                "sequence": interval.sequence,
                "frame_index": frame_index,
                "condition": condition,
                "physical_skip": physical_mode != "none",
                **counts,
            })
        if capture_features:
            records = tracker.consume_stage4c1_feature_records()
            if len(records) != 1:
                raise ContractError(
                    f"{interval.pair_id}/{interval.side}/{frame_index}: "
                    f"expected one feature record, got {len(records)}"
                )
            record = dict(records[0])
            record.update({
                "pair_id": interval.pair_id,
                "side": interval.side,
                "sequence": interval.sequence,
                "frame_index": frame_index,
                "connected_component": PAIR_TO_COMPONENT[interval.pair_id],
            })
            features.append(record)
        if stage4a_enabled:
            records = tracker.consume_stage4a_diagnostic_records()
            tracker_records = [
                item for item in records if item.get("record_type") == "tracker_frame"
            ]
            if len(tracker_records) != 1:
                raise ContractError(
                    f"{condition}: expected one Stage-4A tracker record"
                )
            metric["score_map_max"] = tracker_records[0]["score_map_max"]
            metric["confidence_score"] = tracker_records[0]["confidence_score"]
    interval_elapsed_ms = (time.perf_counter() - interval_started) * 1000.0
    return metrics, timing, proof, features, {
        "trace": trace,
        "interval_end_to_end_ms": interval_elapsed_ms,
        "end_state": normalized_end_state(helper, tracker),
    }


def compare_parity_rows(left: Sequence[Mapping[str, Any]],
                        right: Sequence[Mapping[str, Any]],
                        interval: Any, comparison: str,
                        left_hash: str, right_hash: str) -> list[dict[str, Any]]:
    if len(left) != len(right):
        raise ContractError(f"{comparison}: row-count mismatch")
    rows = []
    for lrow, rrow in zip(left, right):
        if (lrow["pair_id"], lrow["side"], lrow["frame_index"]) != (
            rrow["pair_id"], rrow["side"], rrow["frame_index"]
        ):
            raise ContractError(f"{comparison}: key mismatch")
        float_diff = max(
            abs(float(lrow[key]) - float(rrow[key]))
            for key in (
                "pred_x_float", "pred_y_float", "pred_w_float", "pred_h_float"
            )
        )
        int_exact = all(
            int(lrow[key]) == int(rrow[key])
            for key in ("pred_x_int", "pred_y_int", "pred_w_int", "pred_h_int")
        )
        score_diff = abs(
            float(lrow.get("score_map_max", 0.0))
            - float(rrow.get("score_map_max", 0.0))
        )
        confidence_diff = abs(
            float(lrow.get("confidence_score", 0.0))
            - float(rrow.get("confidence_score", 0.0))
        )
        passed = (
            float_diff <= PARITY_TOLERANCE
            and int_exact
            and score_diff <= PARITY_TOLERANCE
            and confidence_diff <= PARITY_TOLERANCE
            and left_hash == right_hash
        )
        rows.append({
            "pair_id": interval.pair_id,
            "side": interval.side,
            "sequence": interval.sequence,
            "frame_index": lrow["frame_index"],
            "comparison": comparison,
            "maximum_float_bbox_abs_diff": float_diff,
            "integer_bbox_exact": int_exact,
            "score_map_max_abs_diff": score_diff,
            "confidence_abs_diff": confidence_diff,
            "left_end_state_sha256": left_hash,
            "right_end_state_sha256": right_hash,
            "continuation_state_exact": left_hash == right_hash,
            "tolerance": PARITY_TOLERANCE,
            "status": "PASS" if passed else "FAIL",
        })
    return rows


def timing_order_bits(intervals: Sequence[Any], seed: int) -> dict[tuple[str, str], int]:
    rng = random.Random(seed)
    keys = sorted((item.pair_id, item.side) for item in intervals)
    return {key: rng.randint(0, 1) for key in keys}


def percentile(values: Sequence[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=np.float64), q))


def clustered_latency_bootstrap(rows: Sequence[Mapping[str, Any]], seed: int,
                                resamples: int = 10000) -> tuple[float, float]:
    by_sequence: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        by_sequence.setdefault(str(row["sequence"]), []).append(row)
    sequences = sorted(by_sequence)
    rng = np.random.default_rng(seed)
    estimates = np.empty(resamples, dtype=np.float64)
    for index in range(resamples):
        sampled = rng.choice(sequences, size=len(sequences), replace=True)
        baseline: list[float] = []
        skip: list[float] = []
        for sequence in sampled:
            for row in by_sequence[str(sequence)]:
                target = baseline if row["condition"] == "baseline" else skip
                target.append(float(row["model_forward_ms"]))
        estimates[index] = 1.0 - statistics.median(skip) / statistics.median(
            baseline
        )
    return percentile(estimates, 2.5), percentile(estimates, 97.5)


def prepare_csv(helper: ModuleType, path: Path, rows: Sequence[Mapping[str, Any]],
                fields: Sequence[str]) -> Path:
    return helper.prepare_csv(path, list(fields), [dict(row) for row in rows])


def validate_keys(rows: Sequence[Mapping[str, Any]], expected: set[tuple],
                  fields: Sequence[str], context: str) -> None:
    observed = {tuple(row[field] for field in fields) for row in rows}
    if observed != expected or len(rows) != len(expected):
        raise ContractError(
            f"{context} coverage mismatch: rows={len(rows)}, keys={len(observed)}, "
            f"expected={len(expected)}"
        )


def main() -> None:
    args = parse_args()
    if args.seed != SEED:
        raise ContractError(f"Locked seed is {SEED}")
    repo_root = Path(__file__).resolve().parents[3]
    criterion_b_path = repo_root / (
        "screening/codex/scripts/2026-08-26_stage4B_execute_criterionB.py"
    )
    refinement_path = repo_root / (
        "screening/codex/scripts/2026-08-26_stage4B_execute_refinement.py"
    )
    helper = load_module(criterion_b_path, "stage4c1_stage4b_helper")
    refinement = load_module(refinement_path, "stage4c1_refinement_helper")

    for path in (
        args.source_root, args.dataset_root, args.slice_csv, args.config,
        args.checkpoint, args.stage4b_baseline_csv, args.physical_patch,
    ):
        if not path.exists():
            raise FileNotFoundError(path)
    if git_output(args.source_root, "rev-parse", "HEAD") != SOURCE_SHA:
        raise ContractError("Pinned SpikeTrack source SHA mismatch")
    if sha256_file(args.checkpoint) != CHECKPOINT_SHA256:
        raise ContractError("Checkpoint SHA-256 mismatch")
    if normalized_lf_sha256(args.slice_csv) != SLICE_SHA256_LF:
        raise ContractError("Frozen-slice normalized-LF SHA-256 mismatch")

    discovery, intervals_by_sequence, slice_hashes = helper.parse_and_validate_slice(
        args.slice_csv
    )
    if tuple(sorted(row["pair_id"] for row in discovery)) != EXPECTED_DISCOVERY_IDS:
        raise ContractError("Discovery ID set mismatch")
    baseline_reference, baseline_sha = helper.load_baseline_frames(
        args.stage4b_baseline_csv, discovery
    )
    if len(baseline_reference) != 596:
        raise ContractError("Stage-4B baseline reference is not exactly 596 rows")
    all_intervals = [
        item for sequence in sorted(intervals_by_sequence)
        for item in intervals_by_sequence[sequence]
    ]
    if len(all_intervals) != 24:
        raise ContractError("Frozen discovery must contain exactly 24 intervals")
    if set(PAIR_TO_COMPONENT) != set(EXPECTED_DISCOVERY_IDS):
        raise ContractError("Connected-component map mismatch")

    sys.path.insert(0, str(args.source_root))
    import torch
    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.evaluation.otbdataset import OTBDataset
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    # The accepted Stage-4B helper binds torch inside its own main().  Stage 4C1
    # imports that file as a module so its snapshot helpers need the same binding.
    helper.torch = torch
    configure_determinism(torch, args.seed)
    official_info = {
        item["name"]: item for item in OTBDataset._get_sequence_info_list(None)
    }
    missing = sorted(set(intervals_by_sequence) - set(official_info))
    if missing:
        raise ContractError(f"Discovery sequences absent from OTB metadata: {missing}")
    holdout_sequences = {
        str(row[key])
        for row in csv.DictReader(args.slice_csv.open("r", encoding="utf-8-sig"))
        if row["split"] == "HOLDOUT"
        for key in ("primary_sequence", "control_sequence")
    }
    if set(intervals_by_sequence) & holdout_sequences:
        raise ContractError("STAGE4C1_INVALID_HOLDOUT_EXPOSURE")

    tracker = refinement.make_tracker(
        cfg, update_config_from_file, SpikeTrack,
        args.config, args.checkpoint, 1,
    )
    sequence_names = sorted(intervals_by_sequence)
    order_bits = timing_order_bits(all_intervals, args.seed)
    timing_rows: list[dict[str, Any]] = []
    interval_timing_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    parity_rows: list[dict[str, Any]] = []
    proof_rows: list[dict[str, Any]] = []
    traces: list[dict[str, Any]] = []
    warmup_done = False
    global_execution_order = 0

    for sequence_index, sequence_name in enumerate(sequence_names, start=1):
        info = dict(official_info[sequence_name])
        info.update(DISCOVERY_SOURCE_ALIASES.get(sequence_name, {}))
        frame_dir = args.dataset_root / info["path"]
        anno_path = args.dataset_root / info["anno_path"]
        frame_paths = sorted(frame_dir.glob("*.jpg"))
        ground_truth = helper.read_boxes(anno_path)
        intervals = intervals_by_sequence[sequence_name]
        max_frame = max(item.end for item in intervals)
        if len(frame_paths) < max_frame or len(ground_truth) < max_frame:
            raise ContractError(f"Discovery source truncated: {sequence_name}")
        configure_stage4a(helper, tracker, False, "none")
        configure_stage4c1(tracker)
        tracker.initialize(
            helper.read_rgb(frame_paths[0]),
            {"init_bbox": ground_truth[0].astype(np.float64).tolist()},
        )
        current_frame = 1
        print(
            f"PROGRESS sequence {sequence_index}/{len(sequence_names)} "
            f"{sequence_name} intervals={len(intervals)} through={max_frame}",
            flush=True,
        )
        for interval in intervals:
            while current_frame < interval.start - 1:
                current_frame += 1
                configure_stage4a(helper, tracker, False, "none")
                configure_stage4c1(tracker)
                tracker.track(helper.read_rgb(frame_paths[current_frame - 1]), {})
            start_snapshot = capture_state(helper, tracker)
            start_hash = state_hash(helper, start_snapshot)

            if not warmup_done:
                first_frame = max(int(interval.start), 2)
                for _ in range(WARMUP_FORWARDS):
                    restore_state(helper, tracker, start_snapshot)
                    configure_stage4a(helper, tracker, False, "none")
                    configure_stage4c1(tracker)
                    tracker.track(helper.read_rgb(frame_paths[first_frame - 1]), {})
                warmup_done = True
                restore_state(helper, tracker, start_snapshot)

            # Uninterrupted baseline continuation is the sequence-state anchor.
            restore_state(helper, tracker, start_snapshot)
            continuation_metrics, _, _, _, continuation_meta = run_branch(
                helper=helper, torch=torch, tracker=tracker, interval=interval,
                frame_paths=frame_paths, ground_truth=ground_truth,
                condition="baseline_continuation", physical_mode="none",
            )
            baseline_end_snapshot = continuation_meta["end_state"]
            baseline_end_hash = state_hash(helper, baseline_end_snapshot)

            # Locked timing: three complete repetitions, alternating order.
            for repetition in range(1, REPETITIONS + 1):
                baseline_first = (
                    order_bits[(interval.pair_id, interval.side)] + repetition - 1
                ) % 2 == 0
                conditions = (
                    (("baseline", "none"),
                     ("whole_mrm1_physical_skip", "whole_mrm1"))
                    if baseline_first else
                    (("whole_mrm1_physical_skip", "whole_mrm1"),
                     ("baseline", "none"))
                )
                for condition, physical_mode in conditions:
                    restore_state(helper, tracker, start_snapshot)
                    global_execution_order += 1
                    rows, timings, _, _, meta = run_branch(
                        helper=helper, torch=torch, tracker=tracker,
                        interval=interval, frame_paths=frame_paths,
                        ground_truth=ground_truth, condition=condition,
                        physical_mode=physical_mode, timing_enabled=True,
                        repetition=repetition,
                        execution_order=global_execution_order,
                    )
                    timing_rows.extend(timings)
                    interval_timing_rows.append({
                        "pair_id": interval.pair_id,
                        "side": interval.side,
                        "sequence": interval.sequence,
                        "condition": condition,
                        "repetition": repetition,
                        "execution_order": global_execution_order,
                        "interval_end_to_end_ms": meta[
                            "interval_end_to_end_ms"
                        ],
                        "tracked_frames": len(timings),
                        "start_snapshot_sha256": start_hash,
                    })
                    if repetition == 1:
                        metric_rows.extend(rows)

            # Semantic parity against accepted Stage-4B zero-residual controls.
            parity_specs = (
                (
                    "WHOLE_MRM1_ZERO_VS_PHYSICAL",
                    "mrm1", "whole_mrm1",
                    "whole_mrm1_zero_residual", "whole_mrm1_physical_parity",
                ),
                (
                    "MLP_MRM1_ZERO_VS_PHYSICAL",
                    "mrm1_mlp", "mlp_mrm1",
                    "mlp_mrm1_zero_residual", "mlp_mrm1_physical_parity",
                ),
            )
            for comparison, selector, physical_mode, left_name, right_name in parity_specs:
                restore_state(helper, tracker, start_snapshot)
                left_rows, _, _, _, left_meta = run_branch(
                    helper=helper, torch=torch, tracker=tracker,
                    interval=interval, frame_paths=frame_paths,
                    ground_truth=ground_truth, condition=left_name,
                    physical_mode="none", stage4a_selector=selector,
                    stage4a_enabled=True,
                )
                left_hash = state_hash(helper, left_meta["end_state"])
                restore_state(helper, tracker, start_snapshot)
                right_rows, _, _, _, right_meta = run_branch(
                    helper=helper, torch=torch, tracker=tracker,
                    interval=interval, frame_paths=frame_paths,
                    ground_truth=ground_truth, condition=right_name,
                    physical_mode=physical_mode, stage4a_selector=selector,
                    stage4a_enabled=True,
                )
                right_hash = state_hash(helper, right_meta["end_state"])
                parity_rows.extend(
                    compare_parity_rows(
                        left_rows, right_rows, interval, comparison,
                        left_hash, right_hash,
                    )
                )

            # Full-coverage call proof; one bounded profiler trace per condition.
            proof_specs = (
                ("baseline", "none"),
                ("whole_mrm1_physical_skip", "whole_mrm1"),
                ("mlp_mrm1_physical_skip", "mlp_mrm1"),
            )
            for condition, physical_mode in proof_specs:
                restore_state(helper, tracker, start_snapshot)
                _, _, proof, _, meta = run_branch(
                    helper=helper, torch=torch, tracker=tracker,
                    interval=interval, frame_paths=frame_paths,
                    ground_truth=ground_truth, condition=condition,
                    physical_mode=physical_mode, record_call_counts=True,
                    profile_first_frame=(
                        interval.pair_id == "R3-D01"
                        and interval.side == "primary"
                    ),
                )
                proof_rows.extend(proof)
                if meta["trace"]:
                    traces.append(meta["trace"])

            restore_state(helper, tracker, baseline_end_snapshot)
            if state_hash(helper, capture_state(helper, tracker)) != baseline_end_hash:
                raise ContractError("Continuation restore mismatch")
            current_frame = int(interval.end)
            print(
                f"PROGRESS interval {interval.pair_id}/{interval.side} complete",
                flush=True,
            )

    expected_tracked = sum(
        max(0, int(item.end) - max(int(item.start), 2) + 1)
        for item in all_intervals
    )
    if expected_tracked != 593:
        raise ContractError(f"Expected 593 tracked frames, got {expected_tracked}")
    expected_timing = {
        (pair_id, side, frame, condition, repetition)
        for interval in all_intervals
        for pair_id, side in ((interval.pair_id, interval.side),)
        for frame in branch_frame_indices(interval)
        for condition in ("baseline", "whole_mrm1_physical_skip")
        for repetition in range(1, REPETITIONS + 1)
    }
    validate_keys(
        timing_rows, expected_timing,
        ("pair_id", "side", "frame_index", "condition", "repetition"),
        "Criterion-C timing",
    )
    expected_metrics = {
        (interval.pair_id, interval.side, frame, condition)
        for interval in all_intervals
        for frame in range(int(interval.start), int(interval.end) + 1)
        for condition in ("baseline", "whole_mrm1_physical_skip")
    }
    validate_keys(
        metric_rows, expected_metrics,
        ("pair_id", "side", "frame_index", "condition"),
        "Physical-skip metrics",
    )

    parity_pass = bool(parity_rows) and all(row["status"] == "PASS" for row in parity_rows)
    whole_proof = [
        row for row in proof_rows
        if row["condition"] == "whole_mrm1_physical_skip"
    ]
    baseline_proof = [row for row in proof_rows if row["condition"] == "baseline"]
    mlp_proof = [
        row for row in proof_rows if row["condition"] == "mlp_mrm1_physical_skip"
    ]
    call_proof_pass = (
        len(whole_proof) == expected_tracked
        and len(baseline_proof) == expected_tracked
        and len(mlp_proof) == expected_tracked
        and all(
            int(row["mrm1_forward"]) == 0
            and int(row["mrm1_retriever_forward"]) == 0
            and int(row["mrm1_mlp_forward"]) == 0
            and int(row["mrm1_internal_operator_count"]) == 0
            and all(int(row[f"mrm{index}_forward"]) == 1 for index in range(2, 7))
            for row in whole_proof
        )
        and all(
            int(row["mrm1_forward"]) == 1
            and int(row["mrm1_retriever_forward"]) == 1
            and int(row["mrm1_mlp_forward"]) == 1
            and int(row["mrm1_internal_operator_count"]) == 2
            for row in baseline_proof
        )
        and all(
            int(row["mrm1_forward"]) == 0
            and int(row["mrm1_retriever_forward"]) == 1
            and int(row["mrm1_mlp_forward"]) == 0
            for row in mlp_proof
        )
    )
    baseline_ms = [
        float(row["model_forward_ms"]) for row in timing_rows
        if row["condition"] == "baseline"
    ]
    skip_ms = [
        float(row["model_forward_ms"]) for row in timing_rows
        if row["condition"] == "whole_mrm1_physical_skip"
    ]
    baseline_median = statistics.median(baseline_ms)
    skip_median = statistics.median(skip_ms)
    latency_saving = 1.0 - skip_median / baseline_median
    ci_low, ci_high = clustered_latency_bootstrap(timing_rows, args.seed)
    ordered = sorted(timing_rows, key=lambda row: int(row["execution_order"]))
    quartile_size = max(1, len(ordered) // 4)
    first_quartile = ordered[:quartile_size]
    last_quartile = ordered[-quartile_size:]

    if not parity_pass or not call_proof_pass:
        criterion_c_status = "NOT_COMPLETED"
        conclusion = "STAGE4C1_INCOMPLETE_PHYSICAL_SKIP_OR_PREDICTOR"
    elif latency_saving >= 0.05:
        criterion_c_status = "PASS"
        conclusion = "STAGE4C1_CRITERION_C_PASS_PREDICTOR_PHASE_OPEN"
    else:
        criterion_c_status = "FAIL"
        conclusion = "STAGE4C1_CRITERION_C_FAIL"

    feature_rows: list[dict[str, Any]] = []
    oracle_rows: list[dict[str, Any]] = []
    feature_schema = {
        "schema_version": "stage4c1-pre-mrm-features-v1",
        "feature_order": list(FEATURE_ORDER),
        "formulas": {
            "previous_confidence": (
                "previous tracker prediction confidence; cold-start sentinel 0.0"
            ),
            "previous_center_displacement_normalized_by_predicted_scale": (
                "Euclidean center displacement between the two latest tracker "
                "predictions divided by sqrt(width*height) of the latest prediction; "
                "cold-start sentinel 0.0"
            ),
            "previous_log_area_ratio": (
                "log(area(latest tracker prediction)/area(previous tracker prediction)); "
                "cold-start sentinel 0.0"
            ),
            "mrm1_input_abs_mean": "mean(abs(current pre-MRM1 inference tensor))",
            "mrm1_input_std": "population std(current pre-MRM1 inference tensor)",
            "mrm1_input_rms": "sqrt(mean(current pre-MRM1 tensor squared))",
            "mrm1_input_nonzero_ratio": "mean(current pre-MRM1 tensor != 0)",
            "template_memory_abs_mean": "mean(abs(already cached MRM1 template memory))",
            "template_memory_std": "population std(already cached MRM1 template memory)",
            "template_memory_rms": "sqrt(mean(cached MRM1 template memory squared))",
            "template_memory_nonzero_ratio": "mean(cached MRM1 template memory != 0)",
            "search_to_template_rms_ratio": "mrm1_input_rms/max(template_memory_rms,1e-12)",
        },
        "epsilon": 1e-12,
        "cold_start_policy": (
            "No GT-derived history value is used. If prior tracker prediction "
            "history/confidence is unavailable, the three history scalars are 0.0."
        ),
        "forbidden_inputs": [
            "GT", "IoU", "manual distractor annotations", "ambiguity/tier",
            "primary/control side", "pair/sequence ID", "class/stratum",
            "post-MRM values", "Retriever/MLP outputs", "hold-out information",
        ],
        "additional_network_pass": False,
    }

    if criterion_c_status == "PASS":
        metrics_by_key = {
            (row["pair_id"], row["side"], int(row["frame_index"]), row["condition"]): row
            for row in metric_rows
        }
        for interval in all_intervals:
            for frame in range(int(interval.start), int(interval.end) + 1):
                baseline = metrics_by_key[(
                    interval.pair_id, interval.side, frame, "baseline"
                )]
                skip = metrics_by_key[(
                    interval.pair_id, interval.side, frame,
                    "whole_mrm1_physical_skip",
                )]
                benefit = float(skip["iou"]) - float(baseline["iou"])
                oracle_rows.append({
                    "pair_id": interval.pair_id,
                    "side": interval.side,
                    "sequence": interval.sequence,
                    "frame_index": frame,
                    "connected_component": PAIR_TO_COMPONENT[interval.pair_id],
                    "iou_baseline": baseline["iou"],
                    "iou_physical_whole_mrm1_skip": skip["iou"],
                    "oracle_skip_benefit": benefit,
                    "oracle_label": int(benefit > 0.0),
                    "exact_tie_is_zero": benefit == 0.0,
                    "predictor_eligible": not bool(baseline["initialization_frame"]),
                    "holdout": False,
                })

        del tracker
        torch.cuda.empty_cache()
        tracker = refinement.make_tracker(
            cfg, update_config_from_file, SpikeTrack,
            args.config, args.checkpoint, 1,
        )
        for sequence_name in sequence_names:
            info = dict(official_info[sequence_name])
            info.update(DISCOVERY_SOURCE_ALIASES.get(sequence_name, {}))
            frame_paths = sorted((args.dataset_root / info["path"]).glob("*.jpg"))
            ground_truth = helper.read_boxes(args.dataset_root / info["anno_path"])
            intervals = intervals_by_sequence[sequence_name]
            configure_stage4a(helper, tracker, False, "none")
            configure_stage4c1(tracker)
            tracker.initialize(
                helper.read_rgb(frame_paths[0]),
                {"init_bbox": ground_truth[0].astype(np.float64).tolist()},
            )
            current_frame = 1
            for interval in intervals:
                while current_frame < interval.start - 1:
                    current_frame += 1
                    configure_stage4a(helper, tracker, False, "none")
                    configure_stage4c1(tracker)
                    tracker.track(helper.read_rgb(frame_paths[current_frame - 1]), {})
                _, _, _, features, _ = run_branch(
                    helper=helper, torch=torch, tracker=tracker,
                    interval=interval, frame_paths=frame_paths,
                    ground_truth=ground_truth, condition="feature_capture_baseline",
                    physical_mode="none", capture_features=True,
                )
                feature_rows.extend(features)
                current_frame = int(interval.end)
        oracle_by_key = {
            (row["pair_id"], row["side"], int(row["frame_index"])): row
            for row in oracle_rows if row["predictor_eligible"]
        }
        for row in feature_rows:
            oracle = oracle_by_key[(
                row["pair_id"], row["side"], int(row["frame_index"])
            )]
            row["oracle_skip_benefit"] = oracle["oracle_skip_benefit"]
            row["oracle_label"] = oracle["oracle_label"]
            row["holdout"] = False
            if any(not math.isfinite(float(row[name])) for name in FEATURE_ORDER):
                raise ContractError("Non-finite predictor feature")
        if len(feature_rows) != expected_tracked or len(oracle_rows) != 596:
            raise ContractError("Feature/oracle coverage mismatch")

    criterion_row = {
        "criterion_c": criterion_c_status,
        "semantic_parity": "PASS" if parity_pass else "FAIL",
        "whole_mrm1_call_proof": "PASS" if call_proof_pass else "FAIL",
        "warmup_forwards": WARMUP_FORWARDS,
        "repetitions": REPETITIONS,
        "timed_rows_per_condition": len(baseline_ms),
        "baseline_median_model_forward_ms": baseline_median,
        "physical_skip_median_model_forward_ms": skip_median,
        "latency_saving": latency_saving,
        "latency_saving_percent": latency_saving * 100.0,
        "sequence_clustered_bootstrap_ci_low": ci_low,
        "sequence_clustered_bootstrap_ci_high": ci_high,
        "first_quartile_baseline_median_ms": statistics.median(
            float(row["model_forward_ms"]) for row in first_quartile
            if row["condition"] == "baseline"
        ),
        "first_quartile_skip_median_ms": statistics.median(
            float(row["model_forward_ms"]) for row in first_quartile
            if row["condition"] == "whole_mrm1_physical_skip"
        ),
        "last_quartile_baseline_median_ms": statistics.median(
            float(row["model_forward_ms"]) for row in last_quartile
            if row["condition"] == "baseline"
        ),
        "last_quartile_skip_median_ms": statistics.median(
            float(row["model_forward_ms"]) for row in last_quartile
            if row["condition"] == "whole_mrm1_physical_skip"
        ),
        "maximum_peak_allocated_bytes": max(
            int(row["peak_allocated_bytes"]) for row in timing_rows
        ),
        "maximum_peak_reserved_bytes": max(
            int(row["peak_reserved_bytes"]) for row in timing_rows
        ),
        "threshold": 0.05,
        "physical_skip": True,
        "stage4c1_execution_state": conclusion,
    }
    summary = {
        "schema_version": "stage4c1-execution-v1",
        "status": conclusion,
        "criterion_c": criterion_row,
        "discovery_pairs_executed": 12,
        "discovery_intervals_executed": 24,
        "holdout_pairs_executed": 0,
        "holdout_outcomes_read": 0,
        "stage4c2": "LOCKED",
        "warmup_forwards": WARMUP_FORWARDS,
        "repetitions": REPETITIONS,
        "feature_phase_executed": criterion_c_status == "PASS",
        "feature_rows": len(feature_rows),
        "oracle_rows": len(oracle_rows),
        "input_hashes": {
            "source_sha": SOURCE_SHA,
            "config_sha256": sha256_file(args.config),
            "checkpoint_sha256": sha256_file(args.checkpoint),
            "frozen_slice_sha256_normalized_lf": slice_hashes[
                "normalized_lf_sha256"
            ],
            "stage4b_baseline_csv_sha256": baseline_sha,
            "physical_skip_patch_sha256": sha256_file(args.physical_patch),
        },
        "environment": {
            "platform": platform.platform(),
            "python": sys.version,
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "gpu": torch.cuda.get_device_name(0),
            "dtype": "torch.float32",
            "batch_size": 1,
            "seed": args.seed,
            "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "row_counts": {
            "timing_per_frame": len(timing_rows),
            "interval_timing": len(interval_timing_rows),
            "physical_skip_metrics": len(metric_rows),
            "semantic_parity": len(parity_rows),
            "call_path_proof": len(proof_rows),
            "profiler_traces": len(traces),
            "pre_mrm_features": len(feature_rows),
            "oracle_labels": len(oracle_rows),
        },
        "feature_schema": feature_schema if feature_rows else None,
        "next_action": (
            "RUN_LOCKED_DISCOVERY_PREDICTOR_FREEZE"
            if criterion_c_status == "PASS" else "STOP_FOR_MANAGER_REVIEW"
        ),
        "non_claims": {
            "jetson_nano_evidence": False,
            "diag_pass_fail_assigned": False,
            "s1_s7_started": False,
            "main_baseline": None,
            "primary_shortlist": None,
            "proposed_architecture": None,
        },
    }

    args.artifact_root.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[Path, Path] = {}
    outputs[args.output_dir / f"{DATE_PREFIX}criterionC_results.csv"] = prepare_csv(
        helper,
        args.output_dir / f"{DATE_PREFIX}criterionC_results.csv",
        [criterion_row],
        tuple(criterion_row),
    )
    csv_specs = (
        ("timing_per_frame.csv", timing_rows),
        ("interval_timing.csv", interval_timing_rows),
        ("physical_skip_discovery_metrics.csv", metric_rows),
        ("semantic_parity.csv", parity_rows),
        ("physical_skip_call_proof.csv", proof_rows),
        ("pre_mrm_features.csv", feature_rows),
        ("oracle_skip_labels.csv", oracle_rows),
    )
    for name, rows in csv_specs:
        if not rows:
            continue
        path = args.artifact_root / name
        outputs[path] = prepare_csv(helper, path, rows, tuple(rows[0]))
    trace_path = args.artifact_root / "bounded_profiler_trace_summary.json"
    outputs[trace_path] = helper.prepare_json(trace_path, traces)
    schema_path = args.artifact_root / "pre_mrm_feature_schema.json"
    outputs[schema_path] = helper.prepare_json(schema_path, feature_schema)
    summary_path = args.artifact_root / "stage4C1_execution_summary.json"
    summary["output_hashes"] = {
        final.name: sha256_file(temp) for final, temp in outputs.items()
    }
    outputs[summary_path] = helper.prepare_json(summary_path, summary)
    for final, temp in outputs.items():
        os.replace(temp, final)

    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
