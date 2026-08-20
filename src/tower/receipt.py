"""Deterministic Tower release receipt."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .integrity import verify_integrity
from .registry import load_registry, validate_registry


def _stable_json(value: Any) -> bytes:
    return json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")


def _validate_build_report(build_report: dict[str, Any], governed_ids: set[str]) -> list[str]:
    errors: list[str] = []
    rows = build_report.get("results")
    counts = build_report.get("counts")
    if not isinstance(rows, list) or not rows:
        return ["build report requires a non-empty results list"]
    if not isinstance(counts, dict):
        errors.append("build report requires counts")
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"build result {index} must be an object")
            continue
        technology_id = row.get("technology_id")
        status = row.get("status")
        if not isinstance(technology_id, str) or technology_id not in governed_ids:
            errors.append(f"build result {index} has unknown technology_id")
            continue
        if technology_id in seen:
            errors.append(f"duplicate build result: {technology_id}")
        seen.add(technology_id)
        if not isinstance(status, str) or not status:
            errors.append(f"build result {technology_id} requires status")
    missing = sorted(governed_ids - seen)
    if missing:
        errors.append("build report is incomplete: " + ", ".join(missing))
    return errors


def build_receipt(build_report: dict[str, Any]) -> dict[str, Any]:
    registry = load_registry()
    validation_errors = validate_registry(registry)
    governed_ids = {technology["id"] for technology in registry.technologies}
    build_errors = _validate_build_report(build_report, governed_ids)
    integrity = verify_integrity()
    registry_sha = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    integrity_identity_sha = str(integrity.get("receipt_sha256", ""))
    build_sha = hashlib.sha256(_stable_json(build_report)).hexdigest()

    integrity_errors: list[str] = []
    if integrity.get("mode") != "GIT_INDEX_LIVE":
        integrity_errors.append("release receipt requires GIT_INDEX_LIVE integrity")
    if not integrity.get("ok"):
        integrity_errors.append("release receipt requires verified live Git integrity")
    if len(integrity_identity_sha) != 64:
        integrity_errors.append("live Git integrity receipt_sha256 is missing or invalid")
    if not integrity.get("commit_sha") or not integrity.get("tree_sha"):
        integrity_errors.append("live Git integrity commit/tree identity is incomplete")

    body = {
        "schema_version": "2.0.0",
        "tower_id": registry.payload["tower_id"],
        "registry_sha256": registry_sha,
        "integrity_identity_sha256": integrity_identity_sha,
        "integrity_mode": integrity.get("mode"),
        "integrity_commit_sha": integrity.get("commit_sha"),
        "integrity_tree_sha": integrity.get("tree_sha"),
        "build_report_sha256": build_sha,
        "technology_count": len(registry.technologies),
        "registry_valid": not validation_errors,
        "integrity_valid": not integrity_errors,
        "build_report_valid": not build_errors,
        "validation_errors": validation_errors,
        "integrity_errors": integrity_errors,
        "build_report_errors": build_errors,
        "integrity": integrity,
        "build_summary": build_report.get("counts", {}),
    }
    body_sha = hashlib.sha256(_stable_json(body)).hexdigest()
    return {
        **body,
        "receipt_id": f"tower-{registry_sha[:12]}-{integrity_identity_sha[:12]}-{build_sha[:12]}",
        "body_sha256": body_sha,
        "receipt_sha256": body_sha,
    }


def write_receipt(path: Path, build_report: dict[str, Any]) -> dict[str, Any]:
    payload = build_receipt(build_report)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
