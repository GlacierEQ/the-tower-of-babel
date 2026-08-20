"""Deterministic local proof for the Tower of Babel thread."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any, Sequence

from tower.integrity import verify_integrity, write_manifest
from tower.receipt import build_receipt
from tower.registry import load_registry, validate_registry
from tower.visualize import build_topology_graph


PROOF_SCHEMA = "glaciereq.tower-of-babel.context-integrity-proof.v1"
TRUTH_BOUNDARY = (
    "This proof validates local registry consistency, generated-file integrity, "
    "topology construction, and deterministic receipt generation. It does not compile "
    "every technology, benchmark performance, provision hardware, or authorize a toolchain command."
)


def _failure_receipt(stage: str, error: Exception) -> dict[str, Any]:
    """Return an inspectable failed-proof result without masking the failure stage."""
    return {
        "schema": PROOF_SCHEMA,
        "status": "failed",
        "failed_stage": stage,
        "error": f"{type(error).__name__}: {error}",
        "truth_boundary": TRUTH_BOUNDARY,
    }


def _non_execution_build_report(registry: Any) -> dict[str, Any]:
    """Describe every governed floor without claiming that its toolchain was executed."""
    technology_count = len(registry.technologies)
    return {
        "counts": {"NOT_EXECUTED": technology_count},
        "results": [
            {"technology_id": technology["id"], "status": "NOT_EXECUTED"}
            for technology in registry.technologies
        ],
    }


def run() -> dict[str, Any]:
    try:
        registry = load_registry()
    except Exception as exc:
        return _failure_receipt("load_registry", exc)

    try:
        registry_errors = validate_registry(registry)
    except Exception as exc:
        return _failure_receipt("validate_registry", exc)

    try:
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "integrity.json"
            manifest = write_manifest(manifest_path)
            integrity = verify_integrity(manifest_path)
    except Exception as exc:
        return _failure_receipt("verify_integrity", exc)

    try:
        receipt = build_receipt(_non_execution_build_report(registry))
    except Exception as exc:
        return _failure_receipt("build_receipt", exc)

    try:
        topology = build_topology_graph(registry)
    except Exception as exc:
        return _failure_receipt("build_topology_graph", exc)

    failure_reasons = []
    if registry_errors:
        failure_reasons.append("registry_validation")
    if not integrity["ok"]:
        failure_reasons.append("integrity_verification")
    if not receipt["registry_valid"]:
        failure_reasons.append("receipt_registry_validation")
    if not receipt["build_report_valid"]:
        failure_reasons.append("receipt_build_report_validation")

    return {
        "schema": PROOF_SCHEMA,
        "status": "verified" if not failure_reasons else "failed",
        "failure_reasons": failure_reasons,
        "technology_count": len(registry.technologies),
        "registry_errors": registry_errors,
        "integrity_file_count": manifest["file_count"],
        "integrity_verified": integrity["ok"],
        "topology_node_count": topology["node_count"],
        "receipt_sha256": receipt["receipt_sha256"],
        "receipt_registry_valid": receipt["registry_valid"],
        "receipt_integrity_valid": receipt["integrity_valid"],
        "receipt_build_report_valid": receipt["build_report_valid"],
        "truth_boundary": TRUTH_BOUNDARY,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    receipt = run()
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        except OSError as exc:
            receipt = _failure_receipt("write_output", exc)
            rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    return 0 if receipt["status"] == "verified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
