"""Babel semantic placement and Spiral iteration tests."""
from __future__ import annotations

import json
from pathlib import Path

from tower.innovation import BabelSpiralEngine, evaluate_repository, plan_interventions
from tower.registry import load_registry


def _write(root: Path, path: str, content: str) -> None:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _registry(tmp_path: Path):
    reg = tmp_path / "registry"
    (reg / "tower.d").mkdir(parents=True)
    rows = [
        {
            "id": "odin", "name": "Odin", "evidence_state": "compiles", "proof_class": "compile",
            "what": "Explicit data-oriented native programming and memory contexts.",
            "where": "Memory layout allocators buffers deterministic loops.",
            "when": "Use when data layout and allocator visibility are central.",
            "why": "Explicit memory contexts reduce hidden allocation.",
            "how": "Allocators structs arrays procedures.",
        },
        {
            "id": "rust", "name": "Rust", "evidence_state": "tested", "proof_class": "behavioral",
            "what": "Memory-safe systems logic.",
            "where": "Policy engines invariants concurrency security.",
            "when": "Use for correctness-sensitive native logic.",
            "why": "Ownership and types prevent broad failures.",
            "how": "Enums traits Result ownership.",
        },
        {
            "id": "typescript", "name": "TypeScript", "evidence_state": "tested", "proof_class": "behavioral",
            "what": "Typed asynchronous action and interface layer.",
            "where": "MCP gateways APIs connectors web actions.",
            "when": "Use at JSON RPC and asynchronous action boundaries.",
            "why": "Strong contracts with broad runtime reach.",
            "how": "Types async await streams.",
        },
        {
            "id": "lean4", "name": "Lean 4", "evidence_state": "formally_verified", "proof_class": "formal",
            "what": "Dependent types and machine checked proof.",
            "where": "Formal proof safety invariants verified decision logic.",
            "when": "Use when proof obligations justify machine checked verification.",
            "why": "Proof kernel verifies invariants.",
            "how": "Theorems dependent types proof terms.",
        },
    ]
    _write(reg, "tower.d/tech.json", json.dumps({"technologies": rows}))
    _write(reg, "claims.json", json.dumps({
        "metadata": {
            "authority": "registry/tower.yml",
            "contract_type": "advanced_exhibit_semantic_claims",
            "global_claim_boundary": "Claims remain bounded to executable repository evidence and may be revised by stronger evidence."
        },
        "contracts": {}
    }))
    _write(reg, "tower.yml", json.dumps({
        "tower_id": "test",
        "fragments": ["tower.d/tech.json"],
        "claim_contracts": "claims.json",
        "technologies": [],
    }))
    return load_registry(reg / "tower.yml")


def test_memory_logic_action_resolve_to_specialists(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# Engine\nMemory arena, policy logic, and MCP action gateway.\n")
    _write(repo, "memory/state.odin", "package memory // arena allocator buffer layout memory")
    _write(repo, "logic/policy.rs", "fn evaluate_policy() {} // invariant security logic")
    _write(repo, "action/gateway.ts", "async function execute() {} // mcp api action request response")
    _write(repo, "tests/test_contract.py", "def test_ok(): assert True")
    _write(repo, ".github/workflows/ci.yml", "name: ci\non: [push]\njobs: {}")

    evaluation = evaluate_repository(repo, registry)
    selected = {role.role: role.selected.language for role in evaluation.roles}

    assert selected["memory"] == "odin"
    assert selected["logic"] == "rust"
    assert selected["action"] == "typescript"
    assert selected["interface"] == "typescript"


def test_existing_language_is_preserved_when_alternative_gain_is_small(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# Policy engine\n")
    _write(repo, "logic/policy.rs", "fn evaluate_policy() {} // policy invariant logic")
    evaluation = evaluate_repository(repo, registry)
    logic = next(row for row in evaluation.roles if row.role == "logic")
    assert logic.selected.language == "rust"
    assert "FOCUS rust" in logic.recommendation or "PRESERVE rust" in logic.recommendation


def test_plan_carries_near_and_far_term_impact(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# MCP action service\n")
    _write(repo, "action.py", "def execute(): return True # action api workflow")
    evaluation = evaluate_repository(repo, registry)
    plan = plan_interventions(evaluation)
    assert plan
    assert all(row.impact.near_term >= 0 for row in plan)
    assert all(row.impact.far_term >= 0 for row in plan)
    assert all(row.completion_signal for row in plan)


def test_spiral_without_executor_returns_real_next_action(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# API action service\n")
    _write(repo, "action.py", "def execute(): return True # api action")
    result = BabelSpiralEngine(registry, max_revolutions=3).run(repo)
    assert result["revolutions"][0]["status"] == "ACTION_REQUIRED"
    assert result["next_interventions"]


def test_spiral_reinspects_after_execution(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# API action service\n")
    _write(repo, "action.py", "def execute(): return True # api action")
    calls = {"count": 0}

    def executor(intervention, root):
        calls["count"] += 1
        if calls["count"] == 1:
            _write(root, "tests/test_action.py", "def test_action(): assert True")
            _write(root, ".github/workflows/ci.yml", "name: ci\non: [push]\njobs: {}")
            return True
        return False

    result = BabelSpiralEngine(registry, max_revolutions=3).run(repo, executor=executor)
    first = result["revolutions"][0]
    assert calls["count"] >= 1
    assert first["after"] >= first["before"]

def test_executable_evidence_outweighs_documentation(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory/core.odin", "package memory // allocator arena layout buffer memory")
    for index in range(12):
        _write(
            repo,
            f"docs/action_{index}.md",
            "# Action API gateway\nThis document discusses action handlers, APIs, requests, and workflows.\n",
        )

    evaluation = evaluate_repository(repo, registry)
    memory_file = next(row for row in evaluation.files if row.path == "memory/core.odin")
    docs = [row for row in evaluation.files if row.kind == "documentation"]

    assert memory_file.kind == "implementation"
    assert memory_file.evidence_weight == 1.0
    assert docs and all(row.evidence_weight < memory_file.evidence_weight for row in docs)
    memory = next(row for row in evaluation.roles if row.role == "memory")
    assert memory.selected.language == "odin"


def test_gated_new_language_is_not_treated_as_ready(tmp_path: Path):
    registry = _registry(tmp_path)
    odin = registry.by_id("odin")
    assert odin is not None
    odin["evidence_state"] = "toolchain_gated"

    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# Memory service\nArena allocator layout buffer memory.\n")
    _write(repo, "memory.py", "state = bytearray(64)  # memory buffer allocator layout")

    evaluation = evaluate_repository(repo, registry)
    memory = next(row for row in evaluation.roles if row.role == "memory")
    odin_fit = next(row for row in memory.alternatives if row.language == "odin")

    assert odin_fit.execution_ready is False
    if memory.selected.language == "odin":
        assert memory.recommendation.startswith("PROVE odin")

def test_role_scores_do_not_collapse_to_ceiling(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory/state.odin", "package memory // allocator arena buffer layout memory")
    _write(repo, "logic/policy.rs", "fn evaluate_policy() {} // invariant security logic")
    _write(repo, "action/gateway.ts", "async function execute() {} // mcp api action request response")

    evaluation = evaluate_repository(repo, registry)
    memory = next(row for row in evaluation.roles if row.role == "memory")
    logic = next(row for row in evaluation.roles if row.role == "logic")
    action = next(row for row in evaluation.roles if row.role == "action")

    assert memory.selected.language == "odin"
    assert logic.selected.language == "rust"
    assert action.selected.language == "typescript"

    for role in (memory, logic, action):
        scores = [candidate.score for candidate in role.alternatives]
        assert len(set(scores)) > 1
        assert sum(score == 1.0 for score in scores) <= 1

def test_nested_lock_and_security_tests_count_as_security_evidence(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "README.md", "# Secure service\nSecurity policy logic and API actions.\n")
    _write(repo, "src/policy.rs", "fn enforce() {} // security policy invariant")
    _write(repo, "requirements/ci.lock", "pytest==8.0.0 --hash=sha256:deadbeef\n")
    _write(repo, "tests/test_security_boundaries.py", "def test_security(): assert True")
    _write(repo, ".github/workflows/ci.yml", "name: ci\non: [push]\njobs: {}")

    evaluation = evaluate_repository(repo, registry)
    security = next(axis for axis in evaluation.quality if axis.name == "security")

    assert "dependency lock present" in security.evidence
    assert "security/sandbox tests present" in security.evidence
    assert "lock dependencies" not in security.gaps

def test_stable_owner_and_gated_frontier_are_separate(tmp_path: Path):
    registry = _registry(tmp_path)
    odin = registry.by_id("odin")
    assert odin is not None
    odin["evidence_state"] = "toolchain_gated"

    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory.py", "state = bytearray(128)  # memory arena allocator layout buffer")
    _write(repo, "tests/test_memory.py", "def test_memory(): assert True")

    evaluation = evaluate_repository(repo, registry)
    memory = next(row for row in evaluation.roles if row.role == "memory")

    assert memory.selected.language == memory.stable_owner.language
    assert memory.stable_owner.language == "python"
    assert memory.frontier_candidate.language == "odin"
    assert memory.frontier_candidate.execution_ready is False
    assert "STABLE python" in memory.recommendation
    assert "PROVE odin" in memory.recommendation

    plan = plan_interventions(evaluation)
    memory_work = next(row for row in plan if row.role == "memory")
    assert memory_work.language == "odin"
    assert memory_work.impact.near_term < memory_work.impact.far_term
    assert memory_work.impact.reversibility >= 0.9


def test_ready_specialists_can_be_stable_owners(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "memory/state.odin", "package memory // allocator arena layout buffer memory")
    _write(repo, "logic/policy.rs", "fn evaluate_policy() {} // invariant policy logic security")
    _write(repo, "action/gateway.ts", "async function execute() {} // action mcp api request response")

    evaluation = evaluate_repository(repo, registry)
    roles = {row.role: row for row in evaluation.roles}

    assert roles["memory"].stable_owner.language == "odin"
    assert roles["logic"].stable_owner.language == "rust"
    assert roles["action"].stable_owner.language == "typescript"


def test_lean_file_resolves_lean4_registry_evidence_without_duplicate_candidate(tmp_path: Path):
    registry = _registry(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    _write(repo, "proof/invariant.lean", "theorem safe : True := by trivial -- formal proof invariant verify")

    evaluation = evaluate_repository(repo, registry)
    proof = next(row for row in evaluation.roles if row.role == "proof")
    lean_candidates = [row for row in proof.alternatives if row.language == "lean"]

    assert len(lean_candidates) == 1
    assert lean_candidates[0].registry_evidence == "formally_verified"
    assert lean_candidates[0].execution_ready is True
    assert all(row.language != "lean4" for row in proof.alternatives)

