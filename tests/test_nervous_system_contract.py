from __future__ import annotations

import json
import subprocess
import sys


def test_apex_nervous_system_contract_is_current_and_revisable() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/validate_nervous_system.py", "--freshness"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["status"] == "verified"
    assert payload["source"] == "current_apex_mesh"
    assert payload["selection_mode"] == "CURRENT_BEST_REVISABLE"
    assert payload["apex_role"] == "ACTIVE_POLYGLOT_ENGINEERING_CAPABILITY_DONOR"
    assert payload["manifest_version"] == "2.0.0"
    assert payload["freshness_status"] == "current_fetch"
    assert len(payload["manifest_sha256"]) == 64
