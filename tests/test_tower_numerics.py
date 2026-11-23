"""Executable numeric baselines, properties, and rejection cases."""

import math
import unittest
from itertools import repeat

from tower.numerics import bisect_root, linear_quantile, online_covariance, online_moments


class NumericalAlgorithmsTests(unittest.TestCase):
    def test_moments_bessel_and_population(self):
        sample = online_moments([1, 2, 3, 4, 5])
        self.assertEqual(sample.count, 5)
        self.assertAlmostEqual(sample.mean, 3.0)
        self.assertAlmostEqual(sample.variance, 2.5)
        self.assertAlmostEqual(online_moments(iter([1, 2, 3, 4, 5]), ddof=0).variance, 2.0)

    def test_constant_moments_and_large_offset(self):
        self.assertEqual(online_moments([7.0] * 20).variance, 0.0)
        sample = online_moments([1e9 + k for k in range(5)])
        self.assertAlmostEqual(sample.mean, 1e9 + 2)
        self.assertAlmostEqual(sample.variance, 2.5)

    def test_covariance_sign_and_length(self):
        self.assertAlmostEqual(online_covariance([1, 2, 3], [2, 4, 6]), 2.0)
        self.assertAlmostEqual(online_covariance([1, 2, 3], [3, 2, 1]), -1.0)
        self.assertAlmostEqual(online_covariance([1, 2, 3], [2, 4, 6], ddof=0), 4 / 3)
        with self.assertRaises(ValueError):
            online_covariance([1, 2], [3])

    def test_linear_quantile_type_seven(self):
        samples = [4, 1, 3, 2]
        self.assertEqual(linear_quantile(samples, 0), 1)
        self.assertEqual(linear_quantile(samples, 1), 4)
        self.assertAlmostEqual(linear_quantile(samples, 0.25), 1.75)
        self.assertAlmostEqual(linear_quantile(samples, 0.5), 2.5)
        self.assertEqual(linear_quantile([7], 0.2), 7)
        self.assertEqual(linear_quantile([0.0003, 0.0003], 0.95), 0.0003)

    def test_bisection_bracket_convergence(self):
        result = bisect_root(lambda x: x * x - 2, 1, 2, absolute_tolerance=1e-12)
        self.assertAlmostEqual(result.root, math.sqrt(2), places=11)
        self.assertLess(abs(result.residual), 1e-10)
        self.assertGreater(result.iterations, 0)
        self.assertEqual(bisect_root(lambda x: x - 1, 1, 2).iterations, 0)

    def test_bisection_fail_closed(self):
        for call in (
            lambda: bisect_root(lambda x: x * x + 1, -1, 1),
            lambda: bisect_root(lambda x: float("nan"), 0, 2),
            lambda: bisect_root(lambda x: x - 1, 2, 0),
            lambda: bisect_root(lambda x: x - 0.3, 0, 1, max_iterations=1, absolute_tolerance=1e-50),
        ):
            with self.assertRaises(ValueError):
                call()

    def test_invalid_numbers_and_samples_rejected(self):
        for call in (
            lambda: online_moments([]),
            lambda: online_moments([5]),
            lambda: online_moments([1, float("nan")]),
            lambda: online_moments([True, 2]),
            lambda: online_moments(["3.5", 2]),
            lambda: linear_quantile(["3.5", 2], 0.5),
            lambda: linear_quantile(repeat(1.0, 1_000_001), 0.5),
            lambda: online_moments([1, 2], ddof=3),
            lambda: online_moments([1, 2], ddof=True),
            lambda: online_covariance([1, 2], [3, 4], ddof=False),
            lambda: online_covariance([True, 2], [3, 4]),
            lambda: online_covariance(["1", 2], [3, 4]),
            lambda: online_covariance([1, float('nan')], [3, 4]),
            lambda: linear_quantile([1, float("inf")], 0.5),
            lambda: linear_quantile([1, 2], -0.2),
        ):
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
