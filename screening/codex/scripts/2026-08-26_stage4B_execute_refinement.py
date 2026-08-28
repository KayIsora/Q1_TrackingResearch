#!/usr/bin/env python3
"""Execute the one locked Stage-4B bounded-refinement package.

This runner is intentionally narrow.  It is enabled only by a hash-bound
Criterion-B PASS whose selected path is exactly ``mrm1``.  It then executes:

* T1 ``mrm1_retriever`` and ``mrm1_mlp`` state-matched interval forks;
* the exact SpikeTrack-S256-T3 baseline over all frozen discovery intervals;
* when machine preflight confirms the accepted patch supports them, the three
  T3 ``mrm1_template1`` ... ``mrm1_template3`` state-matched controls.

All controls characterize contribution while retaining full computation;
``physical_skip`` is always false.  Only DISCOVERY rows and discovery source
paths are used.  HOLDOUT IDs remain a hard read guard and no holdout outcome or
dataset path is constructed.  Repository outputs are written only after the
whole bounded run and its coverage checks succeed.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import gc
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import statistics
import sys
import time
from types import ModuleType, SimpleNamespace
from typing import Any, Mapping, Sequence


PINNED_SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
T1_CONFIG_SHA256 = "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
T1_CHECKPOINT_SHA256 = (
    "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
)
T3_CONFIG_SHA256 = "369e0ed9e237909bd693b33252068fc9a0ac447eb50a1969579602164695f240"
T3_CHECKPOINT_SHA256 = (
    "ccf04aa90521b21a78b12f4b978c03d8a69b5f6de3ee3498a3594e13e98aa491"
)
PATCH_SHA256_CANONICAL_LF = (
    "d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a"
)
FROZEN_SLICE_SHA256_NORMALIZED_LF = (
    "bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a"
)
EXPECTED_SELECTED_PATH = "mrm1"
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{index:02d}" for index in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
LOCKED_PRIMARY_MODES = (
    "mrm1", "mrm2", "mrm3", "mrm4", "mrm5", "mrm6",
    "early", "middle", "late",
)
MODE_SELECTION_META = {
    "mrm1": (1, 1), "mrm2": (1, 2), "mrm3": (1, 3),
    "mrm4": (1, 4), "mrm5": (1, 5), "mrm6": (1, 6),
    "early": (2, 1), "middle": (2, 3), "late": (2, 5),
}
SEED = 20260826
PARITY_TOLERANCE = 1e-6

PATCHED_FILE_SHA256 = {
    "lib/models/spiketrack/sdtv3_search_inference.py": (
        "77b01cb252919c5a9e50500cc567f8c2766ac86ccd343dfcc7d3af7e95b72931"
    ),
    "lib/models/spiketrack/spiketrack_inf.py": (
        "01a1f891ff10542ce32cbffafd820e0338c5ea4ff67f59065ea3a7e044aa71f8"
    ),
    "lib/test/parameter/spiketrack.py": (
        "fcd53eb2f88e38f673dbb81d6b5c2e83b7b2b2f956d1105f4980a7890aa5af81"
    ),
    "lib/test/tracker/spiketrack_inf.py": (
        "56c0a985cdf5905e7e1c16383b4e9ad41406c3718e066bdf4a6f0701dc427471"
    ),
    "tracking/stage4a_spiketrack_smoke.py": (
        "477730db506c43e31cf8161b770c9479c1e611fc825affe85dfdee5ed947c002"
    ),
}
PATCHED_PATHS = tuple(PATCHED_FILE_SHA256)

DISCOVERY_SOURCE_ALIASES = {
    "Jogging_1": {
        "path": "Jogging/img",
        "anno_path": "Jogging/groundtruth_rect.1.txt",
        "evidence": "2026-08-25_stage4A_E2_otb_source_manifest.csv row E2-OTB-062",
    }
}

T1_CONDITIONS = (
    {
        "condition": "retriever_only_bypass",
        "selector": "mrm1_retriever",
        "kind": "retriever",
        "template_path": None,
    },
    {
        "condition": "mlp_only_bypass",
        "selector": "mrm1_mlp",
        "kind": "mlp",
        "template_path": None,
    },
)
T1_BASELINE_PARITY = {
    "condition": "t1_baseline_parity",
    "selector": "none",
    "kind": "none",
    "template_path": None,
}
T3_BASELINE = {
    "condition": "t3_baseline",
    "selector": "none",
    "kind": "none",
    "template_path": None,
}
T3_CONTROL_NAMES = (
    "t3_template_path_1_zero_contribution",
    "t3_template_path_2_zero_contribution",
    "t3_template_path_3_zero_contribution",
)
T3_CONDITIONS = tuple(
    {
        "condition": condition,
        "selector": f"mrm1_template{index}",
        "kind": "template",
        "template_path": index,
    }
    for index, condition in enumerate(T3_CONTROL_NAMES, start=1)
)
CONDITION_ORDER = {
    "retriever_only_bypass": 1,
    "mlp_only_bypass": 2,
    "t3_baseline": 3,
    "t3_template_path_1_zero_contribution": 4,
    "t3_template_path_2_zero_contribution": 5,
    "t3_template_path_3_zero_contribution": 6,
}

REPO_OUTPUT_NAMES = (
    "retriever_mlp_per_frame_metrics.csv",
    "t3_per_frame_metrics.csv",
    "bounded_refinement_execution_manifest.csv",
    "bounded_refinement_timing_characterization.csv",
    "bounded_refinement_execution_summary.json",
)
OUTPUT_HASH_NAMES = REPO_OUTPUT_NAMES[:4]
FRAME_FIELDS = (
    "pair_id", "side", "sequence", "frame_index", "condition",
    "selected_refinement_path", "iou", "iou_float", "failure",
    "success_at_0_5", "center_error", "physical_skip",
    "pred_x_float", "pred_y_float", "pred_w_float", "pred_h_float",
    "pred_x_int", "pred_y_int", "pred_w_int", "pred_h_int",
    "gt_x", "gt_y", "gt_w", "gt_h", "score_map_max",
    "confidence_score", "model_forward_ms", "initialization_frame",
    "evaluator_first_frame_override", "branch_frame_executed",
    "tracker_mode", "ablation_control",
)
MANIFEST_FIELDS = (
    "pair_id", "side", "sequence", "interval_start", "interval_end",
    "condition", "selected_refinement_path", "physical_skip", "status",
    "tracker_mode", "ablation_control", "source_row_sha256_canonical_lf",
    "snapshot_frame", "start_snapshot_sha256",
    "restored_start_snapshot_sha256", "start_restore_exact",
    "baseline_end_snapshot_sha256",
    "continuation_restored_snapshot_sha256", "continuation_restore_exact",
    "interval_output_frames", "tracked_branch_frames",
    "official_initialization_frames_zero_contribution",
    "raw_jsonl_first_line", "raw_jsonl_last_line",
    "raw_jsonl_external_path",
)
TIMING_METRICS = (
    "retriever_latency_ms", "mlp_latency_ms", "total_mrm_compute_latency_ms",
    "diagnostic_norm_fingerprint_overhead_ms",
    "total_instrumented_mrm_latency_ms", "total_tracker_model_forward_ms",
)

SNAPSHOT_CAPTURE_DESCRIPTION = (
    "tracker.state;tracker.frame_id;tracker.template_list;tracker.cache;"
    "tracker.spike_rate_dict_temp;tracker.last_template_refresh_frame;"
    "tracker.window_penalty;tracker.stage4a flags/records;"
    "network.current_image_idx;network.spike_rate_dict;"
    "encoder._stage4a flags/forward_id/current+completed records;"
    "MRM retriever capture flags/buffers;"
    "template_encoder.current_image_idx+spike_rate_dict_temp;"
    "Python+NumPy+Torch CPU+all CUDA RNG"
)


class RefinementContractError(RuntimeError):
    """A gate, model, state, or output contract was not satisfied."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--slice-csv", type=Path, required=True)
    parser.add_argument("--t1-config", type=Path, required=True)
    parser.add_argument("--t1-checkpoint", type=Path, required=True)
    parser.add_argument("--t3-config", type=Path, required=True)
    parser.add_argument("--t3-checkpoint", type=Path, required=True)
    parser.add_argument("--baseline-csv", type=Path, required=True)
    parser.add_argument("--analysis-summary", type=Path, required=True)
    parser.add_argument("--criterion-b-results", type=Path, required=True)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_bool(value: object, context: str) -> bool:
    normalized = str(value).strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise RefinementContractError(f"{context}: malformed boolean {value!r}")


def parse_float(value: object, context: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise RefinementContractError(f"{context}: malformed float {value!r}") from exc
    if not math.isfinite(result):
        raise RefinementContractError(f"{context}: non-finite float {value!r}")
    return result


def load_criterion_b_helpers(script_path: Path) -> ModuleType:
    """Load the accepted Criterion-B runner as a read-only helper module."""
    if not script_path.is_file():
        raise FileNotFoundError(script_path)
    name = "stage4b_criterion_b_execution_helpers"
    spec = importlib.util.spec_from_file_location(name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load Criterion-B helper module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def validate_refinement_gate(
    analysis_path: Path,
    criterion_b_results_path: Path,
    artifact_root: Path,
    slice_path: Path,
    slice_sha256: str,
    baseline_path: Path,
    baseline_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Bind the run to the final locked A/B analysis and selected mrm1 path."""
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    if analysis.get("schema_version") != "stage4b-analysis-v1":
        raise RefinementContractError("Analysis schema is not stage4b-analysis-v1")
    criterion_a = analysis.get("criterion_a")
    criterion_b = analysis.get("criterion_b")
    if not isinstance(criterion_a, Mapping) or not isinstance(criterion_b, Mapping):
        raise RefinementContractError("Analysis A/B gate objects are missing")
    if criterion_a.get("status") != "PASS" or criterion_a.get("pass") is not True:
        raise RefinementContractError("Bounded refinement is forbidden after Criterion-A non-pass")
    if criterion_b.get("status") != "PASS" or criterion_b.get("pass") is not True:
        raise RefinementContractError("Bounded refinement is forbidden after Criterion-B non-pass")
    if criterion_b.get("selected_refinement_path") != EXPECTED_SELECTED_PATH:
        raise RefinementContractError(
            "The locked selected refinement path is not exactly mrm1"
        )
    if analysis.get("next_action") != "RUN_BOUNDED_REFINEMENT_FOR_SELECTED_PATH_ONLY":
        raise RefinementContractError("Final analysis does not authorize bounded refinement")
    boundary = analysis.get("frozen_boundary")
    if not isinstance(boundary, Mapping) or (
        boundary.get("validation") != "PASS"
        or boundary.get("discovery_pair_count") != 12
        or boundary.get("holdout_outcomes_read") != 0
        or boundary.get("holdout_pairs_present_in_outcome_inputs") != 0
    ):
        raise RefinementContractError("Final analysis frozen/holdout boundary is not PASS")

    frozen_input = analysis.get("inputs", {}).get("frozen_slice", {})
    baseline_input = analysis.get("inputs", {}).get("baseline_csv", {})
    mode_input = analysis.get("inputs", {}).get("mode_csv", {})
    if (
        Path(str(frozen_input.get("path", ""))).resolve() != slice_path.resolve()
        or frozen_input.get("sha256_normalized_lf") != slice_sha256
    ):
        raise RefinementContractError("Analysis frozen-slice binding mismatch")
    if (
        Path(str(baseline_input.get("path", ""))).resolve() != baseline_path.resolve()
        or baseline_input.get("sha256") != baseline_sha256
        or baseline_input.get("rows") != 596
    ):
        raise RefinementContractError("Analysis T1 baseline binding mismatch")
    mode_path = artifact_root / "mode_per_frame_metrics.csv"
    if (
        Path(str(mode_input.get("path", ""))).resolve() != mode_path.resolve()
        or mode_input.get("sha256") != sha256_file(mode_path)
        or mode_input.get("rows") != 5364
    ):
        raise RefinementContractError("Analysis Criterion-B mode input binding mismatch")
    output_record = analysis.get("outputs", {}).get("criterion_b", {})
    if (
        Path(str(output_record.get("path", ""))).resolve()
        != criterion_b_results_path.resolve()
        or output_record.get("sha256") != sha256_file(criterion_b_results_path)
    ):
        raise RefinementContractError("Analysis Criterion-B result binding mismatch")

    with criterion_b_results_path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 9 or tuple(row.get("mode") for row in rows) != LOCKED_PRIMARY_MODES:
        raise RefinementContractError("Criterion-B result family is not the exact nine tests")
    passing: list[tuple[str, float, int, int]] = []
    selected_rows: list[str] = []
    for expected_order, row in enumerate(rows, start=1):
        mode = str(row.get("mode", ""))
        if int(row.get("test_order", "0")) != expected_order:
            raise RefinementContractError("Criterion-B result order mismatch")
        if parse_bool(row.get("physical_skip"), f"Criterion-B {mode} physical_skip"):
            raise RefinementContractError("Criterion-B result reports physical_skip=true")
        if not parse_bool(row.get("criterion_b_pass"), f"Criterion-B {mode} family pass"):
            raise RefinementContractError("Criterion-B rows disagree with family PASS")
        if parse_bool(row.get("test_pass"), f"Criterion-B {mode} test pass"):
            group_size, lower_index = MODE_SELECTION_META[mode]
            passing.append(
                (
                    mode,
                    abs(parse_float(row.get("mean_interaction"), f"{mode} interaction")),
                    group_size,
                    lower_index,
                )
            )
        if parse_bool(row.get("selected_refinement_path"), f"{mode} selected"):
            selected_rows.append(mode)
    if not passing:
        raise RefinementContractError("Criterion-B PASS has no passing primary test")
    derived_selected = min(passing, key=lambda item: (-item[1], item[2], item[3]))[0]
    if derived_selected != EXPECTED_SELECTED_PATH or selected_rows != [EXPECTED_SELECTED_PATH]:
        raise RefinementContractError("Locked refinement selection does not recompute to mrm1")

    execution_path = artifact_root / "criterionB_execution_summary.json"
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    if (
        execution.get("status") != "CRITERION_B_NINE_MODE_EXECUTION_COMPLETE_ANALYSIS_PENDING"
        or execution.get("scope") != "STAGE4B_DISCOVERY_CRITERION_B_ONLY"
        or execution.get("modes") != list(LOCKED_PRIMARY_MODES)
        or execution.get("discovery_pairs_executed") != 12
        or execution.get("discovery_intervals_executed") != 24
        or execution.get("holdout_pairs_executed") != 0
        or execution.get("holdout_outcomes_read") != 0
        or execution.get("physical_skip") is not False
        or execution.get("refinement_executed") is not False
        or execution.get("state_snapshot_parity", {}).get("status") != "PASS"
        or execution.get("baseline_branch_parity", {}).get("status") != "PASS"
    ):
        raise RefinementContractError("Criterion-B execution gate is absent or incomplete")
    output_hashes = execution.get("output_hashes")
    expected_execution_outputs = {
        "state_snapshot_parity.csv",
        "mode_per_frame_metrics.csv",
        "mode_execution_manifest.csv",
        "mode_module_timing_characterization.csv",
    }
    if not isinstance(output_hashes, Mapping) or set(output_hashes) != expected_execution_outputs:
        raise RefinementContractError("Criterion-B execution output-hash map mismatch")
    for name in expected_execution_outputs:
        if output_hashes.get(name) != sha256_file(artifact_root / name):
            raise RefinementContractError(f"Criterion-B execution output hash mismatch: {name}")
    return analysis, execution


def configure_determinism(torch_module: Any, np_module: Any, seed: int) -> None:
    random.seed(seed)
    np_module.random.seed(seed)
    torch_module.manual_seed(seed)
    torch_module.cuda.manual_seed_all(seed)
    torch_module.backends.cudnn.benchmark = False
    torch_module.backends.cudnn.deterministic = True
    torch_module.use_deterministic_algorithms(True)
    if not torch_module.cuda.is_available():
        raise RuntimeError("Authorized local CUDA GPU is unavailable")
    if (
        os.environ.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8"
        or not torch_module.are_deterministic_algorithms_enabled()
        or not torch_module.backends.cudnn.deterministic
        or torch_module.backends.cudnn.benchmark
    ):
        raise RuntimeError("Exact deterministic settings were not established")


def make_tracker(
    cfg: Any,
    update_config_from_file: Any,
    tracker_class: Any,
    config_path: Path,
    checkpoint_path: Path,
    template_count: int,
) -> Any:
    update_config_from_file(str(config_path))
    if (
        cfg.MODEL.ENCODER.TYPE != "Efficient_Spiking_Transformer_s"
        or cfg.TEST.SEARCH_SIZE != 256
        or cfg.TEST.NUM_TEMPLATES != template_count
    ):
        raise RefinementContractError(
            f"Resolved model is not exact SpikeTrack-S256-T{template_count}"
        )
    params = SimpleNamespace(
        cfg=cfg,
        template_factor=cfg.TEST.TEMPLATE_FACTOR,
        template_size=cfg.TEST.TEMPLATE_SIZE,
        search_factor=cfg.TEST.SEARCH_FACTOR,
        search_size=cfg.TEST.SEARCH_SIZE,
        save_all_boxes=False,
        debug=0,
        yaml_name=config_path.stem,
        stage4a_diagnostics=False,
        stage4a_ablation="none",
        stage4a_log_path="",
    )
    tracker = tracker_class(
        params,
        dataset_name="otb",
        checkpoint_path=str(checkpoint_path),
        save_sfr=False,
    )
    if tracker.num_template != template_count:
        raise RefinementContractError(
            f"Tracker runtime is T{tracker.num_template}, expected T{template_count}"
        )
    return tracker


def validate_diagnostic_semantics(
    helper: ModuleType,
    records: list[dict[str, Any]],
    selector: str,
    kind: str,
    template_path: int | None,
    tracker_mode: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    # The Criterion-B helper's validator intentionally understands only the
    # nine whole/group selectors.  Refinement selectors have different
    # component semantics, so perform the common structural checks locally
    # before the Retriever/MLP/template-specific checks below.
    tracker_records = [
        record for record in records if record.get("record_type") == "tracker_frame"
    ]
    mrm_records = [record for record in records if record.get("record_type") == "mrm"]
    if len(tracker_records) != 1:
        raise RefinementContractError(
            f"{selector}: expected one tracker_frame record, got {len(tracker_records)}"
        )
    tracker_record = tracker_records[0]
    if len(records) != 7 or [record.get("mrm_id") for record in mrm_records] != [
        f"MRM{index}" for index in range(1, 7)
    ]:
        raise RefinementContractError(f"{selector}: diagnostic MRM order/count mismatch")
    if tracker_record.get("ablation_control") != selector:
        raise RefinementContractError(f"{selector}: tracker selector mismatch")
    if any(record.get("ablation_control") != selector for record in mrm_records):
        raise RefinementContractError(f"{selector}: MRM selector mismatch")
    if tracker_record.get("tracker_mode") != tracker_mode:
        raise RefinementContractError(
            f"Diagnostic tracker mode {tracker_record.get('tracker_mode')!r} != {tracker_mode}"
        )
    if {record.get("mrm_id") for record in mrm_records} != {
        f"MRM{index}" for index in range(1, 7)
    }:
        raise RefinementContractError("Diagnostic record does not contain exactly MRM1..MRM6")
    selected_ids = {
        record["mrm_id"] for record in mrm_records if record.get("zero_residual_applied")
    }
    expected_selected = set() if kind == "none" else {"MRM1"}
    if selected_ids != expected_selected:
        raise RefinementContractError(
            f"{selector}: applied MRM set {sorted(selected_ids)} != {sorted(expected_selected)}"
        )
    for record in mrm_records:
        selected = record["mrm_id"] == "MRM1" and kind != "none"
        expected_kind = kind if selected else "none"
        if record.get("control_kind") != expected_kind:
            raise RefinementContractError(f"{selector}: control-kind mismatch")
        if record.get("physical_skip") is not False:
            raise RefinementContractError(f"{selector}: physical_skip must be false")
        if record.get("all_retriever_and_mlp_compute_executed") is not True:
            raise RefinementContractError(f"{selector}: full component compute not observed")
        if not selected and any(
            bool(record.get(key))
            for key in (
                "whole_mrm_bypass_applied", "retriever_bypass_applied",
                "mlp_bypass_applied", "template_path_zero_applied",
            )
        ):
            raise RefinementContractError(f"{selector}: nonselected MRM was controlled")
    selected_record = next(
        (record for record in mrm_records if record["mrm_id"] == "MRM1"), None
    )
    if selected_record is None:
        raise RefinementContractError("MRM1 diagnostic record missing")
    if kind == "retriever" and (
        selected_record.get("retriever_bypass_applied") is not True
        or selected_record.get("mlp_input_source") != "unchanged_mrm_input"
        or selected_record.get("mlp_bypass_applied") is not False
    ):
        raise RefinementContractError("Retriever-only bypass semantics were not exact")
    if kind == "mlp" and (
        selected_record.get("mlp_bypass_applied") is not True
        or selected_record.get("retriever_bypass_applied") is not False
    ):
        raise RefinementContractError("MLP-only bypass semantics were not exact")
    if kind == "template":
        raw_norms = selected_record.get("pre_gate_response_norms_l2")
        applied_norms = selected_record.get("applied_pre_gate_response_norms_l2")
        if (
            tracker_mode != "T3"
            or selected_record.get("template_time_dim") != 3
            or selected_record.get("cache_template_dim") != 3
            or selected_record.get("template_path_zero_applied") != template_path
            or selected_record.get("all_pre_gate_paths_computed_before_template_control")
            is not True
            or not isinstance(raw_norms, list)
            or len(raw_norms) != 3
            or not isinstance(applied_norms, list)
            or len(applied_norms) != 3
            or applied_norms[int(template_path) - 1] != 0.0
        ):
            raise RefinementContractError(
                f"{selector}: T3 pre-gate template-path zeroing was not machine verified"
            )
    return mrm_records, tracker_record


def t3_control_preflight(helper: ModuleType, tracker: Any) -> tuple[bool, dict, str]:
    """Verify selector wiring without opening or executing any dataset frame."""
    checks: dict[str, Any] = {
        "method": "PATCH_SELECTOR_AND_RUNTIME_MODEL_STRUCTURE_PREFLIGHT_NO_DATASET_FRAME",
        "tracker_num_templates": int(tracker.num_template),
        "encoder_mrm_count": None,
        "selectors": {},
    }
    try:
        encoder = tracker.network.encoder
        checks["encoder_mrm_count"] = len(encoder.mrm)
        if tracker.num_template != 3 or len(encoder.mrm) != 6:
            raise RefinementContractError("T3 runtime does not expose 3 templates and 6 MRMs")
        for index in range(1, 4):
            selector = f"mrm1_template{index}"
            helper.configure_diagnostics(tracker, True, selector)
            selector_check = {
                "control_kind": encoder._stage4a_control_kind,
                "selected_code_indices": sorted(encoder._stage4a_ablation_indices),
                "zero_based_template_index": encoder._stage4a_template_index,
            }
            checks["selectors"][selector] = selector_check
            if selector_check != {
                "control_kind": "template",
                "selected_code_indices": [0],
                "zero_based_template_index": index - 1,
            }:
                raise RefinementContractError(f"Selector wiring mismatch for {selector}")
        helper.configure_diagnostics(tracker, False, "none")
        checks["status"] = "PASS"
        return True, checks, ""
    except Exception as exc:
        try:
            helper.configure_diagnostics(tracker, False, "none")
        except Exception:
            pass
        checks["status"] = "NOT_TECHNICALLY_VALID"
        checks["exception_type"] = type(exc).__name__
        checks["exception"] = str(exc)
        blocker = (
            "T3_SELECTED_MRM1_TEMPLATE_PATH_CONTROLS_NOT_TECHNICALLY_VALID: "
            f"{type(exc).__name__}: {exc}"
        )
        return False, checks, blocker


def initialize_row(
    condition: Mapping[str, Any],
    interval: Any,
    float_box: Any,
    gt_box: Any,
    helper: ModuleType,
    tracker_mode: str,
) -> dict[str, Any]:
    int_box = float_box.astype(np.int64)
    iou = helper.inclusive_iou(int_box, gt_box)
    return {
        "pair_id": interval.pair_id,
        "side": interval.side,
        "sequence": interval.sequence,
        "frame_index": 1,
        "condition": condition["condition"],
        "selected_refinement_path": EXPECTED_SELECTED_PATH,
        "iou": iou,
        "iou_float": helper.inclusive_iou(float_box, gt_box),
        "failure": int(iou < 0.5),
        "success_at_0_5": int(iou >= 0.5),
        "center_error": helper.inclusive_center_error(int_box, gt_box),
        "physical_skip": False,
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
        "score_map_max": "",
        "confidence_score": "",
        "model_forward_ms": "",
        "initialization_frame": True,
        "evaluator_first_frame_override": True,
        "branch_frame_executed": False,
        "tracker_mode": tracker_mode,
        "ablation_control": condition["selector"],
    }


def run_model_phase(
    *,
    helper: ModuleType,
    tracker: Any,
    tracker_mode: str,
    intervals_by_sequence: Mapping[str, Sequence[Any]],
    discovery_sequences: frozenset[str],
    official_info: Mapping[str, Mapping[str, Any]],
    dataset_root: Path,
    branch_conditions: Sequence[Mapping[str, Any]],
    emit_baseline: bool,
    baseline_reference: Mapping[tuple[str, str, int], Mapping[str, Any]] | None,
    raw_temp_path: Path,
    raw_final_path: Path,
    timing_values: dict[tuple[str, str], dict[str, list[float]]],
) -> tuple[list[dict], list[dict], dict[str, Any]]:
    """Run one model continuously, forking every frozen interval from one state."""
    if raw_temp_path.exists():
        raise FileExistsError(f"Current-process raw partial exists: {raw_temp_path}")
    rows: list[dict[str, Any]] = []
    manifests: list[dict[str, Any]] = []
    raw_line_count = 0
    interval_count = sum(len(items) for items in intervals_by_sequence.values())
    interval_number = 0
    max_reference_float_diff = 0.0
    max_reference_score_diff = 0.0
    max_reference_confidence_diff = 0.0
    reference_integer_exact = True
    restore_branches = 0
    continuation_restores = 0

    def write_records(
        stream: Any,
        records: Sequence[Mapping[str, Any]],
        interval: Any,
        frame_index: int,
        condition: str,
        selector: str,
        branch_kind: str,
    ) -> None:
        nonlocal raw_line_count
        for record in records:
            enriched = dict(record)
            enriched.update(
                {
                    "pair_id": interval.pair_id,
                    "side": interval.side,
                    "sequence": interval.sequence,
                    "evaluator_frame_index": frame_index,
                    "bounded_refinement_condition": condition,
                    "diagnostic_selector": selector,
                    "branch_kind": branch_kind,
                    "selected_refinement_path": EXPECTED_SELECTED_PATH,
                    "frozen_interval_start": interval.start,
                    "frozen_interval_end": interval.end,
                }
            )
            stream.write(json.dumps(enriched, sort_keys=True, allow_nan=False) + "\n")
            raw_line_count += 1

    def run_branch(
        stream: Any,
        interval: Any,
        frame_paths: Sequence[Path],
        ground_truth: Any,
        condition: Mapping[str, Any],
        branch_kind: str,
        emit_rows: bool,
        collect_timing: bool,
    ) -> tuple[list[dict], tuple[int, int], dict[str, Any]]:
        nonlocal max_reference_float_diff, max_reference_score_diff
        nonlocal max_reference_confidence_diff, reference_integer_exact
        selector = str(condition["selector"])
        helper.configure_diagnostics(tracker, True, selector)
        branch_rows: list[dict[str, Any]] = []
        raw_start = raw_line_count + 1
        branch_float_max = 0.0
        branch_score_max = 0.0
        branch_confidence_max = 0.0
        branch_int_exact = True
        for frame_index in range(max(interval.start, 2), interval.end + 1):
            output, _, _ = tracker.track(helper.read_rgb(frame_paths[frame_index - 1]), {})
            diagnostic_records = tracker.consume_stage4a_diagnostic_records()
            mrm_records, tracker_record = validate_diagnostic_semantics(
                helper,
                diagnostic_records,
                selector,
                str(condition["kind"]),
                condition.get("template_path"),
                tracker_mode,
            )
            # T1's clean branch exists solely to re-establish parity with the
            # uninterrupted Criterion-A baseline.  It is neither a refinement
            # condition nor a timing condition, so do not publish it in the
            # bounded-refinement raw log.  T3 baseline and every actual control
            # have emit_rows/collect_timing true and remain fully logged.
            if emit_rows or collect_timing:
                write_records(
                    stream,
                    diagnostic_records,
                    interval,
                    frame_index,
                    str(condition["condition"]),
                    selector,
                    branch_kind,
                )
            float_box = np.asarray(output["target_bbox"], dtype=np.float64)
            int_box = float_box.astype(np.int64)
            gt_box = ground_truth[frame_index - 1]
            if baseline_reference is not None and branch_kind == "baseline":
                reference = baseline_reference[(interval.pair_id, interval.side, frame_index)]
                gt_diff = float(np.max(np.abs(gt_box - reference["gt_box"])))
                float_diff = float(np.max(np.abs(float_box - reference["float_box"])))
                integer_exact = bool(np.array_equal(int_box, reference["int_box"]))
                score_diff = abs(
                    float(tracker_record["score_map_max"]) - float(reference["score_map_max"])
                )
                confidence_diff = abs(
                    float(tracker_record["confidence_score"])
                    - float(reference["confidence_score"])
                )
                branch_float_max = max(branch_float_max, float_diff)
                branch_score_max = max(branch_score_max, score_diff)
                branch_confidence_max = max(branch_confidence_max, confidence_diff)
                branch_int_exact = branch_int_exact and integer_exact
                max_reference_float_diff = max(max_reference_float_diff, float_diff)
                max_reference_score_diff = max(max_reference_score_diff, score_diff)
                max_reference_confidence_diff = max(
                    max_reference_confidence_diff, confidence_diff
                )
                reference_integer_exact = reference_integer_exact and integer_exact
                if (
                    gt_diff > PARITY_TOLERANCE
                    or float_diff > PARITY_TOLERANCE
                    or score_diff > PARITY_TOLERANCE
                    or confidence_diff > PARITY_TOLERANCE
                    or not integer_exact
                ):
                    raise RuntimeError(
                        "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT: "
                        f"T1 refinement baseline parity failed at {interval.pair_id}/"
                        f"{interval.side}/{frame_index}: gt={gt_diff}, float={float_diff}, "
                        f"score={score_diff}, confidence={confidence_diff}, "
                        f"integer_exact={integer_exact}"
                    )
            if emit_rows:
                iou = helper.inclusive_iou(int_box, gt_box)
                branch_rows.append(
                    {
                        "pair_id": interval.pair_id,
                        "side": interval.side,
                        "sequence": interval.sequence,
                        "frame_index": frame_index,
                        "condition": condition["condition"],
                        "selected_refinement_path": EXPECTED_SELECTED_PATH,
                        "iou": iou,
                        "iou_float": helper.inclusive_iou(float_box, gt_box),
                        "failure": int(iou < 0.5),
                        "success_at_0_5": int(iou >= 0.5),
                        "center_error": helper.inclusive_center_error(int_box, gt_box),
                        "physical_skip": False,
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
                        "score_map_max": tracker_record["score_map_max"],
                        "confidence_score": tracker_record["confidence_score"],
                        "model_forward_ms": tracker_record[
                            "total_tracker_model_forward_ms"
                        ],
                        "initialization_frame": False,
                        "evaluator_first_frame_override": False,
                        "branch_frame_executed": True,
                        "tracker_mode": tracker_mode,
                        "ablation_control": selector,
                    }
                )
            if collect_timing:
                for record in mrm_records:
                    key = (str(condition["condition"]), str(record["mrm_id"]))
                    for metric in TIMING_METRICS:
                        timing_values[key][metric].append(float(record[metric]))
        parity = {
            "maximum_float_prediction_abs_diff": branch_float_max,
            "maximum_score_map_abs_diff": branch_score_max,
            "maximum_confidence_abs_diff": branch_confidence_max,
            "integer_prediction_exact": branch_int_exact,
        }
        return branch_rows, (raw_start, raw_line_count), parity

    with raw_temp_path.open("x", encoding="utf-8", newline="\n") as raw_stream:
        sequence_names = sorted(intervals_by_sequence)
        for sequence_index, sequence_name in enumerate(sequence_names, start=1):
            if sequence_name not in discovery_sequences:
                raise RefinementContractError(
                    f"Non-discovery sequence reached execution: {sequence_name}"
                )
            info = official_info[sequence_name]
            if int(info["startFrame"]) != 1:
                raise RefinementContractError(
                    f"Unsupported non-1 official start for {sequence_name}"
                )
            intervals = intervals_by_sequence[sequence_name]
            max_frame = max(interval.end for interval in intervals)
            if max_frame > int(info["endFrame"]):
                raise RefinementContractError(f"Frozen frame exceeds {sequence_name} end")
            effective_info = dict(info)
            effective_info.update(DISCOVERY_SOURCE_ALIASES.get(sequence_name, {}))
            image_dir = dataset_root / str(effective_info["path"])
            gt_path = dataset_root / str(effective_info["anno_path"])
            ground_truth = helper.read_boxes(gt_path)
            if len(ground_truth) < max_frame:
                raise RefinementContractError(
                    f"Discovery GT truncated for {sequence_name}: {len(ground_truth)} < {max_frame}"
                )
            frame_paths = [
                image_dir / f"{frame_index:0{int(info['nz'])}d}.{info['ext']}"
                for frame_index in range(1, max_frame + 1)
            ]
            missing = [str(path) for path in frame_paths if not path.is_file()]
            if missing:
                raise RefinementContractError(
                    f"Discovery source-integrity defect {sequence_name}: {missing[:3]}"
                )

            helper.configure_diagnostics(tracker, False, "none")
            tracker.initialize(
                helper.read_rgb(frame_paths[0]),
                {"init_bbox": ground_truth[0].tolist()},
            )
            current_frame = 1
            print(
                f"PROGRESS {tracker_mode} sequence {sequence_index}/{len(sequence_names)} "
                f"{sequence_name} intervals={len(intervals)} through={max_frame}",
                flush=True,
            )
            for interval in intervals:
                interval_number += 1
                while current_frame < interval.start - 1:
                    helper.configure_diagnostics(tracker, False, "none")
                    current_frame += 1
                    tracker.track(helper.read_rgb(frame_paths[current_frame - 1]), {})
                if current_frame != max(1, interval.start - 1):
                    raise RuntimeError(
                        f"Prefix position mismatch for {interval.pair_id}/{interval.side}: "
                        f"at {current_frame}, need {interval.start - 1}"
                    )

                initialization_box = np.asarray(tracker.state, dtype=np.float64)
                initialization_gt = ground_truth[0]
                if interval.start == 1 and baseline_reference is not None:
                    reference = baseline_reference[(interval.pair_id, interval.side, 1)]
                    gt_diff = float(np.max(np.abs(initialization_gt - reference["gt_box"])))
                    float_diff = float(
                        np.max(np.abs(initialization_box - reference["float_box"]))
                    )
                    int_exact = bool(
                        np.array_equal(
                            initialization_box.astype(np.int64), reference["int_box"]
                        )
                    )
                    max_reference_float_diff = max(max_reference_float_diff, float_diff)
                    reference_integer_exact = reference_integer_exact and int_exact
                    if gt_diff > PARITY_TOLERANCE or float_diff > PARITY_TOLERANCE or not int_exact:
                        raise RuntimeError(
                            "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT: "
                            f"T1 initialization parity failed at {interval.pair_id}/{interval.side}"
                        )

                start_snapshot = helper.capture_tracker_state(tracker)
                start_hash = helper.snapshot_sha256(start_snapshot)
                baseline_restore_hash = helper.restore_and_verify(
                    tracker,
                    start_snapshot,
                    start_hash,
                    f"{tracker_mode}/{interval.pair_id}/{interval.side}/baseline",
                )
                restore_branches += 1
                baseline_condition = (
                    T3_BASELINE if tracker_mode == "T3" else T1_BASELINE_PARITY
                )
                baseline_rows, baseline_raw_bounds, baseline_parity = run_branch(
                    raw_stream,
                    interval,
                    frame_paths,
                    ground_truth,
                    baseline_condition,
                    "baseline",
                    emit_baseline,
                    emit_baseline,
                )
                if interval.start == 1 and emit_baseline:
                    baseline_rows.insert(
                        0,
                        initialize_row(
                            baseline_condition,
                            interval,
                            initialization_box,
                            initialization_gt,
                            helper,
                            tracker_mode,
                        ),
                    )
                if emit_baseline:
                    if len(baseline_rows) != interval.end - interval.start + 1:
                        raise RuntimeError("T3 baseline interval coverage mismatch")
                    rows.extend(baseline_rows)
                baseline_end_snapshot = helper.capture_tracker_state(tracker)
                baseline_end_hash = helper.snapshot_sha256(baseline_end_snapshot)

                branch_manifest_payloads: list[tuple[Mapping[str, Any], str, tuple[int, int]]] = []
                if emit_baseline:
                    branch_manifest_payloads.append(
                        (baseline_condition, baseline_restore_hash, baseline_raw_bounds)
                    )
                for condition in branch_conditions:
                    restored_hash = helper.restore_and_verify(
                        tracker,
                        start_snapshot,
                        start_hash,
                        f"{tracker_mode}/{interval.pair_id}/{interval.side}/"
                        f"{condition['condition']}",
                    )
                    restore_branches += 1
                    condition_rows, raw_bounds, _ = run_branch(
                        raw_stream,
                        interval,
                        frame_paths,
                        ground_truth,
                        condition,
                        "control",
                        True,
                        True,
                    )
                    if interval.start == 1:
                        condition_rows.insert(
                            0,
                            initialize_row(
                                condition,
                                interval,
                                initialization_box,
                                initialization_gt,
                                helper,
                                tracker_mode,
                            ),
                        )
                    if len(condition_rows) != interval.end - interval.start + 1:
                        raise RuntimeError(
                            f"Refinement coverage mismatch for {condition['condition']}/"
                            f"{interval.pair_id}/{interval.side}"
                        )
                    rows.extend(condition_rows)
                    branch_manifest_payloads.append((condition, restored_hash, raw_bounds))

                continuation_hash = helper.restore_and_verify(
                    tracker,
                    baseline_end_snapshot,
                    baseline_end_hash,
                    f"{tracker_mode}/{interval.pair_id}/{interval.side}/continuation",
                )
                continuation_restores += 1
                for condition, restored_hash, raw_bounds in branch_manifest_payloads:
                    manifests.append(
                        {
                            "pair_id": interval.pair_id,
                            "side": interval.side,
                            "sequence": interval.sequence,
                            "interval_start": interval.start,
                            "interval_end": interval.end,
                            "condition": condition["condition"],
                            "selected_refinement_path": EXPECTED_SELECTED_PATH,
                            "physical_skip": False,
                            "status": "COMPLETE",
                            "tracker_mode": tracker_mode,
                            "ablation_control": condition["selector"],
                            "source_row_sha256_canonical_lf": interval.source_row_sha256,
                            "snapshot_frame": max(1, interval.start - 1),
                            "start_snapshot_sha256": start_hash,
                            "restored_start_snapshot_sha256": restored_hash,
                            "start_restore_exact": True,
                            "baseline_end_snapshot_sha256": baseline_end_hash,
                            "continuation_restored_snapshot_sha256": continuation_hash,
                            "continuation_restore_exact": True,
                            "interval_output_frames": interval.end - interval.start + 1,
                            "tracked_branch_frames": (
                                interval.end - max(interval.start, 2) + 1
                            ),
                            "official_initialization_frames_zero_contribution": int(
                                interval.start == 1
                            ),
                            "raw_jsonl_first_line": raw_bounds[0],
                            "raw_jsonl_last_line": raw_bounds[1],
                            "raw_jsonl_external_path": str(raw_final_path),
                        }
                    )
                current_frame = interval.end
                print(
                    f"PROGRESS {tracker_mode} interval {interval_number}/{interval_count} "
                    f"{interval.pair_id}/{interval.side} branches="
                    f"{len(branch_manifest_payloads)} complete",
                    flush=True,
                )

            helper.configure_diagnostics(tracker, False, "none")
            if current_frame != max_frame:
                raise RuntimeError(f"{tracker_mode} did not reach {sequence_name}/{max_frame}")
        raw_stream.flush()
        os.fsync(raw_stream.fileno())

    return rows, manifests, {
        "raw_jsonl_records": raw_line_count,
        "restore_branches": restore_branches,
        "continuation_restores": continuation_restores,
        "baseline_reference_parity": {
            "status": "PASS" if baseline_reference is not None else "NOT_APPLICABLE_T3",
            "tolerance": PARITY_TOLERANCE,
            "maximum_float_prediction_abs_diff": max_reference_float_diff,
            "maximum_score_map_abs_diff": max_reference_score_diff,
            "maximum_confidence_abs_diff": max_reference_confidence_diff,
            "integer_prediction_exact": reference_integer_exact,
        },
    }


def aggregate_timing_rows(
    timing_values: Mapping[tuple[str, str], Mapping[str, Sequence[float]]],
    conditions: Sequence[str],
    expected_tracked_frames: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for condition in conditions:
        for mrm_number in range(1, 7):
            mrm_id = f"MRM{mrm_number}"
            values_by_metric = timing_values[(condition, mrm_id)]
            counts = {len(values_by_metric.get(metric, ())) for metric in TIMING_METRICS}
            if counts != {expected_tracked_frames}:
                raise RuntimeError(
                    f"Timing coverage mismatch for {condition}/{mrm_id}: {sorted(counts)}"
                )
            row: dict[str, Any] = {
                "condition": condition,
                "mode": condition,
                "mrm_id": mrm_id,
                "mrm_code_index": mrm_number - 1,
                "frame_records": expected_tracked_frames,
                "physical_skip": False,
                "timing_role": "SYNCHRONIZED_DESKTOP_CHARACTERIZATION_ONLY_NOT_JETSON_EVIDENCE",
            }
            for metric in TIMING_METRICS:
                values = list(values_by_metric[metric])
                prefix = metric.removesuffix("_ms")
                row[f"{prefix}_mean_ms"] = statistics.fmean(values)
                row[f"{prefix}_median_ms"] = statistics.median(values)
                row[f"{prefix}_std_population_ms"] = statistics.pstdev(values)
                row[f"{prefix}_min_ms"] = min(values)
                row[f"{prefix}_max_ms"] = max(values)
            rows.append(row)
    return rows


def validate_frame_coverage(
    rows: Sequence[Mapping[str, Any]],
    expected_conditions: Sequence[str],
    baseline_keys: set[tuple[str, str, int]],
    label: str,
) -> None:
    observed = {
        (
            str(row["condition"]),
            str(row["pair_id"]),
            str(row["side"]),
            int(row["frame_index"]),
        )
        for row in rows
    }
    expected = {
        (condition, pair_id, side, frame)
        for condition in expected_conditions
        for pair_id, side, frame in baseline_keys
    }
    if observed != expected or len(rows) != len(expected):
        raise RuntimeError(
            f"{label} locked coverage mismatch: rows={len(rows)}, expected={len(expected)}, "
            f"unique={len(observed)}"
        )
    if any(bool(row["physical_skip"]) for row in rows):
        raise RuntimeError(f"{label} reported physical_skip=true")


def main() -> None:
    args = parse_args()
    path_names = (
        "source_root", "dataset_root", "slice_csv", "t1_config",
        "t1_checkpoint", "t3_config", "t3_checkpoint", "baseline_csv",
        "analysis_summary", "criterion_b_results", "external_root",
        "artifact_root",
    )
    for name in path_names:
        setattr(args, name, getattr(args, name).resolve())
    for name in path_names:
        if not getattr(args, name).exists():
            raise FileNotFoundError(getattr(args, name))
    if not args.source_root.is_dir() or not args.dataset_root.is_dir():
        raise NotADirectoryError("Source and dataset roots must be directories")
    if not args.external_root.is_dir() or not args.artifact_root.is_dir():
        raise NotADirectoryError("External and artifact roots must already exist")
    if args.seed != SEED:
        raise RefinementContractError(f"Locked refinement seed must be {SEED}")

    repo_outputs = {name: args.artifact_root / name for name in REPO_OUTPUT_NAMES}
    external_phase_root = args.external_root / "bounded_refinement"
    t1_raw_path = external_phase_root / "t1_retriever_mlp_raw_mrm.jsonl"
    t3_raw_path = external_phase_root / "t3_baseline_template_controls_raw_mrm.jsonl"
    preexisting = [
        path for path in [*repo_outputs.values(), t1_raw_path, t3_raw_path] if path.exists()
    ]
    if preexisting:
        raise FileExistsError(
            f"Bounded-refinement output already exists; refusing reuse: {preexisting}"
        )

    helper_path = Path(__file__).with_name("2026-08-26_stage4B_execute_criterionB.py")
    helper = load_criterion_b_helpers(helper_path)
    global np
    import numpy as np
    global torch
    import torch
    helper.torch = torch

    discovery, intervals_by_sequence, slice_hashes = helper.parse_and_validate_slice(
        args.slice_csv
    )
    if slice_hashes["normalized_lf_sha256"] != FROZEN_SLICE_SHA256_NORMALIZED_LF:
        raise RefinementContractError("Frozen slice hash differs from locked refinement input")
    baseline, baseline_sha = helper.load_baseline_frames(args.baseline_csv, discovery)
    analysis, criterion_b_execution = validate_refinement_gate(
        args.analysis_summary,
        args.criterion_b_results,
        args.artifact_root,
        args.slice_csv,
        slice_hashes["normalized_lf_sha256"],
        args.baseline_csv,
        baseline_sha,
    )

    source_sha = helper.git_output(args.source_root, "rev-parse", "HEAD")
    if source_sha != PINNED_SOURCE_SHA:
        raise RefinementContractError(f"Wrong SpikeTrack source SHA: {source_sha}")
    status_lines = [
        line
        for line in helper.git_output(args.source_root, "status", "--porcelain").splitlines()
        if line
    ]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    if changed_paths != sorted(PATCHED_PATHS):
        raise RefinementContractError(
            f"Patched SpikeTrack worktree has unexpected paths: {changed_paths}"
        )
    observed_patched_hashes = {
        path: sha256_file(args.source_root / path) for path in PATCHED_PATHS
    }
    if observed_patched_hashes != PATCHED_FILE_SHA256:
        raise RefinementContractError("Accepted diagnostic patched-file SHA-256 mismatch")
    expected_file_hashes = {
        args.t1_config: T1_CONFIG_SHA256,
        args.t1_checkpoint: T1_CHECKPOINT_SHA256,
        args.t3_config: T3_CONFIG_SHA256,
        args.t3_checkpoint: T3_CHECKPOINT_SHA256,
    }
    for path, expected_hash in expected_file_hashes.items():
        observed_hash = sha256_file(path)
        if observed_hash != expected_hash:
            raise RefinementContractError(
                f"Pinned input hash mismatch for {path}: {observed_hash}"
            )

    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    os.chdir(args.source_root)
    sys.path.insert(0, str(args.source_root))
    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.evaluation.otbdataset import OTBDataset
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    official_info = {
        item["name"]: item for item in OTBDataset._get_sequence_info_list(None)
    }
    discovery_sequences = frozenset(intervals_by_sequence)
    missing_metadata = sorted(discovery_sequences - set(official_info))
    if missing_metadata:
        raise RefinementContractError(
            f"Discovery sequences absent from pinned OTB metadata: {missing_metadata}"
        )

    external_phase_root.mkdir(parents=True, exist_ok=True)
    t1_raw_temp = helper.atomic_temp_path(t1_raw_path)
    t3_raw_temp = helper.atomic_temp_path(t3_raw_path)
    timing_values: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    total_started = time.perf_counter()

    configure_determinism(torch, np, args.seed)
    t1_tracker = make_tracker(
        cfg,
        update_config_from_file,
        SpikeTrack,
        args.t1_config,
        args.t1_checkpoint,
        1,
    )
    t1_rows, t1_manifests, t1_execution = run_model_phase(
        helper=helper,
        tracker=t1_tracker,
        tracker_mode="T1",
        intervals_by_sequence=intervals_by_sequence,
        discovery_sequences=discovery_sequences,
        official_info=official_info,
        dataset_root=args.dataset_root,
        branch_conditions=T1_CONDITIONS,
        emit_baseline=False,
        baseline_reference=baseline,
        raw_temp_path=t1_raw_temp,
        raw_final_path=t1_raw_path,
        timing_values=timing_values,
    )
    del t1_tracker
    gc.collect()
    torch.cuda.empty_cache()

    configure_determinism(torch, np, args.seed)
    t3_tracker = make_tracker(
        cfg,
        update_config_from_file,
        SpikeTrack,
        args.t3_config,
        args.t3_checkpoint,
        3,
    )
    controls_valid, technical_validity, technical_blocker = t3_control_preflight(
        helper, t3_tracker
    )
    selected_t3_conditions = T3_CONDITIONS if controls_valid else ()
    t3_rows, t3_manifests, t3_execution = run_model_phase(
        helper=helper,
        tracker=t3_tracker,
        tracker_mode="T3",
        intervals_by_sequence=intervals_by_sequence,
        discovery_sequences=discovery_sequences,
        official_info=official_info,
        dataset_root=args.dataset_root,
        branch_conditions=selected_t3_conditions,
        emit_baseline=True,
        baseline_reference=None,
        raw_temp_path=t3_raw_temp,
        raw_final_path=t3_raw_path,
        timing_values=timing_values,
    )
    del t3_tracker
    gc.collect()
    torch.cuda.empty_cache()

    baseline_keys = set(baseline)
    t1_condition_names = tuple(item["condition"] for item in T1_CONDITIONS)
    t3_condition_names = (T3_BASELINE["condition"],) + tuple(
        item["condition"] for item in selected_t3_conditions
    )
    validate_frame_coverage(t1_rows, t1_condition_names, baseline_keys, "T1 refinement")
    validate_frame_coverage(t3_rows, t3_condition_names, baseline_keys, "T3 refinement")
    expected_manifest_conditions = set(t1_condition_names + t3_condition_names)
    observed_manifest_keys = {
        (row["condition"], row["pair_id"], row["side"]) for row in t1_manifests + t3_manifests
    }
    expected_manifest_keys = {
        (condition, pair_id, side)
        for condition in expected_manifest_conditions
        for pair_id in EXPECTED_DISCOVERY_IDS
        for side in ("primary", "control")
    }
    if (
        observed_manifest_keys != expected_manifest_keys
        or len(t1_manifests) + len(t3_manifests) != len(expected_manifest_keys)
    ):
        raise RuntimeError("Bounded-refinement manifest locked coverage mismatch")

    initialization_rows = sum(1 for row in baseline.values() if row["initialization_frame"])
    expected_tracked_frames = len(baseline) - initialization_rows
    expected_t1_raw_records = expected_tracked_frames * len(T1_CONDITIONS) * 7
    expected_t3_raw_records = (
        expected_tracked_frames * (1 + len(selected_t3_conditions)) * 7
    )
    if t1_execution["raw_jsonl_records"] != expected_t1_raw_records:
        raise RuntimeError(
            "T1 refinement raw-record coverage mismatch: "
            f"{t1_execution['raw_jsonl_records']} != {expected_t1_raw_records}"
        )
    if t3_execution["raw_jsonl_records"] != expected_t3_raw_records:
        raise RuntimeError(
            "T3 refinement raw-record coverage mismatch: "
            f"{t3_execution['raw_jsonl_records']} != {expected_t3_raw_records}"
        )
    all_condition_names = tuple(
        sorted(expected_manifest_conditions, key=CONDITION_ORDER.__getitem__)
    )
    timing_rows = aggregate_timing_rows(
        timing_values, all_condition_names, expected_tracked_frames
    )
    t1_rows.sort(
        key=lambda row: (
            CONDITION_ORDER[row["condition"]], row["pair_id"], row["side"],
            int(row["frame_index"]),
        )
    )
    t3_rows.sort(
        key=lambda row: (
            CONDITION_ORDER[row["condition"]], row["pair_id"], row["side"],
            int(row["frame_index"]),
        )
    )
    manifests = t1_manifests + t3_manifests
    manifests.sort(
        key=lambda row: (
            CONDITION_ORDER[row["condition"]], row["pair_id"], row["side"]
        )
    )
    timing_rows.sort(
        key=lambda row: (CONDITION_ORDER[row["condition"]], row["mrm_code_index"])
    )

    timing_fields = list(timing_rows[0])
    prepared: dict[Path, Path] = {}
    prepared[repo_outputs["retriever_mlp_per_frame_metrics.csv"]] = helper.prepare_csv(
        repo_outputs["retriever_mlp_per_frame_metrics.csv"], list(FRAME_FIELDS), t1_rows
    )
    prepared[repo_outputs["t3_per_frame_metrics.csv"]] = helper.prepare_csv(
        repo_outputs["t3_per_frame_metrics.csv"], list(FRAME_FIELDS), t3_rows
    )
    prepared[repo_outputs["bounded_refinement_execution_manifest.csv"]] = (
        helper.prepare_csv(
            repo_outputs["bounded_refinement_execution_manifest.csv"],
            list(MANIFEST_FIELDS),
            manifests,
        )
    )
    prepared[repo_outputs["bounded_refinement_timing_characterization.csv"]] = (
        helper.prepare_csv(
            repo_outputs["bounded_refinement_timing_characterization.csv"],
            timing_fields,
            timing_rows,
        )
    )
    output_hashes = {
        final.name: sha256_file(temp) for final, temp in prepared.items()
    }
    if set(output_hashes) != set(OUTPUT_HASH_NAMES):
        raise RuntimeError("Bounded-refinement output-hash key set mismatch")

    t1_raw_sha = sha256_file(t1_raw_temp)
    t3_raw_sha = sha256_file(t3_raw_temp)
    components: dict[str, dict[str, Any]] = {
        "retriever_only_bypass": {
            "status": "PASS",
            "selected_refinement_path": EXPECTED_SELECTED_PATH,
            "physical_skip": False,
            "discovery_pairs_executed": 12,
            "discovery_intervals_executed": 24,
            "diagnostic_selector": "mrm1_retriever",
        },
        "mlp_only_bypass": {
            "status": "PASS",
            "selected_refinement_path": EXPECTED_SELECTED_PATH,
            "physical_skip": False,
            "discovery_pairs_executed": 12,
            "discovery_intervals_executed": 24,
            "diagnostic_selector": "mrm1_mlp",
        },
        "t3_baseline": {
            "status": "PASS",
            "selected_refinement_path": EXPECTED_SELECTED_PATH,
            "physical_skip": False,
            "discovery_pairs_executed": 12,
            "discovery_intervals_executed": 24,
            "diagnostic_selector": "none",
        },
        "t3_selected_path_controls": {
            "status": "PASS" if controls_valid else "NOT_TECHNICALLY_VALID",
            "selected_refinement_path": EXPECTED_SELECTED_PATH,
            "physical_skip": False,
            "discovery_pairs_executed": 12 if controls_valid else 0,
            "discovery_intervals_executed": 24 if controls_valid else 0,
            "controls_executed": 3 if controls_valid else 0,
            "technical_blocker": "" if controls_valid else technical_blocker,
            "machine_verification": technical_validity,
        },
    }
    elapsed = time.perf_counter() - total_started
    summary = {
        "schema_version": "stage4b-bounded-refinement-v1",
        "status": "BOUNDED_REFINEMENT_COMPLETE",
        "refinement_executed": True,
        "selected_refinement_path": EXPECTED_SELECTED_PATH,
        "discovery_pairs_executed": 12,
        "discovery_intervals_executed": 24,
        "holdout_pairs_executed": 0,
        "holdout_outcomes_read": 0,
        "physical_skip": False,
        "criterion_b_gate": {
            "pass": True,
            "selected_refinement_path": EXPECTED_SELECTED_PATH,
            "analysis_summary_path": str(args.analysis_summary),
            "analysis_summary_sha256": sha256_file(args.analysis_summary),
            "criterion_b_results_path": str(args.criterion_b_results),
            "criterion_b_results_sha256": sha256_file(args.criterion_b_results),
            "criterion_b_execution_summary_sha256": sha256_file(
                args.artifact_root / "criterionB_execution_summary.json"
            ),
        },
        "t1": {
            "config": str(args.t1_config),
            "config_sha256": T1_CONFIG_SHA256,
            "checkpoint": str(args.t1_checkpoint),
            "checkpoint_sha256": T1_CHECKPOINT_SHA256,
            "selected_control_selectors": [item["selector"] for item in T1_CONDITIONS],
        },
        "t3": {
            "config": str(args.t3_config),
            "config_sha256": T3_CONFIG_SHA256,
            "checkpoint": str(args.t3_checkpoint),
            "checkpoint_sha256": T3_CHECKPOINT_SHA256,
            "selected_control_names": list(T3_CONTROL_NAMES),
            "selected_control_selectors": [item["selector"] for item in T3_CONDITIONS],
            "technical_validity": technical_validity,
        },
        "components": components,
        "state_snapshot": {
            "status": "PASS",
            "hash_algorithm": (
                "SHA-256 over stage4b-tracker-state-snapshot-v1 canonical type stream"
            ),
            "captured_state": SNAPSHOT_CAPTURE_DESCRIPTION,
            "t1_restore_branches": t1_execution["restore_branches"],
            "t1_continuation_restores": t1_execution["continuation_restores"],
            "t3_restore_branches": t3_execution["restore_branches"],
            "t3_continuation_restores": t3_execution["continuation_restores"],
        },
        "t1_baseline_reference_parity": t1_execution["baseline_reference_parity"],
        "row_counts": {
            "retriever_mlp_per_frame_metrics": len(t1_rows),
            "t3_per_frame_metrics": len(t3_rows),
            "bounded_refinement_execution_manifest": len(manifests),
            "bounded_refinement_timing_characterization": len(timing_rows),
        },
        "input_hashes": {
            "source_sha": source_sha,
            "patch_sha256_canonical_lf": PATCH_SHA256_CANONICAL_LF,
            "patched_file_sha256": observed_patched_hashes,
            "frozen_slice_sha256_normalized_lf": slice_hashes[
                "normalized_lf_sha256"
            ],
            "baseline_csv_sha256": baseline_sha,
            "analysis_summary_sha256": sha256_file(args.analysis_summary),
            "criterion_b_results_sha256": sha256_file(args.criterion_b_results),
            "criterion_b_mode_csv_sha256": sha256_file(
                args.artifact_root / "mode_per_frame_metrics.csv"
            ),
        },
        "determinism": {
            "seed": args.seed,
            "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
            "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "gpu": torch.cuda.get_device_name(torch.cuda.current_device()),
        },
        "accepted_nonmutating_discovery_aliases": DISCOVERY_SOURCE_ALIASES,
        "external_raw_logs": [
            {
                "phase": "T1_RETRIEVER_MLP",
                "path": str(t1_raw_path),
                "sha256": t1_raw_sha,
                "records": t1_execution["raw_jsonl_records"],
            },
            {
                "phase": "T3_BASELINE_TEMPLATE_CONTROLS",
                "path": str(t3_raw_path),
                "sha256": t3_raw_sha,
                "records": t3_execution["raw_jsonl_records"],
            },
        ],
        "output_hashes": output_hashes,
        "elapsed_seconds": elapsed,
        "next_action": "FINALIZE_STAGE4B_REPORT_FOR_MANAGER_REVIEW",
        "stage4b_conclusion": None,
        "non_claims": {
            "diag_pass_fail_assigned": False,
            "stage4c_unlocked": False,
            "physical_non_execution_claimed": False,
            "jetson_latency_claimed": False,
            "primary_shortlist": None,
            "main_baseline": None,
            "proposed_architecture": None,
        },
    }
    prepared[repo_outputs["bounded_refinement_execution_summary.json"]] = (
        helper.prepare_json(
            repo_outputs["bounded_refinement_execution_summary.json"], summary
        )
    )

    os.replace(t1_raw_temp, t1_raw_path)
    os.replace(t3_raw_temp, t3_raw_path)
    for name in REPO_OUTPUT_NAMES:
        final_path = repo_outputs[name]
        os.replace(prepared[final_path], final_path)
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False), flush=True)


if __name__ == "__main__":
    main()
