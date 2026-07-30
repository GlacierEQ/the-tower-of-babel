"""Repository-level tests for The Tower of Babel."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from babel_registry import (  # noqa: E402
    BABEL_REGISTRY,
    BabelRegistryEngine,
    query_babel_registry,
)


class TestTowerOfBabel(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = BabelRegistryEngine(REPO_ROOT)

    def test_registry_contains_exactly_21_languages(self) -> None:
        self.assertEqual(len(BABEL_REGISTRY), 21)
        self.assertEqual(
            set(BABEL_REGISTRY),
            {
                "python", "c", "cpp", "rust", "go", "typescript", "cuda",
                "verilog", "r", "julia", "swift", "zig", "odin", "mojo",
                "elixir", "haskell", "lean4", "triton", "protobuf", "sql", "wat",
            },
        )

    def test_every_spec_has_complete_w4h_rationale(self) -> None:
        for key in BABEL_REGISTRY:
            result = self.engine.get_spec(key)
            self.assertTrue(result["ok"], key)
            self.assertEqual(result["status"], "VALIDATED_W4H_SPEC")
            for field in ("what", "where", "when", "why", "how"):
                self.assertGreaterEqual(len(result[field].strip()), 20, f"{key}.{field}")

    def test_layout_matches_registry_exactly(self) -> None:
        report = self.engine.validate_layout()
        self.assertTrue(report["ok"], json.dumps(report, indent=2))
        self.assertEqual(report["language_count"], 21)
        self.assertEqual(report["exhibit_count"], 42)

    def test_easy_and_advanced_exhibits_are_distinct(self) -> None:
        registered_paths: set[str] = set()
        for key, spec in BABEL_REGISTRY.items():
            self.assertNotEqual(spec.easy_exhibit, spec.advanced_exhibit, key)
            self.assertIn("/easy_", spec.easy_exhibit, key)
            self.assertIn("/advanced_", spec.advanced_exhibit, key)
            for path in (spec.easy_exhibit, spec.advanced_exhibit):
                self.assertNotIn(path, registered_paths, path)
                registered_paths.add(path)
        self.assertEqual(len(registered_paths), 42)

    def test_programmatic_query_contract(self) -> None:
        all_specs = query_babel_registry()
        self.assertTrue(all_specs["ok"])
        self.assertEqual(all_specs["status"], "BABEL_REGISTRY_READY")
        self.assertEqual(len(all_specs["languages"]), 21)
        self.assertTrue(all_specs["layout"]["ok"])

        rust = query_babel_registry("rust")
        self.assertTrue(rust["ok"])
        self.assertEqual(rust["extension"], ".rs")

        missing = query_babel_registry("not-a-language")
        self.assertFalse(missing["ok"])
        self.assertEqual(missing["status"], "UNKNOWN_SPEC")

    def test_registry_cli_emits_valid_json(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(REPO_ROOT / "src" / "babel_registry.py")],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "BABEL_REGISTRY_READY")
        self.assertEqual(payload["layout"]["exhibit_count"], 42)


if __name__ == "__main__":
    unittest.main(verbosity=2)
