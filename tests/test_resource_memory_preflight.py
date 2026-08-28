from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tower.resource_memory import (
    build_preflight,
    inventory_resources,
    resolve_repo_root,
    write_preflight,
)


def _seed_minimal_tower(root: Path, *, include_registry: bool = True) -> None:
    required = [
        "ARCHITECTURE_LAW.md",
        "NERVOUS_SYSTEM.md",
        "src/tower/registry.py",
        "src/tower/proofs.py",
        "src/tower/integrity.py",
    ]
    if include_registry:
        required.append("registry/tower.yml")
    for relative in required:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"seed:{relative}\n", encoding="utf-8")


def _source_bound_memory(root: Path) -> Path:
    memory = root / "memory.json"
    memory.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding": "The incumbent benchmark won on p99 latency.",
                        "status": "VERIFIED_WITH_SOURCE",
                        "source_pointer": "artifacts/benchmarks/p99.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    return memory


def _init_git_with_release_receipt(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "tower-tests@example.invalid"],
        cwd=root,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "Tower Tests"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    commit_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    tree_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD^{tree}"], cwd=root, text=True
    ).strip()
    body = {
        "schema_version": "2.0.0",
        "tower_id": "test-tower",
        "registry_sha256": "a" * 64,
        "integrity_identity_sha256": "b" * 64,
        "integrity_mode": "GIT_INDEX_LIVE",
        "integrity_commit_sha": commit_sha,
        "integrity_tree_sha": tree_sha,
        "build_report_sha256": "c" * 64,
        "technology_count": 1,
        "registry_valid": True,
        "integrity_valid": True,
        "build_report_valid": True,
        "validation_errors": [],
        "integrity_errors": [],
        "build_report_errors": [],
        "integrity": {},
        "build_summary": {},
    }
    encoded = json.dumps(
        body, separators=(",", ":"), sort_keys=True, ensure_ascii=False
    ).encode("utf-8")
    body_sha = hashlib.sha256(encoded).hexdigest()
    receipt = {
        **body,
        "receipt_id": "tower-test",
        "body_sha256": body_sha,
        "receipt_sha256": body_sha,
    }
    path = root / "artifacts" / "tower_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def test_inventory_collapses_identical_bytes(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    first = tmp_path / "docs" / "one.txt"
    second = tmp_path / "archive" / "one-copy.txt"
    first.parent.mkdir(parents=True, exist_ok=True)
    second.parent.mkdir(parents=True, exist_ok=True)
    first.write_text("same bytes\n", encoding="utf-8")
    second.write_text("same bytes\n", encoding="utf-8")

    resources, duplicates = inventory_resources(tmp_path)

    assert len(resources) == 8
    matching = [
        row
        for row in duplicates
        if sorted(row["locators"]) == ["archive/one-copy.txt", "docs/one.txt"]
    ]
    assert len(matching) == 1
    assert matching[0]["independent_sources"] == 1


def test_memory_without_source_remains_unverified(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
    memory.write_text(
        json.dumps({"findings": [{"finding": "Rust previously won this lane."}]}),
        encoding="utf-8",
    )

    payload = build_preflight("compare lane owner", root=tmp_path, memory_path=memory)

    assert payload["state"] == "RESOURCE_RECONSTRUCTED"
    assert payload["status"] == "PARTIAL"
    assert payload["memory_analysis"]["status"] == "ANALYZED"
    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "RECALLED_NEEDS_SOURCE"
    assert finding["source_pointer"] is None
    assert payload["memory_analysis"]["gaps"]
    assert payload["promotion_gate"]["may_use_memory_as_proof_without_source"] is False


def test_caller_cannot_forge_verified_status_without_source(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
    memory.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding": "This claims proof without a source.",
                        "status": "VERIFIED_WITH_SOURCE",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = build_preflight("reject false proof", root=tmp_path, memory_path=memory)

    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "RECALLED_NEEDS_SOURCE"
    assert payload["memory_analysis"]["gaps"]
    assert payload["status"] == "PARTIAL"


def test_malformed_only_memory_is_invalid(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
    memory.write_text(
        json.dumps([42, {"status": "VERIFIED_WITH_SOURCE"}]), encoding="utf-8"
    )

    payload = build_preflight(
        "reject empty continuity", root=tmp_path, memory_path=memory
    )

    assert payload["memory_analysis"]["status"] == "INVALID"
    assert "no analyzable findings" in payload["memory_analysis"]["gaps"][0]
    assert payload["status"] == "PARTIAL"


def test_superseded_memory_state_is_not_resurrected(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
    memory.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding": "An older placement was superseded.",
                        "status": "SUPERSEDED",
                        "source_pointer": "history/old-placement.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = build_preflight("preserve state", root=tmp_path, memory_path=memory)

    assert payload["memory_analysis"]["findings"][0]["status"] == "SUPERSEDED"


def test_source_bound_memory_requires_release_receipt_for_complete_state(
    tmp_path: Path,
) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)

    without_receipt = build_preflight(
        "evaluate replacement", root=tmp_path, memory_path=memory
    )
    assert without_receipt["status"] == "PARTIAL"
    assert without_receipt["last_verified_checkpoint"] is None
    assert without_receipt["promotion_gate"]["has_verified_checkpoint"] is False

    _init_git_with_release_receipt(tmp_path)
    with_receipt = build_preflight(
        "evaluate replacement", root=tmp_path, memory_path=memory
    )
    assert with_receipt["status"] == "COMPLETE"
    assert (
        with_receipt["last_verified_checkpoint"]["verification_basis"]
        == "TOWER_RELEASE_RECEIPT_V2"
    )
    assert (
        with_receipt["delta"]["committed_delta_status"]
        == "COMPUTED_FROM_VERIFIED_CHECKPOINT"
    )


def test_missing_memory_is_explicit_not_silent(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)

    payload = build_preflight("inspect existing lane", root=tmp_path)

    assert payload["status"] == "PARTIAL"
    assert payload["memory_analysis"]["status"] == "NOT_PROVIDED"
    assert payload["memory_analysis"]["gaps"]
    assert payload["tower_boundary"]["owns_operator_memory"] is False


def test_preflight_survives_missing_registry(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path, include_registry=False)
    memory = _source_bound_memory(tmp_path)

    payload = build_preflight(
        "recover damaged registry", root=tmp_path, memory_path=memory
    )

    assert payload["state"] == "RESOURCE_RECONSTRUCTED"
    assert (
        "required Tower resource missing: registry/tower.yml"
        in payload["resource_analysis"]["resource_gaps"]
    )


def test_receipt_does_not_inventory_itself(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)
    output = tmp_path / "artifacts" / "resource-memory-preflight.json"

    first = write_preflight(
        output, "continue current lane", root=tmp_path, memory_path=memory
    )
    second = write_preflight(
        output, "continue current lane", root=tmp_path, memory_path=memory
    )

    assert first == second
    locators = {row["locator"] for row in second["resource_analysis"]["resources"]}
    assert "artifacts/resource-memory-preflight.json" not in locators


def test_preflight_refuses_to_overwrite_memory_input(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)

    with pytest.raises(ValueError, match="must not overwrite"):
        write_preflight(
            memory, "protect operator memory", root=tmp_path, memory_path=memory
        )


def test_repo_root_resolves_from_active_checkout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _seed_minimal_tower(tmp_path)
    nested = tmp_path / "work" / "deep"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    assert resolve_repo_root() == tmp_path.resolve()
