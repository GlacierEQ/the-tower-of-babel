"""Honest per-floor toolchain execution with exact blockers."""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

from .registry import REPO_ROOT, TowerRegistry, load_registry


def _available(binary: str) -> bool:
    return shutil.which(binary) is not None


def _run(argv: list[str], timeout_s: int = 120) -> dict[str, Any]:
    start = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            timeout=timeout_s,
            check=False,
        )
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-4000:],
            "stderr": completed.stderr[-4000:],
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "timeout": True,
        }


def build_floor(tech: dict[str, Any]) -> dict[str, Any]:
    tech_id = tech["id"]
    tool = tech["toolchain"]["tool"]
    gate = tech["execution"].get("hardware_gate", "")
    tier = tech["execution"].get("ci_tier", "portable")
    missing_modules = [
        module for module in tech["toolchain"].get("python_modules", [])
        if importlib.util.find_spec(module) is None
    ]
    if missing_modules:
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_DEPENDENCY",
            "blocker": "Required Python module(s) not found: " + ", ".join(missing_modules),
            "tool": tool,
            "reference_pin": tech["toolchain"]["reference_pin"],
            "commands": [],
        }
    if gate and os.environ.get(f"TOWER_ENABLE_{tech_id.upper().replace('-', '_')}") != "1":
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_HARDWARE",
            "blocker": gate,
            "tool": tool,
            "reference_pin": tech["toolchain"]["reference_pin"],
            "commands": [],
        }
    if not _available(tool):
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_TOOLCHAIN",
            "blocker": f"Required executable not found: {tool}",
            "tool": tool,
            "reference_pin": tech["toolchain"]["reference_pin"],
            "commands": [],
        }

    (REPO_ROOT / "build").mkdir(exist_ok=True)
    commands = []
    for argv in tech["toolchain"].get("build", []) + tech["toolchain"].get("test", []):
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) for part in argv):
            return {
                "technology_id": tech_id,
                "status": "INVALID_MANIFEST",
                "blocker": "Build/test commands must be non-empty argv lists.",
                "commands": commands,
            }
        result = _run(argv)
        commands.append(result)
        if result.get("returncode") != 0:
            return {
                "technology_id": tech_id,
                "status": "FAILED",
                "blocker": "Command failed or timed out.",
                "commands": commands,
            }
    return {
        "technology_id": tech_id,
        "status": "VERIFIED",
        "tool": tool,
        "reference_pin": tech["toolchain"]["reference_pin"],
        "ci_tier": tier,
        "commands": commands,
    }


def build_many(
    registry: TowerRegistry,
    technology_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    selected = set(technology_ids or [])
    rows = [
        build_floor(tech)
        for tech in registry.technologies
        if not selected or tech["id"] in selected
    ]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {"tower_id": registry.payload["tower_id"], "results": rows, "counts": dict(sorted(counts.items()))}


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
