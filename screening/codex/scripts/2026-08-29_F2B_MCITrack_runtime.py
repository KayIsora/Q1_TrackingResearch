#!/usr/bin/env python3
"""Shared runtime for the locked F2-B MCITrack mini-probe.

This module keeps the official MCITrack model/evaluator path intact while adding
runtime-only observation hooks and exact tracker-state snapshot/restore support.
It does not write scientific outcomes by itself.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import torch


RESEARCH_ROOT = Path(r"E:\Robot_Backup\Q1_TrackingResearch")
SOURCE_ROOT = Path(r"E:\Robot_Backup\tmp\stage2_batchB_root_20260825_7da81ad\mcitrack")
CHECKPOINT = Path(r"E:\Robot_Backup\tmp\stage2b_checkpoints\mcitrack\MCITRACK_ep0300.pth.tar")
CONFIG_REL = Path("experiments/mcitrack/mcitrack_b224.yaml")
CONFIG_PATH = SOURCE_ROOT / CONFIG_REL
DATASET_ROOT = Path(r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015")
ARTIFACT_ROOT = RESEARCH_ROOT / "screening/codex/artifacts/F2B_MCITrack"

EXPECTED_SOURCE_SHA = "e667193eaec4c8a73d4bdd856a662aecdb844b43"
EXPECTED_CHECKPOINT_SHA256 = "6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9"
EXPECTED_CONFIG_SHA256 = "2F498726C55601BA1B056D282E80C600F330EBDB5613ACB9B57041520EC76CC7"
SEED = 20260829
MAX_MODEL_SECONDS = 6 * 60 * 60

PAIR_SPECS: List[Dict[str, Any]] = [
    {"pair_id": "MCI-P01", "sequence": "Liquor", "primary": (565, 589), "control": (20, 44)},
    {"pair_id": "MCI-P02", "sequence": "Car4", "primary": (113, 137), "control": (221, 245)},
    {"pair_id": "MCI-P03", "sequence": "Crowds", "primary": (33, 37), "control": (161, 165)},
    {"pair_id": "MCI-P04", "sequence": "Girl", "primary": (411, 429), "control": (363, 381)},
    {"pair_id": "MCI-P05", "sequence": "Human3", "primary": (57, 81), "control": (264, 288)},
    {"pair_id": "MCI-P06", "sequence": "Suv", "primary": (372, 399), "control": (410, 437)},
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(SOURCE_ROOT), *args], text=True).strip()


def pinned_config_blob_sha256() -> str:
    blob = subprocess.check_output(
        ["git", "-C", str(SOURCE_ROOT), "show", f"{EXPECTED_SOURCE_SHA}:{CONFIG_REL.as_posix()}"]
    )
    return hashlib.sha256(blob).hexdigest().upper()


def set_determinism(seed: int = SEED) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    if hasattr(torch.backends, "cudnn"):
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def _install_cpu_cuda_shim() -> None:
    """Runtime-only device shim; weights/operators remain unchanged FP32."""
    torch.Tensor.cuda = lambda self, *args, **kwargs: self  # type: ignore[assignment]
    torch.nn.Module.cuda = lambda self, *args, **kwargs: self  # type: ignore[assignment]


def bootstrap_official(device: str = "cuda") -> Dict[str, Any]:
    """Resolve official config/evaluator/tracker construction and strict load."""
    if device not in {"cuda", "cpu"}:
        raise ValueError(f"Unsupported device: {device}")
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
    if device == "cpu":
        _install_cpu_cuda_shim()

    source_str = str(SOURCE_ROOT)
    if source_str not in sys.path:
        sys.path.insert(0, source_str)
    os.chdir(SOURCE_ROOT)

    # The release builder tries to bootstrap an external pretraining checkpoint.
    # The complete official tracker checkpoint is strict-loaded immediately after
    # construction, so bypassing only that unavailable initialization does not
    # alter the resulting scientific model state.
    import lib.models.mcitrack.fastitpn as fastitpn

    bootstrap_record: Dict[str, Any] = {
        "pretrained_bootstrap_bypassed": True,
        "pretrained_bootstrap_reason": "complete official tracker checkpoint strict-load follows construction",
        "device_mode": device,
    }

    def _skip_pretrained(model: torch.nn.Module, checkpoint: str, pos_type: str) -> None:
        bootstrap_record["bypassed_pretrained_path"] = str(checkpoint)
        bootstrap_record["bypassed_pretrained_pos_type"] = str(pos_type)
        return None

    fastitpn.load_pretrained = _skip_pretrained  # type: ignore[assignment]

    from lib.test.evaluation.environment import EnvSettings
    import lib.test.evaluation.data as evaluation_data
    import lib.test.evaluation.tracker as evaluation_tracker
    import lib.test.parameter.mcitrack as parameter_module
    from lib.test.evaluation.otbdataset import OTBDataset

    settings = EnvSettings()
    settings.otb_path = str(DATASET_ROOT)
    settings.prj_dir = str(SOURCE_ROOT)
    settings.save_dir = str(CHECKPOINT.parent)
    settings.results_path = str(ARTIFACT_ROOT / "official_evaluator_results_not_written")

    evaluation_data.env_settings = lambda: settings  # type: ignore[assignment]
    evaluation_tracker.env_settings = lambda: settings  # type: ignore[assignment]
    parameter_module.env_settings = lambda: SimpleNamespace(  # type: ignore[assignment]
        prj_dir=str(SOURCE_ROOT), save_dir=str(CHECKPOINT.parent)
    )

    dataset = OTBDataset()
    sequence_list = dataset.get_sequence_list()
    evaluator = evaluation_tracker.Tracker("mcitrack", "mcitrack_b224", "otb")
    params = evaluator.get_parameters()
    params.checkpoint = str(CHECKPOINT)
    params.debug = 0
    tracker = evaluator.create_tracker(params)

    bootstrap_record.update(
        {
            "official_dataset_class": f"{dataset.__class__.__module__}.{dataset.__class__.__name__}",
            "official_evaluator_class": f"{evaluator.__class__.__module__}.{evaluator.__class__.__name__}",
            "official_tracker_class": f"{tracker.__class__.__module__}.{tracker.__class__.__name__}",
            "strict_checkpoint_load": "PASS",
            "model_parameter_count": int(sum(p.numel() for p in tracker.network.parameters())),
            "model_parameter_device": str(next(tracker.network.parameters()).device),
            "model_parameter_dtype": str(next(tracker.network.parameters()).dtype),
            "torch_version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
    )
    return {
        "dataset": dataset,
        "sequences": sequence_list,
        "evaluator": evaluator,
        "params": params,
        "tracker": tracker,
        "record": bootstrap_record,
    }


def official_contract_record() -> Dict[str, Any]:
    config_hash = sha256_file(CONFIG_PATH)
    pinned_blob_hash = pinned_config_blob_sha256()
    worktree_config_oid = git_text("hash-object", CONFIG_REL.as_posix())
    pinned_config_oid = git_text("rev-parse", f"{EXPECTED_SOURCE_SHA}:{CONFIG_REL.as_posix()}")
    config_diff_clean = subprocess.run(
        ["git", "-C", str(SOURCE_ROOT), "diff", "--quiet", "--", CONFIG_REL.as_posix()],
        check=False,
    ).returncode == 0
    return {
        "source_root": str(SOURCE_ROOT),
        "source_sha": git_text("rev-parse", "HEAD"),
        "source_clean": git_text("status", "--porcelain=v1") == "",
        "source_remote": git_text("remote", "get-url", "origin"),
        "config_path": str(CONFIG_PATH),
        "config_sha256": config_hash,
        "pinned_config_blob_sha256": pinned_blob_hash,
        "config_worktree_git_oid": worktree_config_oid,
        "config_pinned_git_oid": pinned_config_oid,
        "config_git_diff_clean": config_diff_clean,
        "config_hash_matches_pinned_blob": (
            config_hash == EXPECTED_CONFIG_SHA256
            and worktree_config_oid == pinned_config_oid
            and config_diff_clean
        ),
        "config_eol_note": "Raw worktree and Git-blob SHA-256 differ under Windows CRLF checkout; Git object identity and a clean path diff verify pinned content.",
        "checkpoint_path": str(CHECKPOINT),
        "checkpoint_bytes": CHECKPOINT.stat().st_size,
        "checkpoint_sha256": sha256_file(CHECKPOINT),
        "dataset_root": str(DATASET_ROOT),
    }


def validate_contract(record: Dict[str, Any]) -> None:
    if record["source_sha"] != EXPECTED_SOURCE_SHA:
        raise RuntimeError(f"Pinned source mismatch: {record['source_sha']}")
    if not record["source_clean"]:
        raise RuntimeError("Pinned source worktree is not clean")
    if not record["config_hash_matches_pinned_blob"]:
        raise RuntimeError("Config hash does not match pinned source blob")
    if record["checkpoint_sha256"] != EXPECTED_CHECKPOINT_SHA256:
        raise RuntimeError("Checkpoint SHA-256 mismatch")


def expected_scientific_row_count() -> int:
    total = 0
    for pair in PAIR_SPECS:
        for key in ("primary", "control"):
            start, end = pair[key]
            total += end - start + 1
    return total


def sequence_contract(sequences: Iterable[Any]) -> Dict[str, Any]:
    by_name = {seq.name: seq for seq in sequences}
    rows: List[Dict[str, Any]] = []
    for pair in PAIR_SPECS:
        seq = by_name[pair["sequence"]]
        max_end = max(pair["primary"][1], pair["control"][1])
        if len(seq.frames) != len(seq.ground_truth_rect):
            raise RuntimeError(f"Frame/GT length mismatch for {seq.name}")
        if max_end > len(seq.frames):
            raise RuntimeError(f"Locked interval exceeds sequence length for {seq.name}")
        if not all(Path(frame).is_file() for frame in seq.frames[:max_end]):
            raise RuntimeError(f"Missing official evaluator frame for {seq.name}")
        rows.append(
            {
                "pair_id": pair["pair_id"],
                "sequence": seq.name,
                "official_frame_count": len(seq.frames),
                "official_gt_rows": len(seq.ground_truth_rect),
                "primary": list(pair["primary"]),
                "control": list(pair["control"]),
            }
        )
    return {"pairs": rows, "expected_rows": expected_scientific_row_count()}


def read_frame(evaluator: Any, sequence: Any, one_based_frame: int) -> np.ndarray:
    return evaluator._read_image(sequence.frames[one_based_frame - 1])


def _clone_optional_tensor(value: Optional[torch.Tensor]) -> Optional[torch.Tensor]:
    return None if value is None else value.detach().clone()


def snapshot_tracker(tracker: Any) -> Dict[str, Any]:
    snapshot: Dict[str, Any] = {
        "state": copy.deepcopy(tracker.state),
        "frame_id": int(tracker.frame_id),
        "h_state": [_clone_optional_tensor(value) for value in tracker.h_state],
        "template_list": list(tracker.template_list),
        "template_anno_list": list(tracker.template_anno_list),
        "memory_template_list": list(tracker.memory_template_list),
        "memory_template_anno_list": list(tracker.memory_template_anno_list),
        "python_rng": random.getstate(),
        "numpy_rng": np.random.get_state(),
        "torch_rng": torch.get_rng_state().clone(),
    }
    if torch.cuda.is_available():
        snapshot["cuda_rng"] = [state.clone() for state in torch.cuda.get_rng_state_all()]
    return snapshot


def restore_tracker(tracker: Any, snapshot: Dict[str, Any]) -> None:
    tracker.state = copy.deepcopy(snapshot["state"])
    tracker.frame_id = int(snapshot["frame_id"])
    tracker.h_state = [_clone_optional_tensor(value) for value in snapshot["h_state"]]
    tracker.template_list = list(snapshot["template_list"])
    tracker.template_anno_list = list(snapshot["template_anno_list"])
    tracker.memory_template_list = list(snapshot["memory_template_list"])
    tracker.memory_template_anno_list = list(snapshot["memory_template_anno_list"])
    random.setstate(snapshot["python_rng"])
    np.random.set_state(snapshot["numpy_rng"])
    torch.set_rng_state(snapshot["torch_rng"])
    if torch.cuda.is_available() and "cuda_rng" in snapshot:
        torch.cuda.set_rng_state_all(snapshot["cuda_rng"])


def clone_state_list(states: Iterable[Optional[torch.Tensor]]) -> List[Optional[torch.Tensor]]:
    return [_clone_optional_tensor(value) for value in states]


def materialize_state_list(tracker: Any, states: Iterable[Optional[torch.Tensor]]) -> List[torch.Tensor]:
    states_list = list(states)
    first = next((value for value in states_list if value is not None), None)
    device = first.device if first is not None else next(tracker.network.parameters()).device
    dtype = first.dtype if first is not None else torch.float32
    shape = (
        1,
        int(tracker.fx_sz * tracker.fx_sz),
        int(tracker.network.neck.d_inner),
        int(tracker.network.neck.d_state),
    )
    return [
        torch.zeros(shape, device=device, dtype=dtype) if value is None else value.detach().clone()
        for value in states_list
    ]


def state_descriptives(states: Iterable[Optional[torch.Tensor]]) -> Dict[str, Any]:
    norms: List[float] = []
    finite: List[bool] = []
    is_none: List[bool] = []
    for value in states:
        if value is None:
            norms.append(0.0)
            finite.append(True)
            is_none.append(True)
        else:
            norms.append(float(torch.linalg.vector_norm(value.detach().float()).item()))
            finite.append(bool(torch.isfinite(value).all().item()))
            is_none.append(False)
    return {"norms": norms, "finite": finite, "is_none": is_none}


def output_values(output: Dict[str, Any]) -> Tuple[List[float], float]:
    bbox = [float(value) for value in output["target_bbox"]]
    score_value = output["best_score"]
    score = float(score_value.detach().item() if torch.is_tensor(score_value) else score_value)
    return bbox, score


def max_abs_diff(left: Iterable[float], right: Iterable[float]) -> float:
    left_arr = np.asarray(list(left), dtype=np.float64)
    right_arr = np.asarray(list(right), dtype=np.float64)
    return float(np.max(np.abs(left_arr - right_arr))) if left_arr.size else 0.0


def _tensor_equal(left: torch.Tensor, right: torch.Tensor) -> bool:
    return left.shape == right.shape and left.dtype == right.dtype and left.device == right.device and torch.equal(left, right)


def continuation_equal(left: Dict[str, Any], right: Dict[str, Any]) -> Tuple[bool, List[str]]:
    mismatches: List[str] = []
    if left["state"] != right["state"]:
        mismatches.append("state")
    if left["frame_id"] != right["frame_id"]:
        mismatches.append("frame_id")
    for key in ("h_state", "template_list", "template_anno_list", "memory_template_list", "memory_template_anno_list"):
        if len(left[key]) != len(right[key]):
            mismatches.append(f"{key}.length")
            continue
        for index, (lval, rval) in enumerate(zip(left[key], right[key])):
            if lval is None or rval is None:
                if lval is not rval:
                    mismatches.append(f"{key}[{index}].none")
            elif not _tensor_equal(lval, rval):
                mismatches.append(f"{key}[{index}]")
    if not torch.equal(left["torch_rng"], right["torch_rng"]):
        mismatches.append("torch_rng")
    if "cuda_rng" in left or "cuda_rng" in right:
        lcuda = left.get("cuda_rng", [])
        rcuda = right.get("cuda_rng", [])
        if len(lcuda) != len(rcuda) or any(not torch.equal(a, b) for a, b in zip(lcuda, rcuda)):
            mismatches.append("cuda_rng")
    return not mismatches, mismatches


class CallInstrumentation:
    """Read-only module-call and state-output instrumentation."""

    def __init__(self, network: torch.nn.Module):
        self.network = network
        self.enabled = False
        self.counts: Dict[str, int] = {}
        self.template_counts: List[int] = []
        self.state_records: Dict[str, Dict[str, Any]] = {}
        self.handles: List[Any] = []
        self._install()

    def _increment(self, name: str) -> None:
        if self.enabled:
            self.counts[name] = self.counts.get(name, 0) + 1

    def _install(self) -> None:
        def encoder_pre(module: torch.nn.Module, inputs: Tuple[Any, ...]) -> None:
            if self.enabled:
                self._increment("encoder")
                self.template_counts.append(len(inputs[0]))

        self.handles.append(self.network.encoder.register_forward_pre_hook(encoder_pre))

        for index, block in enumerate(self.network.encoder.body.blocks):
            self.handles.append(block.register_forward_hook(self._simple_hook(f"backbone_block_{index}")))

        for index, layer in enumerate(self.network.neck.layers):
            self.handles.append(layer.register_forward_hook(self._state_hook(index)))

        for index, interaction in enumerate(self.network.neck.interactions):
            self.handles.append(interaction.injector.register_forward_hook(self._simple_hook(f"injector_{index}")))
            self.handles.append(interaction.extractor.register_forward_hook(self._simple_hook(f"extractor_{index}_0")))
            if interaction.extra_extractors is not None:
                for extra_index, extractor in enumerate(interaction.extra_extractors, start=1):
                    self.handles.append(
                        extractor.register_forward_hook(self._simple_hook(f"extractor_{index}_{extra_index}"))
                    )

        self.handles.append(self.network.decoder.register_forward_hook(self._simple_hook("decoder")))

    def _simple_hook(self, name: str):
        def hook(module: torch.nn.Module, inputs: Tuple[Any, ...], output: Any) -> None:
            self._increment(name)

        return hook

    def _state_hook(self, index: int):
        name = f"mamba_layer_{index}"

        def hook(module: torch.nn.Module, inputs: Tuple[Any, ...], output: Any) -> None:
            if not self.enabled:
                return
            self._increment(name)
            state = output[1]
            self.state_records[name] = {
                "identity": f"network.neck.layers.{index}",
                "module_class": f"{module.__class__.__module__}.{module.__class__.__name__}",
                "shape": list(state.shape),
                "dtype": str(state.dtype),
                "device": str(state.device),
                "finite": bool(torch.isfinite(state).all().item()),
            }

        return hook

    def begin(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self.counts = {}
        self.template_counts = []
        self.state_records = {}

    def end(self) -> Dict[str, Any]:
        record = {
            "counts": dict(sorted(self.counts.items())),
            "template_counts": list(self.template_counts),
            "state_records": dict(sorted(self.state_records.items())),
        }
        self.enabled = False
        return record

    def close(self) -> None:
        for handle in self.handles:
            handle.remove()
        self.handles = []


def compute_signature(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "counts": record["counts"],
        "template_counts": record["template_counts"],
    }


def run_track(
    tracker: Any,
    image: np.ndarray,
    info: Dict[str, Any],
    instrumentation: Optional[CallInstrumentation] = None,
    instrumentation_enabled: bool = True,
) -> Tuple[Dict[str, Any], Dict[str, Any], float]:
    if instrumentation is not None:
        instrumentation.begin(instrumentation_enabled)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    started = time.perf_counter()
    output = tracker.track(image, info)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    record = instrumentation.end() if instrumentation is not None else {"counts": {}, "template_counts": [], "state_records": {}}
    return output, record, elapsed


def xywh_iou(prediction: Iterable[float], ground_truth: Iterable[float]) -> float:
    px, py, pw, ph = [float(v) for v in prediction]
    gx, gy, gw, gh = [float(v) for v in ground_truth]
    pxa, pya, pxb, pyb = px, py, px + max(0.0, pw), py + max(0.0, ph)
    gxa, gya, gxb, gyb = gx, gy, gx + max(0.0, gw), gy + max(0.0, gh)
    ix = max(0.0, min(pxb, gxb) - max(pxa, gxa))
    iy = max(0.0, min(pyb, gyb) - max(pya, gya))
    intersection = ix * iy
    union = max(0.0, pw) * max(0.0, ph) + max(0.0, gw) * max(0.0, gh) - intersection
    return intersection / union if union > 0 else 0.0


def center_error(prediction: Iterable[float], ground_truth: Iterable[float]) -> float:
    px, py, pw, ph = [float(v) for v in prediction]
    gx, gy, gw, gh = [float(v) for v in ground_truth]
    return float(np.hypot((px + pw / 2.0) - (gx + gw / 2.0), (py + ph / 2.0) - (gy + gh / 2.0)))


def json_compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
