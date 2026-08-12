"""Canonical function-to-technology authority for the Tower.

The Tower's central runtime decision is not "use the fewest languages". Given a
mission, it first guarantees functional coverage and then keeps composing proven
specialists while each contributes positive, distinct system value.

A technology can earn a place through function ownership or through a verified
benefit such as memory safety, model portability, interoperability, zero-copy
access, hardware acceleration, formal proof, fault tolerance, or compression.
Coverage is the floor; evidence-qualified specialization is the optimization.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from .registry import TowerRegistry, load_registry


@dataclass(frozen=True)
class TechnologyRequest:
    mission_id: str
    capabilities: tuple[str, ...]
    interfaces: tuple[str, ...] = ()
    minimum_proof_class: str = ""
    desired_benefits: tuple[str, ...] = ()


_PROOF_ORDER = {
    "illustrative": 0,
    "compile": 1,
    "behavioral": 2,
    "benchmark": 3,
    "hardware": 3,
    "integration": 4,
    "formal": 5,
}
_GATED_STATES = {"hardware_gated", "toolchain_gated", "service_gated"}

_CAPABILITY_ALIASES = {
    "coding": {"code", "coding", "compiler", "program", "software", "application", "development"},
    "evidence": {"evidence", "proof", "receipt", "audit", "verification", "integrity", "provenance"},
    "tool": {"tool", "tooling", "toolchain", "automation", "orchestration", "cli", "gateway"},
    "cross-language contract": {"schema", "contract", "message", "rpc", "telemetry", "protobuf", "binary"},
    "typed messages": {"schema", "message", "contract", "protobuf", "binary"},
    "portable model graph": {"model", "graph", "inference", "runtime", "onnx", "backend"},
    "model interchange": {"model", "graph", "exchange", "onnx", "runtime"},
    "data-oriented memory": {"data", "layout", "allocator", "memory", "simd", "native"},
    "memory-safe native": {"memory", "safe", "ownership", "native", "concurrency", "rust"},
    "zero-copy serialization": {"zero", "copy", "buffer", "serialization", "flatbuffers"},
    "quantization compression": {"quantization", "compression", "tensor", "memory", "throughput", "benchmark"},
    "gpu kernel": {"gpu", "kernel", "cuda", "triton", "accelerator"},
    "sandboxed execution": {"sandbox", "capability", "portable", "wasm", "webassembly"},
}

_BENEFIT_ALIASES = {
    "performance": {"performance", "latency", "throughput", "simd", "vectorized", "kernel", "benchmark"},
    "memory_efficiency": {"memory", "allocation", "allocator", "compact", "zero", "copy", "buffer"},
    "memory_safety": {"memory", "safe", "safety", "ownership", "borrow", "race", "concurrency"},
    "data_layout_control": {"layout", "allocator", "data", "simd", "struct", "array", "native"},
    "interoperability": {"interop", "interoperability", "schema", "contract", "rpc", "protobuf", "abi", "interface"},
    "model_portability": {"model", "graph", "onnx", "runtime", "backend", "portable", "inference"},
    "zero_copy_access": {"zero", "copy", "buffer", "direct", "allocation", "flatbuffers"},
    "hardware_acceleration": {"gpu", "accelerator", "cuda", "triton", "tensor", "hardware", "kernel"},
    "compression": {"compression", "quantization", "compact", "memory", "tensor", "benchmark"},
    "sandboxing": {"sandbox", "capability", "isolation", "wasm", "webassembly", "untrusted"},
    "formal_verification": {"formal", "proof", "theorem", "verified", "invariant", "lean", "coq", "agda"},
    "fault_tolerance": {"fault", "supervision", "resilience", "isolation", "recovery", "distributed"},
    "deployment_portability": {"portable", "cross", "target", "static", "deployment", "wasm", "zig"},
    "developer_velocity": {"rapid", "iteration", "ecosystem", "readable", "automation", "orchestration", "python"},
}

_BENEFIT_MIN_PROOF = {
    "performance": "benchmark",
    "memory_efficiency": "benchmark",
    "memory_safety": "behavioral",
    "data_layout_control": "behavioral",
    "interoperability": "behavioral",
    "model_portability": "behavioral",
    "zero_copy_access": "behavioral",
    "hardware_acceleration": "hardware",
    "compression": "benchmark",
    "sandboxing": "behavioral",
    "formal_verification": "formal",
    "fault_tolerance": "behavioral",
    "deployment_portability": "behavioral",
    "developer_velocity": "behavioral",
}


def _words(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.casefold()) if token}


def _tokens(row: dict[str, Any]) -> set[str]:
    values: list[str] = [
        str(row.get("id", "")),
        str(row.get("name", "")),
        str(row.get("category", "")),
        str(row.get("artifact_type", "")),
        str(row.get("what", "")),
        str(row.get("where", "")),
        str(row.get("when", "")),
        str(row.get("why", "")),
        str(row.get("how", "")),
        str(row.get("evidence_state", "")),
        str(row.get("proof_class", "")),
        *[str(item) for item in row.get("interfaces", []) if isinstance(item, str)],
    ]
    return {token for value in values for token in _words(value)}


def _match_score(terms: set[str], tokens: set[str]) -> int:
    if not terms:
        return 0
    hits = {
        candidate
        for candidate in terms
        if candidate in tokens
        or (
            len(candidate) >= 4
            and any(
                token.startswith(candidate) or candidate.startswith(token)
                for token in tokens
                if len(token) >= 4
            )
        )
    }
    minimum_hits = 2 if len(terms) >= 4 else 1
    return len(hits) if len(hits) >= minimum_hits else 0


def _capability_terms(capability: str) -> set[str]:
    direct = _CAPABILITY_ALIASES.get(capability.casefold().strip())
    if direct:
        return direct
    requested_words = _words(capability)
    for alias, terms in _CAPABILITY_ALIASES.items():
        if _words(alias) <= requested_words:
            return terms | requested_words
    return requested_words


def _capability_score(capability: str, tokens: set[str]) -> int:
    score = _match_score(_capability_terms(capability), tokens)
    if len(_words(capability)) == 1 and score:
        return 100
    return score


def _normalize_benefit(value: str) -> str:
    return value.casefold().strip().replace("-", "_").replace(" ", "_")


def _infer_benefits(capabilities: set[str], interfaces: set[str]) -> set[str]:
    inferred: set[str] = set()
    combined = " ".join(sorted(capabilities | interfaces))
    words = _words(combined)
    inference_rules = {
        "interoperability": {"contract", "message", "rpc", "telemetry", "protobuf", "interface"},
        "model_portability": {"model", "onnx", "inference", "backend", "graph"},
        "memory_safety": {"memory", "safe", "ownership", "concurrency"},
        "data_layout_control": {"layout", "allocator", "simd"},
        "zero_copy_access": {"zero", "copy", "buffer", "flatbuffers"},
        "compression": {"compression", "quantization", "quantizer"},
        "hardware_acceleration": {"gpu", "cuda", "triton", "accelerator", "kernel"},
        "sandboxing": {"sandbox", "wasm", "webassembly", "untrusted"},
        "formal_verification": {"formal", "proof", "theorem"},
        "fault_tolerance": {"fault", "supervision", "resilience"},
        "deployment_portability": {"portable", "cross", "deployment"},
    }
    for benefit, trigger_terms in inference_rules.items():
        if words & trigger_terms:
            inferred.add(benefit)
    return inferred


def _benefit_score(benefit: str, row: dict[str, Any], tokens: set[str]) -> int:
    terms = _BENEFIT_ALIASES.get(benefit)
    if not terms:
        return 0
    score = _match_score(terms, tokens)
    technology_id = str(row.get("id", "")).casefold()
    if technology_id in terms:
        score += 5
    return score


def _role_signature(row: dict[str, Any]) -> tuple[str, str]:
    return (str(row.get("category", "")), str(row.get("artifact_type", "")))


def select_technologies(
    request: TechnologyRequest,
    registry: TowerRegistry | None = None,
) -> dict[str, Any]:
    """Compose function owners plus every proven specialist with positive distinct benefit."""
    registry = registry or load_registry()
    mission_id = request.mission_id.strip()
    if not mission_id:
        raise ValueError("mission_id must be a non-empty string")
    minimum_name = request.minimum_proof_class or "illustrative"
    if minimum_name not in _PROOF_ORDER:
        raise ValueError(f"unknown minimum proof class: {minimum_name}")
    minimum = _PROOF_ORDER[minimum_name]

    required = {value.casefold().strip() for value in request.capabilities if value.strip()}
    if not required:
        raise ValueError("at least one required capability is required")
    preferred_interfaces = {value.casefold().strip() for value in request.interfaces if value.strip()}
    explicit_benefits = {_normalize_benefit(value) for value in request.desired_benefits if value.strip()}
    unknown_benefits = sorted(explicit_benefits - set(_BENEFIT_ALIASES))
    if unknown_benefits:
        raise ValueError("unknown desired benefits: " + ", ".join(unknown_benefits))
    desired_benefits = explicit_benefits | _infer_benefits(required, preferred_interfaces)

    eligible: list[dict[str, Any]] = []
    gated_candidates: dict[str, str] = {}
    under_proven_candidates: dict[str, str] = {}
    benefit_blockers: dict[str, list[str]] = {}

    for row in registry.technologies:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            continue
        proof_name = row.get("proof_class")
        if proof_name not in _PROOF_ORDER:
            raise ValueError(f"technology {row['id']} has unknown proof class: {proof_name}")

        tokens = _tokens(row)
        capability_scores = {value: _capability_score(value, tokens) for value in required}
        capability_hits = {value for value, score in capability_scores.items() if score > 0}
        interfaces = {item.casefold() for item in row.get("interfaces", []) if isinstance(item, str)}
        interface_hits = preferred_interfaces & interfaces
        direct_interface_floor = row["id"].casefold() in preferred_interfaces
        benefit_scores = {
            benefit: _benefit_score(benefit, row, tokens)
            for benefit in desired_benefits
        }
        raw_benefit_hits = {benefit for benefit, score in benefit_scores.items() if score > 0}

        if not capability_hits and not interface_hits and not direct_interface_floor and not raw_benefit_hits:
            continue

        evidence_state = str(row.get("evidence_state", ""))
        if evidence_state in _GATED_STATES:
            gated_candidates[row["id"]] = evidence_state
            continue

        proof = _PROOF_ORDER[proof_name]
        if proof < minimum:
            under_proven_candidates[row["id"]] = proof_name
            continue

        qualified_benefits: set[str] = set()
        blocked_benefits: list[str] = []
        for benefit in raw_benefit_hits:
            floor_name = _BENEFIT_MIN_PROOF[benefit]
            if proof >= _PROOF_ORDER[floor_name]:
                qualified_benefits.add(benefit)
            else:
                blocked_benefits.append(f"{benefit}:needs_{floor_name}:has_{proof_name}")
        if blocked_benefits:
            benefit_blockers[row["id"]] = sorted(blocked_benefits)

        functional_score = sum(capability_scores[value] for value in capability_hits)
        benefit_score = sum(benefit_scores[value] for value in qualified_benefits)
        interface_score = len(interface_hits) * 4 + (8 if direct_interface_floor else 0)
        total_score = functional_score * 10 + benefit_score * 6 + interface_score + proof

        eligible.append(
            {
                "score": total_score,
                "row": row,
                "capability_hits": capability_hits,
                "qualified_benefits": qualified_benefits,
                "interface_hits": interface_hits,
                "direct_interface_floor": direct_interface_floor,
            }
        )

    # Phase 1: guarantee every required function has a proven owner.
    selected: list[dict[str, Any]] = []
    uncovered = set(required)
    remaining = list(eligible)
    while uncovered and remaining:
        remaining.sort(
            key=lambda item: (
                -len(item["capability_hits"] & uncovered),
                -item["score"],
                item["row"]["id"],
            )
        )
        candidate = remaining.pop(0)
        if not (candidate["capability_hits"] & uncovered):
            break
        selected.append(candidate)
        uncovered -= candidate["capability_hits"]

    # Phase 2: additive specialization. Coverage does NOT stop selection.
    # Add a proven technology when it contributes a requested/inferred benefit in a
    # distinct engineering role, or is itself the explicitly preferred interface floor.
    if not uncovered:
        selected_ids = {item["row"]["id"] for item in selected}
        represented: dict[str, set[tuple[str, str]]] = {}
        for item in selected:
            role = _role_signature(item["row"])
            for benefit in item["qualified_benefits"]:
                represented.setdefault(benefit, set()).add(role)

        specialists = [item for item in eligible if item["row"]["id"] not in selected_ids]
        specialists.sort(key=lambda item: (-item["score"], item["row"]["id"]))
        for candidate in specialists:
            row = candidate["row"]
            role = _role_signature(row)
            new_benefits = {
                benefit
                for benefit in candidate["qualified_benefits"]
                if role not in represented.get(benefit, set())
            }
            direct_interface_value = candidate["direct_interface_floor"]
            if not new_benefits and not direct_interface_value:
                continue
            selected.append(candidate)
            selected_ids.add(row["id"])
            for benefit in new_benefits:
                represented.setdefault(benefit, set()).add(role)

    registry_sha = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    agents = sorted({
        agent
        for item in selected
        for agent in item["row"].get("megamind", {}).get("agents", [])
        if isinstance(agent, str)
    })
    pistons = sorted({
        piston
        for item in selected
        for piston in item["row"].get("megamind", {}).get("pistons", [])
        if isinstance(piston, str)
    })

    reasons: dict[str, list[str]] = {}
    placements: dict[str, dict[str, Any]] = {}
    benefit_contributions: dict[str, list[str]] = {}
    for item in selected:
        row = item["row"]
        technology_id = row["id"]
        entry_reasons = [f"function:{value}" for value in sorted(item["capability_hits"])]
        entry_reasons += [f"benefit:{value}" for value in sorted(item["qualified_benefits"])]
        entry_reasons += [f"interface:{value}" for value in sorted(item["interface_hits"])]
        if item["direct_interface_floor"]:
            entry_reasons.append(f"interface-floor:{technology_id}")
        reasons[technology_id] = entry_reasons
        benefit_contributions[technology_id] = sorted(item["qualified_benefits"])
        placements[technology_id] = {
            "what": row.get("what", ""),
            "where": row.get("where", ""),
            "when": row.get("when", ""),
            "why": row.get("why", ""),
            "how": row.get("how", ""),
            "evidence_state": row.get("evidence_state", ""),
            "proof_class": row.get("proof_class", ""),
            "category": row.get("category", ""),
            "artifact_type": row.get("artifact_type", ""),
        }

    satisfied_benefits = sorted({benefit for values in benefit_contributions.values() for benefit in values})
    unmet_benefits = sorted(desired_benefits - set(satisfied_benefits))

    return {
        "schema": "glaciereq.function-technology-selection.v2",
        "authority": "tower.selector",
        "optimization_goal": "maximize_verified_system_advantage_without_redundant_responsibility",
        "mission_id": mission_id,
        "technology_ids": [item["row"]["id"] for item in selected] if not uncovered else [],
        "agent_ids": agents if not uncovered else [],
        "piston_ids": pistons if not uncovered else [],
        "reasons": reasons if not uncovered else {},
        "placements": placements if not uncovered else {},
        "benefit_contributions": benefit_contributions if not uncovered else {},
        "required_capabilities": sorted(required),
        "preferred_interfaces": sorted(preferred_interfaces),
        "desired_benefits": sorted(desired_benefits),
        "satisfied_benefits": satisfied_benefits if not uncovered else [],
        "unmet_benefits": unmet_benefits if not uncovered else sorted(desired_benefits),
        "minimum_proof_class": minimum_name,
        "unmatched_capabilities": sorted(uncovered),
        "gated_candidates": dict(sorted(gated_candidates.items())),
        "under_proven_candidates": dict(sorted(under_proven_candidates.items())),
        "benefit_blockers": dict(sorted(benefit_blockers.items())),
        "tower_registry_sha256": registry_sha,
    }
