"""Proof-gated technology diversification for the Tower.

The Tower is not rewarded for language count. Existing floors win by default.
A candidate is admissible only when a concrete boundary is identified, the
incumbent limitation is stated, the candidate has a measurable comparison plan,
and the candidate's current local evidence meets the requested proof gate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .registry import REPO_ROOT, load_registry

POLICY_PATH = REPO_ROOT / "machine" / "diversification-policy.json"

_REQUIRED_DECISION_FIELDS = {
    "problem_boundary",
    "incumbent_floor",
    "candidate_floor",
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
    "incumbent_limitation_demonstrated",
    "candidate_advantage_measured",
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
    "benchmark": 3,
    "formally_verified": 4,
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
    """Validate the authored technology-selection policy against the registry."""
    errors: list[str] = []
    try:
        policy = _load_object(path, "diversification policy")
        registry = load_registry()
    except ValueError as exc:
        return [str(exc)]

    if policy.get("schema") != "glaciereq.technology-diversification-policy.v1":
        errors.append("diversification policy schema is invalid")
    if policy.get("system_id") != "glaciereq.tower-of-babel.v1":
        errors.append("diversification policy system_id must identify the Tower")
    if policy.get("default_decision") != "reuse_existing_floor":
        errors.append("diversification must default to reuse_existing_floor")

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
    """Evaluate one proposed diversification decision without mutating the registry."""
    policy_errors = validate_diversification_policy(policy_path)
    errors = list(policy_errors)
    missing = sorted(
        field
        for field in _REQUIRED_DECISION_FIELDS
        if not isinstance(record.get(field), str) or not str(record.get(field)).strip()
    )
    if missing:
        errors.append("decision record missing substantive fields: " + ", ".join(missing))

    incumbent = str(record.get("incumbent_floor", "")).strip()
    candidate = str(record.get("candidate_floor", "")).strip()
    if incumbent and candidate and incumbent == candidate:
        errors.append("candidate_floor must differ from incumbent_floor")

    try:
        registry = load_registry()
    except ValueError as exc:
        errors.append(str(exc))
        registry = None

    candidate_row = registry.by_id(candidate) if registry is not None and candidate else None
    if candidate and candidate_row is None:
        errors.append(f"candidate floor is not governed by the Tower: {candidate}")
    if incumbent and incumbent != "none" and registry is not None and registry.by_id(incumbent) is None:
        errors.append(f"incumbent floor is not governed by the Tower: {incumbent}")

    proof_gate = str(record.get("proof_gate", "")).strip()
    current_state = str(candidate_row.get("evidence_state", "")) if candidate_row else ""
    if proof_gate in _EVIDENCE_ORDER and current_state in _EVIDENCE_ORDER:
        if _EVIDENCE_ORDER[current_state] < _EVIDENCE_ORDER[proof_gate]:
            errors.append(
                f"candidate evidence_state {current_state!r} does not meet proof_gate {proof_gate!r}"
            )
    elif proof_gate and proof_gate not in _EVIDENCE_ORDER:
        errors.append(f"unknown proof_gate evidence state: {proof_gate}")

    return {
        "schema": "glaciereq.technology-admission-decision.v1",
        "decision": "ADMIT" if not errors else "REJECT",
        "default": "reuse_existing_floor",
        "candidate_floor": candidate,
        "incumbent_floor": incumbent,
        "candidate_evidence_state": current_state or None,
        "errors": errors,
    }
