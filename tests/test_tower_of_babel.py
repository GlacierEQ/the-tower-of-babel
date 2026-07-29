"""Manifest-governed test suite for The Tower of Babel."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from babel_registry import BABEL_REGISTRY, EXPECTED_LANGUAGE_IDS, BabelRegistryEngine


class TestTowerOfBabel(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads((ROOT / "registry" / "languages.json").read_text(encoding="utf-8"))
        cls.languages = cls.manifest["languages"]
        cls.by_id = {item["id"]: item for item in cls.languages}
        cls.engine = BabelRegistryEngine()

    def test_manifest_is_the_registry_source_of_truth(self) -> None:
        manifest_ids = tuple(item["id"] for item in self.languages)
        self.assertEqual(EXPECTED_LANGUAGE_IDS, manifest_ids)
        self.assertEqual(tuple(BABEL_REGISTRY), manifest_ids)
        self.assertEqual(len(BABEL_REGISTRY), 21)

    def test_w4h_registry_for_every_language(self) -> None:
        for language_id in EXPECTED_LANGUAGE_IDS:
            result = self.engine.get_spec(language_id)
            self.assertTrue(result["ok"], language_id)
            self.assertEqual(result["status"], "VALIDATED_W4H_SPEC")
            for key in ("what", "where", "when", "why", "how"):
                self.assertTrue(result[key].strip(), f"{language_id}.{key}")

    def test_language_exhibits_exist(self) -> None:
        for item in self.languages:
            for kind in ("easy", "advanced"):
                path = ROOT / item["examples"][kind]
                self.assertTrue(path.is_file(), f"Missing {item['id']} {kind} exhibit: {path}")

    def test_build_interfaces_maturity_and_links_are_complete(self) -> None:
        allowed_maturity = set(self.manifest["policies"]["maturity_levels"])
        for item in self.languages:
            build = item["build"]
            for key in ("toolchain", "check", "run_easy", "run_advanced", "ci_tier"):
                self.assertTrue(str(build[key]).strip(), f"{item['id']}.build.{key}")
            self.assertGreaterEqual(len(item["interfaces"]), 1, item["id"])
            self.assertIn(item["maturity"]["level"], allowed_maturity)
            self.assertGreaterEqual(len(item["links"]), 2, item["id"])
            for link in item["links"]:
                self.assertTrue(link["url"].startswith("https://"), link)

    def test_mesh_registration_metadata_is_unique_and_truthful(self) -> None:
        spiral_ids = [item["spiral_engine"]["capability_id"] for item in self.languages]
        self.assertEqual(len(spiral_ids), len(set(spiral_ids)))
        for item in self.languages:
            self.assertIn(
                item["smithery"]["registration_status"],
                {"declared-not-published", "published", "not-applicable"},
            )
            self.assertTrue(item["spiral_engine"]["pillar"])
            self.assertTrue(item["spiral_engine"]["piston"])
            self.assertGreaterEqual(len(item["spiral_engine"]["evidence_required"]), 3)

    def test_generated_artifacts_are_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "generate.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_generated_indexes_cover_every_language(self) -> None:
        paths = (
            "generated/build_commands.json",
            "generated/interfaces.json",
            "generated/maturity.json",
            "generated/smithery.registry.json",
            "generated/spiral-engine.registry.json",
        )
        expected = set(EXPECTED_LANGUAGE_IDS)
        for relative in paths:
            payload = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            rows = payload.get("languages") or payload.get("capabilities")
            actual = {row.get("id") or row.get("language_id") for row in rows}
            self.assertEqual(actual, expected, relative)

    def test_readme_has_one_generated_section_of_each_type(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "<!-- BEGIN GENERATED:LANGUAGE_MATRIX -->",
            "<!-- END GENERATED:LANGUAGE_MATRIX -->",
            "<!-- BEGIN GENERATED:LINK_LIBRARY -->",
            "<!-- END GENERATED:LINK_LIBRARY -->",
        ):
            self.assertEqual(readme.count(marker), 1, marker)
        for item in self.languages:
            self.assertIn(f"**{item['name']}**", readme)


if __name__ == "__main__":
    unittest.main()
