"""The catalog must resolve to actual callable functions and executable proofs."""

import json
import os
import subprocess
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from tower.algorithm_catalog import (
    PACKAGED_CATALOG,
    REPOSITORY_CATALOG,
    execute_algorithm,
    list_algorithms,
    load_algorithm_catalog,
    validate_algorithm_catalog,
)
from tower.cli import _read_json_object
from tower.registry import REPO_ROOT, load_registry


class AlgorithmCatalogTests(unittest.TestCase):
    def test_catalog_resolves_implementations_and_proofs(self):
        catalog = load_algorithm_catalog()
        self.assertEqual(validate_algorithm_catalog(catalog, load_registry()), [])
        exposed = list_algorithms()
        self.assertEqual(exposed["count"], 18)
        self.assertIs(exposed["external_effects"], False)
        self.assertEqual(exposed["benchmark_status"], "NOT_BENCHMARKED_AGAINST_ALTERNATIVES")
        self.assertEqual(REPOSITORY_CATALOG.read_bytes(), PACKAGED_CATALOG.read_bytes())

    def test_packaged_catalog_validates_without_source_test_checkout(self):
        packaged = load_algorithm_catalog(PACKAGED_CATALOG)
        with patch("tower.algorithm_catalog.REPOSITORY_CATALOG", Path("/no-source-checkout/registry/algorithm_catalog.json")):
            self.assertEqual(validate_algorithm_catalog(packaged, load_registry()), [])

    def test_catalog_rejects_unimplemented_algorithm_and_duplicate_id(self):
        original = load_algorithm_catalog()
        modified = deepcopy(original)
        modified["algorithms"][0]["function"] = "imaginary_trading_magic"
        modified["algorithms"][1]["id"] = modified["algorithms"][0]["id"]
        errors = validate_algorithm_catalog(modified, load_registry())
        self.assertTrue(any("approved executable implementation" in error for error in errors))
        self.assertTrue(any("duplicate id" in error for error in errors))
        modified = deepcopy(original)
        modified["algorithms"][0]["module"] = []
        modified["algorithms"][1]["domain"] = []
        modified["algorithms"][2]["id"] = "MATH.ONLINE_MOMENTS"
        errors = validate_algorithm_catalog(modified, load_registry())
        self.assertTrue(any("approved executable implementation" in error for error in errors))
        self.assertTrue(any("unknown domain" in error for error in errors))
        self.assertTrue(any("duplicate id" in error for error in errors))

    def test_invalid_catalog_fails_cleanly_when_listed(self):
        with patch("tower.algorithm_catalog.load_algorithm_catalog", return_value={"schema": "bad"}):
            with self.assertRaisesRegex(ValueError, "invalid algorithm catalog"):
                list_algorithms()

    def test_agent_json_rejects_files_over_declared_limit(self):
        with self.assertRaisesRegex(ValueError, "byte safety limit"):
            _read_json_object(REPO_ROOT / "examples/market_algorithm_request.json", "request", max_bytes=4)

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

    def test_json_execution_runs_registered_algorithm(self):
        environment = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
        result = subprocess.run(
            [sys.executable, "-m", "tower", "algorithms", "run", "examples/market_algorithm_request.json"],
            cwd=REPO_ROOT, env=environment, capture_output=True, text=True, check=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["algorithm_id"], "market.simple_moving_average")
        self.assertFalse(payload["external_effects"])
        self.assertEqual(payload["result"], [None, None, 101.0, 102.66666666666667, 105.33333333333333])

    def test_json_execution_supports_polynomial_roots_without_code_evaluation(self):
        payload = execute_algorithm("math.bisect_root", {
            "coefficients": [1, 0, -2], "lower": 1, "upper": 2,
        })
        self.assertAlmostEqual(payload["result"]["root"], 2**0.5, places=9)
        self.assertLess(abs(payload["result"]["residual"]), 1e-8)

    def test_json_execution_rejects_unknown_or_untrusted_parameters(self):
        with self.assertRaisesRegex(ValueError, "unknown algorithm"):
            execute_algorithm("market.send_order", {})
        with self.assertRaisesRegex(ValueError, "invalid algorithm arguments"):
            execute_algorithm("market.simple_returns", {"command": "trade"})
        with self.assertRaisesRegex(ValueError, "polynomial coefficients"):
            execute_algorithm("math.bisect_root", {"coefficients": ["__import__('os')"], "lower": 0, "upper": 1})


if __name__ == "__main__":
    unittest.main()
