"""Bounded three-sequence SpikeTrack T1 reproduction for Stage 4A.

The sequence set is fixed in this file before execution and was selected only
from local image/ground-truth completeness and sequence length.  This is not a
full OTB benchmark runner.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time
from types import SimpleNamespace

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import cv2
import numpy as np
import torch


PREDECLARED_SEQUENCES = (
    (
        "Deer",
        Path(r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified\TRACA-master\sequence\Deer"),
        71,
    ),
    (
        "Crossing",
        Path(r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified\ECO-master\sequences\Crossing"),
        120,
    ),
    (
        "Couple",
        Path(r"E:\Robot_Backup\TrackingResearch-master\OtherTracker\verified\SRDCF\SRDCF\sequences\Couple"),
        140,
    ),
)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--raw-root", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20260825)
    parser.add_argument("--only-sequence", choices=[item[0] for item in PREDECLARED_SEQUENCES])
    return parser.parse_args()


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_boxes(path):
    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        fields = line.strip().replace("\t", ",").split(",")
        if len(fields) < 4:
            fields = line.split()
        rows.append([float(value) for value in fields[:4]])
    return np.asarray(rows, dtype=np.float64)


def find_raw_result(raw_root, sequence_name):
    matches = [
        path
        for path in raw_root.rglob("*.txt")
        if path.stem.casefold() == sequence_name.casefold()
        and "otb" in str(path).casefold()
        and not path.stem.casefold().endswith("_time")
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"Expected exactly one OTB raw prediction for {sequence_name}; "
            f"found {len(matches)}: {matches}"
        )
    return matches[0]


def success_auc(prediction, ground_truth, calc_seq_err_robust):
    pred_tensor = torch.tensor(prediction, dtype=torch.float64)
    gt_tensor = torch.tensor(ground_truth, dtype=torch.float64)
    overlap, _, _, _ = calc_seq_err_robust(
        pred_tensor, gt_tensor, dataset="otb", target_visible=None
    )
    thresholds = torch.arange(0.0, 1.0 + 0.05, 0.05, dtype=torch.float64)
    success = (
        (overlap.view(-1, 1) > thresholds.view(1, -1)).sum(0).double()
        / gt_tensor.shape[0]
    )
    return float(success.mean().item() * 100.0)


def read_rgb(path):
    image = cv2.imread(str(path))
    if image is None:
        raise RuntimeError(f"Could not read image: {path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def main():
    args = parse_args()
    source_root = args.source_root.resolve()
    config_path = args.config.resolve()
    checkpoint_path = args.checkpoint.resolve()
    raw_root = args.raw_root.resolve()
    if config_path.name != "spiketrack_s256_t1.yaml":
        raise ValueError("Bounded reproduction is pinned to Small-256-T1")
    for path in (source_root, config_path, checkpoint_path, raw_root):
        if not path.exists():
            raise FileNotFoundError(path)

    os.chdir(source_root)
    sys.path.insert(0, str(source_root))
    from lib.config.spiketrack.config import cfg, update_config_from_file
    from lib.test.analysis.extract_results import calc_seq_err_robust
    from lib.test.tracker.spiketrack_inf import SpikeTrack

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)

    update_config_from_file(str(config_path))
    if (
        cfg.MODEL.ENCODER.TYPE != "Efficient_Spiking_Transformer_s"
        or cfg.TEST.SEARCH_SIZE != 256
        or cfg.TEST.NUM_TEMPLATES != 1
    ):
        raise RuntimeError("Resolved config is not exact Small-256-T1")

    params = SimpleNamespace(
        cfg=cfg,
        template_factor=cfg.TEST.TEMPLATE_FACTOR,
        template_size=cfg.TEST.TEMPLATE_SIZE,
        search_factor=cfg.TEST.SEARCH_FACTOR,
        search_size=cfg.TEST.SEARCH_SIZE,
        save_all_boxes=False,
        debug=0,
        yaml_name=config_path.stem,
    )

    results = []
    for sequence_name, sequence_root, expected_frames in PREDECLARED_SEQUENCES:
        if args.only_sequence and sequence_name != args.only_sequence:
            continue
        image_paths = sorted((sequence_root / "img").glob("*.jpg"))
        ground_truth = read_boxes(sequence_root / "groundtruth_rect.txt")
        if len(image_paths) != expected_frames or len(ground_truth) != expected_frames:
            raise RuntimeError(
                f"{sequence_name}: expected {expected_frames}, got images="
                f"{len(image_paths)} gt={len(ground_truth)}"
            )
        raw_path = find_raw_result(raw_root, sequence_name)
        released = read_boxes(raw_path)
        if len(released) != expected_frames:
            raise RuntimeError(
                f"{sequence_name}: released prediction length {len(released)} "
                f"!= {expected_frames}"
            )

        tracker = SpikeTrack(
            params,
            dataset_name="otb",
            checkpoint_path=str(checkpoint_path),
            save_sfr=False,
        )
        predictions = [ground_truth[0].tolist()]
        tracker.initialize(read_rgb(image_paths[0]), {"init_bbox": predictions[0]})
        started = time.perf_counter()
        for image_path in image_paths[1:]:
            output, _, _ = tracker.track(read_rgb(image_path), {})
            predictions.append([float(value) for value in output["target_bbox"]])
        elapsed_seconds = time.perf_counter() - started
        predictions = np.asarray(predictions, dtype=np.float64)
        # Match pinned lib/test/evaluation/running.py::save_bb exactly before
        # offline analysis: np.array(data).astype(int), then fmt='%d'.
        saved_predictions = predictions.astype(int)
        prediction_output = (
            args.output_json.parent
            / f"{args.output_json.stem}_{sequence_name}_local.txt"
        )
        np.savetxt(prediction_output, saved_predictions, delimiter="\t", fmt="%d")
        released_auc = success_auc(released, ground_truth, calc_seq_err_robust)
        local_auc = success_auc(saved_predictions, ground_truth, calc_seq_err_robust)
        results.append(
            {
                "sequence": sequence_name,
                "sequence_root": str(sequence_root),
                "frames": expected_frames,
                "released_raw_result": str(raw_path),
                "local_prediction_output": str(prediction_output),
                "released_success_auc_percent": released_auc,
                "local_success_auc_percent": local_auc,
                "absolute_difference_percentage_points": abs(local_auc - released_auc),
                "target_within_0_5_pp": abs(local_auc - released_auc) <= 0.5,
                "local_tracking_seconds_excluding_initialization": elapsed_seconds,
            }
        )
        del tracker
        torch.cuda.empty_cache()

    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=source_root, text=True
    ).strip()
    report = {
        "scope": "STAGE4A_BOUNDED_THREE_SEQUENCE_REPRODUCTION_NOT_FULL_BENCHMARK",
        "predeclaration_basis": (
            "local image/ground-truth completeness and sequence length only; "
            "no SpikeTrack output inspected before selection"
        ),
        "predeclared_sequences": [item[0] for item in PREDECLARED_SEQUENCES],
        "executed_sequences": [item["sequence"] for item in results],
        "source_root": str(source_root),
        "pinned_commit": commit,
        "config": str(config_path),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256_file(checkpoint_path),
        "dtype": "torch.float32",
        "device": "cuda",
        "seed": args.seed,
        "deterministic_settings": {
            "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "cudnn_deterministic": torch.backends.cudnn.deterministic,
            "torch_deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
        "metric_semantics": (
            "pinned lib/test/analysis/extract_results.py calc_seq_err_robust; "
            "inclusive-coordinate IoU; thresholds 0:0.05:1; strict >; first "
            "prediction replaced by ground truth; local boxes persisted with "
            "pinned running.py save_bb int truncation and %d format"
        ),
        "results": results,
        "all_within_0_5_pp": all(item["target_within_0_5_pp"] for item in results),
    }
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(rendered + "\n", encoding="utf-8")
    if not report["all_within_0_5_pp"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
