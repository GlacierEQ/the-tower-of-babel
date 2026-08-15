"""Capability activation and execution for Tower of Babel.

Governance shapes power; it must not collapse every usable capability into a
planning-only denial. This module resolves a capability and, for a declared
local execution boundary, hands it to Tower's existing build engine.

External effects, provider access, promotion, and destructive actions remain
separate boundaries. Local declared build/test execution is real execution.
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
) -> ActivationDecision:
    """Resolve the strongest capability available for one technology."""
    technology_id = _text(technology, "id") or "UNIDENTIFIED_TECHNOLOGY"
    try:
        mode = requested if isinstance(requested, ActivationMode) else ActivationMode(requested)
    except ValueError as exc:
        raise ValueError(f"unknown activation mode: {requested}") from exc

    if mode is ActivationMode.INSPECT:
        return ActivationDecision(technology_id, mode, True, mode, "inspection-is-always-available")
    if external_effects:
        return ActivationDecision(
            technology_id, mode, False, ActivationMode.INSPECT,
            "external-effects-require-separate-mutation-approval",
            blocked_capabilities=("external-effects",),
        )
    if mode is ActivationMode.COMPOSE:
        interfaces = technology.get("interfaces")
        if isinstance(interfaces, list) and interfaces:
            return ActivationDecision(technology_id, mode, True, mode, "declared-interface-boundary-present")
        return ActivationDecision(technology_id, mode, False, ActivationMode.INSPECT, "composition-requires-declared-interfaces", ("interfaces",))

    toolchain = technology.get("toolchain")
    execution = technology.get("execution")
    declared_tool = isinstance(toolchain, dict) and bool(_text(toolchain, "tool"))
    declared_execution = isinstance(execution, dict) and bool(_text(execution, "ci_tier"))
    if mode is ActivationMode.EXECUTE:
        if declared_tool and declared_execution:
            return ActivationDecision(technology_id, mode, True, mode, "declared-execution-boundary-present")
        missing = tuple(name for name, present in (("toolchain.tool", declared_tool), ("execution.ci_tier", declared_execution)) if not present)
        return ActivationDecision(technology_id, mode, False, ActivationMode.INSPECT, "execution-boundary-incomplete", missing)

    evidence_state = _text(technology, "evidence_state")
    proof_class = _text(technology, "proof_class")
    promotable_states = {"tested", "benchmark", "integrated", "production_reference", "formally_verified"}
    if evidence_state in promotable_states and proof_class:
        return ActivationDecision(technology_id, mode, True, mode, "promotion-proof-class-present")
    return ActivationDecision(
        technology_id, mode, False,
        ActivationMode.EXECUTE if declared_tool and declared_execution else ActivationMode.INSPECT,
        "promotion-requires-earned-evidence", ("evidence_state", "proof_class"),
    )


def activate_execution(technology: Mapping[str, Any], *, external_effects: bool = False) -> dict[str, Any]:
    """Actually execute the declared local build/test floor.

    This is the missing power path: activation is not merely a report. Once the
    technology declares a toolchain and execution tier, the existing governed
    ``build_floor`` engine runs it. Its argv allowlist, timeout, dependency,
    hardware, and service boundaries still apply. No provider or mutation
    authority is created here.
    """
    decision = resolve_activation(technology, ActivationMode.EXECUTE, external_effects=external_effects)
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
            "governance": "shaping-and-audit",
        },
    }


def activation_surface(technology: Mapping[str, Any]) -> dict[str, Any]:
    """Return capability visibility without executing anything."""
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
