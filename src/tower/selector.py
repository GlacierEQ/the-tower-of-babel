"""Canonical function-to-technology authority for the Tower.

This is the Tower's central runtime decision: given a mission's required
functions, interfaces, and proof floor, choose the smallest governed set of
technologies that should own those functions *now*.

The selector is deliberately conservative:
- one technology is not rewarded merely for existing in the registry;
- gated or under-proven floors cannot satisfy a mission above their evidence;
- the smallest proven functional cover wins;
- preferred interfaces rank function owners but never create extra floors;
- every choice carries W4H placement and evidence state so callers can inspect
  not just *what* was selected, but *why/where/when/how* it belongs.
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

# Canonical functional vocabulary. These are not hard-coded technology answers;
# they expand user/system intent into terms that are matched against the W4H,
# category, artifact type, and interface vocabulary of every governed floor.
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


def _capability_terms(capability: str) -> set[str]:
    normalized = " ".join(sorted(_words(capability)))
    direct = _CAPABILITY_ALIASES.get(capability.casefold().strip())
    if direct:
        return direct
    for alias, terms in _CAPABILITY_ALIASES.items():
        alias_words = _words(alias)
        requested_words = _words(capability)
        if alias_words and alias_words <= requested_words:
            return terms | requested_words
    return _words(normalized)


def _capability_score(capability: str, tokens: set[str]) -> int:
    requested = _capability_terms(capability)
    if not requested:
        return 0
    hits = {
        candidate
        for candidate in requested
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
    if len(_words(capability)) == 1 and hits:
        return 100
    minimum_hits = 2 if len(requested) >= 4 else 1
    return len(hits) if len(hits) >= minimum_hits else 0


def select_technologies(
    request: TechnologyRequest,
    registry: TowerRegistry | None = None,
) -> dict[str, Any]:
    """Select the smallest proven technology set covering all mission functions."""
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

    ranked: list[tuple[int, dict[str, Any], list[str], set[str]]] = []
    gated_candidates: dict[str, str] = {}
    under_proven_candidates: dict[str, str] = {}

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
        if not capability_hits:
            continue

        evidence_state = str(row.get("evidence_state", ""))
        if evidence_state in _GATED_STATES:
            gated_candidates[row["id"]] = evidence_state
            continue

        proof = _PROOF_ORDER[proof_name]
        if proof < minimum:
            under_proven_candidates[row["id"]] = proof_name
            continue

        functional_score = sum(capability_scores[value] for value in capability_hits)
        score = functional_score * 10 + len(interface_hits) * 4 + proof
        reasons = [f"function:{value}" for value in sorted(capability_hits)]
        reasons += [f"interface:{value}" for value in sorted(interface_hits)]
        ranked.append((score, row, reasons, capability_hits))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    selected: list[tuple[int, dict[str, Any], list[str], set[str]]] = []
    uncovered = set(required)
    remaining = list(ranked)

    while uncovered and remaining:
        remaining.sort(
            key=lambda item: (
                -len(item[3] & uncovered),
                -sum(_capability_score(value, _tokens(item[1])) for value in item[3] & uncovered),
                -item[0],
                item[1]["id"],
            )
        )
        candidate = remaining.pop(0)
        if not (candidate[3] & uncovered):
            break
        selected.append(candidate)
        uncovered -= candidate[3]

    registry_sha = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    agents = sorted({
        agent
        for _, row, _, _ in selected
        for agent in row.get("megamind", {}).get("agents", [])
        if isinstance(agent, str)
    })
    pistons = sorted({
        piston
        for _, row, _, _ in selected
        for piston in row.get("megamind", {}).get("pistons", [])
        if isinstance(piston, str)
    })

    placements = {
        row["id"]: {
            "what": row.get("what", ""),
            "where": row.get("where", ""),
            "when": row.get("when", ""),
            "why": row.get("why", ""),
            "how": row.get("how", ""),
            "evidence_state": row.get("evidence_state", ""),
            "proof_class": row.get("proof_class", ""),
        }
        for _, row, _, _ in selected
    } if not uncovered else {}

    return {
        "schema": "glaciereq.function-technology-selection.v1",
        "authority": "tower.selector",
        "mission_id": mission_id,
        "technology_ids": [row["id"] for _, row, _, _ in selected] if not uncovered else [],
        "agent_ids": agents if not uncovered else [],
        "piston_ids": pistons if not uncovered else [],
        "reasons": {row["id"]: reasons for _, row, reasons, _ in selected} if not uncovered else {},
        "placements": placements,
        "required_capabilities": sorted(required),
        "preferred_interfaces": sorted(preferred_interfaces),
        "minimum_proof_class": minimum_name,
        "unmatched_capabilities": sorted(uncovered),
        "gated_candidates": dict(sorted(gated_candidates.items())),
        "under_proven_candidates": dict(sorted(under_proven_candidates.items())),
        "tower_registry_sha256": registry_sha,
    }
