"""Evidence-bound sequential coding handoff to Aspen Grove (public summary only)."""
from __future__ import annotations
import hashlib
import json
from typing import Any, Mapping, Sequence

SCHEMA = "glaciereq.tower-sequential-handoff.v1"
STAGES = ("recover", "design", "implement", "test", "integrate", "verify", "preserve")
STATUS = frozenset({"pending", "passed", "failed", "blocked"})

def build_handoff(mission_id: str, source_revision: str, steps: Sequence[Mapping[str, Any]], *,
                  aspen_repository: str = "GlacierEQ/aspen-grove-core") -> dict[str, Any]:
    """Emit a deterministic handoff from recorded outcomes, without asserting provider success."""
    if not isinstance(mission_id, str) or not mission_id.strip():
        raise ValueError("mission_id required")
    if not isinstance(source_revision, str) or not source_revision.strip():
        raise ValueError("source_revision required")
    if not isinstance(aspen_repository, str) or not aspen_repository.strip():
        raise ValueError("aspen_repository required")
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes, bytearray)):
        raise ValueError("steps must be a sequence of mappings")
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for step in steps:
        if not isinstance(step, Mapping):
            raise ValueError("step must be a mapping")
        if set(step) - {"stage", "status", "evidence"}:
            raise ValueError("invalid step fields")
        stage, status = step.get("stage"), step.get("status")
        evidence = step.get("evidence", "")
        if not isinstance(stage, str) or not isinstance(status, str):
            raise ValueError("stage and status must be strings")
        if stage not in STAGES or stage in seen or status not in STATUS:
            raise ValueError("invalid or duplicate stage/status")
        if not isinstance(evidence, str):
            raise ValueError("evidence must be a string")
        if status == "passed" and not evidence.strip():
            raise ValueError("passed stages require evidence")
        seen.add(stage)
        rows.append({"stage": stage, "status": status, "evidence": evidence})
    if [STAGES.index(row["stage"]) for row in rows] != sorted(STAGES.index(row["stage"]) for row in rows):
        raise ValueError("steps must follow execution order")
    payload = {"schema": SCHEMA, "producer": "GlacierEQ/the-tower-of-babel",
               "consumer": aspen_repository.strip(), "mission_id": mission_id.strip(),
               "source_revision": source_revision.strip(), "steps": rows}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()).hexdigest()
    return {**payload, "sha256": digest}
