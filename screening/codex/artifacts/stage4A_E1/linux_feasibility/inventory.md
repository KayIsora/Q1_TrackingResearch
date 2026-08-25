# Stage 4A-E1 Linux feasibility inventory

**Probe time:** 2026-08-25T21:55:32+07:00 (2026-08-25T14:55:38Z in WSL)
**Scope:** read-only host, WSL, package-index and resolver probes. No package or environment was installed, no container daemon was started, and SpikeTrack was not executed.

## Local inventory

| Item | Directly observed result |
|---|---|
| WSL application | WSL `2.4.13.0`; default version `2` |
| Installed distributions | `Ubuntu` (WSL 2, running during probe); `docker-desktop` (WSL 2, stopped) |
| Linux distribution | Ubuntu `24.04.3 LTS` (Noble), x86-64 |
| Kernel | `5.15.167.4-microsoft-standard-WSL2` |
| GPU device interface | `/dev/dxg` present; `/usr/lib/wsl/lib/libcuda.so*` present |
| `nvidia-smi` | `/usr/lib/wsl/lib/nvidia-smi`; succeeded |
| Visible GPU | NVIDIA GeForce MX250; compute capability `6.1`; 2,048 MiB total; 1,969 MiB free at probe time |
| Windows NVIDIA driver exposed to WSL | `581.83`; `nvidia-smi` reports driver capability `CUDA Version: 13.0` |
| Python | `/usr/bin/python3` and `/usr/bin/python3.12`; Python `3.12.3` |
| Python 3.10 | no executable found |
| Python 3.11 | no executable found |
| pip | absent; `python3 -m pip` reports `No module named pip` |
| venv | `python3 -m venv --help` succeeds, but `ensurepip` is absent and `python3.12-venv` is not installed |
| Conda/Mamba/Micromamba/uv/virtualenv | none found |
| Linux Torch stack | `torch`, `torchvision`, and `timm` modules absent |
| WSL ext4 storage | 1,081,101,176,832 bytes total; 1,023,219,322,880 bytes available (about 953 GiB) |
| Windows volume underlying the Ubuntu VHDX | Ubuntu `BasePath` is on C:; C: had 64,981,020,672 bytes available (about 60.5 GiB) |
| Mounted Windows E: storage | 206,647,062,528 bytes total; 42,615,635,968 bytes available (about 39.7 GiB) |
| Docker CLI | Windows Docker Desktop client `29.3.1` is visible through `/mnt/c`; no native distro CLI was found |
| Docker daemon | `desktop-linux` context selected, but daemon unavailable; `docker-desktop` distro stopped |
| Future recipe command prerequisites | `/usr/bin/git` 2.43.0, `/usr/bin/curl` 8.5.0, `/usr/bin/sha256sum`, and `/usr/bin/sudo` 1.9.15p5 are present |

The `CUDA Version: 13.0` line above is a driver-capability report, not evidence that a CUDA 13.0 or CUDA 11.8 toolkit/runtime is installed in Ubuntu. No Linux CUDA toolkit was found or installed. The planned PyTorch `+cu118` wheel would supply its CUDA 11.8 user-space runtime after authorization.

## Read-only resolver results

- Ubuntu Noble's configured package sources do not provide a complete Python 3.10 or 3.11 venv path: `apt-get -s install python3.10 python3.10-venv` fails on `python3.10-venv`, and the Python 3.11 simulation cannot locate either `python3.11` or `python3.11-venv`.
- Conda-forge metadata exposes four Linux x86-64 builds of Python `3.11.7`, including the 30,830,615-byte non-debug `hab00c5b_1` build. Pinning `python=3.11.7` therefore matches the already characterized Windows interpreter rather than leaving the future Linux patch version floating.
- `apt-get -s install python3.12-venv python3-pip` resolves, but that would not solve the pinned wheel contract.
- The official PyTorch CUDA 11.8 indexes expose exact Linux x86-64 wheels for `torch==2.0.0+cu118` and `torchvision==0.15.1+cu118` for CPython 3.10 and 3.11.
- Those official indexes expose no CPython 3.12 Linux x86-64 wheels for either pinned version. PyPI's `timm==0.5.4` wheel is `py3-none-any` and declares Python `>=3.6`, but timm compatibility alone cannot make the pinned Torch/Torchvision pair installable on Python 3.12.
- The pinned evaluator imports `jpeg4py` unconditionally in `lib/train/data/image_loader.py`. The existing Windows run uses `jpeg4py==0.1.4`; Ubuntu Noble offers its required TurboJPEG runtime as package `libturbojpeg` (not `libturbojpeg0`). `apt-get -s install libturbojpeg` resolves one 192,082-byte package and performs no installation.
- The exact three-sequence path also imports `lmdb` unconditionally through `lib/test/evaluation/tracker.py:9 -> lib/utils/lmdb_utils.py:1`, even when OTB frames are ordinary image paths. It imports Matplotlib unconditionally in `lib/test/tracker/spiketrack_inf.py:18` and `lib/models/spiketrack/fuc.py:6`, even with tracker debug output disabled. The proven Windows environment pins these packages to `lmdb==1.7.3` and `matplotlib==3.11.1`.
- Direct index/tag inspection and `pip index versions` tag filtering were used instead of `pip install --dry-run`, because the latter had previously begun transferring the 2.267-GB Torch wheel. No wheel payload was downloaded in E1.

## Exact-path static import audit

A read-only AST closure was built from `tracking/test.py`, the dynamically selected OTB dataset, `lib.test.tracker.spiketrack_inf`, `lib.test.parameter.spiketrack`, and the inference model module. Parent-package initializers were included because Python executes them before their submodules. The closure contains 47 local modules.

The non-standard import roots in that closure are:

`torch`, `torchvision`, `timm`, `numpy`, `cv2`, `PIL`, `yaml`, `easydict`, `pandas`, `jpeg4py`, `lmdb`, `matplotlib`, and the `tensorboardX` fallback.

The future package list now covers every root. Two easily missed import-time edges are retained explicitly:

- importing `lib.train.data.image_loader` first executes `lib.train.__init__` and `lib.train.admin.__init__`; `lib/train/admin/tensorboard.py` attempts `torch.utils.tensorboard` and falls back to `tensorboardX`, which is present in the proven environment;
- the OTB loader requests NumPy parsing, but `lib/test/utils/load_text.py` still imports pandas at module import time.

This is a static import-availability audit, not a Linux execution result. The future recipe includes an import-only source-closure check before any authorized tracker run.

Primary metadata sources, accessed 2026-08-25:

- PyTorch CUDA 11.8 Torch index: <https://download.pytorch.org/whl/cu118/torch/>
- PyTorch CUDA 11.8 Torchvision index: <https://download.pytorch.org/whl/cu118/torchvision/>
- PyTorch CUDA 11.8 Torchaudio index: <https://download.pytorch.org/whl/cu118/torchaudio/>
- timm 0.5.4 PyPI metadata: <https://pypi.org/pypi/timm/0.5.4/json>
- jpeg4py 0.1.4 PyPI metadata: <https://pypi.org/pypi/jpeg4py/0.1.4/json>
- lmdb 1.7.3 PyPI metadata: <https://pypi.org/pypi/lmdb/1.7.3/json>
- Matplotlib 3.11.1 PyPI metadata: <https://pypi.org/pypi/matplotlib/3.11.1/json>
- Miniforge release metadata: <https://github.com/conda-forge/miniforge/releases/tag/26.5.3-0>
- Conda-forge Python package metadata: <https://api.anaconda.org/package/conda-forge/python>
- Pinned SpikeTrack `install.sh`, commit `1537db51a1cc9f6e30cce469fba3e51f5721b3d0` (local inspected source)

## Resource estimate

The directly inspected CPython 3.11 payloads total at least 2,443,752,225 bytes (about 2.276 GiB): Miniforge, the selected Python 3.11.7 conda package, Torch, Torchvision, optional official-script Torchaudio, timm, jpeg4py, LMDB, Matplotlib and Ubuntu's TurboJPEG runtime. This excludes remaining conda packages, pip transitive dependencies and index/cache overhead.

**PROJECT PLANNING ESTIMATE:** budget 2.6-3.1 GiB of transfer and 7-10 GiB of WSL ext4 storage for a clean environment, caches and bounded outputs. The ext4 logical filesystem and its underlying C: volume both had enough measured free space for that budget. At ordinary broadband speed, budget 30-90 minutes for download, environment creation and import/GPU validation; the three-sequence tracker runtime is intentionally `UNKNOWN` until E3, because no WSL tracker run was permitted or measured in E1.

## GPU limitations and feasibility decision

**FACT — measured:** the only WSL-visible GPU is the same 2-GiB MX250. WSL GPU forwarding works at the device/driver level, but no compatible Python/Torch stack exists in the distro. Docker cannot currently substitute for that stack because its daemon is stopped.

**INTERPRETATION — reasoned:** the available CPython 3.11 CUDA 11.8 wheels, visible GPU and ample WSL ext4 space make a bounded setup technically plausible on existing hardware. The 2-GiB VRAM ceiling leaves little margin, and successful import, CUDA allocation and SpikeTrack inference remain untested under WSL. No speed or Jetson claim is made.

**Linux comparison feasibility: `LINUX_RUN_FEASIBLE_BUT_SETUP_REQUIRED`.**
