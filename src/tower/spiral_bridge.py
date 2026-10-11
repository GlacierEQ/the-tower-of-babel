"""Machine contract between Babel semantic optimization and Spiral control.

This module intentionally has no dependency on the standalone spiral-engine
package. It emits the neutral v2 contract that Spiral consumes, keeping the two
repositories independently deployable while preserving exact interoperability.
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Mapping

from .innovation import Intervention, RepoEvaluation, RoleResolution

BRIDGE_SCHEMA = "glaciereq.babel-spiral-bridge.v1"


def quality_state(evaluation: RepoEvaluation) -> dict[str, Any]:
    return {
        "overall": evaluation.overall_score,
        "critical_floor": evaluation.critical_floor,
        "dimensions": {
            axis.name: axis.score
            for axis in evaluation.quality
        },
        "fingerprint": evaluation.fingerprint,
    }


def _mid_term(near_term: float, far_term: float) -> float:
    return round((float(near_term) + float(far_term)) / 2.0, 6)


def intervention_contract(intervention: Intervention) -> dict[str, Any]:
    impact = intervention.impact
    return {
        "intervention_id": intervention.intervention_id,
        "title": intervention.title,
        "role": intervention.role,
        "candidate": intervention.language,
        "completion_signal": intervention.completion_signal,
        "impact": {
            "near_term": impact.near_term,
            "mid_term": _mid_term(impact.near_term, impact.far_term),
            "far_term": impact.far_term,
            "capability_gain": impact.capability_gain,
            "stability_gain": impact.stability_gain,
            "reversibility": impact.reversibility,
            "risk": impact.risk,
            "effort": impact.effort,
            "complexity_delta": impact.complexity_delta,
        },
    }


def promotion_evidence_template(
    role: RoleResolution | None,
    *,
    benchmark_gain: float = 0.0,
    interface_cost: float | None = None,
    behavioral_parity: bool = False,
    rollback_ready: bool = False,
    explicit_interface: bool = False,
) -> dict[str, Any]:
    if role is None:
        return {
            "required": False,
            "execution_ready": False,
            "behavioral_parity": False,
            "rollback_ready": False,
            "explicit_interface": False,
            "benchmark_gain": 0.0,
            "interface_cost": 0.0,
        }

    stable = role.stable_owner
    frontier = role.frontier_candidate
    required = frontier.language != stable.language
    return {
        "required": required,
        "execution_ready": frontier.execution_ready if required else stable.execution_ready,
        "behavioral_parity": bool(behavioral_parity),
        "rollback_ready": bool(rollback_ready),
        "explicit_interface": bool(explicit_interface),
        "benchmark_gain": round(float(benchmark_gain), 6),
        "interface_cost": round(
            float(role.interface_cost if interface_cost is None else interface_cost),
            6,
        ),
    }


def boundary_contract(role: RoleResolution, evaluation: RepoEvaluation) -> dict[str, Any]:
    supporting = [
        row for row in evaluation.files
        if role.role in row.roles
    ]
    owned = [
        row.path for row in supporting
        if row.language == role.stable_owner.language
    ]
    spill = [
        row.path for row in supporting
        if row.language and row.language != role.stable_owner.language
    ]
    advisory = [
        row.path for row in supporting
        if row.language is None
    ]
    frontier = role.frontier_candidate
    stable = role.stable_owner

    if frontier.language == stable.language:
        frontier_mode = "CURRENT_OWNER"
    elif frontier.execution_ready:
        frontier_mode = "EXPERIMENT_READY"
    else:
        frontier_mode = "PROOF_REQUIRED"

    return {
        "role": role.role,
        "demand": role.demand,
        "stable_owner": {
            "language": stable.language,
            "operational_score": stable.score,
            "intrinsic_fit": stable.intrinsic_fit,
            "evidence_state": stable.registry_evidence,
        },
        "frontier_specialist": {
            "language": frontier.language,
            "operational_score": frontier.score,
            "intrinsic_fit": frontier.intrinsic_fit,
            "evidence_state": frontier.registry_evidence,
            "execution_ready": frontier.execution_ready,
            "mode": frontier_mode,
        },
        "owned_paths": sorted(owned),
        "shared_or_spill_paths": sorted(spill),
        "advisory_paths": sorted(advisory),
        "recommendation": role.recommendation,
        "promotion_requirements": [
            "frontier toolchain/runtime is executable",
            "explicit versioned interface isolates the experiment",
            "behavioral parity or intentional behavior delta is tested",
            "rollback to stable owner is proven",
            "measured capability/stability gain exceeds interface cost",
            "no critical quality dimension regresses beyond tolerance",
        ] if frontier.language != stable.language else [],
        "regression_guards": [
            "correctness",
            "testing",
            "security",
            "semantic_placement",
        ],
    }


def build_bridge_contract(
    evaluation: RepoEvaluation,
    intervention: Intervention | None = None,
) -> dict[str, Any]:
    role_map = {row.role: row for row in evaluation.roles}
    role = role_map.get(intervention.role) if intervention and intervention.role else None

    payload: dict[str, Any] = {
        "schema": BRIDGE_SCHEMA,
        "repository": evaluation.repository,
        "target": evaluation.target,
        "complete": evaluation.complete,
        "quality_state": quality_state(evaluation),
        "boundaries": [
            boundary_contract(row, evaluation)
            for row in evaluation.roles
        ],
    }
    if intervention is not None:
        payload["intervention"] = intervention_contract(intervention)
        payload["promotion_evidence"] = promotion_evidence_template(role)
    else:
        payload["intervention"] = None
        payload["promotion_evidence"] = None
    return payload
