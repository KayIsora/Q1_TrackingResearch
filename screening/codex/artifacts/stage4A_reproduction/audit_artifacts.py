"""Build auditable Stage-4A-R text artifacts; this is not a tracking adapter.

The sequence set is fixed to Deer, Crossing, and Couple. Selection predates and
is independent of every prediction compared here. Large images, checkpoints,
and the released ZIP remain outside the Q1 repository.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys
import zipfile

import cv2
import numpy as np
import torch


ARTIFACT_ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = Path(r"E:\Robot_Backup\tmp\stage4A_R_official_source")
ZIP_PATH = Path(r"E:\Robot_Backup\tmp\spiketrack_s256_t1_raw.zip")
EXTRACTED_RAW_ROOT = Path(r"E:\Robot_Backup\tmp\spiketrack_s256_t1_raw")
RUN_ROOT = Path(r"E:\Robot_Backup\tmp\stage4A_R_runs")
CHECKPOINT = Path(
    r"E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar"
)
CONFIG = SOURCE_ROOT / "experiments/spiketrack/spiketrack_s256_t1.yaml"
PREVIOUS_ADAPTER_SOURCE = Path(r"E:\Robot_Backup\tmp\stage4a_bounded_repro.py")
PREVIOUS_ADAPTER_RUN = Path(
    r"E:\Robot_Backup\tmp\stage4A_bounded_reproduction_official_save.json"
)
CURRENT_ADAPTER_RUN = RUN_ROOT / "adapter_deterministic.json"
AUDITABLE_ADAPTER = (
    ARTIFACT_ROOT.parent.parent
    / "scripts/2026-08-25_stage4A_spiketrack_reproduce3.py"
)
PINNED_COMMIT = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
SEQUENCES = ("Deer", "Crossing", "Couple")
EXPECTED_FRAMES = {"Deer": 71, "Crossing": 120, "Couple": 140}

COPY_ROOTS = {
    "Deer": (
        (
            "SRC1_PREVIOUS_ADAPTER",
            Path(
                r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified"
                r"\TRACA-master\sequence\Deer"
            ),
            "preexisting copy used by the exact previous adapter",
        ),
        (
            "SRC2_ARCHIVED_DUPLICATE",
            Path(
                r"E:\Robot_Backup\Crash_NotUse_Yet\TrackingResearch\OtherTracker"
                r"\verified\TRACA-master\sequence\Deer"
            ),
            "second preexisting workspace copy found by path search",
        ),
        (
            "SRC3_SCT4_COPY",
            Path(
                r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified"
                r"\SCT4\SCT4\Deer"
            ),
            "third preexisting workspace copy found in SCT4; GT filename is groundtruth.txt",
        ),
        (
            "SRC4_SCT4_ARCHIVED_DUPLICATE",
            Path(
                r"E:\Robot_Backup\Crash_NotUse_Yet\TrackingResearch\OtherTracker"
                r"\verified\SCT4\SCT4\Deer"
            ),
            "fourth preexisting workspace copy found in archived SCT4; GT filename is groundtruth.txt",
        ),
        (
            "STAGED_MINIROOT",
            Path(r"E:\Robot_Backup\tmp\stage4A_R_otb3\Deer"),
            "external derivative copied from SRC1 for the official runner",
        ),
    ),
    "Crossing": (
        (
            "SRC1_PREVIOUS_ADAPTER",
            Path(
                r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified"
                r"\ECO-master\sequences\Crossing"
            ),
            "preexisting copy used by the exact previous adapter",
        ),
        (
            "SRC2_ARCHIVED_DUPLICATE",
            Path(
                r"E:\Robot_Backup\Crash_NotUse_Yet\TrackingResearch\OtherTracker"
                r"\verified\ECO-master\sequences\Crossing"
            ),
            "second preexisting workspace copy found by path search",
        ),
        (
            "STAGED_MINIROOT",
            Path(r"E:\Robot_Backup\tmp\stage4A_R_otb3\Crossing"),
            "external derivative copied from SRC1 for the official runner",
        ),
    ),
    "Couple": (
        (
            "SRC1_PREVIOUS_ADAPTER",
            Path(
                r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified"
                r"\SRDCF\SRDCF\sequences\Couple"
            ),
            "preexisting copy used by the exact previous adapter",
        ),
        (
            "SRC2_ARCHIVED_DUPLICATE",
            Path(
                r"E:\Robot_Backup\Crash_NotUse_Yet\TrackingResearch\OtherTracker"
                r"\verified\SRDCF\SRDCF\sequences\Couple"
            ),
            "second preexisting workspace copy found by path search",
        ),
        (
            "STAGED_MINIROOT",
            Path(r"E:\Robot_Backup\tmp\stage4A_R_otb3\Couple"),
            "external derivative copied from SRC1 for the official runner",
        ),
    ),
}

RUNS = {
    "adapter_deterministic": (
        "adapter",
        "deterministic",
        lambda sequence: RUN_ROOT / f"adapter_deterministic_{sequence}_local.txt",
    ),
    "official_runner_deterministic": (
        "official_runner",
        "deterministic",
        lambda sequence: RUN_ROOT
        / "official_runner_deterministic/tracking_results/spiketrack/"
        / f"spiketrack_s256_t1/otb/{sequence}.txt",
    ),
    "official_runner_default_run1": (
        "official_runner",
        "default",
        lambda sequence: RUN_ROOT
        / "official_runner_default_run1/tracking_results/spiketrack/"
        / f"spiketrack_s256_t1/otb/{sequence}.txt",
    ),
    "official_runner_default_run2": (
        "official_runner",
        "default",
        lambda sequence: RUN_ROOT
        / "official_runner_default_run2/tracking_results/spiketrack/"
        / f"spiketrack_s256_t1/otb/{sequence}.txt",
    ),
    "official_runner_default_run3": (
        "official_runner",
        "default",
        lambda sequence: RUN_ROOT
        / "official_runner_default_run3/tracking_results/spiketrack/"
        / f"spiketrack_s256_t1/otb/{sequence}.txt",
    ),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_array(array: np.ndarray) -> str:
    return sha256_bytes(np.ascontiguousarray(array).tobytes(order="C"))


def read_boxes(path: Path) -> np.ndarray:
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        fields = line.strip().replace("\t", ",").split(",")
        if len(fields) < 4:
            fields = line.split()
        if len(fields) >= 4:
            rows.append([float(value) for value in fields[:4]])
    return np.asarray(rows, dtype=np.float64)


def normalized_box_bytes(boxes: np.ndarray) -> bytes:
    text = "\n".join(
        ",".join(format(float(value), ".17g") for value in row) for row in boxes
    )
    return (text + "\n").encode("ascii")


def ground_truth_path(root: Path) -> Path:
    for filename in ("groundtruth_rect.txt", "groundtruth.txt"):
        candidate = root / filename
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"No ground-truth file under {root}")


def box_json(box) -> str:
    return json.dumps([float(value) for value in box], separators=(",", ":"))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None):
    if fieldnames is None:
        if not rows:
            raise RuntimeError(f"Cannot infer columns for empty CSV: {path}")
        fieldnames = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def copy_prediction_sources():
    for directory in ("released_raw", "previous_adapter_preserved", *RUNS):
        (ARTIFACT_ROOT / directory).mkdir(parents=True, exist_ok=True)
    for sequence in SEQUENCES:
        released = EXTRACTED_RAW_ROOT / "otb" / f"{sequence}.txt"
        shutil.copyfile(released, ARTIFACT_ROOT / "released_raw" / f"{sequence}.txt")
        shutil.copyfile(
            Path(
                rf"E:\Robot_Backup\tmp\stage4A_bounded_reproduction_official_save_"
                rf"{sequence}_local.txt"
            ),
            ARTIFACT_ROOT / "previous_adapter_preserved" / f"{sequence}.txt",
        )
        for run_id, (_, _, resolver) in RUNS.items():
            source = resolver(sequence)
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copyfile(source, ARTIFACT_ROOT / run_id / f"{sequence}.txt")
    shutil.copyfile(PREVIOUS_ADAPTER_RUN, ARTIFACT_ROOT / "previous_adapter_run.json")
    shutil.copyfile(CURRENT_ADAPTER_RUN, ARTIFACT_ROOT / "adapter_deterministic_run.json")


def build_frame_and_ground_truth_hashes():
    sys.path.insert(0, str(SOURCE_ROOT))
    from lib.test.evaluation.tracker import Tracker

    official_reader = Tracker.__new__(Tracker)
    frame_rows = []
    gt_rows = []
    copy_cache = {}
    for sequence in SEQUENCES:
        for copy_id, root, provenance in COPY_ROOTS[sequence]:
            images = sorted((root / "img").glob("*.jpg"))
            if len(images) != EXPECTED_FRAMES[sequence]:
                raise RuntimeError(
                    f"{sequence}/{copy_id}: {len(images)} frames, expected "
                    f"{EXPECTED_FRAMES[sequence]}"
                )
            raw_hashes = []
            bgr_hashes = []
            rgb_hashes = []
            for frame_index, image_path in enumerate(images, start=1):
                raw_hash = sha256_file(image_path)
                bgr = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
                if bgr is None:
                    raise RuntimeError(f"OpenCV failed to decode {image_path}")
                adapter_rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                official_rgb = official_reader._read_image(str(image_path))
                difference = np.abs(
                    adapter_rgb.astype(np.int16) - official_rgb.astype(np.int16)
                )
                raw_hashes.append(raw_hash)
                bgr_hashes.append(sha256_array(bgr))
                rgb_hashes.append(sha256_array(adapter_rgb))
                frame_rows.append(
                    {
                        "sequence": sequence,
                        "frame_index": frame_index,
                        "absolute_local_source_path": str(image_path.resolve()),
                        "raw_file_sha256": raw_hash,
                        "width": int(bgr.shape[1]),
                        "height": int(bgr.shape[0]),
                        "decoded_bgr_sha256": bgr_hashes[-1],
                        "decoded_rgb_sha256": rgb_hashes[-1],
                        "source_copy_identifier": copy_id,
                        "official_tracker_rgb_sha256": sha256_array(official_rgb),
                        "adapter_official_rgb_equal": bool(
                            np.array_equal(adapter_rgb, official_rgb)
                        ),
                        "adapter_official_diff_pixel_count": int(
                            np.count_nonzero(difference)
                        ),
                        "adapter_official_max_abs_pixel_diff": int(
                            difference.max(initial=0)
                        ),
                    }
                )
            gt_path = ground_truth_path(root)
            boxes = read_boxes(gt_path)
            if len(boxes) != EXPECTED_FRAMES[sequence]:
                raise RuntimeError(
                    f"{sequence}/{copy_id}: {len(boxes)} GT rows, expected "
                    f"{EXPECTED_FRAMES[sequence]}"
                )
            gt_rows.append(
                {
                    "sequence": sequence,
                    "source_copy_identifier": copy_id,
                    "absolute_source_path": str(gt_path.resolve()),
                    "raw_sha256": sha256_file(gt_path),
                    "parsed_row_count": len(boxes),
                    "first_box": box_json(boxes[0]),
                    "last_box": box_json(boxes[-1]),
                    "normalized_parsed_value_sha256": sha256_bytes(
                        normalized_box_bytes(boxes)
                    ),
                }
            )
            copy_cache[(sequence, copy_id)] = {
                "root": root,
                "provenance": provenance,
                "raw_hashes": raw_hashes,
                "bgr_hashes": bgr_hashes,
                "rgb_hashes": rgb_hashes,
                "gt_raw": gt_rows[-1]["raw_sha256"],
                "gt_normalized": gt_rows[-1]["normalized_parsed_value_sha256"],
            }

    write_csv(ARTIFACT_ROOT / "frame_hashes.csv", frame_rows)
    write_csv(ARTIFACT_ROOT / "ground_truth_hashes.csv", gt_rows)

    copy_rows = []
    parity_rows = []
    for sequence in SEQUENCES:
        reference = copy_cache[(sequence, "SRC1_PREVIOUS_ADAPTER")]
        seq_frames = [row for row in frame_rows if row["sequence"] == sequence]
        parity_rows.append(
            {
                "sequence": sequence,
                "copy_count_checked": len(COPY_ROOTS[sequence]),
                "frame_records_checked": len(seq_frames),
                "all_adapter_official_rgb_equal": all(
                    row["adapter_official_rgb_equal"] for row in seq_frames
                ),
                "first_differing_copy": "",
                "first_differing_frame": "",
                "maximum_abs_pixel_difference": max(
                    row["adapter_official_max_abs_pixel_diff"] for row in seq_frames
                ),
            }
        )
        for copy_id, _, _ in COPY_ROOTS[sequence]:
            current = copy_cache[(sequence, copy_id)]
            copy_rows.append(
                {
                    "sequence": sequence,
                    "source_copy_identifier": copy_id,
                    "absolute_sequence_root": str(current["root"].resolve()),
                    "source_provenance": current["provenance"],
                    "frame_count": EXPECTED_FRAMES[sequence],
                    "ground_truth_row_count": EXPECTED_FRAMES[sequence],
                    "official_frame_range_complete": True,
                    "raw_frame_files_identical_to_selected": current["raw_hashes"]
                    == reference["raw_hashes"],
                    "decoded_bgr_identical_to_selected": current["bgr_hashes"]
                    == reference["bgr_hashes"],
                    "decoded_rgb_identical_to_selected": current["rgb_hashes"]
                    == reference["rgb_hashes"],
                    "ground_truth_raw_identical_to_selected": current["gt_raw"]
                    == reference["gt_raw"],
                    "ground_truth_parsed_identical_to_selected": current[
                        "gt_normalized"
                    ]
                    == reference["gt_normalized"],
                    "selected_source_copy": copy_id == "SRC1_PREVIOUS_ADAPTER",
                    "used_by_adapter": copy_id == "SRC1_PREVIOUS_ADAPTER",
                    "used_by_official_runner": copy_id == "STAGED_MINIROOT",
                    "selection_basis": (
                        "continuity with preserved previous adapter; complete official "
                        "frame range; all discovered local copies and staged derivative "
                        "are raw-file, decoded-pixel, and parsed-GT identical; no "
                        "prediction value used"
                    ),
                    "preexisting_duplicate_copy_count": sum(
                        1
                        for candidate_id, _, _ in COPY_ROOTS[sequence]
                        if candidate_id != "STAGED_MINIROOT"
                    ),
                    "staged_derivative_copy_count": 1,
                    "canonical_source_status": (
                        "LOCAL_IDENTITY_ESTABLISHED; CANONICAL_OTB_RELEASE_PROVENANCE_"
                        "UNRESOLVED"
                    ),
                }
            )
    write_csv(ARTIFACT_ROOT / "sequence_copy_manifest.csv", copy_rows)
    write_csv(ARTIFACT_ROOT / "image_loader_parity.csv", parity_rows)
    return frame_rows, copy_rows, parity_rows


def build_archive_manifest():
    archive_sha = sha256_file(ZIP_PATH)
    rows = []
    selected_members = {}
    with zipfile.ZipFile(ZIP_PATH) as archive:
        member_names = [item.filename for item in archive.infolist()]
        manifest_like = [
            name
            for name in member_names
            if any(
                token in Path(name).name.casefold()
                for token in ("environment", "requirements", "commit", "manifest")
            )
        ]
        for sequence in SEQUENCES:
            matches = [
                name
                for name in member_names
                if name.casefold() == f"otb/{sequence}.txt".casefold()
            ]
            if len(matches) != 1:
                raise RuntimeError(f"Raw member resolution failed: {sequence}: {matches}")
            selected_members[matches[0]] = sequence
        for info in archive.infolist():
            selected_sequence = selected_members.get(info.filename, "")
            selected = bool(selected_sequence)
            prediction_rows = ""
            first_row = ""
            last_row = ""
            if selected:
                data = archive.read(info.filename)
                text = data.decode("utf-8-sig")
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                prediction_rows = len(lines)
                first_row = lines[0]
                last_row = lines[-1]
                if prediction_rows != EXPECTED_FRAMES[selected_sequence]:
                    raise RuntimeError(
                        f"{selected_sequence}: raw rows={prediction_rows}, expected "
                        f"{EXPECTED_FRAMES[selected_sequence]}"
                    )
                (ARTIFACT_ROOT / "released_raw" / f"{selected_sequence}.txt").write_bytes(
                    data
                )
            rows.append(
                {
                    "archive_absolute_path": str(ZIP_PATH.resolve()),
                    "archive_sha256": archive_sha,
                    "archive_bytes": ZIP_PATH.stat().st_size,
                    "archive_official_file_id": "1QAST-IzBr2rhAteZq_vc0GZszinIOxbD",
                    "archive_local_filename": ZIP_PATH.name,
                    "archive_internal_config_manifest_status": (
                        "ABSENT" if not manifest_like else "PRESENT"
                    ),
                    "archive_manifest_like_members": "|".join(manifest_like),
                    "member_path": info.filename,
                    "member_result_folder": (
                        info.filename.split("/", 1)[0] if "/" in info.filename else ""
                    ),
                    "member_uncompressed_bytes": info.file_size,
                    "member_compressed_bytes": info.compress_size,
                    "member_crc32_hex": f"{info.CRC:08x}",
                    "selected": selected,
                    "selected_sequence": selected_sequence,
                    "selected_prediction_rows": prediction_rows,
                    "selected_first_row": first_row,
                    "selected_last_row": last_row,
                    "configuration_identity_note": (
                        "local archive filename and official release-link identity say "
                        "S256-T1; archive interior has dataset folders but no commit or "
                        "environment/config manifest"
                    ),
                }
            )
    write_csv(ARTIFACT_ROOT / "raw_archive_manifest.csv", rows)
    return archive_sha, rows


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
    union = max(0.0, aw) * max(0.0, ah) + max(0.0, bw) * max(0.0, bh) - intersection
    return intersection / union if union > 0.0 else 0.0


def first_true(mask: np.ndarray):
    indices = np.flatnonzero(mask)
    return int(indices[0]) if len(indices) else None


def build_metrics_and_divergence():
    sys.path.insert(0, str(SOURCE_ROOT))
    from lib.test.analysis.extract_results import calc_seq_err_robust

    metric_rows = []
    divergence_rows = []
    for sequence in SEQUENCES:
        gt = read_boxes(ground_truth_path(COPY_ROOTS[sequence][0][1]))
        released_path = ARTIFACT_ROOT / "released_raw" / f"{sequence}.txt"
        released = read_boxes(released_path)
        released_auc = success_auc(released, gt, calc_seq_err_robust)
        all_runs = {
            "released_raw": ("released", "unknown_author_mode", released_path),
            **{
                run_id: (runner, mode, ARTIFACT_ROOT / run_id / f"{sequence}.txt")
                for run_id, (runner, mode, _) in RUNS.items()
            },
        }
        default1 = read_boxes(
            ARTIFACT_ROOT / "official_runner_default_run1" / f"{sequence}.txt"
        )
        for run_id, (runner, runtime_mode, path) in all_runs.items():
            prediction = read_boxes(path)
            if len(prediction) != EXPECTED_FRAMES[sequence]:
                raise RuntimeError(f"{run_id}/{sequence}: invalid prediction length")
            auc = success_auc(prediction, gt, calc_seq_err_robust)
            metric_rows.append(
                {
                    "sequence": sequence,
                    "run_id": run_id,
                    "runner_type": runner,
                    "runtime_mode": runtime_mode,
                    "prediction_repository_path": str(path.relative_to(ARTIFACT_ROOT)),
                    "prediction_sha256": sha256_file(path),
                    "prediction_rows": len(prediction),
                    "success_auc_percent": format(auc, ".15g"),
                    "released_success_auc_percent": format(released_auc, ".15g"),
                    "absolute_difference_percentage_points": format(
                        abs(auc - released_auc), ".15g"
                    ),
                    "within_0_5_percentage_points": abs(auc - released_auc) <= 0.5,
                    "byte_identical_to_released": path.read_bytes()
                    == released_path.read_bytes(),
                    "box_values_identical_to_released": bool(
                        np.array_equal(prediction, released)
                    ),
                    "box_values_identical_to_official_default_run1": bool(
                        np.array_equal(prediction, default1)
                    ),
                }
            )
            if run_id == "released_raw":
                continue
            component_difference = np.abs(prediction - released)
            any_index = first_true(np.any(component_difference != 0.0, axis=1))
            ious = np.asarray(
                [inclusive_iou(local, raw) for local, raw in zip(prediction, released)]
            )
            iou95_index = first_true(ious < 0.95)
            iou75_index = first_true(ious < 0.75)
            if any_index is None:
                max_index = None
            else:
                max_index = any_index + int(
                    np.argmax(component_difference[any_index:].max(axis=1))
                )

            def frame_number(index):
                return "" if index is None else index + 1

            def at(array, index, renderer):
                return "" if index is None else renderer(array[index])

            divergence_rows.append(
                {
                    "sequence": sequence,
                    "run_id": run_id,
                    "runtime_mode": runtime_mode,
                    "first_any_box_difference_frame": frame_number(any_index),
                    "maximum_component_difference_at_first_frame": at(
                        component_difference,
                        any_index,
                        lambda row: format(float(row.max()), ".17g"),
                    ),
                    "local_box_at_first_difference": at(prediction, any_index, box_json),
                    "released_box_at_first_difference": at(released, any_index, box_json),
                    "first_iou_below_0_95_frame": frame_number(iou95_index),
                    "iou_at_first_below_0_95": at(
                        ious, iou95_index, lambda value: format(float(value), ".17g")
                    ),
                    "local_box_at_first_iou_below_0_95": at(
                        prediction, iou95_index, box_json
                    ),
                    "released_box_at_first_iou_below_0_95": at(
                        released, iou95_index, box_json
                    ),
                    "first_iou_below_0_75_frame": frame_number(iou75_index),
                    "iou_at_first_below_0_75": at(
                        ious, iou75_index, lambda value: format(float(value), ".17g")
                    ),
                    "local_box_at_first_iou_below_0_75": at(
                        prediction, iou75_index, box_json
                    ),
                    "released_box_at_first_iou_below_0_75": at(
                        released, iou75_index, box_json
                    ),
                    "maximum_component_difference_at_or_after_first": at(
                        component_difference,
                        max_index,
                        lambda row: format(float(row.max()), ".17g"),
                    ),
                    "maximum_component_difference_frame": frame_number(max_index),
                    "local_box_at_maximum_component_difference": at(
                        prediction, max_index, box_json
                    ),
                    "released_box_at_maximum_component_difference": at(
                        released, max_index, box_json
                    ),
                }
            )
    write_csv(ARTIFACT_ROOT / "metrics.csv", metric_rows)
    write_csv(ARTIFACT_ROOT / "first_divergence.csv", divergence_rows)
    return metric_rows, divergence_rows


def build_runtime_summary():
    rows = []
    adapter_json = json.loads(CURRENT_ADAPTER_RUN.read_text(encoding="utf-8"))
    adapter_times = {
        item["sequence"]: item["local_tracking_seconds_excluding_initialization"]
        for item in adapter_json["results"]
    }
    for sequence in SEQUENCES:
        rows.append(
            {
                "sequence": sequence,
                "run_id": "adapter_deterministic",
                "runtime_mode": "deterministic",
                "timing_scope": "frame loop excluding initialization",
                "timed_frames": EXPECTED_FRAMES[sequence] - 1,
                "seconds": format(adapter_times[sequence], ".15g"),
                "fps_or_na": format(
                    (EXPECTED_FRAMES[sequence] - 1) / adapter_times[sequence], ".15g"
                ),
                "interpretation_boundary": "characterization only; not a speed comparison",
            }
        )
        for run_id, (_, mode, resolver) in RUNS.items():
            if not run_id.startswith("official_runner"):
                continue
            prediction_path = resolver(sequence)
            time_path = prediction_path.with_name(f"{sequence}_time.txt")
            timings = np.loadtxt(time_path, dtype=np.float64, ndmin=1)
            seconds = float(timings.sum())
            rows.append(
                {
                    "sequence": sequence,
                    "run_id": run_id,
                    "runtime_mode": mode,
                    "timing_scope": "official saved per-frame time including initialization",
                    "timed_frames": len(timings),
                    "seconds": format(seconds, ".15g"),
                    "fps_or_na": format(len(timings) / seconds, ".15g"),
                    "interpretation_boundary": (
                        "characterization only; launch/thermal state uncontrolled; "
                        "prediction repeatability is the runtime-mode test"
                    ),
                }
            )
    write_csv(ARTIFACT_ROOT / "runtime_summary.csv", rows)
    return rows


def build_manifest(frame_rows, copy_rows, parity_rows, archive_sha, archive_rows, metric_rows):
    default_hashes = {
        sequence: [
            sha256_file(ARTIFACT_ROOT / f"official_runner_default_run{index}" / f"{sequence}.txt")
            for index in (1, 2, 3)
        ]
        for sequence in SEQUENCES
    }
    official_det_hashes = {
        sequence: sha256_file(
            ARTIFACT_ROOT / "official_runner_deterministic" / f"{sequence}.txt"
        )
        for sequence in SEQUENCES
    }
    adapter_hashes = {
        sequence: sha256_file(
            ARTIFACT_ROOT / "adapter_deterministic" / f"{sequence}.txt"
        )
        for sequence in SEQUENCES
    }
    previous_adapter_hashes = {
        sequence: sha256_file(
            ARTIFACT_ROOT / "previous_adapter_preserved" / f"{sequence}.txt"
        )
        for sequence in SEQUENCES
    }
    generated_files = sorted(
        path
        for path in ARTIFACT_ROOT.rglob("*")
        if path.is_file()
        and path.name != "manifest.json"
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
    )
    manifest = {
        "scope": "STAGE4A_R_THREE_PREDECLARED_SEQUENCES_ONLY_NOT_STAGE4B",
        "sequences": list(SEQUENCES),
        "selection_boundary": (
            "fixed before these runs from completeness/frame range/provenance only; "
            "no prediction used for copy or sequence selection"
        ),
        "source": {
            "repository": "faicaiwawa/SpikeTrack",
            "pinned_commit": PINNED_COMMIT,
            "isolated_source_root": str(SOURCE_ROOT),
            "tracked_source_status": (
                "exact pinned commit with no tracked modifications; required external "
                "lib/test/evaluation/local.py is untracked and preserved separately"
            ),
            "config": str(CONFIG),
            "config_sha256": sha256_file(CONFIG),
            "checkpoint": str(CHECKPOINT),
            "checkpoint_sha256": sha256_file(CHECKPOINT),
        },
        "previous_adapter": {
            "status": "PRESERVED",
            "extant_source": str(PREVIOUS_ADAPTER_SOURCE),
            "preserved_repository_path": "previous_adapter_exact.py",
            "source_sha256": sha256_file(PREVIOUS_ADAPTER_SOURCE),
            "preserved_sha256": sha256_file(
                ARTIFACT_ROOT / "previous_adapter_exact.py"
            ),
            "preserved_prediction_hashes": previous_adapter_hashes,
            "preserved_predictions_equal_new_adapter": all(
                previous_adapter_hashes[sequence] == adapter_hashes[sequence]
                for sequence in SEQUENCES
            ),
            "definitive_run_association": (
                "filesystem timestamp order, embedded output paths, and exact metric/"
                "prediction hashes agree; the old run did not embed a script hash, so "
                "source-to-run association is corroborated rather than cryptographically "
                "attested"
            ),
        },
        "auditable_adapter_extension": {
            "repository_path": "../../scripts/2026-08-25_stage4A_spiketrack_reproduce3.py",
            "sha256": sha256_file(AUDITABLE_ADAPTER),
            "relationship": (
                "retains previous tracking/metric semantics and adds explicit "
                "--runtime-mode plus info-contract provenance"
            ),
            "adapter_info_contract": (
                "initialize receives init_bbox only; each frame receives {}; no "
                "previous_output is propagated"
            ),
            "official_info_contract": (
                "Tracker.run_sequence adds seq_name at initialization and propagates "
                "frame_info plus previous_output; pinned SpikeTrack initialize reads "
                "only init_bbox and track does not read info"
            ),
            "observed_relationship": (
                "all three persisted adapter predictions are byte-identical to all "
                "official-runner predictions"
            ),
        },
        "official_runner": {
            "entrypoint": "tracking/test.py",
            "path_chain": [
                "OTBDataset",
                "Tracker.run_sequence",
                "Tracker._read_image",
                "lib/test/tracker/spiketrack_inf.py",
                "lib/test/evaluation/running.py::_save_tracker_output",
            ],
            "external_otb_miniroot": r"E:\Robot_Backup\tmp\stage4A_R_otb3",
            "eager_loader_note": (
                "unmodified OTBDataset eagerly parses all 100 annotation paths before "
                "sequence selection; external six-row metadata-only stubs were supplied "
                "for unexecuted names. Only the three predeclared sequences contain real "
                "frames/GT and only those names were executed"
            ),
            "external_local_py": str(
                SOURCE_ROOT / "lib/test/evaluation/local.py"
            ),
        },
        "dataset_identity": {
            "preexisting_copies_per_sequence": {
                sequence: sum(
                    1
                    for copy_id, _, _ in COPY_ROOTS[sequence]
                    if copy_id != "STAGED_MINIROOT"
                )
                for sequence in SEQUENCES
            },
            "staged_derivatives_per_sequence": 1,
            "frame_hash_records": len(frame_rows),
            "copy_manifest_rows": len(copy_rows),
            "all_local_raw_frames_identical": all(
                row["raw_frame_files_identical_to_selected"] for row in copy_rows
            ),
            "all_local_decoded_rgb_identical": all(
                row["decoded_rgb_identical_to_selected"] for row in copy_rows
            ),
            "all_local_ground_truth_parsed_identical": all(
                row["ground_truth_parsed_identical_to_selected"] for row in copy_rows
            ),
            "canonical_otb_release_provenance": "UNRESOLVED",
        },
        "image_loader_parity": {
            "all_frames_all_copies_exact": all(
                row["all_adapter_official_rgb_equal"] for row in parity_rows
            ),
            "comparison": (
                "adapter cv2.imread plus cv2.COLOR_BGR2RGB versus pinned "
                "Tracker._read_image on every frame of every checked copy"
            ),
        },
        "raw_archive": {
            "path": str(ZIP_PATH),
            "sha256": archive_sha,
            "member_count": len(archive_rows),
            "configuration_manifest_status": archive_rows[0][
                "archive_internal_config_manifest_status"
            ],
        },
        "prediction_repeatability": {
            "official_default_three_runs_identical": all(
                len(set(hashes)) == 1 for hashes in default_hashes.values()
            ),
            "official_deterministic_equals_default": all(
                official_det_hashes[sequence] == default_hashes[sequence][0]
                for sequence in SEQUENCES
            ),
            "adapter_deterministic_equals_official": all(
                adapter_hashes[sequence] == official_det_hashes[sequence]
                for sequence in SEQUENCES
            ),
            "hashes": {
                "official_default": default_hashes,
                "official_deterministic": official_det_hashes,
                "adapter_deterministic": adapter_hashes,
            },
        },
        "released_comparison": {
            "all_local_run_rows": len(
                [row for row in metric_rows if row["run_id"] != "released_raw"]
            ),
            "all_local_runs_identical_within_each_sequence": True,
            "released_difference_persists_in_both_local_runtime_modes": True,
            "official_author_runtime_environment": "UNKNOWN_NOT_IN_ARCHIVE",
        },
        "reproduction_label": "REPRO_UNRESOLVED",
        "reason": (
            "adapter and official runner agree exactly, every local run is repeatable, "
            "and local duplicate/staged pixels plus GT agree; however default versus "
            "deterministic mode does not explain the released difference and canonical "
            "OTB/author environment provenance remains unavailable"
        ),
        "artifacts": [
            {
                "path": str(path.relative_to(ARTIFACT_ROOT)).replace("\\", "/"),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in generated_files
        ],
    }
    (ARTIFACT_ROOT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main():
    copy_prediction_sources()
    frame_rows, copy_rows, parity_rows = build_frame_and_ground_truth_hashes()
    archive_sha, archive_rows = build_archive_manifest()
    metric_rows, _ = build_metrics_and_divergence()
    build_runtime_summary()
    build_manifest(
        frame_rows, copy_rows, parity_rows, archive_sha, archive_rows, metric_rows
    )


if __name__ == "__main__":
    main()
