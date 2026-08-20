#!/usr/bin/env python3
"""Operational facade for the current selected Tower registry.

The facade deliberately refuses to turn a technology name into an execution
choice without an evidence threshold, capability match, and deterministic
selection receipt.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from tower.registry import load_registry, validate_registry


_EVIDENCE_RANK = {
    "illustrative": 0,
    "toolchain_gated": 1,
    "service_gated": 1,
    "hardware_gated": 1,
    "compiles": 2,
    "tested": 3,
    "benchmark": 4,
    "formally_verified": 4,
    "integrated": 5,
    "production_reference": 6,
}


def _validated_registry(repo_root=None):
    if repo_root is not None:
        target = Path(repo_root) / "registry" / "tower.yml"
        registry = load_registry(target)
    else:
        registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        raise RuntimeError("Invalid Tower registry: " + "; ".join(errors))
    return registry


def _tokens(row: dict) -> set[str]:
    values = [row.get("id", ""), row.get("name", ""), row.get("category", "")]
    values.extend(row.get("interfaces", []))
    return {str(value).casefold() for value in values if value}


class BabelRegistryEngine:
    def __init__(self, repo_root=None):
        self.registry = _validated_registry(repo_root=repo_root)

    def get_spec(self, lang_key: str):
        row = self.registry.by_id(lang_key)
        if row is None:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {**row, "status": "VALIDATED_W4H_SPEC", "ok": True}

    def select(
        self,
        required_capabilities: Iterable[str],
        preferred_interfaces: Iterable[str] = (),
        *,
        minimum_evidence_state: str = "tested",
        available_hardware: Iterable[str] = (),
    ) -> dict:
        """Select a verified technology and emit a deterministic decision receipt.

        Capability matching is intentionally conservative: every requested
        capability must match an ID, name, category, or declared interface.
        Gated hardware is admitted only when the caller supplies hardware proof.
        """
        required = tuple(sorted({str(x).strip().casefold() for x in required_capabilities if str(x).strip()}))
        preferred = tuple(sorted({str(x).strip().casefold() for x in preferred_interfaces if str(x).strip()}))
        if minimum_evidence_state not in _EVIDENCE_RANK:
            raise ValueError(f"unknown evidence state: {minimum_evidence_state}")
        minimum_rank = _EVIDENCE_RANK[minimum_evidence_state]
        hardware = {str(x).strip().casefold() for x in available_hardware if str(x).strip()}
        candidates = []
        excluded = []
        for row in sorted(self.registry.technologies, key=lambda item: item["id"]):
            state = row["evidence_state"]
            rank = _EVIDENCE_RANK.get(state, -1)
            tokens = _tokens(row)
            missing = [cap for cap in required if not any(cap in token for token in tokens)]
            if missing:
                excluded.append({"id": row["id"], "reason": "missing_capabilities", "missing": missing})
                continue
            if rank < minimum_rank:
                excluded.append({"id": row["id"], "reason": "insufficient_evidence", "evidence_state": state})
                continue
            gate = str(row.get("execution", {}).get("hardware_gate", ""))
            if gate and state in {"hardware_gated", "toolchain_gated", "service_gated"} and not hardware:
                excluded.append({"id": row["id"], "reason": "runtime_gate_unmet", "gate": gate})
                continue
            interface_hits = sum(1 for item in preferred if any(item in token for token in tokens))
            score = (rank * 100) + (interface_hits * 10) - len(row["id"])
            candidates.append({
                "id": row["id"],
                "name": row["name"],
                "evidence_state": state,
                "score": score,
                "interface_hits": interface_hits,
                "reason": "capabilities_and_evidence_match",
            })
        candidates.sort(key=lambda item: (-item["score"], item["id"]))
        registry_sha256 = hashlib.sha256(self.registry.canonical_bytes()).hexdigest()
        if not candidates:
            return {
                "ok": False,
                "status": "NO_VERIFIED_MATCH",
                "required_capabilities": list(required),
                "minimum_evidence_state": minimum_evidence_state,
                "registry_sha256": registry_sha256,
                "candidates": [],
                "excluded": excluded,
            }
        selected = candidates[0]
        return {
            "ok": True,
            "status": "SELECTED_VERIFIED_TECHNOLOGY",
            "selected": selected,
            "required_capabilities": list(required),
            "preferred_interfaces": list(preferred),
            "minimum_evidence_state": minimum_evidence_state,
            "registry_sha256": registry_sha256,
            "candidates": candidates,
            "excluded": excluded,
        }


_REGISTRY = _validated_registry()
BABEL_REGISTRY = {row["id"]: row for row in _REGISTRY.technologies}


if __name__ == "__main__":
    print(f"Tower of Babel Registry Initialized: {len(_REGISTRY.technologies)} Technologies Registered.")
