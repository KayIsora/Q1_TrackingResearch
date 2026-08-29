#!/usr/bin/env python3
"""Zero-outcome technical preflight for locked MCITrack F7."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import torch


RUNTIME_PATH = Path(__file__).with_name("2026-08-29_F7_MCITrack_runtime.py")
RUNTIME_SPEC = importlib.util.spec_from_file_location("f7_mcitrack_runtime", RUNTIME_PATH)
if RUNTIME_SPEC is None or RUNTIME_SPEC.loader is None:
    raise RuntimeError(f"Unable to load runtime module: {RUNTIME_PATH}")
rt = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(rt)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cuda",), default="cuda")
    args = parser.parse_args()

    output_path = rt.ARTIFACT_ROOT / "preflight.json"
    result = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "f7_asset_verified_utc": rt.F7_ASSET_VERIFIED_UTC.isoformat(),
        "f7_deadline_utc": rt.F7_DEADLINE_UTC.isoformat(),
        "device_requested": args.device,
        "scientific_outcome_rows": 0,
        "status": "FAIL",
    }
    instrumentation = None
    try:
        rt.enforce_deadline()
        rt.set_determinism()
        contract = rt.official_contract_record()
        rt.validate_contract(contract)
        runtime = rt.bootstrap_official(args.device)
        sequences = runtime["sequences"]
        evaluator = runtime["evaluator"]
        tracker = runtime["tracker"]
        sequence_contract = rt.sequence_contract(sequences)
        sequence = {item.name: item for item in sequences}[rt.PAIR_SPECS[0]["sequence"]]

        init_info = sequence.init_info()
        init_info["seq_name"] = sequence.name
        tracker.initialize(rt.read_frame(evaluator, sequence, 1), init_info)
        initialized = rt.snapshot_tracker(tracker)

        info2 = sequence.frame_info(1)
        info2["previous_output"] = OrderedDict()
        image2 = rt.read_frame(evaluator, sequence, 2)

        torch.cuda.synchronize()
        clean_output = tracker.track(image2, info2)
        torch.cuda.synchronize()
        clean_post = rt.snapshot_tracker(tracker)

        rt.restore_tracker(tracker, initialized)
        instrumentation = rt.CallInstrumentation(tracker.network)
        disabled_output, disabled_record, _ = rt.run_track(
            tracker, image2, info2, instrumentation, instrumentation_enabled=False
        )
        disabled_post = rt.snapshot_tracker(tracker)
        clean_bbox, clean_score = rt.output_values(clean_output)
        disabled_bbox, disabled_score = rt.output_values(disabled_output)
        disabled_continuation_equal, disabled_mismatches = rt.continuation_equal(clean_post, disabled_post)
        diagnostics_disabled_max_abs = max(
            rt.max_abs_diff(clean_bbox, disabled_bbox), abs(clean_score - disabled_score)
        )

        frame3_pre = clean_post
        info3 = sequence.frame_info(2)
        info3["previous_output"] = OrderedDict(clean_output)
        image3 = rt.read_frame(evaluator, sequence, 3)

        rt.restore_tracker(tracker, frame3_pre)
        baseline_a, baseline_record, _ = rt.run_track(tracker, image3, info3, instrumentation, True)
        baseline_post_a = rt.snapshot_tracker(tracker)

        rt.restore_tracker(tracker, frame3_pre)
        baseline_b, baseline_b_record, _ = rt.run_track(tracker, image3, info3, instrumentation, True)
        baseline_post_b = rt.snapshot_tracker(tracker)
        bbox_a, score_a = rt.output_values(baseline_a)
        bbox_b, score_b = rt.output_values(baseline_b)
        snapshot_exact, snapshot_mismatches = rt.continuation_equal(baseline_post_a, baseline_post_b)
        snapshot_output_max_abs = max(rt.max_abs_diff(bbox_a, bbox_b), abs(score_a - score_b))

        rt.restore_tracker(tracker, frame3_pre)
        tracker.h_state = rt.clone_state_list(tracker.h_state)
        noop_output, noop_record, _ = rt.run_track(tracker, image3, info3, instrumentation, True)
        bbox_noop, score_noop = rt.output_values(noop_output)
        noop_max_abs = max(rt.max_abs_diff(bbox_a, bbox_noop), abs(score_a - score_noop))

        rt.restore_tracker(tracker, frame3_pre)
        tracker.h_state = rt.materialize_state_list(tracker, [None] * len(tracker.h_state))
        _, zero_record, _ = rt.run_track(tracker, image3, info3, instrumentation, True)

        rt.restore_tracker(tracker, frame3_pre)
        tracker.h_state = rt.materialize_state_list(tracker, frame3_pre["h_state"])
        _, stale_record, _ = rt.run_track(tracker, image3, info3, instrumentation, True)

        baseline_signature = rt.compute_signature(baseline_record)
        call_parity = (
            baseline_signature == rt.compute_signature(baseline_b_record)
            == rt.compute_signature(noop_record)
            == rt.compute_signature(zero_record)
            == rt.compute_signature(stale_record)
        )
        five_template_parity = all(
            record["template_counts"] == [5]
            for record in (baseline_record, baseline_b_record, noop_record, zero_record, stale_record)
        )
        state_records = baseline_record["state_records"]
        state_shape_gate = len(state_records) == 4 and all(item["finite"] for item in state_records.values())

        gates = {
            "source_config_checkpoint_identity": (
                contract["source_sha"] == rt.EXPECTED_SOURCE_SHA
                and contract["source_clean"]
                and contract["config_hash_matches_pinned_blob"]
                and contract["checkpoint_sha256"] == rt.EXPECTED_CHECKPOINT_SHA256
            ),
            "single_official_bootstrap_identity": (
                contract["bootstrap_external_sha256"] == rt.EXPECTED_BOOTSTRAP_SHA256
                and contract["bootstrap_required_sha256"] == rt.EXPECTED_BOOTSTRAP_SHA256
                and contract["bootstrap_copy_exact"]
                and runtime["record"]["pretrained_bootstrap_bypassed"] is False
            ),
            "strict_load": runtime["record"]["strict_checkpoint_load"] == "PASS",
            "official_deterministic_frame_smoke": snapshot_output_max_abs == 0.0 and snapshot_exact,
            "diagnostics_disabled_parity": diagnostics_disabled_max_abs <= 1e-6 and disabled_continuation_equal,
            "snapshot_restore_parity": snapshot_output_max_abs == 0.0 and snapshot_exact,
            "state_copy_noop_parity": noop_max_abs <= 1e-6,
            "four_state_contract": state_shape_gate,
            "five_template_parity": five_template_parity,
            "current_compute_call_parity": call_parity,
            "locked_dataset_contract": sequence_contract["expected_rows"] == 254 and len(sequence_contract["pairs"]) == 6,
            "within_four_hour_cap": datetime.now(timezone.utc) <= rt.F7_DEADLINE_UTC,
        }
        result.update({
            "contract": contract,
            "runtime": runtime["record"],
            "dataset_contract": sequence_contract,
            "gates": gates,
            "diagnostics_disabled": {
                "max_abs": diagnostics_disabled_max_abs,
                "continuation_equal": disabled_continuation_equal,
                "mismatches": disabled_mismatches,
                "disabled_hook_record": disabled_record,
            },
            "snapshot_restore": {
                "bbox_score_max_abs": snapshot_output_max_abs,
                "continuation_exact": snapshot_exact,
                "mismatches": snapshot_mismatches,
            },
            "state_copy_noop": {"bbox_score_max_abs": noop_max_abs},
            "state_contract": state_records,
            "call_signature": baseline_signature,
            "status": "PASS" if all(gates.values()) else "FAIL",
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        })
        rt.write_json(output_path, result)
        print(f"PRECHECK_STATUS={result['status']}")
        print("SCIENTIFIC_OUTCOME_ROWS=0")
        print(f"OUTPUT={output_path}")
        return 0 if result["status"] == "PASS" else 2
    except Exception as error:
        result.update({
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
            "completed_utc": datetime.now(timezone.utc).isoformat(),
        })
        rt.write_json(output_path, result)
        print(f"PRECHECK_STATUS=FAIL\nERROR={type(error).__name__}: {error}\nOUTPUT={output_path}")
        return 2
    finally:
        if instrumentation is not None:
            instrumentation.close()


if __name__ == "__main__":
    sys.exit(main())
