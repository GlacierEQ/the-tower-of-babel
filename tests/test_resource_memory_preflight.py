from __future__ import annotations

import json
from pathlib import Path

from tower.resource_memory import build_preflight, inventory_resources


def _seed_minimal_tower(root: Path) -> None:
    required = [
        "registry/tower.yml",
        "ARCHITECTURE_LAW.md",
        "NERVOUS_SYSTEM.md",
        "src/tower/registry.py",
        "src/tower/proofs.py",
        "src/tower/integrity.py",
    ]
    for relative in required:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"seed:{relative}\n", encoding="utf-8")


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
    assert payload["memory_analysis"]["status"] == "ANALYZED"
    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "RECALLED_NEEDS_SOURCE"
    assert finding["source_pointer"] is None
    assert payload["promotion_gate"]["may_use_memory_as_proof_without_source"] is False


def test_source_bound_memory_is_preserved_as_verified_input(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)
    memory = tmp_path / "memory.json"
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

    payload = build_preflight("evaluate replacement", root=tmp_path, memory_path=memory)

    assert payload["status"] == "COMPLETE"
    finding = payload["memory_analysis"]["findings"][0]
    assert finding["status"] == "VERIFIED_WITH_SOURCE"
    assert finding["source_pointer"] == "artifacts/benchmarks/p99.json"
    assert payload["resource_analysis"]["resource_gaps"] == []


def test_missing_memory_is_explicit_not_silent(tmp_path: Path) -> None:
    _seed_minimal_tower(tmp_path)

    payload = build_preflight("inspect existing lane", root=tmp_path)

    assert payload["status"] == "PARTIAL"
    assert payload["memory_analysis"]["status"] == "NOT_PROVIDED"
    assert payload["memory_analysis"]["gaps"]
    assert payload["tower_boundary"]["owns_operator_memory"] is False
