from __future__ import annotations

from pathlib import Path

from tower.integrity import DEFAULT_SNAPSHOT, LEGACY_MANIFEST, verify_integrity, write_manifest


def test_live_integrity_uses_current_git_head_not_static_baseline() -> None:
    result = verify_integrity()
    assert result["mode"] == "GIT_INDEX_LIVE"
    assert result["selection_mode"] == "CURRENT_HEAD_REVISABLE"
    assert result["ok"] is True
    assert result["status"] == "VERIFIED"
    assert len(result["commit_sha"]) == 40
    assert len(result["tree_sha"]) == 40
    assert len(result["tree_listing_sha256"]) == 64
    assert len(result["receipt_sha256"]) == 64
    assert result["changed"] == []
    assert result["unexpected"] == []
    assert not LEGACY_MANIFEST.exists()


def test_explicit_snapshot_remains_available_as_evidence(tmp_path: Path) -> None:
    path = tmp_path / "integrity-snapshot.json"
    snapshot = write_manifest(path)
    assert snapshot["mode"] == "EXPLICIT_EVIDENCE_SNAPSHOT"
    assert snapshot["schema_version"] == "2.0.0"
    result = verify_integrity(path)
    assert result["mode"] == "EXPLICIT_EVIDENCE_SNAPSHOT"
    assert result["ok"] is True


def test_default_snapshot_target_is_artifact_not_control_plane() -> None:
    assert DEFAULT_SNAPSHOT.parts[-2:] == ("artifacts", "integrity-snapshot.json")
