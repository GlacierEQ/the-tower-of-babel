"""Fail-closed validation for Tower machine projections and promotion boundaries.

The canonical technology registry may describe and verify local capabilities, but
repository-local files must never promote themselves by assertion.  This module
keeps the boundary explicit:

* external production references never upgrade local implementation evidence;
* repository-local excellence state has an ``OPERABLE`` ceiling;
* promotion authority cannot be self-granted inside this repository;
* proof, adversarial, and operability gates must point at substantive artifacts.

An external control plane may later verify a signed promotion receipt, but that
verification must live outside the subject repository's trust boundary.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT, load_registry, validate_registry

MACHINE_DIR = REPO_ROOT / "machine"
TARGET_CONTRACT = MACHINE_DIR / "target-contract.json"
PROMOTION_AUTHORITY = MACHINE_DIR / "promotion_authority.json"
EXCELLENCE_STATE = MACHINE_DIR / "excellence-state.json"

LOCAL_STATE_CEILING = "OPERABLE"
_STATE_ORDER = {
    "DISCOVERED": 0,
    "IDENTITY_RESOLVED": 1,
    "PROBLEM_VERIFIED": 2,
    "TARGET_CONTRACTED": 3,
    "SEEDED": 4,
    "VERTICAL_SLICE": 5,
    "IMPLEMENTED": 6,
    "TESTED": 7,
    "ADVERSARIAL_VERIFIED": 8,
    "OPERABLE": 9,
    "PROOF_REPRODUCED": 10,
    "PROMOTED": 11,
}
_REQUIRED_TARGET_INVARIANTS = {
    "plurality_preserved",
    "local_authority_not_reinterpreted",
    "proof_before_promotion",
    "explicit_blockers_not_false_success",
    "external_references_do_not_promote_local_evidence",
    "deterministic_receipts",
}
_FRONTIER_REFERENCE_ONLY = ("cuda", "jax", "rhl_quant")
_RUNTIME_EVIDENCE = {
    "tested",
    "benchmark",
    "formally_verified",
    "integrated",
    "production_reference",
}


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is unreadable: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object")
    return payload


def validate_target_contract(path: Path = TARGET_CONTRACT) -> list[str]:
    """Validate the machine target contract as a substantive system contract."""
    errors: list[str] = []
    try:
        payload = _load_object(path, "target contract")
    except ValueError as exc:
        return [str(exc)]

    if payload.get("schema") != "glaciereq.tower-target-contract.v1":
        errors.append("target contract schema must be glaciereq.tower-target-contract.v1")
    if payload.get("system_id") != "glaciereq.tower-of-babel.v1":
        errors.append("target contract system_id must identify the Tower")
    if payload.get("repository") != "GlacierEQ/the-tower-of-babel":
        errors.append("target contract repository must identify GlacierEQ/the-tower-of-babel")
    if payload.get("canonical_authority") != "registry/tower.yml":
        errors.append("target contract canonical_authority must be registry/tower.yml")

    problem = payload.get("problem")
    if not isinstance(problem, str) or len(problem.strip()) < 60:
        errors.append("target contract problem must be substantive")
    unique_value = payload.get("unique_value")
    if not isinstance(unique_value, str) or len(unique_value.strip()) < 60:
        errors.append("target contract unique_value must be substantive")

    invariants = payload.get("invariants")
    if not isinstance(invariants, list) or not all(isinstance(item, str) for item in invariants):
        errors.append("target contract invariants must be a string list")
    else:
        missing = sorted(_REQUIRED_TARGET_INVARIANTS - set(invariants))
        if missing:
            errors.append("target contract missing invariants: " + ", ".join(missing))

    policy = payload.get("promotion_policy")
    if not isinstance(policy, dict):
        errors.append("target contract promotion_policy must be an object")
    else:
        if policy.get("local_projection_ceiling") != LOCAL_STATE_CEILING:
            errors.append(f"local projection ceiling must be {LOCAL_STATE_CEILING}")
        if policy.get("external_authority_required") is not True:
            errors.append("promotion policy must require external authority")
        if policy.get("revision_bound_proof_required") is not True:
            errors.append("promotion policy must require revision-bound proof")
        if policy.get("external_reference_is_not_local_proof") is not True:
            errors.append("promotion policy must separate external references from local proof")
    return errors


def validate_promotion_authority(path: Path = PROMOTION_AUTHORITY) -> list[str]:
    """Reject repository-local self-promotion and legacy auto-grants."""
    errors: list[str] = []
    try:
        payload = _load_object(path, "promotion authority")
    except ValueError as exc:
        return [str(exc)]

    if payload.get("schema") != "glaciereq.promotion-authority-boundary.v1":
        errors.append("promotion authority schema must be glaciereq.promotion-authority-boundary.v1")
    if payload.get("subject") != "GlacierEQ/the-tower-of-babel":
        errors.append("promotion authority subject must identify this repository")
    if "hmac_grant" in payload:
        errors.append("repository-local hmac_grant is forbidden")
    if payload.get("mode") != "not_granted":
        errors.append("repository-local promotion authority must remain not_granted")
    reason = payload.get("reason")
    if not isinstance(reason, str) or len(reason.strip()) < 40:
        errors.append("promotion authority requires a substantive fail-closed reason")
    requirements = payload.get("external_requirements")
    if not isinstance(requirements, list) or len(requirements) < 3 or not all(
        isinstance(item, str) and item.strip() for item in requirements
    ):
        errors.append("promotion authority must declare external promotion requirements")
    return errors


def validate_frontier_reference_separation() -> list[str]:
    """Ensure external industry references cannot promote local frontier exhibits."""
    errors: list[str] = []
    try:
        registry = load_registry()
    except ValueError as exc:
        return [str(exc)]

    for technology_id in _FRONTIER_REFERENCE_ONLY:
        row = registry.by_id(technology_id)
        if row is None:
            errors.append(f"frontier floor missing: {technology_id}")
            continue
        state = row.get("evidence_state")
        if state in _RUNTIME_EVIDENCE:
            errors.append(
                f"{technology_id} local evidence is {state!r}; reference-only frontier floors "
                "must remain unpromoted until executable local evidence exists"
            )
        notes = str(row.get("verification_notes", "")).lower()
        if "demoted" not in notes and "reference" not in notes:
            errors.append(f"{technology_id} must state its local proof limitation explicitly")

        contract = registry.claim_contract_for(technology_id)
        if not isinstance(contract, dict):
            errors.append(f"{technology_id} advanced claim contract missing")
            continue
        promotion = contract.get("promotion_requirements")
        if not isinstance(promotion, dict):
            errors.append(f"{technology_id} promotion requirements missing")
            continue
        minimum = promotion.get("minimum_evidence_state")
        if technology_id == "rhl_quant" and minimum != "benchmark":
            errors.append("rhl_quant promotion must require benchmark evidence")
        if technology_id in {"cuda", "jax"} and minimum != "tested":
            errors.append(f"{technology_id} promotion must require tested evidence")
    return errors


def validate_excellence_projection(
    path: Path = EXCELLENCE_STATE,
    *,
    repo_root: Path = REPO_ROOT,
    promotion_path: Path = PROMOTION_AUTHORITY,
    target_path: Path = TARGET_CONTRACT,
) -> list[str]:
    """Validate that the local excellence projection cannot outrun physical proof."""
    errors: list[str] = []
    try:
        payload = _load_object(path, "excellence projection")
        promotion = _load_object(promotion_path, "promotion authority")
    except ValueError as exc:
        return [str(exc)]

    principal_state = payload.get("principal_state")
    state = payload.get("state")
    if not isinstance(principal_state, str) or principal_state not in _STATE_ORDER:
        errors.append("excellence projection principal_state is invalid")
    if state != principal_state:
        errors.append("excellence projection state must equal principal_state")
    if isinstance(principal_state, str) and principal_state in _STATE_ORDER:
        if _STATE_ORDER[principal_state] > _STATE_ORDER[LOCAL_STATE_CEILING]:
            errors.append(
                f"repository-local excellence state cannot exceed {LOCAL_STATE_CEILING}; "
                "promotion belongs to an external authority"
            )

    serialized = json.dumps(payload, sort_keys=True)
    for forbidden in ("HYPER_VALIDATED_SHA256", "HYPER_VALIDATED_IDENTITY", "auto_granted"):
        if forbidden in serialized:
            errors.append(f"placeholder promotion evidence is forbidden: {forbidden}")

    gates = payload.get("gates")
    if not isinstance(gates, dict):
        errors.append("excellence projection gates must be an object")
        return errors

    authority_gate = gates.get("AUTHORITY_BOUND", {})
    if promotion.get("mode") == "not_granted" and isinstance(authority_gate, dict):
        if authority_gate.get("status") == "PASS":
            errors.append("AUTHORITY_BOUND cannot PASS while promotion authority is not_granted")

    proof_gate = gates.get("PROOF_RECEIPT_BOUND", {})
    if isinstance(proof_gate, dict) and proof_gate.get("status") == "PASS":
        proof_ref = payload.get("proof_receipt_ref", "machine/proof_receipt.json")
        proof_path = repo_root / proof_ref if isinstance(proof_ref, str) else Path("")
        if not isinstance(proof_ref, str) or not proof_path.is_file():
            errors.append("PROOF_RECEIPT_BOUND cannot PASS without a checked-in proof receipt")

    target_gate = gates.get("TARGET_CONTRACT_FROZEN", {})
    if isinstance(target_gate, dict) and target_gate.get("status") == "PASS":
        errors.extend(f"TARGET_CONTRACT_FROZEN: {error}" for error in validate_target_contract(target_path))

    adversarial_gate = gates.get("ADVERSARIAL_SURVIVAL", {})
    if isinstance(adversarial_gate, dict) and adversarial_gate.get("status") == "PASS":
        adversarial = repo_root / "tests" / "test_adversarial.py"
        try:
            source = adversarial.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"ADVERSARIAL_SURVIVAL evidence unreadable: {exc}")
        else:
            compact = "".join(source.split())
            if len(source) < 500 or compact in {
                "deftest_adversarial_bounds():assertTrue",
                "deftest_adversarial_bounds():assert1",
            }:
                errors.append("ADVERSARIAL_SURVIVAL cannot rely on a placeholder test")

    operate_gate = gates.get("OPERABLE_AND_OBSERVABLE", {})
    if isinstance(operate_gate, dict) and operate_gate.get("status") == "PASS":
        operate = repo_root / "scripts" / "operate.py"
        try:
            source = operate.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"OPERABLE_AND_OBSERVABLE evidence unreadable: {exc}")
        else:
            if len(source) < 800 or "Runtime observed ok" in source:
                errors.append("OPERABLE_AND_OBSERVABLE requires a substantive fail-closed operator")

    projection_gate = gates.get("PROJECTION_TRUTH_CLOSED", {})
    if isinstance(projection_gate, dict) and projection_gate.get("status") == "PASS":
        evidence = str(projection_gate.get("evidence", "")).lower()
        if "proof=missing" in evidence or "operability=missing" in evidence:
            errors.append("PROJECTION_TRUTH_CLOSED cannot PASS while its own evidence says proof is missing")

    scores_ref = payload.get("scores_ref")
    if isinstance(scores_ref, str) and scores_ref and not (repo_root / scores_ref).is_file():
        errors.append(f"excellence projection references missing scores file: {scores_ref}")
    return errors


def build_machine_trust_report(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    """Return one deterministic report for the repository-local trust boundary."""
    checks: dict[str, list[str]] = {}
    try:
        registry = load_registry()
        checks["canonical_registry"] = validate_registry(registry)
    except ValueError as exc:
        checks["canonical_registry"] = [str(exc)]

    checks["target_contract"] = validate_target_contract(repo_root / "machine" / "target-contract.json")
    checks["promotion_authority"] = validate_promotion_authority(
        repo_root / "machine" / "promotion_authority.json"
    )
    checks["frontier_reference_separation"] = validate_frontier_reference_separation()
    checks["excellence_projection"] = validate_excellence_projection(
        repo_root / "machine" / "excellence-state.json",
        repo_root=repo_root,
        promotion_path=repo_root / "machine" / "promotion_authority.json",
        target_path=repo_root / "machine" / "target-contract.json",
    )
    return {
        "schema": "glaciereq.tower-machine-trust-report.v1",
        "local_state_ceiling": LOCAL_STATE_CEILING,
        "ok": all(not errors for errors in checks.values()),
        "checks": {
            name: {"ok": not errors, "errors": errors}
            for name, errors in checks.items()
        },
    }
