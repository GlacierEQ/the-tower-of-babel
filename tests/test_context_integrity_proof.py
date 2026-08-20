from __future__ import annotations

import json

from scripts import run_context_integrity_proof


def test_context_integrity_proof_binds_registry_integrity_and_receipt():
    receipt = run_context_integrity_proof.run()

    assert receipt["status"] == "verified"
    assert receipt["failure_reasons"] == []
    assert receipt["technology_count"] == 40
    assert receipt["registry_errors"] == []
    assert receipt["integrity_file_count"] > 30
    assert receipt["integrity_verified"] is True
    assert receipt["topology_node_count"] == receipt["technology_count"]
    assert len(receipt["receipt_sha256"]) == 64
    assert "does not compile every technology" in receipt["truth_boundary"]


def test_context_integrity_proof_cli_reports_load_failure_with_nonzero_status(monkeypatch, capsys):
    def fail_load_registry():
        raise ValueError("fixture registry is unavailable")

    monkeypatch.setattr(run_context_integrity_proof, "load_registry", fail_load_registry)

    assert run_context_integrity_proof.main([]) == 1

    rendered = json.loads(capsys.readouterr().out)
    assert rendered["status"] == "failed"
    assert rendered["failed_stage"] == "load_registry"
    assert "fixture registry is unavailable" in rendered["error"]
