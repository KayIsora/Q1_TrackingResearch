#!/usr/bin/env python3
"""Zero-outcome technical preflight for the locked F2-B mini-probe."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import torch

RUNTIME_PATH = Path(__file__).with_name("2026-08-29_F2B_MCITrack_runtime.py")
RUNTIME_SPEC = importlib.util.spec_from_file_location("f2b_mcitrack_runtime", RUNTIME_PATH)
if RUNTIME_SPEC is None or RUNTIME_SPEC.loader is None:
    raise RuntimeError(f"Unable to load runtime module: {RUNTIME_PATH}")
runtime_module = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(runtime_module)

ARTIFACT_ROOT = runtime_module.ARTIFACT_ROOT
CallInstrumentation = runtime_module.CallInstrumentation
PAIR_SPECS = runtime_module.PAIR_SPECS
bootstrap_official = runtime_module.bootstrap_official
clone_state_list = runtime_module.clone_state_list
compute_signature = runtime_module.compute_signature
continuation_equal = runtime_module.continuation_equal
materialize_state_list = runtime_module.materialize_state_list
max_abs_diff = runtime_module.max_abs_diff
official_contract_record = runtime_module.official_contract_record
output_values = runtime_module.output_values
read_frame = runtime_module.read_frame
restore_tracker = runtime_module.restore_tracker
run_track = runtime_module.run_track
sequence_contract = runtime_module.sequence_contract
set_determinism = runtime_module.set_determinism
snapshot_tracker = runtime_module.snapshot_tracker
validate_contract = runtime_module.validate_contract
write_json = runtime_module.write_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", choices=("cuda", "cpu"), default="cuda")
    args = parser.parse_args()

    output_path = ARTIFACT_ROOT / "preflight.json"
    result = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "device_requested": args.device,
        "scientific_outcome_rows": 0,
        "status": "FAIL",
    }
    instrumentation = None
    try:
        set_determinism()
        contract = official_contract_record()
        validate_contract(contract)
        runtime = bootstrap_official(args.device)
        sequences = runtime["sequences"]
        evaluator = runtime["evaluator"]
        tracker = runtime["tracker"]
        seq_contract = sequence_contract(sequences)
        by_name = {seq.name: seq for seq in sequences}
        sequence = by_name[PAIR_SPECS[0]["sequence"]]

        init_info = sequence.init_info()
        init_info["seq_name"] = sequence.name
        tracker.initialize(read_frame(evaluator, sequence, 1), init_info)
        initialized = snapshot_tracker(tracker)

        info2 = sequence.frame_info(1)
        info2["previous_output"] = OrderedDict()
        image2 = read_frame(evaluator, sequence, 2)

        # Truly clean official forward: no observation hooks are installed yet.
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        clean_output = tracker.track(image2, info2)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        clean_post = snapshot_tracker(tracker)

        # Hooks installed but disabled must leave the released forward unchanged.
        restore_tracker(tracker, initialized)
        instrumentation = CallInstrumentation(tracker.network)
        disabled_output, disabled_record, _ = run_track(
            tracker, image2, info2, instrumentation, instrumentation_enabled=False
        )
        disabled_post = snapshot_tracker(tracker)
        clean_bbox, clean_score = output_values(clean_output)
        disabled_bbox, disabled_score = output_values(disabled_output)
        disabled_continuation_equal, disabled_mismatches = continuation_equal(clean_post, disabled_post)
        diagnostics_disabled_max_abs = max(
            max_abs_diff(clean_bbox, disabled_bbox), abs(clean_score - disabled_score)
        )

        # Frame 3 begins with real carried state produced by the clean frame-2 forward.
        frame3_pre = clean_post
        info3 = sequence.frame_info(2)
        info3["previous_output"] = OrderedDict(clean_output)
        image3 = read_frame(evaluator, sequence, 3)

        restore_tracker(tracker, frame3_pre)
        baseline_a, baseline_record, _ = run_track(tracker, image3, info3, instrumentation, True)
        baseline_post_a = snapshot_tracker(tracker)

        restore_tracker(tracker, frame3_pre)
        baseline_b, baseline_b_record, _ = run_track(tracker, image3, info3, instrumentation, True)
        baseline_post_b = snapshot_tracker(tracker)
        bbox_a, score_a = output_values(baseline_a)
        bbox_b, score_b = output_values(baseline_b)
        snapshot_exact, snapshot_mismatches = continuation_equal(baseline_post_a, baseline_post_b)
        snapshot_output_max_abs = max(max_abs_diff(bbox_a, bbox_b), abs(score_a - score_b))

        restore_tracker(tracker, frame3_pre)
        tracker.h_state = clone_state_list(tracker.h_state)
        noop_output, noop_record, _ = run_track(tracker, image3, info3, instrumentation, True)
        bbox_noop, score_noop = output_values(noop_output)
        noop_max_abs = max(max_abs_diff(bbox_a, bbox_noop), abs(score_a - score_noop))

        restore_tracker(tracker, frame3_pre)
        tracker.h_state = materialize_state_list(tracker, [None] * len(tracker.h_state))
        _, zero_record, _ = run_track(tracker, image3, info3, instrumentation, True)

        restore_tracker(tracker, frame3_pre)
        tracker.h_state = materialize_state_list(tracker, frame3_pre["h_state"])
        _, stale_record, _ = run_track(tracker, image3, info3, instrumentation, True)

        baseline_signature = compute_signature(baseline_record)
        call_parity = (
            baseline_signature == compute_signature(baseline_b_record)
            == compute_signature(noop_record)
            == compute_signature(zero_record)
            == compute_signature(stale_record)
        )
        five_template_parity = all(
            record["template_counts"] == [5]
            for record in (baseline_record, baseline_b_record, noop_record, zero_record, stale_record)
        )
        state_records = baseline_record["state_records"]
        state_shape_gate = len(state_records) == 4 and all(item["finite"] for item in state_records.values())

        gates = {
            "pinned_source": contract["source_sha"] == "e667193eaec4c8a73d4bdd856a662aecdb844b43",
            "clean_source": contract["source_clean"],
            "config_hash": contract["config_hash_matches_pinned_blob"],
            "checkpoint_hash": contract["checkpoint_sha256"] == "6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9",
            "strict_load": runtime["record"]["strict_checkpoint_load"] == "PASS",
            "official_evaluator_bootstrap": True,
            "deterministic_clean_forward": snapshot_output_max_abs == 0.0 and snapshot_exact,
            "diagnostics_disabled_parity": diagnostics_disabled_max_abs <= 1e-6 and disabled_continuation_equal,
            "snapshot_restore_parity": snapshot_output_max_abs == 0.0 and snapshot_exact,
            "state_copy_noop_parity": noop_max_abs <= 1e-6,
            "four_state_contract": state_shape_gate,
            "five_template_parity": five_template_parity,
            "current_compute_call_parity": call_parity,
            "locked_dataset_contract": seq_contract["expected_rows"] == 254 and len(seq_contract["pairs"]) == 6,
        }
        result.update(
            {
                "contract": contract,
                "runtime": runtime["record"],
                "dataset_contract": seq_contract,
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
            }
        )
        write_json(output_path, result)
        print(f"PRECHECK_STATUS={result['status']}")
        print(f"SCIENTIFIC_OUTCOME_ROWS={result['scientific_outcome_rows']}")
        print(f"OUTPUT={output_path}")
        return 0 if result["status"] == "PASS" else 2
    except Exception as error:
        result.update(
            {
                "error_type": type(error).__name__,
                "error": str(error),
                "traceback": traceback.format_exc(),
                "completed_utc": datetime.now(timezone.utc).isoformat(),
            }
        )
        write_json(output_path, result)
        print(f"PRECHECK_STATUS=FAIL\nERROR={type(error).__name__}: {error}\nOUTPUT={output_path}")
        return 2
    finally:
        if instrumentation is not None:
            instrumentation.close()


if __name__ == "__main__":
    sys.exit(main())
