"""Capability activation and execution for Tower of Babel.

Governance shapes power; it must not collapse usable capability into a
planning-only denial. Tower may inspect, compose, execute, and promote within
its technical evidence contract.

Project direction belongs to the Operator. Reversible external work may execute
within the current Operator-directed mission without manufacturing a second
approval layer. Materially irreversible or unclassified external effects retain
an exact Operator-scope authorization boundary. Evidence requirements still
control factual claimability and promotion state.
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


class EffectRisk(str, Enum):
    NONE = "none"
    REVERSIBLE = "reversible"
    MATERIAL_IRREVERSIBLE = "materially-irreversible"
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class ActivationDecision:
    technology_id: str
    requested: ActivationMode
    allowed: bool
    effective_mode: ActivationMode
    reason: str
    effect_risk: EffectRisk = EffectRisk.NONE
    operator_scope_required: bool = False
    required_proof: tuple[str, ...] = ()
    blocked_capabilities: tuple[str, ...] = ()


def _text(row: Mapping[str, Any], key: str) -> str:
    value = row.get(key)
    return value.strip() if isinstance(value, str) else ""


def _resolve_effect_risk(
    *,
    external_effects: bool,
    effect_risk: EffectRisk | str | None,
) -> EffectRisk:
    if not external_effects:
        if effect_risk is None:
            return EffectRisk.NONE
        parsed = effect_risk if isinstance(effect_risk, EffectRisk) else EffectRisk(effect_risk)
        if parsed is EffectRisk.NONE:
            return parsed
        raise ValueError("effect_risk requires external_effects=true")

    if effect_risk is None:
        return EffectRisk.UNCLASSIFIED

    parsed = effect_risk if isinstance(effect_risk, EffectRisk) else EffectRisk(effect_risk)
    if parsed is EffectRisk.NONE:
        raise ValueError("external effects cannot use effect_risk=none")
    return parsed


def resolve_activation(
    technology: Mapping[str, Any],
    requested: ActivationMode | str,
    *,
    external_effects: bool = False,
    effect_risk: EffectRisk | str | None = None,
    operator_scope_authorized: bool = False,
) -> ActivationDecision:
    """Resolve capability without inventing a second authority layer.

    operator_scope_authorized answers only whether the current Operator
    instruction covers an external effect that actually requires a separate
    authorization boundary. It does not bypass technical prerequisites or
    evidence requirements.
    """
    technology_id = _text(technology, "id") or "UNIDENTIFIED_TECHNOLOGY"
    try:
        mode = requested if isinstance(requested, ActivationMode) else ActivationMode(requested)
    except ValueError as exc:
        raise ValueError(f"unknown activation mode: {requested}") from exc

    if mode is ActivationMode.INSPECT:
        return ActivationDecision(
            technology_id,
            mode,
            True,
            mode,
            "inspection-is-always-available",
        )

    try:
        risk = _resolve_effect_risk(
            external_effects=external_effects,
            effect_risk=effect_risk,
        )
    except ValueError as exc:
        raise ValueError(f"invalid effect risk: {effect_risk}") from exc

    operator_scope_required = external_effects and risk in {
        EffectRisk.MATERIAL_IRREVERSIBLE,
        EffectRisk.UNCLASSIFIED,
    }
    if operator_scope_required and not operator_scope_authorized:
        reason = (
            "materially-irreversible-external-effects-require-operator-scope-authorization"
            if risk is EffectRisk.MATERIAL_IRREVERSIBLE
            else "unclassified-external-effects-require-operator-scope-authorization"
        )
        return ActivationDecision(
            technology_id,
            mode,
            False,
            ActivationMode.INSPECT,
            reason,
            effect_risk=risk,
            operator_scope_required=True,
            blocked_capabilities=("external-effects",),
        )

    if mode is ActivationMode.COMPOSE:
        interfaces = technology.get("interfaces")
        if isinstance(interfaces, list) and interfaces:
            return ActivationDecision(
                technology_id,
                mode,
                True,
                mode,
                "declared-interface-boundary-present",
                effect_risk=risk,
                operator_scope_required=operator_scope_required,
            )
        return ActivationDecision(
            technology_id,
            mode,
            False,
            ActivationMode.INSPECT,
            "composition-requires-declared-interfaces",
            effect_risk=risk,
            operator_scope_required=operator_scope_required,
            required_proof=("interfaces",),
        )

    toolchain = technology.get("toolchain")
    execution = technology.get("execution")
    declared_tool = isinstance(toolchain, dict) and bool(_text(toolchain, "tool"))
    declared_execution = isinstance(execution, dict) and bool(_text(execution, "ci_tier"))

    if mode is ActivationMode.EXECUTE:
        if declared_tool and declared_execution:
            if not external_effects:
                reason = "declared-execution-boundary-present"
            elif risk is EffectRisk.REVERSIBLE:
                reason = "reversible-external-execution-boundary-present"
            elif risk is EffectRisk.MATERIAL_IRREVERSIBLE:
                reason = "operator-scoped-materially-irreversible-execution-boundary-present"
            else:
                reason = "operator-scoped-unclassified-external-execution-boundary-present"
            return ActivationDecision(
                technology_id,
                mode,
                True,
                mode,
                reason,
                effect_risk=risk,
                operator_scope_required=operator_scope_required,
            )
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
            effect_risk=risk,
            operator_scope_required=operator_scope_required,
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
            technology_id,
            mode,
            True,
            mode,
            "promotion-proof-class-present",
            effect_risk=risk,
            operator_scope_required=operator_scope_required,
        )

    return ActivationDecision(
        technology_id,
        mode,
        False,
        ActivationMode.EXECUTE if declared_tool and declared_execution else ActivationMode.INSPECT,
        "promotion-requires-earned-evidence",
        effect_risk=risk,
        operator_scope_required=operator_scope_required,
        required_proof=("evidence_state", "proof_class"),
    )


def activate_execution(
    technology: Mapping[str, Any],
    *,
    external_effects: bool = False,
    effect_risk: EffectRisk | str | None = None,
    operator_scope_authorized: bool = False,
) -> dict[str, Any]:
    decision = resolve_activation(
        technology,
        ActivationMode.EXECUTE,
        external_effects=external_effects,
        effect_risk=effect_risk,
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
            "effect_risk": decision.effect_risk.value,
            "operator_scope_required": decision.operator_scope_required,
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
                "effect_risk": decision.effect_risk.value,
                "operator_scope_required": decision.operator_scope_required,
                "required_proof": list(decision.required_proof),
                "blocked_capabilities": list(decision.blocked_capabilities),
            }
            for decision in decisions
        ],
    }
