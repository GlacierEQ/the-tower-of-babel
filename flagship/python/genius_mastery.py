#!/usr/bin/env python3
"""Genius Mastery gate for the Tower flagship mega-pipeline.

This stage adjudicates the technology plan produced by ``planner.py`` using the
Genius Logic deductive engine (vendored from APEX longest-horizon). It encodes
each selected technology as a Proposition, derives truth to a fixpoint, and runs
the adversary to prove (or refute) the claim that the plan is internally
coherent: capability coverage, proof-class floor, interface composition, and the
absence of gated selections.

It also leverages the APEX mega-skills CLI (``apex_mega``) as an optional
verification sub-stage. That lever is OFF by default to keep the portable
governance pass free of external agent/network side effects; opt in with
``APEX_MEGA_ENABLED=1``.

Usage:
    python flagship/python/genius_mastery.py <plan.json> <genius_report.json> [--mission mission.json]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from genius_logic import LogicEngine, Proposition  # noqa: E402
from tower.registry import TowerRegistry, load_registry  # noqa: E402

_PROOF_ORDER = {
    "illustrative": 0,
    "compile": 1,
    "behavioral": 2,
    "benchmark": 3,
    "hardware": 3,
    "integration": 4,
    "formal": 5,
}
_GATED_STATES = {"hardware_gated", "toolchain_gated", "service_gated"}
# evidence_state values that indicate a technology is directly executable in
# standard CI without extra hardware/service/toolchain provisioning.
_DIRECTLY_EXECUTABLE = {
    "tested",
    "compiles",
    "formally_verified",
    "behavioral",
    "benchmark",
    "integration",
}


def read_object(path: Path, label: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{label} must be a JSON object")
    return payload


def _proof_rank(row: dict) -> int:
    return _PROOF_ORDER.get(str(row.get("proof_class", "")), -1)


def build_engine(
    plan: dict,
    registry: TowerRegistry,
    preferred_interfaces: set[str] | None = None,
) -> LogicEngine:
    """Encode the plan + registry metadata into a Genius Logic belief set.

    ``preferred_interfaces`` is normally the mission's declared interfaces
    (the planner does not echo them into the plan); passing them explicitly
    enables the interface-composition coherence check.
    """
    engine = LogicEngine()

    selected_ids = [str(t) for t in plan.get("technology_ids", []) if isinstance(t, str)]
    if preferred_interfaces is None:
        preferred_interfaces = {str(i).casefold() for i in plan.get("preferred_interfaces", []) if isinstance(i, str)}
    preferred_interfaces = {str(i).casefold() for i in preferred_interfaces}
    unmatched = plan.get("unmatched_capabilities", []) or []
    gated = plan.get("gated_candidates", {}) or {}

    coverage_ok = not unmatched
    engine.add(Proposition(
        id="capability_coverage",
        statement="all required mission capabilities are covered by selected technology",
        truth="true" if coverage_ok else "false",
    ))

    exec_claims: list[str] = []
    covered_interfaces: set[str] = set()
    selected_rows: dict[str, dict] = {}
    missing_fact_ids: list[str] = []
    for tech_id in selected_ids:
        row = registry.by_id(tech_id)
        if row is None:
            # Unknown selected id is itself a coherence failure.
            fact_id = f"missing:{tech_id}"
            engine.add(Proposition(
                id=fact_id,
                statement=f"selected technology {tech_id} is absent from the registry",
                truth="true",
                contradicts=["coherent"],
            ))
            missing_fact_ids.append(fact_id)
            continue
        selected_rows[tech_id] = row
        proof = _proof_rank(row)
        interfaces = {str(i).casefold() for i in row.get("interfaces", []) if isinstance(i, str)}
        covered_interfaces |= interfaces
        exec_id = f"exec:{tech_id}"
        exec_truth = (
            "true"
            if row.get("evidence_state") in _DIRECTLY_EXECUTABLE and proof >= 1
            else "false"
        )
        exec_claims.append(exec_id)
        engine.add(Proposition(
            id=exec_id,
            statement=(
                f"{row.get('name', tech_id)} is directly executable in standard CI "
                f"(proof_class={row.get('proof_class')}, evidence_state={row.get('evidence_state')})"
            ),
            truth=exec_truth,
        ))
        engine.add(Proposition(
            id=f"sel:{tech_id}",
            statement=f"{row.get('name', tech_id)} is selected for the mission",
            truth="true",
            supports=[exec_id],
        ))

    engine.add(Proposition(
        id="covered_interfaces",
        statement=",".join(sorted(covered_interfaces)) if covered_interfaces else "",
        truth="true",
    ))

    # Proof-class floor: every selected technology must meet the minimum proof
    # class declared by the planner (compile). Proof rank < 1 is a violation.
    proof_floor_ok = all(_proof_rank(row) >= _PROOF_ORDER["compile"] for row in selected_rows.values())
    engine.add(Proposition(
        id="proof_floor",
        statement="all selected technologies meet the minimum proof-class floor (compile)",
        truth="true" if proof_floor_ok else "false",
    ))

    # Interface composition: every preferred interface is provided by some
    # selected technology.
    interface_ok = preferred_interfaces.issubset(covered_interfaces) if preferred_interfaces else True
    engine.add(Proposition(
        id="interface_composition",
        statement="all preferred interfaces are provided by the selected technology set",
        truth="true" if interface_ok else "false",
    ))

    # No selected technology may be gated (gated candidates must remain
    # candidates, not selections).
    gated_ok = not any(tid in gated for tid in selected_ids)
    engine.add(Proposition(
        id="no_gated_selection",
        statement="no gated technology was promoted to a selected technology",
        truth="true" if gated_ok else "false",
    ))

    # Failure evidence facts. Each is established TRUE exactly when the failure
    # it names is present and contradicts the `coherent` claim, so the adversary
    # and contradiction detector can refute coherence. The parallel claim
    # propositions above (truth == pass/fail state) are retained for the report.
    evidence_fact_ids: list[str] = list(missing_fact_ids)
    failures = [
        ("capabilities_uncovered", "at least one required capability is uncovered", not coverage_ok),
        ("proof_floor_violated", "a selected technology undercuts the minimum proof-class floor", not proof_floor_ok),
        ("interfaces_uncovered", "a preferred interface is not provided by any selected technology", not interface_ok),
        ("gated_selection_promoted", "a gated (unprovisioned) technology was promoted to a selection", not gated_ok),
    ]
    for fact_id, statement, present in failures:
        engine.add(Proposition(
            id=fact_id,
            statement=statement,
            truth="true" if present else "false",
            contradicts=["coherent"],
        ))
        if present:
            evidence_fact_ids.append(fact_id)

    # A selected technology that cannot run under CI is a coherence threat too.
    for exec_id in exec_claims:
        prop = engine.props.get(exec_id)
        if prop is None or prop.truth != "true":
            engine.add(Proposition(
                id=f"exec_unavailable:{exec_id}",
                statement=(prop.statement if prop else exec_id) + " is not directly executable in standard CI",
                truth="true",
                contradicts=["coherent"],
            ))
            evidence_fact_ids.append(f"exec_unavailable:{exec_id}")

    coherent_truth = "true" if not evidence_fact_ids else "false"
    engine.add(Proposition(
        id="coherent",
        statement="the selected technology plan is internally coherent",
        truth=coherent_truth,
        supports=["capability_coverage", "proof_floor", "interface_composition", "no_gated_selection"],
        contradicts=list(evidence_fact_ids),
    ))

    return engine


def leverage_mega_skills(work_dir: Path) -> dict:
    """Optionally invoke the APEX mega-skills CLI as a verification lever.

    Disabled unless ``APEX_MEGA_ENABLED`` is set, so the default governance pass
    performs no external agent/network work. Honors the user's existing tooling
    layout (``~/.agents/skills/apex-mega-skills/apex_mega.py`` or a ``apex_mega``
    console entry on PATH).
    """
    if not os.environ.get("APEX_MEGA_ENABLED"):
        return {"enabled": False, "status": "SKIPPED", "note": "apex_mega verification lever disabled (APEX_MEGA_ENABLED unset)"}

    mega_path = os.environ.get("APEX_MEGA") or shutil.which("apex_mega")
    if not mega_path:
        candidates = Path.home() / ".agents" / "skills" / "apex-mega-skills" / "apex_mega.py"
        if candidates.is_file():
            mega_path = str(candidates)
    if not mega_path:
        return {"enabled": True, "status": "BLOCKED_TOOLCHAIN", "blocker": "apex_mega CLI not found"}

    cmd = [sys.executable, mega_path, "code", "verify", "--target", str(work_dir), "--level", "syntax"]
    try:
        completed = subprocess.run(cmd, text=True, capture_output=True, timeout=120, check=False)
    except subprocess.TimeoutExpired:
        return {"enabled": True, "status": "FAILED_TIMEOUT"}
    except OSError as exc:
        return {"enabled": True, "status": "FAILED_SPAWN", "error": str(exc)}

    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError:
        data = {"raw": completed.stdout.strip()}
    return {
        "enabled": True,
        "status": "VERIFIED" if completed.returncode == 0 else "FAILED",
        "code": completed.returncode,
        "data": data,
    }


def adjudicate(
    plan: dict,
    registry: TowerRegistry,
    work_dir: Path,
    preferred_interfaces: set[str] | None = None,
) -> dict:
    """Run the Genius Mastery coherence gate and the optional mega-skills lever."""
    engine = build_engine(plan, registry, preferred_interfaces)
    engine.derive()
    adversary = engine.adversary("coherent")
    contradictions = engine.contradictions()

    coherent_prop = engine.props.get("coherent")
    coherent_truth = coherent_prop.truth if coherent_prop else "unknown"
    coherent_holds = coherent_truth == "true"

    coherent = not contradictions and not adversary.refuted and coherent_holds

    mega = leverage_mega_skills(work_dir)

    iface_prop = engine.props.get("interface_composition")
    covered_prop = engine.props.get("covered_interfaces")
    covered_list = (
        [s for s in covered_prop.statement.split(",") if s]
        if covered_prop is not None and covered_prop.statement
        else []
    )
    return {
        "stage": "genius_mastery",
        "status": "VERIFIED" if coherent else "FAILED",
        "proposition_count": len(engine.props),
        "rule_count": len(engine.rules),
        "coherent": coherent_holds,
        "adversary": {
            "claim_id": adversary.claim_id,
            "refuted": adversary.refuted,
            "challengers": list(adversary.challengers),
            "note": adversary.note,
        },
        "contradictions": [
            {"a": a, "b": b, "statement_a": engine.props[a].statement, "statement_b": engine.props[b].statement}
            for a, b in contradictions
        ],
        "capability_coverage": engine.props.get("capability_coverage", Proposition("", "")).truth,
        "proof_floor": engine.props.get("proof_floor", Proposition("", "")).truth,
        "interface_composition": iface_prop.truth if iface_prop else "unknown",
        "preferred_interfaces_covered": sorted(covered_list),
        "no_gated_selection": engine.props.get("no_gated_selection", Proposition("", "")).truth,
        "selected_technologies": plan.get("technology_ids", []),
        "unmatched_capabilities": plan.get("unmatched_capabilities", []),
        "gated_candidates": plan.get("gated_candidates", {}),
        "tower_registry_sha256": plan.get("tower_registry_sha256"),
        "mega_skills": mega,
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="genius_mastery", description="Genius Mastery coherence gate")
    parser.add_argument("plan", type=Path, help="path to plan.json")
    parser.add_argument("report", type=Path, help="path to write genius_report.json")
    parser.add_argument("--mission", type=Path, default=None, help="optional mission.input.json for preferred interfaces")
    args = parser.parse_args()

    plan = read_object(args.plan, "plan")
    if plan.get("unmatched_capabilities"):
        raise ValueError("plan must have no unmatched capabilities before genius mastery")

    preferred_interfaces: set[str] | None = None
    if args.mission is not None:
        mission = read_object(args.mission, "mission")
        preferred_interfaces = {str(i) for i in mission.get("preferred_interfaces", []) if isinstance(i, str)}

    registry = load_registry()
    report = adjudicate(plan, registry, args.plan.parent, preferred_interfaces)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "VERIFIED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
