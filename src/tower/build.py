"""Honest per-floor toolchain execution with exact blockers."""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Iterable

from .registry import REPO_ROOT, TowerRegistry


def _available(binary: str) -> bool:
    return shutil.which(binary) is not None


def _run(argv: list[str], timeout_s: int = 120) -> dict[str, Any]:
    """Run an argv-only command and return bounded evidence without throwing."""
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
    except OSError as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": "",
            "stderr": str(exc),
            "duration_ms": round((time.monotonic() - start) * 1000, 3),
            "spawn_error": True,
        }


def _invalid(technology_id: str, blocker: str, commands: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "technology_id": technology_id,
        "status": "INVALID_MANIFEST",
        "blocker": blocker,
        "commands": commands or [],
    }


def _tool_version(tool: str) -> str:
    """Capture a best-effort observed tool version without making it authoritative."""
    for suffix in (["--version"], ["version"], ["-version"]):
        result = _run([tool, *suffix], timeout_s=15)
        if result.get("returncode") == 0:
            text = (result.get("stdout") or result.get("stderr") or "").strip()
            if text:
                return text.splitlines()[0][:300]
    return "UNAVAILABLE"


def build_floor(tech: dict[str, Any]) -> dict[str, Any]:
    """Execute one validated floor, failing closed on incomplete contracts."""
    if not isinstance(tech, dict):
        return _invalid("UNKNOWN", "Technology record must be an object.")
    tech_id = tech.get("id")
    if not isinstance(tech_id, str) or not tech_id.strip():
        return _invalid("UNKNOWN", "Technology id must be a non-empty string.")
    toolchain = tech.get("toolchain")
    execution = tech.get("execution")
    if not isinstance(toolchain, dict):
        return _invalid(tech_id, "toolchain must be an object.")
    if not isinstance(execution, dict):
        return _invalid(tech_id, "execution must be an object.")
    tool = toolchain.get("tool")
    reference_pin = toolchain.get("reference_pin")
    if not isinstance(tool, str) or not tool or not isinstance(reference_pin, str) or not reference_pin:
        return _invalid(tech_id, "toolchain requires string tool and reference_pin.")

    gate = execution.get("hardware_gate", "")
    tier = execution.get("ci_tier", "portable")
    if not isinstance(gate, str) or not isinstance(tier, str):
        return _invalid(tech_id, "execution gate and ci_tier must be strings.")
    python_modules = toolchain.get("python_modules", [])
    if not isinstance(python_modules, list) or not all(isinstance(module, str) and module for module in python_modules):
        return _invalid(tech_id, "python_modules must be a list of module names.")
    missing_modules = [
        module for module in python_modules if importlib.util.find_spec(module) is None
    ]
    if missing_modules:
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_DEPENDENCY",
            "blocker": "Required Python module(s) not found: " + ", ".join(missing_modules),
            "tool": tool,
            "reference_pin": reference_pin,
            "commands": [],
        }

    gate_key = re.sub(r"[^A-Z0-9]+", "_", tech_id.upper()).strip("_")
    if gate and os.environ.get(f"TOWER_ENABLE_{gate_key}") != "1":
        status = "BLOCKED_DEPENDENCY" if tier in {"service", "specialized"} and "service" in gate.casefold() else "BLOCKED_HARDWARE"
        return {
            "technology_id": tech_id,
            "status": status,
            "blocker": gate,
            "tool": tool,
            "reference_pin": reference_pin,
            "commands": [],
        }
    if not _available(tool):
        return {
            "technology_id": tech_id,
            "status": "BLOCKED_TOOLCHAIN",
            "blocker": f"Required executable not found: {tool}",
            "tool": tool,
            "reference_pin": reference_pin,
            "commands": [],
        }

    build_commands = toolchain.get("build", [])
    test_commands = toolchain.get("test", [])
    if not isinstance(build_commands, list) or not isinstance(test_commands, list):
        return _invalid(tech_id, "Build and test contracts must be lists.")
    declared_commands = build_commands + test_commands
    if not declared_commands:
        return _invalid(tech_id, "At least one build or test command is required for VERIFIED status.")

    (REPO_ROOT / "build").mkdir(exist_ok=True)
    commands: list[dict[str, Any]] = []
    for argv in declared_commands:
        if not isinstance(argv, list) or not argv or not all(isinstance(part, str) and part for part in argv):
            return _invalid(tech_id, "Build/test commands must be non-empty argv string lists.", commands)
        result = _run(argv)
        commands.append(result)
        if result.get("spawn_error"):
            return {
                "technology_id": tech_id,
                "status": "BLOCKED_TOOLCHAIN",
                "blocker": f"Command executable could not be started: {argv[0]}: {result.get('stderr', '')}",
                "tool": tool,
                "reference_pin": reference_pin,
                "commands": commands,
            }
        if result.get("returncode") != 0:
            return {
                "technology_id": tech_id,
                "status": "FAILED",
                "blocker": "Command failed or timed out.",
                "tool": tool,
                "reference_pin": reference_pin,
                "commands": commands,
            }
    return {
        "technology_id": tech_id,
        "status": "VERIFIED",
        "tool": tool,
        "reference_pin": reference_pin,
        "observed_tool_version": _tool_version(tool),
        "ci_tier": tier,
        "commands": commands,
    }


def build_many(
    registry: TowerRegistry,
    technology_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Build requested floors and represent every unknown request as an error row."""
    requested = list(technology_ids or [])
    selected = {value.casefold() for value in requested}
    known = {
        tech.get("id", "").casefold(): tech
        for tech in registry.technologies
        if isinstance(tech, dict) and isinstance(tech.get("id"), str)
    }
    rows = [
        build_floor(tech)
        for key, tech in known.items()
        if not selected or key in selected
    ]
    unknown = sorted({value for value in requested if value.casefold() not in known})
    rows.extend(_invalid(value, f"Unknown technology requested: {value}") for value in unknown)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "tower_id": registry.payload.get("tower_id", "UNKNOWN"),
        "requested_technology_ids": requested,
        "results": rows,
        "counts": dict(sorted(counts.items())),
    }


def write_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
