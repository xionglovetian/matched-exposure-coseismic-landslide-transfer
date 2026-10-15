#!/bin/bash
# Reference environment for the revision-phase E3 runs (Linux/CUDA cloud host).
# The experiments were also reproduced on the local Windows workstation with the
# versions pinned in environment-full.txt.
set -e
VENV=${VENV:-/root/autodl-tmp/landslide-env}
PIP=$VENV/bin/pip
export PIP_INDEX_URL=${PIP_INDEX_URL:-https://pypi.org/simple}
echo "=== upgrade pip ==="
$PIP install -q -U pip setuptools wheel 2>&1 | tail -2
echo "=== torch ==="
$PIP install torch==2.14.0+cu126 torchvision==0.29.0+cu126 --index-url https://download.pytorch.org/whl/cu126 2>&1 | tail -6
echo "=== rest ==="
$PIP install numpy==2.2.6 timm==1.0.29 albumentations==1.3.1 segmentation-models-pytorch==0.5.0 \
  opencv-python==5.0.0.93 opencv-python-headless==5.0.0.93 scikit-image==0.25.2 scipy==1.15.3 \
  pandas==2.3.3 matplotlib==3.10.9 pillow==12.3.0 einops==0.8.2 rasterio==1.4.4 tqdm==4.70.1 2>&1 | tail -6
echo INSTALL_DONE
