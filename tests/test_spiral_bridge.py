from __future__ import annotations

import json
from pathlib import Path

from tower.innovation import evaluate_repository, plan_interventions
from tower.registry import load_registry
from tower.spiral_bridge import (
    BRIDGE_SCHEMA,
    build_bridge_contract,
    boundary_contract,
    intervention_contract,
    promotion_evidence_template,
)


def _write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _registry(tmp_path: Path):
    reg = tmp_path / "registry"
    (reg / "tower.d").mkdir(parents=True)
    rows = [
        {
            "id": "odin", "name": "Odin", "evidence_state": "toolchain_gated", "proof_class": "compile",
            "what": "Explicit native memory contexts and data layout.",
            "where": "Memory allocators arenas buffers layout.",
            "when": "Use when allocator visibility matters.",
            "why": "Explicit memory.",
            "how": "Memory contexts.",
        },
        {
            "id": "rust", "name": "Rust", "evidence_state": "tested", "proof_class": "behavioral",
            "what": "Memory safe systems logic.",
            "where": "Logic policy invariants security.",
            "when": "Use for safety critical logic.",
            "why": "Ownership.",
            "how": "Types Result.",
        },
        {
            "id": "typescript", "name": "TypeScript", "evidence_state": "tested", "proof_class": "behavioral",
            "what": "Typed async action interfaces.",
            "where": "Action API MCP interfaces.",
            "when": "Use for async connector boundaries.",
            "why": "Runtime reach.",
            "how": "Types async.",
        },
    ]
    _write(reg, "tower.d/tech.json", json.dumps({"technologies": rows}))
    _write(reg, "claims.json", json.dumps({
        "metadata": {
            "authority": "registry/tower.yml",
            "contract_type": "advanced_exhibit_semantic_claims",
            "global_claim_boundary": "Test contract."
        },
        "contracts": {}
    }))
    _write(reg, "tower.yml", json.dumps({
        "tower_id": "bridge-test",
        "fragments": ["tower.d/tech.json"],
        "claim_contracts": "claims.json",
        "technologies": [],
    }))
    return load_registry(reg / "tower.yml")


def test_bridge_exports_spiral_quality_and_intervention(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory.py", "state = bytearray(64) # memory allocator arena buffer layout")
    _write(repo, "action/gateway.ts", "async function execute() {} // action api mcp request")
    _write(repo, "tests/test_runtime.py", "def test_ok(): assert True")

    evaluation = evaluate_repository(repo, registry)
    plan = plan_interventions(evaluation)
    assert plan

    payload = build_bridge_contract(evaluation, plan[0])
    assert payload["schema"] == BRIDGE_SCHEMA
    assert payload["quality_state"]["overall"] == evaluation.overall_score
    assert payload["intervention"]["impact"]["mid_term"] >= 0
    assert payload["boundaries"]


def test_memory_boundary_preserves_stable_and_exposes_gated_frontier(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory.py", "state = bytearray(64) # memory allocator arena buffer layout")

    evaluation = evaluate_repository(repo, registry)
    memory = next(row for row in evaluation.roles if row.role == "memory")
    contract = boundary_contract(memory, evaluation)

    assert contract["stable_owner"]["language"] == "python"
    assert contract["frontier_specialist"]["language"] == "odin"
    assert contract["frontier_specialist"]["mode"] == "PROOF_REQUIRED"
    assert contract["promotion_requirements"]
    assert "memory.py" in contract["owned_paths"]


def test_promotion_template_is_not_fake_success(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory.py", "state = bytearray(64) # memory allocator arena buffer layout")

    evaluation = evaluate_repository(repo, registry)
    memory = next(row for row in evaluation.roles if row.role == "memory")
    promotion = promotion_evidence_template(memory)

    assert promotion["required"] is True
    assert promotion["execution_ready"] is False
    assert promotion["behavioral_parity"] is False
    assert promotion["rollback_ready"] is False
    assert promotion["benchmark_gain"] == 0.0


def test_intervention_contract_preserves_near_far_and_derives_mid(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "logic/policy.rs", "fn policy() {} // logic policy invariant security")

    evaluation = evaluate_repository(repo, registry)
    item = plan_interventions(evaluation)[0]
    contract = intervention_contract(item)
    impact = contract["impact"]

    assert min(impact["near_term"], impact["far_term"]) <= impact["mid_term"] <= max(
        impact["near_term"], impact["far_term"]
    )
