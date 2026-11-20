from __future__ import annotations

import json
import subprocess
import sys


def test_apex_nervous_system_contract_is_current_or_source_bound_and_revisable() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_nervous_system.py", "--freshness"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "verified"
    assert payload["selection_mode"] == "CURRENT_BEST_REVISABLE"
    assert payload["apex_role"] == "ACTIVE_POLYGLOT_ENGINEERING_CAPABILITY_DONOR"
    assert payload["manifest_version"] == "2.1.0"

    if payload["source"] == "current_apex_mesh":
        assert payload["freshness_status"] == "current_fetch"
        assert len(payload["manifest_sha256"]) == 64
    else:
        assert payload["source"] == "private_source_checkpoint"
        assert payload["freshness_status"] == "checkpoint_within_horizon"
        assert len(payload["observed_commit"]) == 40
        assert len(payload["observed_blob_sha"]) == 40
        assert len(payload["verified_summary_sha256"]) == 64
        assert payload["checkpoint_age_hours"] <= payload["checkpoint_max_age_hours"]


def test_local_tower_contract_cannot_reintroduce_execution_gate() -> None:
    payload = json.loads(open(".glaciereq/nervous-system.node.json", encoding="utf-8").read())
    assert "resource_memory_preflight" not in payload
    orientation = payload["resource_memory_orientation"]
    assert orientation["mode"] == "ORIENTATION_NOT_PERMISSION"
    assert orientation["required_before_mutation"] is False
    assert orientation["partial_state_changes_certainty_not_execution_permission"] is True
    assert orientation["missing_checkpoint_is_not_execution_veto"] is True
    assert orientation["default_continuation"] == "CONTINUE_WHILE_MEANINGFUL_ROUTE_EXISTS"
    assert orientation["command"].startswith("tower orient ")
    assert orientation["legacy_command"].startswith("tower preflight ")
    assert orientation["receipt"] == "artifacts/resource-memory-orientation.json"
    assert orientation["orientation_can_stop_execution"] is False
    assert orientation["execution_permission_source"] == "OUTSIDE_ORIENTATION"
    assert "certainty" in orientation["continuation_telemetry"]
    assert "recommended_next_route" in orientation["continuation_telemetry"]
