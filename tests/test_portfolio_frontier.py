from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from tower.portfolio import (
    EVIDENCE_STATE,
    NoFeasibleTechnologyPortfolio,
    PortfolioRequirements,
    PortfolioSearchTooLarge,
    TechnologyPortfolioPlanner,
)
from tower.registry import load_registry


@pytest.fixture(scope="module")
def registry():
    return load_registry()


def test_exact_interface_mission_composes_two_proven_floors(registry) -> None:
    planner = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_interfaces=frozenset({"bpf_map", "datalog_facts"}),
            minimum_evidence_state="compiles",
            allow_gated=False,
            max_technologies=2,
        ),
    )
    decision = planner.decide("minimal_stack")
    ids = {row.technology_id for row in decision.selected.technologies}
    assert ids == {"ebpf", "datalog"}
    assert decision.selected.coverage_ratio == 1.0
    assert decision.selected.gated_count == 0
    assert decision.evidence_state == EVIDENCE_STATE


def test_toolchain_gated_floor_requires_explicit_admission(registry) -> None:
    blocked = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_interfaces=frozenset({"qasm_ir"}),
            minimum_evidence_state="illustrative",
            allow_gated=False,
        ),
    )
    with pytest.raises(NoFeasibleTechnologyPortfolio):
        blocked.decide()

    admitted = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_interfaces=frozenset({"qasm_ir"}),
            minimum_evidence_state="illustrative",
            allow_gated=True,
        ),
    ).decide("minimal_stack")
    assert [row.technology_id for row in admitted.selected.technologies] == ["openqasm"]
    assert admitted.selected.gated_count == 1


def test_required_floor_below_evidence_threshold_fails_closed(registry) -> None:
    planner = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_technology_ids=frozenset({"jax"}),
            minimum_evidence_state="tested",
            allow_gated=False,
        ),
    )
    with pytest.raises(NoFeasibleTechnologyPortfolio):
        planner.decide()


def test_combination_guard_trips_before_search_explosion(registry) -> None:
    planner = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_interfaces=frozenset({"bpf_map", "datalog_facts"}),
            minimum_evidence_state="illustrative",
            allow_gated=True,
            max_candidates=1,
        ),
    )
    with pytest.raises(PortfolioSearchTooLarge):
        planner.decide()


def test_frontier_contains_no_strictly_dominated_portfolio(registry) -> None:
    planner = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_interfaces=frozenset({"bpf_map", "datalog_facts"}),
            preferred_categories=frozenset(
                {"kernel_tracing_and_security", "declarative_static_analysis"}
            ),
            minimum_evidence_state="compiles",
            max_technologies=3,
        ),
    )
    frontier = planner.pareto_frontier(planner.feasible_portfolios())
    for candidate in frontier:
        assert not any(
            other.dominates(candidate)
            for other in frontier
            if other is not candidate
        )


def test_decision_keeps_selection_below_execution_and_operator_authority(registry) -> None:
    decision = TechnologyPortfolioPlanner(
        registry,
        PortfolioRequirements(
            required_interfaces=frozenset({"bpf_map"}),
            minimum_evidence_state="compiles",
        ),
    ).decide()
    payload = decision.as_dict()
    assert payload["project_direction_authority"] == "OPERATOR"
    assert payload["selection_is_execution"] is False
    assert payload["selection_is_ownership"] is False
    assert "does not prove runtime execution" in payload["truth_boundary"]
    assert len(payload["decision_sha256"]) == 64


def test_receipt_cli_executes_real_registry_selection(tmp_path: Path) -> None:
    output = tmp_path / "decision.json"
    receipt_path = tmp_path / "receipt.json"
    subprocess.run(
        [
            sys.executable,
            "tools/resolve_portfolio.py",
            "--input",
            "examples/tower-portfolio-demand.json",
            "--preference",
            "minimal_stack",
            "--output",
            str(output),
            "--receipt",
            str(receipt_path),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    decision = json.loads(output.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    ids = {row["technology_id"] for row in decision["selected"]["technologies"]}
    assert ids == {"ebpf", "datalog"}
    assert receipt["decision_sha256"] == decision["decision_sha256"]
    assert receipt["verified_state"] == "DETERMINISTIC_PORTFOLIO_MODEL_EXECUTED"
    assert receipt["execution_claim"] == "PORTFOLIO_SELECTED_TECHNOLOGIES_NOT_YET_EXECUTED"
    assert receipt["project_direction_authority"] == "OPERATOR"


def test_empty_mission_and_unknown_required_id_are_rejected(registry) -> None:
    with pytest.raises(ValueError):
        PortfolioRequirements()
    with pytest.raises(NoFeasibleTechnologyPortfolio):
        TechnologyPortfolioPlanner(
            registry,
            PortfolioRequirements(required_technology_ids=frozenset({"not-a-floor"})),
        )
