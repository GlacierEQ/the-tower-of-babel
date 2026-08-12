#!/usr/bin/env python3
"""Run the Tower's repository-local operational readiness gate.

This command is intentionally read-only.  It does not repair drift, grant authority,
or promote state.  It reports the exact condition of the canonical registry,
generated projections, immutable integrity ledger, and machine trust boundary and
returns non-zero whenever any required local invariant is false.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tower.generate import generate
from tower.integrity import verify_integrity
from tower.registry import load_registry, validate_registry
from tower.trust import build_machine_trust_report


def _registry_report() -> dict[str, Any]:
    try:
        registry = load_registry()
    except ValueError as exc:
        return {
            "ok": False,
            "technology_count": 0,
            "errors": [str(exc)],
        }
    errors = validate_registry(registry)
    return {
        "ok": not errors,
        "technology_count": len(registry.technologies),
        "errors": errors,
    }


def _generation_report() -> dict[str, Any]:
    try:
        drift = generate(check=True)
    except (OSError, ValueError) as exc:
        return {"ok": False, "drift": [], "errors": [str(exc)]}
    return {
        "ok": not drift,
        "drift": list(drift),
        "errors": [],
    }


def build_operational_report() -> dict[str, Any]:
    """Build one deterministic, machine-readable readiness report."""
    registry = _registry_report()
    generated = _generation_report()
    integrity = verify_integrity()
    trust = build_machine_trust_report(ROOT)

    checks = {
        "canonical_registry": registry,
        "generated_surfaces": generated,
        "integrity": integrity,
        "machine_trust": trust,
    }
    ok = all(check.get("ok") is True for check in checks.values())
    return {
        "schema": "glaciereq.tower-operational-readiness.v1",
        "repository": "GlacierEQ/the-tower-of-babel",
        "mode": "read_only_fail_closed",
        "ok": ok,
        "checks": checks,
    }


def main() -> int:
    report = build_operational_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
