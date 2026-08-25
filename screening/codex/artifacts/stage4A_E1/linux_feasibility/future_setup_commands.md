# Future Stage 4A-E3 Linux setup commands — not executed

These commands are an authorization package, not a record of actions taken. They target the existing Ubuntu WSL2 distribution, its visible MX250, CPython 3.11, and the pinned CUDA 11.8 package pair. They intentionally place the environment on WSL ext4 under `/home/kay`, where about 953 GiB was free during E1.

## 1. Install the minimum system runtime prerequisite

```bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y libturbojpeg
```

Ubuntu 24.04 names this package `libturbojpeg`; the `libturbojpeg0` name does not resolve in the configured Noble repositories. This shared library is required by `jpeg4py`, which the pinned evaluator imports unconditionally.

## 2. Install a pinned isolated Python distribution

```bash
set -euo pipefail
mkdir -p /home/kay/stage4A_E3_setup
cd /home/kay/stage4A_E3_setup

curl -fL --retry 3 \
  -o Miniforge3-26.5.3-0-Linux-x86_64.sh \
  https://github.com/conda-forge/miniforge/releases/download/26.5.3-0/Miniforge3-26.5.3-0-Linux-x86_64.sh

printf '%s  %s\n' \
  '14db468222ad564658656f769506056209b6dc375f5e7dfd31eb5ebbf08fa529' \
  'Miniforge3-26.5.3-0-Linux-x86_64.sh' | sha256sum -c -

bash Miniforge3-26.5.3-0-Linux-x86_64.sh \
  -b -p /home/kay/miniforge3-stage4A-E3

source /home/kay/miniforge3-stage4A-E3/etc/profile.d/conda.sh
conda create -y -n spiketrack-e3 'python=3.11.7' pip
conda activate spiketrack-e3
python --version
python -m pip --version
```

## 3. Install the pinned core stack and bounded-run dependencies

```bash
python -m pip install --no-cache-dir \
  'torch==2.0.0+cu118' \
  'torchvision==0.15.1+cu118' \
  'torchaudio==2.0.1+cu118' \
  --index-url https://download.pytorch.org/whl/cu118

python -m pip install --no-cache-dir \
  'numpy==1.26.4' \
  'opencv-python-headless==4.11.0.86' \
  'PyYAML==6.0.3' \
  'easydict==1.13' \
  'jpeg4py==0.1.4' \
  'lmdb==1.7.3' \
  'matplotlib==3.11.1' \
  'pandas==2.2.3' \
  'pillow==12.3.0' \
  'requests==2.28.1' \
  'tensorboardX==2.6.4' \
  'timm==0.5.4' \
  'tqdm==4.67.1' \
  'yacs==0.1.8'
```

The second command mirrors the bounded Windows runner's proven package versions rather than blindly executing every unpinned optional package in the official `install.sh`. `jpeg4py`, `lmdb`, and Matplotlib are included because the exact official path imports them unconditionally; that import requirement is independent of whether OTB frames come from LMDB or whether debug plots are enabled. This remains a characterization environment, not a claim about the authors' original environment.

## 4. Validate before any authorized tracker run

```bash
export MPLBACKEND=Agg

/usr/lib/wsl/lib/nvidia-smi \
  --query-gpu=name,driver_version,memory.total,memory.free,compute_cap \
  --format=csv,noheader

python - <<'PY'
import torch
import torchvision
import timm
import jpeg4py
import lmdb
import matplotlib

assert torch.__version__ == '2.0.0+cu118', torch.__version__
assert torchvision.__version__ == '0.15.1+cu118', torchvision.__version__
assert timm.__version__ == '0.5.4', timm.__version__
assert lmdb.__version__ == '1.7.3', lmdb.__version__
assert matplotlib.__version__ == '3.11.1', matplotlib.__version__
assert torch.version.cuda == '11.8', torch.version.cuda
assert torch.cuda.is_available(), 'CUDA is not visible to PyTorch'
assert torch.cuda.get_device_name(0) == 'NVIDIA GeForce MX250'
print({
    'python_torch': torch.__version__,
    'torchvision': torchvision.__version__,
    'timm': timm.__version__,
    'torch_cuda_build': torch.version.cuda,
    'cudnn': torch.backends.cudnn.version(),
    'gpu': torch.cuda.get_device_name(0),
    'gpu_memory_bytes': torch.cuda.get_device_properties(0).total_memory,
})
PY

cd /mnt/e/Robot_Backup/tmp/stage4A_R_official_source
test "$(git rev-parse HEAD)" = \
  '1537db51a1cc9f6e30cce469fba3e51f5721b3d0'

PYTHONPATH=/mnt/e/Robot_Backup/tmp/stage4A_R_official_source \
MPLBACKEND=Agg \
python - <<'PY'
import importlib

modules = (
    'lib.test.evaluation.tracker',
    'lib.test.evaluation.otbdataset',
    'lib.test.parameter.spiketrack',
    'lib.test.tracker.spiketrack_inf',
)
for name in modules:
    importlib.import_module(name)
    print('IMPORT_OK', name)
PY
```

Stop here if the import/CUDA assertions fail or if the GPU cannot allocate the model. Do not change the model to force a run. Only after separate E3 authorization should the exact pinned source, S256-T1 checkpoint and the same three predeclared sequences be run through the official evaluator.

## Planning cost

- Directly inspected payload floor: about 2.276 GiB including Miniforge, Python 3.11.7, Torch, Torchvision, Torchaudio, timm, jpeg4py, LMDB, Matplotlib and Ubuntu's TurboJPEG runtime.
- Transfer budget including remaining Python packages and overhead: 2.6-3.1 GiB.
- WSL ext4 storage budget including installation, package caches and bounded outputs: 7-10 GiB.
- Setup and validation planning time: 30-90 minutes on ordinary broadband; tracker runtime remains `UNKNOWN` pending E3 measurement.
