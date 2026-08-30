import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_machine_state_does_not_fake_current_proof():
    state = load("machine/excellence-state.json")
    assert state["state_semantics"] == "historical_product_projection_separate_from_current_proof"
    assert state["project_direction_authority"] == "operator"
    assert state["gates"]["PROOF_RECEIPT_BOUND"]["status"] == "PENDING"
    assert state["gates"]["proof_receipt_bound_to_sha"] is False
    assert state["proof_receipt"]["status"] == "MISSING_CURRENT_BOUND_RECEIPT"
    assert state["proof_receipt"]["source_sha"] is None
    assert state["proof_receipt"]["identity"] is None
    assert "HYPER_VALIDATED" not in json.dumps(state)


def test_machine_state_moves_forward_without_canonical_position_gate():
    state = load("machine/excellence-state.json")
    assert state["evolution_cursor"] == "next:maximize_boundary_fitness_and_capability_recovery"
    assert "canonical_position_only" not in state["evolution_cursor"]
    assert (
        "not required for material evolution"
        in state["gates"]["CANONICAL_POSITION_RESOLVED"]["evidence"]
    )


def test_machine_promotion_control_cannot_grant_project_authority():
    control = load("machine/promotion_authority.json")
    assert control["project_direction_authority"] == "operator"
    assert control["machine_may_grant_project_authority"] is False
    assert control["legacy_hmac_grant"] == "retired"
    assert "auto_granted" not in json.dumps(control)


def test_machine_target_is_real_and_preserves_capability():
    target = load("machine/target-contract.json")
    assert target["project_direction_authority"] == "operator"
    assert target["target"] == "maximum-boundary-fitness-polyglot-engine"
    assert "projection-does-not-delete-capability" in target["invariants"]
    assert "truth-by-capability-amputation" in target["non_goals"]


def test_capability_inventory_names_real_tower_mechanisms():
    capabilities = load("machine/capabilities.json")
    names = set(capabilities["capabilities"])
    assert {
        "boundary-fitness-technology-selection",
        "cross-language-interface-mapping",
        "capability-activation",
        "flagship-polyglot-integration",
        "git-index-integrity-verification",
    }.issubset(names)
    assert capabilities["project_direction_authority"] == "operator"
