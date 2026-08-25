"""Audit the bounded Stage-4A-E2 official-runner outputs.

This script never invokes a tracker.  It reads the six already persisted E2
predictions, the acquired OTB ground truth, the prior committed local official
predictions, and the author-released S256-T1 predictions.  Metric semantics are
the exact Stage-4A-R method: ``calc_seq_err_robust`` with OTB, float64 boxes,
thresholds 0.00..1.00 in 0.05 steps, and strict overlap > threshold.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import shutil
import sys

import cv2
import numpy as np
import torch


Q1_ROOT = Path(r"E:\Robot_Backup\Embodied-Tracking-Problem-Research")
ARTIFACT_ROOT = (
    Q1_ROOT / "screening/codex/artifacts/stage4A_E2/reproduction"
)
TOP_LEVEL_CSV = (
    Q1_ROOT / "screening/codex/2026-08-25_stage4A_E2_reproduction.csv"
)
SOURCE_ROOT = Path(r"E:\Robot_Backup\tmp\stage4A_R_official_source")
CONFIG = SOURCE_ROOT / "experiments/spiketrack/spiketrack_s256_t1.yaml"
CHECKPOINT = Path(
    r"E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar"
)
E2_ROOT = Path(r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1")
ACQUIRED_ROOT = E2_ROOT / "extracted/OTB2015"
EXTERNAL_RESULTS = E2_ROOT / "stage4a_e2_results"
EXTERNAL_SUPPORT = EXTERNAL_RESULTS / "runner_support"
EXTERNAL_RUNS = EXTERNAL_RESULTS / "runs"
PRIOR_ROOT = (
    Q1_ROOT
    / "screening/codex/artifacts/stage4A_reproduction/official_runner_default_run1"
)
RELEASED_ROOT = (
    Q1_ROOT / "screening/codex/artifacts/stage4A_reproduction/released_raw"
)
SEQUENCES = ("Deer", "Crossing", "Couple")
EXPECTED_ROWS = {"Deer": 71, "Crossing": 120, "Couple": 140}
E2_RUN_IDS = {
    "official_default": {
        "Deer": "E2-RUN-001",
        "Crossing": "E2-RUN-002",
        "Couple": "E2-RUN-003",
    },
    "deterministic": {
        "Deer": "E2-RUN-004",
        "Crossing": "E2-RUN-005",
        "Couple": "E2-RUN-006",
    },
}
GT_SHA256 = {
    "Deer": "f22bd21c55d23f24371993e4e5f36b09b744a204953a7de4654e99358900ad59",
    "Crossing": "3588d1821b80f8bc7f88645cbfca32454d474135d7841f85b304615fecf54ac4",
    "Couple": "43c6d304f9f65b28940389429dfdbd33e544075c6b8d3c00e0c72558dac55d10",
}
CONFIG_SHA256 = "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
CHECKPOINT_SHA256 = "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
PINNED_COMMIT = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
INVENTORY_SHA256 = "8cd2ab115a361fb99afd24a1aa6e1bc1931c48de3ed050fb3f53893d2a32bcc6"
PRIOR_DATASET_ROOTS = {
    "Deer": Path(
        r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified\TRACA-master\sequence\Deer"
    ),
    "Crossing": Path(
        r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified\ECO-master\sequences\Crossing"
    ),
    "Couple": Path(
        r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified\SRDCF\SRDCF\sequences\Couple"
    ),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_boxes(path: Path) -> np.ndarray:
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        fields = line.strip().replace("\t", ",").split(",")
        if len(fields) < 4:
            fields = line.split()
        if len(fields) >= 4:
            rows.append([float(value) for value in fields[:4]])
    return np.asarray(rows, dtype=np.float64)


def stable_box_value(value: float):
    value = float(value)
    return int(value) if value.is_integer() else value


def rows_json(boxes: np.ndarray) -> str:
    return json.dumps(
        [[stable_box_value(value) for value in row] for row in boxes],
        separators=(",", ":"),
    )


def row_json(box: np.ndarray) -> str:
    return json.dumps(
        [stable_box_value(value) for value in box], separators=(",", ":")
    )


def success_auc(prediction: np.ndarray, ground_truth: np.ndarray, calculator) -> float:
    overlap, _, _, _ = calculator(
        torch.tensor(prediction, dtype=torch.float64),
        torch.tensor(ground_truth, dtype=torch.float64),
        dataset="otb",
        target_visible=None,
    )
    thresholds = torch.arange(0.0, 1.0 + 0.05, 0.05, dtype=torch.float64)
    success = (
        (overlap.view(-1, 1) > thresholds.view(1, -1)).sum(0).double()
        / ground_truth.shape[0]
    )
    return float(success.mean().item() * 100.0)


def inclusive_iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    ax1, ay1, aw, ah = box_a
    bx1, by1, bw, bh = box_b
    ax2, ay2 = ax1 + aw - 1.0, ay1 + ah - 1.0
    bx2, by2 = bx1 + bw - 1.0, by1 + bh - 1.0
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1 + 1.0), max(0.0, iy2 - iy1 + 1.0)
    intersection = iw * ih
    union = (
        max(0.0, aw) * max(0.0, ah)
        + max(0.0, bw) * max(0.0, bh)
        - intersection
    )
    return intersection / union if union > 0.0 else 0.0


def first_true(mask: np.ndarray):
    indices = np.flatnonzero(mask)
    return int(indices[0]) if len(indices) else None


def frame_or_na(index) -> str | int:
    return "NA" if index is None else index + 1


def format_number(value: float, digits: str = ".15g") -> str:
    return format(float(value), digits)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    if not rows:
        raise RuntimeError(f"No rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def relative_q1(path: Path) -> str:
    return path.relative_to(Q1_ROOT).as_posix()


def external_prediction(mode: str, sequence: str) -> Path:
    return (
        EXTERNAL_RUNS
        / mode
        / sequence
        / "tracking_results/spiketrack/spiketrack_s256_t1/otb"
        / f"{sequence}.txt"
    )


def copy_method_artifacts():
    copy_map = {
        EXTERNAL_SUPPORT / "run_preconditions.csv": ARTIFACT_ROOT / "commands.csv",
        EXTERNAL_SUPPORT / "run_execution_manifest.csv": ARTIFACT_ROOT / "run_manifest.csv",
        EXTERNAL_SUPPORT / "mini_root_manifest.csv": ARTIFACT_ROOT / "mini_root_manifest.csv",
        EXTERNAL_SUPPORT / "real_copy_verification.csv": ARTIFACT_ROOT / "real_copy_verification.csv",
        EXTERNAL_SUPPORT / "predeclared_six_run_contract.initial.csv": ARTIFACT_ROOT / "predeclared_six_run_contract.initial.csv",
        EXTERNAL_SUPPORT / "predeclared_six_run_contract.csv": ARTIFACT_ROOT / "predeclared_six_run_contract.final.csv",
        EXTERNAL_SUPPORT / "execute_six_runs.ps1": ARTIFACT_ROOT / "execute_six_runs.ps1",
        EXTERNAL_SUPPORT / "verify_mini_copy.py": ARTIFACT_ROOT / "verify_mini_copy.py",
        EXTERNAL_SUPPORT / "build_mini_root_manifest.py": ARTIFACT_ROOT / "build_mini_root_manifest.py",
        EXTERNAL_SUPPORT / "make_otb_loader_stubs_e2.py": ARTIFACT_ROOT / "make_otb_loader_stubs_e2.py",
        EXTERNAL_SUPPORT / "local.py": ARTIFACT_ROOT / "staged_local_runtime_config.py",
        EXTERNAL_SUPPORT / "deterministic/sitecustomize.py": ARTIFACT_ROOT / "deterministic_sitecustomize.py",
    }
    for source, destination in copy_map.items():
        if not source.is_file():
            raise FileNotFoundError(source)
        shutil.copyfile(source, destination)


def build_rows():
    sys.path.insert(0, str(SOURCE_ROOT))
    from lib.test.analysis.extract_results import calc_seq_err_robust

    prediction_root = ARTIFACT_ROOT / "predictions"
    default_repo_root = prediction_root / "acquired_default"
    deterministic_repo_root = prediction_root / "acquired_deterministic"
    default_repo_root.mkdir(parents=True, exist_ok=True)
    deterministic_repo_root.mkdir(parents=True, exist_ok=True)

    rows = []
    sequence_summary = []
    for sequence in SEQUENCES:
        gt_path = ACQUIRED_ROOT / sequence / "groundtruth_rect.txt"
        if sha256_file(gt_path) != GT_SHA256[sequence]:
            raise RuntimeError(f"{sequence}: acquired GT hash changed")
        ground_truth = read_boxes(gt_path)
        if len(ground_truth) != EXPECTED_ROWS[sequence]:
            raise RuntimeError(f"{sequence}: acquired GT row mismatch")

        external_default = external_prediction("official_default", sequence)
        external_deterministic = external_prediction("deterministic", sequence)
        repo_default = default_repo_root / f"{sequence}.txt"
        repo_deterministic = deterministic_repo_root / f"{sequence}.txt"
        shutil.copyfile(external_default, repo_default)
        shutil.copyfile(external_deterministic, repo_deterministic)

        prior_path = PRIOR_ROOT / f"{sequence}.txt"
        released_path = RELEASED_ROOT / f"{sequence}.txt"
        role_paths = (
            (
                "acquired_source_default",
                E2_RUN_IDS["official_default"][sequence],
                "official_default",
                repo_default,
                EXTERNAL_RESULTS / "evaluator_otb3" / sequence,
                CONFIG_SHA256,
                CHECKPOINT_SHA256,
                "Verified byte-identical staging copy of the newly acquired Figshare source; official process-default runtime.",
            ),
            (
                "acquired_source_deterministic",
                E2_RUN_IDS["deterministic"][sequence],
                "deterministic",
                repo_deterministic,
                EXTERNAL_RESULTS / "evaluator_otb3" / sequence,
                CONFIG_SHA256,
                CHECKPOINT_SHA256,
                "Verified byte-identical staging copy of the newly acquired Figshare source; locked deterministic characterization runtime.",
            ),
            (
                "prior_committed_local_official",
                "STAGE4A_R_OFFICIAL_DEFAULT_RUN1",
                "official_default",
                prior_path,
                PRIOR_DATASET_ROOTS[sequence],
                CONFIG_SHA256,
                CHECKPOINT_SHA256,
                "Previously committed local official-runner prediction; metric recomputed against acquired GT.",
            ),
            (
                "author_released_s256_t1",
                "AUTHOR_RELEASED_S256_T1_RAW",
                "unknown_author_mode",
                released_path,
                Path("UNKNOWN_NOT_RECORDED_IN_RELEASE"),
                "UNKNOWN_NOT_IN_RELEASED_ARCHIVE",
                "UNKNOWN_NOT_IN_RELEASED_ARCHIVE",
                "Author-released S256-T1 raw prediction; release contains no runtime manifest.",
            ),
        )

        default_boxes = read_boxes(repo_default)
        deterministic_boxes = read_boxes(repo_deterministic)
        prior_boxes = read_boxes(prior_path)
        released_boxes = read_boxes(released_path)
        for name, boxes in {
            "default": default_boxes,
            "deterministic": deterministic_boxes,
            "prior": prior_boxes,
            "released": released_boxes,
        }.items():
            if len(boxes) != EXPECTED_ROWS[sequence]:
                raise RuntimeError(f"{sequence}/{name}: prediction row mismatch")

        released_auc = success_auc(released_boxes, ground_truth, calc_seq_err_robust)
        default_deterministic_identical = (
            repo_default.read_bytes() == repo_deterministic.read_bytes()
            and np.array_equal(default_boxes, deterministic_boxes)
        )
        acquired_changed_local = not (
            repo_default.read_bytes() == prior_path.read_bytes()
            and repo_deterministic.read_bytes() == prior_path.read_bytes()
            and np.array_equal(default_boxes, prior_boxes)
            and np.array_equal(deterministic_boxes, prior_boxes)
        )

        for (
            comparison_role,
            run_id,
            runtime_mode,
            prediction_path,
            source_dataset_path,
            config_sha,
            checkpoint_sha,
            notes,
        ) in role_paths:
            prediction = read_boxes(prediction_path)
            auc = success_auc(prediction, ground_truth, calc_seq_err_robust)
            is_released = comparison_role == "author_released_s256_t1"
            byte_identical_released = prediction_path.read_bytes() == released_path.read_bytes()
            box_identical_released = bool(np.array_equal(prediction, released_boxes))
            component_difference = np.abs(prediction - released_boxes)
            if is_released:
                first_difference = None
                first_iou_95 = None
                first_iou_75 = None
                maximum_component = "NA"
                maximum_frame = "NA"
            else:
                first_difference = first_true(np.any(component_difference != 0.0, axis=1))
                ious = np.asarray(
                    [inclusive_iou(local, released) for local, released in zip(prediction, released_boxes)]
                )
                first_iou_95 = first_true(ious < 0.95)
                first_iou_75 = first_true(ious < 0.75)
                if first_difference is None:
                    maximum_component = "0"
                    maximum_frame = "NA"
                else:
                    per_frame_max = component_difference.max(axis=1)
                    maximum_index = int(np.argmax(per_frame_max))
                    maximum_component = format_number(per_frame_max[maximum_index], ".17g")
                    maximum_frame = maximum_index + 1

            row = {
                "sequence": sequence,
                "comparison_role": comparison_role,
                "run_id": run_id,
                "runtime_mode": runtime_mode,
                "source_dataset_path": str(source_dataset_path),
                "ground_truth_sha256": GT_SHA256[sequence],
                "config_sha256": config_sha,
                "checkpoint_sha256": checkpoint_sha,
                "prediction_path": relative_q1(prediction_path),
                "prediction_sha256": sha256_file(prediction_path),
                "row_count": len(prediction),
                "first_five_rows": rows_json(prediction[:5]),
                "last_row": row_json(prediction[-1]),
                "success_auc_percent": format_number(auc),
                "released_success_auc_percent": format_number(released_auc),
                "difference_from_released_percentage_points": (
                    "0" if is_released else format_number(abs(auc - released_auc))
                ),
                "first_frame_different_from_released": (
                    "NA" if is_released else frame_or_na(first_difference)
                ),
                "first_iou_below_0_95_frame": (
                    "NA" if is_released else frame_or_na(first_iou_95)
                ),
                "first_iou_below_0_75_frame": (
                    "NA" if is_released else frame_or_na(first_iou_75)
                ),
                "maximum_component_divergence": maximum_component,
                "maximum_component_divergence_frame": maximum_frame,
                "byte_identical_to_released": byte_identical_released,
                "box_identical_to_released": box_identical_released,
                "default_deterministic_identical": default_deterministic_identical,
                "byte_identical_to_prior_local": prediction_path.read_bytes()
                == prior_path.read_bytes(),
                "acquired_data_changed_local_prediction": acquired_changed_local,
                "notes": notes
                + " Difference is absolute percentage points; frame indices are one-based; IoU uses inclusive OTB box geometry.",
            }
            rows.append(row)

        sequence_summary.append(
            {
                "sequence": sequence,
                "acquired_default_sha256": sha256_file(repo_default),
                "acquired_deterministic_sha256": sha256_file(repo_deterministic),
                "prior_local_sha256": sha256_file(prior_path),
                "released_sha256": sha256_file(released_path),
                "default_equals_deterministic": default_deterministic_identical,
                "default_equals_prior_local": repo_default.read_bytes()
                == prior_path.read_bytes(),
                "deterministic_equals_prior_local": repo_deterministic.read_bytes()
                == prior_path.read_bytes(),
                "acquired_data_changed_local_prediction": acquired_changed_local,
            }
        )

    return rows, sequence_summary


def build_environment(sequence_summary: list[dict]):
    run_rows = list(
        csv.DictReader(
            (EXTERNAL_SUPPORT / "run_execution_manifest.csv").open(
                encoding="utf-8-sig", newline=""
            )
        )
    )
    environment = {
        "scope": "STAGE4A_E2_THREE_SEQUENCE_OFFICIAL_RUNNER_ONLY",
        "inventory_independence_gate": {
            "sha256": INVENTORY_SHA256,
            "rows": 100,
            "unique_canonical_sequences": 100,
            "all_manager_review_status_pending": True,
            "gate_completed_before_any_tracker_output": True,
        },
        "source_contract": {
            "source_root": str(SOURCE_ROOT),
            "pinned_commit": PINNED_COMMIT,
            "tracked_diff_after_runs": "CLEAN",
            "config": str(CONFIG),
            "config_sha256": CONFIG_SHA256,
            "checkpoint": str(CHECKPOINT),
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "runner_chain": [
                "tracking/test.py",
                "OTBDataset",
                "Tracker.run_sequence",
                "Tracker._read_image",
                "lib/test/tracker/spiketrack_inf.py",
                "integer result persistence",
            ],
        },
        "windows_python_environment": {
            "operating_system": platform.platform(),
            "python": platform.python_version(),
            "python_executable": sys.executable,
            "torch": torch.__version__,
            "torchvision": importlib.metadata.version("torchvision"),
            "timm": importlib.metadata.version("timm"),
            "opencv": cv2.__version__,
            "numpy": np.__version__,
            "cuda_build": torch.version.cuda,
            "cudnn": torch.backends.cudnn.version(),
            "device": "NVIDIA GeForce MX250 2048 MiB",
            "dtype": "torch.float32",
            "evidence_boundary": "desktop development/reproduction evidence only",
        },
        "runtime_modes": {
            "official_default": {
                "forced_seed": False,
                "PYTHONPATH": "REMOVED",
                "PYTHONHASHSEED": "REMOVED",
                "CUBLAS_WORKSPACE_CONFIG": "REMOVED",
            },
            "deterministic": {
                "seed": 20260825,
                "PYTHONHASHSEED": "20260825",
                "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
                "sitecustomize_sha256": "56284cd8e1fd12ec564f460714f787dcd71c91a1550fb616be34da457aabaee1",
                "torch_deterministic_algorithms": True,
                "cudnn_deterministic": True,
                "cudnn_benchmark": False,
            },
        },
        "staging": {
            "acquired_root": str(ACQUIRED_ROOT),
            "mini_root": str(EXTERNAL_RESULTS / "evaluator_otb3"),
            "requested_junction_result": "FAILED_INCORRECT_FUNCTION",
            "filesystem": "exFAT_NO_REPARSE_POINT_SUPPORT",
            "authorized_fallback": "BYTE_COPY_ONLY_DEER_CROSSING_COUPLE",
            "per_file_sha256_verification": "PASS",
            "other_97_records": "METADATA_ONLY_GT_STUBS_NO_IMAGES",
        },
        "runs": run_rows,
        "sequence_identity_result": sequence_summary,
        "timing_boundary": "External timing files retained but no speed claim is made.",
        "linux_setup": "NOT_PERFORMED",
        "stage4b": "LOCKED",
    }
    (ARTIFACT_ROOT / "environment.json").write_text(
        json.dumps(environment, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_summary(rows: list[dict], sequence_summary: list[dict]):
    if all(not item["acquired_data_changed_local_prediction"] for item in sequence_summary):
        recommendation = "E2_DATA_IDENTITY_NOT_CAUSE"
    elif all(
        row["box_identical_to_released"]
        for row in rows
        if row["comparison_role"].startswith("acquired_source_")
    ):
        recommendation = "E2_DATA_IDENTITY_EXPLAINS_MISMATCH"
    else:
        recommendation = "E2_REPRODUCTION_PENDING"

    lines = [
        "# Stage 4A-E2 bounded reproduction validation",
        "",
        "- Inventory gate: PASS — 100 unique canonical rows, all PENDING, completed before tracker output.",
        "- Executed scope: exactly Deer, Crossing, Couple; one official-default and one deterministic process each.",
        "- Run validation: six exit-code-0 runs; result and time files present; row counts 71/120/140.",
        "- Source cleanup: original untracked local.py restored to SHA-256 `e76f5713bac3f31b3b587f4fe869aea25aeceeab5cb45b2800c46a76d7aff6fb`; tracked diff clean.",
        "- Staging: F: exFAT rejected directory junctions with `Incorrect function`; authorized three-directory byte-copy fallback passed relative-file-set and every-file SHA-256 checks.",
        "- Timing files remain external and are not used for a speed claim.",
        f"- Evidence recommendation: `{recommendation}`.",
        "",
        "| Sequence | Acquired default = deterministic | Acquired default = prior local | Data changed local prediction |",
        "|---|---:|---:|---:|",
    ]
    for item in sequence_summary:
        lines.append(
            f"| {item['sequence']} | {item['default_equals_deterministic']} | "
            f"{item['default_equals_prior_local']} | "
            f"{item['acquired_data_changed_local_prediction']} |"
        )
    lines.extend(
        [
            "",
            "This recommendation is an E2 evidence label only. It is not DIAG_PASS/FAIL and does not authorize Stage 4B.",
        ]
    )
    (ARTIFACT_ROOT / "validation_summary.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n"
    )
    return recommendation


def build_artifact_manifest():
    rows = []
    for path in sorted(ARTIFACT_ROOT.rglob("*")):
        if not path.is_file() or path.name == "artifact_manifest.csv":
            continue
        rows.append(
            {
                "path": path.relative_to(ARTIFACT_ROOT).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "content_boundary": (
                    "PREDICTION_TEXT_ONLY"
                    if "predictions" in path.parts
                    else "SMALL_TEXT_AUDIT_ARTIFACT"
                ),
            }
        )
    write_csv(ARTIFACT_ROOT / "artifact_manifest.csv", rows)


def main():
    if sha256_file(CONFIG) != CONFIG_SHA256:
        raise RuntimeError("Config hash mismatch")
    if sha256_file(CHECKPOINT) != CHECKPOINT_SHA256:
        raise RuntimeError("Checkpoint hash mismatch")
    inventory = Q1_ROOT / "screening/codex/2026-08-25_stage4A_E2_slice_inventory.csv"
    if sha256_file(inventory) != INVENTORY_SHA256:
        raise RuntimeError("Inventory gate artifact changed")
    copy_method_artifacts()
    rows, sequence_summary = build_rows()
    if len(rows) != 12:
        raise RuntimeError(f"Expected 12 comparison rows, got {len(rows)}")
    write_csv(TOP_LEVEL_CSV, rows)
    build_environment(sequence_summary)
    recommendation = build_summary(rows, sequence_summary)
    build_artifact_manifest()
    print(f"E2_AUDIT=PASS")
    print(f"COMPARISON_ROWS={len(rows)}")
    print(f"RECOMMENDATION={recommendation}")


if __name__ == "__main__":
    main()
