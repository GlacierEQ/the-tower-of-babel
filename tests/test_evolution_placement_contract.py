from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = json.loads(
    (ROOT / "governance" / "evolution-placement-contract.apex.v2.json").read_text(
        encoding="utf-8"
    )
)
REGISTRY = json.loads((ROOT / "registry" / "tower.yml").read_text(encoding="utf-8"))
CATALOG = json.loads(
    (ROOT / "generated" / "smithery.registry.json").read_text(encoding="utf-8")
)
QUALITY = (ROOT / "QUALITY_CONTRACT.md").read_text(encoding="utf-8")
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_tower_is_boundary_evidence_engine_not_project_authority():
    assert CONTRACT["schema"] == "glaciereq.tower-evolution-placement-contract.apex.v2"
    assert CONTRACT["human_project_authority"] == "Casey Barton"
    assert CONTRACT["tower_role"]["repository"] == "GlacierEQ/the-tower-of-babel"
    assert CONTRACT["tower_role"]["role"] == "boundary_technology_fitness_evidence_engine"
    assert CONTRACT["tower_role"]["project_direction_authority"] is False
    assert CONTRACT["policy"]["operator_intent_controls_target"] is True
    assert CONTRACT["policy"]["tower_evidence_may_redefine_operator_target"] is False
    assert "sole human authority over project direction" in AGENTS


def test_apex_objective_does_not_reward_smallness_uniformity_or_language_count():
    objective = CONTRACT["objective"]
    assert objective["mode"] == "MAXIMUM_COHERENT_ADVANCE"
    assert objective["selection"] == "PARETO_NON_DOMINATED_FRONTIER"
    assert objective["smallness_intrinsic_score"] == 0
    assert objective["uniformity_intrinsic_score"] == 0
    assert objective["language_count_intrinsic_score"] == 0
    assert objective["diversity_rule"] == "specialize_only_when_boundary_fit_improves_apex"
    assert set(objective["gains"]) >= {
        "capability",
        "intelligence",
        "reliability",
        "efficiency",
        "leverage",
        "composability",
        "reach",
        "frontier_fitness",
    }


def test_decisions_model_frontier_metabolism_not_language_counting():
    assert CONTRACT["decisions"] == [
        "IGNORE_WITH_REASON",
        "WATCH",
        "EXPERIMENT",
        "ADMIT",
        "MIGRATE",
        "RETIRE",
    ]
    policy = CONTRACT["policy"]
    assert policy["language_count_is_not_a_success_metric"] is True
    assert policy["repository_count_is_not_a_success_metric"] is True
    assert policy["presentation_need_cannot_force_language_change"] is True
    assert policy["existing_unique_capability_must_be_preserved_or_exceeded"] is True
    assert policy["new_runtime_requires_unique_boundary_advantage"] is True
    assert policy["experiment_may_be_narrow_without_shrinking_final_target"] is True
    assert policy["fresh_frontier_technology_is_continuous_input"] is True


def test_experiment_baseline_is_not_promoted_to_authority():
    semantics = CONTRACT["experiment_semantics"]
    assert semantics["predecessor_role"] == "measured_baseline"
    assert semantics["predecessor_is_project_authority"] is False
    assert semantics["candidate_role"] == "reversible_boundary_challenger"
    assert semantics["rollback_required"] is True
    assert "strengthen the relevant APEX frontier" in semantics["promotion_rule"]


def test_cross_runtime_boundary_requires_parity_proof_and_gain_preservation():
    policy = CONTRACT["policy"]
    assert policy["semantic_overlap_requires_cross_runtime_parity_or_explicit_non_equivalence"] is True
    assert policy["new_runtime_requires_declared_proof_tier"] is True
    assert policy["toolchain_or_external_unavailability_must_remain_blocked_not_passed"] is True
    required = set(CONTRACT["boundary_required_fields"])
    assert {
        "responsibility",
        "candidate_technology",
        "incumbent_technology",
        "activation_condition",
        "why_existing_boundary_is_insufficient",
        "expected_apex_advantage",
        "interface_contract",
        "proof_tier",
        "parity_required",
        "parity_contract",
        "prior_gains_to_preserve",
        "rollback",
        "replacement_trigger",
    }.issubset(required)


def test_receipt_records_evidence_not_tower_authority():
    required = set(CONTRACT["required_receipt_fields"])
    assert "tower_evidence" in required
    assert "tower_authority" not in required
    assert "operator_intent_ref" in required
    assert "prior_gains" in required
    assert "next_frontier_cursor" in required


def test_contract_is_consistent_with_apex_tower_source_and_quality_proof():
    assert REGISTRY["tower_id"] == "glaciereq.tower-of-babel.v1"
    assert REGISTRY["governance"]["apex_source"] == "registry/tower.yml"
    assert "canonical_source" not in REGISTRY["governance"]
    assert CATALOG["source"] == "registry/tower.yml"
    assert CATALOG["engineering_mode"] == "APEX"
    assert "technology:python" in CATALOG["capabilities"]
    assert "technology:go" in CATALOG["capabilities"]
    assert "technology:rust" in CATALOG["capabilities"]
    assert set(REGISTRY["governance"]["proof_classes"]) >= {
        "compile",
        "behavioral",
        "benchmark",
        "integration",
    }
    assert "Boundary comparison" in QUALITY
    assert "Preservation accounting" in QUALITY
    assert "Evidence constrains claims, not reversible experimentation" in QUALITY
    assert "Missing toolchains, services, dependencies, or hardware produce exact blockers" in QUALITY
    assert "Structural presence is not compiler proof, and compiler proof is not production proof" in QUALITY
