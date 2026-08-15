import json
from pathlib import Path

import pytest

from tower.integrity import _load_delta


def write_delta(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_reviewed_delta_overlays_exact_changes_and_removals(tmp_path: Path):
    base_digest = "a" * 64
    baseline = {"old.txt": "1" * 64, "keep.txt": "2" * 64}
    delta = write_delta(
        tmp_path / "delta.json",
        {
            "schema": "glaciereq.integrity-delta.v1",
            "base_manifest_sha256": base_digest,
            "changes": {"keep.txt": "3" * 64, "new.txt": "4" * 64},
            "removals": ["old.txt"],
            "resulting_file_count": 2,
        },
    )

    resolved, receipt = _load_delta(
        delta,
        base_manifest_sha256=base_digest,
        expected_hashes=baseline,
    )

    assert resolved == {"keep.txt": "3" * 64, "new.txt": "4" * 64}
    assert receipt["applied"] is True
    assert receipt["change_count"] == 2
    assert receipt["removal_count"] == 1


def test_delta_rejects_wrong_base_manifest(tmp_path: Path):
    delta = write_delta(
        tmp_path / "delta.json",
        {
            "schema": "glaciereq.integrity-delta.v1",
            "base_manifest_sha256": "a" * 64,
            "changes": {},
            "removals": [],
            "resulting_file_count": 0,
        },
    )
    with pytest.raises(ValueError, match="not bound"):
        _load_delta(
            delta,
            base_manifest_sha256="b" * 64,
            expected_hashes={},
        )


def test_delta_cannot_self_approve_governance_manifests(tmp_path: Path):
    delta = write_delta(
        tmp_path / "delta.json",
        {
            "schema": "glaciereq.integrity-delta.v1",
            "base_manifest_sha256": "a" * 64,
            "changes": {".integrity/approved_delta.json": "1" * 64},
            "removals": [],
            "resulting_file_count": 1,
        },
    )
    with pytest.raises(ValueError, match="invalid integrity delta change"):
        _load_delta(
            delta,
            base_manifest_sha256="a" * 64,
            expected_hashes={},
        )
