from __future__ import annotations

import re
from pathlib import Path

from tower.registry import REPO_ROOT, load_registry, validate_registry


def test_every_floor_has_one_semantic_claim_contract() -> None:
    registry = load_registry()
    assert validate_registry(registry) == []
    ids = {tech["id"] for tech in registry.technologies}
    assert set(registry.claim_contracts) == ids
    assert len(ids) == len(registry.technologies)


def test_claim_contract_source_assertions_match_advanced_exhibits() -> None:
    registry = load_registry()
    for tech in registry.technologies:
        contract = registry.claim_contract_for(tech["id"])
        assert contract is not None
        text = (REPO_ROOT / tech["advanced_example"]).read_text(encoding="utf-8")
        for pattern in contract["required_source_patterns"]:
            assert re.search(pattern, text, re.IGNORECASE | re.MULTILINE), (
                tech["id"], pattern, Path(tech["advanced_example"]).name
            )


def test_claim_contracts_expose_failure_receipt_and_overclaim_boundaries() -> None:
    registry = load_registry()
    for tech_id, contract in registry.claim_contracts.items():
        assert len(contract["expected_failure_cases"]) >= 3, tech_id
        assert len(contract["required_receipt_fields"]) >= 3, tech_id
        assert contract["forbidden_claim_patterns"], tech_id
        for pattern in contract["forbidden_claim_patterns"]:
            re.compile(pattern, re.IGNORECASE)


def test_frontier_exhibits_cannot_promote_without_runtime_proof() -> None:
    registry = load_registry()
    for tech_id in ("jax", "cuda", "rhl_quant"):
        tech = registry.by_id(tech_id)
        assert tech is not None
        assert tech["evidence_state"] == "illustrative"
        assert tech["proof_class"] == "illustrative"
        contract = registry.claim_contract_for(tech_id)
        assert contract is not None
        assert contract["promotion_requirements"]["minimum_evidence_state"] in {
            "tested", "benchmark"
        }
        text = (REPO_ROOT / tech["advanced_example"]).read_text(encoding="utf-8")
        assert not re.search(r"[\"']status[\"']\s*:\s*[\"']VERIFIED", text, re.IGNORECASE)


def test_selection_engine_excludes_concept_only_frontier_claims() -> None:
    from babel_registry import BabelRegistryEngine

    engine = BabelRegistryEngine()
    selected = engine.select(["python_api"], preferred_interfaces=["python_api"])
    assert selected["ok"] is True
    assert selected["selected"]["evidence_state"] in {
        "tested", "benchmark", "formally_verified", "integrated", "production_reference"
    }

    no_match = engine.select(["tensor_cores"], minimum_evidence_state="tested")
    assert no_match["ok"] is False
    assert no_match["status"] == "NO_VERIFIED_MATCH"
