import hashlib
import json
from pathlib import Path

from tower.operator_scope import (
    REPOSITORY,
    scope_payload,
    scope_sha256,
    verify_operator_scope_receipt,
)


def write_receipt(path: Path, *, technology_id: str = "python") -> Path:
    instruction_sha = hashlib.sha256(b"execute python with external effects").hexdigest()
    scope = scope_payload(
        authorization_id="operator-request-001",
        instruction_sha256=instruction_sha,
        repository=REPOSITORY,
        technology_id=technology_id,
        mode="execute",
        external_effects=True,
    )
    payload = {
        "schema": "glaciereq.operator-scope.v1",
        "authority_holder": "OPERATOR",
        "authorized": True,
        **scope,
        "scope_sha256": scope_sha256(scope),
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_exact_scope_receipt_authorizes_only_matching_execution(tmp_path: Path):
    path = write_receipt(tmp_path / "scope.json")
    verified = verify_operator_scope_receipt(
        path,
        technology_id="python",
        mode="execute",
        external_effects=True,
    )
    assert verified.authorized is True
    assert verified.errors == ()


def test_scope_receipt_cannot_be_reused_for_another_technology(tmp_path: Path):
    path = write_receipt(tmp_path / "scope.json", technology_id="python")
    verified = verify_operator_scope_receipt(
        path,
        technology_id="rust",
        mode="execute",
        external_effects=True,
    )
    assert verified.authorized is False
    assert any("technology_id" in error for error in verified.errors)


def test_scope_receipt_cannot_widen_from_non_external_to_external(tmp_path: Path):
    path = write_receipt(tmp_path / "scope.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["external_effects"] = False
    path.write_text(json.dumps(payload), encoding="utf-8")

    verified = verify_operator_scope_receipt(
        path,
        technology_id="python",
        mode="execute",
        external_effects=True,
    )
    assert verified.authorized is False
    assert any("external_effects" in error for error in verified.errors)
    assert any("scope_sha256" in error for error in verified.errors)


def test_scope_digest_rejects_instruction_tampering(tmp_path: Path):
    path = write_receipt(tmp_path / "scope.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["instruction_sha256"] = hashlib.sha256(b"different instruction").hexdigest()
    path.write_text(json.dumps(payload), encoding="utf-8")

    verified = verify_operator_scope_receipt(
        path,
        technology_id="python",
        mode="execute",
        external_effects=True,
    )
    assert verified.authorized is False
    assert any("scope_sha256" in error for error in verified.errors)


def test_receipt_does_not_claim_cryptographic_identity_proof(tmp_path: Path):
    path = write_receipt(tmp_path / "scope.json")
    verified = verify_operator_scope_receipt(
        path,
        technology_id="python",
        mode="execute",
        external_effects=True,
    )
    payload = verified.to_dict()
    assert verified.authorized is True
    assert "does not independently prove human identity" in payload["identity_nonclaim"]
