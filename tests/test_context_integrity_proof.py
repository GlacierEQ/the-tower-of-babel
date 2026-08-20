from scripts.run_context_integrity_proof import run


def test_context_integrity_proof_binds_registry_integrity_and_receipt():
    receipt = run()

    assert receipt["technology_count"] == 40
    assert receipt["registry_errors"] == []
    assert receipt["integrity_file_count"] > 30
    assert receipt["integrity_verified"] is True
    assert receipt["topology_node_count"] == receipt["technology_count"]
    assert len(receipt["receipt_sha256"]) == 64
    assert "does not compile every technology" in receipt["truth_boundary"]
