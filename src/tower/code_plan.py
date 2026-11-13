"""Deterministic, evaluation-only sequential plans for code improvement."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Sequence

from .innovation import Intervention, RepoEvaluation

SCHEMA = "glaciereq.tower.sequential-code-plan.v1"


def build_sequential_code_plan(
    evaluation: RepoEvaluation,
    interventions: Sequence[Intervention],
    *,
    objective: str,
) -> dict[str, Any]:
    """Turn ranked Tower interventions into gated inspect/change/verify steps."""
    if not objective.strip():
        raise ValueError("objective must not be empty")

    steps = []
    previous_step_id = None
    for index, intervention in enumerate(interventions, start=1):
        step_id = f"step-{index:03d}"
        steps.append({
            "step_id": step_id,
            "sequence": index,
            "intervention_id": intervention.intervention_id,
            "title": intervention.title,
            "reason": intervention.reason,
            "boundary": {
                "role": intervention.role,
                "language": intervention.language,
            },
            "inspect": [
                "Inspect the current implementation and its relevant tests before changing it.",
                "Record the baseline behavior and the repository fingerprint.",
            ],
            "change": {
                "recommendation": intervention.title,
                "requires_operator_authorization": True,
            },
            "verify": [
                intervention.completion_signal,
                "Re-evaluate the repository and check for critical-quality regressions.",
                "Run the native checks relevant to the changed boundary.",
            ],
            "persist": "Record changed paths and verification evidence before advancing.",
            "depends_on": [previous_step_id] if previous_step_id else [],
            "advance_only_after_verification": True,
        })
        previous_step_id = step_id

    body = {
        "schema": SCHEMA,
        "status": "ACTION_REQUIRED" if steps else (
            "COMPLETE" if evaluation.complete else "NO_INTERVENTIONS"
        ),
        "mode": "PLAN_ONLY",
        "execution_authorized": False,
        "objective": objective.strip(),
        "repository": evaluation.repository,
        "baseline": {
            "fingerprint": evaluation.fingerprint,
            "overall_score": evaluation.overall_score,
            "critical_floor": evaluation.critical_floor,
            "target": evaluation.target,
            "complete": evaluation.complete,
        },
        "steps": steps,
        "completion_gate": [
            "Verify every completed step against its stated signal.",
            "Re-evaluate the final repository state against the target and critical floor.",
            "Persist the final fingerprint and native-check results.",
        ],
    }
    body["plan_sha256"] = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return body
