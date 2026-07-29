"""Measured, non-promotional cross-language benchmark runner."""
from __future__ import annotations

import json
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

from .build import build_floor
from .registry import REPO_ROOT, TowerRegistry


def _measure(argv: list[str], iterations: int) -> dict[str, Any]:
    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        completed = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=120,
            check=False,
        )
        elapsed = (time.perf_counter() - start) * 1000
        if completed.returncode != 0:
            return {
                "status": "FAILED",
                "argv": argv,
                "returncode": completed.returncode,
                "stderr": completed.stderr[-2000:],
            }
        samples.append(elapsed)
    return {
        "status": "MEASURED",
        "argv": argv,
        "iterations": iterations,
        "median_ms": round(statistics.median(samples), 3),
        "min_ms": round(min(samples), 3),
        "max_ms": round(max(samples), 3),
        "samples_ms": [round(value, 3) for value in samples],
    }


def benchmark_many(
    registry: TowerRegistry,
    technology_ids: Iterable[str],
    *,
    iterations: int = 3,
) -> dict[str, Any]:
    requested = set(technology_ids)
    results = []
    for tech in registry.technologies:
        if tech["id"] not in requested:
            continue
        build = build_floor(tech)
        row: dict[str, Any] = {
            "technology_id": tech["id"],
            "build_status": build["status"],
            "evidence_state": tech["evidence_state"],
            "proof_class": tech["proof_class"],
        }
        if build["status"] != "VERIFIED":
            row["status"] = build["status"]
            row["blocker"] = build.get("blocker", "")
        else:
            tests = tech["toolchain"].get("test", [])
            if not tests:
                row["status"] = "NO_RUNTIME_BENCHMARK"
            else:
                row["measurement"] = _measure(tests[-1], iterations)
                row["status"] = row["measurement"]["status"]
        results.append(row)
    return {
        "benchmark_id": "tower-portable-benchmark-v1",
        "iterations": iterations,
        "results": results,
        "truth_note": "Measurements are local process timings for the declared exhibit commands, not universal language rankings.",
    }


def write_benchmark(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
