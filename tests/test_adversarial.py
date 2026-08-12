"""Adversarial tests for Tower truth, authority, and evidence boundaries."""
from __future__ import annotations

import json
from pathlib import Path

from tower.registry import REPO_ROOT, load_registry
from tower.trust import (
    PROMOTION_AUTHORITY,
    TARGET_CONTRACT,
    build_machine_trust_report,
    validate_capability_projection,
    validate_excellence_projection,
    validate_frontier_reference_separation,
    validate_production_reference_row,
    validate_promotion_authority,
    validate_target_contract,
)


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def test_repository_cannot_auto_grant_its_own_promotion(tmp_path: Path) -> None:
    authority = _write(
        tmp_path / "promotion.json",
        {"hmac_grant": "auto_granted"},
    )
    errors = validate_promotion_authority(authority)
    assert any("hmac_grant" in error for error in errors)
    assert any("not_granted" in error for error in errors)


def test_vague_target_contract_cannot_close_target_gate(tmp_path: Path) -> None:
    target = _write(
        tmp_path / "target.json",
        {"unique_value": "hyper-optimization"},
    )
    errors = validate_target_contract(target)
    assert any("schema" in error for error in errors)
    assert any("problem must be substantive" in error for error in errors)
    assert any("unique_value must be substantive" in error for error in errors)
    assert any("invariants" in error for error in errors)


def test_generic_capability_without_evidence_is_rejected(tmp_path: Path) -> None:
    projection = _write(
        tmp_path / "capabilities.json",
        {
            "schema": "glaciereq.machine-capabilities.v1",
            "system_id": "glaciereq.tower-of-babel.v1",
            "capabilities": ["hyper-scaling"],
            "evidence_refs": {},
        },
    )
    errors = validate_capability_projection(projection, repo_root=tmp_path)
    assert any("generic unsupported capabilities" in error for error in errors)
    assert any("missing evidence refs" in error for error in errors)


def test_repository_local_projection_cannot_promote_itself(tmp_path: Path) -> None:
    projection = _write(
        tmp_path / "excellence.json",
        {
            "principal_state": "PROMOTED",
            "state": "PROMOTED",
            "gates": {
                "AUTHORITY_BOUND": {"status": "PASS"},
                "PROOF_RECEIPT_BOUND": {"status": "PENDING"},
            },
            "scores_ref": None,
        },
    )
    errors = validate_excellence_projection(
        projection,
        repo_root=REPO_ROOT,
        promotion_path=PROMOTION_AUTHORITY,
        target_path=TARGET_CONTRACT,
    )
    assert any("cannot exceed OPERABLE" in error for error in errors)
    assert any("AUTHORITY_BOUND cannot PASS" in error for error in errors)


def test_projection_truth_gate_rejects_missing_proof_disguised_as_pass(tmp_path: Path) -> None:
    projection = _write(
        tmp_path / "excellence.json",
        {
            "principal_state": "OPERABLE",
            "state": "OPERABLE",
            "gates": {
                "PROJECTION_TRUTH_CLOSED": {
                    "status": "PASS",
                    "evidence": "proof=missing; operability=missing",
                }
            },
            "scores_ref": None,
        },
    )
    errors = validate_excellence_projection(
        projection,
        repo_root=REPO_ROOT,
        promotion_path=PROMOTION_AUTHORITY,
        target_path=TARGET_CONTRACT,
    )
    assert any("cannot PASS while its own evidence says proof is missing" in error for error in errors)


def test_external_reference_cannot_create_local_production_reference(tmp_path: Path) -> None:
    row = {
        "id": "synthetic-frontier",
        "evidence_state": "production_reference",
        "primary_evidence": ["https://example.invalid/external-production-context"],
    }
    errors = validate_production_reference_row(row, repo_root=tmp_path)
    assert any("local_production_receipt" in error for error in errors)


def test_revision_bound_local_receipt_allows_production_reference(tmp_path: Path) -> None:
    _write(
        tmp_path / "receipts" / "synthetic-production.json",
        {"schema": "test.production-receipt.v1", "revision": "abc123"},
    )
    row = {
        "id": "synthetic-frontier",
        "evidence_state": "production_reference",
        "primary_evidence": ["https://example.invalid/external-production-context"],
        "local_production_receipt": "receipts/synthetic-production.json",
    }
    assert validate_production_reference_row(row, repo_root=tmp_path) == []


def test_frontier_contracts_preserve_promotion_requirements_without_freezing_state() -> None:
    registry = load_registry()
    expected_minimum = {
        "cuda": "tested",
        "jax": "tested",
        "rhl_quant": "benchmark",
    }
    for technology_id, minimum in expected_minimum.items():
        row = registry.by_id(technology_id)
        assert row is not None
        assert row["primary_evidence"], technology_id
        contract = registry.claim_contract_for(technology_id)
        assert contract is not None
        assert contract["promotion_requirements"]["minimum_evidence_state"] == minimum
    assert validate_frontier_reference_separation() == []


def test_current_machine_projection_is_fail_closed_and_coherent() -> None:
    report = build_machine_trust_report(REPO_ROOT)
    assert report["local_state_ceiling"] == "OPERABLE"
    assert report["ok"], report
    for check in report["checks"].values():
        assert check["ok"], check
