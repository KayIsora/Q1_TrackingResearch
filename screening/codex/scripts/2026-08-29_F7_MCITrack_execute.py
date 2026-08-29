#!/usr/bin/env python3
"""Execute the one locked deterministic F7 MCITrack scientific run."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import torch


RUNTIME_PATH = Path(__file__).with_name("2026-08-29_F7_MCITrack_runtime.py")
RUNTIME_SPEC = importlib.util.spec_from_file_location("f7_mcitrack_runtime", RUNTIME_PATH)
if RUNTIME_SPEC is None or RUNTIME_SPEC.loader is None:
    raise RuntimeError(f"Unable to load runtime module: {RUNTIME_PATH}")
rt = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(rt)


RAW_FIELDS = [
    "pair_id", "sequence", "condition", "frame", "ground_truth_xywh",
    "baseline_bbox_xywh", "zero_bbox_xywh", "stale_bbox_xywh",
    "baseline_iou", "zero_iou", "stale_iou",
    "baseline_center_error", "zero_center_error", "stale_center_error",
    "zero_contribution", "stale_contribution",
    "baseline_confidence", "zero_confidence", "stale_confidence",
    "baseline_controller_reset", "zero_controller_reset", "stale_controller_reset",
    "reset_threshold", "baseline_reset_margin", "zero_reset_margin", "stale_reset_margin",
    "incoming_state_norm_0", "incoming_state_norm_1", "incoming_state_norm_2", "incoming_state_norm_3",
    "incoming_state_finite_0", "incoming_state_finite_1", "incoming_state_finite_2", "incoming_state_finite_3",
    "incoming_state_none_0", "incoming_state_none_1", "incoming_state_none_2", "incoming_state_none_3",
    "baseline_call_signature", "zero_call_signature", "stale_call_signature", "call_parity",
    "baseline_model_seconds", "zero_model_seconds", "stale_model_seconds",
]


def load_preflight() -> Dict[str, Any]:
    path = rt.ARTIFACT_ROOT / "preflight.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "PASS" or data.get("scientific_outcome_rows") != 0:
        raise RuntimeError("Scientific execution requires a PASS preflight with zero outcome rows")
    if not all(data.get("gates", {}).values()):
        raise RuntimeError("Scientific execution requires every locked preflight gate to pass")
    return data


def interval_label(pair: Dict[str, Any], frame: int) -> str | None:
    for label in ("primary", "control"):
        start, end = pair[label]
        if start <= frame <= end:
            return label
    return None


def initialize_sequence(tracker: Any, evaluator: Any, sequence: Any) -> OrderedDict:
    tracker.h_state = [None] * len(tracker.h_state)
    init_info = sequence.init_info()
    init_info["seq_name"] = sequence.name
    tracker.initialize(rt.read_frame(evaluator, sequence, 1), init_info)
    return OrderedDict()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cuda",), default="cuda")
    args = parser.parse_args()

    rt.ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    raw_path = rt.ARTIFACT_ROOT / "per_frame_results.csv"
    status_path = rt.ARTIFACT_ROOT / "execution_status.json"
    load_preflight()
    status: Dict[str, Any] = {
        "status": "RUNNING",
        "mini_probe_terminal_state": None,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "f7_deadline_utc": rt.F7_DEADLINE_UTC.isoformat(),
        "device_requested": args.device,
        "scientific_rows_written": 0,
        "sequences_completed": 0,
        "model_execution_seconds": 0.0,
        "branch_order": ["BASELINE_RELEASED_STATE", "ZERO_ALL_CARRIED_STATES", "STALE_INTERVAL_START_STATES"],
        "none_to_stale_rule": "A released None state at interval_start-1 is materialized as the exact-shape FP32 zero tensor used by the official Mamba initialization semantics.",
        "preflight_path": str(rt.ARTIFACT_ROOT / "preflight.json"),
    }
    rt.write_json(status_path, status)

    rows_written = 0
    model_seconds = 0.0
    scientific_started = False
    instrumentation = None

    try:
        rt.enforce_deadline()
        rt.set_determinism()
        contract = rt.official_contract_record()
        rt.validate_contract(contract)
        runtime = rt.bootstrap_official(args.device)
        sequence_contract = rt.sequence_contract(runtime["sequences"])
        if sequence_contract["expected_rows"] != 254:
            raise RuntimeError("Locked row count is not 254")
        sequence_by_name = {sequence.name: sequence for sequence in runtime["sequences"]}
        tracker = runtime["tracker"]
        evaluator = runtime["evaluator"]

        with raw_path.open("w", newline="", encoding="utf-8") as raw_handle:
            writer = csv.DictWriter(raw_handle, fieldnames=RAW_FIELDS)
            writer.writeheader()
            raw_handle.flush()

            for pair_index, pair in enumerate(rt.PAIR_SPECS, start=1):
                sequence = sequence_by_name[pair["sequence"]]
                previous_output = initialize_sequence(tracker, evaluator, sequence)
                instrumentation = rt.CallInstrumentation(tracker.network)
                stale_by_condition: Dict[str, List[torch.Tensor]] = {}
                max_frame = max(pair["primary"][1], pair["control"][1])
                print(f"SEQUENCE_START {pair['pair_id']} {sequence.name} max_frame={max_frame}", flush=True)

                for frame in range(2, max_frame + 1):
                    rt.enforce_deadline()
                    image = rt.read_frame(evaluator, sequence, frame)
                    info = sequence.frame_info(frame - 1)
                    info["previous_output"] = previous_output
                    pre = rt.snapshot_tracker(tracker)

                    for condition_name in ("primary", "control"):
                        if frame == pair[condition_name][0]:
                            stale_by_condition[condition_name] = rt.materialize_state_list(tracker, pre["h_state"])

                    condition = interval_label(pair, frame)
                    if condition is None:
                        baseline_output, _, elapsed = rt.run_track(
                            tracker, image, info, instrumentation, instrumentation_enabled=False
                        )
                        model_seconds += elapsed
                        previous_output = OrderedDict(baseline_output)
                        continue

                    scientific_started = True
                    incoming = rt.state_descriptives(pre["h_state"])

                    rt.restore_tracker(tracker, pre)
                    baseline_output, baseline_record, baseline_seconds = rt.run_track(
                        tracker, image, info, instrumentation, True
                    )
                    baseline_post = rt.snapshot_tracker(tracker)

                    rt.restore_tracker(tracker, pre)
                    tracker.h_state = rt.materialize_state_list(tracker, [None] * len(tracker.h_state))
                    zero_output, zero_record, zero_seconds = rt.run_track(
                        tracker, image, info, instrumentation, True
                    )

                    rt.restore_tracker(tracker, pre)
                    tracker.h_state = [value.detach().clone() for value in stale_by_condition[condition]]
                    stale_output, stale_record, stale_seconds = rt.run_track(
                        tracker, image, info, instrumentation, True
                    )

                    rt.restore_tracker(tracker, baseline_post)
                    previous_output = OrderedDict(baseline_output)
                    model_seconds += baseline_seconds + zero_seconds + stale_seconds

                    baseline_bbox, baseline_confidence = rt.output_values(baseline_output)
                    zero_bbox, zero_confidence = rt.output_values(zero_output)
                    stale_bbox, stale_confidence = rt.output_values(stale_output)
                    ground_truth = [float(value) for value in sequence.ground_truth_rect[frame - 1]]
                    baseline_iou = rt.xywh_iou(baseline_bbox, ground_truth)
                    zero_iou = rt.xywh_iou(zero_bbox, ground_truth)
                    stale_iou = rt.xywh_iou(stale_bbox, ground_truth)
                    reset_threshold = float(tracker.update_h_t)
                    baseline_signature = rt.compute_signature(baseline_record)
                    zero_signature = rt.compute_signature(zero_record)
                    stale_signature = rt.compute_signature(stale_record)
                    call_parity = (
                        baseline_signature == zero_signature == stale_signature
                        and baseline_record["template_counts"] == [5]
                        and zero_record["template_counts"] == [5]
                        and stale_record["template_counts"] == [5]
                    )
                    finite_outputs = all(
                        torch.isfinite(torch.tensor(values)).all().item()
                        for values in (
                            baseline_bbox + [baseline_confidence],
                            zero_bbox + [zero_confidence],
                            stale_bbox + [stale_confidence],
                        )
                    )

                    row = {
                        "pair_id": pair["pair_id"],
                        "sequence": sequence.name,
                        "condition": condition,
                        "frame": frame,
                        "ground_truth_xywh": rt.json_compact(ground_truth),
                        "baseline_bbox_xywh": rt.json_compact(baseline_bbox),
                        "zero_bbox_xywh": rt.json_compact(zero_bbox),
                        "stale_bbox_xywh": rt.json_compact(stale_bbox),
                        "baseline_iou": baseline_iou,
                        "zero_iou": zero_iou,
                        "stale_iou": stale_iou,
                        "baseline_center_error": rt.center_error(baseline_bbox, ground_truth),
                        "zero_center_error": rt.center_error(zero_bbox, ground_truth),
                        "stale_center_error": rt.center_error(stale_bbox, ground_truth),
                        "zero_contribution": baseline_iou - zero_iou,
                        "stale_contribution": baseline_iou - stale_iou,
                        "baseline_confidence": baseline_confidence,
                        "zero_confidence": zero_confidence,
                        "stale_confidence": stale_confidence,
                        "baseline_controller_reset": baseline_confidence < reset_threshold,
                        "zero_controller_reset": zero_confidence < reset_threshold,
                        "stale_controller_reset": stale_confidence < reset_threshold,
                        "reset_threshold": reset_threshold,
                        "baseline_reset_margin": baseline_confidence - reset_threshold,
                        "zero_reset_margin": zero_confidence - reset_threshold,
                        "stale_reset_margin": stale_confidence - reset_threshold,
                        "baseline_call_signature": rt.json_compact(baseline_signature),
                        "zero_call_signature": rt.json_compact(zero_signature),
                        "stale_call_signature": rt.json_compact(stale_signature),
                        "call_parity": call_parity,
                        "baseline_model_seconds": baseline_seconds,
                        "zero_model_seconds": zero_seconds,
                        "stale_model_seconds": stale_seconds,
                    }
                    for index in range(4):
                        row[f"incoming_state_norm_{index}"] = incoming["norms"][index]
                        row[f"incoming_state_finite_{index}"] = incoming["finite"][index]
                        row[f"incoming_state_none_{index}"] = incoming["is_none"][index]
                    writer.writerow(row)
                    raw_handle.flush()
                    rows_written += 1

                    if not finite_outputs or not all(incoming["finite"]):
                        raise RuntimeError("Non-finite value detected after a scientific outcome row")
                    if not call_parity:
                        raise RuntimeError("Five-template/current-computation call parity failed after an outcome row")
                    if rows_written % 25 == 0:
                        print(f"PROGRESS rows={rows_written}/254 model_seconds={model_seconds:.3f}", flush=True)

                instrumentation.close()
                instrumentation = None
                status["sequences_completed"] = pair_index
                status["scientific_rows_written"] = rows_written
                status["model_execution_seconds"] = model_seconds
                rt.write_json(status_path, status)
                print(f"SEQUENCE_DONE {pair['pair_id']} rows={rows_written}", flush=True)
                torch.cuda.empty_cache()

        if rows_written != 254:
            raise RuntimeError(f"Scientific run completed with {rows_written} rows instead of 254")
        rt.enforce_deadline()
        status.update({
            "status": "COMPLETE",
            "scientific_rows_written": rows_written,
            "sequences_completed": 6,
            "model_execution_seconds": model_seconds,
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "raw_results_path": str(raw_path),
            "call_parity_all_rows": True,
            "scientific_run_count": 1,
        })
        rt.write_json(status_path, status)
        print(f"EXECUTION_STATUS=COMPLETE ROWS={rows_written} MODEL_SECONDS={model_seconds:.3f}", flush=True)
        return 0
    except Exception as error:
        if instrumentation is not None:
            instrumentation.close()
        status.update({
            "status": "STOPPED",
            "mini_probe_terminal_state": "PROBE_INCONCLUSIVE_RESOURCE_BLOCKER",
            "scientific_rows_written": rows_written,
            "model_execution_seconds": model_seconds,
            "failure_after_scientific_outcome": scientific_started,
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        })
        rt.write_json(status_path, status)
        print(f"EXECUTION_STATUS=STOPPED ROWS={rows_written} ERROR={type(error).__name__}: {error}", flush=True)
        return 2


if __name__ == "__main__":
    sys.exit(main())
