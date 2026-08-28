#!/usr/bin/env python3
"""Final authorized restricted-dataset adapter for F2-B R1.

All scientific/runtime helpers are reused from the initial F2-B implementation.
The only compatibility change is filtering the official OTBDataset metadata to
the six locked names before its unchanged get_sequence_list() is called.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import torch


BASE_RUNTIME_PATH = Path(__file__).with_name("2026-08-29_F2B_MCITrack_runtime.py")
BASE_SPEC = importlib.util.spec_from_file_location("f2b_mcitrack_base_runtime", BASE_RUNTIME_PATH)
if BASE_SPEC is None or BASE_SPEC.loader is None:
    raise RuntimeError(f"Unable to load base runtime: {BASE_RUNTIME_PATH}")
base = importlib.util.module_from_spec(BASE_SPEC)
BASE_SPEC.loader.exec_module(base)

for exported_name in dir(base):
    if not exported_name.startswith("__"):
        globals()[exported_name] = getattr(base, exported_name)

ARTIFACT_ROOT = RESEARCH_ROOT / "screening/codex/artifacts/F2B_MCITrack_R1"
base.ARTIFACT_ROOT = ARTIFACT_ROOT
LOCKED_SEQUENCE_NAMES = ("Liquor", "Car4", "Crowds", "Girl", "Human3", "Suv")


def bootstrap_official(device: str = "cuda") -> Dict[str, Any]:
    """Construct the official tracker after the one authorized dataset filter."""
    if device not in {"cuda", "cpu"}:
        raise ValueError(f"Unsupported device: {device}")
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
    if device == "cpu":
        base._install_cpu_cuda_shim()

    source_str = str(SOURCE_ROOT)
    if source_str not in sys.path:
        sys.path.insert(0, source_str)
    os.chdir(SOURCE_ROOT)

    import lib.models.mcitrack.fastitpn as fastitpn

    bootstrap_record: Dict[str, Any] = {
        "pretrained_bootstrap_bypassed": True,
        "pretrained_bootstrap_reason": "complete official tracker checkpoint strict-load follows construction",
        "device_mode": device,
        "restricted_dataset_adapter": "LOCKED_FINAL_ATTEMPT",
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
    original_entries = dataset.sequence_info_list
    selected_entries = [entry for entry in original_entries if entry["name"] in LOCKED_SEQUENCE_NAMES]
    selected_names = tuple(entry["name"] for entry in selected_entries)
    if len(selected_entries) != 6 or set(selected_names) != set(LOCKED_SEQUENCE_NAMES):
        raise RuntimeError(f"Restricted official dataset metadata mismatch: {selected_names}")
    if any(not any(entry is original for original in original_entries) for entry in selected_entries):
        raise RuntimeError("Restricted dataset filter did not preserve official dictionary identity")
    dataset.sequence_info_list = selected_entries
    sequence_list = dataset.get_sequence_list()

    bootstrap_record.update(
        {
            "official_metadata_names_in_preserved_order": list(selected_names),
            "official_metadata_dictionary_identity_preserved": True,
            "official_get_sequence_list_unchanged": True,
            "official_construct_sequence_unchanged": True,
            "non_allowlisted_sequence_access": "NONE",
        }
    )

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
            "model_parameter_count": int(sum(parameter.numel() for parameter in tracker.network.parameters())),
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
