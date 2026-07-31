#!/usr/bin/env python3
"""One-time canonical rename, generator patch, and staging cleanup."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPLACEMENTS = {
    "languages/swift/advanced_metal_ane_engine.swift": "languages/swift/advanced_metal_compute_engine.swift",
    "languages/cuda/advanced_flash_attn_kernel.cu": "languages/cuda/advanced_reference_attention.cu",
    "languages/mojo/advanced_tpu_tensor_kernel.mojo": "languages/mojo/advanced_simd_tensor_kernel.mojo",
    "languages/verilog/advanced_systolic_matmul.v": "languages/verilog/advanced_weight_stationary_dot_array.v",
    "systolic_matmul": "weight_stationary_dot_array",
}

for relative in (
    "registry/tower.d/orchestration-runtime.json",
    "registry/tower.d/compute-graphs.json",
    "registry/tower.d/contracts-hardware.json",
):
    path = ROOT / relative
    payload = json.loads(path.read_text(encoding="utf-8"))

    def replace(value):
        if isinstance(value, str):
            return REPLACEMENTS.get(value, value)
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        return value

    path.write_text(
        json.dumps(replace(payload), separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )

for obsolete in (
    "languages/swift/advanced_metal_ane_engine.swift",
    "languages/cuda/advanced_flash_attn_kernel.cu",
    "languages/mojo/advanced_tpu_tensor_kernel.mojo",
    "languages/verilog/advanced_systolic_matmul.v",
):
    path = ROOT / obsolete
    if path.exists():
        path.unlink()

staging = ROOT / "tools/promotion_parts"
if staging.exists():
    shutil.rmtree(staging)

generator = ROOT / "src/tower/generate.py"
source = generator.read_text(encoding="utf-8")
needle = "## The thirty-floor map\n\nThe matrix is generated from the canonical registry."
replacement = """## Advanced Exhibit Atlas

The easy exhibit teaches the technology. The advanced exhibit must own a real engineering boundary, expose failure behavior, and terminate in proof or an exact blocker. [`ADVANCED_EXHIBITS.md`](ADVANCED_EXHIBITS.md) publishes the signature engineering move and claim boundary for all {count} floors; [`quality/advanced_exhibit_atlas.json`](quality/advanced_exhibit_atlas.json) provides the same map to agents and automation.

## The thirty-floor map

The matrix is generated from the canonical registry."""
if "## Advanced Exhibit Atlas" not in source:
    if needle not in source:
        raise RuntimeError("README generator insertion point not found")
    source = source.replace(needle, replacement)
    generator.write_text(source, encoding="utf-8")
