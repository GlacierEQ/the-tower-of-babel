"""Proof-gated additive technology diversification for the Tower.

The Tower does not optimize for the fewest technologies. It evaluates whether a
candidate contributes a distinct system benefit that is worth its integration
and operational cost. Existing technologies may remain excellent in their own
roles while a specialist is added for another role.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .registry import REPO_ROOT, load_registry

POLICY_PATH = REPO_ROOT / "machine" / "diversification-policy.json"

_REQUIRED_DECISION_FIELDS = {
    "problem_boundary",
    "existing_composition",
    "candidate_floor",
    "benefit_dimension",
    "measurable_requirement",
    "comparison_method",
    "integration_cost",
    "failure_modes",
    "interop_boundary",
    "proof_gate",
    "rollback_path",
}
_REQUIRED_ADMISSION_GATES = {
    "boundary_is_real_not_novelty",
    "candidate_has_distinct_system_role",
    "marginal_benefit_is_positive",
    "benefit_claim_matches_required_evidence",
    "interop_contract_explicit",
    "operational_cost_bounded",
    "failure_and_rollback_defined",
    "required_evidence_gate_passed",
}
_EVIDENCE_ORDER = {
    "illustrative": 0,
    "compiles": 1,
    "toolchain_gated": 1,
    "service_gated": 1,
    "hardware_gated": 1,
    "tested": 2,
    "behavioral": 2,
    "benchmark": 3,
    "hardware": 3,
    "formally_verified": 4,
    "formal": 4,
    "integrated": 5,
    "production_reference": 6,
}


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} unreadable: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object")
    return payload


def validate_diversification_policy(path: Path = POLICY_PATH) -> list[str]:
    """Validate the authored additive specialization policy against the registry."""
    errors: list[str] = []
    try:
        policy = _load_object(path, "diversification policy")
        registry = load_registry()
    except ValueError as exc:
        return [str(exc)]

    if policy.get("schema") != "glaciereq.technology-diversification-policy.v2":
        errors.append("diversification policy schema must be v2 additive specialization")
    if policy.get("system_id") != "glaciereq.tower-of-babel.v1":
        errors.append("diversification policy system_id must identify the Tower")
    if policy.get("default_decision") != "evaluate_additive_benefit":
        errors.append("diversification must default to evaluate_additive_benefit")
    if policy.get("optimization_goal") != "maximize_verified_system_advantage_without_redundant_responsibility":
        errors.append("diversification optimization goal must maximize verified system advantage")

    dimensions = policy.get("benefit_dimensions")
    if not isinstance(dimensions, list) or not dimensions or not all(
        isinstance(item, str) and item.strip() for item in dimensions
    ):
        errors.append("diversification benefit_dimensions must be a non-empty string list")
        dimensions = []

    proof_floor = policy.get("benefit_proof_floor")
    if not isinstance(proof_floor, dict):
        errors.append("benefit_proof_floor must be an object")
    else:
        missing_floors = sorted(set(dimensions) - set(proof_floor))
        if missing_floors:
            errors.append("benefit dimensions missing proof floors: " + ", ".join(missing_floors))

    decision = policy.get("decision_record")
    fields = decision.get("required_fields") if isinstance(decision, dict) else None
    if not isinstance(fields, list) or not all(isinstance(item, str) for item in fields):
        errors.append("diversification decision_record.required_fields must be a string list")
    else:
        missing = sorted(_REQUIRED_DECISION_FIELDS - set(fields))
        if missing:
            errors.append("diversification decision record missing fields: " + ", ".join(missing))

    gates = policy.get("admission_gates")
    if not isinstance(gates, list) or not all(isinstance(item, str) for item in gates):
        errors.append("diversification admission_gates must be a string list")
    else:
        missing = sorted(_REQUIRED_ADMISSION_GATES - set(gates))
        if missing:
            errors.append("diversification policy missing gates: " + ", ".join(missing))

    anti_patterns = policy.get("anti_patterns")
    if not isinstance(anti_patterns, list) or "minimal_language_count_as_quality" not in anti_patterns:
        errors.append("policy must explicitly reject minimal language count as a quality objective")

    role_examples = policy.get("role_examples")
    if not isinstance(role_examples, dict) or not role_examples:
        errors.append("diversification role_examples must be a non-empty object")
    else:
        registry_ids = {str(row.get("id")) for row in registry.technologies if isinstance(row, dict)}
        for technology_id, role in role_examples.items():
            if technology_id not in registry_ids:
                errors.append(f"diversification role references unknown floor: {technology_id}")
                continue
            if not isinstance(role, dict):
                errors.append(f"diversification role must be an object: {technology_id}")
                continue
            for field in ("owns", "does_not_own"):
                values = role.get(field)
                if not isinstance(values, list) or not values or not all(
                    isinstance(item, str) and item.strip() for item in values
                ):
                    errors.append(f"{technology_id} diversification role requires non-empty {field}")
    return errors


def evaluate_candidate(
    record: Mapping[str, Any],
    *,
    policy_path: Path = POLICY_PATH,
) -> dict[str, Any]:
    """Evaluate one additive specialization decision without mutating the registry."""
    errors = list(validate_diversification_policy(policy_path))
    missing = sorted(
        field
        for field in _REQUIRED_DECISION_FIELDS
        if not isinstance(record.get(field), str) or not str(record.get(field)).strip()
    )
    if missing:
        errors.append("decision record missing substantive fields: " + ", ".join(missing))

    candidate = str(record.get("candidate_floor", "")).strip()
    benefit = str(record.get("benefit_dimension", "")).strip()

    try:
        policy = _load_object(policy_path, "diversification policy")
        registry = load_registry()
    except ValueError as exc:
        errors.append(str(exc))
        policy = {}
        registry = None

    candidate_row = registry.by_id(candidate) if registry is not None and candidate else None
    if candidate and candidate_row is None:
        errors.append(f"candidate floor is not governed by the Tower: {candidate}")

    dimensions = set(policy.get("benefit_dimensions", [])) if isinstance(policy, dict) else set()
    if benefit and benefit not in dimensions:
        errors.append(f"unknown benefit_dimension: {benefit}")

    proof_gate = str(record.get("proof_gate", "")).strip()
    current_state = str(candidate_row.get("evidence_state", "")) if candidate_row else ""
    current_proof = str(candidate_row.get("proof_class", "")) if candidate_row else ""

    if proof_gate in _EVIDENCE_ORDER:
        candidate_level = max(
            _EVIDENCE_ORDER.get(current_state, -1),
            _EVIDENCE_ORDER.get(current_proof, -1),
        )
        if candidate_level < _EVIDENCE_ORDER[proof_gate]:
            errors.append(
                f"candidate proof {current_state!r}/{current_proof!r} does not meet proof_gate {proof_gate!r}"
            )
    elif proof_gate:
        errors.append(f"unknown proof_gate evidence state: {proof_gate}")

    benefit_floors = policy.get("benefit_proof_floor", {}) if isinstance(policy, dict) else {}
    required_floor = benefit_floors.get(benefit)
    if benefit and isinstance(required_floor, str) and required_floor in _EVIDENCE_ORDER:
        candidate_level = max(
            _EVIDENCE_ORDER.get(current_state, -1),
            _EVIDENCE_ORDER.get(current_proof, -1),
        )
        if candidate_level < _EVIDENCE_ORDER[required_floor]:
            errors.append(
                f"benefit {benefit!r} requires {required_floor!r} evidence; "
                f"candidate has {current_state!r}/{current_proof!r}"
            )

    return {
        "schema": "glaciereq.technology-admission-decision.v2",
        "decision": "ADMIT" if not errors else "REJECT",
        "default": "evaluate_additive_benefit",
        "optimization_goal": "maximize_verified_system_advantage_without_redundant_responsibility",
        "candidate_floor": candidate,
        "benefit_dimension": benefit or None,
        "candidate_evidence_state": current_state or None,
        "candidate_proof_class": current_proof or None,
        "existing_composition_preserved": True,
        "errors": errors,
    }
