"""Regression tests for proof-gated technology diversification."""
from __future__ import annotations

from tower.diversification import evaluate_candidate, validate_diversification_policy


def _decision(incumbent: str, candidate: str, proof_gate: str) -> dict[str, str]:
    return {
        "problem_boundary": "A measured system boundary cannot be satisfied by the incumbent without violating its declared contract.",
        "incumbent_floor": incumbent,
        "candidate_floor": candidate,
        "measurable_requirement": "The candidate must satisfy the declared boundary under a reproducible comparison rather than a language-preference claim.",
        "comparison_method": "Run the incumbent and candidate against the same fixture and preserve deterministic receipts for the relevant metric.",
        "integration_cost": "Account for toolchain, build, deployment, observability, interoperability, maintenance, and operator cost.",
        "failure_modes": "Reject on missing toolchain, semantic drift, failed proof, unacceptable regression, or hidden operational dependency.",
        "interop_boundary": "Exchange only through the Tower-governed contract declared for the selected floor.",
        "proof_gate": proof_gate,
        "rollback_path": "Retain the incumbent implementation until the candidate is proven and revert selection if its measured advantage disappears."
    }


def test_current_diversification_policy_is_valid() -> None:
    assert validate_diversification_policy() == []


def test_protobuf_can_be_admitted_for_a_tested_contract_boundary() -> None:
    result = evaluate_candidate(_decision("typescript", "protobuf", "tested"))
    assert result["decision"] == "ADMIT", result
    assert result["candidate_evidence_state"] == "tested"


def test_odin_cannot_be_selected_as_tested_while_toolchain_gated() -> None:
    result = evaluate_candidate(_decision("c", "odin", "tested"))
    assert result["decision"] == "REJECT"
    assert result["candidate_evidence_state"] == "toolchain_gated"
    assert any("does not meet proof_gate 'tested'" in error for error in result["errors"])


def test_rhl_quant_cannot_be_selected_for_compression_before_benchmark() -> None:
    result = evaluate_candidate(_decision("python", "rhl_quant", "benchmark"))
    assert result["decision"] == "REJECT"
    assert result["candidate_evidence_state"] == "illustrative"
    assert any("does not meet proof_gate 'benchmark'" in error for error in result["errors"])


def test_language_novelty_without_decision_record_is_rejected() -> None:
    result = evaluate_candidate(
        {
            "incumbent_floor": "rust",
            "candidate_floor": "odin",
            "proof_gate": "compiles"
        }
    )
    assert result["decision"] == "REJECT"
    assert any("missing substantive fields" in error for error in result["errors"])


def test_existing_floor_remains_default_even_when_candidate_is_admissible() -> None:
    result = evaluate_candidate(_decision("typescript", "protobuf", "tested"))
    assert result["default"] == "reuse_existing_floor"
