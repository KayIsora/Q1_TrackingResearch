"""Execute the locked Stage-4B Criterion-A discovery baseline.

This program is intentionally discovery-only.  It parses HOLDOUT rows solely
to create the metadata-only seal and never resolves, opens, or evaluates a
hold-out dataset path.  Scientific metrics use the pinned OTB evaluator's
inclusive-coordinate IoU and center definitions.  Tracker boxes are truncated
to integer exactly as ``running.py::save_bb`` before evaluation; the official
first-frame GT override is applied only at the sequence's initialization
frame.  Floating predictions are retained separately for audit.

Large full-sequence predictions and raw MRM JSONL are written below the
external working root.  Bounded interval metrics and manifests are written to
the repository artifact root supplied on the command line.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import subprocess
import sys
import time
from types import SimpleNamespace

import cv2
import numpy as np


PINNED_SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
T1_CONFIG_SHA256 = "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
T1_CHECKPOINT_SHA256 = "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
PATCH_SHA256_CANONICAL_LF = "d4a1065a32ef6da6132e4f9f7980f727e9109bb00e2e2370398b1e90de5a713a"
EXPECTED_DISCOVERY_IDS = tuple(f"R3-D{i:02d}" for i in range(1, 13))
EXPECTED_HOLDOUT_IDS = tuple(f"R3-H{i:02d}" for i in range(1, 9))
PATCHED_PATHS = (
    "lib/models/spiketrack/sdtv3_search_inference.py",
    "lib/models/spiketrack/spiketrack_inf.py",
    "lib/test/parameter/spiketrack.py",
    "lib/test/tracker/spiketrack_inf.py",
    "tracking/stage4a_spiketrack_smoke.py",
)
# The accepted Figshare package keeps the two Jogging annotations in one
# physical directory.  Stage-4A-E2 records this as a nonmutating evaluator
# alias; it is not a change to any frozen interval or frame bound.
DISCOVERY_SOURCE_ALIASES = {
    "Jogging_1": {
        "path": "Jogging/img",
        "anno_path": "Jogging/groundtruth_rect.1.txt",
        "evidence": "2026-08-25_stage4A_E2_otb_source_manifest.csv row E2-OTB-062",
    }
}
SEED = 20260826


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--slice-csv", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--parity-json", type=Path, required=True)
    parser.add_argument("--external-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=SEED)
    return parser.parse_args()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_lf_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n")


def read_boxes(path: Path) -> np.ndarray:
    rows = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        fields = line.replace("\t", ",").split(",")
        if len(fields) < 4:
            fields = line.split()
        rows.append([float(value) for value in fields[:4]])
    result = np.asarray(rows, dtype=np.float64)
    if result.ndim != 2 or result.shape[1] != 4:
        raise RuntimeError(f"Invalid ground truth shape at {path}: {result.shape}")
    return result


def read_rgb(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Could not read discovery image: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def inclusive_iou(prediction: np.ndarray, ground_truth: np.ndarray) -> float:
    pred = np.asarray(prediction, dtype=np.float64)
    gt = np.asarray(ground_truth, dtype=np.float64)
    top_left = np.maximum(pred[:2], gt[:2])
    bottom_right = np.minimum(pred[:2] + pred[2:] - 1.0, gt[:2] + gt[2:] - 1.0)
    size = np.maximum(bottom_right - top_left + 1.0, 0.0)
    intersection = float(size[0] * size[1])
    union = float(pred[2] * pred[3] + gt[2] * gt[3] - intersection)
    if union <= 0.0:
        raise RuntimeError(f"Non-positive IoU union: pred={pred.tolist()} gt={gt.tolist()}")
    return intersection / union


def inclusive_center_error(prediction: np.ndarray, ground_truth: np.ndarray) -> float:
    pred = np.asarray(prediction, dtype=np.float64)
    gt = np.asarray(ground_truth, dtype=np.float64)
    pred_center = pred[:2] + 0.5 * (pred[2:] - 1.0)
    gt_center = gt[:2] + 0.5 * (gt[2:] - 1.0)
    return float(np.sqrt(np.square(pred_center - gt_center).sum()))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_output(source_root: Path, *arguments: str) -> str:
    command = ["git", "-c", f"safe.directory={source_root.as_posix()}", "-C", str(source_root), *arguments]
    # Keep the leading status column (e.g. `` M``); remove only final newlines.
    return subprocess.check_output(command, text=True).rstrip()


def parse_and_validate_slice(path: Path) -> tuple[list[dict], list[dict], dict]:
    working_bytes = path.read_bytes()
    normalized = working_bytes.replace(b"\r\n", b"\n")
    text = normalized.decode("utf-8-sig")
    rows = list(csv.DictReader(text.splitlines()))
    discovery = [row for row in rows if row["split"] == "DISCOVERY"]
    holdout = [row for row in rows if row["split"] == "HOLDOUT"]
    if tuple(row["pair_id"] for row in discovery) != EXPECTED_DISCOVERY_IDS:
        raise RuntimeError("Frozen discovery IDs/order differ from the locked allowlist")
    if tuple(row["pair_id"] for row in holdout) != EXPECTED_HOLDOUT_IDS:
        raise RuntimeError("Frozen hold-out IDs/order differ from the locked seal")
    if any(row["manager_status"] != "FROZEN" for row in rows):
        raise RuntimeError("At least one frozen-slice row is not FROZEN")
    discovery_sequences = {
        value
        for row in discovery
        for value in (row["primary_sequence"], row["control_sequence"])
    }
    holdout_sequences = {
        value
        for row in holdout
        for value in (row["primary_sequence"], row["control_sequence"])
    }
    if discovery_sequences & holdout_sequences:
        raise RuntimeError("Discovery and hold-out source sequence sets are not disjoint")
    for row in rows:
        for prefix in ("primary", "control"):
            start = int(row[f"{prefix}_start"])
            end = int(row[f"{prefix}_end"])
            if start < 1 or end < start:
                raise RuntimeError(f"Invalid frozen bounds in {row['pair_id']} {prefix}")
        if int(row["primary_end"]) - int(row["primary_start"]) != int(row["control_end"]) - int(row["control_start"]):
            raise RuntimeError(f"Unequal pair interval lengths in {row['pair_id']}")

    # Row hashes are over the exact canonical LF CSV row including its final LF.
    # This avoids platform-dependent checkout CRLF while retaining exact field
    # order, quoting, and values from the committed frozen slice.
    canonical_lines = normalized.splitlines(keepends=True)
    if len(canonical_lines) != len(rows) + 1:
        raise RuntimeError("Unexpected multiline CSV fields in frozen slice")
    row_hashes = {
        row["pair_id"]: sha256_bytes(canonical_lines[index + 1])
        for index, row in enumerate(rows)
    }
    hashes = {
        "canonical_lf_sha256": sha256_bytes(normalized),
        "working_tree_byte_sha256": sha256_bytes(working_bytes),
        "row_hashes": row_hashes,
        "row_hash_semantics": "SHA-256 of the exact canonical-LF CSV data row including final LF",
    }
    return discovery, holdout, hashes


def build_interval_index(discovery: list[dict]) -> tuple[dict, dict]:
    by_sequence: dict[str, list[dict]] = {}
    max_frame: dict[str, int] = {}
    for row in discovery:
        for side in ("primary", "control"):
            sequence = row[f"{side}_sequence"]
            start = int(row[f"{side}_start"])
            end = int(row[f"{side}_end"])
            item = {"pair_id": row["pair_id"], "side": side, "start": start, "end": end}
            by_sequence.setdefault(sequence, []).append(item)
            max_frame[sequence] = max(max_frame.get(sequence, 0), end)
    return by_sequence, max_frame


def labels_for_frame(intervals: list[dict], frame_index: int) -> list[dict]:
    return [item for item in intervals if item["start"] <= frame_index <= item["end"]]


def package_versions(names: tuple[str, ...]) -> dict[str, str | None]:
    result = {}
    for name in names:
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = None
    return result


def environment_payload(torch, args: argparse.Namespace) -> dict:
    try:
        import psutil

        ram_bytes = int(psutil.virtual_memory().total)
        cpu_logical = int(psutil.cpu_count(logical=True) or 0)
        cpu_physical = int(psutil.cpu_count(logical=False) or 0)
    except Exception:
        ram_bytes = None
        cpu_logical = None
        cpu_physical = None
    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)
    return {
        "os": platform.platform(),
        "python": sys.version,
        "executable": sys.executable,
        "cpu": platform.processor(),
        "cpu_logical_count": cpu_logical,
        "cpu_physical_count": cpu_physical,
        "ram_bytes": ram_bytes,
        "gpu": props.name,
        "gpu_total_memory_bytes": int(props.total_memory),
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "cuda_available": bool(torch.cuda.is_available()),
        "dtype": "torch.float32",
        "seed": args.seed,
        "deterministic_settings": {
            "CUBLAS_WORKSPACE_CONFIG": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
            "cudnn_deterministic": bool(torch.backends.cudnn.deterministic),
            "cudnn_benchmark": bool(torch.backends.cudnn.benchmark),
        },
        "packages": package_versions(
            (
                "timm",
                "torchvision",
                "opencv-python",
                "numpy",
                "pandas",
                "scipy",
                "spikingjelly",
                "yacs",
                "einops",
            )
        ),
    }


def configure_diagnostics(tracker, enabled: bool, ablation: str = "none") -> None:
    tracker.stage4a_diagnostics_enabled = bool(enabled)
    tracker.stage4a_ablation = ablation
    tracker.stage4a_diagnostic_records = []
    tracker.network.configure_stage4a_diagnostics(enabled=enabled, ablation=ablation)


def find_tracker_record(records: list[dict]) -> dict | None:
    matches = [record for record in records if record.get("record_type") == "tracker_frame"]
    if len(matches) > 1:
        raise RuntimeError("More than one tracker_frame record emitted for one frame")
    return matches[0] if matches else None


def main() -> None:
    args = parse_args()
    args.source_root = args.source_root.resolve()
    args.dataset_root = args.dataset_root.resolve()
    args.slice_csv = args.slice_csv.resolve()
    args.config = args.config.resolve()
    args.checkpoint = args.checkpoint.resolve()
    args.parity_json = args.parity_json.resolve()
    args.external_root = args.external_root.resolve()
    args.artifact_root = args.artifact_root.resolve()
    for path in (
        args.source_root,
        args.dataset_root,
        args.slice_csv,
        args.config,
        args.checkpoint,
        args.parity_json,
    ):
        if not path.exists():
            raise FileNotFoundError(path)

    # Refuse accidental mixing with an earlier scientific run.
    external_phase_root = args.external_root / "criterionA"
    sentinel_paths = (
        external_phase_root / "baseline_raw_mrm.jsonl",
        args.artifact_root / "baseline_per_frame_metrics.csv",
    )
    if any(path.exists() for path in sentinel_paths):
        raise FileExistsError(f"Criterion-A output already exists: {sentinel_paths}")
    external_phase_root.mkdir(parents=True, exist_ok=True)
    args.artifact_root.mkdir(parents=True, exist_ok=True)

    discovery, holdout, slice_hashes = parse_and_validate_slice(args.slice_csv)
    intervals_by_sequence, max_frame_by_sequence = build_interval_index(discovery)

    source_sha = git_output(args.source_root, "rev-parse", "HEAD")
    if source_sha != PINNED_SOURCE_SHA:
        raise RuntimeError(f"Wrong source SHA: {source_sha}")
    status_lines = [line for line in git_output(args.source_root, "status", "--porcelain").splitlines() if line]
    changed_paths = sorted(line[3:].replace("\\", "/") for line in status_lines)
    if changed_paths != sorted(PATCHED_PATHS):
        raise RuntimeError(f"Patched worktree has unexpected paths: {changed_paths}")
    if sha256_file(args.config) != T1_CONFIG_SHA256:
        raise RuntimeError("T1 config SHA-256 mismatch")
    if sha256_file(args.checkpoint) != T1_CHECKPOINT_SHA256:
        raise RuntimeError("T1 checkpoint SHA-256 mismatch")

    parity = json.loads(args.parity_json.read_text(encoding="utf-8"))
    parity_result = parity.get("clean_pinned_reference_parity") or parity.get("parity")
    if not parity_result or not parity_result.get("pass") or float(parity_result["maximum_observed_abs_diff"]) > 1e-6:
        raise RuntimeError("No-ablation parity is absent or failed")
    parity_summary = {
        "status": "PASS",
        "tolerance": 1e-6,
        "maximum_observed_abs_diff": float(parity_result["maximum_observed_abs_diff"]),
        "source_sha": source_sha,
        "input": parity.get("input"),
        "baseline_output_fingerprints": parity.get("baseline_output_fingerprints"),
        "instrumented_output_fingerprints": parity.get("instrumented_output_fingerprints"),
        "external_raw_path": str(args.parity_json),
        "external_raw_sha256": sha256_file(args.parity_json),
    }
    write_json(args.artifact_root / "no_ablation_parity.json", parity_summary)

    # HOLDOUT rows are consumed only here.  No dataset path is ever resolved.
    holdout_seal_rows = []
    for row in holdout:
        holdout_seal_rows.append(
            {
                "pair_id": row["pair_id"],
                "primary_sequence": row["primary_sequence"],
                "primary_start": row["primary_start"],
                "primary_end": row["primary_end"],
                "control_sequence": row["control_sequence"],
                "control_start": row["control_start"],
                "control_end": row["control_end"],
                "row_sha256_canonical_lf": slice_hashes["row_hashes"][row["pair_id"]],
                "frozen_slice_sha256_canonical_lf": slice_hashes["canonical_lf_sha256"],
                "status": "NOT_EXECUTED_STAGE4B",
            }
        )
    write_csv(
        args.artifact_root / "holdout_seal.csv",
        list(holdout_seal_rows[0]),
        holdout_seal_rows,
    )

    discovery_manifest_rows = []
    for row in discovery:
        for side in ("primary", "control"):
            discovery_manifest_rows.append(
                {
                    "pair_id": row["pair_id"],
                    "side": side,
                    "sequence": row[f"{side}_sequence"],
                    "start": row[f"{side}_start"],
                    "end": row[f"{side}_end"],
                    "event_id": row["primary_event_id"] if side == "primary" else row["control_id"],
                    "source_row_sha256_canonical_lf": slice_hashes["row_hashes"][row["pair_id"]],
                    "status": "AUTHORIZED_DISCOVERY_PENDING_EXECUTION",
                }
            )
    write_csv(
        args.artifact_root / "discovery_execution_manifest.csv",
        list(discovery_manifest_rows[0]),
        discovery_manifest_rows,
    )

    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    os.chdir(args.source_root)
    sys.path.insert(0, str(args.source_root))
    global torch
    import torch

    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.evaluation.otbdataset import OTBDataset
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    if not torch.cuda.is_available():
        raise RuntimeError("Authorized local CUDA GPU is unavailable")

    update_config_from_file(str(args.config))
    if (
        cfg.MODEL.ENCODER.TYPE != "Efficient_Spiking_Transformer_s"
        or cfg.TEST.SEARCH_SIZE != 256
        or cfg.TEST.NUM_TEMPLATES != 1
    ):
        raise RuntimeError("Resolved model is not exact SpikeTrack-S256-T1")
    params = SimpleNamespace(
        cfg=cfg,
        template_factor=cfg.TEST.TEMPLATE_FACTOR,
        template_size=cfg.TEST.TEMPLATE_SIZE,
        search_factor=cfg.TEST.SEARCH_FACTOR,
        search_size=cfg.TEST.SEARCH_SIZE,
        save_all_boxes=False,
        debug=0,
        yaml_name=args.config.stem,
        stage4a_diagnostics=False,
        stage4a_ablation="none",
        stage4a_log_path="",
    )

    official_info = {
        item["name"]: item for item in OTBDataset._get_sequence_info_list(None)
    }
    missing_metadata = sorted(set(intervals_by_sequence) - set(official_info))
    if missing_metadata:
        raise RuntimeError(f"Discovery sequences absent from pinned OTB metadata: {missing_metadata}")

    provenance = {
        "scope": "STAGE4B_DISCOVERY_CRITERION_A_ONLY",
        "source_sha": source_sha,
        "source_root": str(args.source_root),
        "patch_sha256_canonical_lf": PATCH_SHA256_CANONICAL_LF,
        "patch_apply_result": "PASS_CANONICAL_GIT_BLOB_STRICT_WHITESPACE",
        "patched_paths": changed_paths,
        "patched_file_sha256": {
            path: sha256_file(args.source_root / path) for path in PATCHED_PATHS
        },
        "config": str(args.config),
        "config_sha256": sha256_file(args.config),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": sha256_file(args.checkpoint),
        "dataset_root": str(args.dataset_root),
        "frozen_slice": str(args.slice_csv),
        "frozen_slice_sha256_canonical_lf": slice_hashes["canonical_lf_sha256"],
        "frozen_slice_sha256_working_tree_bytes": slice_hashes["working_tree_byte_sha256"],
        "frozen_slice_hash_semantics": (
            "canonical_lf is the committed-content identity and is used in seal rows; "
            "working_tree hash records Windows core.autocrlf checkout bytes"
        ),
        "discovery_pair_ids": list(EXPECTED_DISCOVERY_IDS),
        "discovery_pair_count": len(discovery),
        "holdout_pair_ids_metadata_only": list(EXPECTED_HOLDOUT_IDS),
        "holdout_pair_count": len(holdout),
        "holdout_pairs_executed": 0,
        "official_metadata_source": "pinned lib/test/evaluation/otbdataset.py",
        "accepted_nonmutating_discovery_aliases": DISCOVERY_SOURCE_ALIASES,
        "operational_baseline_boundary": (
            "local paired diagnostic baseline only; no author-released raw-result parity claim"
        ),
        "metric_semantics": (
            "integer persistence via numpy astype(int); pinned inclusive-coordinate IoU/center; "
            "official sequence-first-frame GT override"
        ),
        "environment": environment_payload(torch, args),
        "no_ablation_parity": parity_summary,
    }
    write_json(args.artifact_root / "provenance_environment.json", provenance)

    tracker = SpikeTrack(
        params,
        dataset_name="otb",
        checkpoint_path=str(args.checkpoint),
        save_sfr=False,
    )
    interval_rows: list[dict] = []
    sequence_rows: list[dict] = []
    timing_rows: list[dict] = []
    raw_mrm_path = external_phase_root / "baseline_raw_mrm.jsonl"
    predictions_root = external_phase_root / "baseline_full_predictions"
    predictions_root.mkdir(parents=True, exist_ok=True)
    total_started = time.perf_counter()
    sequence_names = sorted(intervals_by_sequence)
    with raw_mrm_path.open("w", encoding="utf-8", newline="\n") as raw_mrm_stream:
        for sequence_number, sequence_name in enumerate(sequence_names, start=1):
            info = official_info[sequence_name]
            official_start = int(info["startFrame"])
            official_end = int(info["endFrame"])
            max_frame = int(max_frame_by_sequence[sequence_name])
            if official_start != 1:
                raise RuntimeError(
                    f"Discovery sequence {sequence_name} has unsupported non-1 official start {official_start}"
                )
            if max_frame > official_end:
                raise RuntimeError(f"Frozen frame exceeds official sequence end: {sequence_name}")
            effective_info = dict(info)
            effective_info.update(DISCOVERY_SOURCE_ALIASES.get(sequence_name, {}))
            image_dir = args.dataset_root / effective_info["path"]
            gt_path = args.dataset_root / effective_info["anno_path"]
            # The two paths above are discovery-derived only.  No hold-out name
            # can reach this block because sequence_names came from discovery.
            ground_truth = read_boxes(gt_path)
            if len(ground_truth) < max_frame:
                raise RuntimeError(
                    f"Discovery GT truncated: {sequence_name} rows={len(ground_truth)} need={max_frame}"
                )
            frame_paths = [
                image_dir / f"{frame_index:0{int(info['nz'])}d}.{info['ext']}"
                for frame_index in range(official_start, max_frame + 1)
            ]
            missing_frames = [str(path) for path in frame_paths if not path.is_file()]
            if missing_frames:
                raise RuntimeError(
                    f"Discovery source-integrity defect {sequence_name}: missing {missing_frames[:3]}"
                )

            configure_diagnostics(tracker, False)
            init_box = ground_truth[0].tolist()
            tracker.initialize(read_rgb(frame_paths[0]), {"init_bbox": init_box})
            float_predictions = [np.asarray(init_box, dtype=np.float64)]
            int_predictions = [np.asarray(init_box, dtype=np.float64).astype(np.int64)]
            sequence_started = time.perf_counter()

            # Record initialization-frame interval metrics where applicable.
            first_labels = labels_for_frame(intervals_by_sequence[sequence_name], 1)
            for label in first_labels:
                metric_prediction = ground_truth[0]
                interval_rows.append(
                    {
                        "pair_id": label["pair_id"],
                        "side": label["side"],
                        "sequence": sequence_name,
                        "frame_index": 1,
                        "pred_x_float": init_box[0],
                        "pred_y_float": init_box[1],
                        "pred_w_float": init_box[2],
                        "pred_h_float": init_box[3],
                        "pred_x_int": int_predictions[0][0],
                        "pred_y_int": int_predictions[0][1],
                        "pred_w_int": int_predictions[0][2],
                        "pred_h_int": int_predictions[0][3],
                        "gt_x": ground_truth[0][0],
                        "gt_y": ground_truth[0][1],
                        "gt_w": ground_truth[0][2],
                        "gt_h": ground_truth[0][3],
                        "iou": inclusive_iou(metric_prediction, ground_truth[0]),
                        "iou_float": inclusive_iou(float_predictions[0], ground_truth[0]),
                        "failure": 0,
                        "success_at_0_5": 1,
                        "center_error": 0.0,
                        "score_map_max": "",
                        "confidence_score": "",
                        "model_forward_ms": "",
                        "initialization_frame": True,
                        "evaluator_first_frame_override": True,
                        "tracker_mode": "T1",
                        "ablation_control": "none",
                        "physical_skip": False,
                    }
                )

            diagnostics_enabled = False
            for frame_index, image_path in enumerate(frame_paths[1:], start=2):
                labels = labels_for_frame(intervals_by_sequence[sequence_name], frame_index)
                should_enable = bool(labels)
                if should_enable != diagnostics_enabled:
                    configure_diagnostics(tracker, should_enable, "none")
                    diagnostics_enabled = should_enable
                output, _, _ = tracker.track(read_rgb(image_path), {})
                float_box = np.asarray(output["target_bbox"], dtype=np.float64)
                int_box = float_box.astype(np.int64)
                float_predictions.append(float_box)
                int_predictions.append(int_box)
                records = tracker.consume_stage4a_diagnostic_records() if should_enable else []
                tracker_record = find_tracker_record(records)
                if should_enable and tracker_record is None:
                    raise RuntimeError(f"Missing tracker diagnostic record: {sequence_name} {frame_index}")
                for record in records:
                    enriched = dict(record)
                    enriched["sequence"] = sequence_name
                    enriched["evaluator_frame_index"] = frame_index
                    enriched["frozen_labels"] = [
                        {"pair_id": label["pair_id"], "side": label["side"]}
                        for label in labels
                    ]
                    raw_mrm_stream.write(json.dumps(enriched, sort_keys=True) + "\n")
                gt_box = ground_truth[frame_index - 1]
                primary_iou = inclusive_iou(int_box, gt_box)
                for label in labels:
                    interval_rows.append(
                        {
                            "pair_id": label["pair_id"],
                            "side": label["side"],
                            "sequence": sequence_name,
                            "frame_index": frame_index,
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
                            "iou": primary_iou,
                            "iou_float": inclusive_iou(float_box, gt_box),
                            "failure": int(primary_iou < 0.5),
                            "success_at_0_5": int(primary_iou >= 0.5),
                            "center_error": inclusive_center_error(int_box, gt_box),
                            "score_map_max": tracker_record["score_map_max"],
                            "confidence_score": tracker_record["confidence_score"],
                            "model_forward_ms": tracker_record["total_tracker_model_forward_ms"],
                            "initialization_frame": False,
                            "evaluator_first_frame_override": False,
                            "tracker_mode": "T1",
                            "ablation_control": "none",
                            "physical_skip": False,
                        }
                    )
                for record in records:
                    if record.get("record_type") == "mrm":
                        timing_rows.append(
                            {
                                "sequence": sequence_name,
                                "frame_index": frame_index,
                                "mrm_id": record["mrm_id"],
                                "ablation_control": record["ablation_control"],
                                "retriever_latency_ms": record["retriever_latency_ms"],
                                "mlp_latency_ms": record["mlp_latency_ms"],
                                "total_mrm_compute_latency_ms": record["total_mrm_compute_latency_ms"],
                                "diagnostic_norm_fingerprint_overhead_ms": record[
                                    "diagnostic_norm_fingerprint_overhead_ms"
                                ],
                                "total_instrumented_mrm_latency_ms": record[
                                    "total_instrumented_mrm_latency_ms"
                                ],
                                "physical_skip": record["physical_skip"],
                            }
                        )

            configure_diagnostics(tracker, False)
            prediction_path = predictions_root / f"{sequence_name}.csv"
            full_rows = []
            for index, (float_box, int_box) in enumerate(zip(float_predictions, int_predictions), start=1):
                full_rows.append(
                    {
                        "sequence": sequence_name,
                        "frame_index": index,
                        "pred_x_float": float_box[0],
                        "pred_y_float": float_box[1],
                        "pred_w_float": float_box[2],
                        "pred_h_float": float_box[3],
                        "pred_x_int": int_box[0],
                        "pred_y_int": int_box[1],
                        "pred_w_int": int_box[2],
                        "pred_h_int": int_box[3],
                    }
                )
            write_csv(prediction_path, list(full_rows[0]), full_rows)
            sequence_elapsed = time.perf_counter() - sequence_started
            sequence_rows.append(
                {
                    "sequence": sequence_name,
                    "official_start_frame": official_start,
                    "executed_through_frame": max_frame,
                    "initialized_once_from_official_start": True,
                    "frames_processed_including_initialization": len(frame_paths),
                    "prediction_path_external": str(prediction_path),
                    "prediction_sha256": sha256_file(prediction_path),
                    "elapsed_seconds_excluding_initialization": sequence_elapsed,
                    "status": "COMPLETE",
                }
            )
            print(
                f"PROGRESS {sequence_number}/{len(sequence_names)} {sequence_name} "
                f"through={max_frame} elapsed={sequence_elapsed:.1f}s",
                flush=True,
            )

    expected_interval_frames = sum(
        int(row["primary_end"]) - int(row["primary_start"]) + 1
        + int(row["control_end"]) - int(row["control_start"]) + 1
        for row in discovery
    )
    if len(interval_rows) != expected_interval_frames:
        raise RuntimeError(
            f"Incomplete frozen interval metrics: got {len(interval_rows)} expected {expected_interval_frames}"
        )
    observed_coverage = {
        (row["pair_id"], row["side"], int(row["frame_index"])) for row in interval_rows
    }
    for row in discovery:
        for side in ("primary", "control"):
            for frame_index in range(int(row[f"{side}_start"]), int(row[f"{side}_end"]) + 1):
                if (row["pair_id"], side, frame_index) not in observed_coverage:
                    raise RuntimeError(f"Missing frozen metric {row['pair_id']} {side} {frame_index}")

    interval_fields = [
        "pair_id", "side", "sequence", "frame_index",
        "pred_x_float", "pred_y_float", "pred_w_float", "pred_h_float",
        "pred_x_int", "pred_y_int", "pred_w_int", "pred_h_int",
        "gt_x", "gt_y", "gt_w", "gt_h", "iou", "iou_float", "failure",
        "success_at_0_5", "center_error", "score_map_max", "confidence_score",
        "model_forward_ms", "initialization_frame", "evaluator_first_frame_override",
        "tracker_mode", "ablation_control", "physical_skip",
    ]
    write_csv(args.artifact_root / "baseline_per_frame_metrics.csv", interval_fields, interval_rows)
    write_csv(args.artifact_root / "baseline_sequence_execution.csv", list(sequence_rows[0]), sequence_rows)
    write_csv(args.artifact_root / "module_timing_characterization.csv", list(timing_rows[0]), timing_rows)
    discovery_manifest_complete = [dict(row, status="EXECUTED_STAGE4B_CRITERION_A") for row in discovery_manifest_rows]
    write_csv(
        args.artifact_root / "discovery_execution_manifest.csv",
        list(discovery_manifest_complete[0]),
        discovery_manifest_complete,
    )
    execution_summary = {
        "status": "CRITERION_A_BASELINE_EXECUTION_COMPLETE_ANALYSIS_PENDING",
        "discovery_pairs_executed": len(discovery),
        "holdout_pairs_executed": 0,
        "unique_discovery_source_sequences_executed": len(sequence_rows),
        "frozen_interval_frames": len(interval_rows),
        "raw_mrm_external_path": str(raw_mrm_path),
        "raw_mrm_sha256": sha256_file(raw_mrm_path),
        "elapsed_seconds": time.perf_counter() - total_started,
    }
    write_json(args.artifact_root / "criterionA_execution_summary.json", execution_summary)
    print(json.dumps(execution_summary, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
