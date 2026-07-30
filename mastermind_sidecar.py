#!/usr/bin/env python3
"""Mastermind Sidecar Daemon for the-tower-of-babel repo.

The sidecar is now a consumer of the canonical Tower registry. It reports
OPERATIONAL only when registry validation and integrity verification both pass.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from tower_registry import TowerRegistry, verify_integrity


def get_telemetry() -> dict:
    registry = TowerRegistry(REPO_ROOT)
    validation = registry.validate(require_files=True)
    integrity = verify_integrity(REPO_ROOT)
    operational = validation.ok and integrity["ok"]
    return {
        "repo_name": "the-tower-of-babel",
        "status": "OPERATIONAL" if operational else "DEGRADED",
        "timestamp": time.time(),
        "source_of_truth": "registry/tower.yml",
        "registry_valid": validation.ok,
        "integrity_valid": integrity["ok"],
        "validation_errors": validation.errors,
        "validation_warnings": validation.warnings,
        "integrity": integrity,
        "total_technologies": registry.actual_count,
        "total_exhibits": registry.total_exhibits,
        "version": "1.1.0-p0-truth-convergence",
    }


if __name__ == "__main__":
    print(json.dumps(get_telemetry(), indent=2, sort_keys=True))
