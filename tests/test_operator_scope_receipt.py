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


def test_cli_passes_only_verified_operator_scope_to_runtime(tmp_path: Path, monkeypatch, capsys):
    from tower import activation_cli

    receipt = write_receipt(tmp_path / "scope.json")

    class Registry:
        def by_id(self, technology_id: str):
            return {"id": technology_id}

    observed = {}

    def fake_activate(technology, *, external_effects=False, operator_scope_authorized=False):
        observed["technology"] = technology
        observed["external_effects"] = external_effects
        observed["operator_scope_authorized"] = operator_scope_authorized
        return {"status": "VERIFIED", "technology_id": technology["id"]}

    monkeypatch.setattr(activation_cli, "load_registry", lambda: Registry())
    monkeypatch.setattr(activation_cli, "activate_execution", fake_activate)

    rc = activation_cli.main(
        [
            "python",
            "--external-effects",
            "--operator-scope-receipt",
            str(receipt),
        ]
    )
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert observed["external_effects"] is True
    assert observed["operator_scope_authorized"] is True
    assert payload["operator_scope"]["authorized"] is True


def test_cli_missing_operator_scope_never_promotes_flag_to_authority(monkeypatch, capsys):
    from tower import activation_cli

    class Registry:
        def by_id(self, technology_id: str):
            return {"id": technology_id}

    observed = {}

    def fake_activate(technology, *, external_effects=False, operator_scope_authorized=False):
        observed["operator_scope_authorized"] = operator_scope_authorized
        return {"status": "ACTIVATION_BLOCKED", "technology_id": technology["id"]}

    monkeypatch.setattr(activation_cli, "load_registry", lambda: Registry())
    monkeypatch.setattr(activation_cli, "activate_execution", fake_activate)

    rc = activation_cli.main(["python", "--external-effects"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert observed["operator_scope_authorized"] is False
    assert payload["operator_scope"]["authorized"] is False
