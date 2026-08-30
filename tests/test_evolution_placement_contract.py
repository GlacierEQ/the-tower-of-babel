from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "governance" / "evolution-placement-contract.v1.json").read_text(
        encoding="utf-8"
    )
)
REGISTRY = json.loads((ROOT / "registry" / "tower.yml").read_text(encoding="utf-8"))
CATALOG = json.loads(
    (ROOT / "generated" / "smithery.registry.json").read_text(encoding="utf-8")
)
QUALITY = (ROOT / "QUALITY_CONTRACT.md").read_text(encoding="utf-8")


def test_tower_advises_evolution_without_acquiring_project_authority():
    assert CONTRACT["schema"] == "glaciereq.tower-evolution-placement-contract.v1"
    assert CONTRACT["authority"]["repository"] == "GlacierEQ/the-tower-of-babel"
    assert CONTRACT["authority"]["registry"] == "registry/tower.yml"
    assert (
        CONTRACT["authority"]["technology_catalog"]
        == "generated/smithery.registry.json"
    )
    assert CONTRACT["authority"]["project_direction_authority"] is False
    assert CONTRACT["operator"]["project_direction_authority"] == "absolute"
    assert CONTRACT["operator"]["tower_may_veto_operator_direction"] is False
    assert CONTRACT["integration"]["consumer"] == "GlacierEQ/job-application"
    assert CONTRACT["integration"]["placement_required_before_material_evolution"] is False
    assert CONTRACT["integration"]["placement_can_delay_material_evolution"] is False
    assert (
        CONTRACT["integration"]["placement_receipt_semantics"]
        == "advisory_technical_evidence_not_permission"
    )
    assert CONTRACT["integration"]["retroactively_invalidates_existing_excellence_state"] is False


def test_decisions_force_architectural_reasoning_not_language_counting():
    assert CONTRACT["decisions"] == ["KEEP", "ADD", "SPLIT", "EXPERIMENT"]
    policy = CONTRACT["policy"]
    assert policy["language_count_is_not_a_success_metric"] is True
    assert policy["presentation_need_cannot_force_language_change"] is True
    assert policy["existing_working_implementation_is_preserved_by_default"] is True
    assert policy["add_requires_unique_architectural_responsibility"] is True
    assert policy["split_requires_explicit_interface_contract"] is True
    assert policy["experiment_precedes_adoption_when_placement_is_uncertain"] is True
    assert policy["tower_recommendation_cannot_veto_operator_direction"] is True
    assert policy["material_evolution_continues_without_tower_receipt"] is True


def test_cross_runtime_overlap_requires_parity_and_proof():
    policy = CONTRACT["policy"]
    assert policy["semantic_overlap_requires_cross_runtime_parity_or_explicit_non_equivalence"] is True
    assert policy["new_runtime_requires_declared_proof_tier"] is True
    assert policy["toolchain_or_external_unavailability_must_remain_blocked_not_passed"] is True
    assert CONTRACT["proof_tiers"] == ["A", "B", "C"]
    required = set(CONTRACT["boundary_required_fields"])
    assert {
        "responsibility",
        "candidate_technology",
        "activation_condition",
        "why_existing_boundary_is_insufficient",
        "interface_contract",
        "proof_tier",
        "parity_required",
        "parity_contract",
    }.issubset(required)


def test_legacy_authority_field_is_non_authoritative_compatibility_only():
    assert "tower_authority" in CONTRACT["required_receipt_fields"]
    assert "never project-direction authority" in CONTRACT["compatibility"]["tower_authority_field"]


def test_contract_is_consistent_with_tower_and_quality_evidence_sources():
    assert REGISTRY["tower_id"] == "glaciereq.tower-of-babel.v1"
    assert REGISTRY["governance"]["canonical_source"] == "registry/tower.yml"
    assert CATALOG["source"] == "registry/tower.yml"
    assert "technology:python" in CATALOG["capabilities"]
    assert "technology:go" in CATALOG["capabilities"]
    assert "technology:rust" in CATALOG["capabilities"]
    assert set(REGISTRY["governance"]["proof_classes"]) >= {
        "compile",
        "behavioral",
        "benchmark",
        "integration",
    }
    assert "Typed or explicit inputs and outputs" in QUALITY
    assert "Validation and failure behavior" in QUALITY
    assert "A meaningful invariant or policy boundary" in QUALITY
    assert "A runnable demonstration, proof, benchmark, or test vector" in QUALITY
    assert "Missing toolchains, services, dependencies, or hardware produce exact blockers" in QUALITY
    assert "Structural presence is not compiler proof, and compiler proof is not production proof" in QUALITY
