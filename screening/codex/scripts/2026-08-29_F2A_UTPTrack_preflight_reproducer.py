"""Reproduce the F2-A pre-outcome official-tracker import blocker.

This script performs provenance/hash checks and the one authorized runtime-only
compatibility repair. It deliberately stops at the second import failure and
does not construct the tracker, load the checkpoint, run a model forward, or
write a scientific outcome row.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import types
from pathlib import Path


SOURCE_ROOT = Path(r"E:\Robot_Backup\tmp\stage2B_utptrack_84e0f497")
MODEL_ROOT = SOURCE_ROOT / "UTPTrack-O"
DEPS_ROOT = SOURCE_ROOT / ".characterization_deps"
HOST_SITE_PACKAGES = Path(
    r"C:\Users\nguye\AppData\Local\Programs\Python\Python313\Lib\site-packages"
)
CHECKPOINT = (
    SOURCE_ROOT
    / ".characterization_artifacts"
    / "UTPTrack-O-224"
    / "OSTrackCMP_ep0300.pth.tar"
)
EXPECTED_SOURCE_SHA = "84e0f49711254a44f5308faaa9a2405db1964dd7"
EXPECTED_CHECKPOINT_SHA256 = (
    "E4EE630CD0E88E41CDBC55BD727C16CA5A4BE3756ADED65F2506B8F670ED0FEF"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main() -> None:
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=SOURCE_ROOT, text=True
    ).strip()
    if source_sha != EXPECTED_SOURCE_SHA:
        raise RuntimeError(f"source SHA mismatch: {source_sha}")
    checkpoint_sha = sha256(CHECKPOINT)
    if checkpoint_sha != EXPECTED_CHECKPOINT_SHA256:
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {checkpoint_sha}")

    sys.path.insert(0, str(DEPS_ROOT))
    import torch  # noqa: F401  # Load the sealed CUDA runtime first.

    sys.path.append(str(HOST_SITE_PACKAGES))
    import cv2  # noqa: F401  # Existing host module; no installation/download.

    shim = types.ModuleType("torch._six")
    shim.string_classes = (str,)
    sys.modules["torch._six"] = shim

    sys.path.insert(0, str(MODEL_ROOT))
    from lib.test.tracker.ostrackcmp import OSTrackCMP  # noqa: F401

    raise RuntimeError("unexpected: official tracker import did not reproduce blocker")


if __name__ == "__main__":
    main()
