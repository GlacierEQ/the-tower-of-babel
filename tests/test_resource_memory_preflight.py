from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tower.resource_memory import build_preflight, inventory_resources, resolve_repo_root, write_preflight


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
    source = root / "artifacts" / "benchmarks" / "p99.json"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text('{"p99_ms": 12.5}\n', encoding="utf-8")
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
    subprocess.run(["git", "config", "user.email", "tower-tests@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Tower Tests"], cwd=root, check=True)
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=root, check=True)
    commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    tree_sha = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=root, text=True).strip()
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
    encoded = json.dumps(body, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    body_sha = hashlib.sha256(encoded).hexdigest()
    receipt = {
        **body,
        "receipt_id": "tower-test",
        "body_sha256": body_sha,
        "receipt_sha256": body_sha,
    }
    path = root / "artifacts" / "tower_receipt.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    matching = [row for row in duplicates if sorted(row["locators"]) == ["archive/one-copy.txt", "docs/one.txt"]]
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
    assert payload["schema"] == "glaciereq.tower.resource-memory-preflight.v3"
    assert payload["status"] == "PARTIAL"
    assert payload["memory_analysis"]["status"] == "ANALYZED"
    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "RECALLED_NEEDS_SOURCE"
    assert finding["source_pointer"] is None
    assert payload["memory_analysis"]["gaps"]
    assert "promotion_gate" not in payload
    controls = payload["continuation_controls"]
    assert controls["mode"] == "ORIENTATION_NOT_PERMISSION"
    assert controls["memory_changes_certainty_not_permission"] is True
    assert controls["default_behavior"] == "CONTINUE_WHILE_MEANINGFUL_ROUTE_EXISTS"


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


def test_caller_cannot_forge_verified_status_with_nonresolving_source(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
    memory.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding": "This points at a file that does not exist.",
                        "status": "VERIFIED_WITH_SOURCE",
                        "source_pointer": "artifacts/missing-proof.json",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = build_preflight("reject fabricated source binding", root=tmp_path, memory_path=memory)

    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "RECALLED_NEEDS_SOURCE"
    assert finding["source_pointer_valid"] is False
    assert finding["source_validation"] == "local source pointer does not resolve to a file"
    assert payload["memory_analysis"]["gaps"]
    assert payload["status"] == "PARTIAL"


def test_commit_source_pointer_must_resolve_in_git_history(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    _init_git_with_release_receipt(tmp_path)
    commit_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True
    ).strip()
    memory = tmp_path / "memory.json"
    memory.write_text(
        json.dumps(
            {
                "findings": [
                    {
                        "finding": "Architecture law exists at the verified checkpoint.",
                        "status": "VERIFIED_WITH_SOURCE",
                        "source_pointer": f"commit:{commit_sha}:ARCHITECTURE_LAW.md",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    payload = build_preflight("verify historical source pointer", root=tmp_path, memory_path=memory)

    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "VERIFIED_WITH_SOURCE"
    assert finding["source_pointer_valid"] is True
    assert finding["source_validation"] == "GIT_OBJECT_RESOLVED"


def test_malformed_only_memory_is_invalid(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
    memory.write_text(json.dumps([42, {"status": "VERIFIED_WITH_SOURCE"}]), encoding="utf-8")

    payload = build_preflight("reject empty continuity", root=tmp_path, memory_path=memory)

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


def test_source_bound_memory_requires_release_receipt_for_complete_state(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)

    without_receipt = build_preflight("evaluate replacement", root=tmp_path, memory_path=memory)
    assert without_receipt["status"] == "PARTIAL"
    assert without_receipt["last_verified_checkpoint"] is None
    assert without_receipt["continuation_controls"]["has_verified_checkpoint"] is False
    assert without_receipt["continuation_controls"]["checkpoint_absence_is_not_execution_veto"] is True

    _init_git_with_release_receipt(tmp_path)
    with_receipt = build_preflight("evaluate replacement", root=tmp_path, memory_path=memory)
    assert with_receipt["status"] == "COMPLETE"
    assert with_receipt["last_verified_checkpoint"]["verification_basis"] == "TOWER_RELEASE_RECEIPT_V2"
    assert with_receipt["delta"]["committed_delta_status"] == "COMPUTED_FROM_VERIFIED_CHECKPOINT"


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

    payload = build_preflight("recover damaged registry", root=tmp_path, memory_path=memory)

    assert payload["state"] == "RESOURCE_RECONSTRUCTED"
    assert "required Tower resource missing: registry/tower.yml" in payload["resource_analysis"]["resource_gaps"]


def test_receipt_does_not_inventory_itself(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)
    output = tmp_path / "artifacts" / "resource-memory-preflight.json"

    first = write_preflight(output, "continue current lane", root=tmp_path, memory_path=memory)
    second = write_preflight(output, "continue current lane", root=tmp_path, memory_path=memory)

    assert first == second
    locators = {row["locator"] for row in second["resource_analysis"]["resources"]}
    assert "artifacts/resource-memory-preflight.json" not in locators


def test_preflight_refuses_to_overwrite_memory_input(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)

    with pytest.raises(ValueError, match="must not overwrite"):
        write_preflight(memory, "protect operator memory", root=tmp_path, memory_path=memory)


def test_orientation_partial_state_is_not_an_execution_veto(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path, include_registry=False)

    payload = build_preflight("continue through partial state", root=tmp_path)

    assert payload["status"] == "PARTIAL"
    assert payload["continuation_controls"]["mode"] == "ORIENTATION_NOT_PERMISSION"
    assert payload["continuation_controls"]["resource_gaps_change_routing_not_global_execution_permission"] is True
    assert payload["continuation_controls"]["checkpoint_absence_is_not_execution_veto"] is True
    orientation = payload["orientation"]
    assert orientation["continuation_state"] == "CONTINUE_WITH_GAPS"
    assert orientation["execution_permission"] == "NOT_EVALUATED_BY_ORIENTATION"
    assert orientation["stop_condition_created"] is False
    assert orientation["recommended_next_route"] == "RECOVER_RESOURCE_GAPS"
    assert orientation["certainty"] == "LOW"
    assert "promotion_gate" not in payload


def test_complete_orientation_points_to_next_frontier(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = _source_bound_memory(tmp_path)
    _init_git_with_release_receipt(tmp_path)
    subprocess.run(["git", "add", "artifacts/tower_receipt.json"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "record verified checkpoint"], cwd=tmp_path, check=True)

    payload = build_preflight("continue strongest lane", root=tmp_path, memory_path=memory)

    orientation = payload["orientation"]
    assert payload["status"] == "COMPLETE"
    assert orientation["continuation_state"] == "CONTINUE"
    assert orientation["certainty"] == "HIGH"
    assert orientation["recommended_next_route"] == "EXECUTE_NEXT_FRONTIER"
    assert orientation["unresolved_count"] == 0


def test_cli_orient_and_legacy_preflight_are_nonblocking(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    from tower.cli import main as tower_main

    _seed_minimal_tower(tmp_path, include_registry=False)
    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tower",
            "orient",
            "--mission",
            "continue despite partial reconstruction",
            "--output",
            "artifacts/orientation.json",
        ],
    )
    assert tower_main() == 0
    orient_payload = json.loads(capsys.readouterr().out)
    assert orient_payload["status"] == "PARTIAL"
    assert orient_payload["orientation"]["stop_condition_created"] is False
    assert orient_payload["orientation"]["execution_permission"] == "NOT_EVALUATED_BY_ORIENTATION"

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "tower",
            "preflight",
            "--mission",
            "legacy caller must also continue",
            "--require-memory",
            "--output",
            "artifacts/legacy-preflight.json",
        ],
    )
    assert tower_main() == 0
    legacy_payload = json.loads(capsys.readouterr().out)
    assert legacy_payload["status"] == "PARTIAL"
    assert legacy_payload["orientation"]["continuation_state"] == "CONTINUE_WITH_GAPS"


def test_repo_root_resolves_from_active_checkout(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    nested = tmp_path / "work" / "deep"
    nested.mkdir(parents=True)
    monkeypatch.chdir(nested)

    assert resolve_repo_root() == tmp_path.resolve()
