"""The catalog must resolve to actual callable functions and executable proofs."""

import json
import os
import subprocess
import sys
import unittest
from copy import deepcopy

from tower.algorithm_catalog import (
    list_algorithms,
    load_algorithm_catalog,
    validate_algorithm_catalog,
)
from tower.registry import REPO_ROOT, load_registry


class AlgorithmCatalogTests(unittest.TestCase):
    def test_catalog_resolves_implementations_and_proofs(self):
        catalog = load_algorithm_catalog()
        self.assertEqual(validate_algorithm_catalog(catalog, load_registry()), [])
        exposed = list_algorithms()
        self.assertEqual(exposed["count"], 18)
        self.assertIs(exposed["external_effects"], False)
        self.assertEqual(exposed["benchmark_status"], "NOT_BENCHMARKED_AGAINST_ALTERNATIVES")

    def test_catalog_rejects_unimplemented_algorithm_and_duplicate_id(self):
        original = load_algorithm_catalog()
        modified = deepcopy(original)
        modified["algorithms"][0]["function"] = "imaginary_trading_magic"
        modified["algorithms"][1]["id"] = modified["algorithms"][0]["id"]
        errors = validate_algorithm_catalog(modified, load_registry())
        self.assertTrue(any("approved executable implementation" in error for error in errors))
        self.assertTrue(any("duplicate id" in error for error in errors))

    def test_cli_simulates_fixture_without_broker_and_is_deterministic(self):
        command = [sys.executable, "-m", "tower", "algorithms", "simulate", "examples/market_research_signals.json"]
        environment = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
        first = subprocess.run(command, cwd=REPO_ROOT, env=environment, capture_output=True, text=True, check=True)
        second = subprocess.run(command, cwd=REPO_ROOT, env=environment, capture_output=True, text=True, check=True)
        self.assertEqual(first.stdout, second.stdout)
        result = json.loads(first.stdout)
        self.assertEqual(result["initial_capital"], 59.0)
        self.assertEqual(result["schema"], "glaciereq.tower.market-backtest.v1")
        self.assertEqual([fill["fill_index"] for fill in result["fills"]], [2, 5])

    def test_cli_rejects_invalid_market_dataset(self):
        environment = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, "-m", "tower", "algorithms", "simulate", "examples/tower-portfolio-demand.json"],
            cwd=REPO_ROOT, env=environment, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported market research dataset schema", result.stdout)


if __name__ == "__main__":
    unittest.main()
