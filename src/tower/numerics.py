"""Deterministic, dependency-free numerical reference algorithms.

These implementations favour explicit domains and reproducible correctness over
speed.  They are reference baselines for a future Julia/Rust/Fortran comparison,
not claims of superiority over specialised numerical libraries.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from itertools import islice, zip_longest

MAX_SERIES_LENGTH = 1_000_000


def finite_values(values: Iterable[float], *, minimum: int = 1) -> tuple[float, ...]:
    """Materialise at most one million finite numbers, rejecting bad inputs."""
    if isinstance(values, (str, bytes)):
        raise ValueError("expected numeric values, not text")
    try:
        result = tuple(
            float(value) if not isinstance(value, (bool, str, bytes)) else float("nan")
            for value in islice(values, MAX_SERIES_LENGTH + 1)
        )
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("values must be finite numbers") from exc
    if len(result) < minimum:
        raise ValueError(f"at least {minimum} observations required")
    if len(result) > MAX_SERIES_LENGTH:
        raise ValueError("series exceeds one-million-observation safety bound")
    if not all(math.isfinite(value) for value in result):
        raise ValueError("nonfinite observations are not accepted")
    return result


@dataclass(frozen=True)
class Moments:
    count: int
    mean: float
    variance: float


def online_moments(values: Iterable[float], *, ddof: int = 1) -> Moments:
    """One-pass Welford mean and variance; ddof is explicitly 0 or 1."""
    if isinstance(ddof, bool) or ddof not in (0, 1):
        raise ValueError("ddof must be 0 or 1")
    count = 0
    mean = 0.0
    m2 = 0.0
    if isinstance(values, (str, bytes)):
        raise ValueError("expected numeric values, not text")
    for raw_value in values:
        count += 1
        if count > MAX_SERIES_LENGTH:
            raise ValueError("series exceeds one-million-observation safety bound")
        try:
            value = float(raw_value) if not isinstance(raw_value, (bool, str, bytes)) else float("nan")
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("values must be finite numbers") from exc
        if not math.isfinite(value):
            raise ValueError("nonfinite observations are not accepted")
        delta = value - mean
        mean += delta / count
        m2 += delta * (value - mean)
    if count <= ddof:
        raise ValueError("insufficient observations for the requested ddof")
    variance = max(0.0, m2 / (count - ddof))
    if not math.isfinite(mean) or not math.isfinite(variance):
        raise ValueError("numeric overflow while computing moments")
    return Moments(count=count, mean=mean, variance=variance)


def online_covariance(
    left: Iterable[float], right: Iterable[float], *, ddof: int = 1
) -> float:
    """One-pass paired sample/population covariance with strict equal lengths."""
    if isinstance(ddof, bool) or ddof not in (0, 1):
        raise ValueError("ddof must be 0 or 1")
    if isinstance(left, (str, bytes)) or isinstance(right, (str, bytes)):
        raise ValueError("expected paired numeric values, not text")
    mean_x = mean_y = cross = 0.0
    missing = object()
    count = 0
    for index, (raw_x, raw_y) in enumerate(zip_longest(left, right, fillvalue=missing), start=1):
        if raw_x is missing or raw_y is missing:
            raise ValueError("paired series must have equal lengths")
        if index > MAX_SERIES_LENGTH:
            raise ValueError("series exceeds one-million-observation safety bound")
        try:
            x = float(raw_x) if not isinstance(raw_x, (bool, str, bytes)) else float("nan")
            y = float(raw_y) if not isinstance(raw_y, (bool, str, bytes)) else float("nan")
        except (TypeError, ValueError, OverflowError) as exc:
            raise ValueError("paired values must be finite numbers") from exc
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("nonfinite paired values are not accepted")
        count = index
        delta_x = x - mean_x
        mean_x += delta_x / index
        delta_y = y - mean_y
        mean_y += delta_y / index
        cross += delta_x * (y - mean_y)
    if count <= ddof:
        raise ValueError("insufficient paired observations for ddof")
    result = cross / (count - ddof)
    if not math.isfinite(result):
        raise ValueError("numeric overflow while computing covariance")
    return result


def linear_quantile(values: Iterable[float], probability: float) -> float:
    """Type-7 empirical quantile, matching NumPy's default linear convention."""
    numbers = sorted(finite_values(values))
    if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("probability must lie in [0, 1]")
    index = (len(numbers) - 1) * probability
    lower = int(index)
    upper = min(lower + 1, len(numbers) - 1)
    fraction = index - lower
    if numbers[lower] == numbers[upper]:
        return numbers[lower]
    result = numbers[lower] * (1.0 - fraction) + numbers[upper] * fraction
    if not math.isfinite(result):
        raise ValueError("numeric overflow while interpolating quantile")
    return min(numbers[upper], max(numbers[lower], result))


@dataclass(frozen=True)
class RootResult:
    root: float
    residual: float
    iterations: int


def bisect_root(
    function: Callable[[float], float],
    lower: float,
    upper: float,
    *,
    absolute_tolerance: float = 1e-10,
    max_iterations: int = 200,
) -> RootResult:
    """Bracketed bisection with no silent convergence on an invalid bracket."""
    if not all(math.isfinite(x) for x in (lower, upper, absolute_tolerance)):
        raise ValueError("bounds and tolerance must be finite")
    if not lower < upper or absolute_tolerance <= 0:
        raise ValueError("require lower < upper and positive tolerance")
    if isinstance(max_iterations, bool) or not isinstance(max_iterations, int) or max_iterations < 1:
        raise ValueError("max_iterations must be a positive integer")

    def checked(value: float) -> float:
        result = float(function(value))
        if not math.isfinite(result):
            raise ValueError("function returned a nonfinite value")
        return result

    left, right = float(lower), float(upper)
    f_left, f_right = checked(left), checked(right)
    if f_left == 0:
        return RootResult(left, 0.0, 0)
    if f_right == 0:
        return RootResult(right, 0.0, 0)
    if (f_left > 0) == (f_right > 0):
        raise ValueError("root is not bracketed by opposite signs")
    for iteration in range(1, max_iterations + 1):
        middle = left / 2.0 + right / 2.0
        if middle in (left, right):
            return RootResult(middle, checked(middle), iteration)
        f_middle = checked(middle)
        if f_middle == 0 or (right - left) / 2 <= absolute_tolerance:
            return RootResult(middle, f_middle, iteration)
        if (f_middle > 0) == (f_left > 0):
            left, f_left = middle, f_middle
        else:
            right = middle
    raise ValueError("bisection did not converge within max_iterations")
