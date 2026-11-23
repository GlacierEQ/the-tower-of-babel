"""Market formula fixtures, risk invariants, latency and cost counterexamples."""

import math
import random
import unittest

from tower.market_algorithms import (
    annualized_volatility,
    black_scholes_european,
    black_scholes_implied_volatility,
    cumulative_vwap,
    exponential_moving_average,
    gbm_terminal_prices,
    historical_var_expected_shortfall,
    log_returns,
    maximum_drawdown,
    order_book_imbalance,
    simple_moving_average,
    simple_returns,
    simulate_long_only,
    wilder_rsi,
)


class MarketAlgorithmsTests(unittest.TestCase):
    def test_returns(self):
        self.assertAlmostEqual(simple_returns([100, 110, 99])[0], 0.1)
        self.assertAlmostEqual(simple_returns([100, 110, 99])[1], -0.1)
        self.assertAlmostEqual(log_returns([100, 110])[0], math.log(1.1))
        self.assertAlmostEqual(log_returns([100, 110, 99])[1], math.log(0.9))
        self.assertAlmostEqual(log_returns([1e-300, 1e300])[0], 600 * math.log(10))

    def test_moving_averages_warmup(self):
        self.assertEqual(simple_moving_average([1, 2, 3, 4], 2), (None, 1.5, 2.5, 3.5))
        self.assertEqual(exponential_moving_average([1, 2, 3], 3), (1.0, 1.5, 2.25))
        self.assertEqual(simple_moving_average([1, 2], 5), (None, None))

    def test_wilder_rsi_known_edges(self):
        self.assertEqual(wilder_rsi([10, 10, 10, 10, 10], 3), (None, None, None, 50, 50))
        self.assertEqual(wilder_rsi([1, 2, 3, 4, 5], 3)[-1], 100)
        self.assertEqual(wilder_rsi([5, 4, 3, 2, 1], 3)[-1], 0)
        mixed = wilder_rsi([10, 12, 11, 13, 10, 14], 3)
        self.assertEqual(len(mixed), 6)
        self.assertTrue(all(0 <= v <= 100 for v in mixed if v is not None))

    def test_vwap_and_order_book_microstructure(self):
        self.assertEqual(cumulative_vwap([100, 110, 90], [1, 3, 0]), (100, 107.5, 107.5))
        self.assertEqual(cumulative_vwap([100, 110], [0, 1]), (None, 110))
        self.assertAlmostEqual(order_book_imbalance([(99, 20), (98, 10)], [(100, 10)]), 0.5)
        self.assertEqual(order_book_imbalance([(99, 10)], [(100, 10)]), 0)

    def test_black_scholes_reference_and_put_call_parity(self):
        call = black_scholes_european(100, 100, 1, 0.2, 0.05)
        put = black_scholes_european(100, 100, 1, 0.2, 0.05, option_type="put")
        self.assertAlmostEqual(call, 10.450583572185565, places=9)
        self.assertAlmostEqual(put, 5.573526022256971, places=9)
        self.assertAlmostEqual(call - put, 100 - 100 * math.exp(-0.05), places=9)
        self.assertEqual(black_scholes_european(120, 100, 0, 0.2, 0.05), 20)
        self.assertEqual(black_scholes_european(80, 100, 0, 0.2, 0.05), 0)
        self.assertAlmostEqual(black_scholes_european(100, 100, 1, 0, 0.05), 100 * (1 - math.exp(-0.05)))
        self.assertAlmostEqual(black_scholes_implied_volatility(call, 100, 100, 1, 0.05), 0.2, places=8)
        self.assertAlmostEqual(black_scholes_implied_volatility(put, 100, 100, 1, 0.05, option_type="put"), 0.2, places=8)

    def test_drawdown_and_volatility(self):
        self.assertAlmostEqual(maximum_drawdown([100, 120, 90, 108]), 0.25)
        self.assertEqual(maximum_drawdown([1, 2, 3]), 0)
        self.assertAlmostEqual(annualized_volatility([0.01, -0.01]), math.sqrt(0.0002 * 252))

    def test_historical_var_es(self):
        var, es = historical_var_expected_shortfall([-0.1, -0.05, 0, 0.02, 0.03], confidence=0.8)
        self.assertAlmostEqual(var, 0.06)
        self.assertAlmostEqual(es, 0.1)
        self.assertGreaterEqual(es, var)
        self.assertEqual(historical_var_expected_shortfall([0.01, 0.03, 0.02]), (0, 0))

    def test_gbm_reproducible_and_not_market_data(self):
        first = gbm_terminal_prices(100, 0.05, 0.2, 1, paths=20, seed=123)
        self.assertEqual(first, gbm_terminal_prices(100, 0.05, 0.2, 1, paths=20, seed=123))
        self.assertNotEqual(first, gbm_terminal_prices(100, 0.05, 0.2, 1, paths=20, seed=124))
        self.assertEqual(gbm_terminal_prices(100, 0, 0, 1, paths=3), (100, 100, 100))

    def test_backtest_signal_acts_only_on_next_bar(self):
        result = simulate_long_only([100, 110, 120, 100], [1, 1, 0, 1], initial_capital=59)
        self.assertEqual([fill.side for fill in result.fills], ["BUY", "SELL"])
        self.assertEqual([fill.fill_index for fill in result.fills], [1, 3])
        self.assertEqual(result.equity_curve[0], 59)
        self.assertAlmostEqual(result.equity_curve[1], 59)
        self.assertAlmostEqual(result.equity_curve[2], 59 * 120 / 110)
        self.assertAlmostEqual(result.final_equity, 59 * 100 / 110)
        self.assertEqual(result.schema, "glaciereq.tower.market-backtest.v1")

    def test_backtest_costs_monotonically_hurt_identical_strategy(self):
        prices = [100, 101, 102, 100, 99, 103]
        positions = [1, 1, 0, 0, 1, 1]
        clean = simulate_long_only(prices, positions, initial_capital=59)
        with_costs = simulate_long_only(prices, positions, initial_capital=59, fee_bps=10, slippage_bps=20)
        self.assertLess(with_costs.final_equity, clean.final_equity)
        self.assertGreater(sum(fill.fee_paid for fill in with_costs.fills), 0)
        self.assertEqual(len(with_costs.equity_curve), len(prices))

    def test_no_same_bar_execution_or_unbounded_leverage(self):
        result = simulate_long_only([100, 200], [0, 1], initial_capital=59)
        self.assertEqual(result.fills, ())  # final signal cannot fill in history
        self.assertEqual(result.final_equity, 59)
        expensive = simulate_long_only([1000, 1100, 1200], [1, 1, 0], initial_capital=59)
        self.assertGreater(expensive.fills[0].shares, 0)  # simulated fractional shares
        self.assertLess(expensive.fills[0].shares, 1)

    def test_randomized_delayed_fills_and_positive_equity(self):
        generator = random.Random(20261123)
        for _ in range(30):
            closes = [100.0]
            for _ in range(39):
                closes.append(closes[-1] * generator.uniform(0.85, 1.15))
            positions = [generator.randrange(2) for _ in closes]
            result = simulate_long_only(closes, positions, fee_bps=12, slippage_bps=15)
            self.assertEqual(len(result.equity_curve), len(closes))
            self.assertTrue(all(math.isfinite(value) and value > 0 for value in result.equity_curve))
            self.assertTrue(all(fill.fill_index == fill.signal_index + 1 for fill in result.fills))
            self.assertTrue(all(fill.shares > 0 and fill.fee_paid >= 0 for fill in result.fills))
            self.assertGreaterEqual(result.max_drawdown, 0)
            self.assertLessEqual(result.max_drawdown, 1)

    def test_invalid_market_inputs_fail_closed(self):
        invalid = (
            lambda: simple_returns([100, 0]),
            lambda: simple_returns([1e-300, 1e300]),
            lambda: log_returns([1, float("nan")]),
            lambda: exponential_moving_average([1, 2], 0),
            lambda: simple_moving_average([1, 2], -2),
            lambda: wilder_rsi([1, 2], 2),
            lambda: cumulative_vwap([100, 110], [0]),
            lambda: cumulative_vwap([100, 110], [2, -1]),
            lambda: order_book_imbalance([(100, 2)], [(99, 1)]),
            lambda: order_book_imbalance([(100, 0)], [(101, 0)]),
            lambda: order_book_imbalance(((100, 1) for _ in range(10_001)), [(101, 1)]),
            lambda: black_scholes_european(100, 0, 1, 0.2, 0.05),
            lambda: black_scholes_european(100, 100, 1, 0.2, 0.05, option_type="other"),
            lambda: black_scholes_implied_volatility(200, 100, 100, 1, 0.05),
            lambda: maximum_drawdown([10, -1]),
            lambda: annualized_volatility([0.01]),
            lambda: historical_var_expected_shortfall([0.1, -0.1], confidence=1),
            lambda: gbm_terminal_prices(1, 0, -1, 1),
            lambda: simulate_long_only([100, 110], [1], initial_capital=59),
            lambda: simulate_long_only([100, 110], [1, 0.5], initial_capital=59),
            lambda: simulate_long_only([100, 110], [1, 1], initial_capital=-1),
            lambda: simulate_long_only([100, 110], [1, 1], slippage_bps=10000),
        )
        for call in invalid:
            with self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
