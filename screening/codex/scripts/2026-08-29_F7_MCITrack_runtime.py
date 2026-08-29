#!/usr/bin/env python3
"""Shared runtime for the locked F7 MCITrack resource re-entry and mini-probe."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from datetime import datetime, timezone
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
F7_EXTERNAL_ROOT = Path(r"F:\Q1_TrackingResearch_Data\MCITrack_F7_2026-08-29")
BOOTSTRAP_EXTERNAL = F7_EXTERNAL_ROOT / "official_asset/fast_itpn_base_clipl_e1600.pt"
BOOTSTRAP_REQUIRED = SOURCE_ROOT / "pretrained/fast_itpn_base_clipl_e1600.pt"
ASSET_MANIFEST = F7_EXTERNAL_ROOT / "manifests/official_asset_manifest.json"
EXTERNAL_RESULTS_ROOT = F7_EXTERNAL_ROOT / "results"
ARTIFACT_ROOT = RESEARCH_ROOT / "screening/codex/artifacts/F7_MCITrack"

EXPECTED_SOURCE_SHA = "e667193eaec4c8a73d4bdd856a662aecdb844b43"
EXPECTED_CHECKPOINT_SHA256 = "6F28F9425FE6E7B52ECA4D1D9ADC7A59AA51558A21BE300F4F456AEBBD4EB2D9"
EXPECTED_CONFIG_SHA256 = "2F498726C55601BA1B056D282E80C600F330EBDB5613ACB9B57041520EC76CC7"
EXPECTED_BOOTSTRAP_SHA256 = "626FD426DD89B2681D8B3942FA00E05FFFB467AF111C7BBD6A0A4B8BC0AFC388"
EXPECTED_BOOTSTRAP_BYTES = 180830695
EXPECTED_BOOTSTRAP_FILE_ID = "1hxth6RWiJ-3rY21CClZqjl2xsL07Kt17"
EXPECTED_BOOTSTRAP_FOLDER_ID = "1qDAMcU3JpahV7MriEOl4KfjKvAAFXd3E"
F7_ASSET_VERIFIED_UTC = datetime.fromisoformat("2026-08-29T03:46:22.9121465+00:00")
F7_DEADLINE_UTC = datetime.fromisoformat("2026-08-29T07:46:22.9121465+00:00")
SEED = 20260829

LOCKED_SEQUENCE_NAMES = ("Liquor", "Car4", "Crowds", "Girl", "Human3", "Suv")
PAIR_SPECS: List[Dict[str, Any]] = [
    {"pair_id": "MCI-P01", "sequence": "Liquor", "primary": (565, 589), "control": (20, 44)},
    {"pair_id": "MCI-P02", "sequence": "Car4", "primary": (113, 137), "control": (221, 245)},
    {"pair_id": "MCI-P03", "sequence": "Crowds", "primary": (33, 37), "control": (161, 165)},
    {"pair_id": "MCI-P04", "sequence": "Girl", "primary": (411, 429), "control": (363, 381)},
    {"pair_id": "MCI-P05", "sequence": "Human3", "primary": (57, 81), "control": (264, 288)},
    {"pair_id": "MCI-P06", "sequence": "Suv", "primary": (372, 399), "control": (410, 437)},
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def enforce_deadline() -> None:
    if utc_now() > F7_DEADLINE_UTC:
        raise RuntimeError("F7 four-hour cap exceeded")


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
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def bootstrap_official(device: str = "cuda") -> Dict[str, Any]:
    """Construct the official B224 tracker with the exact official bootstrap asset."""
    enforce_deadline()
    if device != "cuda":
        raise ValueError("F7 permits only the existing CUDA execution path")
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")

    source_str = str(SOURCE_ROOT)
    if source_str not in sys.path:
        sys.path.insert(0, source_str)
    os.chdir(SOURCE_ROOT)

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
    original_entries = dataset.sequence_info_list
    selected_entries = [entry for entry in original_entries if entry["name"] in LOCKED_SEQUENCE_NAMES]
    selected_names = tuple(entry["name"] for entry in selected_entries)
    if len(selected_entries) != 6 or set(selected_names) != set(LOCKED_SEQUENCE_NAMES):
        raise RuntimeError(f"Restricted official dataset metadata mismatch: {selected_names}")
    if any(not any(entry is original for original in original_entries) for entry in selected_entries):
        raise RuntimeError("Restricted dataset filter did not preserve official dictionary identity")
    dataset.sequence_info_list = selected_entries
    sequence_list = dataset.get_sequence_list()

    evaluator = evaluation_tracker.Tracker("mcitrack", "mcitrack_b224", "otb")
    params = evaluator.get_parameters()
    params.checkpoint = str(CHECKPOINT)
    params.debug = 0
    tracker = evaluator.create_tracker(params)

    record = {
        "pretrained_bootstrap_bypassed": False,
        "official_bootstrap_path": str(BOOTSTRAP_REQUIRED),
        "official_bootstrap_sha256": sha256_file(BOOTSTRAP_REQUIRED),
        "official_bootstrap_bytes": BOOTSTRAP_REQUIRED.stat().st_size,
        "official_dataset_class": f"{dataset.__class__.__module__}.{dataset.__class__.__name__}",
        "official_evaluator_class": f"{evaluator.__class__.__module__}.{evaluator.__class__.__name__}",
        "official_tracker_class": f"{tracker.__class__.__module__}.{tracker.__class__.__name__}",
        "official_metadata_names_in_preserved_order": list(selected_names),
        "official_metadata_dictionary_identity_preserved": True,
        "non_allowlisted_sequence_access": "NONE",
        "strict_checkpoint_load": "PASS",
        "strict_load_source_line": "lib/test/tracker/mcitrack.py:18 strict=True",
        "model_parameter_count": int(sum(parameter.numel() for parameter in tracker.network.parameters())),
        "model_parameter_device": str(next(tracker.network.parameters()).device),
        "model_parameter_dtype": str(next(tracker.network.parameters()).dtype),
        "torch_version": torch.__version__,
        "cuda_available": bool(torch.cuda.is_available()),
        "cuda_device": torch.cuda.get_device_name(0),
    }
    return {
        "dataset": dataset,
        "sequences": sequence_list,
        "evaluator": evaluator,
        "params": params,
        "tracker": tracker,
        "record": record,
    }


def official_contract_record() -> Dict[str, Any]:
    enforce_deadline()
    manifest = json.loads(ASSET_MANIFEST.read_text(encoding="utf-8"))
    config_hash = sha256_file(CONFIG_PATH)
    worktree_config_oid = git_text("hash-object", CONFIG_REL.as_posix())
    pinned_config_oid = git_text("rev-parse", f"{EXPECTED_SOURCE_SHA}:{CONFIG_REL.as_posix()}")
    config_diff_clean = subprocess.run(
        ["git", "-C", str(SOURCE_ROOT), "diff", "--quiet", "--", CONFIG_REL.as_posix()], check=False
    ).returncode == 0
    external_hash = sha256_file(BOOTSTRAP_EXTERNAL)
    required_hash = sha256_file(BOOTSTRAP_REQUIRED)
    return {
        "source_root": str(SOURCE_ROOT),
        "source_sha": git_text("rev-parse", "HEAD"),
        "source_clean": git_text("status", "--porcelain=v1") == "",
        "source_remote": git_text("remote", "get-url", "origin"),
        "config_path": str(CONFIG_PATH),
        "config_sha256": config_hash,
        "pinned_config_blob_sha256": pinned_config_blob_sha256(),
        "config_worktree_git_oid": worktree_config_oid,
        "config_pinned_git_oid": pinned_config_oid,
        "config_hash_matches_pinned_blob": (
            config_hash == EXPECTED_CONFIG_SHA256
            and worktree_config_oid == pinned_config_oid
            and config_diff_clean
        ),
        "checkpoint_path": str(CHECKPOINT),
        "checkpoint_bytes": CHECKPOINT.stat().st_size,
        "checkpoint_sha256": sha256_file(CHECKPOINT),
        "bootstrap_external_path": str(BOOTSTRAP_EXTERNAL),
        "bootstrap_required_path": str(BOOTSTRAP_REQUIRED),
        "bootstrap_external_bytes": BOOTSTRAP_EXTERNAL.stat().st_size,
        "bootstrap_required_bytes": BOOTSTRAP_REQUIRED.stat().st_size,
        "bootstrap_external_sha256": external_hash,
        "bootstrap_required_sha256": required_hash,
        "bootstrap_copy_exact": external_hash == required_hash,
        "bootstrap_manifest": manifest,
        "dataset_root": str(DATASET_ROOT),
        "f7_asset_verified_utc": F7_ASSET_VERIFIED_UTC.isoformat(),
        "f7_deadline_utc": F7_DEADLINE_UTC.isoformat(),
    }


def validate_contract(record: Dict[str, Any]) -> None:
    manifest = record["bootstrap_manifest"]
    gates = {
        "source_sha": record["source_sha"] == EXPECTED_SOURCE_SHA,
        "source_clean": record["source_clean"],
        "source_remote": record["source_remote"] == "https://github.com/kangben258/MCITrack.git",
        "config": record["config_hash_matches_pinned_blob"],
        "checkpoint": record["checkpoint_sha256"] == EXPECTED_CHECKPOINT_SHA256,
        "bootstrap_bytes": (
            record["bootstrap_external_bytes"] == EXPECTED_BOOTSTRAP_BYTES
            and record["bootstrap_required_bytes"] == EXPECTED_BOOTSTRAP_BYTES
        ),
        "bootstrap_hash": (
            record["bootstrap_external_sha256"] == EXPECTED_BOOTSTRAP_SHA256
            and record["bootstrap_required_sha256"] == EXPECTED_BOOTSTRAP_SHA256
            and record["bootstrap_copy_exact"]
        ),
        "manifest_identity": (
            manifest["display_name"] == "fast_itpn_base_clipl_e1600.pt"
            and manifest["official_file_id"] == EXPECTED_BOOTSTRAP_FILE_ID
            and manifest["official_folder_id"] == EXPECTED_BOOTSTRAP_FOLDER_ID
            and int(manifest["download_count"]) == 1
            and int(manifest["byte_count"]) == EXPECTED_BOOTSTRAP_BYTES
            and manifest["sha256"] == EXPECTED_BOOTSTRAP_SHA256
        ),
    }
    failed = [name for name, value in gates.items() if not value]
    if failed:
        raise RuntimeError(f"F7 identity contract failed: {failed}")


def expected_scientific_row_count() -> int:
    return sum(
        end - start + 1
        for pair in PAIR_SPECS
        for start, end in (pair["primary"], pair["control"])
    )


def sequence_contract(sequences: Iterable[Any]) -> Dict[str, Any]:
    by_name = {sequence.name: sequence for sequence in sequences}
    if set(by_name) != set(LOCKED_SEQUENCE_NAMES):
        raise RuntimeError(f"Restricted sequence set mismatch: {sorted(by_name)}")
    rows: List[Dict[str, Any]] = []
    for pair in PAIR_SPECS:
        sequence = by_name[pair["sequence"]]
        max_end = max(pair["primary"][1], pair["control"][1])
        if len(sequence.frames) != len(sequence.ground_truth_rect):
            raise RuntimeError(f"Frame/GT length mismatch for {sequence.name}")
        if max_end > len(sequence.frames):
            raise RuntimeError(f"Locked interval exceeds sequence length for {sequence.name}")
        if not all(Path(frame).is_file() for frame in sequence.frames[:max_end]):
            raise RuntimeError(f"Missing official evaluator frame for {sequence.name}")
        rows.append({
            "pair_id": pair["pair_id"],
            "sequence": sequence.name,
            "official_frame_count": len(sequence.frames),
            "official_gt_rows": len(sequence.ground_truth_rect),
            "primary": list(pair["primary"]),
            "control": list(pair["control"]),
        })
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
        "cuda_rng": [state.clone() for state in torch.cuda.get_rng_state_all()],
    }
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
    torch.cuda.set_rng_state_all(snapshot["cuda_rng"])


def clone_state_list(states: Iterable[Optional[torch.Tensor]]) -> List[Optional[torch.Tensor]]:
    return [_clone_optional_tensor(value) for value in states]


def materialize_state_list(tracker: Any, states: Iterable[Optional[torch.Tensor]]) -> List[torch.Tensor]:
    states_list = list(states)
    first = next((value for value in states_list if value is not None), None)
    device = first.device if first is not None else next(tracker.network.parameters()).device
    dtype = first.dtype if first is not None else torch.float32
    shape = (1, int(tracker.fx_sz * tracker.fx_sz), int(tracker.network.neck.d_inner), int(tracker.network.neck.d_state))
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
        for index, (left_value, right_value) in enumerate(zip(left[key], right[key])):
            if left_value is None or right_value is None:
                if left_value is not right_value:
                    mismatches.append(f"{key}[{index}].none")
            elif not _tensor_equal(left_value, right_value):
                mismatches.append(f"{key}[{index}]")
    if not torch.equal(left["torch_rng"], right["torch_rng"]):
        mismatches.append("torch_rng")
    if len(left["cuda_rng"]) != len(right["cuda_rng"]) or any(
        not torch.equal(a, b) for a, b in zip(left["cuda_rng"], right["cuda_rng"])
    ):
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
                    self.handles.append(extractor.register_forward_hook(self._simple_hook(f"extractor_{index}_{extra_index}")))
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
    return {"counts": record["counts"], "template_counts": record["template_counts"]}


def run_track(
    tracker: Any,
    image: np.ndarray,
    info: Dict[str, Any],
    instrumentation: Optional[CallInstrumentation] = None,
    instrumentation_enabled: bool = True,
) -> Tuple[Dict[str, Any], Dict[str, Any], float]:
    enforce_deadline()
    if instrumentation is not None:
        instrumentation.begin(instrumentation_enabled)
    torch.cuda.synchronize()
    started = time.perf_counter()
    output = tracker.track(image, info)
    torch.cuda.synchronize()
    elapsed = time.perf_counter() - started
    record = instrumentation.end() if instrumentation is not None else {"counts": {}, "template_counts": [], "state_records": {}}
    return output, record, elapsed


def xywh_iou(prediction: Iterable[float], ground_truth: Iterable[float]) -> float:
    px, py, pw, ph = [float(value) for value in prediction]
    gx, gy, gw, gh = [float(value) for value in ground_truth]
    pxa, pya, pxb, pyb = px, py, px + max(0.0, pw), py + max(0.0, ph)
    gxa, gya, gxb, gyb = gx, gy, gx + max(0.0, gw), gy + max(0.0, gh)
    ix = max(0.0, min(pxb, gxb) - max(pxa, gxa))
    iy = max(0.0, min(pyb, gyb) - max(pya, gya))
    intersection = ix * iy
    union = max(0.0, pw) * max(0.0, ph) + max(0.0, gw) * max(0.0, gh) - intersection
    return intersection / union if union > 0 else 0.0


def center_error(prediction: Iterable[float], ground_truth: Iterable[float]) -> float:
    px, py, pw, ph = [float(value) for value in prediction]
    gx, gy, gw, gh = [float(value) for value in ground_truth]
    return float(np.hypot((px + pw / 2.0) - (gx + gw / 2.0), (py + ph / 2.0) - (gy + gh / 2.0)))


def json_compact(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
