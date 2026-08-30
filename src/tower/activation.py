"""Capability activation and execution for Tower of Babel.

Governance shapes power; it must not collapse usable capability into a
planning-only denial. Tower may inspect, compose, execute, and promote within
its technical evidence contract.

Project direction belongs to the Operator. External effects therefore require
Operator-scoped authorization, not a second model/governance approval. Evidence
requirements still control factual claimability and promotion state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class ActivationMode(str, Enum):
    INSPECT = "inspect"
    COMPOSE = "compose"
    EXECUTE = "execute"
    PROMOTE = "promote"


@dataclass(frozen=True)
class ActivationDecision:
    technology_id: str
    requested: ActivationMode
    allowed: bool
    effective_mode: ActivationMode
    reason: str
    required_proof: tuple[str, ...] = ()
    blocked_capabilities: tuple[str, ...] = ()


def _text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    return value.strip() if isinstance(value, str) else ""


def resolve_activation(
    technology: Mapping[str, Any],
    requested: ActivationMode | str,
    *,
    external_effects: bool = False,
    operator_scope_authorized: bool = False,
) -> ActivationDecision:
    """Resolve capability without inventing a second authority layer.

    operator_scope_authorized answers only whether the current Operator
    instruction covers the requested external effect. It does not bypass
    technical prerequisites or evidence requirements.
    """
    technology_id = _text(technology, "id") or "UNIDENTIFIED_TECHNOLOGY"
    try:
        mode = requested if isinstance(requested, ActivationMode) else ActivationMode(requested)
    except ValueError as exc:
        raise ValueError(f"unknown activation mode: {requested}") from exc

    if mode is ActivationMode.INSPECT:
        return ActivationDecision(
            technology_id, mode, True, mode, "inspection-is-always-available"
        )

    if external_effects and not operator_scope_authorized:
        return ActivationDecision(
            technology_id,
            mode,
            False,
            ActivationMode.INSPECT,
            "external-effects-require-operator-scope-authorization",
            blocked_capabilities=("external-effects",),
        )

    if mode is ActivationMode.COMPOSE:
        interfaces = technology.get("interfaces")
        if isinstance(interfaces, list) and interfaces:
            return ActivationDecision(
                technology_id, mode, True, mode, "declared-interface-boundary-present"
            )
        return ActivationDecision(
            technology_id,
            mode,
            False,
            ActivationMode.INSPECT,
            "composition-requires-declared-interfaces",
            required_proof=("interfaces",),
        )

    toolchain = technology.get("toolchain")
    execution = technology.get("execution")
    declared_tool = isinstance(toolchain, dict) and bool(_text(toolchain, "tool"))
    declared_execution = isinstance(execution, dict) and bool(_text(execution, "ci_tier"))

    if mode is ActivationMode.EXECUTE:
        if declared_tool and declared_execution:
            reason = (
                "operator-scoped-external-execution-boundary-present"
                if external_effects
                else "declared-execution-boundary-present"
            )
            return ActivationDecision(technology_id, mode, True, mode, reason)
        missing = tuple(
            name
            for name, present in (
                ("toolchain.tool", declared_tool),
                ("execution.ci_tier", declared_execution),
            )
            if not present
        )
        return ActivationDecision(
            technology_id,
            mode,
            False,
            ActivationMode.INSPECT,
            "execution-boundary-incomplete",
            required_proof=missing,
        )

    evidence_state = _text(technology, "evidence_state")
    proof_class = _text(technology, "proof_class")
    if (
        evidence_state
        in {"tested", "benchmark", "integrated", "production_reference", "formally_verified"}
        and proof_class
    ):
        return ActivationDecision(
            technology_id, mode, True, mode, "promotion-proof-class-present"
        )

    return ActivationDecision(
        technology_id,
        mode,
        False,
        ActivationMode.EXECUTE if declared_tool and declared_execution else ActivationMode.INSPECT,
        "promotion-requires-earned-evidence",
        required_proof=("evidence_state", "proof_class"),
    )


def activate_execution(
    technology: Mapping[str, Any],
    *,
    external_effects: bool = False,
    operator_scope_authorized: bool = False,
) -> dict[str, Any]:
    decision = resolve_activation(
        technology,
        ActivationMode.EXECUTE,
        external_effects=external_effects,
        operator_scope_authorized=operator_scope_authorized,
    )
    if not decision.allowed:
        return {
            "technology_id": decision.technology_id,
            "status": "ACTIVATION_BLOCKED",
            "decision": decision,
        }

    from .build import build_floor

    result = build_floor(dict(technology))
    return {
        **result,
        "activation": {
            "mode": ActivationMode.EXECUTE.value,
            "reason": decision.reason,
            "governance": "technical-evidence-and-audit",
            "project_direction_authority": "operator",
        },
    }


def activation_surface(technology: Mapping[str, Any]) -> dict[str, Any]:
    decisions = [resolve_activation(technology, mode) for mode in ActivationMode]
    return {
        "technology_id": _text(technology, "id") or "UNIDENTIFIED_TECHNOLOGY",
        "available": [decision.effective_mode.value for decision in decisions if decision.allowed],
        "decisions": [
            {
                "requested": decision.requested.value,
                "allowed": decision.allowed,
                "effective_mode": decision.effective_mode.value,
                "reason": decision.reason,
                "required_proof": list(decision.required_proof),
                "blocked_capabilities": list(decision.blocked_capabilities),
            }
            for decision in decisions
        ],
    }
