"""Test suite for The Tower of Babel repository."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from babel_registry import BabelRegistryEngine, BABEL_REGISTRY

class TestTowerOfBabel(unittest.TestCase):

    def setUp(self):
        self.engine = BabelRegistryEngine()
        self.repo_root = Path(__file__).resolve().parent.parent
        self.languages_dir = self.repo_root / "languages"

    def test_registry_count(self):
        self.assertEqual(len(BABEL_REGISTRY), 17)

    def test_w4h_evaluator_all(self):
        for lang_key in BABEL_REGISTRY.keys():
            res = self.engine.get_spec(lang_key)
            self.assertTrue(res["ok"])
            self.assertEqual(res["status"], "VALIDATED_W4H_SPEC")

    def test_language_directories_and_exhibits_exist(self):
        for lang_key, spec in BABEL_REGISTRY.items():
            lang_dir = self.languages_dir / lang_key
            self.assertTrue(lang_dir.is_dir(), f"Missing language directory: {lang_dir}")
            files = list(lang_dir.glob(f"*{spec.extension}")) + list(lang_dir.glob("*.py")) + list(lang_dir.glob("*.proto"))
            self.assertGreaterEqual(len(files), 2, f"Language {lang_key} must have at least easy & advanced exhibits")

if __name__ == "__main__":
    unittest.main()
