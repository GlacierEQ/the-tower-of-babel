"""Build-bound proof and evidence report."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .registry import TowerRegistry


def build_proof_report(registry: TowerRegistry, build_report: dict[str, Any]) -> dict[str, Any]:
    statuses = {
        row["technology_id"]: row["status"]
        for row in build_report.get("results", [])
    }
    floors = []
    for tech in registry.technologies:
        build_status = statuses.get(tech["id"], "NOT_EXECUTED")
        proof_class = tech["proof_class"]
        if build_status == "VERIFIED":
            proof_status = "SATISFIED_FOR_DECLARED_GATE"
        elif build_status.startswith("BLOCKED_"):
            proof_status = "BLOCKED"
        elif build_status == "NOT_EXECUTED":
            proof_status = "NOT_EXECUTED"
        else:
            proof_status = "FAILED"
        floors.append({
            "technology_id": tech["id"],
            "easy_example": tech["easy_example"],
            "advanced_example": tech["advanced_example"],
            "evidence_state": tech["evidence_state"],
            "proof_class": proof_class,
            "build_status": build_status,
            "proof_status": proof_status,
            "primary_evidence": tech["primary_evidence"],
        })
    return {
        "proof_report_id": "tower-proof-report-v1",
        "tower_id": registry.payload["tower_id"],
        "floors": floors,
        "counts": {
            status: sum(1 for floor in floors if floor["proof_status"] == status)
            for status in sorted({floor["proof_status"] for floor in floors})
        },
    }


def write_proof_report(report: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
