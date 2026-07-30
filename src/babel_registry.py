#!/usr/bin/env python3
"""Compatibility runtime registry sourced from registry/tower.yml.

The canonical registry is no longer hand-maintained in this file. This module
preserves the original ``BabelRegistryEngine`` API for agents/tests while using
TowerRegistry as the single source of truth.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

try:
    from tower_registry import TowerRegistry
except ImportError:  # pragma: no cover - package-style import fallback
    from .tower_registry import TowerRegistry


@dataclass(frozen=True)
class BabelLanguageSpec:
    name: str
    extension: str
    what: str
    where: str
    when: str
    why: str
    how: str
    technology_type: str
    advanced_evidence_state: str


def _build_registry() -> Dict[str, BabelLanguageSpec]:
    registry = TowerRegistry()
    built: Dict[str, BabelLanguageSpec] = {}
    for tech in registry.technologies:
        built[tech["id"]] = BabelLanguageSpec(
            name=tech["name"],
            extension=tech["extension"],
            what=tech["w4h"]["what"],
            where=tech["w4h"]["where"],
            when=tech["w4h"]["when"],
            why=tech["w4h"]["why"],
            how=tech["w4h"]["how"],
            technology_type=tech["technology_type"],
            advanced_evidence_state=tech["examples"]["advanced"]["evidence_state"],
        )
    return built


BABEL_REGISTRY: Dict[str, BabelLanguageSpec] = _build_registry()


class BabelRegistryEngine:
    def get_spec(self, lang_key: str) -> Dict[str, Any]:
        spec = BABEL_REGISTRY.get(lang_key.lower())
        if not spec:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {
            "name": spec.name,
            "extension": spec.extension,
            "what": spec.what,
            "where": spec.where,
            "when": spec.when,
            "why": spec.why,
            "how": spec.how,
            "technology_type": spec.technology_type,
            "advanced_evidence_state": spec.advanced_evidence_state,
            "status": "VALIDATED_W4H_SPEC",
            "ok": True,
        }


if __name__ == "__main__":
    print(f"Tower of Babel Registry Initialized: {len(BABEL_REGISTRY)} Technologies Registered.")
