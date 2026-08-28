"""Reproduce the authorized F2-A R1 loader check and final import blocker.

This script registers only the two Manager-authorized runtime compatibility
modules. It performs no package installation, model construction, checkpoint
load, forward pass, or scientific outcome write.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import numpy as np
import torch


SOURCE_ROOT = Path(r"E:\Robot_Backup\tmp\stage2B_utptrack_84e0f497")
MODEL_ROOT = SOURCE_ROOT / "UTPTrack-O"
DEPS_ROOT = SOURCE_ROOT / ".characterization_deps"
HOST_SITE_PACKAGES = Path(
    r"C:\Users\nguye\AppData\Local\Programs\Python\Python313\Lib\site-packages"
)
OTB_ROOT = Path(
    r"F:\Q1_TrackingResearch_Data\OTB100_Figshare_24427468_v1\extracted\OTB2015"
)


class ControlledJPEG:
    def __init__(self, path: str) -> None:
        self.path = path

    def decode(self):
        raise RuntimeError("F2A_R1_CONTROLLED_JPEG4PY_UNAVAILABLE")


def register_authorized_runtime_modules() -> None:
    torch_six = types.ModuleType("torch._six")
    torch_six.string_classes = (str,)
    sys.modules["torch._six"] = torch_six

    jpeg4py = types.ModuleType("jpeg4py")
    jpeg4py.JPEG = ControlledJPEG
    sys.modules["jpeg4py"] = jpeg4py


def main() -> None:
    sys.path.insert(0, str(DEPS_ROOT))
    sys.path.append(str(HOST_SITE_PACKAGES))
    import cv2

    register_authorized_runtime_modules()
    sys.path.insert(0, str(MODEL_ROOT))

    from lib.train.data.image_loader import default_image_loader

    frames = [
        OTB_ROOT / "Basketball" / "img" / "0001.jpg",
        OTB_ROOT / "Bolt" / "img" / "0001.jpg",
        OTB_ROOT / "Liquor" / "img" / "0001.jpg",
        OTB_ROOT / "Car4" / "img" / "0001.jpg",
        OTB_ROOT / "Jogging" / "img" / "0001.jpg",
        OTB_ROOT / "Shaking" / "img" / "0001.jpg",
    ]
    default_image_loader.use_jpeg4py = None
    for path in frames:
        official = default_image_loader(str(path))
        direct = cv2.cvtColor(
            cv2.imread(str(path), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB
        )
        assert official.shape == direct.shape
        assert official.dtype == direct.dtype
        assert int(np.max(np.abs(official.astype(np.int16) - direct.astype(np.int16)))) == 0
        assert default_image_loader.use_jpeg4py is False

    from lib.test.tracker.ostrackcmp import OSTrackCMP  # noqa: F401

    raise RuntimeError("unexpected: missing-visdom blocker did not reproduce")


if __name__ == "__main__":
    main()
