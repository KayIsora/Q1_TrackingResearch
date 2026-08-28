#!/usr/bin/env python3
"""Finalize the bounded Stage-4B discovery report and artifact manifest.

This is a reporting-only lane.  It never launches SpikeTrack, never opens a
held-out outcome, and never changes the frozen slice.  It consumes the bounded
discovery artifacts emitted by the execution and analysis lanes, verifies
their gates, copies the small analysis tables into the machine-artifact root,
and writes the required twenty-section report plus a manifest of repository
and externally retained evidence.

The conclusion logic is intentionally conservative.  In particular, a
Criterion-B pass does not become ``STAGE4B_AB_PASS_READY_FOR_MANAGER_REVIEW``
until explicit Retriever-only, MLP-only, and T3 bounded-refinement evidence is
present and complete.  Missing refinement evidence resolves to the only
allowed incomplete Stage-4B state; it is never silently treated as readiness.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import re
import statistics
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence


DATE_PREFIX = "2026-08-26_stage4B_"
EXPECTED_SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
EXPECTED_T1_CONFIG_SHA256 = (
    "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
)
EXPECTED_CHECKPOINT_SHA256 = (
    "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
)
EXPECTED_T3_CHECKPOINT_SHA256 = (
    "ccf04aa90521b21a78b12f4b978c03d8a69b5f6de3ee3498a3594e13e98aa491"
)
EXPECTED_PATCH_SHA256_CANONICAL_LF = (
    "d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a"
)
EXPECTED_PATCH_APPLY_RESULT = "PASS_CANONICAL_GIT_BLOB_STRICT_WHITESPACE"
EXPECTED_PATCHED_FILE_SHA256 = {
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
EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256 = (
    "bc52bd7ec6277a76e6da69346a84a8f9d801e2fee9cd92634a60cf9f119ea11a"
)
EXPECTED_EXTERNAL_ROOT = Path(
    r"F:\Q1_TrackingResearch_Data\Stage4B_SpikeTrack_Discovery_2026-08-26"
)
EXPECTED_DATASET_ROOT = Path(
    r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015"
)
EXPECTED_E2_SOURCE_MANIFEST_SHA256 = (
    "35638156ef0f069978ee6e13daa9095be528bde1244b085e230170726a21956d"
)
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{index:02d}" for index in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{index:02d}" for index in range(1, 9))
EXPECTED_DISCOVERY_SOURCE_ALIASES = {
    "Jogging_1": {
        "path": "Jogging/img",
        "anno_path": "Jogging/groundtruth_rect.1.txt",
        "evidence": "2026-08-25_stage4A_E2_otb_source_manifest.csv row E2-OTB-062",
    }
}
LOCKED_MODES = (
    "mrm1", "mrm2", "mrm3", "mrm4", "mrm5", "mrm6",
    "early", "middle", "late",
)
MODE_SELECTION_META = {
    "mrm1": (1, 1, 1),
    "mrm2": (1, 2, 2),
    "mrm3": (1, 3, 3),
    "mrm4": (1, 4, 4),
    "mrm5": (1, 5, 5),
    "mrm6": (1, 6, 6),
    "early": (2, 1, 7),
    "middle": (2, 3, 8),
    "late": (2, 5, 9),
}
MODE_MEMBERS_TEXT = {
    "mrm1": "1", "mrm2": "2", "mrm3": "3", "mrm4": "4", "mrm5": "5",
    "mrm6": "6", "early": "1;2", "middle": "3;4", "late": "5;6",
}
LOCKED_SENSITIVITY_GROUPS = (
    ("final_ambiguity_level", "AMBIGUITY_LEVEL_2"),
    ("final_ambiguity_level", "AMBIGUITY_LEVEL_1"),
    ("control_sequence_relation", "SAME_SEQUENCE_CONTROL"),
    ("control_sequence_relation", "CROSS_SEQUENCE_CONTROL"),
    ("sensitivity_stratum", "STRONG_SAME_SEQUENCE"),
    ("sensitivity_stratum", "CROSS_SCENE_ACTIVITY"),
    ("sensitivity_stratum", "COLOR_DIFFERENCE"),
    ("sensitivity_stratum", "APPEARANCE_DIFFERENCE"),
    ("sensitivity_stratum", "LOW_LIGHT_MULTI_TRAFFIC"),
    ("sensitivity_stratum", "CONTROL_PARTIAL_OCCLUSION"),
    ("sensitivity_stratum", "MULTI_FACE_BACKGROUND"),
    ("sensitivity_stratum", "COSTUME_DIFFERENCE_CLASS_RESOLVED_PERSON"),
    ("broad_superclass", "PERSON"),
    ("broad_superclass", "VEHICLE"),
    ("broad_superclass", "FACE_HEAD"),
    ("broad_superclass", "OBJECT_OTHER"),
)
ALLOWED_CONCLUSIONS = {
    "STAGE4B_CRITERION_A_FAIL",
    "STAGE4B_CRITERION_B_FAIL",
    "STAGE4B_AB_PASS_READY_FOR_MANAGER_REVIEW",
    "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT",
    "STAGE4B_INVALID_HOLDOUT_EXPOSURE",
}
INCOMPLETE = "STAGE4B_INCOMPLETE_ENVIRONMENT_OR_STATE_SNAPSHOT"
INVALID_HOLDOUT = "STAGE4B_INVALID_HOLDOUT_EXPOSURE"
PARITY_TOLERANCE = 1e-6

ANALYSIS_COPY_MAP = {
    f"{DATE_PREFIX}analysis_summary.json": "analysis_summary.json",
    f"{DATE_PREFIX}criterionA_results.csv": "criterionA_results.csv",
    f"{DATE_PREFIX}criterionB_results.csv": "criterionB_results.csv",
    f"{DATE_PREFIX}sensitivity_results.csv": "sensitivity_results.csv",
    f"{DATE_PREFIX}pair_level_A.csv": "pair_level_A.csv",
    f"{DATE_PREFIX}pair_level_B.csv": "pair_level_B.csv",
    f"{DATE_PREFIX}bootstrap_results.csv": "bootstrap_results.csv",
    f"{DATE_PREFIX}holm_adjusted_tests.csv": "holm_adjusted_tests.csv",
}

REFINEMENT_SUMMARY_NAME = "bounded_refinement_execution_summary.json"
REFINEMENT_SCHEMA_VERSION = "stage4b-bounded-refinement-v1"
REFINEMENT_COMPONENT_KEYS = {
    "retriever_only_bypass",
    "mlp_only_bypass",
    "t3_baseline",
    "t3_selected_path_controls",
}
T3_REFINEMENT_CONTROL_NAMES = (
    "t3_template_path_1_zero_contribution",
    "t3_template_path_2_zero_contribution",
    "t3_template_path_3_zero_contribution",
)
REFINEMENT_OUTPUT_HASH_KEYS = {
    "retriever_mlp_per_frame_metrics.csv",
    "t3_per_frame_metrics.csv",
    "bounded_refinement_execution_manifest.csv",
    "bounded_refinement_timing_characterization.csv",
}

HOLDOUT_SEAL_FIELDS = (
    "pair_id", "primary_sequence", "primary_start", "primary_end",
    "control_sequence", "control_start", "control_end",
    "row_sha256_canonical_lf", "frozen_slice_sha256_canonical_lf", "status",
)
DISCOVERY_MANIFEST_FIELDS = (
    "pair_id", "side", "sequence", "start", "end", "event_id",
    "source_row_sha256_canonical_lf", "status",
)
BASELINE_SEQUENCE_FIELDS = (
    "sequence", "official_start_frame", "executed_through_frame",
    "initialized_once_from_official_start",
    "frames_processed_including_initialization", "prediction_path_external",
    "prediction_sha256", "elapsed_seconds_excluding_initialization", "status",
)
BASELINE_METRIC_FIELDS = (
    "pair_id", "side", "sequence", "frame_index", "pred_x_float", "pred_y_float",
    "pred_w_float", "pred_h_float", "pred_x_int", "pred_y_int", "pred_w_int",
    "pred_h_int", "gt_x", "gt_y", "gt_w", "gt_h", "iou", "iou_float",
    "failure", "success_at_0_5", "center_error", "score_map_max",
    "confidence_score", "model_forward_ms", "initialization_frame",
    "evaluator_first_frame_override", "tracker_mode", "ablation_control",
    "physical_skip",
)
MODE_METRIC_FIELDS = (
    "pair_id", "side", "sequence", "frame_index", "mode", "iou",
    "physical_skip", "baseline_iou", "contribution", "pred_x_float",
    "pred_y_float", "pred_w_float", "pred_h_float", "pred_x_int", "pred_y_int",
    "pred_w_int", "pred_h_int", "gt_x", "gt_y", "gt_w", "gt_h", "iou_float",
    "failure", "success_at_0_5", "center_error", "score_map_max",
    "confidence_score", "model_forward_ms", "initialization_frame",
    "evaluator_first_frame_override", "branch_frame_executed", "tracker_mode",
    "ablation_control",
)
STATE_PARITY_FIELDS = (
    "pair_id", "side", "sequence", "interval_start", "interval_end",
    "branch_kind", "mode", "snapshot_frame", "start_snapshot_sha256",
    "restored_start_snapshot_sha256", "start_restore_exact",
    "baseline_end_snapshot_sha256", "continuation_restored_snapshot_sha256",
    "continuation_restore_exact", "maximum_float_prediction_abs_diff",
    "maximum_score_map_abs_diff", "maximum_confidence_abs_diff",
    "integer_prediction_exact", "tolerance",
    "official_initialization_zero_contribution", "captured_state", "status",
)
MODE_EXECUTION_FIELDS = (
    "pair_id", "side", "sequence", "interval_start", "interval_end", "mode",
    "test_order", "mrm_members", "physical_skip",
    "source_row_sha256_canonical_lf", "start_snapshot_sha256",
    "restored_start_snapshot_sha256", "start_restore_exact",
    "interval_output_frames", "tracked_branch_frames",
    "official_initialization_frames_zero_contribution", "raw_jsonl_first_line",
    "raw_jsonl_last_line", "raw_jsonl_external_path", "status",
)
CRITERION_B_OUTPUT_HASH_KEYS = {
    "state_snapshot_parity.csv",
    "mode_per_frame_metrics.csv",
    "mode_execution_manifest.csv",
    "mode_module_timing_characterization.csv",
}
ANALYSIS_OUTPUT_BASENAMES = {
    "criterion_a": f"{DATE_PREFIX}criterionA_results.csv",
    "criterion_b": f"{DATE_PREFIX}criterionB_results.csv",
    "sensitivity": f"{DATE_PREFIX}sensitivity_results.csv",
    "pair_a": f"{DATE_PREFIX}pair_level_A.csv",
    "pair_b": f"{DATE_PREFIX}pair_level_B.csv",
    "bootstrap": f"{DATE_PREFIX}bootstrap_results.csv",
    "holm": f"{DATE_PREFIX}holm_adjusted_tests.csv",
}
PAIR_A_FIELDS = (
    "pair_id", "primary_sequence", "control_sequence", "primary_start",
    "primary_end", "control_start", "control_end", "primary_frame_count",
    "control_frame_count", "broad_superclass", "final_ambiguity_level",
    "sensitivity_stratum", "control_relation", "primary_mean_iou",
    "control_mean_iou", "iou_weakness", "primary_failure_rate",
    "control_failure_rate", "failure_weakness", "primary_mean_center_error",
    "control_mean_center_error", "center_error_primary_minus_control",
)
PAIR_B_FIELDS = (
    "test_order", "mode", "mrm_members", "pair_id", "primary_sequence",
    "control_sequence", "broad_superclass", "final_ambiguity_level",
    "sensitivity_stratum", "contribution_distractor", "contribution_control",
    "interaction",
)
SENSITIVITY_FIELDS = (
    "analysis_family", "sensitivity_dimension", "sensitivity_group",
    "selection_rule", "metric_or_mode", "effect_definition", "n_pairs",
    "pair_ids", "estimate", "n_primary_clusters", "primary_ci_low",
    "primary_ci_high", "primary_p_two_sided_sign_tail",
    "n_connected_components", "component_ci_low", "component_ci_high",
    "component_p_two_sided_sign_tail", "decision_role",
)
CRITERION_A_FIELDS = (
    "metric", "definition", "estimate", "threshold", "threshold_relation",
    "n_pairs", "primary_cluster_unit", "n_primary_clusters", "primary_ci_low",
    "primary_ci_high", "primary_p_two_sided_sign_tail",
    "primary_ci_excludes_zero", "component_cluster_unit",
    "n_connected_components", "component_ci_low", "component_ci_high",
    "component_p_two_sided_sign_tail", "component_ci_excludes_zero",
    "metric_pass", "criterion_a_pass", "decision_role",
)
CRITERION_B_FIELDS = (
    "test_order", "mode", "mrm_members", "group_size",
    "mean_contribution_distractor", "mean_contribution_control",
    "mean_interaction", "absolute_interaction_threshold", "n_pairs",
    "n_primary_clusters", "primary_ci_low", "primary_ci_high",
    "primary_p_unadjusted", "primary_p_holm_adjusted", "holm_reject_0_05",
    "primary_ci_excludes_zero", "n_connected_components", "component_ci_low",
    "component_ci_high", "component_p_two_sided_sign_tail",
    "component_ci_excludes_zero", "direction", "direction_stable",
    "scientifically_interpretable", "test_pass", "criterion_b_pass",
    "selected_refinement_path", "physical_skip", "decision_role",
)
BOOTSTRAP_FIELDS = (
    "analysis_family", "test_id", "bootstrap_scheme", "cluster_unit",
    "n_clusters", "n_pairs", "estimate", "ci_low", "ci_high",
    "p_two_sided_sign_tail", "resamples", "seed", "decision_role",
)
HOLM_FIELDS = (
    "test_order", "mode", "p_unadjusted", "holm_rank", "holm_multiplier",
    "p_holm_adjusted", "reject_familywise_0_05", "family_size",
    "familywise_alpha", "decision_role",
)

OUTCOME_BEARING_BASENAMES = {
    "baseline_per_frame_metrics.csv",
    "mode_per_frame_metrics.csv",
    "module_timing_characterization.csv",
    "mode_module_timing_characterization.csv",
    "criterionA_results.csv",
    "criterionB_results.csv",
    "sensitivity_results.csv",
    "pair_level_A.csv",
    "pair_level_B.csv",
    "bootstrap_results.csv",
    "holm_adjusted_tests.csv",
    f"{DATE_PREFIX}criterionA_results.csv",
    f"{DATE_PREFIX}criterionB_results.csv",
    f"{DATE_PREFIX}sensitivity_results.csv",
    f"{DATE_PREFIX}pair_level_A.csv",
    f"{DATE_PREFIX}pair_level_B.csv",
    f"{DATE_PREFIX}bootstrap_results.csv",
    f"{DATE_PREFIX}holm_adjusted_tests.csv",
}

SAFE_INVALID_MANIFEST_BASENAMES = {
    "provenance_environment.json",
    "no_ablation_parity.json",
    "holdout_seal.csv",
    "discovery_execution_manifest.csv",
    "baseline_sequence_execution.csv",
    "criterionA_execution_summary.json",
    "criterionB_execution_summary.json",
    f"{DATE_PREFIX}command_log.txt",
    f"{DATE_PREFIX}discovery_execution_report.md",
    "external_evidence_registry.csv",
}

REGISTERED_CODEX_ROOT_BASENAMES = {
    f"{DATE_PREFIX}analysis_summary.json",
    f"{DATE_PREFIX}bootstrap_results.csv",
    f"{DATE_PREFIX}command_log.txt",
    f"{DATE_PREFIX}criterionA_results.csv",
    f"{DATE_PREFIX}criterionB_results.csv",
    f"{DATE_PREFIX}discovery_execution_report.md",
    f"{DATE_PREFIX}holm_adjusted_tests.csv",
    f"{DATE_PREFIX}pair_level_A.csv",
    f"{DATE_PREFIX}pair_level_B.csv",
    f"{DATE_PREFIX}sensitivity_results.csv",
}
REGISTERED_ARTIFACT_BASENAMES = {
    "analysis_summary.json",
    "artifact_manifest.csv",
    "baseline_per_frame_metrics.csv",
    "baseline_sequence_execution.csv",
    "bootstrap_results.csv",
    "bounded_refinement_execution_manifest.csv",
    "bounded_refinement_execution_summary.json",
    "bounded_refinement_timing_characterization.csv",
    "criterionA_execution_summary.json",
    "criterionA_results.csv",
    "criterionB_execution_summary.json",
    "criterionB_results.csv",
    "discovery_execution_manifest.csv",
    "distractor_margin_evidence.csv",
    "external_evidence_registry.csv",
    "holdout_seal.csv",
    "holm_adjusted_tests.csv",
    "mode_execution_manifest.csv",
    "mode_module_timing_characterization.csv",
    "mode_per_frame_metrics.csv",
    "module_timing_characterization.csv",
    "no_ablation_parity.json",
    "pair_level_A.csv",
    "pair_level_B.csv",
    "provenance_environment.json",
    "retriever_mlp_per_frame_metrics.csv",
    "sensitivity_results.csv",
    "state_snapshot_parity.csv",
    "t3_per_frame_metrics.csv",
}

BOUNDED_REPOSITORY_SUFFIXES = {".csv", ".json", ".md", ".txt", ".py", ".patch"}
PROHIBITED_REPOSITORY_SUFFIXES = {
    ".bin", ".ckpt", ".jpg", ".jpeg", ".mp4", ".npy", ".npz", ".pth",
    ".pt", ".tar", ".tif", ".tiff", ".zip",
}
MAX_BOUNDED_REPOSITORY_BYTES = 10 * 1024 * 1024
B_EXECUTION_BASENAMES = {
    "state_snapshot_parity.csv",
    "mode_per_frame_metrics.csv",
    "mode_execution_manifest.csv",
    "mode_module_timing_characterization.csv",
    "criterionB_execution_summary.json",
}
PROVENANCE_TOP_LEVEL_KEYS = {
    "scope", "source_sha", "source_root", "patch_sha256_canonical_lf",
    "patch_apply_result", "patched_paths", "patched_file_sha256", "config",
    "config_sha256", "checkpoint", "checkpoint_sha256", "dataset_root",
    "frozen_slice", "frozen_slice_sha256_canonical_lf",
    "frozen_slice_sha256_working_tree_bytes", "frozen_slice_hash_semantics",
    "discovery_pair_ids", "discovery_pair_count", "holdout_pair_ids_metadata_only",
    "holdout_pair_count", "holdout_pairs_executed", "official_metadata_source",
    "accepted_nonmutating_discovery_aliases", "operational_baseline_boundary",
    "metric_semantics", "environment", "no_ablation_parity",
}
PARITY_TOP_LEVEL_KEYS = {
    "status", "tolerance", "maximum_observed_abs_diff", "source_sha", "input",
    "baseline_output_fingerprints", "instrumented_output_fingerprints",
    "external_raw_path", "external_raw_sha256",
}
CRITERION_A_EXECUTION_TOP_LEVEL_KEYS = {
    "status", "discovery_pairs_executed", "holdout_pairs_executed",
    "unique_discovery_source_sequences_executed", "frozen_interval_frames",
    "raw_mrm_external_path", "raw_mrm_sha256", "elapsed_seconds",
}
CRITERION_B_EXECUTION_TOP_LEVEL_KEYS = {
    "status", "scope", "criterion_a_gate", "discovery_pairs_executed",
    "discovery_intervals_executed", "holdout_pairs_executed",
    "holdout_outcomes_read", "modes", "physical_skip", "state_snapshot_parity",
    "baseline_branch_parity", "row_counts", "input_hashes", "determinism",
    "accepted_nonmutating_discovery_aliases", "external_raw_mrm", "output_hashes",
    "elapsed_seconds", "next_action", "refinement_executed", "stage4b_conclusion",
}
ANALYSIS_TOP_LEVEL_KEYS = {
    "schema_version", "analysis_contract", "inputs", "frozen_boundary",
    "criterion_a", "criterion_b", "stage4b_conclusion", "next_action",
    "non_claims", "outputs",
}


@dataclass(frozen=True)
class ExternalEvidence:
    source_artifact: str
    evidence_kind: str
    path: Path
    recorded_sha256: str | None


@dataclass(frozen=True)
class ExternalVerification:
    source_artifact: str
    evidence_kind: str
    path: str
    size_bytes: int | None
    recorded_sha256: str | None
    observed_sha256: str | None
    status: str


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _sha256_if_file(path: Path) -> str | None:
    return _sha256(path) if path.is_file() else None


def _normalized_lf_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _canonical_slice_row_hashes(
    path: Path,
) -> tuple[dict[str, str], tuple[str, ...], dict[str, dict[str, str]]]:
    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = normalized.splitlines(keepends=True)
    rows = list(csv.DictReader(io.StringIO(normalized, newline="")))
    if len(lines) != len(rows) + 1:
        raise ValueError("frozen slice contains an unsupported multiline CSV field")
    row_hashes = {
        str(row.get("pair_id", "")): hashlib.sha256(
            lines[index + 1].encode("utf-8")
        ).hexdigest()
        for index, row in enumerate(rows)
    }
    pair_order = tuple(str(row.get("pair_id", "")) for row in rows)
    return row_hashes, pair_order, {
        str(row.get("pair_id", "")): dict(row) for row in rows
    }


def _csv_header(path: Path) -> tuple[str, ...] | None:
    if not path.is_file():
        return None
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        try:
            return tuple(next(csv.reader(stream)))
        except StopIteration:
            return ()
        except csv.Error:
            return ("__INVALID_CSV__",)


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_csv(
    path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and _sha256(source) == _sha256(destination):
        return
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        with source.open("rb") as input_stream, temporary.open("wb") as output_stream:
            for block in iter(lambda: input_stream.read(1024 * 1024), b""):
                output_stream.write(block)
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_json(
    path: Path,
    blockers: list[str],
    label: str,
    *,
    required: bool,
) -> dict[str, Any] | None:
    if not path.is_file():
        if required:
            blockers.append(f"MISSING_{label}: {path}")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        blockers.append(f"INVALID_{label}: {path}: {exc}")
        return None
    if not isinstance(value, dict):
        blockers.append(f"INVALID_{label}: expected a JSON object at {path}")
        return None
    return value


def _load_csv(
    path: Path,
    blockers: list[str],
    label: str,
    *,
    required: bool,
) -> list[dict[str, str]]:
    if not path.is_file():
        if required:
            blockers.append(f"MISSING_{label}: {path}")
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    except (OSError, UnicodeError, csv.Error) as exc:
        blockers.append(f"INVALID_{label}: {path}: {exc}")
        return []


def _load_exact_csv(
    path: Path,
    expected_header: Sequence[str],
    blockers: list[str],
    label: str,
    *,
    required: bool,
) -> list[dict[str, str]]:
    header = _csv_header(path)
    if header is None:
        if required:
            blockers.append(f"MISSING_{label}: {path}")
        return []
    if header != tuple(expected_header):
        blockers.append(
            f"{label}_HEADER_MISMATCH: expected={tuple(expected_header)}; observed={header}"
        )
        return []
    return _load_csv(path, blockers, label, required=required)


def _require_mapping_children(
    document: dict[str, Any] | None,
    keys: Iterable[str],
    blockers: list[str],
    label: str,
) -> None:
    if document is None:
        return
    for key in keys:
        value = document.get(key)
        if not isinstance(value, Mapping):
            blockers.append(f"{label}_{key.upper()}_OBJECT_MISSING_OR_INVALID")
            document[key] = {}


def _require_exact_json_keys(
    document: Mapping[str, Any] | None,
    expected: set[str],
    blockers: list[str],
    label: str,
) -> None:
    if document is None:
        return
    observed = {str(key) for key in document}
    if observed != expected:
        blockers.append(
            f"{label}_TOP_LEVEL_KEY_SET_MISMATCH: "
            f"missing={sorted(expected - observed)}; "
            f"extra={sorted(observed - expected)}"
        )


def _as_bool(value: object) -> bool | None:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "pass"}:
        return True
    if normalized in {"false", "0", "no", "fail"}:
        return False
    return None


def _as_float(value: object) -> float | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        result = float(value)
    except (TypeError, ValueError):
        return None
    if result != result or result in {float("inf"), float("-inf")}:
        return None
    return result


def _as_int(value: object) -> int | None:
    number = _as_float(value)
    if number is None or not number.is_integer():
        return None
    return int(number)


def _as_sequence_tuple(value: object) -> tuple[object, ...] | None:
    if not isinstance(value, (list, tuple)):
        return None
    return tuple(value)


def _require_zero_count(
    document: Mapping[str, Any] | None,
    key: str,
    label: str,
    blockers: list[str],
    invalid_reasons: list[str],
) -> None:
    if document is None:
        return
    observed = _as_int(document.get(key))
    if observed is None:
        blockers.append(f"{label}_{key.upper()}_MISSING_OR_MALFORMED")
    elif observed != 0:
        invalid_reasons.append(f"{label}_{key.upper()}={observed}")


def _format_number(value: object, digits: int = 6) -> str:
    number = _as_float(value)
    if number is None:
        return "NOT AVAILABLE"
    return f"{number:.{digits}f}"


def _numbers_close(left: object, right: object, tolerance: float = 5e-10) -> bool:
    left_number = _as_float(left)
    right_number = _as_float(right)
    return (
        left_number is not None
        and right_number is not None
        and abs(left_number - right_number) <= tolerance
    )


def _inclusive_iou(
    prediction: Sequence[float], ground_truth: Sequence[float]
) -> float | None:
    if len(prediction) != 4 or len(ground_truth) != 4:
        return None
    pred_x2 = prediction[0] + prediction[2] - 1.0
    pred_y2 = prediction[1] + prediction[3] - 1.0
    gt_x2 = ground_truth[0] + ground_truth[2] - 1.0
    gt_y2 = ground_truth[1] + ground_truth[3] - 1.0
    intersection_w = max(min(pred_x2, gt_x2) - max(prediction[0], ground_truth[0]) + 1.0, 0.0)
    intersection_h = max(min(pred_y2, gt_y2) - max(prediction[1], ground_truth[1]) + 1.0, 0.0)
    intersection = intersection_w * intersection_h
    union = prediction[2] * prediction[3] + ground_truth[2] * ground_truth[3] - intersection
    return None if union <= 0.0 else intersection / union


def _inclusive_center_error(
    prediction: Sequence[float], ground_truth: Sequence[float]
) -> float | None:
    if len(prediction) != 4 or len(ground_truth) != 4:
        return None
    dx = (
        prediction[0] + 0.5 * (prediction[2] - 1.0)
        - ground_truth[0] - 0.5 * (ground_truth[2] - 1.0)
    )
    dy = (
        prediction[1] + 0.5 * (prediction[3] - 1.0)
        - ground_truth[1] - 0.5 * (ground_truth[3] - 1.0)
    )
    return (dx * dx + dy * dy) ** 0.5


def _ci_supports_direction(estimate: float, low: float, high: float) -> bool:
    return (estimate > 0 and low > 0) or (estimate < 0 and high < 0)


def _holm_adjusted(p_values: Mapping[str, float]) -> dict[str, float]:
    ordered = sorted(
        LOCKED_MODES,
        key=lambda mode: (p_values[mode], MODE_SELECTION_META[mode][2]),
    )
    adjusted: dict[str, float] = {}
    running = 0.0
    family_size = len(LOCKED_MODES)
    for rank, mode in enumerate(ordered, start=1):
        running = max(running, (family_size - rank + 1) * p_values[mode])
        adjusted[mode] = min(1.0, running)
    return adjusted


def _quantile_linear(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    location = (len(ordered) - 1) * probability
    lower = math.floor(location)
    upper = math.ceil(location)
    if lower == upper:
        return ordered[lower]
    fraction = location - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _locked_cluster_partitions(
    pair_a_rows: Sequence[Mapping[str, str]],
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[str, ...]]]:
    by_id = {str(row.get("pair_id", "")): row for row in pair_a_rows}
    primary: dict[str, list[str]] = defaultdict(list)
    for pair_id in EXPECTED_DISCOVERY_IDS:
        primary[str(by_id[pair_id].get("primary_sequence", ""))].append(pair_id)

    parent = {pair_id: pair_id for pair_id in EXPECTED_DISCOVERY_IDS}

    def find(pair_id: str) -> str:
        while parent[pair_id] != pair_id:
            parent[pair_id] = parent[parent[pair_id]]
            pair_id = parent[pair_id]
        return pair_id

    def union(left: str, right: str) -> None:
        left_root, right_root = find(left), find(right)
        if left_root != right_root:
            parent[max(left_root, right_root)] = min(left_root, right_root)

    for left_index, left in enumerate(EXPECTED_DISCOVERY_IDS):
        left_sequences = {
            str(by_id[left].get("primary_sequence", "")),
            str(by_id[left].get("control_sequence", "")),
        }
        for right in EXPECTED_DISCOVERY_IDS[left_index + 1:]:
            right_sequences = {
                str(by_id[right].get("primary_sequence", "")),
                str(by_id[right].get("control_sequence", "")),
            }
            if left_sequences & right_sequences:
                union(left, right)
    components: dict[str, list[str]] = defaultdict(list)
    for pair_id in EXPECTED_DISCOVERY_IDS:
        components[find(pair_id)].append(pair_id)
    return (
        {key: tuple(value) for key, value in sorted(primary.items())},
        {key: tuple(value) for key, value in sorted(components.items())},
    )


def _recompute_locked_bootstrap(
    pair_values: Mapping[str, float], clusters: Mapping[str, Sequence[str]]
) -> tuple[float, float, float, float]:
    cluster_names = tuple(sorted(clusters))
    rng = random.Random(20_260_826)
    distribution: list[float] = []
    for _ in range(10_000):
        sampled_clusters = [
            cluster_names[rng.randrange(len(cluster_names))]
            for _ in range(len(cluster_names))
        ]
        sampled_pairs = [
            pair_id for cluster in sampled_clusters for pair_id in clusters[cluster]
        ]
        distribution.append(
            math.fsum(pair_values[pair_id] for pair_id in sampled_pairs)
            / len(sampled_pairs)
        )
    nonpositive = sum(value <= 0.0 for value in distribution)
    nonnegative = sum(value >= 0.0 for value in distribution)
    p_value = min(
        1.0,
        2.0 * min(
            (nonpositive + 1) / 10_001,
            (nonnegative + 1) / 10_001,
        ),
    )
    return (
        statistics.fmean(pair_values[pair_id] for pair_id in sorted(pair_values)),
        _quantile_linear(distribution, 0.025),
        _quantile_linear(distribution, 0.975),
        p_value,
    )


def _validate_locked_statistics(
    analysis: Mapping[str, Any] | None,
    criterion_a_rows: Sequence[Mapping[str, str]],
    criterion_b_rows: Sequence[Mapping[str, str]],
    pair_a_rows: Sequence[Mapping[str, str]],
    pair_b_rows: Sequence[Mapping[str, str]],
    bootstrap_rows: Sequence[Mapping[str, str]],
    holm_rows: Sequence[Mapping[str, str]],
    blockers: list[str],
) -> tuple[bool | None, bool | None, str | None]:
    """Recompute both locked decisions and the selected path from CSV evidence."""

    contract = (analysis or {}).get("analysis_contract") or {}
    if _as_int(contract.get("bootstrap_resamples")) != 10_000:
        blockers.append("ANALYSIS_BOOTSTRAP_RESAMPLES_NOT_10000")
    if _as_int(contract.get("bootstrap_seed")) != 20_260_826:
        blockers.append("ANALYSIS_BOOTSTRAP_SEED_NOT_20260826")
    if _as_float(contract.get("familywise_alpha")) != 0.05:
        blockers.append("ANALYSIS_FAMILYWISE_ALPHA_NOT_0_05")
    if _as_bool(contract.get("physical_skip")) is not False:
        blockers.append("ANALYSIS_CONTRACT_PHYSICAL_SKIP_FALSE_NOT_EXPLICIT")
    if _as_sequence_tuple(contract.get("locked_modes")) != LOCKED_MODES:
        blockers.append("ANALYSIS_CONTRACT_LOCKED_MODES_MISMATCH")
    thresholds = contract.get("criterion_a_thresholds") or {}
    if not isinstance(thresholds, Mapping):
        blockers.append("ANALYSIS_CRITERION_A_THRESHOLDS_OBJECT_INVALID")
        thresholds = {}
    if not _numbers_close(thresholds.get("iou_weakness_minimum"), 0.05):
        blockers.append("ANALYSIS_CRITERION_A_IOU_THRESHOLD_MISMATCH")
    if not _numbers_close(thresholds.get("failure_weakness_minimum"), 0.10):
        blockers.append("ANALYSIS_CRITERION_A_FAILURE_THRESHOLD_MISMATCH")
    if not _numbers_close(contract.get("criterion_b_absolute_interaction_minimum"), 0.02):
        blockers.append("ANALYSIS_CRITERION_B_THRESHOLD_MISMATCH")

    a_by_metric = {str(row.get("metric", "")): row for row in criterion_a_rows}
    expected_a_metrics = {"iou_weakness", "failure_weakness"}
    derived_a: bool | None = None
    if set(a_by_metric) != expected_a_metrics:
        blockers.append("CRITERION_A_METRIC_SET_MISMATCH")
    else:
        pair_ids = {str(row.get("pair_id", "")) for row in pair_a_rows}
        if pair_ids != set(EXPECTED_DISCOVERY_IDS) or len(pair_a_rows) != 12:
            blockers.append("PAIR_LEVEL_A_DISCOVERY_KEY_SET_MISMATCH")
        derived_metric_pass: dict[str, bool] = {}
        for metric, threshold in (("iou_weakness", 0.05), ("failure_weakness", 0.10)):
            row = a_by_metric[metric]
            estimate = _as_float(row.get("estimate"))
            low = _as_float(row.get("primary_ci_low"))
            high = _as_float(row.get("primary_ci_high"))
            if estimate is None or low is None or high is None:
                blockers.append(f"CRITERION_A_NONFINITE_RESULT: {metric}")
                derived_metric_pass[metric] = False
                continue
            pair_estimates = [_as_float(pair.get(metric)) for pair in pair_a_rows]
            if any(value is None for value in pair_estimates):
                blockers.append(f"PAIR_LEVEL_A_NONFINITE_EFFECT: {metric}")
            else:
                recomputed = statistics.fmean(
                    value for value in pair_estimates if value is not None
                )
                if not _numbers_close(recomputed, estimate):
                    blockers.append(f"CRITERION_A_PAIR_AGGREGATE_MISMATCH: {metric}")
            derived = estimate >= threshold and low > 0 and high > 0
            derived_metric_pass[metric] = derived
            if not _numbers_close(row.get("threshold"), threshold):
                blockers.append(f"CRITERION_A_ROW_THRESHOLD_MISMATCH: {metric}")
            if _as_int(row.get("n_pairs")) != 12:
                blockers.append(f"CRITERION_A_N_PAIRS_NOT_12: {metric}")
            if _as_bool(row.get("metric_pass")) is not derived:
                blockers.append(f"CRITERION_A_METRIC_PASS_RECOMPUTE_MISMATCH: {metric}")
        derived_a = any(derived_metric_pass.values())
        if any(_as_bool(row.get("criterion_a_pass")) is not derived_a
               for row in criterion_a_rows):
            blockers.append("CRITERION_A_FAMILY_PASS_RECOMPUTE_MISMATCH")
        declared_a = ((analysis or {}).get("criterion_a") or {}).get("pass")
        declared_a_status = str(
            ((analysis or {}).get("criterion_a") or {}).get("status", "")
        ).upper()
        if declared_a is not derived_a or declared_a_status != ("PASS" if derived_a else "FAIL"):
            blockers.append("CRITERION_A_SUMMARY_DECISION_RECOMPUTE_MISMATCH")

    expected_bootstrap_keys = {
        ("CRITERION_A", metric, scheme)
        for metric in expected_a_metrics
        for scheme in ("PRIMARY_SEQUENCE_CLUSTERED", "CONNECTED_SOURCE_COMPONENT")
    }

    derived_b: bool | None = None
    selected: str | None = None
    if criterion_b_rows:
        b_by_mode = {str(row.get("mode", "")): row for row in criterion_b_rows}
        if tuple(str(row.get("mode", "")) for row in criterion_b_rows) != LOCKED_MODES:
            blockers.append("CRITERION_B_MODE_ORDER_MISMATCH")
        if set(b_by_mode) != set(LOCKED_MODES):
            blockers.append("CRITERION_B_MODE_SET_MISMATCH")
        else:
            pair_b_keys = {
                (str(row.get("mode", "")), str(row.get("pair_id", "")))
                for row in pair_b_rows
            }
            expected_pair_b_keys = {
                (mode, pair_id) for mode in LOCKED_MODES for pair_id in EXPECTED_DISCOVERY_IDS
            }
            if pair_b_keys != expected_pair_b_keys or len(pair_b_rows) != 108:
                blockers.append("PAIR_LEVEL_B_LOCKED_KEY_SET_MISMATCH")
            p_values: dict[str, float] = {}
            for mode in LOCKED_MODES:
                value = _as_float(b_by_mode[mode].get("primary_p_unadjusted"))
                if value is None or not 0 <= value <= 1:
                    blockers.append(f"CRITERION_B_INVALID_P_VALUE: {mode}")
                    value = 1.0
                p_values[mode] = value
            recomputed_holm = _holm_adjusted(p_values)
            test_pass: dict[str, bool] = {}
            for mode in LOCKED_MODES:
                row = b_by_mode[mode]
                estimate = _as_float(row.get("mean_interaction"))
                low = _as_float(row.get("primary_ci_low"))
                high = _as_float(row.get("primary_ci_high"))
                if estimate is None or low is None or high is None:
                    blockers.append(f"CRITERION_B_NONFINITE_RESULT: {mode}")
                    test_pass[mode] = False
                    continue
                pair_values = [
                    _as_float(pair.get("interaction"))
                    for pair in pair_b_rows if pair.get("mode") == mode
                ]
                if len(pair_values) != 12 or any(value is None for value in pair_values):
                    blockers.append(f"PAIR_LEVEL_B_NONFINITE_OR_INCOMPLETE: {mode}")
                else:
                    recomputed_mean = statistics.fmean(
                        value for value in pair_values if value is not None
                    )
                    if not _numbers_close(recomputed_mean, estimate):
                        blockers.append(f"CRITERION_B_PAIR_AGGREGATE_MISMATCH: {mode}")
                direction_stable = _ci_supports_direction(estimate, low, high)
                derived = (
                    abs(estimate) >= 0.02
                    and direction_stable
                    and recomputed_holm[mode] <= 0.05
                )
                test_pass[mode] = derived
                if not _numbers_close(
                    row.get("primary_p_holm_adjusted"), recomputed_holm[mode]
                ):
                    blockers.append(f"CRITERION_B_HOLM_RECOMPUTE_MISMATCH: {mode}")
                if _as_bool(row.get("direction_stable")) is not direction_stable:
                    blockers.append(f"CRITERION_B_DIRECTION_STABILITY_MISMATCH: {mode}")
                if _as_bool(row.get("scientifically_interpretable")) is not (
                    estimate != 0
                ):
                    blockers.append(f"CRITERION_B_INTERPRETABILITY_MISMATCH: {mode}")
                if _as_bool(row.get("test_pass")) is not derived:
                    blockers.append(f"CRITERION_B_TEST_PASS_RECOMPUTE_MISMATCH: {mode}")
            derived_b = any(test_pass.values())
            if derived_b:
                selected = min(
                    (mode for mode in LOCKED_MODES if test_pass[mode]),
                    key=lambda mode: (
                        -abs(_as_float(b_by_mode[mode].get("mean_interaction")) or 0.0),
                        MODE_SELECTION_META[mode][0],
                        MODE_SELECTION_META[mode][1],
                        MODE_SELECTION_META[mode][2],
                    ),
                )
            selected_rows = {
                str(row.get("mode", ""))
                for row in criterion_b_rows
                if _as_bool(row.get("selected_refinement_path")) is True
            }
            expected_selected_rows = {selected} if selected else set()
            if selected_rows != expected_selected_rows:
                blockers.append("CRITERION_B_SELECTED_ROW_RECOMPUTE_MISMATCH")
            if any(_as_bool(row.get("criterion_b_pass")) is not derived_b
                   for row in criterion_b_rows):
                blockers.append("CRITERION_B_FAMILY_PASS_RECOMPUTE_MISMATCH")
            summary_b = (analysis or {}).get("criterion_b") or {}
            if summary_b.get("pass") is not derived_b:
                blockers.append("CRITERION_B_SUMMARY_PASS_RECOMPUTE_MISMATCH")
            if str(summary_b.get("status", "")).upper() != (
                "PASS" if derived_b else "FAIL"
            ):
                blockers.append("CRITERION_B_SUMMARY_STATUS_RECOMPUTE_MISMATCH")
            if summary_b.get("selected_refinement_path") != selected:
                blockers.append("CRITERION_B_SUMMARY_SELECTED_PATH_RECOMPUTE_MISMATCH")

            holm_by_mode = {str(row.get("mode", "")): row for row in holm_rows}
            ordered = sorted(
                LOCKED_MODES,
                key=lambda mode: (p_values[mode], MODE_SELECTION_META[mode][2]),
            )
            ranks = {mode: index for index, mode in enumerate(ordered, start=1)}
            if set(holm_by_mode) != set(LOCKED_MODES) or len(holm_rows) != 9:
                blockers.append("HOLM_TABLE_MODE_SET_MISMATCH")
            else:
                for mode in LOCKED_MODES:
                    row = holm_by_mode[mode]
                    if (
                        not _numbers_close(row.get("p_unadjusted"), p_values[mode])
                        or not _numbers_close(row.get("p_holm_adjusted"), recomputed_holm[mode])
                        or _as_int(row.get("holm_rank")) != ranks[mode]
                        or _as_int(row.get("holm_multiplier")) != 10 - ranks[mode]
                        or _as_int(row.get("family_size")) != 9
                        or not _numbers_close(row.get("familywise_alpha"), 0.05)
                        or _as_bool(row.get("reject_familywise_0_05"))
                        is not (recomputed_holm[mode] <= 0.05)
                    ):
                        blockers.append(f"HOLM_TABLE_RECOMPUTE_MISMATCH: {mode}")
            expected_bootstrap_keys |= {
                ("CRITERION_B", mode, scheme)
                for mode in LOCKED_MODES
                for scheme in (
                    "PRIMARY_SEQUENCE_CLUSTERED", "CONNECTED_SOURCE_COMPONENT",
                )
            }
    else:
        summary_b = (analysis or {}).get("criterion_b") or {}
        if summary_b.get("pass") is not None:
            blockers.append("CRITERION_B_SUMMARY_HAS_DECISION_WITHOUT_RESULT_ROWS")

    observed_bootstrap_keys = {
        (
            str(row.get("analysis_family", "")),
            str(row.get("test_id", "")),
            str(row.get("bootstrap_scheme", "")),
        )
        for row in bootstrap_rows
    }
    if observed_bootstrap_keys != expected_bootstrap_keys:
        blockers.append(
            "BOOTSTRAP_LOCKED_KEY_SET_MISMATCH: "
            f"expected={len(expected_bootstrap_keys)}; observed={len(observed_bootstrap_keys)}"
        )
    bootstrap_by_key = {
        (
            str(row.get("analysis_family", "")),
            str(row.get("test_id", "")),
            str(row.get("bootstrap_scheme", "")),
        ): row
        for row in bootstrap_rows
    }
    if len(bootstrap_by_key) != len(bootstrap_rows):
        blockers.append("BOOTSTRAP_DUPLICATE_LOCKED_KEY")
    for metric, criterion_row in a_by_metric.items():
        for scheme, criterion_columns in (
            (
                "PRIMARY_SEQUENCE_CLUSTERED",
                ("primary_ci_low", "primary_ci_high", "primary_p_two_sided_sign_tail"),
            ),
            (
                "CONNECTED_SOURCE_COMPONENT",
                ("component_ci_low", "component_ci_high", "component_p_two_sided_sign_tail"),
            ),
        ):
            bootstrap_row = bootstrap_by_key.get(("CRITERION_A", metric, scheme))
            if bootstrap_row is None:
                continue
            if (
                not _numbers_close(bootstrap_row.get("estimate"), criterion_row.get("estimate"))
                or not _numbers_close(
                    bootstrap_row.get("ci_low"), criterion_row.get(criterion_columns[0])
                )
                or not _numbers_close(
                    bootstrap_row.get("ci_high"), criterion_row.get(criterion_columns[1])
                )
                or not _numbers_close(
                    bootstrap_row.get("p_two_sided_sign_tail"),
                    criterion_row.get(criterion_columns[2]),
                )
            ):
                blockers.append(f"CRITERION_A_BOOTSTRAP_BINDING_MISMATCH: {metric}/{scheme}")
    b_by_mode_for_binding = {
        str(row.get("mode", "")): row for row in criterion_b_rows
    }
    for mode, criterion_row in b_by_mode_for_binding.items():
        for scheme, criterion_columns in (
            (
                "PRIMARY_SEQUENCE_CLUSTERED",
                ("primary_ci_low", "primary_ci_high", "primary_p_unadjusted"),
            ),
            (
                "CONNECTED_SOURCE_COMPONENT",
                ("component_ci_low", "component_ci_high", "component_p_two_sided_sign_tail"),
            ),
        ):
            bootstrap_row = bootstrap_by_key.get(("CRITERION_B", mode, scheme))
            if bootstrap_row is None:
                continue
            if (
                not _numbers_close(
                    bootstrap_row.get("estimate"), criterion_row.get("mean_interaction")
                )
                or not _numbers_close(
                    bootstrap_row.get("ci_low"), criterion_row.get(criterion_columns[0])
                )
                or not _numbers_close(
                    bootstrap_row.get("ci_high"), criterion_row.get(criterion_columns[1])
                )
                or not _numbers_close(
                    bootstrap_row.get("p_two_sided_sign_tail"),
                    criterion_row.get(criterion_columns[2]),
                )
            ):
                blockers.append(f"CRITERION_B_BOOTSTRAP_BINDING_MISMATCH: {mode}/{scheme}")
    pair_a_by_id_for_bootstrap = {
        str(row.get("pair_id", "")): row for row in pair_a_rows
    }
    if set(pair_a_by_id_for_bootstrap) == set(EXPECTED_DISCOVERY_IDS):
        primary_clusters, component_clusters = _locked_cluster_partitions(pair_a_rows)
        cluster_schemes = {
            "PRIMARY_SEQUENCE_CLUSTERED": primary_clusters,
            "CONNECTED_SOURCE_COMPONENT": component_clusters,
        }
        for metric in ("iou_weakness", "failure_weakness"):
            values = {
                pair_id: _as_float(pair_a_by_id_for_bootstrap[pair_id].get(metric))
                for pair_id in EXPECTED_DISCOVERY_IDS
            }
            if all(value is not None for value in values.values()):
                numeric_values = {
                    key: float(value) for key, value in values.items()
                    if value is not None
                }
                for scheme, clusters in cluster_schemes.items():
                    observed = bootstrap_by_key.get(("CRITERION_A", metric, scheme))
                    if observed is None:
                        continue
                    recomputed = _recompute_locked_bootstrap(numeric_values, clusters)
                    if any(
                        not _numbers_close(observed.get(column), expected)
                        for column, expected in zip(
                            ("estimate", "ci_low", "ci_high", "p_two_sided_sign_tail"),
                            recomputed,
                        )
                    ):
                        blockers.append(
                            f"CRITERION_A_BOOTSTRAP_RECOMPUTE_MISMATCH: "
                            f"{metric}/{scheme}"
                        )
        pair_b_by_mode_and_id = {
            (str(row.get("mode", "")), str(row.get("pair_id", ""))): row
            for row in pair_b_rows
        }
        for mode in LOCKED_MODES:
            values = {
                pair_id: _as_float(
                    (pair_b_by_mode_and_id.get((mode, pair_id)) or {}).get("interaction")
                )
                for pair_id in EXPECTED_DISCOVERY_IDS
            }
            if all(value is not None for value in values.values()):
                numeric_values = {
                    key: float(value) for key, value in values.items()
                    if value is not None
                }
                for scheme, clusters in cluster_schemes.items():
                    observed = bootstrap_by_key.get(("CRITERION_B", mode, scheme))
                    if observed is None:
                        continue
                    recomputed = _recompute_locked_bootstrap(numeric_values, clusters)
                    if any(
                        not _numbers_close(observed.get(column), expected)
                        for column, expected in zip(
                            ("estimate", "ci_low", "ci_high", "p_two_sided_sign_tail"),
                            recomputed,
                        )
                    ):
                        blockers.append(
                            f"CRITERION_B_BOOTSTRAP_RECOMPUTE_MISMATCH: {mode}/{scheme}"
                        )
    for row in bootstrap_rows:
        scheme = str(row.get("bootstrap_scheme", ""))
        expected_cluster = (
            "primary_sequence" if scheme == "PRIMARY_SEQUENCE_CLUSTERED"
            else "connected_source_component"
        )
        expected_n_clusters = 11 if scheme == "PRIMARY_SEQUENCE_CLUSTERED" else 9
        expected_role = (
            "PRIMARY_DECISION" if scheme == "PRIMARY_SEQUENCE_CLUSTERED"
            else "REQUIRED_SENSITIVITY"
        )
        if (
            _as_int(row.get("resamples")) != 10_000
            or _as_int(row.get("seed")) != 20_260_826
            or _as_int(row.get("n_pairs")) != 12
            or _as_int(row.get("n_clusters")) != expected_n_clusters
            or row.get("cluster_unit") != expected_cluster
            or row.get("decision_role") != expected_role
        ):
            blockers.append(
                "BOOTSTRAP_CONTRACT_ROW_MISMATCH: "
                f"{row.get('analysis_family')}/{row.get('test_id')}/{scheme}"
            )
    return derived_a, derived_b, selected


def _validate_per_frame_effect_bindings(
    baseline_path: Path,
    mode_path: Path,
    frozen_rows_by_id: Mapping[str, Mapping[str, str]],
    pair_a_rows: Sequence[Mapping[str, str]],
    pair_b_rows: Sequence[Mapping[str, str]],
    criterion_b_was_run: bool,
    blockers: list[str],
) -> None:
    """Bind pair-level effects to guarded discovery-only per-frame outcomes."""

    baseline_rows = _load_exact_csv(
        baseline_path, BASELINE_METRIC_FIELDS, blockers,
        "BASELINE_PER_FRAME_METRICS", required=True,
    )
    baseline: dict[
        tuple[str, str, int],
        tuple[
            float, bool, float, tuple[float, ...], tuple[int, ...],
            tuple[float, ...], float, bool,
        ],
    ] = {}
    for row in baseline_rows:
        pair_id = str(row.get("pair_id", ""))
        side = str(row.get("side", ""))
        frame_index = _as_int(row.get("frame_index"))
        iou = _as_float(row.get("iou"))
        failure = _as_bool(row.get("failure"))
        success = _as_bool(row.get("success_at_0_5"))
        center_error = _as_float(row.get("center_error"))
        float_box_values = tuple(
            _as_float(row.get(f"pred_{axis}_float")) for axis in "xywh"
        )
        int_box_values = tuple(
            _as_int(row.get(f"pred_{axis}_int")) for axis in "xywh"
        )
        gt_box_values = tuple(_as_float(row.get(f"gt_{axis}")) for axis in "xywh")
        boxes_valid = (
            all(value is not None for value in float_box_values)
            and all(value is not None for value in int_box_values)
            and all(value is not None for value in gt_box_values)
        )
        float_box = tuple(float(value) for value in float_box_values if value is not None)
        int_box = tuple(int(value) for value in int_box_values if value is not None)
        gt_box = tuple(float(value) for value in gt_box_values if value is not None)
        recomputed_iou = _inclusive_iou(int_box, gt_box) if boxes_valid else None
        recomputed_iou_float = _inclusive_iou(float_box, gt_box) if boxes_valid else None
        recomputed_center = (
            _inclusive_center_error(int_box, gt_box) if boxes_valid else None
        )
        iou_float = _as_float(row.get("iou_float"))
        initialization = _as_bool(row.get("initialization_frame"))
        evaluator_override = _as_bool(row.get("evaluator_first_frame_override"))
        score = _as_float(row.get("score_map_max"))
        confidence = _as_float(row.get("confidence_score"))
        frozen = frozen_rows_by_id.get(pair_id)
        valid_metadata = (
            frozen is not None
            and side in {"primary", "control"}
            and frame_index is not None
            and row.get("sequence") == frozen.get(f"{side}_sequence")
            and int(frozen[f"{side}_start"]) <= frame_index
            <= int(frozen[f"{side}_end"])
        )
        key = (pair_id, side, frame_index or -1)
        if (
            not valid_metadata
            or key in baseline
            or iou is None
            or not 0.0 <= iou <= 1.0
            or failure is None
            or failure is not (iou < 0.5)
            or success is not (iou >= 0.5)
            or center_error is None
            or center_error < 0.0
            or not boxes_valid
            or tuple(int(value) for value in float_box) != int_box
            or recomputed_iou is None
            or not _numbers_close(iou, recomputed_iou)
            or recomputed_iou_float is None
            or not _numbers_close(iou_float, recomputed_iou_float)
            or recomputed_center is None
            or not _numbers_close(center_error, recomputed_center)
            or initialization is not (frame_index == 1)
            or evaluator_override is not initialization
            or (initialization and (score is not None or confidence is not None))
            or (not initialization and (score is None or confidence is None))
            or _as_bool(row.get("physical_skip")) is not False
            or row.get("tracker_mode") != "T1"
            or row.get("ablation_control") != "none"
        ):
            blockers.append(
                f"BASELINE_PER_FRAME_ROW_CONTRACT_MISMATCH: "
                f"{pair_id}/{side}/{frame_index}"
            )
            continue
        baseline[key] = (
            iou, failure, center_error, float_box, int_box, gt_box,
            iou_float if iou_float is not None else 0.0, bool(initialization),
        )
    expected_baseline_keys = {
        (pair_id, side, frame_index)
        for pair_id in EXPECTED_DISCOVERY_IDS
        for side in ("primary", "control")
        for frame_index in range(
            int(frozen_rows_by_id[pair_id][f"{side}_start"]),
            int(frozen_rows_by_id[pair_id][f"{side}_end"]) + 1,
        )
    }
    if set(baseline) != expected_baseline_keys or len(baseline_rows) != 596:
        blockers.append(
            "BASELINE_PER_FRAME_LOCKED_COVERAGE_MISMATCH: "
            f"rows={len(baseline_rows)}; keys={len(baseline)}"
        )
    pair_a_by_id = {str(row.get("pair_id", "")): row for row in pair_a_rows}
    if set(baseline) == expected_baseline_keys:
        for pair_id in EXPECTED_DISCOVERY_IDS:
            pair_row = pair_a_by_id.get(pair_id)
            if pair_row is None:
                continue
            aggregates: dict[str, tuple[float, float, float, int]] = {}
            for side in ("primary", "control"):
                values = [
                    baseline[key]
                    for key in sorted(baseline)
                    if key[0] == pair_id and key[1] == side
                ]
                aggregates[side] = (
                    statistics.fmean(value[0] for value in values),
                    statistics.fmean(float(value[1]) for value in values),
                    statistics.fmean(value[2] for value in values),
                    len(values),
                )
            primary = aggregates["primary"]
            control = aggregates["control"]
            expected_values = {
                "primary_frame_count": primary[3],
                "control_frame_count": control[3],
                "primary_mean_iou": primary[0],
                "control_mean_iou": control[0],
                "iou_weakness": control[0] - primary[0],
                "primary_failure_rate": primary[1],
                "control_failure_rate": control[1],
                "failure_weakness": primary[1] - control[1],
                "primary_mean_center_error": primary[2],
                "control_mean_center_error": control[2],
                "center_error_primary_minus_control": primary[2] - control[2],
            }
            if any(
                not _numbers_close(pair_row.get(column), expected)
                for column, expected in expected_values.items()
            ):
                blockers.append(f"PAIR_LEVEL_A_PER_FRAME_BINDING_MISMATCH: {pair_id}")

    if not criterion_b_was_run:
        return
    mode_rows = _load_exact_csv(
        mode_path, MODE_METRIC_FIELDS, blockers,
        "MODE_PER_FRAME_METRICS", required=True,
    )
    modes: dict[tuple[str, str, str, int], tuple[float, float]] = {}
    for row in mode_rows:
        pair_id = str(row.get("pair_id", ""))
        side = str(row.get("side", ""))
        mode = str(row.get("mode", ""))
        frame_index = _as_int(row.get("frame_index"))
        iou = _as_float(row.get("iou"))
        baseline_iou = _as_float(row.get("baseline_iou"))
        contribution = _as_float(row.get("contribution"))
        failure = _as_bool(row.get("failure"))
        success = _as_bool(row.get("success_at_0_5"))
        center_error = _as_float(row.get("center_error"))
        float_box_values = tuple(
            _as_float(row.get(f"pred_{axis}_float")) for axis in "xywh"
        )
        int_box_values = tuple(
            _as_int(row.get(f"pred_{axis}_int")) for axis in "xywh"
        )
        gt_box_values = tuple(_as_float(row.get(f"gt_{axis}")) for axis in "xywh")
        boxes_valid = (
            all(value is not None for value in float_box_values)
            and all(value is not None for value in int_box_values)
            and all(value is not None for value in gt_box_values)
        )
        float_box = tuple(float(value) for value in float_box_values if value is not None)
        int_box = tuple(int(value) for value in int_box_values if value is not None)
        gt_box = tuple(float(value) for value in gt_box_values if value is not None)
        recomputed_iou = _inclusive_iou(int_box, gt_box) if boxes_valid else None
        recomputed_iou_float = _inclusive_iou(float_box, gt_box) if boxes_valid else None
        recomputed_center = (
            _inclusive_center_error(int_box, gt_box) if boxes_valid else None
        )
        iou_float = _as_float(row.get("iou_float"))
        initialization = _as_bool(row.get("initialization_frame"))
        evaluator_override = _as_bool(row.get("evaluator_first_frame_override"))
        branch_executed = _as_bool(row.get("branch_frame_executed"))
        score = _as_float(row.get("score_map_max"))
        confidence = _as_float(row.get("confidence_score"))
        baseline_key = (pair_id, side, frame_index or -1)
        frozen = frozen_rows_by_id.get(pair_id)
        key = (mode, pair_id, side, frame_index or -1)
        if (
            frozen is None
            or mode not in LOCKED_MODES
            or baseline_key not in baseline
            or key in modes
            or row.get("sequence") != frozen.get(f"{side}_sequence")
            or iou is None
            or not 0.0 <= iou <= 1.0
            or baseline_iou is None
            or contribution is None
            or not _numbers_close(baseline_iou, baseline[baseline_key][0])
            or not _numbers_close(contribution, baseline_iou - iou)
            or any(
                not _numbers_close(observed, expected)
                for observed, expected in zip(gt_box, baseline[baseline_key][5])
            )
            or failure is not (iou < 0.5)
            or success is not (iou >= 0.5)
            or center_error is None
            or not boxes_valid
            or tuple(int(value) for value in float_box) != int_box
            or recomputed_iou is None
            or not _numbers_close(iou, recomputed_iou)
            or recomputed_iou_float is None
            or not _numbers_close(iou_float, recomputed_iou_float)
            or recomputed_center is None
            or not _numbers_close(center_error, recomputed_center)
            or initialization is not (frame_index == 1)
            or evaluator_override is not initialization
            or branch_executed is not (not bool(initialization))
            or (initialization and (score is not None or confidence is not None))
            or (not initialization and (score is None or confidence is None))
            or row.get("tracker_mode") != "T1"
            or row.get("ablation_control") != mode
            or _as_bool(row.get("physical_skip")) is not False
            or (
                bool(initialization)
                and (
                    not _numbers_close(contribution, 0.0)
                    or int_box != baseline[baseline_key][4]
                    or any(
                        not _numbers_close(observed, expected)
                        for observed, expected in zip(
                            float_box, baseline[baseline_key][3]
                        )
                    )
                )
            )
        ):
            blockers.append(
                f"MODE_PER_FRAME_ROW_CONTRACT_MISMATCH: "
                f"{mode}/{pair_id}/{side}/{frame_index}"
            )
            continue
        modes[key] = (iou, contribution)
    expected_mode_keys = {
        (mode, pair_id, side, frame_index)
        for mode in LOCKED_MODES
        for pair_id, side, frame_index in expected_baseline_keys
    }
    if set(modes) != expected_mode_keys or len(mode_rows) != 596 * len(LOCKED_MODES):
        blockers.append(
            "MODE_PER_FRAME_LOCKED_COVERAGE_MISMATCH: "
            f"rows={len(mode_rows)}; keys={len(modes)}"
        )
        return
    pair_b_by_key = {
        (str(row.get("mode", "")), str(row.get("pair_id", ""))): row
        for row in pair_b_rows
    }
    for mode in LOCKED_MODES:
        for pair_id in EXPECTED_DISCOVERY_IDS:
            pair_row = pair_b_by_key.get((mode, pair_id))
            if pair_row is None:
                continue
            side_means = {
                side: statistics.fmean(
                    modes[(mode, pair_id, side, frame_index)][1]
                    for key_pair_id, row_side, frame_index
                    in sorted(expected_baseline_keys)
                    if key_pair_id == pair_id and row_side == side
                )
                for side in ("primary", "control")
            }
            if (
                not _numbers_close(
                    pair_row.get("contribution_distractor"), side_means["primary"]
                )
                or not _numbers_close(
                    pair_row.get("contribution_control"), side_means["control"]
                )
                or not _numbers_close(
                    pair_row.get("interaction"),
                    side_means["primary"] - side_means["control"],
                )
            ):
                blockers.append(
                    f"PAIR_LEVEL_B_PER_FRAME_BINDING_MISMATCH: {mode}/{pair_id}"
                )


def _validate_environment(
    provenance: Mapping[str, Any] | None, blockers: list[str]
) -> None:
    if provenance is None:
        return
    environment = provenance.get("environment")
    if not isinstance(environment, Mapping):
        blockers.append("ENVIRONMENT_OBJECT_MISSING_OR_INVALID")
        return
    required_text = ("os", "cpu", "gpu", "python", "torch", "torch_cuda", "dtype")
    for key in required_text:
        if not isinstance(environment.get(key), str) or not str(environment.get(key)).strip():
            blockers.append(f"ENVIRONMENT_{key.upper()}_MISSING")
    for key in ("ram_bytes", "gpu_total_memory_bytes"):
        value = _as_int(environment.get(key))
        if value is None or value <= 0:
            blockers.append(f"ENVIRONMENT_{key.upper()}_INVALID")
    if _as_bool(environment.get("cuda_available")) is not True:
        blockers.append("ENVIRONMENT_CUDA_AVAILABLE_NOT_TRUE")
    if _as_int(environment.get("cudnn")) is None:
        blockers.append("ENVIRONMENT_CUDNN_MISSING")
    if environment.get("dtype") != "torch.float32":
        blockers.append(f"ENVIRONMENT_DTYPE_MISMATCH: {environment.get('dtype')}")
    if _as_int(environment.get("seed")) != 20_260_826:
        blockers.append("ENVIRONMENT_SEED_NOT_20260826")
    packages = environment.get("packages")
    if not isinstance(packages, Mapping):
        blockers.append("ENVIRONMENT_PACKAGES_OBJECT_MISSING_OR_INVALID")
    else:
        for key in ("numpy", "pandas", "timm", "torchvision", "yacs"):
            if not isinstance(packages.get(key), str) or not str(packages.get(key)).strip():
                blockers.append(f"ENVIRONMENT_PACKAGE_{key.upper()}_MISSING")
    deterministic = environment.get("deterministic_settings")
    expected_determinism = {
        "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
        "cudnn_benchmark": False,
        "cudnn_deterministic": True,
        "torch_deterministic_algorithms": True,
    }
    if not isinstance(deterministic, Mapping):
        blockers.append("ENVIRONMENT_DETERMINISTIC_SETTINGS_MISSING_OR_INVALID")
    else:
        for key, expected in expected_determinism.items():
            if deterministic.get(key) != expected:
                blockers.append(
                    f"ENVIRONMENT_DETERMINISM_MISMATCH: {key}="
                    f"{deterministic.get(key)!r}; expected={expected!r}"
                )


def _markdown_cell(value: object) -> str:
    if value is None or str(value) == "":
        return "NOT AVAILABLE"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _markdown_table(headers: Sequence[str], rows: Iterable[Sequence[object]]) -> str:
    materialized = [list(row) for row in rows]
    lines = [
        "| " + " | ".join(_markdown_cell(value) for value in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    if materialized:
        lines.extend(
            "| " + " | ".join(_markdown_cell(value) for value in row) + " |"
            for row in materialized
        )
    else:
        lines.append("| " + " | ".join("NOT RUN" for _ in headers) + " |")
    return "\n".join(lines)


def _repo_relative(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _is_within(path: Path, root: Path) -> bool:
    try:
        common = os.path.commonpath(
            (os.path.normcase(str(path.resolve())), os.path.normcase(str(root.resolve())))
        )
    except (OSError, ValueError):
        return False
    return common == os.path.normcase(str(root.resolve()))


def _status_is_pass(value: object) -> bool:
    normalized = str(value or "").strip().upper()
    return normalized == "PASS"


def _status_is_complete(value: object) -> bool:
    normalized = str(value or "").strip().upper()
    return normalized in {
        "PASS",
        "COMPLETE",
        "COMPLETED",
        "SUCCESS",
        "EXECUTION_COMPLETE",
        "REFINEMENT_EXECUTION_COMPLETE",
        "BOUNDED_REFINEMENT_COMPLETE",
        "T3_EXECUTION_COMPLETE",
        "COMPONENT_COMPLETE",
    }


def _deep_values_for_key(value: object, key_pattern: re.Pattern[str]) -> list[object]:
    matches: list[object] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            if key_pattern.search(str(key)):
                matches.append(child)
            matches.extend(_deep_values_for_key(child, key_pattern))
    elif isinstance(value, list):
        for child in value:
            matches.extend(_deep_values_for_key(child, key_pattern))
    return matches


def _json_holdout_outcome_signals(value: object, context: str = "") -> list[str]:
    """Detect outcome-bearing hold-out structures while permitting frozen metadata."""

    signals: list[str] = []
    outcome_tokens = (
        "iou", "failure", "score", "confidence", "contribution", "interaction",
        "prediction", "utility", "metric", "latency", "result",
    )
    metadata_holdout_keys = {
        "holdout_pair_ids_metadata_only",
        "holdout_ids_used_only_as_read_guard",
        "holdout_pair_count",
        "holdout_pair_count_in_seal_metadata",
        "holdout_pairs_executed",
        "holdout_outcomes_read",
        "holdout_pairs_present_in_outcome_inputs",
    }
    if isinstance(value, Mapping):
        holdout_identifiers = {
            str(child)
            for key, child in value.items()
            if str(key).lower() in {"id", "pair", "pair_id", "source_pair_id"}
            and str(child) in EXPECTED_HOLDOUT_IDS
        }
        if holdout_identifiers and any(
            any(token in str(key).lower() for token in outcome_tokens)
            for key in value
        ):
            signals.append(
                f"{context or '<root>'}.id={sorted(holdout_identifiers)}"
            )
        for key, child in value.items():
            key_text = str(key)
            child_context = f"{context}.{key_text}" if context else key_text
            if key_text in EXPECTED_HOLDOUT_IDS:
                signals.append(child_context)
                continue
            lowered = key_text.lower()
            if (
                "holdout" in lowered
                and lowered not in metadata_holdout_keys
                and child not in (None, False, 0, "", [], {})
            ):
                signals.append(child_context)
                continue
            signals.extend(_json_holdout_outcome_signals(child, child_context))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            signals.extend(_json_holdout_outcome_signals(child, f"{context}[{index}]"))
    elif str(value) in EXPECTED_HOLDOUT_IDS and any(
        token in context.lower() for token in outcome_tokens
    ):
        signals.append(f"{context}={value}")
    return signals


def _guard_discovery_first_field(path: Path) -> tuple[str, str | None, int | None]:
    """Inspect only column one before consuming any outcome fields.

    Baseline and mode per-frame CSV contracts put ``pair_id`` first.  The
    unbuffered byte reader stops at the first comma.  If that identifier is a
    sealed hold-out ID, no byte after the comma on the offending row is read.
    """

    if not path.is_file():
        return "MISSING", None, None
    with path.open("rb", buffering=0) as stream:
        line_number = 0
        while True:
            first_field = bytearray()
            saw_any = False
            delimiter: bytes | None = None
            while True:
                byte = stream.read(1)
                if byte == b"":
                    delimiter = None
                    break
                saw_any = True
                if byte in {b",", b"\n"}:
                    delimiter = byte
                    break
                if byte != b"\r":
                    first_field.extend(byte)
            if not saw_any:
                break
            line_number += 1
            try:
                token = first_field.decode("utf-8-sig").strip().strip('"')
            except UnicodeDecodeError:
                return "INVALID_ENCODING", None, line_number
            if line_number == 1:
                if token != "pair_id":
                    return "PAIR_ID_NOT_FIRST", token, line_number
            elif token in EXPECTED_HOLDOUT_IDS:
                return "HOLDOUT_DETECTED_BEFORE_OUTCOME_READ", token, line_number
            elif token not in EXPECTED_DISCOVERY_IDS:
                return "NON_DISCOVERY_PAIR_ID", token, line_number

            # This row is confirmed discovery-only.  It is now safe to consume
            # the rest of the physical record.  Execution outputs never quote
            # embedded newlines, so a newline terminates the row.
            if delimiter == b",":
                while True:
                    byte = stream.read(1)
                    if byte in {b"", b"\n"}:
                        break
            if delimiter is None:
                break
    if line_number <= 1:
        return "EMPTY", None, line_number or None
    return "PASS", None, None


def _guard_external_prediction_sequence(
    path: Path, expected_sequence: str, expected_rows: int
) -> tuple[str, str | None, int | None]:
    """Read a prediction row only after its first field proves discovery scope."""

    if not path.is_file():
        return "MISSING", None, None
    line_number = 0
    with path.open("rb", buffering=0) as stream:
        while True:
            first_field = bytearray()
            saw_any = False
            delimiter: bytes | None = None
            while True:
                byte = stream.read(1)
                if byte == b"":
                    break
                saw_any = True
                if byte in {b",", b"\n"}:
                    delimiter = byte
                    break
                if byte != b"\r":
                    first_field.extend(byte)
            if not saw_any:
                break
            line_number += 1
            try:
                token = first_field.decode("utf-8-sig").strip().strip('"')
            except UnicodeDecodeError:
                return "INVALID_ENCODING", None, line_number
            if line_number == 1:
                if token != "sequence":
                    return "SEQUENCE_NOT_FIRST", token, line_number
            elif token != expected_sequence:
                return "NON_DISCOVERY_SEQUENCE", token, line_number
            if delimiter == b",":
                while True:
                    byte = stream.read(1)
                    if byte in {b"", b"\n"}:
                        break
            if delimiter is None:
                break
    observed_rows = max(0, line_number - 1)
    if observed_rows != expected_rows:
        return "ROW_COUNT_MISMATCH", str(observed_rows), line_number or None
    return "PASS", None, None


def _read_unbuffered_csv_field(stream: Any) -> tuple[bytes, bytes | None, bool]:
    value = bytearray()
    quoted = False
    at_start = True
    while True:
        byte = stream.read(1)
        if byte == b"":
            return bytes(value), None, True
        if at_start and byte == b'"':
            quoted = True
            at_start = False
            continue
        at_start = False
        if quoted:
            if byte != b'"':
                value.extend(byte)
                continue
            following = stream.read(1)
            if following == b'"':
                value.extend(b'"')
                continue
            if following == b",":
                return bytes(value), b",", False
            if following == b"\r":
                following = stream.read(1)
            if following == b"\n":
                return bytes(value), b"\n", False
            if following == b"":
                return bytes(value), None, True
            return bytes(value), b"INVALID", False
        if byte == b",":
            return bytes(value), b",", False
        if byte == b"\n":
            if value.endswith(b"\r"):
                del value[-1]
            return bytes(value), b"\n", False
        value.extend(byte)


def _guard_discovery_identifier_column(
    path: Path,
    expected_header: Sequence[str],
    identifier_column: str,
    *,
    multi_value: bool,
) -> tuple[str, str | None, int | None]:
    """Guard a pair-ID column before reading any later outcome column."""

    header = _csv_header(path)
    if header is None:
        return "MISSING", None, None
    if header != tuple(expected_header):
        return "HEADER_MISMATCH", repr(header), 1
    target_index = header.index(identifier_column)
    with path.open("rb", buffering=0) as stream:
        while True:
            byte = stream.read(1)
            if byte in {b"", b"\n"}:
                break
        line_number = 1
        while True:
            fields: list[str] = []
            reached_eof = False
            delimiter: bytes | None = None
            for _ in range(target_index + 1):
                raw, delimiter, reached_eof = _read_unbuffered_csv_field(stream)
                if raw == b"" and reached_eof and not fields:
                    return "PASS", None, None
                if delimiter == b"INVALID":
                    return "INVALID_CSV_QUOTING", None, line_number + 1
                try:
                    fields.append(raw.decode("utf-8-sig"))
                except UnicodeDecodeError:
                    return "INVALID_ENCODING", None, line_number + 1
                if delimiter != b"," and len(fields) <= target_index:
                    return "TRUNCATED_ROW_BEFORE_PAIR_ID", None, line_number + 1
            line_number += 1
            identifiers = (
                [value for value in fields[target_index].split(";") if value]
                if multi_value else [fields[target_index]]
            )
            if not identifiers:
                return "EMPTY_PAIR_ID_SET", None, line_number
            for pair_id in identifiers:
                if pair_id in EXPECTED_HOLDOUT_IDS:
                    return "HOLDOUT_DETECTED_BEFORE_OUTCOME_READ", pair_id, line_number
                if pair_id not in EXPECTED_DISCOVERY_IDS:
                    return "NON_DISCOVERY_PAIR_ID", pair_id, line_number
            if delimiter == b",":
                while True:
                    byte = stream.read(1)
                    if byte in {b"", b"\n"}:
                        reached_eof = byte == b""
                        break
            if reached_eof:
                return "PASS", None, None


def _collect_external_from_json(
    document: Mapping[str, Any] | None, source_artifact: str
) -> list[ExternalEvidence]:
    if document is None:
        return []
    evidence: list[ExternalEvidence] = []

    def visit(value: object, context: str) -> None:
        if isinstance(value, Mapping):
            lowered = {str(key).lower(): key for key in value}
            for lower_key, original_key in lowered.items():
                child = value[original_key]
                if not isinstance(child, str) or "path" not in lower_key:
                    continue
                semantic = f"{context}.{lower_key}".lower()
                if not any(token in semantic for token in ("raw", "prediction", "log")):
                    continue
                if "dataset" in semantic or "checkpoint" in semantic or "config" in semantic:
                    continue
                derived_hash_candidates = (
                    lower_key.replace("_external_path", "_sha256"),
                    lower_key.replace("_path_external", "_sha256"),
                    lower_key.replace("_path", "_sha256"),
                )
                # str.replace returns the original key when its pattern is
                # absent.  Do not let that unchanged path key win before a
                # sibling `sha256` field in nested objects such as
                # {"path": ..., "sha256": ...}.
                hash_candidates = tuple(
                    candidate
                    for candidate in derived_hash_candidates
                    if candidate != lower_key
                ) + (
                    "sha256",
                    "external_raw_sha256",
                    "raw_mrm_sha256",
                    "prediction_sha256",
                )
                recorded: str | None = None
                for candidate in hash_candidates:
                    actual_key = lowered.get(candidate)
                    if actual_key is not None and isinstance(value[actual_key], str):
                        recorded = str(value[actual_key]).strip().lower() or None
                        break
                kind = "external_prediction" if "prediction" in semantic else "external_raw_log"
                evidence.append(
                    ExternalEvidence(source_artifact, kind, Path(child), recorded)
                )
            for key, child in value.items():
                visit(child, f"{context}.{key}" if context else str(key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, f"{context}[{index}]")

    visit(document, "")
    return evidence


def _collect_external_from_sequence_rows(
    rows: Sequence[Mapping[str, str]], source_artifact: str
) -> list[ExternalEvidence]:
    result: list[ExternalEvidence] = []
    for row in rows:
        path_text = str(row.get("prediction_path_external", "")).strip()
        if path_text:
            result.append(
                ExternalEvidence(
                    source_artifact,
                    "external_prediction",
                    Path(path_text),
                    str(row.get("prediction_sha256", "")).strip().lower() or None,
                )
            )
    return result


def _verify_external_evidence(
    evidence: Iterable[ExternalEvidence], external_root: Path
) -> list[ExternalVerification]:
    unique: dict[str, ExternalEvidence] = {}
    hash_conflicts: set[str] = set()
    for item in evidence:
        key = os.path.normcase(str(item.path.resolve()))
        previous = unique.get(key)
        if (
            previous is not None
            and previous.recorded_sha256
            and item.recorded_sha256
            and previous.recorded_sha256 != item.recorded_sha256
        ):
            hash_conflicts.add(key)
        if previous is None or (previous.recorded_sha256 is None and item.recorded_sha256):
            unique[key] = item

    verified: list[ExternalVerification] = []
    for item in sorted(unique.values(), key=lambda value: str(value.path).lower()):
        path = item.path.resolve()
        recorded = item.recorded_sha256
        normalized_key = os.path.normcase(str(path))
        if not _is_within(path, external_root):
            verified.append(
                ExternalVerification(
                    item.source_artifact, item.evidence_kind, str(path), None,
                    recorded, None, "OUTSIDE_DECLARED_EXTERNAL_ROOT",
                )
            )
            continue
        if not path.is_file():
            verified.append(
                ExternalVerification(
                    item.source_artifact, item.evidence_kind, str(path), None,
                    recorded, None, "MISSING",
                )
            )
            continue
        if item.evidence_kind == "external_raw_log":
            status = (
                "RECORDED_HASH_CONFLICT"
                if normalized_key in hash_conflicts
                else "HASH_NOT_RECORDED"
                if recorded is None
                else "RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE"
            )
            verified.append(
                ExternalVerification(
                    item.source_artifact, item.evidence_kind, str(path),
                    path.stat().st_size, recorded, None, status,
                )
            )
            continue
        observed = _sha256(path)
        if normalized_key in hash_conflicts:
            status = "RECORDED_HASH_CONFLICT"
        elif recorded is None:
            status = "HASH_NOT_RECORDED"
        elif observed != recorded:
            status = "HASH_MISMATCH"
        else:
            status = "VERIFIED"
        verified.append(
            ExternalVerification(
                item.source_artifact, item.evidence_kind, str(path),
                path.stat().st_size, recorded, observed, status,
            )
        )
    return verified


def _validate_refinement(
    document: Mapping[str, Any] | None, selected_path: str | None
) -> tuple[bool, list[str], dict[str, str]]:
    """Validate the one canonical, hash-bound bounded-refinement package."""

    if document is None:
        return False, ["REFINEMENT_INPUTS_ABSENT_AFTER_CRITERION_B_PASS"], {}

    issues: list[str] = []
    component_status: dict[str, str] = {}
    if document.get("schema_version") != REFINEMENT_SCHEMA_VERSION:
        issues.append("REFINEMENT_SCHEMA_VERSION_MISMATCH")
    if document.get("status") != "BOUNDED_REFINEMENT_COMPLETE":
        issues.append("REFINEMENT_SUMMARY_STATUS_NOT_BOUNDED_REFINEMENT_COMPLETE")
    if _as_bool(document.get("refinement_executed")) is not True:
        issues.append("REFINEMENT_EXECUTED_TRUE_NOT_EXPLICIT")
    if not selected_path:
        issues.append("REFINEMENT_SELECTED_PATH_FROM_CRITERION_B_ABSENT")
    elif document.get("selected_refinement_path") != selected_path:
        issues.append(
            "REFINEMENT_SELECTED_PATH_MISMATCH: "
            f"analysis={selected_path}; refinement="
            f"{document.get('selected_refinement_path')!r}"
        )

    for key, expected in (
        ("discovery_pairs_executed", 12),
        ("discovery_intervals_executed", 24),
    ):
        observed = _as_int(document.get(key))
        if observed != expected:
            issues.append(f"REFINEMENT_{key.upper()}_NOT_{expected}: {observed!r}")
    for key in ("holdout_pairs_executed", "holdout_outcomes_read"):
        observed = _as_int(document.get(key))
        if observed is None:
            issues.append(f"REFINEMENT_{key.upper()}_MISSING_OR_MALFORMED")
        elif observed != 0:
            issues.append("REFINEMENT_REPORTS_NONZERO_HOLDOUT_EXECUTION_OR_ACCESS")
    if _as_bool(document.get("physical_skip")) is not False:
        issues.append("REFINEMENT_PHYSICAL_SKIP_FALSE_NOT_EXPLICIT")

    criterion_b_gate = document.get("criterion_b_gate")
    if not isinstance(criterion_b_gate, Mapping):
        issues.append("REFINEMENT_CRITERION_B_GATE_OBJECT_MISSING")
    elif (
        _as_bool(criterion_b_gate.get("pass")) is not True
        or criterion_b_gate.get("selected_refinement_path") != selected_path
    ):
        issues.append("REFINEMENT_CRITERION_B_GATE_MISMATCH")

    t3 = document.get("t3")
    if not isinstance(t3, Mapping):
        issues.append("REFINEMENT_T3_PROVENANCE_OBJECT_MISSING")
    else:
        config = str(t3.get("config", "")).replace("\\", "/")
        if not config.endswith("experiments/spiketrack/spiketrack_s256_t3.yaml"):
            issues.append("REFINEMENT_T3_CONFIG_NOT_EXACT_OR_NOT_RECORDED")
        if str(t3.get("checkpoint_sha256", "")).lower() != EXPECTED_T3_CHECKPOINT_SHA256:
            issues.append("REFINEMENT_T3_CHECKPOINT_SHA256_NOT_EXACT_OR_NOT_RECORDED")

    components = document.get("components")
    if not isinstance(components, Mapping):
        issues.append("REFINEMENT_COMPONENTS_OBJECT_MISSING")
        components = {}
    if {str(key) for key in components} != REFINEMENT_COMPONENT_KEYS:
        issues.append(
            "REFINEMENT_COMPONENT_KEY_SET_MISMATCH: "
            f"expected={sorted(REFINEMENT_COMPONENT_KEYS)}; "
            f"observed={sorted(str(key) for key in components)}"
        )
    for key in sorted(REFINEMENT_COMPONENT_KEYS):
        value = components.get(key)
        if not isinstance(value, Mapping):
            component_status[key] = "MISSING_OR_INVALID"
            issues.append(f"REFINEMENT_COMPONENT_INCOMPLETE: {key}")
            continue
        status = str(value.get("status", "")).upper()
        technical_blocker = str(value.get("technical_blocker", "")).strip()
        technically_unavailable = (
            key == "t3_selected_path_controls"
            and status == "NOT_TECHNICALLY_VALID"
            and bool(technical_blocker)
        )
        complete = status in {"PASS", "COMPLETE"}
        if not complete and not technically_unavailable:
            component_status[key] = "MISSING_OR_INCOMPLETE"
            issues.append(f"REFINEMENT_COMPONENT_INCOMPLETE: {key}")
            continue
        if value.get("selected_refinement_path") != selected_path:
            issues.append(f"REFINEMENT_COMPONENT_SELECTED_PATH_MISMATCH: {key}")
        if _as_bool(value.get("physical_skip")) is not False:
            issues.append(f"REFINEMENT_COMPONENT_PHYSICAL_SKIP_NOT_FALSE: {key}")
        if complete:
            if _as_int(value.get("discovery_pairs_executed")) != 12:
                issues.append(f"REFINEMENT_COMPONENT_PAIR_COUNT_NOT_12: {key}")
            if _as_int(value.get("discovery_intervals_executed")) != 24:
                issues.append(f"REFINEMENT_COMPONENT_INTERVAL_COUNT_NOT_24: {key}")
            if (
                key == "t3_selected_path_controls"
                and _as_int(value.get("controls_executed")) != 3
            ):
                issues.append("REFINEMENT_T3_SELECTED_CONTROL_COUNT_NOT_3")
            component_status[key] = "COMPLETE"
        else:
            if _as_int(value.get("controls_executed")) != 0:
                issues.append(
                    "REFINEMENT_T3_TECHNICAL_BLOCKER_CONTROL_COUNT_NOT_ZERO"
                )
            issues.append(
                "REFINEMENT_T3_TECHNICAL_INVALIDITY_NOT_MACHINE_VERIFIED"
            )
            component_status[key] = (
                f"TECHNICAL_BLOCKER_RECORDED: {technical_blocker}"
            )

    output_hashes = document.get("output_hashes")
    if not isinstance(output_hashes, Mapping):
        issues.append("REFINEMENT_OUTPUT_HASH_MAP_MISSING")
    elif {str(key) for key in output_hashes} != REFINEMENT_OUTPUT_HASH_KEYS:
        issues.append(
            "REFINEMENT_OUTPUT_HASH_KEY_SET_MISMATCH: "
            f"expected={sorted(REFINEMENT_OUTPUT_HASH_KEYS)}; "
            f"observed={sorted(str(key) for key in output_hashes)}"
        )

    raw_logs = document.get("external_raw_logs")
    if not isinstance(raw_logs, list) or len(raw_logs) < 2:
        issues.append("REFINEMENT_EXTERNAL_RAW_LOG_SET_MISSING_OR_INCOMPLETE")
    else:
        for index, item in enumerate(raw_logs):
            if (
                not isinstance(item, Mapping)
                or not str(item.get("path", "")).strip()
                or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", "")).lower())
            ):
                issues.append(f"REFINEMENT_EXTERNAL_RAW_LOG_INVALID: index={index}")

    return not issues, issues, component_status


def _validate_refinement_machine_outputs(
    artifact_root: Path,
    document: Mapping[str, Any],
    selected_path: str,
    frozen_rows_by_id: Mapping[str, Mapping[str, str]],
) -> list[str]:
    """Validate canonical bounded-refinement schemas and discovery coverage."""

    issues: list[str] = []

    def read_rows(name: str, required_columns: set[str]) -> list[dict[str, str]]:
        path = artifact_root / name
        if not path.is_file():
            issues.append(f"REFINEMENT_MACHINE_OUTPUT_MISSING: {name}")
            return []
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                header = tuple(reader.fieldnames or ())
                if not header or header[0] != "pair_id":
                    issues.append(f"REFINEMENT_PAIR_ID_NOT_FIRST: {name}")
                    return []
                if not required_columns.issubset(header):
                    issues.append(
                        f"REFINEMENT_MACHINE_HEADER_MISSING_COLUMNS: {name}: "
                        f"{sorted(required_columns - set(header))}"
                    )
                    return []
                return list(reader)
        except (OSError, UnicodeError, csv.Error) as exc:
            issues.append(f"REFINEMENT_MACHINE_OUTPUT_INVALID: {name}: {exc}")
            return []

    def validate_frame_rows(
        rows: Sequence[Mapping[str, str]], conditions: set[str], label: str
    ) -> None:
        observed: set[tuple[str, str, str, int]] = set()
        for row in rows:
            pair_id = str(row.get("pair_id", ""))
            side = str(row.get("side", ""))
            condition = str(row.get("condition", ""))
            frame_index = _as_int(row.get("frame_index"))
            iou = _as_float(row.get("iou"))
            iou_float = _as_float(row.get("iou_float"))
            failure = _as_bool(row.get("failure"))
            success = _as_bool(row.get("success_at_0_5"))
            center_error = _as_float(row.get("center_error"))
            initialization = _as_bool(row.get("initialization_frame"))
            evaluator_override = _as_bool(
                row.get("evaluator_first_frame_override")
            )
            float_values = tuple(
                _as_float(row.get(f"pred_{axis}_float")) for axis in "xywh"
            )
            int_values = tuple(
                _as_int(row.get(f"pred_{axis}_int")) for axis in "xywh"
            )
            gt_values = tuple(
                _as_float(row.get(f"gt_{axis}")) for axis in "xywh"
            )
            boxes_valid = (
                all(value is not None for value in float_values)
                and all(value is not None for value in int_values)
                and all(value is not None for value in gt_values)
            )
            float_box = tuple(
                float(value) for value in float_values if value is not None
            )
            int_box = tuple(int(value) for value in int_values if value is not None)
            gt_box = tuple(float(value) for value in gt_values if value is not None)
            recomputed_iou = _inclusive_iou(int_box, gt_box) if boxes_valid else None
            recomputed_iou_float = (
                _inclusive_iou(float_box, gt_box) if boxes_valid else None
            )
            recomputed_center = (
                _inclusive_center_error(int_box, gt_box) if boxes_valid else None
            )
            frozen = frozen_rows_by_id.get(pair_id)
            key = (condition, pair_id, side, frame_index or -1)
            valid = (
                frozen is not None
                and side in {"primary", "control"}
                and condition in conditions
                and frame_index is not None
                and row.get("sequence") == frozen.get(f"{side}_sequence")
                and int(frozen[f"{side}_start"]) <= frame_index
                <= int(frozen[f"{side}_end"])
                and row.get("selected_refinement_path") == selected_path
                and _as_bool(row.get("physical_skip")) is False
                and iou is not None
                and 0.0 <= iou <= 1.0
                and boxes_valid
                and tuple(int(value) for value in float_box) == int_box
                and recomputed_iou is not None
                and _numbers_close(iou, recomputed_iou)
                and recomputed_iou_float is not None
                and _numbers_close(iou_float, recomputed_iou_float)
                and recomputed_center is not None
                and _numbers_close(center_error, recomputed_center)
                and failure is (iou < 0.5)
                and success is (iou >= 0.5)
                and initialization is (frame_index == 1)
                and evaluator_override is initialization
                and key not in observed
            )
            if not valid:
                issues.append(
                    f"REFINEMENT_{label}_ROW_CONTRACT_MISMATCH: "
                    f"{condition}/{pair_id}/{side}/{frame_index}"
                )
                continue
            observed.add(key)
        expected = {
            (condition, pair_id, side, frame_index)
            for condition in conditions
            for pair_id in EXPECTED_DISCOVERY_IDS
            for side in ("primary", "control")
            for frame_index in range(
                int(frozen_rows_by_id[pair_id][f"{side}_start"]),
                int(frozen_rows_by_id[pair_id][f"{side}_end"]) + 1,
            )
        }
        if observed != expected or len(rows) != len(expected):
            issues.append(
                f"REFINEMENT_{label}_LOCKED_COVERAGE_MISMATCH: "
                f"expected={len(expected)}; rows={len(rows)}; keys={len(observed)}"
            )

    retriever_conditions = {"retriever_only_bypass", "mlp_only_bypass"}
    t3 = document.get("t3") if isinstance(document.get("t3"), Mapping) else {}
    selected_control_value = t3.get("selected_control_names")
    selected_control_names = (
        tuple(str(value) for value in selected_control_value)
        if isinstance(selected_control_value, (list, tuple)) else ()
    )
    if selected_control_names != T3_REFINEMENT_CONTROL_NAMES:
        issues.append("REFINEMENT_T3_SELECTED_CONTROL_NAME_SET_MISMATCH")
        selected_control_names = ()
    components = document.get("components")
    if not isinstance(components, Mapping):
        components = {}
    controls = components.get("t3_selected_path_controls") or {}
    if not isinstance(controls, Mapping):
        controls = {}
    controls_complete = str(controls.get("status", "")).upper() in {"PASS", "COMPLETE"}
    t3_conditions = {"t3_baseline"}
    if controls_complete:
        t3_conditions.update(str(value) for value in selected_control_names)

    common_frame_columns = {
        "pair_id", "side", "sequence", "frame_index", "condition",
        "selected_refinement_path", "iou", "iou_float", "failure",
        "success_at_0_5", "center_error", "physical_skip",
        "pred_x_float", "pred_y_float", "pred_w_float", "pred_h_float",
        "pred_x_int", "pred_y_int", "pred_w_int", "pred_h_int",
        "gt_x", "gt_y", "gt_w", "gt_h", "initialization_frame",
        "evaluator_first_frame_override",
    }
    retriever_rows = read_rows(
        "retriever_mlp_per_frame_metrics.csv", common_frame_columns
    )
    t3_rows = read_rows("t3_per_frame_metrics.csv", common_frame_columns)
    validate_frame_rows(retriever_rows, retriever_conditions, "RETRIEVER_MLP")
    validate_frame_rows(t3_rows, t3_conditions, "T3")

    manifest_rows = read_rows(
        "bounded_refinement_execution_manifest.csv",
        {
            "pair_id", "side", "sequence", "interval_start", "interval_end",
            "condition", "selected_refinement_path", "physical_skip", "status",
        },
    )
    manifest_conditions = retriever_conditions | t3_conditions
    observed_manifest: set[tuple[str, str, str]] = set()
    for row in manifest_rows:
        pair_id = str(row.get("pair_id", ""))
        side = str(row.get("side", ""))
        condition = str(row.get("condition", ""))
        frozen = frozen_rows_by_id.get(pair_id)
        key = (condition, pair_id, side)
        if (
            frozen is None
            or side not in {"primary", "control"}
            or condition not in manifest_conditions
            or row.get("sequence") != frozen.get(f"{side}_sequence")
            or row.get("interval_start") != frozen.get(f"{side}_start")
            or row.get("interval_end") != frozen.get(f"{side}_end")
            or row.get("selected_refinement_path") != selected_path
            or _as_bool(row.get("physical_skip")) is not False
            or not _status_is_complete(row.get("status"))
            or key in observed_manifest
        ):
            issues.append(
                f"REFINEMENT_MANIFEST_ROW_CONTRACT_MISMATCH: "
                f"{condition}/{pair_id}/{side}"
            )
            continue
        observed_manifest.add(key)
    expected_manifest = {
        (condition, pair_id, side)
        for condition in manifest_conditions
        for pair_id in EXPECTED_DISCOVERY_IDS
        for side in ("primary", "control")
    }
    if observed_manifest != expected_manifest or len(manifest_rows) != len(expected_manifest):
        issues.append(
            "REFINEMENT_MANIFEST_LOCKED_COVERAGE_MISMATCH: "
            f"expected={len(expected_manifest)}; rows={len(manifest_rows)}"
        )

    timing_path = artifact_root / "bounded_refinement_timing_characterization.csv"
    timing_rows: list[dict[str, str]] = []
    if not timing_path.is_file():
        issues.append("REFINEMENT_MACHINE_OUTPUT_MISSING: bounded_refinement_timing_characterization.csv")
    else:
        try:
            with timing_path.open("r", encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                required = {"condition", "frame_records", "physical_skip"}
                if not required.issubset(reader.fieldnames or ()):
                    issues.append("REFINEMENT_TIMING_HEADER_MISMATCH")
                else:
                    timing_rows = list(reader)
        except (OSError, UnicodeError, csv.Error) as exc:
            issues.append(f"REFINEMENT_TIMING_INVALID: {exc}")
    timing_conditions = {str(row.get("condition", "")) for row in timing_rows}
    if (
        not timing_rows
        or timing_conditions != manifest_conditions
        or any((_as_int(row.get("frame_records")) or 0) <= 0 for row in timing_rows)
        or any(_as_bool(row.get("physical_skip")) is not False for row in timing_rows)
    ):
        issues.append("REFINEMENT_TIMING_COVERAGE_OR_PHYSICAL_SKIP_MISMATCH")

    row_counts = document.get("row_counts")
    observed_counts = {
        "retriever_mlp_per_frame_metrics": len(retriever_rows),
        "t3_per_frame_metrics": len(t3_rows),
        "bounded_refinement_execution_manifest": len(manifest_rows),
        "bounded_refinement_timing_characterization": len(timing_rows),
    }
    if not isinstance(row_counts, Mapping) or {
        str(key) for key in row_counts
    } != set(observed_counts) or any(
        _as_int(row_counts.get(key)) != value
        for key, value in observed_counts.items()
    ):
        issues.append("REFINEMENT_ROW_COUNT_HASH_BOUND_CONTRACT_MISMATCH")
    return issues


def _timing_summary(
    path: Path,
) -> tuple[int, list[dict[str, object]], bool, bool]:
    if not path.is_file():
        return 0, [], True, False
    groups: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    group_record_counts: dict[tuple[str, str], list[int]] = defaultdict(list)
    physical_skip_all_false = True
    numeric_contract_valid = True
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        row_count = 0
        for row in reader:
            row_count += 1
            mode = row.get("mode") or row.get("ablation_control") or "baseline"
            module = row.get("mrm_id") or row.get("module") or "all"
            key = (str(mode), str(module))
            for column in (
                "retriever_latency_ms", "mlp_latency_ms",
                "total_mrm_compute_latency_ms", "total_instrumented_mrm_latency_ms",
            ):
                number = _as_float(row.get(column))
                if number is None:
                    number = _as_float(row.get(column.removesuffix("_ms") + "_mean_ms"))
                if number is not None and number >= 0:
                    groups[key][column].append(number)
                else:
                    numeric_contract_valid = False
            record_count = _as_int(row.get("frame_records"))
            if record_count is not None:
                group_record_counts[key].append(record_count)
            skip = _as_bool(row.get("physical_skip"))
            if skip is not False:
                physical_skip_all_false = False
    summary_rows: list[dict[str, object]] = []
    for (mode, module), values in sorted(groups.items()):
        summary_rows.append(
            {
                "mode": mode,
                "module": module,
                "n": (
                    sum(group_record_counts[(mode, module)])
                    if group_record_counts[(mode, module)]
                    else max((len(items) for items in values.values()), default=0)
                ),
                "retriever_mean_ms": (
                    statistics.fmean(values["retriever_latency_ms"])
                    if values["retriever_latency_ms"] else None
                ),
                "mlp_mean_ms": (
                    statistics.fmean(values["mlp_latency_ms"])
                    if values["mlp_latency_ms"] else None
                ),
                "compute_mean_ms": (
                    statistics.fmean(values["total_mrm_compute_latency_ms"])
                    if values["total_mrm_compute_latency_ms"] else None
                ),
                "instrumented_mean_ms": (
                    statistics.fmean(values["total_instrumented_mrm_latency_ms"])
                    if values["total_instrumented_mrm_latency_ms"] else None
                ),
            }
        )
    observed_keys = set(groups)
    if path.name == "module_timing_characterization.csv":
        expected_keys = {("none", f"MRM{index}") for index in range(1, 7)}
        coverage_valid = (
            row_count == 593 * 6
            and observed_keys == expected_keys
            and all(row["n"] == 593 for row in summary_rows)
        )
    elif path.name == "mode_module_timing_characterization.csv":
        expected_keys = {
            (mode, f"MRM{index}")
            for mode in LOCKED_MODES
            for index in range(1, 7)
        }
        coverage_valid = (
            row_count == len(LOCKED_MODES) * 6
            and observed_keys == expected_keys
            and all(row["n"] == 593 for row in summary_rows)
        )
    else:
        coverage_valid = False
    return (
        row_count,
        summary_rows,
        physical_skip_all_false,
        numeric_contract_valid and coverage_valid,
    )


def _copy_analysis_files(
    codex_root: Path,
    artifact_root: Path,
    blockers: list[str],
    *,
    permitted: bool,
) -> list[Path]:
    copied: list[Path] = []
    if not permitted:
        return copied
    for source_name, destination_name in ANALYSIS_COPY_MAP.items():
        source = codex_root / source_name
        if not source.is_file():
            blockers.append(f"MISSING_ANALYSIS_MACHINE_FILE: {source}")
            continue
        destination = artifact_root / destination_name
        _atomic_copy(source, destination)
        if _sha256(source) != _sha256(destination):
            blockers.append(f"ANALYSIS_COPY_HASH_MISMATCH: {source} -> {destination}")
        copied.append(destination)
    return copied


def _validate_analysis_output_hashes(
    analysis: Mapping[str, Any] | None,
    repo_root: Path,
    blockers: list[str],
) -> None:
    if analysis is None:
        return
    outputs = analysis.get("outputs")
    if not isinstance(outputs, Mapping):
        blockers.append("ANALYSIS_SUMMARY_OUTPUT_HASH_MAP_MISSING")
        return
    if set(str(key) for key in outputs) != set(ANALYSIS_OUTPUT_BASENAMES):
        blockers.append(
            "ANALYSIS_OUTPUT_KEY_SET_MISMATCH: "
            f"expected={sorted(ANALYSIS_OUTPUT_BASENAMES)}; "
            f"observed={sorted(str(key) for key in outputs)}"
        )
    for label, record in outputs.items():
        if not isinstance(record, Mapping):
            blockers.append(f"ANALYSIS_OUTPUT_RECORD_INVALID: {label}")
            continue
        path_text = record.get("path")
        recorded = str(record.get("sha256", "")).strip().lower()
        if not isinstance(path_text, str) or not path_text or not recorded:
            blockers.append(f"ANALYSIS_OUTPUT_PATH_OR_HASH_MISSING: {label}")
            continue
        path = Path(path_text).resolve()
        expected_basename = ANALYSIS_OUTPUT_BASENAMES.get(str(label))
        expected_path = (
            repo_root / "screening" / "codex" / expected_basename
            if expected_basename else None
        )
        if expected_path is None or path != expected_path.resolve():
            blockers.append(
                f"ANALYSIS_OUTPUT_CANONICAL_PATH_MISMATCH: {label}: "
                f"expected={expected_path}; observed={path}"
            )
            continue
        if not _is_within(path, repo_root):
            blockers.append(f"ANALYSIS_OUTPUT_OUTSIDE_REPOSITORY: {label}: {path}")
            continue
        if not path.is_file():
            blockers.append(f"ANALYSIS_OUTPUT_MISSING: {label}: {path}")
            continue
        observed = _sha256(path)
        if observed != recorded:
            blockers.append(
                f"ANALYSIS_OUTPUT_HASH_MISMATCH: {label}: "
                f"recorded={recorded}; observed={observed}"
            )


def _validate_analysis_input_hashes(
    analysis: Mapping[str, Any] | None,
    repo_root: Path,
    expected_baseline: Path,
    expected_mode: Path,
    criterion_b_was_run: bool,
    blockers: list[str],
) -> None:
    if analysis is None:
        return
    inputs = analysis.get("inputs")
    if not isinstance(inputs, Mapping):
        blockers.append("ANALYSIS_SUMMARY_INPUT_HASH_MAP_MISSING")
        return
    for key, expected, required in (
        ("baseline_csv", expected_baseline, True),
        ("mode_csv", expected_mode, criterion_b_was_run),
    ):
        record = inputs.get(key)
        if not isinstance(record, Mapping):
            if required:
                blockers.append(f"ANALYSIS_INPUT_RECORD_MISSING: {key}")
            continue
        path_text = record.get("path")
        recorded = str(record.get("sha256", "")).strip().lower()
        if not path_text:
            if required:
                blockers.append(f"ANALYSIS_INPUT_PATH_MISSING: {key}")
            continue
        path = Path(str(path_text)).resolve()
        if path != expected.resolve() or not _is_within(path, repo_root):
            blockers.append(
                f"ANALYSIS_INPUT_PATH_MISMATCH: {key}: "
                f"expected={expected.resolve()}; observed={path}"
            )
            continue
        if not path.is_file():
            blockers.append(f"ANALYSIS_INPUT_MISSING: {key}: {path}")
            continue
        observed = _sha256(path)
        if not recorded or observed != recorded:
            blockers.append(
                f"ANALYSIS_INPUT_HASH_MISMATCH: {key}: "
                f"recorded={recorded or 'NONE'}; observed={observed}"
            )


def _validate_execution_output_hashes(
    summary: Mapping[str, Any] | None,
    artifact_root: Path,
    blockers: list[str],
    *,
    require_map: bool,
    required_names: set[str] | None = None,
) -> None:
    if summary is None:
        return
    output_hashes = summary.get("output_hashes")
    if output_hashes is None:
        if require_map:
            blockers.append("EXECUTION_OUTPUT_HASH_MAP_MISSING")
        return
    if not isinstance(output_hashes, Mapping):
        blockers.append("EXECUTION_OUTPUT_HASH_MAP_INVALID")
        return
    observed_names = {str(name) for name in output_hashes}
    if required_names is not None and observed_names != required_names:
        blockers.append(
            "EXECUTION_OUTPUT_HASH_KEY_SET_MISMATCH: "
            f"expected={sorted(required_names)}; observed={sorted(observed_names)}"
        )
    for name, recorded_value in output_hashes.items():
        if Path(str(name)).name != str(name):
            blockers.append(f"EXECUTION_OUTPUT_HASH_KEY_NOT_BASENAME: {name}")
            continue
        path = artifact_root / str(name)
        recorded = str(recorded_value or "").strip().lower()
        if not path.is_file():
            blockers.append(f"EXECUTION_OUTPUT_MISSING: {path}")
            continue
        observed = _sha256(path)
        if not recorded or observed != recorded:
            blockers.append(
                f"EXECUTION_OUTPUT_HASH_MISMATCH: {path}; "
                f"recorded={recorded or 'NONE'}; observed={observed}"
            )


def _manifest_scope(path: Path, repo_root: Path, artifact_root: Path) -> str:
    if path.parent == artifact_root:
        name = path.name.lower()
        if "manifest" in name:
            return "stage4b_machine_manifest"
        if "parity" in name:
            return "stage4b_parity_evidence"
        if "timing" in name:
            return "stage4b_timing_characterization"
        if "per_frame" in name:
            return "stage4b_bounded_per_frame_metrics"
        if "summary" in name:
            return "stage4b_execution_or_analysis_summary"
        if any(token in name for token in ("criterion", "bootstrap", "holm", "pair_level")):
            return "stage4b_bounded_analysis_machine_file"
        return "stage4b_machine_artifact"
    relative = _repo_relative(path, repo_root)
    if relative.endswith("discovery_execution_report.md"):
        return "stage4b_execution_report"
    if "/scripts/" in f"/{relative}":
        return "stage4b_reproducibility_script"
    if "/patches/" in f"/{relative}":
        return "stage4b_diagnostic_patch"
    if relative.endswith("command_log.txt"):
        return "stage4b_command_log"
    if relative.endswith(".csv"):
        return "stage4b_required_or_analysis_csv"
    if relative.endswith(".json"):
        return "stage4b_analysis_summary"
    return "stage4b_repository_artifact"


def _repository_artifact_paths(
    repo_root: Path,
    codex_root: Path,
    artifact_root: Path,
    report_path: Path,
    *,
    exclude_outcome_files: bool,
    excluded_repository_paths: set[Path],
) -> set[Path]:
    manifest_path = artifact_root / "artifact_manifest.csv"
    repository_paths: set[Path] = set()

    def permitted(path: Path) -> bool:
        resolved = path.resolve()
        codex_root_file = resolved.parent == codex_root.resolve()
        artifact_member = _is_within(resolved, artifact_root)
        registered_location = (
            (not codex_root_file or path.name in REGISTERED_CODEX_ROOT_BASENAMES)
            and (
                not artifact_member
                or (
                    resolved.parent == artifact_root.resolve()
                    and path.name in REGISTERED_ARTIFACT_BASENAMES
                )
            )
        )
        reproducibility_source = any(
            _is_within(resolved, directory)
            for directory in (codex_root / "scripts", codex_root / "patches")
            if directory.is_dir()
        )
        return (
            resolved != manifest_path.resolve()
            and registered_location
            and resolved not in excluded_repository_paths
            and not (exclude_outcome_files and path.name in OUTCOME_BEARING_BASENAMES)
            and not (
                exclude_outcome_files
                and path.name not in SAFE_INVALID_MANIFEST_BASENAMES
                and not reproducibility_source
            )
        )

    for path in codex_root.glob(f"{DATE_PREFIX}*"):
        if path.is_file() and permitted(path):
            repository_paths.add(path.absolute())
    for directory in (codex_root / "scripts", codex_root / "patches"):
        if directory.is_dir():
            for path in directory.glob(f"{DATE_PREFIX}*"):
                if path.is_file() and permitted(path):
                    repository_paths.add(path.absolute())
    if artifact_root.is_dir():
        for path in artifact_root.rglob("*"):
            if path.is_file() and permitted(path):
                repository_paths.add(path.absolute())
    if permitted(report_path):
        repository_paths.add(report_path.absolute())
    return repository_paths


def _bounded_repository_artifact_issue(path: Path, repo_root: Path) -> str | None:
    if path.is_symlink():
        return "SYMLINK_NOT_ALLOWED"
    if not _is_within(path, repo_root):
        return "OUTSIDE_REPOSITORY"
    suffix = path.suffix.lower()
    if suffix in PROHIBITED_REPOSITORY_SUFFIXES:
        return f"PROHIBITED_SUFFIX_{suffix}"
    if suffix not in BOUNDED_REPOSITORY_SUFFIXES:
        return f"UNAPPROVED_SUFFIX_{suffix or 'NONE'}"
    if path.stat().st_size > MAX_BOUNDED_REPOSITORY_BYTES:
        return f"EXCEEDS_{MAX_BOUNDED_REPOSITORY_BYTES}_BYTES"
    return None


def _git_repository_state(path: Path, repo_root: Path) -> str:
    relative = _repo_relative(path, repo_root)
    try:
        tracked = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", "--", relative],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        ).returncode == 0
        if not tracked:
            return "UNTRACKED"
        staged = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--cached", "--quiet", "--", relative],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        ).returncode != 0
        unstaged = subprocess.run(
            ["git", "-C", str(repo_root), "diff", "--quiet", "--", relative],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        ).returncode != 0
    except OSError:
        return "GIT_STATE_UNAVAILABLE"
    if staged and unstaged:
        return "STAGED_AND_MODIFIED"
    if staged:
        return "STAGED"
    if unstaged:
        return "MODIFIED"
    return "COMMITTED"


def _write_artifact_manifest(
    repo_root: Path,
    codex_root: Path,
    artifact_root: Path,
    report_path: Path,
    external: Sequence[ExternalVerification],
    *,
    exclude_outcome_files: bool,
    excluded_repository_paths: set[Path],
) -> Path:
    manifest_path = artifact_root / "artifact_manifest.csv"
    repository_paths = _repository_artifact_paths(
        repo_root, codex_root, artifact_root, report_path,
        exclude_outcome_files=exclude_outcome_files,
        excluded_repository_paths=excluded_repository_paths,
    )

    rows: list[dict[str, object]] = []
    for path in sorted(repository_paths, key=lambda item: _repo_relative(item, repo_root)):
        if not path.is_file():
            continue
        if _bounded_repository_artifact_issue(path, repo_root) is not None:
            continue
        git_state = _git_repository_state(path, repo_root)
        rows.append(
            {
                "path": _repo_relative(path, repo_root),
                "scope": _manifest_scope(path, repo_root, artifact_root),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "committed_external": (
                    "COMMITTED" if git_state == "COMMITTED" else "COMMIT_CANDIDATE"
                ),
                "verification_status": (
                    f"HASH_VERIFIED_REPOSITORY_BOUNDED;GIT_STATE={git_state}"
                ),
            }
        )
    for item in external:
        rows.append(
            {
                "path": item.path,
                "scope": item.evidence_kind,
                "size_bytes": "" if item.size_bytes is None else item.size_bytes,
                "sha256": item.observed_sha256 or item.recorded_sha256 or "",
                "committed_external": "EXTERNAL",
                "verification_status": item.status,
            }
        )
    rows.sort(key=lambda row: (str(row["committed_external"]), str(row["path"]).lower()))
    _atomic_write_csv(
        manifest_path,
        (
            "path", "scope", "size_bytes", "sha256", "committed_external",
            "verification_status",
        ),
        rows,
    )
    return manifest_path


def finalize(repo_root: Path, external_root: Path) -> dict[str, object]:
    repo_root = repo_root.resolve()
    external_root = external_root.resolve()
    codex_root = repo_root / "screening" / "codex"
    artifact_root = codex_root / "artifacts" / "stage4B_discovery"
    report_path = codex_root / f"{DATE_PREFIX}discovery_execution_report.md"
    frozen_slice_path = (
        repo_root / "screening" / "manager" /
        "2026-08-25_stage4_spiketrack_diagnostic_slice.csv"
    )

    if not codex_root.is_dir() or not frozen_slice_path.is_file():
        raise FileNotFoundError(
            f"--repo-root is not the expected Q1_TrackingResearch checkout: {repo_root}"
        )

    blockers: list[str] = []
    limitations: list[str] = []
    invalid_reasons: list[str] = []
    if os.path.normcase(str(external_root)) != os.path.normcase(
        str(EXPECTED_EXTERNAL_ROOT.resolve())
    ):
        blockers.append(
            "EXTERNAL_ROOT_NOT_FROZEN_PROTOCOL_PATH: "
            f"expected={EXPECTED_EXTERNAL_ROOT.resolve()}; observed={external_root}"
        )
    e2_source_manifest = codex_root / "2026-08-25_stage4A_E2_otb_source_manifest.csv"
    if _sha256_if_file(e2_source_manifest) != EXPECTED_E2_SOURCE_MANIFEST_SHA256:
        blockers.append("CANONICAL_E2_SOURCE_MANIFEST_HASH_MISMATCH_OR_MISSING")

    provenance_path = artifact_root / "provenance_environment.json"
    parity_path = artifact_root / "no_ablation_parity.json"
    holdout_seal_path = artifact_root / "holdout_seal.csv"
    discovery_manifest_path = artifact_root / "discovery_execution_manifest.csv"
    sequence_path = artifact_root / "baseline_sequence_execution.csv"
    criterion_a_execution_path = artifact_root / "criterionA_execution_summary.json"
    criterion_b_execution_path = artifact_root / "criterionB_execution_summary.json"
    state_parity_path = artifact_root / "state_snapshot_parity.csv"
    mode_execution_path = artifact_root / "mode_execution_manifest.csv"
    baseline_metrics_path = artifact_root / "baseline_per_frame_metrics.csv"
    mode_metrics_path = artifact_root / "mode_per_frame_metrics.csv"
    analysis_summary_path = codex_root / f"{DATE_PREFIX}analysis_summary.json"

    provenance = _load_json(
        provenance_path, blockers, "PROVENANCE_ENVIRONMENT", required=True
    )
    parity = _load_json(parity_path, blockers, "NO_ABLATION_PARITY", required=True)
    criterion_a_execution = _load_json(
        criterion_a_execution_path, blockers, "CRITERION_A_EXECUTION_SUMMARY",
        required=True,
    )
    analysis = _load_json(
        analysis_summary_path, blockers, "FINAL_ANALYSIS_SUMMARY", required=True
    )
    _require_mapping_children(
        analysis,
        (
            "analysis_contract", "inputs", "outputs", "frozen_boundary",
            "criterion_a", "criterion_b", "non_claims",
        ),
        blockers,
        "ANALYSIS",
    )
    _require_mapping_children(
        provenance,
        (
            "environment", "no_ablation_parity", "patched_file_sha256",
            "accepted_nonmutating_discovery_aliases",
        ),
        blockers,
        "PROVENANCE",
    )
    if provenance is not None:
        environment_value = provenance.get("environment")
        if isinstance(environment_value, dict):
            _require_mapping_children(
                environment_value,
                ("packages", "deterministic_settings"),
                blockers,
                "ENVIRONMENT",
            )
    _validate_environment(provenance, blockers)
    if analysis is not None:
        if analysis.get("schema_version") != "stage4b-analysis-v1":
            blockers.append("ANALYSIS_SCHEMA_VERSION_MISMATCH")
        non_claims = analysis.get("non_claims") or {}
        expected_non_claims = {
            "diag_pass_fail_assigned": False,
            "stage4c_unlocked": False,
            "s1_s7_started": False,
            "primary_shortlist": None,
            "main_baseline": None,
            "proposed_architecture": None,
        }
        if any(non_claims.get(key) is not expected
               for key, expected in expected_non_claims.items()):
            blockers.append("ANALYSIS_NONCLAIM_BOUNDARY_MISMATCH")
        reported_conclusion = analysis.get("stage4b_conclusion")
        if reported_conclusion not in {
            None,
            "STAGE4B_CRITERION_A_FAIL",
            "STAGE4B_CRITERION_B_FAIL",
            INVALID_HOLDOUT,
        }:
            blockers.append(
                f"ANALYSIS_PREMATURE_OR_DISALLOWED_CONCLUSION: {reported_conclusion}"
            )

    criterion_a_status = str(
        ((analysis or {}).get("criterion_a") or {}).get("status", "NOT_COMPLETED")
    ).upper()
    criterion_a_pass = ((analysis or {}).get("criterion_a") or {}).get("pass") is True
    criterion_a_fail = (
        ((analysis or {}).get("criterion_a") or {}).get("pass") is False
        and criterion_a_status == "FAIL"
    )
    declared_criterion_a_pass = criterion_a_pass
    criterion_b_status = str(
        ((analysis or {}).get("criterion_b") or {}).get("status", "NOT_RUN")
    ).upper()
    criterion_b_pass_value = ((analysis or {}).get("criterion_b") or {}).get("pass")
    criterion_b_pass = criterion_b_pass_value is True
    criterion_b_fail = criterion_b_pass_value is False and criterion_b_status == "FAIL"
    criterion_b_was_run = criterion_b_pass_value is not None
    declared_criterion_b_was_run = criterion_b_was_run

    criterion_b_execution = _load_json(
        criterion_b_execution_path, blockers, "CRITERION_B_EXECUTION_SUMMARY",
        required=criterion_a_pass,
    )
    _require_mapping_children(
        criterion_b_execution,
        (
            "criterion_a_gate", "state_snapshot_parity", "baseline_branch_parity",
            "row_counts", "input_hashes", "determinism", "external_raw_mrm",
            "output_hashes",
        ),
        blockers,
        "CRITERION_B_EXECUTION",
    )
    for document, expected_keys, label in (
        (provenance, PROVENANCE_TOP_LEVEL_KEYS, "PROVENANCE"),
        (parity, PARITY_TOP_LEVEL_KEYS, "PARITY"),
        (
            criterion_a_execution, CRITERION_A_EXECUTION_TOP_LEVEL_KEYS,
            "CRITERION_A_EXECUTION",
        ),
        (
            criterion_b_execution, CRITERION_B_EXECUTION_TOP_LEVEL_KEYS,
            "CRITERION_B_EXECUTION",
        ),
        (analysis, ANALYSIS_TOP_LEVEL_KEYS, "ANALYSIS"),
    ):
        _require_exact_json_keys(document, expected_keys, blockers, label)
    for label, document in (
        ("PROVENANCE", provenance),
        ("PARITY", parity),
        ("CRITERION_A_EXECUTION", criterion_a_execution),
        ("CRITERION_B_EXECUTION", criterion_b_execution),
        ("ANALYSIS", analysis),
    ):
        for signal in _json_holdout_outcome_signals(document):
            invalid_reasons.append(
                f"{label}_HOLDOUT_OUTCOME_STRUCTURE_DETECTED: {signal}"
            )
    if criterion_a_fail and (
        any(
            path.is_file()
            for path in (
                state_parity_path,
                mode_metrics_path,
                mode_execution_path,
                artifact_root / "mode_module_timing_characterization.csv",
            )
        )
        or "EXECUTION_COMPLETE" in str(
            (criterion_b_execution or {}).get("status", "")
        ).upper()
    ):
        blockers.append("CRITERION_B_EXECUTION_ARTIFACT_PRESENT_AFTER_CRITERION_A_FAIL")

    # Guard discovery-only per-frame inputs before any whole-file hash, copy, or
    # statistical-table read in this reporting lane.
    guarded_inputs = [(baseline_metrics_path, "BASELINE_PER_FRAME", True)]
    distractor_margin_path = artifact_root / "distractor_margin_evidence.csv"
    if distractor_margin_path.is_file():
        guarded_inputs.append(
            (distractor_margin_path, "DISTRACTOR_MARGIN_EVIDENCE", False)
        )
    if criterion_a_pass or criterion_b_was_run:
        guarded_inputs.extend(
            (
                (mode_metrics_path, "MODE_PER_FRAME", True),
                (state_parity_path, "STATE_SNAPSHOT_PARITY", True),
                (mode_execution_path, "MODE_EXECUTION_MANIFEST", True),
            )
        )
    for path, label, required in guarded_inputs:
        guard_status, pair_id, line_number = _guard_discovery_first_field(path)
        if guard_status == "MISSING":
            if required:
                blockers.append(f"MISSING_{label}: {path}")
        elif guard_status == "HOLDOUT_DETECTED_BEFORE_OUTCOME_READ":
            invalid_reasons.append(
                f"{label}: sealed {pair_id} at line {line_number}; outcome fields not read"
            )
        elif guard_status != "PASS":
            blockers.append(
                f"INVALID_{label}_PAIR_GUARD: {guard_status}; value={pair_id}; "
                f"line={line_number}"
            )

    analysis_boundary = (analysis or {}).get("frozen_boundary") or {}
    if (analysis or {}).get("stage4b_conclusion") == INVALID_HOLDOUT:
        invalid_reasons.append("analysis summary reports invalid hold-out exposure")
    if str(analysis_boundary.get("validation", "")).upper() == "FAIL":
        invalid_reasons.append("analysis frozen-boundary validation is FAIL")
    for key in ("holdout_outcomes_read", "holdout_pairs_present_in_outcome_inputs"):
        _require_zero_count(
            analysis_boundary if isinstance(analysis_boundary, Mapping) else None,
            key, "ANALYSIS", blockers, invalid_reasons,
        )
    for label, summary in (
        ("criterionA", criterion_a_execution),
        ("criterionB", criterion_b_execution),
        ("provenance", provenance),
    ):
        if summary is None:
            continue
        counts = _deep_values_for_key(
            summary, re.compile(r"holdout.*(executed|outcomes?.*read)", re.I)
        )
        for value in counts:
            count = _as_int(value)
            if count is not None and count > 0:
                invalid_reasons.append(f"{label} reports hold-out execution/access={count}")

    frozen_sha = _normalized_lf_sha256(frozen_slice_path)
    frozen_row_hashes, frozen_pair_order, frozen_rows_by_id = (
        _canonical_slice_row_hashes(frozen_slice_path)
    )
    frozen_pair_contract_pass = (
        frozen_pair_order == EXPECTED_DISCOVERY_IDS + EXPECTED_HOLDOUT_IDS
    )
    frozen_boundary_pass = (
        frozen_sha == EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256
        and frozen_pair_contract_pass
    )
    if not frozen_boundary_pass:
        blockers.append(
            "FROZEN_SLICE_HASH_OR_PAIR_CONTRACT_MISMATCH: "
            f"expected={EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256}; observed={frozen_sha}"
        )
    if provenance:
        if provenance.get("scope") != "STAGE4B_DISCOVERY_CRITERION_A_ONLY":
            blockers.append("PROVENANCE_SCOPE_MISMATCH")
        dataset_root = Path(str(provenance.get("dataset_root", ""))).resolve()
        if os.path.normcase(str(dataset_root)) != os.path.normcase(
            str(EXPECTED_DATASET_ROOT.resolve())
        ):
            blockers.append(
                "PROVENANCE_DATASET_ROOT_NOT_CANONICAL_FIGSHARE_OTB2015: "
                f"{dataset_root}"
            )
        if provenance.get("source_sha") != EXPECTED_SOURCE_SHA:
            blockers.append(
                f"SOURCE_SHA_MISMATCH: expected={EXPECTED_SOURCE_SHA}; "
                f"observed={provenance.get('source_sha')}"
            )
        expected_source_root = (external_root / "SpikeTrack_pinned").resolve()
        if Path(str(provenance.get("source_root", ""))).resolve() != expected_source_root:
            blockers.append("PROVENANCE_PINNED_SOURCE_ROOT_MISMATCH")
        if provenance.get("checkpoint_sha256") != EXPECTED_CHECKPOINT_SHA256:
            blockers.append("CHECKPOINT_SHA256_MISMATCH")
        config_text = str(provenance.get("config", "")).replace("\\", "/")
        if not config_text.endswith("experiments/spiketrack/spiketrack_s256_t1.yaml"):
            blockers.append(f"T1_CONFIG_PATH_MISMATCH: {provenance.get('config')}")
        if Path(str(provenance.get("config", ""))).resolve() != (
            expected_source_root / "experiments" / "spiketrack"
            / "spiketrack_s256_t1.yaml"
        ).resolve():
            blockers.append("T1_CONFIG_CANONICAL_PATH_MISMATCH")
        if provenance.get("config_sha256") != EXPECTED_T1_CONFIG_SHA256:
            blockers.append("T1_CONFIG_SHA256_MISMATCH")
        if provenance.get("frozen_slice_sha256_canonical_lf") != frozen_sha:
            blockers.append("PROVENANCE_FROZEN_SLICE_HASH_MISMATCH")
        if Path(str(provenance.get("frozen_slice", ""))).resolve() != (
            frozen_slice_path.resolve()
        ):
            blockers.append("PROVENANCE_FROZEN_SLICE_PATH_MISMATCH")
        if provenance.get("patch_sha256_canonical_lf") != EXPECTED_PATCH_SHA256_CANONICAL_LF:
            blockers.append("PATCH_SHA256_MISMATCH")
        if provenance.get("patch_apply_result") != EXPECTED_PATCH_APPLY_RESULT:
            blockers.append(
                f"PATCH_APPLICATION_NOT_PASS: {provenance.get('patch_apply_result')}"
            )
        if _as_sequence_tuple(provenance.get("patched_paths")) != tuple(
            EXPECTED_PATCHED_FILE_SHA256
        ):
            blockers.append("PATCHED_PATH_SET_OR_ORDER_MISMATCH")
        if provenance.get("patched_file_sha256") != EXPECTED_PATCHED_FILE_SHA256:
            blockers.append("PATCHED_FILE_SHA256_MAP_MISMATCH")
        if _as_sequence_tuple(provenance.get("discovery_pair_ids")) != EXPECTED_DISCOVERY_IDS:
            blockers.append("PROVENANCE_DISCOVERY_PAIR_ID_SET_OR_ORDER_MISMATCH")
        if _as_int(provenance.get("discovery_pair_count")) != 12:
            blockers.append("PROVENANCE_DISCOVERY_PAIR_COUNT_NOT_12")
        if _as_sequence_tuple(provenance.get("holdout_pair_ids_metadata_only")) != (
            EXPECTED_HOLDOUT_IDS
        ):
            blockers.append("PROVENANCE_HOLDOUT_METADATA_ID_SET_OR_ORDER_MISMATCH")
        if _as_int(provenance.get("holdout_pair_count")) != 8:
            blockers.append("PROVENANCE_HOLDOUT_METADATA_COUNT_NOT_8")
        if provenance.get("accepted_nonmutating_discovery_aliases") != (
            EXPECTED_DISCOVERY_SOURCE_ALIASES
        ):
            blockers.append("PROVENANCE_DISCOVERY_ALIAS_MAP_MISMATCH")
        if provenance.get("no_ablation_parity") != parity:
            blockers.append("PROVENANCE_AND_PARITY_ARTIFACT_DISAGREE")
        _require_zero_count(
            provenance, "holdout_pairs_executed", "PROVENANCE",
            blockers, invalid_reasons,
        )

    holdout_header = _csv_header(holdout_seal_path)
    if holdout_header != HOLDOUT_SEAL_FIELDS:
        blockers.append(
            "HOLDOUT_SEAL_HEADER_MISMATCH: "
            f"expected={HOLDOUT_SEAL_FIELDS}; observed={holdout_header}"
        )
        # Do not consume any data row when a seal contains an unapproved field.
        holdout_rows: list[dict[str, str]] = []
    else:
        holdout_rows = _load_csv(
            holdout_seal_path, blockers, "HOLDOUT_SEAL", required=True
        )
    holdout_ids = tuple(row.get("pair_id", "") for row in holdout_rows)
    holdout_seal_pass = (
        holdout_ids == EXPECTED_HOLDOUT_IDS
        and all(row.get("status") == "NOT_EXECUTED_STAGE4B" for row in holdout_rows)
        and all(
            row.get("frozen_slice_sha256_canonical_lf") == frozen_sha
            for row in holdout_rows
        )
        and all(
            row.get("row_sha256_canonical_lf")
            == frozen_row_hashes.get(row.get("pair_id", ""))
            for row in holdout_rows
        )
        and all(
            all(
                row.get(field) == frozen_rows_by_id[row["pair_id"]].get(field)
                for field in (
                    "primary_sequence", "primary_start", "primary_end",
                    "control_sequence", "control_start", "control_end",
                )
            )
            for row in holdout_rows
        )
    )
    if not holdout_seal_pass:
        blockers.append("HOLDOUT_SEAL_VALIDATION_FAIL")

    discovery_header = _csv_header(discovery_manifest_path)
    if discovery_header != DISCOVERY_MANIFEST_FIELDS:
        blockers.append(
            "DISCOVERY_EXECUTION_MANIFEST_HEADER_MISMATCH: "
            f"expected={DISCOVERY_MANIFEST_FIELDS}; observed={discovery_header}"
        )
        discovery_rows: list[dict[str, str]] = []
    else:
        discovery_rows = _load_csv(
            discovery_manifest_path, blockers, "DISCOVERY_EXECUTION_MANIFEST",
            required=True,
        )
    discovery_ids = {row.get("pair_id", "") for row in discovery_rows}
    if discovery_ids & set(EXPECTED_HOLDOUT_IDS):
        invalid_reasons.append("discovery execution manifest contains a sealed hold-out ID")
    manifest_pairs_pass = (
        discovery_ids == set(EXPECTED_DISCOVERY_IDS)
        and len(discovery_rows) == 24
        and {
            (row.get("pair_id", ""), row.get("side", "")) for row in discovery_rows
        }
        == {
            (pair_id, side)
            for pair_id in EXPECTED_DISCOVERY_IDS
            for side in ("primary", "control")
        }
        and all(row.get("side") in {"primary", "control"} for row in discovery_rows)
        and all(
            row.get("source_row_sha256_canonical_lf")
            == frozen_row_hashes.get(row.get("pair_id", ""))
            for row in discovery_rows
        )
        and all(
            row.get("sequence")
            == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_sequence"]
            and row.get("start")
            == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_start"]
            and row.get("end")
            == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_end"]
            and row.get("event_id")
            == frozen_rows_by_id[row["pair_id"]][
                "primary_event_id" if row["side"] == "primary" else "control_id"
            ]
            and row.get("status") == "EXECUTED_STAGE4B_CRITERION_A"
            for row in discovery_rows
        )
    )
    if not manifest_pairs_pass:
        blockers.append(
            f"DISCOVERY_EXECUTION_MANIFEST_FAIL: rows={len(discovery_rows)}; "
            f"pair_ids={sorted(discovery_ids)}"
        )

    sequence_header = _csv_header(sequence_path)
    if sequence_header != BASELINE_SEQUENCE_FIELDS:
        blockers.append(
            "BASELINE_SEQUENCE_EXECUTION_HEADER_MISMATCH: "
            f"expected={BASELINE_SEQUENCE_FIELDS}; observed={sequence_header}"
        )
        sequence_rows: list[dict[str, str]] = []
    else:
        sequence_rows = _load_csv(
            sequence_path, blockers, "BASELINE_SEQUENCE_EXECUTION", required=True
        )
    expected_sequences = {row.get("sequence", "") for row in discovery_rows}
    sequence_names = {row.get("sequence", "") for row in sequence_rows}
    sequence_contract_pass = (
        bool(sequence_rows)
        and len(sequence_rows) == len(expected_sequences)
        and sequence_names == expected_sequences
        and len(sequence_names) == len(sequence_rows)
        and all(_as_bool(row.get("initialized_once_from_official_start")) is True
                for row in sequence_rows)
        and all(_as_int(row.get("official_start_frame")) == 1 for row in sequence_rows)
        and all(
            _as_int(row.get("executed_through_frame"))
            == max(
                int(interval["end"])
                for interval in discovery_rows
                if interval["sequence"] == row["sequence"]
            )
            for row in sequence_rows
        )
        and all(
            _as_int(row.get("frames_processed_including_initialization"))
            == _as_int(row.get("executed_through_frame"))
            for row in sequence_rows
        )
        and all(bool(row.get("prediction_path_external")) for row in sequence_rows)
        and all(
            bool(re.fullmatch(r"[0-9a-f]{64}", row.get("prediction_sha256", "")))
            for row in sequence_rows
        )
        and all((_as_float(row.get("elapsed_seconds_excluding_initialization")) or 0) > 0
                for row in sequence_rows)
        and all(str(row.get("status", "")).upper() == "COMPLETE" for row in sequence_rows)
    )
    if not sequence_contract_pass:
        blockers.append("BASELINE_SEQUENCE_CONTRACT_VALIDATION_FAIL")

    parity_max_diff = _as_float((parity or {}).get("maximum_observed_abs_diff"))
    parity_tolerance = _as_float((parity or {}).get("tolerance"))
    baseline_fingerprints = (parity or {}).get("baseline_output_fingerprints")
    instrumented_fingerprints = (
        (parity or {}).get("instrumented_output_fingerprints")
    )
    parity_pass = (
        parity is not None
        and _status_is_pass(parity.get("status"))
        and parity_max_diff is not None
        and 0.0 <= parity_max_diff <= PARITY_TOLERANCE
        and parity_tolerance is not None
        and parity_tolerance == PARITY_TOLERANCE
        and parity.get("source_sha") == EXPECTED_SOURCE_SHA
        and isinstance(baseline_fingerprints, Mapping)
        and bool(baseline_fingerprints)
        and baseline_fingerprints == instrumented_fingerprints
    )
    if not parity_pass:
        blockers.append("NO_ABLATION_PARITY_FAIL_OR_INCOMPLETE")

    criterion_a_rows: list[dict[str, str]] = []
    criterion_b_rows: list[dict[str, str]] = []
    sensitivity_rows: list[dict[str, str]] = []
    bootstrap_rows: list[dict[str, str]] = []
    holm_rows: list[dict[str, str]] = []
    pair_a_rows: list[dict[str, str]] = []
    pair_b_rows: list[dict[str, str]] = []
    copied_analysis_paths: list[Path] = []
    for path, header, identifier_column, multi_value, label in (
        (
            codex_root / f"{DATE_PREFIX}pair_level_A.csv", PAIR_A_FIELDS,
            "pair_id", False, "PAIR_LEVEL_A",
        ),
        (
            codex_root / f"{DATE_PREFIX}pair_level_B.csv", PAIR_B_FIELDS,
            "pair_id", False, "PAIR_LEVEL_B",
        ),
        (
            codex_root / f"{DATE_PREFIX}sensitivity_results.csv", SENSITIVITY_FIELDS,
            "pair_ids", True, "SENSITIVITY_RESULTS",
        ),
    ):
        guard_status, pair_id, line_number = _guard_discovery_identifier_column(
            path, header, identifier_column, multi_value=multi_value
        )
        if guard_status == "HOLDOUT_DETECTED_BEFORE_OUTCOME_READ":
            invalid_reasons.append(
                f"{label}: sealed {pair_id} at line {line_number}; outcome fields not read"
            )
        elif guard_status != "PASS":
            blockers.append(
                f"INVALID_{label}_DISCOVERY_GUARD: {guard_status}; "
                f"value={pair_id}; line={line_number}"
            )
    if not invalid_reasons:
        _validate_analysis_input_hashes(
            analysis, repo_root, baseline_metrics_path, mode_metrics_path,
            criterion_b_was_run, blockers,
        )
        _validate_analysis_output_hashes(analysis, repo_root, blockers)
        validate_b_execution_outputs = (
            criterion_b_execution is not None
            and criterion_a_pass
            and criterion_b_was_run
        )
        _validate_execution_output_hashes(
            criterion_b_execution if validate_b_execution_outputs else None,
            artifact_root, blockers,
            require_map=validate_b_execution_outputs,
            required_names=(
                CRITERION_B_OUTPUT_HASH_KEYS
                if validate_b_execution_outputs else None
            ),
        )
        copied_analysis_paths = _copy_analysis_files(
            codex_root, artifact_root, blockers, permitted=True
        )
        criterion_a_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}criterionA_results.csv", CRITERION_A_FIELDS,
            blockers, "CRITERION_A_RESULTS", required=True,
        )
        criterion_b_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}criterionB_results.csv", CRITERION_B_FIELDS,
            blockers, "CRITERION_B_RESULTS", required=True,
        )
        sensitivity_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}sensitivity_results.csv", SENSITIVITY_FIELDS,
            blockers, "SENSITIVITY_RESULTS", required=True,
        )
        bootstrap_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}bootstrap_results.csv", BOOTSTRAP_FIELDS,
            blockers, "BOOTSTRAP_RESULTS", required=True,
        )
        holm_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}holm_adjusted_tests.csv", HOLM_FIELDS,
            blockers, "HOLM_RESULTS", required=True,
        )
        pair_a_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}pair_level_A.csv", PAIR_A_FIELDS,
            blockers, "PAIR_LEVEL_A", required=True,
        )
        pair_b_rows = _load_exact_csv(
            codex_root / f"{DATE_PREFIX}pair_level_B.csv", PAIR_B_FIELDS,
            blockers, "PAIR_LEVEL_B", required=True,
        )

    if not invalid_reasons and (len(criterion_a_rows) != 2 or len(pair_a_rows) != 12):
        blockers.append(
            f"CRITERION_A_TABLE_COMPLETENESS_FAIL: result_rows={len(criterion_a_rows)}; "
            f"pair_rows={len(pair_a_rows)}"
        )
    elif not invalid_reasons and any(
        _as_bool(row.get("criterion_a_pass")) is not criterion_a_pass
        for row in criterion_a_rows
    ):
        blockers.append("CRITERION_A_SUMMARY_AND_RESULT_TABLE_DISAGREE")
    if not invalid_reasons and len(pair_a_rows) == 12:
        for row in pair_a_rows:
            pair_id = row.get("pair_id", "")
            frozen = frozen_rows_by_id.get(pair_id)
            if frozen is None or any(
                row.get(field) != frozen.get(field)
                for field in (
                    "primary_sequence", "primary_start", "primary_end",
                    "control_sequence", "control_start", "control_end",
                    "broad_superclass", "sensitivity_stratum",
                )
            ) or row.get("final_ambiguity_level") != frozen.get("final_ambiguity_level"):
                blockers.append(f"PAIR_LEVEL_A_FROZEN_METADATA_MISMATCH: {pair_id}")

    expected_a_sensitivity = {
        (dimension, group, metric)
        for dimension, group in LOCKED_SENSITIVITY_GROUPS
        for metric in ("iou_weakness", "failure_weakness")
    }
    observed_a_sensitivity = {
        (
            row.get("sensitivity_dimension", ""),
            row.get("sensitivity_group", ""),
            row.get("metric_or_mode", ""),
        )
        for row in sensitivity_rows
        if row.get("analysis_family") == "CRITERION_A"
    }
    if not invalid_reasons and observed_a_sensitivity != expected_a_sensitivity:
        blockers.append(
            "CRITERION_A_LOCKED_SENSITIVITY_COVERAGE_FAIL: "
            f"expected={len(expected_a_sensitivity)}; observed={len(observed_a_sensitivity)}"
        )

    criterion_b_tables_pass = True
    if criterion_b_rows and not invalid_reasons:
        modes = tuple(row.get("mode", "") for row in criterion_b_rows)
        criterion_b_tables_pass = (
            modes == LOCKED_MODES
            and len(holm_rows) == 9
            and len(pair_b_rows) == 9 * 12
            and all(_as_bool(row.get("physical_skip")) is False for row in criterion_b_rows)
            and all(_as_int(row.get("family_size")) == 9 for row in holm_rows)
        )
        if not criterion_b_tables_pass:
            blockers.append(
                "CRITERION_B_NINE_TEST_COMPLETENESS_FAIL: "
                f"modes={modes}; holm_rows={len(holm_rows)}; pair_rows={len(pair_b_rows)}"
            )
        for row in pair_b_rows:
            pair_id = row.get("pair_id", "")
            frozen = frozen_rows_by_id.get(pair_id)
            if frozen is None or any(
                row.get(field) != frozen.get(field)
                for field in (
                    "primary_sequence", "control_sequence", "broad_superclass",
                    "sensitivity_stratum",
                )
            ) or row.get("final_ambiguity_level") != frozen.get("final_ambiguity_level"):
                blockers.append(
                    f"PAIR_LEVEL_B_FROZEN_METADATA_MISMATCH: "
                    f"{row.get('mode')}/{pair_id}"
                )
        if any(
            _as_bool(row.get("criterion_b_pass")) is not criterion_b_pass
            for row in criterion_b_rows
        ):
            blockers.append("CRITERION_B_SUMMARY_AND_RESULT_TABLE_DISAGREE")
        expected_b_sensitivity = {
            (dimension, group, mode)
            for dimension, group in LOCKED_SENSITIVITY_GROUPS
            for mode in LOCKED_MODES
        }
        observed_b_sensitivity = {
            (
                row.get("sensitivity_dimension", ""),
                row.get("sensitivity_group", ""),
                row.get("metric_or_mode", ""),
            )
            for row in sensitivity_rows
            if row.get("analysis_family") == "CRITERION_B"
        }
        if observed_b_sensitivity != expected_b_sensitivity:
            blockers.append(
                "CRITERION_B_LOCKED_SENSITIVITY_COVERAGE_FAIL: "
                f"expected={len(expected_b_sensitivity)}; "
                f"observed={len(observed_b_sensitivity)}"
            )
    elif (
        not invalid_reasons
        and criterion_a_fail
        and (criterion_b_rows or holm_rows or pair_b_rows)
    ):
        blockers.append("CRITERION_B_DATA_PRESENT_AFTER_CRITERION_A_FAIL")

    if invalid_reasons:
        derived_a, derived_b, derived_selected_path = None, None, None
    else:
        derived_a, derived_b, derived_selected_path = _validate_locked_statistics(
            analysis, criterion_a_rows, criterion_b_rows, pair_a_rows, pair_b_rows,
            bootstrap_rows, holm_rows, blockers,
        )
        criterion_a_pass = derived_a is True
        criterion_a_fail = derived_a is False
        criterion_b_was_run = derived_b is not None
        criterion_b_pass = derived_b is True
        criterion_b_fail = derived_b is False
    selected_path = derived_selected_path
    if criterion_a_pass and not declared_criterion_a_pass:
        for path, label in (
            (mode_metrics_path, "MODE_PER_FRAME"),
            (state_parity_path, "STATE_SNAPSHOT_PARITY"),
            (mode_execution_path, "MODE_EXECUTION_MANIFEST"),
        ):
            guard_status, pair_id, line_number = _guard_discovery_first_field(path)
            if guard_status == "HOLDOUT_DETECTED_BEFORE_OUTCOME_READ":
                invalid_reasons.append(
                    f"{label}: sealed {pair_id} at line {line_number}; "
                    "outcome fields not read"
                )
            elif guard_status != "PASS":
                blockers.append(
                    f"INVALID_{label}_PAIR_GUARD: {guard_status}; "
                    f"value={pair_id}; line={line_number}"
                )
    if not invalid_reasons:
        _validate_per_frame_effect_bindings(
            baseline_metrics_path, mode_metrics_path, frozen_rows_by_id,
            pair_a_rows, pair_b_rows, criterion_b_was_run, blockers,
        )
    if criterion_a_pass and criterion_b_execution is None:
        blockers.append("CRITERION_B_EXECUTION_SUMMARY_MISSING_AFTER_DERIVED_A_PASS")
    if criterion_a_fail and any(
        path.is_file()
        for path in (
            state_parity_path, mode_metrics_path, mode_execution_path,
            artifact_root / "mode_module_timing_characterization.csv",
        )
    ):
        blockers.append("CRITERION_B_EXECUTION_ARTIFACT_PRESENT_AFTER_DERIVED_A_FAIL")
    refinement_artifact_paths = [
        path for path in artifact_root.rglob("*")
        if path.is_file()
        and any(
            token in path.name.lower()
            for token in ("refinement", "retriever", "mlp", "t3_")
        )
    ]
    if criterion_b_fail and refinement_artifact_paths:
        blockers.append(
            "REFINEMENT_ARTIFACT_PRESENT_AFTER_CRITERION_B_FAIL: "
            + ";".join(sorted(path.name for path in refinement_artifact_paths))
        )

    state_header = (
        _csv_header(state_parity_path)
        if not invalid_reasons and not criterion_a_fail else None
    )
    if state_header is not None and state_header != STATE_PARITY_FIELDS:
        blockers.append(
            "STATE_SNAPSHOT_PARITY_HEADER_MISMATCH: "
            f"expected={STATE_PARITY_FIELDS}; observed={state_header}"
        )
        state_rows: list[dict[str, str]] = []
    else:
        state_rows = (
            []
            if invalid_reasons or criterion_a_fail
            else _load_csv(
                state_parity_path, blockers, "STATE_SNAPSHOT_PARITY",
                required=criterion_a_pass,
            )
        )
    state_summary = (
        {} if criterion_a_fail
        else (criterion_b_execution or {}).get("state_snapshot_parity") or {}
    )
    branch_summary = (
        {} if criterion_a_fail
        else (criterion_b_execution or {}).get("baseline_branch_parity") or {}
    )
    state_status_values = [
        str(row.get("status") or row.get("snapshot_status") or row.get("parity_status") or "")
        for row in state_rows
    ]
    branch_float_diffs = [
        _as_float(
            branch_summary.get(exact_key, branch_summary.get(legacy_key))
        )
        for exact_key, legacy_key in (
            ("maximum_float_prediction_abs_diff", "max_float_prediction_abs_diff"),
            ("maximum_score_map_abs_diff", "max_score_map_abs_diff"),
            ("maximum_confidence_abs_diff", "max_confidence_abs_diff"),
        )
    ]
    baseline_state_rows = [
        row for row in state_rows if row.get("branch_kind") == "baseline"
    ]
    mode_state_rows = [row for row in state_rows if row.get("branch_kind") == "mode"]
    state_rows_exact = (
        len(state_rows) == 24 * (1 + len(LOCKED_MODES))
        and len(baseline_state_rows) == 24
        and len(mode_state_rows) == 24 * len(LOCKED_MODES)
        and {
            (row.get("pair_id", ""), row.get("side", ""))
            for row in baseline_state_rows
        }
        == {
            (pair_id, side)
            for pair_id in EXPECTED_DISCOVERY_IDS
            for side in ("primary", "control")
        }
        and {row.get("pair_id", "") for row in state_rows}
        == set(EXPECTED_DISCOVERY_IDS)
        and all(row.get("side") in {"primary", "control"} for row in state_rows)
        and all(
            row.get("sequence")
            == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_sequence"]
            and row.get("interval_start")
            == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_start"]
            and row.get("interval_end")
            == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_end"]
            and _as_int(row.get("snapshot_frame"))
            == max(1, int(row["interval_start"]) - 1)
            for row in state_rows
        )
        and all(
            bool(re.fullmatch(r"[0-9a-f]{64}", row.get(column, "")))
            for row in state_rows
            for column in (
                "start_snapshot_sha256", "restored_start_snapshot_sha256",
                "baseline_end_snapshot_sha256",
                "continuation_restored_snapshot_sha256",
            )
        )
        and {row.get("mode", "") for row in mode_state_rows} == set(LOCKED_MODES)
        and {
            (row.get("pair_id", ""), row.get("side", ""), row.get("mode", ""))
            for row in mode_state_rows
        }
        == {
            (pair_id, side, mode)
            for pair_id in EXPECTED_DISCOVERY_IDS
            for side in ("primary", "control")
            for mode in LOCKED_MODES
        }
        and all(_as_bool(row.get("start_restore_exact")) is True for row in state_rows)
        and all(_as_bool(row.get("continuation_restore_exact")) is True for row in state_rows)
        and all(
            row.get("start_snapshot_sha256")
            == row.get("restored_start_snapshot_sha256")
            for row in state_rows
        )
        and all(
            row.get("baseline_end_snapshot_sha256")
            == row.get("continuation_restored_snapshot_sha256")
            for row in state_rows
        )
        and all(_as_bool(row.get("integer_prediction_exact")) is True
                for row in baseline_state_rows)
        and all(row.get("mode") == "none" for row in baseline_state_rows)
        and all(bool(str(row.get("captured_state", "")).strip()) for row in state_rows)
        and all(
            (_as_float(row.get(column)) is not None)
            and 0.0 <= (_as_float(row.get(column)) or 0.0) <= PARITY_TOLERANCE
            for row in baseline_state_rows
            for column in (
                "maximum_float_prediction_abs_diff",
                "maximum_score_map_abs_diff",
                "maximum_confidence_abs_diff",
            )
        )
        and all(
            (_as_float(row.get("tolerance")) is not None)
            and 0.0 <= (_as_float(row.get("tolerance")) or 0.0) <= PARITY_TOLERANCE
            for row in state_rows
        )
    )
    state_parity_pass = (
        state_rows_exact
        and all(_status_is_pass(value) for value in state_status_values)
        and _status_is_pass(state_summary.get("status"))
        and _status_is_pass(branch_summary.get("status"))
        and _as_bool(
            branch_summary.get(
                "integer_prediction_exact", branch_summary.get("integer_exact")
            )
        ) is True
        and all(
            value is not None and 0.0 <= value <= PARITY_TOLERANCE
            for value in branch_float_diffs
        )
        and _as_int(state_summary.get("start_restore_branches"))
        == 24 * (1 + len(LOCKED_MODES))
        and _as_int(state_summary.get("continuation_restore_intervals")) == 24
    )
    if criterion_a_pass and not invalid_reasons and not state_parity_pass:
        blockers.append("STATE_SNAPSHOT_OR_BASELINE_BRANCH_PARITY_NOT_PASS")

    mode_execution_header = (
        _csv_header(mode_execution_path)
        if not invalid_reasons and criterion_b_was_run else None
    )
    if mode_execution_header is not None and mode_execution_header != MODE_EXECUTION_FIELDS:
        blockers.append(
            "MODE_EXECUTION_MANIFEST_HEADER_MISMATCH: "
            f"expected={MODE_EXECUTION_FIELDS}; observed={mode_execution_header}"
        )
        mode_execution_rows: list[dict[str, str]] = []
    else:
        mode_execution_rows = (
            []
            if invalid_reasons or not criterion_b_was_run
            else _load_csv(
                mode_execution_path, blockers, "MODE_EXECUTION_MANIFEST",
                required=criterion_b_was_run,
            )
        )
    if criterion_b_was_run and not invalid_reasons and not mode_execution_rows:
        blockers.append("MODE_EXECUTION_MANIFEST_EMPTY")
    if criterion_b_was_run and not invalid_reasons:
        mode_execution_pass = (
            len(mode_execution_rows) == 24 * len(LOCKED_MODES)
            and {row.get("pair_id", "") for row in mode_execution_rows}
            == set(EXPECTED_DISCOVERY_IDS)
            and {row.get("mode", "") for row in mode_execution_rows}
            == set(LOCKED_MODES)
            and {
                (row.get("pair_id", ""), row.get("side", ""), row.get("mode", ""))
                for row in mode_execution_rows
            }
            == {
                (pair_id, side, mode)
                for pair_id in EXPECTED_DISCOVERY_IDS
                for side in ("primary", "control")
                for mode in LOCKED_MODES
            }
            and all(_as_bool(row.get("physical_skip")) is False
                    for row in mode_execution_rows)
            and all(
                row.get("sequence")
                == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_sequence"]
                and row.get("interval_start")
                == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_start"]
                and row.get("interval_end")
                == frozen_rows_by_id[row["pair_id"]][f"{row['side']}_end"]
                and row.get("source_row_sha256_canonical_lf")
                == frozen_row_hashes[row["pair_id"]]
                and _as_int(row.get("test_order"))
                == MODE_SELECTION_META[row["mode"]][2]
                and row.get("mrm_members") == MODE_MEMBERS_TEXT[row["mode"]]
                and _as_int(row.get("interval_output_frames"))
                == int(row["interval_end"]) - int(row["interval_start"]) + 1
                and _as_int(row.get("tracked_branch_frames"))
                == int(row["interval_end"]) - max(int(row["interval_start"]), 2) + 1
                for row in mode_execution_rows
            )
            and all(
                bool(re.fullmatch(r"[0-9a-f]{64}", row.get(column, "")))
                for row in mode_execution_rows
                for column in (
                    "start_snapshot_sha256", "restored_start_snapshot_sha256",
                )
            )
            and all(
                row.get("start_snapshot_sha256")
                == row.get("restored_start_snapshot_sha256")
                and _as_bool(row.get("start_restore_exact")) is True
                and bool(row.get("raw_jsonl_external_path"))
                and (_as_int(row.get("raw_jsonl_first_line")) or 0) > 0
                and (_as_int(row.get("raw_jsonl_last_line")) or 0)
                >= (_as_int(row.get("raw_jsonl_first_line")) or 0)
                for row in mode_execution_rows
            )
            and all(row.get("status") == "EXECUTED_STAGE4B_CRITERION_B"
                    for row in mode_execution_rows)
        )
        if not mode_execution_pass:
            blockers.append("MODE_EXECUTION_MANIFEST_LOCKED_COVERAGE_FAIL")

    if criterion_a_execution:
        if criterion_a_execution.get("status") != (
            "CRITERION_A_BASELINE_EXECUTION_COMPLETE_ANALYSIS_PENDING"
        ):
            blockers.append("CRITERION_A_EXECUTION_SUMMARY_STATUS_INVALID")
        if _as_int(criterion_a_execution.get("discovery_pairs_executed")) != 12:
            blockers.append("CRITERION_A_DISCOVERY_PAIR_COUNT_NOT_12")
        if _as_int(
            criterion_a_execution.get("unique_discovery_source_sequences_executed")
        ) != 18:
            blockers.append("CRITERION_A_UNIQUE_SEQUENCE_COUNT_NOT_18")
        if _as_int(criterion_a_execution.get("frozen_interval_frames")) != 596:
            blockers.append("CRITERION_A_FROZEN_INTERVAL_FRAME_COUNT_NOT_596")
        if (_as_float(criterion_a_execution.get("elapsed_seconds")) or 0.0) <= 0:
            blockers.append("CRITERION_A_ELAPSED_SECONDS_NOT_POSITIVE")
        _require_zero_count(
            criterion_a_execution, "holdout_pairs_executed", "CRITERION_A",
            blockers, invalid_reasons,
        )
    if criterion_b_execution:
        if criterion_b_was_run and criterion_b_execution.get("status") != (
            "CRITERION_B_NINE_MODE_EXECUTION_COMPLETE_ANALYSIS_PENDING"
        ):
            blockers.append(
                "CRITERION_B_EXECUTION_SUMMARY_STATUS_INVALID: "
                f"{criterion_b_execution.get('status')}"
            )
        if criterion_b_was_run and criterion_b_execution.get("scope") != (
            "STAGE4B_DISCOVERY_CRITERION_B_ONLY"
        ):
            blockers.append("CRITERION_B_EXECUTION_SCOPE_MISMATCH")
        if _as_int(criterion_b_execution.get("discovery_pairs_executed")) != 12:
            blockers.append("CRITERION_B_DISCOVERY_PAIR_COUNT_NOT_12")
        if criterion_b_was_run and _as_int(
            criterion_b_execution.get("discovery_intervals_executed")
        ) != 24:
            blockers.append("CRITERION_B_DISCOVERY_INTERVAL_COUNT_NOT_24")
        _require_zero_count(
            criterion_b_execution, "holdout_pairs_executed", "CRITERION_B",
            blockers, invalid_reasons,
        )
        _require_zero_count(
            criterion_b_execution, "holdout_outcomes_read", "CRITERION_B",
            blockers, invalid_reasons,
        )
        modes = criterion_b_execution.get("modes")
        if criterion_b_was_run and _as_sequence_tuple(modes) != LOCKED_MODES:
            blockers.append(f"CRITERION_B_EXECUTION_MODES_NOT_LOCKED_NINE: {modes}")
        if criterion_b_was_run and _as_bool(criterion_b_execution.get("physical_skip")) is not False:
            blockers.append("CRITERION_B_PHYSICAL_SKIP_FALSE_NOT_CONFIRMED")
        if criterion_b_was_run and _as_bool(
            criterion_b_execution.get("refinement_executed")
        ) is not False:
            blockers.append("CRITERION_B_EXECUTION_SUMMARY_PREMATURE_REFINEMENT_FLAG")
        if criterion_b_was_run:
            criterion_a_gate = criterion_b_execution.get("criterion_a_gate") or {}
            if (
                criterion_a_gate.get("status") != "PASS"
                or Path(str(criterion_a_gate.get("summary_path", ""))).resolve()
                != analysis_summary_path.resolve()
                or not re.fullmatch(
                    r"[0-9a-f]{64}",
                    str(criterion_a_gate.get("summary_sha256", "")).lower(),
                )
                or criterion_a_gate.get("criterion_a_estimates")
                != ((analysis or {}).get("criterion_a") or {}).get("metrics")
            ):
                blockers.append("CRITERION_B_CRITERION_A_GATE_BINDING_MISMATCH")
            row_counts = criterion_b_execution.get("row_counts") or {}
            expected_row_counts = {
                "baseline_reference_frames": 596,
                "mode_per_frame_metrics": 596 * len(LOCKED_MODES),
                "state_snapshot_parity": 24 * (1 + len(LOCKED_MODES)),
                "mode_execution_manifest": 24 * len(LOCKED_MODES),
                "mode_module_timing_characterization": len(LOCKED_MODES) * 6,
            }
            if any(
                _as_int(row_counts.get(key)) != expected
                for key, expected in expected_row_counts.items()
            ):
                blockers.append("CRITERION_B_EXECUTION_ROW_COUNT_CONTRACT_MISMATCH")
            raw_record_count = _as_int(row_counts.get("external_raw_jsonl_records"))
            external_raw_summary = criterion_b_execution.get("external_raw_mrm") or {}
            if (
                raw_record_count is None
                or raw_record_count <= 0
                or _as_int(external_raw_summary.get("records")) != raw_record_count
            ):
                blockers.append("CRITERION_B_EXTERNAL_RAW_RECORD_COUNT_MISMATCH")
            input_hashes = criterion_b_execution.get("input_hashes") or {}
            expected_input_hashes: dict[str, object] = {
                "source_sha": EXPECTED_SOURCE_SHA,
                "patch_sha256_canonical_lf": EXPECTED_PATCH_SHA256_CANONICAL_LF,
                "patched_file_sha256": EXPECTED_PATCHED_FILE_SHA256,
                "config_sha256": EXPECTED_T1_CONFIG_SHA256,
                "checkpoint_sha256": EXPECTED_CHECKPOINT_SHA256,
                "frozen_slice_sha256_normalized_lf": frozen_sha,
                "baseline_csv_sha256": _sha256_if_file(baseline_metrics_path),
                "criterion_a_provenance_sha256": _sha256_if_file(provenance_path),
            }
            if any(
                input_hashes.get(key) != expected
                for key, expected in expected_input_hashes.items()
            ):
                blockers.append("CRITERION_B_EXECUTION_INPUT_HASH_BINDING_MISMATCH")
            determinism = criterion_b_execution.get("determinism") or {}
            if (
                _as_int(determinism.get("seed")) != 20_260_826
                or determinism.get("CUBLAS_WORKSPACE_CONFIG") != ":4096:8"
                or _as_bool(determinism.get("torch_deterministic_algorithms")) is not True
                or _as_bool(determinism.get("cudnn_deterministic")) is not True
                or _as_bool(determinism.get("cudnn_benchmark")) is not False
                or determinism.get("torch")
                != ((provenance or {}).get("environment") or {}).get("torch")
                or determinism.get("torch_cuda")
                != ((provenance or {}).get("environment") or {}).get("torch_cuda")
                or determinism.get("cudnn")
                != ((provenance or {}).get("environment") or {}).get("cudnn")
                or determinism.get("gpu")
                != ((provenance or {}).get("environment") or {}).get("gpu")
            ):
                blockers.append("CRITERION_B_DETERMINISM_OR_ENVIRONMENT_MISMATCH")
            if criterion_b_execution.get(
                "accepted_nonmutating_discovery_aliases"
            ) != EXPECTED_DISCOVERY_SOURCE_ALIASES:
                blockers.append("CRITERION_B_DISCOVERY_ALIAS_MAP_MISMATCH")
            if (
                criterion_b_execution.get("next_action")
                != "RUN_LOCKED_CRITERION_B_ANALYSIS_BEFORE_ANY_REFINEMENT"
                or criterion_b_execution.get("stage4b_conclusion") is not None
                or (_as_float(criterion_b_execution.get("elapsed_seconds")) or 0.0)
                <= 0.0
            ):
                blockers.append("CRITERION_B_EXECUTION_TERMINAL_STATE_MISMATCH")

    refinement_documents: dict[str, Mapping[str, Any]] = {}
    refinement_document: Mapping[str, Any] | None = None
    if criterion_b_pass and not invalid_reasons:
        refinement_path = artifact_root / REFINEMENT_SUMMARY_NAME
        refinement_guard_ok = False
        refinement_document = _load_json(
            refinement_path, blockers, "BOUNDED_REFINEMENT_EXECUTION_SUMMARY",
            required=False,
        )
        if refinement_document is not None:
            refinement_documents[REFINEMENT_SUMMARY_NAME] = refinement_document
            refinement_signals = _json_holdout_outcome_signals(refinement_document)
            for signal in refinement_signals:
                invalid_reasons.append(
                    f"REFINEMENT_HOLDOUT_OUTCOME_STRUCTURE_DETECTED: {signal}"
                )
            refinement_guard_ok = not refinement_signals
            for name in (
                "retriever_mlp_per_frame_metrics.csv",
                "t3_per_frame_metrics.csv",
                "bounded_refinement_execution_manifest.csv",
            ):
                if not refinement_guard_ok:
                    break
                guard_status, pair_id, line_number = _guard_discovery_first_field(
                    artifact_root / name
                )
                if guard_status == "HOLDOUT_DETECTED_BEFORE_OUTCOME_READ":
                    invalid_reasons.append(
                        f"REFINEMENT_{name}: sealed {pair_id} at line "
                        f"{line_number}; outcome fields not read"
                    )
                    refinement_guard_ok = False
                elif guard_status != "PASS":
                    blockers.append(
                        f"INVALID_REFINEMENT_DISCOVERY_GUARD: {name}: "
                        f"{guard_status}; value={pair_id}; line={line_number}"
                    )
                    refinement_guard_ok = False
            if refinement_guard_ok:
                _validate_execution_output_hashes(
                    refinement_document, artifact_root, blockers, require_map=True,
                    required_names=REFINEMENT_OUTPUT_HASH_KEYS,
                )
        registered_refinement_names = (
            {REFINEMENT_SUMMARY_NAME} | REFINEMENT_OUTPUT_HASH_KEYS
        )
        unregistered_refinement = [
            path.name for path in refinement_artifact_paths
            if path.name not in registered_refinement_names
        ]
        if unregistered_refinement:
            blockers.append(
                "UNREGISTERED_REFINEMENT_ARTIFACT: "
                + ";".join(sorted(unregistered_refinement))
            )
        refinement_complete, refinement_issues, refinement_component_status = (
            _validate_refinement(
                refinement_document,
                str(selected_path) if selected_path else None,
            )
        )
        if (
            refinement_document is not None
            and refinement_guard_ok
            and not invalid_reasons
            and selected_path
        ):
            refinement_issues.extend(
                _validate_refinement_machine_outputs(
                    artifact_root, refinement_document, str(selected_path),
                    frozen_rows_by_id,
                )
            )
            refinement_complete = not refinement_issues
        for issue in refinement_issues:
            if issue == "REFINEMENT_REPORTS_NONZERO_HOLDOUT_EXECUTION_OR_ACCESS":
                invalid_reasons.append(issue)
            else:
                blockers.append(issue)
        if not selected_path:
            blockers.append("CRITERION_B_PASS_WITHOUT_SELECTED_REFINEMENT_PATH")
    else:
        refinement_complete = False
        refinement_component_status = {}

    if not any("distractor" in path.name.lower() and "margin" in path.name.lower()
               for path in artifact_root.glob("*")):
        limitations.append(
            "SECONDARY_DISTRACTOR_MARGIN_NOT_AVAILABLE: accepted instrumentation "
            "exposes only the global score-map output and supplies no validated mapping "
            "from frozen manual distractor boxes to the tracker head grid; therefore no "
            "target-versus-distractor margin was approximated"
        )

    reported_holdout_counts: list[int] = []
    reported_documents: list[Mapping[str, Any] | None] = [
        provenance, criterion_a_execution, analysis,
    ]
    if criterion_b_was_run:
        reported_documents.append(criterion_b_execution)
    reported_documents.extend(refinement_documents.values())
    for document in reported_documents:
        if document is None:
            continue
        for value in _deep_values_for_key(
            document, re.compile(r"holdout.*(executed|outcomes?.*read)", re.I)
        ):
            count = _as_int(value)
            if count is not None:
                reported_holdout_counts.append(count)
    reported_holdout_execution: int | str = (
        max(reported_holdout_counts) if reported_holdout_counts else "NOT AVAILABLE"
    )

    command_log_path = codex_root / f"{DATE_PREFIX}command_log.txt"
    if not command_log_path.is_file():
        blockers.append(f"MISSING_COMMAND_LOG: {command_log_path}")

    provenance_source = _repo_relative(provenance_path, repo_root)
    criterion_a_source = _repo_relative(criterion_a_execution_path, repo_root)
    criterion_b_source = _repo_relative(criterion_b_execution_path, repo_root)
    sequence_source = _repo_relative(sequence_path, repo_root)
    external_evidence: list[ExternalEvidence] = []
    if not invalid_reasons:
        external_evidence.extend(
            _collect_external_from_json(provenance, provenance_source)
        )
        external_evidence.extend(
            _collect_external_from_json(criterion_a_execution, criterion_a_source)
        )
        if criterion_b_was_run:
            external_evidence.extend(
                _collect_external_from_json(criterion_b_execution, criterion_b_source)
            )
        for name, document in refinement_documents.items():
            external_evidence.extend(
                _collect_external_from_json(document, f"artifacts/stage4B_discovery/{name}")
            )
        prediction_evidence = _collect_external_from_sequence_rows(
            sequence_rows, sequence_source
        )
        external_evidence.extend(prediction_evidence)

        unique_prediction_paths = {
            os.path.normcase(str(item.path.resolve())) for item in prediction_evidence
        }
        if len(prediction_evidence) != 18 or len(unique_prediction_paths) != 18:
            blockers.append(
                "EXTERNAL_BASELINE_PREDICTION_SET_NOT_EXACT_18: "
                f"records={len(prediction_evidence)}; unique_paths="
                f"{len(unique_prediction_paths)}"
            )
        if any(
            not item.recorded_sha256
            or not re.fullmatch(r"[0-9a-f]{64}", item.recorded_sha256)
            for item in prediction_evidence
        ):
            blockers.append("EXTERNAL_BASELINE_PREDICTION_HASH_MISSING_OR_MALFORMED")

        raw_evidence = [
            item for item in external_evidence
            if item.evidence_kind == "external_raw_log"
        ]
        required_raw_sources = {provenance_source, criterion_a_source}
        if criterion_b_was_run:
            required_raw_sources.add(criterion_b_source)
        for source in sorted(required_raw_sources):
            if not any(item.source_artifact == source for item in raw_evidence):
                blockers.append(f"EXTERNAL_RAW_LOG_REFERENCE_MISSING: {source}")
        required_raw_paths = {
            os.path.normcase(str(item.path.resolve()))
            for item in raw_evidence
            if item.source_artifact in required_raw_sources
        }
        if len(required_raw_paths) < len(required_raw_sources):
            blockers.append(
                "EXTERNAL_RAW_LOG_PATHS_NOT_DISTINCT_PER_EXECUTION_PHASE: "
                f"required_sources={len(required_raw_sources)}; "
                f"unique_paths={len(required_raw_paths)}"
            )
        if any(
            not item.recorded_sha256
            or not re.fullmatch(r"[0-9a-f]{64}", item.recorded_sha256)
            for item in raw_evidence
        ):
            blockers.append("EXTERNAL_RAW_LOG_HASH_MISSING_OR_MALFORMED")
        if refinement_documents:
            refinement_source = (
                f"artifacts/stage4B_discovery/{REFINEMENT_SUMMARY_NAME}"
            )
            refinement_raw_paths = {
                os.path.normcase(str(item.path.resolve()))
                for item in raw_evidence
                if item.source_artifact == refinement_source
            }
            if len(refinement_raw_paths) < 2:
                blockers.append("REFINEMENT_EXTERNAL_RAW_LOG_SET_NOT_VERIFIABLE")
    safe_external_evidence: list[ExternalEvidence] = []
    canonical_raw_paths = {
        provenance_source: (external_root / "parity_instrumented.json").resolve(),
        criterion_a_source: (
            external_root / "criterionA" / "baseline_raw_mrm.jsonl"
        ).resolve(),
        criterion_b_source: (
            external_root / "criterionB" / "criterionB_raw_mrm.jsonl"
        ).resolve(),
    }
    expected_prediction_paths = {
        (
            external_root / "criterionA" / "baseline_full_predictions"
            / f"{row.get('sequence', '')}.csv"
        ).resolve(): (
            str(row.get("sequence", "")),
            _as_int(row.get("executed_through_frame")) or 0,
        )
        for row in sequence_rows
    }
    refinement_source = f"artifacts/stage4B_discovery/{REFINEMENT_SUMMARY_NAME}"
    refinement_external_root = (external_root / "bounded_refinement").resolve()
    holdout_sequences = {
        str(frozen_rows_by_id[pair_id][f"{side}_sequence"])
        for pair_id in EXPECTED_HOLDOUT_IDS
        for side in ("primary", "control")
    }
    for item in external_evidence:
        resolved = item.path.resolve()
        safe = False
        if item.evidence_kind == "external_prediction":
            expected = expected_prediction_paths.get(resolved)
            if item.source_artifact != sequence_source or expected is None:
                blockers.append(f"NONCANONICAL_EXTERNAL_PREDICTION_PATH: {resolved}")
                continue
            if resolved.is_file():
                guard_status, observed, line_number = (
                    _guard_external_prediction_sequence(
                        resolved, expected[0], expected[1]
                    )
                )
                if guard_status == "NON_DISCOVERY_SEQUENCE" and observed in holdout_sequences:
                    invalid_reasons.append(
                        f"EXTERNAL_PREDICTION_HOLDOUT_SEQUENCE_AT_LINE_"
                        f"{line_number}: {observed}; outcome fields not read"
                    )
                    continue
                if guard_status not in {"PASS", "MISSING"}:
                    blockers.append(
                        f"EXTERNAL_PREDICTION_DISCOVERY_GUARD_{guard_status}: "
                        f"{resolved}; value={observed}; line={line_number}"
                    )
                    continue
            safe = True
        elif item.evidence_kind == "external_raw_log":
            expected_raw = canonical_raw_paths.get(item.source_artifact)
            if expected_raw is not None:
                safe = resolved == expected_raw
            elif item.source_artifact == refinement_source:
                safe = (
                    _is_within(resolved, refinement_external_root)
                    and resolved.suffix.lower() == ".jsonl"
                    and "holdout" not in resolved.name.lower()
                )
            if not safe:
                if re.search(r"R3-H\d\d|holdout", str(resolved), re.I):
                    invalid_reasons.append(
                        f"EXTERNAL_RAW_LOG_HOLDOUT_PATH_REJECTED_WITHOUT_OPEN: {resolved}"
                    )
                else:
                    blockers.append(f"NONCANONICAL_EXTERNAL_RAW_LOG_PATH: {resolved}")
                continue
        if safe:
            safe_external_evidence.append(item)
    external_evidence = safe_external_evidence
    if invalid_reasons:
        external_evidence = []
    external_verification = _verify_external_evidence(external_evidence, external_root)
    for item in external_verification:
        if item.status not in {
            "VERIFIED", "RECORDED_HASH_NOT_REOPENED_BOUNDARY_SAFE",
        }:
            blockers.append(
                f"EXTERNAL_EVIDENCE_{item.status}: {item.path}; "
                f"recorded_sha256={item.recorded_sha256 or 'NONE'}"
            )

    external_registry_path = artifact_root / "external_evidence_registry.csv"
    _atomic_write_csv(
        external_registry_path,
        (
            "source_artifact", "evidence_kind", "path", "size_bytes",
            "recorded_sha256", "observed_sha256", "verification_status",
        ),
        (
            {
                "source_artifact": item.source_artifact,
                "evidence_kind": item.evidence_kind,
                "path": item.path,
                "size_bytes": "" if item.size_bytes is None else item.size_bytes,
                "recorded_sha256": item.recorded_sha256 or "",
                "observed_sha256": item.observed_sha256 or "",
                "verification_status": item.status,
            }
            for item in external_verification
        ),
    )

    excluded_repository_paths: set[Path] = set()
    if criterion_a_fail:
        excluded_repository_paths.update(
            (artifact_root / name).resolve() for name in B_EXECUTION_BASENAMES
        )
    if criterion_a_fail or criterion_b_fail:
        excluded_repository_paths.update(
            path.resolve() for path in refinement_artifact_paths
        )
        excluded_repository_paths.add(
            (artifact_root / REFINEMENT_SUMMARY_NAME).resolve()
        )
        excluded_repository_paths.update(
            (artifact_root / name).resolve()
            for name in REFINEMENT_OUTPUT_HASH_KEYS
        )

    unexpected_repository_artifacts = [
        path for path in codex_root.glob(f"{DATE_PREFIX}*")
        if path.is_file() and path.name not in REGISTERED_CODEX_ROOT_BASENAMES
    ]
    if artifact_root.is_dir():
        unexpected_repository_artifacts.extend(
            path for path in artifact_root.rglob("*")
            if path.is_file()
            and (
                path.parent.resolve() != artifact_root.resolve()
                or path.name not in REGISTERED_ARTIFACT_BASENAMES
            )
        )
    for path in sorted(unexpected_repository_artifacts, key=str):
        blockers.append(
            "UNREGISTERED_STAGE4B_REPOSITORY_ARTIFACT_REJECTED_WITHOUT_OPEN: "
            f"{_repo_relative(path, repo_root)}"
        )

    pre_manifest_paths = _repository_artifact_paths(
        repo_root, codex_root, artifact_root, report_path,
        exclude_outcome_files=bool(invalid_reasons),
        excluded_repository_paths=excluded_repository_paths,
    )
    for path in sorted(pre_manifest_paths, key=str):
        if path.resolve() == report_path.resolve() or not path.is_file():
            continue
        bounded_issue = _bounded_repository_artifact_issue(path, repo_root)
        if bounded_issue is not None:
            blockers.append(
                f"UNBOUNDED_REPOSITORY_ARTIFACT_{bounded_issue}: "
                f"{_repo_relative(path, repo_root)}"
            )

    # Duplicate blocker strings do not add evidence.  Preserve first-observed
    # ordering while making report generation idempotent.
    blockers = list(dict.fromkeys(blockers))
    invalid_reasons = list(dict.fromkeys(invalid_reasons))
    limitations = list(dict.fromkeys(limitations))

    report_criterion_a_rows = [] if invalid_reasons else criterion_a_rows
    report_criterion_b_rows = [] if invalid_reasons else criterion_b_rows
    report_sensitivity_rows = [] if invalid_reasons else sensitivity_rows
    report_bootstrap_rows = [] if invalid_reasons else bootstrap_rows
    report_selected_path = None if invalid_reasons else selected_path
    a_by_metric = {row.get("metric", ""): row for row in report_criterion_a_rows}
    iou_a = a_by_metric.get("iou_weakness", {})
    failure_a = a_by_metric.get("failure_weakness", {})
    a_sensitivity = [
        row for row in report_sensitivity_rows
        if row.get("analysis_family") == "CRITERION_A"
    ]
    b_sensitivity = [
        row for row in report_sensitivity_rows
        if row.get("analysis_family") == "CRITERION_B"
    ]

    baseline_timing_path = artifact_root / "module_timing_characterization.csv"
    mode_timing_path = artifact_root / "mode_module_timing_characterization.csv"
    if invalid_reasons:
        baseline_timing_count, baseline_timing_rows = 0, []
        baseline_skip_false, baseline_timing_contract = True, False
        mode_timing_count, mode_timing_rows = 0, []
        mode_skip_false, mode_timing_contract = True, False
    else:
        (
            baseline_timing_count, baseline_timing_rows, baseline_skip_false,
            baseline_timing_contract,
        ) = _timing_summary(baseline_timing_path)
        (
            mode_timing_count, mode_timing_rows, mode_skip_false,
            mode_timing_contract,
        ) = _timing_summary(mode_timing_path)
        if baseline_timing_count == 0:
            blockers.append("BASELINE_TIMING_CHARACTERIZATION_MISSING_OR_EMPTY")
        if criterion_b_was_run and mode_timing_count == 0:
            blockers.append("CRITERION_B_TIMING_CHARACTERIZATION_MISSING_OR_EMPTY")
        if baseline_timing_path.is_file() and not baseline_skip_false:
            blockers.append("BASELINE_TIMING_ROWS_DO_NOT_ALL_CONFIRM_PHYSICAL_SKIP_FALSE")
        if mode_timing_path.is_file() and not mode_skip_false:
            blockers.append("MODE_TIMING_ROWS_DO_NOT_ALL_CONFIRM_PHYSICAL_SKIP_FALSE")
        if baseline_timing_count and not baseline_timing_contract:
            blockers.append("BASELINE_TIMING_NUMERIC_OR_COVERAGE_CONTRACT_FAIL")
        if criterion_b_was_run and mode_timing_count and not mode_timing_contract:
            blockers.append("CRITERION_B_TIMING_NUMERIC_OR_COVERAGE_CONTRACT_FAIL")
    timing_physical_skip_decision = (
        "PASS"
        if not invalid_reasons
        and baseline_timing_count > 0
        and baseline_skip_false
        and baseline_timing_contract
        and (
            not criterion_b_was_run
            or (mode_timing_count > 0 and mode_skip_false and mode_timing_contract)
        )
        else "FAIL"
    )

    blockers = list(dict.fromkeys(blockers))
    if invalid_reasons:
        conclusion = INVALID_HOLDOUT
    elif blockers:
        conclusion = INCOMPLETE
    elif criterion_a_fail:
        conclusion = "STAGE4B_CRITERION_A_FAIL"
    elif not criterion_a_pass:
        conclusion = INCOMPLETE
        blockers.append("CRITERION_A_NOT_COMPLETED")
    elif not criterion_b_was_run:
        conclusion = INCOMPLETE
        blockers.append("CRITERION_B_NOT_RUN_AFTER_CRITERION_A_PASS")
    elif criterion_b_fail:
        conclusion = "STAGE4B_CRITERION_B_FAIL"
    elif criterion_b_pass and refinement_complete:
        conclusion = "STAGE4B_AB_PASS_READY_FOR_MANAGER_REVIEW"
    else:
        conclusion = INCOMPLETE
        blockers.append("CRITERION_B_RESULT_NOT_FINAL_OR_REFINEMENT_INCOMPLETE")
    blockers = list(dict.fromkeys(blockers))
    if conclusion not in ALLOWED_CONCLUSIONS:
        raise AssertionError(f"disallowed Stage-4B conclusion: {conclusion}")

    env = (provenance or {}).get("environment") or {}
    packages = env.get("packages") or {}
    patch_paths = (provenance or {}).get("patched_paths") or []
    blocker_lines = invalid_reasons + blockers
    if blocker_lines:
        blockers_markdown = "\n".join(f"- `{_markdown_cell(item)}`" for item in blocker_lines)
    else:
        blockers_markdown = "- None."
    limitation_markdown = (
        "\n".join(f"- {_markdown_cell(item)}" for item in limitations)
        if limitations else "- None."
    )

    criterion_a_table = _markdown_table(
        ("Metric", "Estimate", "Primary 95% CI", "Threshold", "Primary p", "Pass",
         "Component 95% CI"),
        (
            (
                row.get("metric"), _format_number(row.get("estimate")),
                f"[{_format_number(row.get('primary_ci_low'))}, "
                f"{_format_number(row.get('primary_ci_high'))}]",
                _format_number(row.get("threshold")),
                _format_number(row.get("primary_p_two_sided_sign_tail")),
                row.get("metric_pass"),
                f"[{_format_number(row.get('component_ci_low'))}, "
                f"{_format_number(row.get('component_ci_high'))}]",
            )
            for row in report_criterion_a_rows
        ),
    )
    criterion_b_table = _markdown_table(
        ("Order", "Mode", "Mean interaction", "Primary 95% CI", "p", "Holm p",
         "Direction", "Pass", "Selected"),
        (
            (
                row.get("test_order"), row.get("mode"),
                _format_number(row.get("mean_interaction")),
                f"[{_format_number(row.get('primary_ci_low'))}, "
                f"{_format_number(row.get('primary_ci_high'))}]",
                _format_number(row.get("primary_p_unadjusted")),
                _format_number(row.get("primary_p_holm_adjusted")),
                row.get("direction"), row.get("test_pass"),
                row.get("selected_refinement_path"),
            )
            for row in report_criterion_b_rows
        ),
    )
    sensitivity_table = _markdown_table(
        ("Dimension", "Group", "Metric", "n pairs", "Estimate", "Primary 95% CI",
         "Component 95% CI"),
        (
            (
                row.get("sensitivity_dimension"), row.get("sensitivity_group"),
                row.get("metric_or_mode"), row.get("n_pairs"),
                _format_number(row.get("estimate")),
                f"[{_format_number(row.get('primary_ci_low'))}, "
                f"{_format_number(row.get('primary_ci_high'))}]",
                f"[{_format_number(row.get('component_ci_low'))}, "
                f"{_format_number(row.get('component_ci_high'))}]",
            )
            for row in a_sensitivity
        ),
    )
    timing_rows = baseline_timing_rows + mode_timing_rows
    timing_table = _markdown_table(
        ("Mode/control", "MRM", "n", "Retriever mean ms", "MLP mean ms",
         "MRM compute mean ms", "Instrumented mean ms"),
        (
            (
                row["mode"], row["module"], row["n"],
                _format_number(row["retriever_mean_ms"], 3),
                _format_number(row["mlp_mean_ms"], 3),
                _format_number(row["compute_mean_ms"], 3),
                _format_number(row["instrumented_mean_ms"], 3),
            )
            for row in timing_rows
        ),
    )
    external_table = _markdown_table(
        ("Kind", "Path", "Size bytes", "SHA-256", "Verification"),
        (
            (
                item.evidence_kind, item.path,
                item.size_bytes if item.size_bytes is not None else "NOT AVAILABLE",
                item.observed_sha256 or item.recorded_sha256 or "NOT AVAILABLE",
                item.status,
            )
            for item in external_verification
            if item.evidence_kind == "external_raw_log"
        ),
    )
    sequence_table = _markdown_table(
        ("Sequence", "Official start", "Executed through", "Initialized once", "Status",
         "External prediction SHA-256"),
        (
            (
                row.get("sequence"), row.get("official_start_frame"),
                row.get("executed_through_frame"),
                row.get("initialized_once_from_official_start"), row.get("status"),
                row.get("prediction_sha256"),
            )
            for row in sequence_rows
        ),
    )
    holdout_table = _markdown_table(
        ("Pair ID", "Frozen primary", "Frozen control", "Row SHA-256", "Status"),
        (
            (
                row.get("pair_id"),
                f"{row.get('primary_sequence')} {row.get('primary_start')}-{row.get('primary_end')}",
                f"{row.get('control_sequence')} {row.get('control_start')}-{row.get('control_end')}",
                row.get("row_sha256_canonical_lf"), row.get("status"),
            )
            for row in holdout_rows
        ),
    )

    a_decision = (
        "NOT COMPLETED" if invalid_reasons else
        "PASS" if criterion_a_pass else "FAIL" if criterion_a_fail else "NOT COMPLETED"
    )
    b_decision = (
        "NOT RUN" if invalid_reasons else
        "PASS" if criterion_b_pass else "FAIL" if criterion_b_fail else "NOT RUN"
    )
    state_decision = (
        "BLOCKED" if invalid_reasons else
        "PASS" if state_parity_pass else "BLOCKED" if criterion_a_pass
        else "NOT REQUIRED AFTER A FAIL"
    )
    holm_decision = (
        "NOT RUN" if invalid_reasons else
        "PASS" if criterion_b_was_run and criterion_b_tables_pass else
        "FAIL" if criterion_b_was_run else "NOT RUN"
    )
    after_a = (
        "STOP: invalid hold-out exposure signal" if invalid_reasons else
        "STOP before MRM mining" if criterion_a_fail else
        "Proceed to exactly nine predeclared Criterion-B controls" if criterion_a_pass else
        "STOP: Criterion A is incomplete"
    )
    after_b = (
        "STOP: invalid hold-out exposure signal" if invalid_reasons else
        "STOP before refinement" if criterion_b_fail else
        "Proceed only to the selected bounded refinement path" if criterion_b_pass else
        "Criterion B has not been run to a final result"
    )

    refinement_rows = [] if invalid_reasons else [
        (component, status) for component, status in refinement_component_status.items()
    ]
    refinement_table = _markdown_table(("Component", "Status"), refinement_rows)
    refinement_components = (
        refinement_document.get("components", {})
        if isinstance(refinement_document, Mapping) else {}
    )
    if not isinstance(refinement_components, Mapping):
        refinement_components = {}
    t3_baseline_component = refinement_components.get("t3_baseline", {})
    if not isinstance(t3_baseline_component, Mapping):
        t3_baseline_component = {}
    t3_controls_component = refinement_components.get(
        "t3_selected_path_controls", {}
    )
    if not isinstance(t3_controls_component, Mapping):
        t3_controls_component = {}
    t3_baseline_status = refinement_component_status.get(
        "t3_baseline", "NOT AVAILABLE"
    )
    t3_controls_status = refinement_component_status.get(
        "t3_selected_path_controls", "NOT AVAILABLE"
    )
    t3_refinement_rows = [
        (
            "t3_baseline",
            t3_baseline_status,
            t3_baseline_component.get("discovery_pairs_executed", "NOT AVAILABLE"),
            t3_baseline_component.get(
                "discovery_intervals_executed", "NOT AVAILABLE"
            ),
        )
    ]
    t3_refinement_rows.extend(
        (
            control_name,
            t3_controls_status,
            t3_controls_component.get(
                "discovery_pairs_executed", "NOT AVAILABLE"
            ),
            t3_controls_component.get(
                "discovery_intervals_executed", "NOT AVAILABLE"
            ),
        )
        for control_name in T3_REFINEMENT_CONTROL_NAMES
    )
    t3_refinement_table = _markdown_table(
        ("T3 condition", "Status", "Discovery pairs", "Frozen intervals"),
        t3_refinement_rows,
    )
    t3_controls_executed = t3_controls_component.get(
        "controls_executed", "NOT AVAILABLE"
    )
    produced_key_paths = sorted(
        {
            path for path in pre_manifest_paths
            if path.resolve() == report_path.resolve()
            or (
                path.is_file()
                and _bounded_repository_artifact_issue(path, repo_root) is None
            )
        }
        | {(artifact_root / "artifact_manifest.csv").resolve()},
        key=lambda path: _repo_relative(path, repo_root),
    )
    files_table = _markdown_table(
        ("Path", "Role"),
        (
            (
                _repo_relative(path, repo_root),
                "generated report" if path == report_path else
                "artifact manifest" if path.name == "artifact_manifest.csv" else
                _manifest_scope(path, repo_root, artifact_root),
            )
            for path in produced_key_paths
        ),
    )

    report = f"""# Stage 4B frozen discovery diagnostic execution report

**Date:** 2026-08-26

**Scope:** frozen 12-pair discovery execution only

**Report conclusion:** `{conclusion}`

This report is generated deterministically from bounded execution and analysis
artifacts. It does not assign a final diagnostic decision, does not unlock
Stage 4C, and contains no held-out outcome.

## 1. Boundary and frozen-slice verification

- Frozen-slice normalized-LF SHA-256: `{frozen_sha}`
- Locked expected SHA-256: `{EXPECTED_FROZEN_SLICE_NORMALIZED_SHA256}`
- Frozen-slice validation: `{'PASS' if frozen_boundary_pass and manifest_pairs_pass else 'FAIL'}`
- Frozen discovery IDs: `{', '.join(EXPECTED_DISCOVERY_IDS)}`
- Discovery pairs represented in the execution manifest: `{len(discovery_ids & set(EXPECTED_DISCOVERY_IDS))}`
- Discovery intervals represented: `{len(discovery_rows)}` (expected 24 primary/control intervals)
- Held-out outcome rows consumed by this reporting lane: `0`

## 2. Hold-out seal declaration

The eight held-out pairs remain frozen metadata only. Their tracker outcomes,
IoU, failures, scores, contributions, utilities, and labels were not opened or
computed by this reporting lane. Maximum hold-out execution/access count
reported by the input summaries: `{reported_holdout_execution}`. Seal status:
`{'PASS' if holdout_seal_pass and not invalid_reasons else 'FAIL'}`.

{holdout_table}

## 3. Source/config/checkpoint/patch provenance

- Official source: `faicaiwawa/SpikeTrack`
- Clean pinned source SHA: `{(provenance or {}).get('source_sha', 'NOT AVAILABLE')}`
- Config: `{(provenance or {}).get('config', 'NOT AVAILABLE')}`
- Config SHA-256: `{(provenance or {}).get('config_sha256', 'NOT AVAILABLE')}`
- Checkpoint: `{(provenance or {}).get('checkpoint', 'NOT AVAILABLE')}`
- Checkpoint SHA-256: `{(provenance or {}).get('checkpoint_sha256', 'NOT AVAILABLE')}`
- Canonical OTB2015 dataset root: `{(provenance or {}).get('dataset_root', 'NOT AVAILABLE')}`
- Accepted Stage-4A-E2 source-manifest SHA-256: `{EXPECTED_E2_SOURCE_MANIFEST_SHA256}`
- Accepted patch SHA-256 (canonical LF): `{(provenance or {}).get('patch_sha256_canonical_lf', 'NOT AVAILABLE')}`
- Patch application: `{(provenance or {}).get('patch_apply_result', 'NOT AVAILABLE')}`
- Patched files: `{', '.join(str(value) for value in patch_paths) if patch_paths else 'NOT AVAILABLE'}`
- Patched-file SHA-256 map: `{_markdown_cell(json.dumps((provenance or {}).get('patched_file_sha256', {}), sort_keys=True))}`
- Operational boundary: `{(provenance or {}).get('operational_baseline_boundary', 'NOT AVAILABLE')}`

## 4. Environment

| Field | Recorded value |
| --- | --- |
| OS | {_markdown_cell(env.get('os'))} |
| CPU | {_markdown_cell(env.get('cpu'))} |
| RAM bytes | {_markdown_cell(env.get('ram_bytes'))} |
| GPU | {_markdown_cell(env.get('gpu'))} |
| VRAM bytes | {_markdown_cell(env.get('gpu_total_memory_bytes'))} |
| Python | {_markdown_cell(env.get('python'))} |
| PyTorch | {_markdown_cell(env.get('torch'))} |
| CUDA | {_markdown_cell(env.get('torch_cuda'))} |
| cuDNN | {_markdown_cell(env.get('cudnn'))} |
| timm | {_markdown_cell(packages.get('timm'))} |
| key dependency versions | {_markdown_cell(json.dumps(packages, sort_keys=True))} |
| dtype | {_markdown_cell(env.get('dtype'))} |
| seed | {_markdown_cell(env.get('seed'))} |
| deterministic settings | {_markdown_cell(json.dumps(env.get('deterministic_settings', {}), sort_keys=True))} |

## 5. No-ablation parity

- Status: `{'PASS' if parity_pass else 'FAIL'}`
- Maximum observed absolute difference: `{_format_number(parity_max_diff, 9)}`
- Required tolerance: `<= 0.000001`
- Recorded tolerance: `{_format_number(parity_tolerance, 9)}`
- Prediction, encoded state, score map, and head fingerprints are retained in
  `{_repo_relative(parity_path, repo_root)}`.

## 6. Sequence execution contract

Every unique discovery source sequence was required to initialize once through
the official sequence start and run sequentially through its maximum frozen
frame. No interval-level GT reinitialization is accepted. Contract validation:
`{'PASS' if sequence_contract_pass else 'FAIL'}`.

{sequence_table}

## 7. Snapshot/restore implementation

Criterion-B branches must restore the same prefix snapshot at
`interval_start - 1`, clone it into baseline and each of the nine predeclared
ablation controls, then continue over identical frames. Reinitializing from GT
is prohibited. Recorded start/restore branches:
`{state_summary.get('start_restore_branches', 'NOT AVAILABLE')}`; recorded
continuation/restore intervals:
`{state_summary.get('continuation_restore_intervals', 'NOT AVAILABLE')}`.

## 8. Snapshot parity results

- State snapshot parity: `{state_decision}`
- State-parity rows: `{len(state_rows)}`
- Summary state status: `{state_summary.get('status', 'NOT AVAILABLE')}`
- Baseline branch status: `{branch_summary.get('status', 'NOT AVAILABLE')}`
- Integer prediction parity: `{branch_summary.get('integer_prediction_exact', branch_summary.get('integer_exact', 'NOT AVAILABLE'))}`
- Maximum floating prediction difference: `{_format_number(branch_summary.get('maximum_float_prediction_abs_diff', branch_summary.get('max_float_prediction_abs_diff')), 9)}`
- Maximum score-map difference: `{_format_number(branch_summary.get('maximum_score_map_abs_diff', branch_summary.get('max_score_map_abs_diff')), 9)}`
- Maximum confidence difference: `{_format_number(branch_summary.get('maximum_confidence_abs_diff', branch_summary.get('max_confidence_abs_diff')), 9)}`

Absence of state-parity evidence is acceptable only when Criterion A failed and
the protocol stopped before MRM execution.

## 9. Criterion A complete-set result

Criterion A: `{a_decision}`. Pair effects are equally weighted after
within-interval frame means; the primary bootstrap clusters by unique primary
sequence and retains all pairs belonging to a sampled sequence.

{criterion_a_table}

## 10. Criterion A sensitivity results

These locked strata are descriptive only. They do not change the complete-set
decision and no positive conclusion relies on a favorable subgroup.

{sensitivity_table}

## 11. Stop/proceed decision after Criterion A

`{after_a}`.

## 12. Criterion B nine-test results, if run

Criterion B: `{b_decision}`. Exactly the six individual MRMs and three locked
groups are admissible. All controls remain `physical_skip=false`.

{criterion_b_table}

The machine sensitivity table retains `{len(b_sensitivity)}` locked
Criterion-B descriptive rows. Those rows do not create extra tests and cannot
rescue the primary nine-test family.

## 13. Holm correction and clustered bootstrap

- Bootstrap resamples: `{((analysis or {}).get('analysis_contract') or {}).get('bootstrap_resamples', 'NOT AVAILABLE')}`
- Bootstrap seed: `{((analysis or {}).get('analysis_contract') or {}).get('bootstrap_seed', 'NOT AVAILABLE')}`
- Primary cluster unit: `unique primary_sequence`
- Required dependency sensitivity: connected source components
- Criterion-A primary/component bootstrap rows: `{sum(1 for row in report_bootstrap_rows if row.get('analysis_family') == 'CRITERION_A')}`
- Criterion-B primary/component bootstrap rows: `{sum(1 for row in report_bootstrap_rows if row.get('analysis_family') == 'CRITERION_B')}`
- Holm correction: `{holm_decision}` across `{len(holm_rows)}` rows; familywise alpha `0.05`

## 14. Criterion B stop/proceed decision

`{after_b}`. Selected refinement path: `{report_selected_path or 'NONE'}`.

## 15. Retriever/MLP refinement, if permitted

Retriever-only and MLP-only bypasses are permitted only after the primary
nine-test Criterion-B family passes, and only for the locked selected path.

{refinement_table}

No refinement result creates a new Criterion-B test or rescues a failed primary
family.

## 16. T3 controlled comparison, if permitted

T3 is secondary and is permitted only after Criterion B passes. A complete
refinement package requires the T3 baseline on all frozen discovery pairs and,
when technically valid, the three selected-path template/time controls. An
explicit technical-validity blocker is accepted for unavailable controls; a
missing artifact is not. T3 never replaces the T1 Criterion-A/B decision.
The required controlled config is `experiments/spiketrack/spiketrack_s256_t3.yaml`
and the pinned T3 checkpoint SHA-256 is `{EXPECTED_T3_CHECKPOINT_SHA256}`.

Selected-path T3 controls executed: `{t3_controls_executed}` of `3`.

{t3_refinement_table}

## 17. Timing characterization and non-claims

- Baseline timing rows: `{baseline_timing_count}`
- Criterion-B mode timing rows: `{mode_timing_count}`
- Timing physical-skip flag validation: `{timing_physical_skip_decision}`

{timing_table}

These desktop measurements characterize instrumented execution only. They are
not physical-skipping savings, not end-to-end deployment latency, and not
Jetson Nano evidence. No parity with author-released raw OTB predictions is
claimed.

External raw logs and their recorded/observed hashes:

{external_table}

## 18. Exact blockers

Blocking or invalidating conditions:

{blockers_markdown}

Secondary non-gating limitations:

{limitation_markdown}

## 19. Files produced

{files_table}

The complete repository/external inventory is written to
`screening/codex/artifacts/stage4B_discovery/artifact_manifest.csv` with path,
scope, size, SHA-256, and committed/external classification. The manifest
excludes its own row because a stable file cannot contain its own SHA-256.
`COMMITTED` is used only for a clean tracked path at generation time;
new/staged/modified bounded paths are labeled `COMMIT_CANDIDATE`. Commit and
push state are reconciled separately after this report is generated.

## 20. Stage 4B conclusion

| Final field | Value |
| --- | --- |
| Frozen-slice validation | {'PASS' if frozen_boundary_pass and manifest_pairs_pass else 'FAIL'} |
| Discovery pairs executed | {_as_int((criterion_a_execution or {}).get('discovery_pairs_executed')) if criterion_a_execution else 'NOT AVAILABLE'} |
| Hold-out pairs executed/accessed (maximum reported count) | {reported_holdout_execution} |
| Hold-out seal | {'PASS' if holdout_seal_pass and not invalid_reasons else 'FAIL'} |
| No-ablation parity | {'PASS' if parity_pass else 'FAIL'} |
| State snapshot parity | {state_decision} |
| Criterion A | {a_decision} |
| IoU weakness | {_format_number(iou_a.get('estimate'))} [{_format_number(iou_a.get('primary_ci_low'))}, {_format_number(iou_a.get('primary_ci_high'))}] |
| Failure-rate weakness | {_format_number(failure_a.get('estimate'))} [{_format_number(failure_a.get('primary_ci_low'))}, {_format_number(failure_a.get('primary_ci_high'))}] |
| Criterion B | {b_decision} |
| Passing MRM/group | {'; '.join(row.get('mode', '') for row in report_criterion_b_rows if _as_bool(row.get('test_pass')) is True) or 'NONE'} |
| Holm correction | {holm_decision} |
| Selected refinement path | {report_selected_path or 'NONE'} |
| Stage 4B | `{conclusion}` |
| Stage 4C | `LOCKED` |
| Diagnostic decision | `NOT ASSIGNED` |
| S1-S7 | `NOT STARTED` |
| Primary shortlist | `NONE` |
| Main baseline | `NONE` |
| Proposed architecture | `NONE` |

STOP. Wait for Manager Stage-4B reconciliation.
"""

    _atomic_write_text(report_path, report)
    manifest_path = _write_artifact_manifest(
        repo_root, codex_root, artifact_root, report_path, external_verification,
        exclude_outcome_files=bool(invalid_reasons),
        excluded_repository_paths=excluded_repository_paths,
    )
    return {
        "report": str(report_path),
        "artifact_manifest": str(manifest_path),
        "external_evidence_registry": str(external_registry_path),
        "stage4b_conclusion": conclusion,
        "frozen_slice_validation": (
            "PASS" if frozen_boundary_pass and manifest_pairs_pass else "FAIL"
        ),
        "holdout_pairs_executed": reported_holdout_execution,
        "holdout_seal": "PASS" if holdout_seal_pass and not invalid_reasons else "FAIL",
        "criterion_a": a_decision,
        "criterion_b": b_decision,
        "stage4c": "LOCKED",
        "diagnostic_decision": "NOT ASSIGNED",
        "blockers": invalid_reasons + blockers,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the deterministic Stage-4B discovery report and artifact manifest "
            "without executing tracker diagnostics."
        )
    )
    parser.add_argument(
        "--repo-root", type=Path, required=True,
        help="Path to the Q1_TrackingResearch repository root.",
    )
    parser.add_argument(
        "--external-root", type=Path, required=True,
        help=(
            "Declared external Stage-4B evidence root; referenced raw logs must remain "
            "inside this root and match their recorded hashes."
        ),
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        result = finalize(args.repo_root, args.external_root)
    except (
        AttributeError, FileNotFoundError, KeyError, PermissionError,
        OSError, TypeError, ValueError, csv.Error,
    ) as exc:
        print(f"STAGE4B_REPORT_INPUT_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["stage4b_conclusion"] != INVALID_HOLDOUT else 3


if __name__ == "__main__":
    raise SystemExit(main())
