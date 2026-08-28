#!/usr/bin/env python3
"""Run the unchanged F2-B scientific execution after the R1 preflight passes."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


r1 = load_module("f2b_mcitrack_r1_runtime", SCRIPT_DIR / "2026-08-29_F2B_MCITrack_R1_runtime.py")
execute = load_module("f2b_mcitrack_base_execute", SCRIPT_DIR / "2026-08-29_F2B_MCITrack_execute.py")
execute.rt = r1


if __name__ == "__main__":
    sys.exit(execute.main())
