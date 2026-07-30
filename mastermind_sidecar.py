#!/usr/bin/env python3
"""Truthful telemetry sidecar for The Tower of Babel.

The sidecar derives counts and readiness from the canonical registry instead of
hard-coded values, so mesh consumers cannot receive stale portfolio claims.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from babel_registry import BABEL_REGISTRY, BabelRegistryEngine  # noqa: E402


def get_telemetry() -> dict[str, object]:
    validation = BabelRegistryEngine(REPO_ROOT).validate_layout()
    integrity_path = REPO_ROOT / ".integrity" / "file_hashes.json"
    watchdog_path = REPO_ROOT / ".integrity" / "watchdog_daemon.py"

    return {
        "schema_version": 2,
        "repo_name": "the-tower-of-babel",
        "status": "OPERATIONAL" if validation["ok"] else "DEGRADED",
        "timestamp": time.time(),
        "integrity_manifest_present": integrity_path.is_file(),
        "watchdog_daemon_present": watchdog_path.is_file(),
        "total_languages": len(BABEL_REGISTRY),
        "total_exhibits": len(BABEL_REGISTRY) * 2,
        "layout_validation": validation,
        "version": "1.1.0",
    }


if __name__ == "__main__":
    print(json.dumps(get_telemetry(), indent=2, sort_keys=True))
