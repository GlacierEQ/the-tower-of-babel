"""Executable Tower of Babel architecture law.

The Tower selects technologies by boundary fitness. It does not impose a
repository-wide implementation language. A polyglot design is valid when each
architectural concern has one owner, explicit interfaces, proof, and a language
choice that survives evidence-backed comparison against credible alternatives.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class LanguageLane:
    lane_id: str
    concern: str
    language: str
    rationale: str
    interface: str
    proof: str

    def validate(self) -> list[str]:
        errors: list[str] = []
        for field_name in ("lane_id", "concern", "language", "rationale", "interface", "proof"):
            if not getattr(self, field_name).strip():
                errors.append(f"{field_name} must be non-empty")
        if len(self.rationale.strip()) < 20:
            errors.append("rationale must explain measurable boundary fitness")
        return errors


def validate_lanes(lanes: Iterable[LanguageLane]) -> list[str]:
    rows = list(lanes)
    errors: list[str] = []
    ids: set[str] = set()
    concerns: set[str] = set()
    for lane in rows:
        errors.extend(f"{lane.lane_id}: {error}" for error in lane.validate())
        key = lane.lane_id.casefold()
        concern = lane.concern.casefold()
        if key in ids:
            errors.append(f"duplicate lane id: {lane.lane_id}")
        if concern in concerns:
            errors.append(f"duplicate concern owner: {lane.concern}")
        ids.add(key)
        concerns.add(concern)
    return errors


def architecture_is_valid(lanes: Iterable[LanguageLane]) -> bool:
    rows = list(lanes)
    return bool(rows) and not validate_lanes(rows)


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
class BoundaryObjective:
    """Weighted objective for one engineering boundary."""

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
    minimum_confidence: float = 0.65
    minimum_advantage_margin: float = 0.03

    def validate(self) -> None:
        if set(self.weights) != set(FITNESS_DIMENSIONS):
            raise ValueError("weights must define every fitness dimension exactly once")
        if any(weight < 0 for weight in self.weights.values()):
            raise ValueError("fitness weights must be non-negative")
        if abs(sum(self.weights.values()) - 1.0) > 1e-9:
            raise ValueError("fitness weights must sum to 1.0")
        for name in (
            "interoperability_penalty",
            "migration_penalty",
            "minimum_confidence",
            "minimum_advantage_margin",
        ):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.interoperability_penalty + self.migration_penalty >= 0.5:
            raise ValueError("interface costs must not dominate boundary fitness")


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

    def validate(self) -> None:
        if not self.language.strip():
            raise ValueError("language must be non-empty")
        if not self.boundary.strip():
            raise ValueError("boundary must be non-empty")
        if not self.evidence.strip():
            raise ValueError("evidence must be non-empty")
        unknown = set(self.fitness) - set(FITNESS_DIMENSIONS)
        if unknown:
            raise ValueError(f"unknown fitness dimensions: {sorted(unknown)!r}")
        for name in FITNESS_DIMENSIONS:
            value = self.fitness.get(name, 0.0)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"fitness.{name} must be between 0 and 1")
        for name in ("evidence_confidence", "interoperability_cost", "migration_cost"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class RankedTechnology:
    candidate: TechnologyCandidate
    score: float
    eligible: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class BoundarySelection:
    boundary: str
    selected: RankedTechnology | None
    ranked: tuple[RankedTechnology, ...]
    decision: str


def rank_technology(
    candidate: TechnologyCandidate,
    objective: BoundaryObjective | None = None,
) -> RankedTechnology:
    candidate.validate()
    policy = objective or BoundaryObjective()
    policy.validate()
    blockers: list[str] = []
    if candidate.evidence_confidence < policy.minimum_confidence:
        blockers.append("insufficient_evidence_confidence")
    if candidate.experimental and not candidate.reversible:
        blockers.append("experimental_candidate_requires_reversible_path")

    raw_fitness = sum(
        candidate.fitness.get(name, 0.0) * weight
        for name, weight in policy.weights.items()
    )
    score = (
        raw_fitness * candidate.evidence_confidence
        - policy.interoperability_penalty * candidate.interoperability_cost
        - policy.migration_penalty * candidate.migration_cost
    )
    return RankedTechnology(
        candidate=candidate,
        score=round(score, 6),
        eligible=not blockers,
        blockers=tuple(blockers),
    )


def select_best_technology(
    candidates: Iterable[TechnologyCandidate],
    objective: BoundaryObjective | None = None,
) -> BoundarySelection:
    policy = objective or BoundaryObjective()
    policy.validate()
    rows = list(candidates)
    boundaries = {row.boundary.casefold() for row in rows}
    if len(boundaries) > 1:
        raise ValueError("one selection may compare only one engineering boundary")
    ranked = tuple(
        sorted(
            (rank_technology(candidate, policy) for candidate in rows),
            key=lambda item: (-item.score, item.candidate.language.casefold()),
        )
    )
    selected = next((item for item in ranked if item.eligible), None)
    boundary = rows[0].boundary if rows else ""
    return BoundarySelection(
        boundary=boundary,
        selected=selected,
        ranked=ranked,
        decision="selected_maximum_boundary_fitness" if selected else "no_eligible_candidate",
    )


def validate_lane_against_candidates(
    lane: LanguageLane,
    candidates: Iterable[TechnologyCandidate],
    objective: BoundaryObjective | None = None,
) -> list[str]:
    """Reject a merely plausible lane when a materially better candidate exists."""
    policy = objective or BoundaryObjective()
    policy.validate()
    errors = lane.validate()
    rows = list(candidates)
    if not rows:
        errors.append("no technology candidates supplied for boundary comparison")
        return errors
    if any(row.boundary.casefold() != lane.concern.casefold() for row in rows):
        errors.append("candidate boundary does not match lane concern")
        return errors
    selection = select_best_technology(rows, policy)
    if selection.selected is None:
        errors.append("no eligible technology candidate")
        return errors

    chosen = next(
        (
            item
            for item in selection.ranked
            if item.candidate.language.casefold() == lane.language.casefold() and item.eligible
        ),
        None,
    )
    if chosen is None:
        errors.append(f"declared language {lane.language} has no eligible candidate evidence")
        return errors
    advantage = selection.selected.score - chosen.score
    if (
        selection.selected.candidate.language.casefold() != lane.language.casefold()
        and advantage >= policy.minimum_advantage_margin
    ):
        errors.append(
            "inferior language placement: "
            f"{selection.selected.candidate.language} leads {lane.language} "
            f"by {advantage:.6f} fitness points"
        )
    return errors


def optimize_architecture(
    candidate_sets: Mapping[str, Sequence[TechnologyCandidate]],
    objectives: Mapping[str, BoundaryObjective] | None = None,
) -> Mapping[str, BoundarySelection]:
    """Select the best technology independently for every explicit concern.

    This creates diversification when specialized technologies win different
    boundaries. It never adds languages merely to increase language count.
    """
    result: dict[str, BoundarySelection] = {}
    for boundary, candidates in sorted(candidate_sets.items()):
        if not candidates:
            raise ValueError(f"boundary {boundary} has no technology candidates")
        if any(candidate.boundary.casefold() != boundary.casefold() for candidate in candidates):
            raise ValueError(f"candidate boundary mismatch for {boundary}")
        result[boundary] = select_best_technology(
            candidates,
            (objectives or {}).get(boundary),
        )
    return result
