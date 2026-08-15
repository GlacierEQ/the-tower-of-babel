"""Executable Tower of Babel architecture law.

The Tower selects technologies by boundary fitness.  It does not impose a
repository-wide implementation language.  A polyglot design is valid when each
architectural concern has one owner, explicit interfaces, and proof.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


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
        for field in ("lane_id", "concern", "language", "rationale", "interface", "proof"):
            if not getattr(self, field).strip():
                errors.append(f"{field} must be non-empty")
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
