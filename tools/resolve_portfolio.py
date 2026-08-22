#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from tower.portfolio import PortfolioRequirements, TechnologyPortfolioPlanner
from tower.registry import load_registry


def read_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("portfolio demand root must be an object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve an explicit Tower technology portfolio demand.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument(
        "--preference",
        choices=("balanced", "strongest_proof", "minimal_stack", "maximum_coverage"),
        default="balanced",
    )
    args = parser.parse_args()

    raw = read_object(args.input)
    requirements_raw = raw.get("requirements")
    if not isinstance(requirements_raw, dict):
        raise ValueError("requirements must be an object")
    requirements_data = dict(requirements_raw)
    for key in ("required_interfaces", "preferred_categories", "required_technology_ids"):
        if key in requirements_data:
            value = requirements_data[key]
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise ValueError(f"{key} must be a string list")
            requirements_data[key] = frozenset(value)

    requirements = PortfolioRequirements(**requirements_data)
    decision = TechnologyPortfolioPlanner(load_registry(), requirements).decide(args.preference)
    payload = decision.as_dict()
    payload["requirements"] = {
        "required_interfaces": sorted(requirements.required_interfaces),
        "preferred_categories": sorted(requirements.preferred_categories),
        "required_technology_ids": sorted(requirements.required_technology_ids),
        "minimum_evidence_state": requirements.minimum_evidence_state,
        "allow_gated": requirements.allow_gated,
        "require_full_interface_coverage": requirements.require_full_interface_coverage,
        "max_technologies": requirements.max_technologies,
        "max_candidates": requirements.max_candidates,
        "max_combinations": requirements.max_combinations,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    artifact_sha = hashlib.sha256(args.output.read_bytes()).hexdigest()
    receipt = {
        "schema": "glaciereq.tower.portfolio-receipt.v1",
        "artifact": str(args.output),
        "artifact_sha256": artifact_sha,
        "decision_sha256": payload["decision_sha256"],
        "selected_technologies": [
            row["technology_id"] for row in payload["selected"]["technologies"]
        ],
        "evidence_state": payload["evidence_state"],
        "verified_state": "DETERMINISTIC_PORTFOLIO_MODEL_EXECUTED",
        "execution_claim": "PORTFOLIO_SELECTED_TECHNOLOGIES_NOT_YET_EXECUTED",
        "project_direction_authority": "OPERATOR",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
