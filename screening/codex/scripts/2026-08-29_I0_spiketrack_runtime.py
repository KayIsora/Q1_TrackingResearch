#!/usr/bin/env python3
"""Bounded SpikeTrack-S256-T1 runtime/parity wrapper for I0.

This wrapper intentionally does not download assets, mutate the pinned source,
run a benchmark suite, or export a model.  Each invocation validates the frozen
source/config/checkpoint identities, proves strict state-dict compatibility, and
then runs exactly one OTB sequence, image folder, or video.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Iterator, Sequence

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

EXPECTED_SOURCE_SHA = "1537db51a1cc9f6e30cce469fba3e51f5721b3d0"
EXPECTED_CONFIG_SHA256 = "9a352f3e98ecdbce2355a95399752a1bc772c90ad9ddcab2ad35951d0c6366f8"
EXPECTED_CHECKPOINT_SHA256 = "cf5c078ef7741109b8db8f8dd66b322b0814bf787ad56a5cdd5594dd2a8b85df"
CONFIG_RELATIVE_PATH = Path("experiments/spiketrack/spiketrack_s256_t1.yaml")
DEFAULT_SOURCE_ROOT = Path(r"E:\Robot_Backup\tmp\i0_spiketrack_runtime_20260829")
DEFAULT_CHECKPOINT = Path(r"E:\Robot_Backup\tmp\stage2B_spiketrack\ckpt\spiketrack_s256_t1.pth.tar")
DEFAULT_OTB_ROOT = Path(r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015")
SEED = 20260829


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def run_git(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def validate_identities(source_root: Path, checkpoint: Path) -> dict[str, Any]:
    if not source_root.is_dir():
        raise FileNotFoundError(f"Pinned source root is missing: {source_root}")
    if not checkpoint.is_file():
        raise FileNotFoundError(f"Pinned checkpoint is missing: {checkpoint}")

    config_path = source_root / CONFIG_RELATIVE_PATH
    if not config_path.is_file():
        raise FileNotFoundError(f"Pinned config is missing: {config_path}")

    source_sha = run_git(source_root, "rev-parse", "HEAD")
    source_status = run_git(source_root, "status", "--porcelain=v1", "--untracked-files=all")
    remote_url = run_git(source_root, "remote", "get-url", "origin")
    config_sha = sha256_file(config_path)
    checkpoint_sha = sha256_file(checkpoint)

    checks = {
        "source_sha_matches": source_sha.lower() == EXPECTED_SOURCE_SHA,
        "source_worktree_clean": source_status == "",
        "config_sha256_matches": config_sha.lower() == EXPECTED_CONFIG_SHA256,
        "checkpoint_sha256_matches": checkpoint_sha.lower() == EXPECTED_CHECKPOINT_SHA256,
    }
    if not all(checks.values()):
        raise RuntimeError(f"Frozen identity preflight failed: {checks}")

    return {
        "repository": remote_url,
        "source_root": str(source_root.resolve()),
        "source_sha": source_sha,
        "source_status_porcelain": source_status,
        "config_path": str(config_path.resolve()),
        "config_sha256": config_sha,
        "checkpoint_path": str(checkpoint.resolve()),
        "checkpoint_bytes": checkpoint.stat().st_size,
        "checkpoint_sha256": checkpoint_sha,
        "checks": checks,
    }


def configure_determinism(torch_module: Any) -> None:
    random.seed(SEED)
    try:
        import numpy as np

        np.random.seed(SEED)
    except ImportError:
        pass
    torch_module.manual_seed(SEED)
    torch_module.cuda.manual_seed_all(SEED)
    torch_module.backends.cudnn.benchmark = False
    torch_module.backends.cudnn.deterministic = True
    torch_module.use_deterministic_algorithms(True)


def environment_record(torch_module: Any, cv2_module: Any, numpy_module: Any) -> dict[str, Any]:
    import psutil

    try:
        import timm

        timm_version = timm.__version__
    except Exception as exc:  # pragma: no cover - provenance fallback
        timm_version = f"unavailable: {type(exc).__name__}: {exc}"

    try:
        import torchvision

        torchvision_version = torchvision.__version__
    except Exception as exc:  # pragma: no cover - provenance fallback
        torchvision_version = f"unavailable: {type(exc).__name__}: {exc}"

    return {
        "python": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "torch": torch_module.__version__,
        "torchvision": torchvision_version,
        "timm": timm_version,
        "opencv": cv2_module.__version__,
        "numpy": numpy_module.__version__,
        "psutil": psutil.__version__,
        "cuda_available": bool(torch_module.cuda.is_available()),
        "torch_cuda": torch_module.version.cuda,
        "cudnn": torch_module.backends.cudnn.version(),
        "gpu_name": torch_module.cuda.get_device_name(0) if torch_module.cuda.is_available() else None,
        "gpu_capability": list(torch_module.cuda.get_device_capability(0)) if torch_module.cuda.is_available() else None,
        "cublas_workspace_config": os.environ.get("CUBLAS_WORKSPACE_CONFIG"),
        "seed": SEED,
        "deterministic_algorithms": bool(torch_module.are_deterministic_algorithms_enabled()),
        "cudnn_benchmark": bool(torch_module.backends.cudnn.benchmark),
        "cudnn_deterministic": bool(torch_module.backends.cudnn.deterministic),
        "batch_size": 1,
        "precision": "FP32",
    }


def make_params(cfg: Any) -> Any:
    from lib.test.utils import TrackerParams

    params = TrackerParams()
    params.cfg = cfg
    params.yaml_name = "spiketrack_s256_t1"
    params.template_factor = cfg.TEST.TEMPLATE_FACTOR
    params.template_size = cfg.TEST.TEMPLATE_SIZE
    params.search_factor = cfg.TEST.SEARCH_FACTOR
    params.search_size = cfg.TEST.SEARCH_SIZE
    params.checkpoint = "/."
    params.save_all_boxes = False
    params.debug = 0
    params.tracker_name = "spiketrack_inf"
    params.param_name = "spiketrack_s256_t1"
    return params


def strict_load_probe(cfg: Any, checkpoint: Path, torch_module: Any) -> tuple[dict[str, Any], dict[str, int]]:
    from lib.models.spiketrack.spiketrack_inf import build_spiketrack

    network, encoder_temp = build_spiketrack(cfg, False)
    checkpoint_object = torch_module.load(str(checkpoint), map_location="cpu")
    if not isinstance(checkpoint_object, dict) or "net" not in checkpoint_object:
        raise RuntimeError("Checkpoint is not a mapping containing the required 'net' state dict")
    state_dict = checkpoint_object["net"]
    network_result = network.load_state_dict(state_dict, strict=True)
    encoder_candidate_state = {
        key.removeprefix("encoder."): value
        for key, value in state_dict.items()
        if key.startswith("encoder.")
    }
    template_keyspace = set(encoder_temp.state_dict().keys())
    encoder_state = {key: value for key, value in encoder_candidate_state.items() if key in template_keyspace}
    missing_template_keys = sorted(template_keyspace.difference(encoder_state))
    excluded_search_only_keys = sorted(set(encoder_candidate_state).difference(template_keyspace))
    if missing_template_keys:
        raise RuntimeError(f"Template encoder checkpoint mapping is incomplete: {missing_template_keys}")
    encoder_result = encoder_temp.load_state_dict(encoder_state, strict=True)

    counts = {
        "network_parameters": sum(parameter.numel() for parameter in network.parameters()),
        "network_trainable_parameters": sum(parameter.numel() for parameter in network.parameters() if parameter.requires_grad),
        "template_encoder_parameters": sum(parameter.numel() for parameter in encoder_temp.parameters()),
        "template_encoder_trainable_parameters": sum(
            parameter.numel() for parameter in encoder_temp.parameters() if parameter.requires_grad
        ),
    }
    counts["resident_total_parameters"] = counts["network_parameters"] + counts["template_encoder_parameters"]
    counts["resident_total_parameter_bytes_fp32"] = counts["resident_total_parameters"] * 4

    result = {
        "passed": True,
        "network_missing_keys": list(network_result.missing_keys),
        "network_unexpected_keys": list(network_result.unexpected_keys),
        "template_encoder_missing_keys": list(encoder_result.missing_keys),
        "template_encoder_unexpected_keys": list(encoder_result.unexpected_keys),
        "template_encoder_mapping": "checkpoint encoder.* keys intersected with the exact template-encoder keyspace",
        "template_encoder_excluded_search_only_key_count": len(excluded_search_only_keys),
        "template_encoder_excluded_search_only_keys": excluded_search_only_keys,
        "checkpoint_top_level_keys": sorted(str(key) for key in checkpoint_object.keys()),
        "network_state_tensor_count": len(state_dict),
        "template_encoder_state_tensor_count": len(encoder_state),
    }
    del checkpoint_object, state_dict, encoder_candidate_state, encoder_state, network, encoder_temp
    return result, counts


def read_rgb(path: Path, cv2_module: Any) -> Any:
    image = cv2_module.imread(str(path), cv2_module.IMREAD_COLOR)
    if image is None:
        raise RuntimeError(f"Could not read image: {path}")
    return cv2_module.cvtColor(image, cv2_module.COLOR_BGR2RGB)


def otb_input(sequence_name: str, otb_root: Path, cv2_module: Any) -> tuple[str, list[float], Iterable[tuple[int, str, Any, dict[str, Any]]]]:
    import lib.test.evaluation.data as evaluation_data

    evaluation_data.env_settings = lambda: SimpleNamespace(otb_path=str(otb_root))
    from lib.test.evaluation.otbdataset import OTBDataset

    dataset = OTBDataset()
    exact_metadata = [item for item in dataset.sequence_info_list if item["name"] == sequence_name]
    if len(exact_metadata) != 1:
        raise RuntimeError(f"Expected exactly one OTB metadata row for {sequence_name!r}, got {len(exact_metadata)}")
    dataset.sequence_info_list = exact_metadata
    sequence = dataset.get_sequence_list()[0]
    init_info = sequence.init_info()
    init_bbox = [float(value) for value in init_info["init_bbox"]]

    def iterator() -> Iterator[tuple[int, str, Any, dict[str, Any]]]:
        previous_output: OrderedDict[str, Any] = OrderedDict()
        for zero_index, frame_path in enumerate(sequence.frames):
            info = sequence.frame_info(zero_index)
            if zero_index == 0:
                info["seq_name"] = sequence.name
            else:
                info["previous_output"] = previous_output
            image = read_rgb(Path(frame_path), cv2_module)
            yield zero_index + 1, str(Path(frame_path).resolve()), image, info
            if zero_index == 0:
                previous_output = OrderedDict()

    return sequence.name, init_bbox, iterator()


IMAGE_SUFFIXES = {".bmp", ".jpeg", ".jpg", ".png", ".tif", ".tiff"}


def folder_input(folder: Path, init_bbox: Sequence[float], cv2_module: Any) -> tuple[str, list[float], Iterable[tuple[int, str, Any, dict[str, Any]]]]:
    frame_paths = sorted(
        (path for path in folder.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES),
        key=lambda path: path.name.lower(),
    )
    if not frame_paths:
        raise RuntimeError(f"No supported images found in folder: {folder}")
    bbox = [float(value) for value in init_bbox]

    def iterator() -> Iterator[tuple[int, str, Any, dict[str, Any]]]:
        for index, frame_path in enumerate(frame_paths, start=1):
            info = {"init_bbox": bbox, "seq_name": folder.name} if index == 1 else {}
            yield index, str(frame_path.resolve()), read_rgb(frame_path, cv2_module), info

    return folder.name, bbox, iterator()


def video_input(video: Path, init_bbox: Sequence[float], cv2_module: Any) -> tuple[str, list[float], Iterable[tuple[int, str, Any, dict[str, Any]]]]:
    bbox = [float(value) for value in init_bbox]

    def iterator() -> Iterator[tuple[int, str, Any, dict[str, Any]]]:
        capture = cv2_module.VideoCapture(str(video))
        if not capture.isOpened():
            raise RuntimeError(f"Could not open video: {video}")
        try:
            index = 0
            while True:
                ok, frame_bgr = capture.read()
                if not ok:
                    break
                index += 1
                frame_rgb = cv2_module.cvtColor(frame_bgr, cv2_module.COLOR_BGR2RGB)
                info = {"init_bbox": bbox, "seq_name": video.stem} if index == 1 else {}
                yield index, f"{video.resolve()}#frame={index}", frame_rgb, info
        finally:
            capture.release()
        if index == 0:
            raise RuntimeError(f"Video has no readable frames: {video}")

    return video.stem, bbox, iterator()


class ForwardTimer:
    def __init__(self, tracker: Any, torch_module: Any) -> None:
        self.tracker = tracker
        self.torch = torch_module
        self.original_encoder = tracker.network.forward_encoder
        self.original_decoder = tracker.network.inference_decoder
        self.encoder_ms = 0.0
        self.decoder_ms = 0.0

        def timed_encoder(*args: Any, **kwargs: Any) -> Any:
            self.torch.cuda.synchronize()
            started = time.perf_counter()
            result = self.original_encoder(*args, **kwargs)
            self.torch.cuda.synchronize()
            self.encoder_ms += (time.perf_counter() - started) * 1000.0
            return result

        def timed_decoder(*args: Any, **kwargs: Any) -> Any:
            self.torch.cuda.synchronize()
            started = time.perf_counter()
            result = self.original_decoder(*args, **kwargs)
            self.torch.cuda.synchronize()
            self.decoder_ms += (time.perf_counter() - started) * 1000.0
            return result

        tracker.network.forward_encoder = timed_encoder
        tracker.network.inference_decoder = timed_decoder

    def start_frame(self) -> None:
        self.encoder_ms = 0.0
        self.decoder_ms = 0.0

    def frame_values(self) -> tuple[float, float, float]:
        return self.encoder_ms, self.decoder_ms, self.encoder_ms + self.decoder_ms

    def close(self) -> None:
        self.tracker.network.forward_encoder = self.original_encoder
        self.tracker.network.inference_decoder = self.original_decoder


def percentile(values: Sequence[float], q: float, numpy_module: Any) -> float | None:
    if not values:
        return None
    return float(numpy_module.percentile(numpy_module.asarray(values, dtype=numpy_module.float64), q))


def timing_summary(rows: Sequence[dict[str, Any]], numpy_module: Any) -> dict[str, Any]:
    measured = [row for row in rows if row["phase"] == "track" and row["measurement_state"] == "measured"]
    e2e = [float(row["end_to_end_ms"]) for row in measured]
    model = [float(row["model_forward_ms"]) for row in measured if row["model_forward_ms"] != ""]

    def stats(values: Sequence[float]) -> dict[str, Any]:
        median = percentile(values, 50, numpy_module)
        return {
            "count": len(values),
            "median_ms": median,
            "p90_ms": percentile(values, 90, numpy_module),
            "p95_ms": percentile(values, 95, numpy_module),
            "fps_from_median": None if median in (None, 0.0) else 1000.0 / median,
        }

    return {"model_forward": stats(model), "end_to_end_track": stats(e2e)}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("otb", "folder", "video"), required=True)
    parser.add_argument("--sequence", help="Exact OTB sequence name (OTB mode)")
    parser.add_argument("--otb-root", type=Path, default=DEFAULT_OTB_ROOT)
    parser.add_argument("--input", type=Path, help="Image folder or video path")
    parser.add_argument("--init-bbox", nargs=4, type=float, metavar=("X", "Y", "W", "H"))
    parser.add_argument("--measure-model-forward", action="store_true")
    parser.add_argument("--warmup-forwards", type=int, default=0)
    args = parser.parse_args()

    if args.warmup_forwards < 0:
        parser.error("--warmup-forwards must be non-negative")
    if args.mode == "otb":
        if not args.sequence:
            parser.error("--sequence is required in OTB mode")
        if args.input is not None or args.init_bbox is not None:
            parser.error("--input/--init-bbox are not accepted in OTB mode")
    else:
        if args.input is None or args.init_bbox is None:
            parser.error("--input and --init-bbox are required in folder/video mode")
        if args.sequence is not None:
            parser.error("--sequence is only accepted in OTB mode")
    if args.warmup_forwards and not args.measure_model_forward:
        parser.error("--warmup-forwards requires --measure-model-forward")
    return args


def main() -> int:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    failure_path = output_dir / "failure.json"

    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    partial: dict[str, Any] = {
        "schema": "I0_spiketrack_runtime_provenance_v1",
        "started_utc": started_utc,
        "command": [sys.executable, *sys.argv],
        "status": "running",
    }

    try:
        identities = validate_identities(args.source_root.resolve(), args.checkpoint.resolve())
        partial["identities"] = identities
        sys.path.insert(0, str(args.source_root.resolve()))

        import cv2
        import numpy as np
        import psutil
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is required by the frozen official SpikeTrack tracker")
        configure_determinism(torch)
        environment = environment_record(torch, cv2, np)
        partial["environment"] = environment

        config_path = args.source_root.resolve() / CONFIG_RELATIVE_PATH
        from lib.config.spiketrack.config import cfg, update_config_from_file

        update_config_from_file(str(config_path))
        strict_result, parameter_counts = strict_load_probe(cfg, args.checkpoint.resolve(), torch)
        partial["strict_load"] = strict_result
        partial["parameter_counts"] = parameter_counts

        if args.mode == "otb":
            if not args.otb_root.is_dir():
                raise FileNotFoundError(f"Canonical OTB root is missing: {args.otb_root}")
            name, init_bbox, frames = otb_input(args.sequence, args.otb_root.resolve(), cv2)
            input_record = {
                "mode": "otb",
                "name": name,
                "canonical_otb_root": str(args.otb_root.resolve()),
                "official_initialization": True,
                "initial_bbox": init_bbox,
            }
        elif args.mode == "folder":
            if not args.input.is_dir():
                raise FileNotFoundError(f"Image folder is missing: {args.input}")
            name, init_bbox, frames = folder_input(args.input.resolve(), args.init_bbox, cv2)
            input_record = {
                "mode": "folder",
                "name": name,
                "input": str(args.input.resolve()),
                "official_initialization": False,
                "initial_bbox": init_bbox,
            }
        else:
            if not args.input.is_file():
                raise FileNotFoundError(f"Video is missing: {args.input}")
            name, init_bbox, frames = video_input(args.input.resolve(), args.init_bbox, cv2)
            input_record = {
                "mode": "video",
                "name": name,
                "input": str(args.input.resolve()),
                "official_initialization": False,
                "initial_bbox": init_bbox,
            }
        partial["input"] = input_record

        from lib.test.tracker.spiketrack_inf import SpikeTrack

        params = make_params(cfg)
        tracker = SpikeTrack(params, "otb" if args.mode == "otb" else args.mode, str(args.checkpoint.resolve()), False)
        forward_timer = ForwardTimer(tracker, torch) if args.measure_model_forward else None

        process = psutil.Process(os.getpid())
        torch.cuda.reset_peak_memory_stats(0)
        host_peak_rss = process.memory_info().rss
        rows: list[dict[str, Any]] = []
        boxes_float: list[list[float]] = []
        previous_output: OrderedDict[str, Any] = OrderedDict()
        measured_memory_reset = False

        try:
            for frame_index, frame_source, image, frame_info in frames:
                if frame_index == 1:
                    torch.cuda.synchronize()
                    frame_started = time.perf_counter()
                    tracker.initialize(image, frame_info)
                    torch.cuda.synchronize()
                    e2e_ms = (time.perf_counter() - frame_started) * 1000.0
                    bbox = list(init_bbox)
                    phase = "initialize"
                    measurement_state = "not_applicable"
                    encoder_ms: float | str = ""
                    decoder_ms: float | str = ""
                    model_ms: float | str = ""
                else:
                    forward_number = frame_index - 1
                    frame_info["previous_output"] = previous_output
                    if args.measure_model_forward and not measured_memory_reset and forward_number == args.warmup_forwards + 1:
                        torch.cuda.reset_peak_memory_stats(0)
                        host_peak_rss = process.memory_info().rss
                        measured_memory_reset = True
                    if forward_timer is not None:
                        forward_timer.start_frame()
                    torch.cuda.synchronize()
                    frame_started = time.perf_counter()
                    tracker_output, _search_spike_rates, _template_spike_rates = tracker.track(image, frame_info)
                    torch.cuda.synchronize()
                    e2e_ms = (time.perf_counter() - frame_started) * 1000.0
                    bbox = [float(value) for value in tracker_output["target_bbox"]]
                    previous_output = OrderedDict(tracker_output)
                    phase = "track"
                    measurement_state = "warmup" if forward_number <= args.warmup_forwards else "measured"
                    if forward_timer is None:
                        encoder_ms = decoder_ms = model_ms = ""
                    else:
                        encoder_ms, decoder_ms, model_ms = forward_timer.frame_values()

                boxes_float.append([float(value) for value in bbox])
                bbox_integer = [int(value) for value in bbox]
                rows.append(
                    {
                        "frame_index": frame_index,
                        "frame_source": frame_source,
                        "phase": phase,
                        "measurement_state": measurement_state,
                        "bbox_x_float": bbox[0],
                        "bbox_y_float": bbox[1],
                        "bbox_w_float": bbox[2],
                        "bbox_h_float": bbox[3],
                        "bbox_x_int": bbox_integer[0],
                        "bbox_y_int": bbox_integer[1],
                        "bbox_w_int": bbox_integer[2],
                        "bbox_h_int": bbox_integer[3],
                        "encoder_forward_ms": encoder_ms,
                        "decoder_forward_ms": decoder_ms,
                        "model_forward_ms": model_ms,
                        "end_to_end_ms": e2e_ms,
                    }
                )
                memory_info = process.memory_info()
                host_peak_rss = max(
                    host_peak_rss,
                    memory_info.rss,
                    int(getattr(memory_info, "peak_wset", 0)),
                )
        finally:
            if forward_timer is not None:
                forward_timer.close()

        if len(boxes_float) < 1:
            raise RuntimeError("No frames were processed")

        boxes_path = output_dir / "boxes.txt"
        # Match the accepted local operational baseline serialization byte-for-byte.
        with boxes_path.open("w", encoding="utf-8", newline="") as handle:
            for bbox in boxes_float:
                handle.write("\t".join(str(int(value)) for value in bbox) + "\r\n")

        timing_path = output_dir / "per_frame_timing.csv"
        with timing_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

        float_serialization = json.dumps(boxes_float, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        prediction_hashes = {
            "integer_boxes_sha256": sha256_file(boxes_path),
            "float_boxes_canonical_json_sha256": hashlib.sha256(float_serialization).hexdigest(),
            "integer_box_rows": len(boxes_float),
        }
        memory = {
            "scope": (
                "CUDA peaks cover measured track forwards after the warmup reset; "
                "host peak_wset covers the complete process lifetime"
                if args.measure_model_forward
                else "complete single-sequence process run"
            ),
            "cuda_peak_allocated_bytes": int(torch.cuda.max_memory_allocated(0)),
            "cuda_peak_reserved_bytes": int(torch.cuda.max_memory_reserved(0)),
            "host_process_peak_rss_bytes": int(host_peak_rss),
            "host_peak_method": "max(psutil rss samples, Windows peak_wset when available)",
        }
        timing = timing_summary(rows, np)

        provenance = {
            **partial,
            "status": "complete",
            "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "measurement": {
                "model_forward_instrumented": bool(args.measure_model_forward),
                "warmup_forwards_requested": args.warmup_forwards,
                "cuda_synchronized": True,
                "batch_size": 1,
                "precision": "FP32",
                "timing": timing,
                "memory": memory,
            },
            "prediction_hashes": prediction_hashes,
            "outputs": {
                "boxes": str(boxes_path),
                "per_frame_timing": str(timing_path),
            },
        }
        provenance_path = output_dir / "provenance.json"
        provenance_path.write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        if failure_path.exists():
            failure_path.unlink()
        print(json.dumps({"status": "complete", "output_dir": str(output_dir), **prediction_hashes}, sort_keys=True))
        return 0
    except Exception as exc:
        partial.update(
            {
                "status": "failed",
                "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )
        failure_path.write_text(json.dumps(partial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
