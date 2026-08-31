"""Exact-scope Operator authorization receipts for high-consequence Tower execution.

This module verifies receipt structure, exact execution scope, and deterministic
content integrity for materially irreversible or conservatively unclassified
external effects. Reversible external work does not manufacture a redundant
second approval requirement. It does not pretend to prove human identity cryptographically;
the trust boundary is the Operator-controlled invocation environment. A receipt
cannot widen itself beyond the exact repository, technology, mode, and external-
effects tuple it names.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SCHEMA = "glaciereq.operator-scope.v1"
REPOSITORY = "GlacierEQ/the-tower-of-babel"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class OperatorScopeVerification:
    authorized: bool
    authorization_id: str
    instruction_sha256: str
    scope_sha256: str
    errors: tuple[str, ...]
    assurance: str = "exact-scope-and-integrity-verified"

    def to_dict(self) -> dict[str, Any]:
        return {
            "authorized": self.authorized,
            "authorization_id": self.authorization_id,
            "instruction_sha256": self.instruction_sha256,
            "scope_sha256": self.scope_sha256,
            "errors": list(self.errors),
            "assurance": self.assurance,
            "identity_nonclaim": (
                "receipt integrity does not independently prove human identity; "
                "the invocation environment supplies the Operator trust boundary"
            ),
        }


def scope_payload(
    *,
    authorization_id: str,
    instruction_sha256: str,
    repository: str,
    technology_id: str,
    mode: str,
    external_effects: bool,
) -> dict[str, Any]:
    return {
        "authorization_id": authorization_id,
        "instruction_sha256": instruction_sha256,
        "repository": repository,
        "technology_id": technology_id,
        "mode": mode,
        "external_effects": external_effects,
    }


def scope_sha256(scope: Mapping[str, Any]) -> str:
    encoded = json.dumps(
        dict(scope),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def verify_operator_scope_receipt(
    path: Path,
    *,
    technology_id: str,
    mode: str,
    external_effects: bool,
    repository: str = REPOSITORY,
) -> OperatorScopeVerification:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return OperatorScopeVerification(
            authorized=False,
            authorization_id="",
            instruction_sha256="",
            scope_sha256="",
            errors=(f"operator scope receipt unreadable: {exc}",),
        )

    if not isinstance(payload, dict):
        return OperatorScopeVerification(
            authorized=False,
            authorization_id="",
            instruction_sha256="",
            scope_sha256="",
            errors=("operator scope receipt root must be an object",),
        )

    if payload.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    if payload.get("authority_holder") != "OPERATOR":
        errors.append("authority_holder must be OPERATOR")
    if payload.get("authorized") is not True:
        errors.append("authorized must be true")

    authorization_id = payload.get("authorization_id")
    if not isinstance(authorization_id, str) or not authorization_id.strip():
        errors.append("authorization_id must be non-empty")
        authorization_id = ""

    instruction_sha = payload.get("instruction_sha256")
    if not isinstance(instruction_sha, str) or not _SHA256.fullmatch(instruction_sha):
        errors.append("instruction_sha256 must be a lowercase SHA-256 digest")
        instruction_sha = ""

    expected_scope = scope_payload(
        authorization_id=authorization_id,
        instruction_sha256=instruction_sha,
        repository=repository,
        technology_id=technology_id,
        mode=mode,
        external_effects=external_effects,
    )
    for key, expected in expected_scope.items():
        if payload.get(key) != expected:
            errors.append(f"{key} does not match requested execution scope")

    declared_scope = {
        key: payload.get(key)
        for key in (
            "authorization_id",
            "instruction_sha256",
            "repository",
            "technology_id",
            "mode",
            "external_effects",
        )
    }
    declared_scope_sha = payload.get("scope_sha256")
    declared_integrity_sha = scope_sha256(declared_scope)
    if not isinstance(declared_scope_sha, str) or declared_scope_sha != declared_integrity_sha:
        errors.append("scope_sha256 does not match the receipt's declared scope")
        declared_scope_sha = ""

    return OperatorScopeVerification(
        authorized=not errors,
        authorization_id=authorization_id,
        instruction_sha256=instruction_sha,
        scope_sha256=declared_scope_sha,
        errors=tuple(errors),
    )
