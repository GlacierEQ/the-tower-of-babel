"""Reference test for the host-side CUDA attention simulation; it does not prove GPU execution."""

from __future__ import annotations

import subprocess
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_cuda_flash_attention_kernel_compiles_and_runs():
    cu_file = (
        REPO_ROOT / "languages" / "cuda" / "advanced_nvidia_flash_attention_kernel.cu"
    )
    out_bin = REPO_ROOT / "build" / "test_cuda_kernel"
    out_bin.parent.mkdir(exist_ok=True)

    cmd_compile = ["g++", "-O2", "-x", "c++", str(cu_file), "-o", str(out_bin)]
    subprocess.run(cmd_compile, check=True)

    res = subprocess.run([str(out_bin)], check=True, capture_output=True, text=True)
    report = json.loads(res.stdout)

    assert report["status"] == "REFERENCE_ONLY"
    assert report["flagship_tier"] == "HOST_REFERENCE_ATTENTION_TILE"
    assert report["cuda_arch"]["compute_capability"] == "sm_90a (Hopper/Blackwell)"
    assert report["kernel_metrics"]["online_softmax_status"] == "REFERENCE_STABLE"

    if out_bin.exists():
        out_bin.unlink()
