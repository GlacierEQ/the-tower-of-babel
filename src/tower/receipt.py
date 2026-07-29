"""Deterministic Tower release receipt."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .integrity import MANIFEST, verify_integrity
from .registry import REPO_ROOT, load_registry, validate_registry


def _canonical(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def build_receipt(build_report: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = load_registry()
    errors = validate_registry(registry)
    integrity = verify_integrity()
    registry_sha = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    manifest_sha = hashlib.sha256(MANIFEST.read_bytes()).hexdigest() if MANIFEST.is_file() else ""
    report = build_report or {}
    build_sha = hashlib.sha256(_canonical(report)).hexdigest()
    body = {
        "schema_version": "1.0.0",
        "tower_id": registry.payload["tower_id"],
        "registry_sha256": registry_sha,
        "integrity_manifest_sha256": manifest_sha,
        "build_report_sha256": build_sha,
        "technology_count": len(registry.technologies),
        "registry_valid": not errors,
        "integrity_valid": bool(integrity.get("ok")),
        "validation_errors": errors,
        "integrity": integrity,
        "build_summary": report.get("counts", {}),
    }
    body_sha = hashlib.sha256(_canonical(body)).hexdigest()
    return {
        **body,
        "receipt_id": f"tower-{registry_sha[:12]}-{manifest_sha[:12]}-{build_sha[:12]}",
        "receipt_sha256": body_sha,
    }


def write_receipt(path: Path, build_report: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = build_receipt(build_report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
