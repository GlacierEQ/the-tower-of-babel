"""Read-only market mathematics and explicit, delayed-fill research simulation.

No broker, credentials, network access, order submission or investment recommendation
exists in this module. All inputs are caller-supplied historical/synthetic data.
"""

from __future__ import annotations

import math
import random
import sys
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
from itertools import islice
from typing import Iterable

from .numerics import bisect_root, finite_values, linear_quantile, online_moments


def _prices(values: Iterable[float], *, minimum: int = 1) -> tuple[float, ...]:
    prices = finite_values(values, minimum=minimum)
    if any(price <= 0 for price in prices):
        raise ValueError("prices must be strictly positive")
    return prices


def simple_returns(prices: Iterable[float]) -> tuple[float, ...]:
    """One-period arithmetic returns; the first price has no return."""
    values = _prices(prices, minimum=2)
    result = tuple(values[index] / values[index - 1] - 1 for index in range(1, len(values)))
    if not all(math.isfinite(value) for value in result):
        raise ValueError("return calculation overflow")
    return result


def log_returns(prices: Iterable[float]) -> tuple[float, ...]:
    """One-period continuously compounded returns."""
    values = _prices(prices, minimum=2)
    return tuple(math.log(values[index]) - math.log(values[index - 1]) for index in range(1, len(values)))


def simple_moving_average(prices: Iterable[float], window: int) -> tuple[float | None, ...]:
    """Trailing SMA with None until an entire window is observed."""
    values = _prices(prices)
    if isinstance(window, bool) or not isinstance(window, int) or window < 1:
        raise ValueError("window must be a positive integer")
    # A finite mean can exist even if a float summation overflows. Use exact
    # decimal sliding sums in that exceptional regime, preserving subnormals
    # that would disappear if every observation were divided by the window.
    if max(values) > sys.float_info.max / min(window, len(values)):
        output: list[float | None] = []
        with localcontext() as context:
            context.prec = 800  # spans the entire IEEE-754 double exponent range
            running = Decimal(0)
            for index, value in enumerate(values):
                if index >= window:
                    running -= Decimal.from_float(values[index - window])
                running += Decimal.from_float(value)
                output.append(float(running / window) if index + 1 >= window else None)
        return tuple(output)
    # Neumaier compensation retains small values while a much larger observation
    # enters and later leaves the rolling window; O(n) instead of resumming it.
    total = correction = 0.0

    def accumulate(value: float) -> None:
        nonlocal total, correction
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated

    output: list[float | None] = []
    for index, value in enumerate(values):
        if index >= window:
            accumulate(-values[index - window])
        accumulate(value)
        adjusted = total + correction
        if not math.isfinite(total) or not math.isfinite(correction) or not math.isfinite(adjusted):
            raise ValueError("SMA accumulation overflow")
        output.append(adjusted / window if index + 1 >= window else None)
    return tuple(output)


def exponential_moving_average(prices: Iterable[float], span: int) -> tuple[float, ...]:
    """Recursive EMA: alpha=2/(span+1), initial EMA=first observation."""
    values = _prices(prices)
    if isinstance(span, bool) or not isinstance(span, int) or span < 1:
        raise ValueError("span must be a positive integer")
    alpha = 2 / (span + 1)
    output = [values[0]]
    for value in values[1:]:
        output.append(alpha * value + (1 - alpha) * output[-1])
        if not math.isfinite(output[-1]):
            raise ValueError("EMA accumulation overflow")
    return tuple(output)


def wilder_rsi(prices: Iterable[float], period: int = 14) -> tuple[float | None, ...]:
    """Wilder's RSI, with explicit warmup and defined flat-market behaviour."""
    values = _prices(prices)
    if isinstance(period, bool) or not isinstance(period, int) or period < 1:
        raise ValueError("period must be a positive integer")
    if len(values) <= period:
        raise ValueError("RSI requires at least period + 1 prices")
    deltas = [new - old for old, new in zip(values, values[1:])]
    gain = math.fsum(max(delta, 0.0) / period for delta in deltas[:period])
    loss = math.fsum(max(-delta, 0.0) / period for delta in deltas[:period])

    def index_value(average_gain: float, average_loss: float) -> float:
        if not (math.isfinite(average_gain) and math.isfinite(average_loss)):
            raise ValueError("RSI accumulation overflow")
        if average_gain == 0 and average_loss == 0:
            return 50.0  # no directional movement
        if average_loss == 0:
            return 100.0
        if average_gain == 0:
            return 0.0
        return 100 - 100 / (1 + average_gain / average_loss)

    output: list[float | None] = [None] * period + [index_value(gain, loss)]
    for delta in deltas[period:]:
        gain += (max(delta, 0.0) - gain) / period
        loss += (max(-delta, 0.0) - loss) / period
        output.append(index_value(gain, loss))
    return tuple(output)


def cumulative_vwap(
    prices: Iterable[float], volumes: Iterable[float]
) -> tuple[float | None, ...]:
    """Cumulative volume-weighted average of caller-supplied transaction bars."""
    px = _prices(prices)
    volume = finite_values(volumes)
    if len(px) != len(volume) or any(value < 0 for value in volume):
        raise ValueError("prices/volumes must align and volumes cannot be negative")
    scale = 0.0
    total_weight = mean = 0.0
    result: list[float | None] = []
    for price, size in zip(px, volume):
        if size > scale:
            total_weight *= scale / size
            scale = size
        weight = size / scale if scale > 0 else 0.0
        total_weight += weight
        if weight:
            mean += (price - mean) * (weight / total_weight)
        if not math.isfinite(mean) or not math.isfinite(total_weight):
            raise ValueError("VWAP accumulation overflow")
        result.append(mean if total_weight > 0 else None)
    return tuple(result)


def order_book_imbalance(
    bids: Iterable[tuple[float, float]], asks: Iterable[tuple[float, float]]
) -> float:
    """Size imbalance in [-1,1] for a valid two-sided order-book snapshot."""
    try:
        left = tuple((float(price), float(size)) for price, size in islice(bids, 10_001))
        right = tuple((float(price), float(size)) for price, size in islice(asks, 10_001))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("order book levels must be (price, size) pairs") from exc
    if not left or not right:
        raise ValueError("order book requires bids and asks")
    if len(left) > 10_000 or len(right) > 10_000:
        raise ValueError("order-book depth exceeds 10000 levels per side")
    for price, size in (*left, *right):
        if not (math.isfinite(price) and math.isfinite(size)) or price <= 0 or size < 0:
            raise ValueError("order book prices must be positive and sizes nonnegative")
    if max(price for price, _ in left) > min(price for price, _ in right):
        raise ValueError("crossed order book cannot be measured as a valid snapshot")
    largest = max(size for _, size in (*left, *right))
    if largest <= 0:
        raise ValueError("order book depth must be finite and nonzero")
    buy_size = math.fsum(size / largest for _, size in left)
    sell_size = math.fsum(size / largest for _, size in right)
    return (buy_size - sell_size) / (buy_size + sell_size)


def black_scholes_european(
    spot: float, strike: float, years: float, annual_volatility: float,
    risk_free_rate: float, *, option_type: str = "call"
) -> float:
    """No-dividend European call/put theoretical value under Black-Scholes."""
    args = (spot, strike, years, annual_volatility, risk_free_rate)
    if not all(isinstance(x, (int, float)) and math.isfinite(x) for x in args):
        raise ValueError("option inputs must be finite numbers")
    if spot <= 0 or strike <= 0 or years < 0 or annual_volatility < 0:
        raise ValueError("spot/strike > 0, time/volatility >= 0 required")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be call or put")
    if years == 0:
        return max(0.0, spot - strike) if option_type == "call" else max(0.0, strike - spot)
    try:
        discounted_strike = strike * math.exp(-risk_free_rate * years)
        if not math.isfinite(discounted_strike):
            raise ValueError("discounted strike overflow")
        if annual_volatility == 0:
            intrinsic = spot - discounted_strike
            return max(0.0, intrinsic if option_type == "call" else -intrinsic)
        total_vol = annual_volatility * math.sqrt(years)
        d1 = ((math.log(spot) - math.log(strike)) +
              (risk_free_rate + annual_volatility**2 / 2) * years) / total_vol
        d2 = d1 - total_vol
        phi = lambda x: math.erfc(-x / math.sqrt(2)) / 2
        if option_type == "call":
            premium = spot * phi(d1) - discounted_strike * phi(d2)
        else:
            premium = discounted_strike * phi(-d2) - spot * phi(-d1)
    except (OverflowError, ZeroDivisionError) as exc:
        raise ValueError("option calculation overflow") from exc
    if not math.isfinite(premium):
        raise ValueError("option premium is nonfinite")
    return max(0.0, premium)


def black_scholes_implied_volatility(
    observed_premium: float, spot: float, strike: float, years: float,
    risk_free_rate: float, *, option_type: str = "call"
) -> float:
    """Invert the no-dividend European price with bounded, bracketed bisection."""
    if not isinstance(observed_premium, (int, float)) or not math.isfinite(observed_premium) or observed_premium < 0 or years <= 0:
        raise ValueError("observed premium >= 0 and years > 0 required")

    def price(volatility: float) -> float:
        return black_scholes_european(
            spot, strike, years, volatility, risk_free_rate, option_type=option_type
        )

    floor = price(0.0)
    upper = price(5.0)  # 500% annualized model volatility is an explicit solver cap
    if observed_premium < floor - 1e-10 or observed_premium > upper + 1e-10:
        raise ValueError("premium is outside model bounds or volatility solver cap")
    if abs(observed_premium - floor) < 1e-10:
        return 0.0
    if abs(observed_premium - upper) < 1e-10:
        return 5.0
    return bisect_root(lambda vol: price(vol) - observed_premium, 0.0, 5.0).root


def maximum_drawdown(equity: Iterable[float]) -> float:
    """Largest peak-to-trough loss fraction, with the initial peak included."""
    values = _prices(equity)
    peak = values[0]
    maximum = 0.0
    for value in values:
        peak = max(peak, value)
        maximum = max(maximum, 1 - value / peak)
    return maximum


def annualized_volatility(returns: Iterable[float], *, periods_per_year: int = 252) -> float:
    """Sample volatility of periodic returns, annualized by square-root-of-time."""
    if (isinstance(periods_per_year, bool) or not isinstance(periods_per_year, int)
            or periods_per_year < 1):
        raise ValueError("periods_per_year must be a positive integer")
    variance = online_moments(returns).variance
    try:
        result = math.sqrt(variance) * math.sqrt(periods_per_year)
    except OverflowError as exc:
        raise ValueError("periods_per_year is outside numeric range") from exc
    if not math.isfinite(result):
        raise ValueError("annualized volatility overflow")
    return result


def historical_var_expected_shortfall(
    returns: Iterable[float], *, confidence: float = 0.95
) -> tuple[float, float]:
    """Historical positive-loss VaR and tail-average ES, in return fractions.

    Uses type-7 linear quantile for VaR. ES averages observations at or beyond
    that loss threshold (a documented discrete-tail convention, not a claim of
    regulatory FRTB ES equivalence). Both values are floored at zero.
    """
    values = finite_values(returns, minimum=2)
    if not math.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence must be strictly between zero and one")
    losses = tuple(-value for value in values)
    threshold = linear_quantile(losses, confidence)
    tail = [value for value in losses if value >= threshold]
    return max(0.0, threshold), max(0.0, math.fsum(value / len(tail) for value in tail))


def gbm_terminal_prices(
    initial_price: float,
    annual_drift: float,
    annual_volatility: float,
    years: float,
    *,
    paths: int = 1000,
    seed: int = 0,
) -> tuple[float, ...]:
    """Seeded geometric-Brownian-motion scenarios; synthetic, not forecasts."""
    parameters = (initial_price, annual_drift, annual_volatility, years)
    if not all(math.isfinite(value) for value in parameters):
        raise ValueError("GBM parameters must be finite")
    if initial_price <= 0 or annual_volatility < 0 or years < 0:
        raise ValueError("GBM price > 0, volatility >= 0, years >= 0 required")
    if isinstance(paths, bool) or not isinstance(paths, int) or not 1 <= paths <= 100_000:
        raise ValueError("paths must be an integer from 1 to 100000")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    generator = random.Random(seed)
    try:
        scale = annual_volatility * math.sqrt(years)
        mean_log = annual_drift * years - scale**2 / 2
    except OverflowError as exc:
        raise ValueError("GBM overflow; constrain scenario parameters") from exc
    if not math.isfinite(scale) or not math.isfinite(mean_log):
        raise ValueError("GBM overflow; constrain scenario parameters")
    try:
        result = tuple(initial_price * math.exp(mean_log + scale * generator.gauss(0, 1))
                       for _ in range(paths))
    except OverflowError as exc:
        raise ValueError("GBM overflow; constrain scenario parameters") from exc
    if not all(math.isfinite(value) and value > 0 for value in result):
        raise ValueError("GBM generated nonfinite terminal prices")
    return result


@dataclass(frozen=True)
class SimulatedFill:
    signal_index: int
    fill_index: int
    side: str
    shares: float
    reference_price: float
    fill_price: float
    fee_paid: float


@dataclass(frozen=True)
class BacktestResult:
    schema: str
    initial_capital: float
    final_equity: float
    total_return: float
    max_drawdown: float
    equity_curve: tuple[float, ...]
    fills: tuple[SimulatedFill, ...]

    def as_dict(self) -> dict:
        return asdict(self)


def simulate_long_only(
    prices: Iterable[float],
    signals: Iterable[int],
    *,
    initial_capital: float = 59.0,
    fee_bps: float = 0.0,
    slippage_bps: float = 0.0,
) -> BacktestResult:
    """Zero-leverage, fractional-unit research simulation with one-bar signal lag.

    Signal[i] is target exposure observed at the close of bar i. An order fills
    at close i+1, *not* at bar i. This conservative next-close approximation
    avoids same-bar look-ahead but does not model an exchange order book or
    market impact. Signals must be 0 (cash) or 1 (fully long).
    """
    closes = _prices(prices, minimum=2)
    # At most one extra element is necessary to detect both mismatches and an
    # infinite/oversized signal generator without unbounded allocation.
    targets = tuple(islice(signals, len(closes) + 1))
    if len(targets) != len(closes) or any(
        type(value) is not int or value not in (0, 1) for value in targets
    ):
        raise ValueError("signals must be exactly one integer 0/1 per price")
    try:
        capital = float(initial_capital)
        friction = (float(fee_bps), float(slippage_bps))
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("capital and friction must be finite numeric values") from exc
    if (isinstance(initial_capital, bool) or not math.isfinite(capital)
            or capital <= 0):
        raise ValueError("initial_capital must be finite and positive")
    if (isinstance(fee_bps, bool) or isinstance(slippage_bps, bool)
            or not all(math.isfinite(value) and 0 <= value < 10_000 for value in friction)):
        raise ValueError("fee_bps and slippage_bps must lie in [0, 10000)")
    fee = friction[0] / 10_000
    slip = friction[1] / 10_000
    cash, shares = capital, 0.0
    equity: list[float] = []
    fills: list[SimulatedFill] = []
    for index, close in enumerate(closes):
        if index > 0:
            wanted = targets[index - 1]
            if wanted == 1 and shares == 0:
                fill_price = close * (1 + slip)
                shares = cash / (fill_price * (1 + fee))
                transaction_fee = shares * fill_price * fee
                cash = 0.0
                fills.append(SimulatedFill(index - 1, index, "BUY", shares, close, fill_price, transaction_fee))
            elif wanted == 0 and shares > 0:
                fill_price = close * (1 - slip)
                gross = shares * fill_price
                transaction_fee = gross * fee
                cash = gross - transaction_fee
                fills.append(SimulatedFill(index - 1, index, "SELL", shares, close, fill_price, transaction_fee))
                shares = 0.0
        marked_equity = cash + shares * close
        if not math.isfinite(marked_equity) or marked_equity <= 0:
            raise ValueError("simulation equity is nonfinite or nonpositive")
        equity.append(marked_equity)
    total_return = equity[-1] / capital - 1
    if not math.isfinite(total_return):
        raise ValueError("simulation total return overflow")
    return BacktestResult(
        schema="glaciereq.tower.market-backtest.v1",
        initial_capital=capital,
        final_equity=equity[-1],
        total_return=total_return,
        max_drawdown=maximum_drawdown(equity),
        equity_curve=tuple(equity),
        fills=tuple(fills),
    )
