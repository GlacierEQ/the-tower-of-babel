#!/usr/bin/env python3
"""Tower of Babel operational health probe and runtime diagnostic observer.

Validates the nervous system contract, registry integrity, evidence promotion
status, spiral engine capability, and mastermind sidecar telemetry.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from mastermind_sidecar import get_telemetry
from tower.capability_resolution import (
    LanguageLane,
    resolve_lanes,
)
from tower.integrity import verify_integrity
from tower.registry import load_registry, validate_registry


def observe_runtime(verbose: bool = False) -> dict[str, Any]:
    """Perform deterministic operational observation of Tower subsystems."""
    start_time = time.time()
    observations: dict[str, Any] = {
        "timestamp": start_time,
        "repo_name": "the-tower-of-babel",
        "subsystems": {},
    }

    # 1. Registry verification
    try:
        registry = load_registry()
        reg_errors = validate_registry(registry)
        observations["subsystems"]["registry"] = {
            "status": "PASS" if not reg_errors else "FAIL",
            "technology_count": len(registry.technologies),
            "errors": reg_errors,
        }
    except Exception as exc:  # pylint: disable=broad-except
        observations["subsystems"]["registry"] = {
            "status": "ERROR",
            "error": str(exc),
        }

    # 2. Sidecar telemetry
    try:
        telemetry = get_telemetry()
        observations["subsystems"]["sidecar"] = {
            "status": "PASS" if telemetry.get("status") in {"OPERATIONAL", "DEGRADED"} else "FAIL",
            "telemetry_status": telemetry.get("status"),
            "total_technologies": telemetry.get("total_technologies"),
            "total_exhibits": telemetry.get("total_exhibits"),
            "evidence_states": telemetry.get("evidence_states"),
        }
    except Exception as exc:
        observations["subsystems"]["sidecar"] = {
            "status": "ERROR",
            "error": str(exc),
        }

    # 3. Live integrity verification
    try:
        integrity_res = verify_integrity()
        observations["subsystems"]["integrity"] = {
            "status": "PASS" if integrity_res.get("status") in {"VERIFIED", "DRIFT"} else "FAIL",
            "integrity_mode": integrity_res.get("mode"),
            "integrity_status": integrity_res.get("status"),
            "tracked_file_count": integrity_res.get("tracked_file_count"),
        }
    except Exception as exc:
        observations["subsystems"]["integrity"] = {
            "status": "ERROR",
            "error": str(exc),
        }

    # 4. Capability resolution sanity
    try:
        sample_lane = LanguageLane(
            lane_id="sample-python-orchestration",
            concern="distributed task coordination",
            language="python",
            rationale="Robust async event loop and extensive ecosystem for distributed orchestration",
            interface="asyncio/protobuf",
            proof="languages/python/advanced_async_orchestrator.py",
        )
        sample_obs = sample_lane.observations()
        resolution = resolve_lanes([sample_lane])
        observations["subsystems"]["capability_resolution"] = {
            "status": "PASS" if not sample_obs and resolution else "FAIL",
            "observations": list(sample_obs),
            "resolved_count": len(resolution),
        }
    except Exception as exc:
        observations["subsystems"]["capability_resolution"] = {
            "status": "ERROR",
            "error": str(exc),
        }

    duration = time.time() - start_time
    observations["duration_ms"] = round(duration * 1000, 2)

    # Overall operational health
    all_pass = all(
        sub.get("status") == "PASS"
        for sub in observations["subsystems"].values()
    )
    observations["status"] = "OPERATIONAL" if all_pass else "DEGRADED"
    return observations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Observe Tower operational health and subsystem readiness."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if degraded or failing")
    parser.add_argument("--verbose", action="store_true", help="Include detailed subsystem diagnostic logs")
    args = parser.parse_args()

    result = observe_runtime(verbose=args.verbose)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Tower Operational Status: {result['status']} ({result['duration_ms']} ms)")
        for name, sub in result["subsystems"].items():
            print(f"  - {name}: {sub.get('status')}")
            if args.verbose or sub.get("status") != "PASS":
                for k, v in sub.items():
                    if k != "status":
                        print(f"      {k}: {v}")

    if args.check and result["status"] != "OPERATIONAL":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())