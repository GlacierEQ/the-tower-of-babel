from __future__ import annotations

from tower.receipt import build_receipt
from tower.registry import REPO_ROOT, load_registry


def complete_build_report() -> dict:
    technologies = load_registry().technologies
    return {
        "counts": {"VERIFIED": len(technologies)},
        "results": [
            {"technology_id": technology["id"], "status": "VERIFIED"}
            for technology in technologies
        ],
    }


def test_release_receipt_binds_live_git_integrity_identity() -> None:
    receipt = build_receipt(complete_build_report())
    integrity = receipt["integrity"]

    assert receipt["schema_version"] == "2.0.0"
    assert receipt["integrity_valid"] is True
    assert receipt["integrity_errors"] == []
    assert receipt["integrity_mode"] == "GIT_INDEX_LIVE"
    assert receipt["integrity_identity_sha256"] == integrity["receipt_sha256"]
    assert receipt["integrity_commit_sha"] == integrity["commit_sha"]
    assert receipt["integrity_tree_sha"] == integrity["tree_sha"]
    assert len(receipt["integrity_identity_sha256"]) == 64
    assert receipt["integrity_identity_sha256"][:12] in receipt["receipt_id"]
    assert "integrity_manifest_sha256" not in receipt


def test_release_receipt_is_deterministic_for_same_head_and_report() -> None:
    report = complete_build_report()
    first = build_receipt(report)
    second = build_receipt(report)
    assert first == second


def test_protobuf_receipt_contract_preserves_wire_number_with_new_identity_name() -> None:
    proto = (REPO_ROOT / "proto" / "tower.proto").read_text(encoding="utf-8")
    assert "string integrity_identity_sha256 = 3;" in proto
    assert "string integrity_manifest_sha256 = 3;" not in proto
    assert "string integrity_commit_sha = 7;" in proto
    assert "string integrity_tree_sha = 8;" in proto
    assert "string integrity_mode = 9;" in proto
    assert "service TowerSelectionService" in proto
    assert "service TowerAuthority" in proto
    assert "option deprecated = true;" in proto
