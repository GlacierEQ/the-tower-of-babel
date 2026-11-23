# Mathematical and Market Algorithm Reference — Tower of Babel

## Executable result and architectural boundary

The Tower now includes **18 implemented mathematical / market research functions**,
not merely algorithm names. They are discoverable through the authored
[`registry/algorithm_catalog.json`](../registry/algorithm_catalog.json), which
`tower validate` checks against real function objects and test paths.

The *existing* Python floor owns the correctness-reference implementation. No
new programming language is claimed. Julia, Fortran, R, and C++ remain candidates
for specialized numerical performance, statistics, or native kernels; no speed
superiority is claimed without a measured same-input benchmark. This adds a
domain capability to the Tower, not a fictitious extra technology floor.

| Function | Method / invariant | Implemented boundary |
|---|---|---|
| `math.online_moments` | Welford recurrence, sample/population variance with explicit `ddof` | Stable streaming statistics |
| `math.online_covariance` | One-pass paired covariance, matching sample lengths | Multivariate data quality |
| `math.linear_quantile` | Sorted type-7 linear interpolation | Reproducible empirical distributions |
| `math.bisect_root` | Sign-bracketed interval bisection, bounded iterations | Robust scalar root finding |
| `market.simple_returns` | \(P_t/P_{t-1}-1\) | Arithmetic return transformation |
| `market.log_returns` | \(\log(P_t/P_{t-1})\) | Logarithmic return transformation |
| `market.simple_moving_average` | Trailing mean; missing until full warmup | Windowed technical statistics |
| `market.exponential_moving_average` | Recursive \(\alpha=2/(N+1)\), initial EMA = first price | Causal smoothing |
| `market.wilder_rsi` | Wilder gain/loss smoothing; explicit flat-market RSI = 50 | Bounded 0–100 momentum indicator |
| `market.cumulative_vwap` | Cumulative price × volume / cumulative volume | Volume-weighted price statistics |
| `market.order_book_imbalance` | Two-sided bid/ask depth normalized to [-1, 1] | Market microstructure snapshot |
| `market.black_scholes_european` | No-dividend European call/put closed-form theoretical premium | Option pricing reference |
| `market.black_scholes_implied_volatility` | Inverse Black-Scholes price via bracketed bisection | Option volatility inference |
| `market.maximum_drawdown` | \(\max_t(1-E_t/\max_{s\le t}E_s)\) | Path-dependent loss |
| `market.annualized_volatility` | Sample standard deviation × square root of periods | Historical fluctuation metric |
| `market.historical_var_expected_shortfall` | Type-7 historical VaR and tail-mean ES | Historical loss distribution |
| `market.gbm_terminal_prices` | Seeded lognormal geometric Brownian-motion scenarios | Synthetic stress-model generator |
| `market.simulate_long_only` | 0/1 close signals, fills **one bar later**, fractional units, explicit fee/slippage | Fully local long-only research simulator |

### Agent-facing usage

```bash
PYTHONPATH=src python3 -m tower validate
PYTHONPATH=src python3 -m tower algorithms list
PYTHONPATH=src python3 -m tower algorithms run examples/market_algorithm_request.json
PYTHONPATH=src python3 -m tower algorithms simulate examples/market_research_signals.json
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_tower_numerics.py'
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_tower_market_algorithms.py'
PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_tower_algorithm_catalog.py'
```

The **agent calculation interface** accepts a read-only JSON request with
schema `glaciereq.tower.algorithm-execution.v1`, a catalog `algorithm_id`, and
an `arguments` object matching that function's named parameters. The checked-in
request computes a three-bar moving average. The response contains the
algorithm ID, a JSON-serializable result, and `external_effects: false`.
Only registered functions can run; unsupported names and parameters fail.
The root-finding adapter accepts polynomial coefficients (highest degree first)
in lieu of accepting arbitrary executable functions. For example,
`{"coefficients": [1, 0, -2], "lower": 1, "upper": 2}` finds positive √2.
This interface performs numerical calculations, **not trade orders**.

The simulation input is a JSON object using
`glaciereq.tower.market-research-input.v1`: strictly positive closing prices,
equal-length integer 0/1 *target* positions, simulated starting capital, and
nonnegative fee/slippage in basis points. The checked-in demonstration uses
**$59 of entirely simulated capital**, not a financial account balance.

CLI output contains a typed `market-backtest.v1` envelope with simulated fills,
equity curve, total return and maximum drawdown. A signal at close `t` may only
fill at close `t+1`. Final-bar signals cannot secretly trade within the sample.
The model permits fractional units for algorithmic research, not as a claim
about any broker's support or permitted minimum order.

### Explicit limitations and adverse cases

- **No money movement, account access, broker adapter, network call or order
  submission.** This implementation cannot operate a Coinbase or Alpaca account.
- `simulate_long_only` assumes next-close fills and fixed basis-point friction;
  it cannot model market impact, bid/ask queueing, latency, halts, borrowing,
  taxes, partial fills, funding, corporate actions, or changing market hours.
- Research inputs are caller-provided; the code has no verified current market
  prices, survivorship-bias treatment, or independent trading alpha evidence.
- Volatility presumes equally spaced returns. Simple sample annualization is
  not a forecast. Historical VaR/ES is a discrete empirical method, not a
  calibrated tail model or a regulatory FRTB capital calculation.
- GBM produces seeded synthetic scenarios under *assumed* drift/volatility; it
  neither estimates those assumptions nor predicts an investment return.
- Black-Scholes assumes European exercise, no dividend yield, continuous
  risk-free compounding, and constant volatility. An implied-volatility root
  is constrained to 0–500% annualized; no American-option or market quote
  interpretation is claimed. Order-book imbalance only reflects supplied
  snapshots, not actual exchange liquidity or executable market depth.
- Validation rejects nonfinite or impossible inputs. Tests exercise known
  reference fixtures, monotonicity/failure cases, costs, look-ahead lag, and
  deterministic CLI readback. Passing these tests supports only these methods.
- Numeric series are bounded to one million observations, market-book snapshots
  to 10,000 levels per side, Monte Carlo to 100,000 paths, and bisection to
  a caller-bounded iteration count; excess work is rejected.

### Technology choice, provenance, and next comparison

Python was chosen first for deterministic inspectability, zero new runtime
dependencies, and immediate reuse through `tower.algorithms`. The existing
Tower technology registry already declares stronger HPC and statistical
candidates; replacing a baseline requires *the same validated input fixtures*
across implementations, native toolchain execution, precision/latency/resource
measurements, and preservation of the exact interface and failure behaviours.

Useful primary mathematical references:

- [Python numerical summation and floating point semantics](https://docs.python.org/3/library/math.html)
- [NumPy type-7 linear quantile convention](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html)
- [Pandas recursive exponentially weighted mean convention](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.ewm.html)
- [Options Industry Council — Black-Scholes limitations](https://www.optionseducation.org/advancedconcepts/black-scholes-formula)

The Tower owns this reusable algorithm **reference**, not Quant Lab's model,
training data, brokerage credentials, or claims of profitable investment.
