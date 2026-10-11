"""Continuation-oriented technology resolution for the Tower of Babel.

This active module composes the Tower's existing fitness dimensions into a
selection and resolution record.  Evidence gaps, experimental posture, and
placement differences stay visible as follow-up work; they do not erase a
candidate or leave a boundary without a selected capability.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


FITNESS_DIMENSIONS = (
    "performance",
    "memory_safety",
    "determinism",
    "concurrency",
    "memory_density",
    "portability",
    "accelerator_access",
    "formal_verifiability",
    "ecosystem",
    "operability",
)


@dataclass(frozen=True)
class LanguageLane:
    lane_id: str
    concern: str
    language: str
    rationale: str
    interface: str
    proof: str

    def observations(self) -> tuple[str, ...]:
        observations: list[str] = []
        for field_name in (
            "lane_id",
            "concern",
            "language",
            "rationale",
            "interface",
            "proof",
        ):
            if not getattr(self, field_name).strip():
                observations.append(f"{field_name}_needs_detail")
        if self.rationale.strip() and len(self.rationale.strip()) < 20:
            observations.append("rationale_needs_boundary_fitness_detail")
        return tuple(observations)


@dataclass(frozen=True)
class BoundaryObjective:
    """Weighted comparison objective with review signals instead of exclusions."""

    weights: Mapping[str, float] = field(
        default_factory=lambda: {
            "performance": 0.16,
            "memory_safety": 0.14,
            "determinism": 0.10,
            "concurrency": 0.10,
            "memory_density": 0.08,
            "portability": 0.08,
            "accelerator_access": 0.10,
            "formal_verifiability": 0.08,
            "ecosystem": 0.08,
            "operability": 0.08,
        }
    )
    interoperability_penalty: float = 0.06
    migration_penalty: float = 0.03
    confidence_review_threshold: float = 0.65
    advantage_review_threshold: float = 0.03

    def observations(self) -> tuple[str, ...]:
        observations: list[str] = []
        if set(self.weights) != set(FITNESS_DIMENSIONS):
            observations.append("fitness_dimensions_need_alignment")
        if any(
            not isinstance(weight, (int, float)) or weight < 0
            for weight in self.weights.values()
        ):
            observations.append("fitness_weights_need_nonnegative_numeric_values")
        if (
            abs(
                sum(
                    float(weight)
                    for weight in self.weights.values()
                    if isinstance(weight, (int, float))
                )
                - 1.0
            )
            > 1e-9
        ):
            observations.append("fitness_weights_need_normalization")
        for name in (
            "interoperability_penalty",
            "migration_penalty",
            "confidence_review_threshold",
            "advantage_review_threshold",
        ):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
                observations.append(f"{name}_needs_unit_interval_value")
        if self.interoperability_penalty + self.migration_penalty >= 0.5:
            observations.append("interface_cost_weight_needs_review")
        return tuple(observations)


@dataclass(frozen=True)
class TechnologyCandidate:
    language: str
    boundary: str
    evidence: str
    fitness: Mapping[str, float]
    evidence_confidence: float = 1.0
    interoperability_cost: float = 0.0
    migration_cost: float = 0.0
    experimental: bool = False
    reversible: bool = True

    def observations(self) -> tuple[str, ...]:
        observations: list[str] = []
        for name in ("language", "boundary", "evidence"):
            if not getattr(self, name).strip():
                observations.append(f"{name}_needs_detail")
        unknown = set(self.fitness) - set(FITNESS_DIMENSIONS)
        if unknown:
            observations.append(
                "fitness_contains_unmapped_dimensions:" + ",".join(sorted(unknown))
            )
        for name in FITNESS_DIMENSIONS:
            value = self.fitness.get(name, 0.0)
            if not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
                observations.append(f"fitness.{name}_needs_unit_interval_value")
        for name in ("evidence_confidence", "interoperability_cost", "migration_cost"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not 0.0 <= value <= 1.0:
                observations.append(f"{name}_needs_unit_interval_value")
        return tuple(observations)


@dataclass(frozen=True)
class RankedTechnology:
    candidate: TechnologyCandidate
    score: float
    continuation: str
    resolution_work: tuple[str, ...]


@dataclass(frozen=True)
class BoundaryResolution:
    boundary: str
    selected: RankedTechnology | None
    ranked: tuple[RankedTechnology, ...]
    decision: str
    continuation: str
    resolution_work: tuple[str, ...]


@dataclass(frozen=True)
class LaneResolution:
    lane: LanguageLane
    selected: RankedTechnology | None
    continuation: str
    resolution_work: tuple[str, ...]


def _unit_interval(value: object) -> float:
    """Keep a malformed score observable while preserving a runnable ranking."""
    if not isinstance(value, (int, float)):
        return 0.0
    return max(0.0, min(1.0, float(value)))


def _normalized_weights(objective: BoundaryObjective) -> dict[str, float]:
    values = {
        name: max(0.0, float(objective.weights.get(name, 0.0)))
        for name in FITNESS_DIMENSIONS
    }
    total = sum(values.values())
    if total == 0.0:
        return {name: 1.0 / len(FITNESS_DIMENSIONS) for name in FITNESS_DIMENSIONS}
    return {name: value / total for name, value in values.items()}


def rank_technology(
    candidate: TechnologyCandidate,
    objective: BoundaryObjective | None = None,
) -> RankedTechnology:
    """Rank every candidate and describe follow-up work without excluding it."""
    policy = objective or BoundaryObjective()
    resolution_work = list(policy.observations()) + list(candidate.observations())
    if _unit_interval(candidate.evidence_confidence) < _unit_interval(
        policy.confidence_review_threshold
    ):
        resolution_work.append("expand_evidence_confidence")
    if candidate.experimental and not candidate.reversible:
        resolution_work.append("design_reversible_experiment_path")

    weights = _normalized_weights(policy)
    raw_fitness = sum(
        _unit_interval(candidate.fitness.get(name, 0.0)) * weight
        for name, weight in weights.items()
    )
    score = (
        raw_fitness * _unit_interval(candidate.evidence_confidence)
        - _unit_interval(policy.interoperability_penalty)
        * _unit_interval(candidate.interoperability_cost)
        - _unit_interval(policy.migration_penalty)
        * _unit_interval(candidate.migration_cost)
    )
    return RankedTechnology(
        candidate=candidate,
        score=round(score, 6),
        continuation="enabled",
        resolution_work=tuple(sorted(set(resolution_work))),
    )


def resolve_technology(
    candidates: Iterable[TechnologyCandidate],
    objective: BoundaryObjective | None = None,
) -> BoundaryResolution:
    """Select the strongest available capability and retain all alternatives."""
    policy = objective or BoundaryObjective()
    rows = list(candidates)
    ranked = tuple(
        sorted(
            (rank_technology(candidate, policy) for candidate in rows),
            key=lambda item: (-item.score, item.candidate.language.casefold()),
        )
    )
    boundary_names = sorted({row.boundary for row in rows if row.boundary.strip()})
    resolution_work: list[str] = list(policy.observations())
    if not rows:
        resolution_work.append("supply_capability_candidates")
    if len(boundary_names) > 1:
        resolution_work.append("split_multi_boundary_comparison")
    selected = ranked[0] if ranked else None
    if selected is not None:
        resolution_work.extend(selected.resolution_work)
    return BoundaryResolution(
        boundary=boundary_names[0] if len(boundary_names) == 1 else "",
        selected=selected,
        ranked=ranked,
        decision="selected_strongest_available_capability"
        if selected
        else "resolution_work_required",
        continuation="enabled",
        resolution_work=tuple(sorted(set(resolution_work))),
    )


def resolve_lane_against_candidates(
    lane: LanguageLane,
    candidates: Iterable[TechnologyCandidate],
    objective: BoundaryObjective | None = None,
) -> LaneResolution:
    """Keep a declared lane active while exposing comparative follow-up work."""
    resolution = resolve_technology(candidates, objective)
    work = list(lane.observations()) + list(resolution.resolution_work)
    comparable = [
        item
        for item in resolution.ranked
        if item.candidate.boundary.casefold() == lane.concern.casefold()
    ]
    selected = comparable[0] if comparable else resolution.selected
    declared = next(
        (
            item
            for item in comparable
            if item.candidate.language.casefold() == lane.language.casefold()
        ),
        None,
    )
    if not comparable:
        work.append("supply_candidates_for_lane_boundary")
    elif declared is None:
        work.append("add_declared_language_comparison_evidence")
    elif (
        selected is not None
        and selected.candidate.language.casefold()
        != declared.candidate.language.casefold()
    ):
        advantage = selected.score - declared.score
        threshold = _unit_interval(
            (objective or BoundaryObjective()).advantage_review_threshold
        )
        if advantage >= threshold:
            work.append("review_stronger_alternative:" + selected.candidate.language)
    return LaneResolution(
        lane=lane,
        selected=selected,
        continuation="enabled",
        resolution_work=tuple(sorted(set(work))),
    )


def resolve_architecture(
    candidate_sets: Mapping[str, Sequence[TechnologyCandidate]],
    objectives: Mapping[str, BoundaryObjective] | None = None,
) -> Mapping[str, BoundaryResolution]:
    """Resolve every known boundary without abandoning empty or evolving surfaces."""
    result: dict[str, BoundaryResolution] = {}
    for boundary, candidates in sorted(candidate_sets.items()):
        result[boundary] = resolve_technology(
            candidates, (objectives or {}).get(boundary)
        )
    return result


def resolve_lanes(
    lanes: Iterable[LanguageLane],
) -> tuple[tuple[LanguageLane, tuple[str, ...]], ...]:
    """Return lane observations without rejecting existing language ownership."""
    return tuple((lane, lane.observations()) for lane in lanes)
