"""Proof-aware technology portfolio selection for Tower missions.

The Tower registry already proves individual floors. This module composes those floors
for a mission using only explicit registry fields: interfaces, categories, technology
IDs, evidence states, and execution gates. It does not infer runtime fitness from prose
or convert a selected portfolio into project authority or execution proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from typing import Iterable, Literal

from .registry import TowerRegistry

EVIDENCE_STATE = "DETERMINISTIC_TOWER_PORTFOLIO_FRONTIER"
Preference = Literal["balanced", "strongest_proof", "minimal_stack", "maximum_coverage"]

EVIDENCE_RANK = {
    "illustrative": 0,
    "toolchain_gated": 1,
    "service_gated": 1,
    "hardware_gated": 1,
    "compiles": 2,
    "tested": 3,
    "formally_verified": 3,
    "benchmark": 4,
    "integrated": 5,
    "production_reference": 6,
}


class NoFeasibleTechnologyPortfolio(ValueError):
    """Raised when explicit Tower requirements cannot be satisfied."""


class PortfolioSearchTooLarge(ValueError):
    """Raised before a portfolio search exceeds its declared combinatorial ceiling."""


@dataclass(frozen=True)
class PortfolioRequirements:
    required_interfaces: frozenset[str] = frozenset()
    preferred_categories: frozenset[str] = frozenset()
    required_technology_ids: frozenset[str] = frozenset()
    minimum_evidence_state: str = "illustrative"
    allow_gated: bool = False
    require_full_interface_coverage: bool = True
    max_technologies: int = 4
    max_candidates: int = 16
    max_combinations: int = 20_000

    def __post_init__(self) -> None:
        if self.minimum_evidence_state not in EVIDENCE_RANK:
            raise ValueError(f"unsupported evidence state: {self.minimum_evidence_state}")
        for name in ("max_technologies", "max_candidates", "max_combinations"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be positive")
        for name in ("required_interfaces", "preferred_categories", "required_technology_ids"):
            values = getattr(self, name)
            if any(not value.strip() for value in values):
                raise ValueError(f"{name} may not contain empty values")
        if not (
            self.required_interfaces
            or self.preferred_categories
            or self.required_technology_ids
        ):
            raise ValueError(
                "portfolio requirements need an explicit interface, category, or technology target"
            )


@dataclass(frozen=True)
class TechnologyOption:
    technology_id: str
    name: str
    category: str
    interfaces: frozenset[str]
    evidence_state: str
    proof_class: str
    gated: bool

    @property
    def evidence_rank(self) -> int:
        return EVIDENCE_RANK[self.evidence_state]

    @classmethod
    def from_registry_row(cls, row: dict[str, object]) -> "TechnologyOption":
        interfaces = row.get("interfaces", [])
        if not isinstance(interfaces, list) or not all(isinstance(item, str) for item in interfaces):
            raise ValueError(f"invalid interfaces for Tower technology {row.get('id')!r}")
        evidence_state = str(row.get("evidence_state") or "")
        if evidence_state not in EVIDENCE_RANK:
            raise ValueError(
                f"unsupported evidence state on Tower technology {row.get('id')!r}: {evidence_state!r}"
            )
        return cls(
            technology_id=str(row.get("id") or ""),
            name=str(row.get("name") or ""),
            category=str(row.get("category") or ""),
            interfaces=frozenset(interfaces),
            evidence_state=evidence_state,
            proof_class=str(row.get("proof_class") or ""),
            gated=evidence_state in {"toolchain_gated", "service_gated", "hardware_gated"},
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "technology_id": self.technology_id,
            "name": self.name,
            "category": self.category,
            "interfaces": sorted(self.interfaces),
            "evidence_state": self.evidence_state,
            "proof_class": self.proof_class,
            "evidence_rank": self.evidence_rank,
            "gated": self.gated,
        }


@dataclass(frozen=True)
class TechnologyPortfolio:
    technologies: tuple[TechnologyOption, ...]
    covered_interfaces: frozenset[str]
    required_interface_count: int
    category_matches: int
    evidence_floor: int
    evidence_sum: int
    gated_count: int
    interface_surplus: int

    @property
    def technology_count(self) -> int:
        return len(self.technologies)

    @property
    def coverage_count(self) -> int:
        return len(self.covered_interfaces)

    @property
    def coverage_ratio(self) -> float:
        if self.required_interface_count == 0:
            return 1.0
        return self.coverage_count / self.required_interface_count

    def dominates(self, other: "TechnologyPortfolio") -> bool:
        gains = (
            self.coverage_count,
            self.category_matches,
            self.evidence_floor,
            self.evidence_sum,
        )
        other_gains = (
            other.coverage_count,
            other.category_matches,
            other.evidence_floor,
            other.evidence_sum,
        )
        costs = (self.technology_count, self.gated_count, self.interface_surplus)
        other_costs = (other.technology_count, other.gated_count, other.interface_surplus)
        no_worse = all(left >= right for left, right in zip(gains, other_gains))
        no_worse = no_worse and all(left <= right for left, right in zip(costs, other_costs))
        strictly = any(left > right for left, right in zip(gains, other_gains))
        strictly = strictly or any(left < right for left, right in zip(costs, other_costs))
        return no_worse and strictly

    def as_dict(self) -> dict[str, object]:
        return {
            "technologies": [item.as_dict() for item in self.technologies],
            "technology_count": self.technology_count,
            "covered_interfaces": sorted(self.covered_interfaces),
            "required_interface_count": self.required_interface_count,
            "coverage_count": self.coverage_count,
            "coverage_ratio": round(self.coverage_ratio, 6),
            "category_matches": self.category_matches,
            "evidence_floor": self.evidence_floor,
            "evidence_sum": self.evidence_sum,
            "gated_count": self.gated_count,
            "interface_surplus": self.interface_surplus,
        }


@dataclass(frozen=True)
class PortfolioDecision:
    preference: Preference
    selected: TechnologyPortfolio
    frontier: tuple[TechnologyPortfolio, ...]
    eligible_candidate_count: int
    search_combination_count: int
    evidence_state: str = EVIDENCE_STATE

    def as_dict(self, *, include_digest: bool = True) -> dict[str, object]:
        value: dict[str, object] = {
            "schema": "glaciereq.tower.portfolio-decision.v1",
            "preference": self.preference,
            "selected": self.selected.as_dict(),
            "frontier": [item.as_dict() for item in self.frontier],
            "frontier_count": len(self.frontier),
            "eligible_candidate_count": self.eligible_candidate_count,
            "search_combination_count": self.search_combination_count,
            "evidence_state": self.evidence_state,
            "project_direction_authority": "OPERATOR",
            "selection_is_execution": False,
            "selection_is_ownership": False,
            "truth_boundary": (
                "Portfolio selection uses explicit Tower registry interfaces, categories, IDs, and evidence states. "
                "It does not prove runtime execution or measured superiority for the selected stack."
            ),
        }
        if include_digest:
            encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
            value["decision_sha256"] = sha256(encoded).hexdigest()
        return value


class TechnologyPortfolioPlanner:
    """Enumerate bounded Tower portfolios, Pareto-filter, then apply preference."""

    def __init__(self, registry: TowerRegistry, requirements: PortfolioRequirements) -> None:
        self.registry = registry
        self.requirements = requirements
        self.options = tuple(
            TechnologyOption.from_registry_row(row)
            for row in registry.technologies
            if isinstance(row, dict)
        )
        ids = [item.technology_id for item in self.options]
        if any(not item for item in ids) or len(ids) != len(set(ids)):
            raise ValueError("Tower technology IDs must be non-empty and unique")
        known = set(ids)
        missing_required = requirements.required_technology_ids - known
        if missing_required:
            raise NoFeasibleTechnologyPortfolio(
                f"required Tower technologies are not present: {sorted(missing_required)}"
            )

    def eligible_options(self) -> tuple[TechnologyOption, ...]:
        req = self.requirements
        minimum_rank = EVIDENCE_RANK[req.minimum_evidence_state]
        rows: list[TechnologyOption] = []
        for option in self.options:
            relevant = (
                option.technology_id in req.required_technology_ids
                or bool(option.interfaces & req.required_interfaces)
                or option.category in req.preferred_categories
            )
            if not relevant:
                continue
            if option.evidence_rank < minimum_rank:
                continue
            if option.gated and not req.allow_gated:
                continue
            rows.append(option)
        rows.sort(key=lambda item: item.technology_id)
        if len(rows) > req.max_candidates:
            raise PortfolioSearchTooLarge(
                f"{len(rows)} eligible Tower technologies exceed max_candidates={req.max_candidates}"
            )
        return tuple(rows)

    def search_combination_count(self, candidate_count: int) -> int:
        limit = min(candidate_count, self.requirements.max_technologies)
        return sum(comb(candidate_count, size) for size in range(1, limit + 1))

    def feasible_portfolios(self) -> tuple[TechnologyPortfolio, ...]:
        req = self.requirements
        options = self.eligible_options()
        if not options:
            raise NoFeasibleTechnologyPortfolio(
                "no Tower technology satisfies the explicit mission requirements"
            )
        combination_count = self.search_combination_count(len(options))
        if combination_count > req.max_combinations:
            raise PortfolioSearchTooLarge(
                f"Tower portfolio search requires {combination_count} combinations; ceiling is {req.max_combinations}"
            )

        feasible: list[TechnologyPortfolio] = []
        for size in range(1, min(len(options), req.max_technologies) + 1):
            for selected in combinations(options, size):
                selected_ids = {item.technology_id for item in selected}
                if not req.required_technology_ids.issubset(selected_ids):
                    continue
                interfaces = frozenset().union(*(item.interfaces for item in selected))
                covered = interfaces & req.required_interfaces
                if req.require_full_interface_coverage and covered != req.required_interfaces:
                    continue
                evidence_ranks = [item.evidence_rank for item in selected]
                feasible.append(
                    TechnologyPortfolio(
                        technologies=tuple(selected),
                        covered_interfaces=covered,
                        required_interface_count=len(req.required_interfaces),
                        category_matches=len(
                            {item.category for item in selected} & req.preferred_categories
                        ),
                        evidence_floor=min(evidence_ranks),
                        evidence_sum=sum(evidence_ranks),
                        gated_count=sum(item.gated for item in selected),
                        interface_surplus=len(interfaces - req.required_interfaces),
                    )
                )
        if not feasible:
            raise NoFeasibleTechnologyPortfolio(
                "no bounded Tower portfolio covers the required interfaces and technology constraints"
            )
        return tuple(feasible)

    @staticmethod
    def pareto_frontier(
        portfolios: Iterable[TechnologyPortfolio],
    ) -> tuple[TechnologyPortfolio, ...]:
        items = tuple(portfolios)
        frontier = tuple(
            item
            for item in items
            if not any(other.dominates(item) for other in items if other is not item)
        )
        return tuple(
            sorted(
                frontier,
                key=lambda item: (
                    -item.coverage_count,
                    -item.evidence_floor,
                    -item.category_matches,
                    item.technology_count,
                    item.gated_count,
                    tuple(option.technology_id for option in item.technologies),
                ),
            )
        )

    def decide(self, preference: Preference = "balanced") -> PortfolioDecision:
        if preference not in {
            "balanced",
            "strongest_proof",
            "minimal_stack",
            "maximum_coverage",
        }:
            raise ValueError("unsupported Tower portfolio preference")
        options = self.eligible_options()
        combination_count = self.search_combination_count(len(options))
        if combination_count > self.requirements.max_combinations:
            raise PortfolioSearchTooLarge(
                f"Tower portfolio search requires {combination_count} combinations; ceiling is {self.requirements.max_combinations}"
            )
        frontier = self.pareto_frontier(self.feasible_portfolios())

        if preference == "strongest_proof":
            selected = max(
                frontier,
                key=lambda item: (
                    item.evidence_floor,
                    item.evidence_sum,
                    item.coverage_count,
                    item.category_matches,
                    -item.technology_count,
                ),
            )
        elif preference == "minimal_stack":
            selected = min(
                frontier,
                key=lambda item: (
                    item.technology_count,
                    item.gated_count,
                    item.interface_surplus,
                    -item.evidence_floor,
                    -item.coverage_count,
                ),
            )
        elif preference == "maximum_coverage":
            selected = max(
                frontier,
                key=lambda item: (
                    item.coverage_count,
                    item.category_matches,
                    item.evidence_floor,
                    -item.technology_count,
                ),
            )
        else:
            selected = max(
                frontier,
                key=lambda item: (
                    item.coverage_ratio
                    + item.evidence_floor / max(EVIDENCE_RANK.values())
                    + min(item.category_matches, 3) / 3
                    - item.gated_count / max(item.technology_count, 1)
                    - item.technology_count / max(self.requirements.max_technologies, 1)
                    - min(item.interface_surplus, 10) / 10,
                    item.evidence_floor,
                    item.coverage_count,
                    -item.technology_count,
                ),
            )

        return PortfolioDecision(
            preference=preference,
            selected=selected,
            frontier=frontier,
            eligible_candidate_count=len(options),
            search_combination_count=combination_count,
        )
