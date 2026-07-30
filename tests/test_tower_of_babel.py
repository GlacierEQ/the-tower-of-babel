"""Governance tests for The Tower of Babel repository."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from babel_registry import BABEL_REGISTRY, BabelRegistryEngine
from tower_registry import TowerRegistry, evidence_state_counts


class TestTowerOfBabel(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = BabelRegistryEngine()
        self.registry = TowerRegistry(REPO_ROOT)

    def test_canonical_registry_count(self) -> None:
        self.assertEqual(self.registry.actual_count, self.registry.expected_count)
        self.assertEqual(len(BABEL_REGISTRY), self.registry.expected_count)

    def test_missing_readme_languages_are_governed(self) -> None:
        required = {"python", "c", "r", "verilog"}
        self.assertTrue(required.issubset(set(self.registry.technology_ids())))

    def test_w4h_evaluator_all(self) -> None:
        for lang_key in self.registry.technology_ids():
            result = self.engine.get_spec(lang_key)
            self.assertTrue(result["ok"])
            self.assertEqual(result["status"], "VALIDATED_W4H_SPEC")
            self.assertIn(result["advanced_evidence_state"], self.registry.data["evidence_states"])

    def test_language_directories_and_exhibits_exist(self) -> None:
        result = self.registry.validate(require_files=True)
        self.assertTrue(result.ok, result.errors)

    def test_every_advanced_exhibit_has_evidence_state(self) -> None:
        counts = evidence_state_counts(self.registry.technologies)
        self.assertGreater(sum(counts.values()), 0)
        self.assertEqual(sum(counts.values()), self.registry.expected_count)


if __name__ == "__main__":
    unittest.main()
