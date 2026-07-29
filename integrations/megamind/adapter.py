"""Tower-to-Megamind technology selection adapter."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from tower.registry import TowerRegistry, load_registry


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


def _tokens(row: dict) -> set[str]:
    values: list[str] = [
        row["id"], row["name"], row["category"], row["artifact_type"],
        row["what"], row["where"], row["when"], row["why"], row["how"],
        *row.get("interfaces", []),
    ]
    return {
        token
        for value in values
        for token in value.casefold().replace("/", " ").replace("-", " ").split()
    }


def select_technologies(
    request: TechnologyRequest,
    registry: TowerRegistry | None = None,
) -> dict:
    registry = registry or load_registry()
    required = {value.casefold() for value in request.capabilities}
    preferred_interfaces = {value.casefold() for value in request.interfaces}
    minimum = _PROOF_ORDER.get(request.minimum_proof_class, 0)

    ranked: list[tuple[int, dict, list[str]]] = []
    for row in registry.technologies:
        proof = _PROOF_ORDER.get(row["proof_class"], 0)
        if proof < minimum:
            continue
        tokens = _tokens(row)
        capability_hits = sorted(value for value in required if value in tokens)
        interface_hits = sorted(
            value for value in preferred_interfaces
            if value in {item.casefold() for item in row.get("interfaces", [])}
        )
        score = len(capability_hits) * 10 + len(interface_hits) * 4 + proof
        if score:
            reasons = [f"capability:{value}" for value in capability_hits]
            reasons += [f"interface:{value}" for value in interface_hits]
            ranked.append((score, row, reasons))

    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))
    selected = ranked[:5]
    registry_sha = hashlib.sha256(registry.canonical_bytes()).hexdigest()
    agents = sorted({
        agent
        for _, row, _ in selected
        for agent in row["megamind"]["agents"]
    })
    pistons = sorted({
        piston
        for _, row, _ in selected
        for piston in row["megamind"]["pistons"]
    })
    return {
        "mission_id": request.mission_id,
        "technology_ids": [row["id"] for _, row, _ in selected],
        "agent_ids": agents,
        "piston_ids": pistons,
        "reasons": {
            row["id"]: reasons for _, row, reasons in selected
        },
        "tower_registry_sha256": registry_sha,
    }
