#!/usr/bin/env python3
"""Run the Tower's repository-local operational readiness gate.

This command is intentionally read-only. It does not repair drift, grant authority,
or promote state. It reports the exact condition of the canonical registry,
generated projections, immutable integrity ledger, and machine trust boundary and
returns non-zero whenever any required local invariant is false.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tower.generate import generate
from tower.integrity import verify_integrity
from tower.registry import load_registry, validate_registry
from tower.trust import build_machine_trust_report


def _exception_report(exc: Exception) -> dict[str, Any]:
    return {
        "ok": False,
        "errors": [f"{type(exc).__name__}: {exc}"],
    }


def _registry_report() -> dict[str, Any]:
    try:
        registry = load_registry()
        errors = validate_registry(registry)
    except Exception as exc:  # CLI trust boundary must remain machine-readable.
        return {
            **_exception_report(exc),
            "technology_count": 0,
        }
    return {
        "ok": not errors,
        "technology_count": len(registry.technologies),
        "errors": errors,
    }


def _generation_report() -> dict[str, Any]:
    try:
        drift = generate(check=True)
    except Exception as exc:  # Renderer/schema defects are readiness failures too.
        return {
            **_exception_report(exc),
            "drift": [],
        }
    return {
        "ok": not drift,
        "drift": list(drift),
        "errors": [],
    }


def _safe_report(check: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        report = check()
    except Exception as exc:  # Never replace a fail-closed report with a traceback.
        return _exception_report(exc)
    if not isinstance(report, dict):
        return {
            "ok": False,
            "errors": [f"TypeError: readiness check returned {type(report).__name__}, expected dict"],
        }
    return report


def build_operational_report() -> dict[str, Any]:
    """Build one deterministic, machine-readable readiness report."""
    checks = {
        "canonical_registry": _registry_report(),
        "generated_surfaces": _generation_report(),
        "integrity": _safe_report(verify_integrity),
        "machine_trust": _safe_report(lambda: build_machine_trust_report(ROOT)),
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
    try:
        report = build_operational_report()
    except Exception as exc:  # Last-resort JSON envelope; KeyboardInterrupt/SystemExit pass through.
        report = {
            "schema": "glaciereq.tower-operational-readiness.v1",
            "repository": "GlacierEQ/the-tower-of-babel",
            "mode": "read_only_fail_closed",
            "ok": False,
            "checks": {},
            "fatal": _exception_report(exc),
        }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
