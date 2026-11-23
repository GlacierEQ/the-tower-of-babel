"""Governed discovery and validation for executable numerical/market functions."""

from __future__ import annotations

import json
import inspect
import math
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from . import market_algorithms, numerics
from .registry import REPO_ROOT, TowerRegistry, load_registry

REPOSITORY_CATALOG = REPO_ROOT / "registry" / "algorithm_catalog.json"
PACKAGED_CATALOG = Path(__file__).resolve().parent / "data" / "algorithm_catalog.json"
CATALOG_PATH = REPOSITORY_CATALOG if REPOSITORY_CATALOG.is_file() else PACKAGED_CATALOG
_MODULES = {
    "tower.numerics": numerics,
    "tower.market_algorithms": market_algorithms,
}


def load_algorithm_catalog(path: Path = CATALOG_PATH) -> dict[str, Any]:
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid algorithm catalog: {path}: {exc}") from exc
    if not isinstance(catalog, dict):
        raise ValueError("algorithm catalog root must be an object")
    return catalog


def validate_algorithm_catalog(catalog: dict[str, Any], registry: TowerRegistry) -> list[str]:
    errors: list[str] = []
    if REPOSITORY_CATALOG.is_file() and (
        not PACKAGED_CATALOG.is_file()
        or REPOSITORY_CATALOG.read_bytes() != PACKAGED_CATALOG.read_bytes()
    ):
        errors.append("packaged algorithm catalog differs from authored catalog")
    if catalog.get("schema") != "glaciereq.tower.algorithm-catalog.v1":
        errors.append("algorithm catalog has unsupported schema")
    owner = catalog.get("owner_technology_id")
    if not isinstance(owner, str) or registry.by_id(owner) is None:
        errors.append("algorithm catalog owner_technology_id is unknown")
    rows = catalog.get("algorithms")
    if not isinstance(rows, list) or not rows:
        return errors + ["algorithm catalog requires nonempty algorithms"]
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"algorithm[{index}] must be an object")
            continue
        identifier = row.get("id")
        if not isinstance(identifier, str) or not identifier or identifier.casefold() in seen:
            errors.append(f"algorithm[{index}] missing or duplicate id")
        else:
            seen.add(identifier.casefold())
        module_name = row.get("module")
        module = _MODULES.get(module_name) if isinstance(module_name, str) else None
        function = row.get("function")
        implementation = getattr(module, function, None) if module is not None and isinstance(function, str) else None
        if (not inspect.isfunction(implementation) or function.startswith("_")
                or implementation.__module__ != module.__name__):
            errors.append(f"algorithm[{index}] has no approved executable implementation")
        proof = row.get("proof")
        proof_path = REPO_ROOT / proof if isinstance(proof, str) else None
        if (
            not isinstance(proof, str)
            or not proof.startswith("tests/")
            or ".." in Path(proof).parts
            or (REPOSITORY_CATALOG.is_file() and (
                not proof_path.is_file()
                or not proof_path.resolve().is_relative_to(REPO_ROOT.resolve())
                or not isinstance(function, str)
                or function not in proof_path.read_text(encoding="utf-8")
            ))
        ):
            errors.append(f"algorithm[{index}] has no valid contained proof path")
        domain = row.get("domain")
        if not isinstance(domain, str) or domain not in {
            "mathematics", "market_research", "market_risk", "market_simulation",
            "market_microstructure", "derivatives_research",
        }:
            errors.append(f"algorithm[{index}] has an unknown domain")
    return errors


def _verified_catalog() -> dict[str, Any]:
    catalog = load_algorithm_catalog()
    errors = validate_algorithm_catalog(catalog, load_registry())
    if errors:
        raise ValueError("invalid algorithm catalog: " + "; ".join(errors))
    return catalog


def list_algorithms() -> dict[str, Any]:
    catalog = _verified_catalog()
    return {
        "schema": catalog["schema"],
        "owner_technology_id": catalog["owner_technology_id"],
        "external_effects": False,
        "benchmark_status": "NOT_BENCHMARKED_AGAINST_ALTERNATIVES",
        "count": len(catalog["algorithms"]),
        "algorithms": catalog["algorithms"],
    }


def execute_algorithm(identifier: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute only a registered, side-effect-free algorithm from JSON arguments.

    Bisection receives polynomial coefficients (highest degree first) instead
    of accepting executable code across the JSON boundary.
    """
    if not isinstance(arguments, dict):
        raise ValueError("algorithm arguments must be a JSON object")
    catalog = _verified_catalog()
    entry = next((row for row in catalog["algorithms"] if row["id"] == identifier), None)
    if entry is None:
        raise ValueError(f"unknown algorithm id: {identifier}")
    implementation = getattr(_MODULES[entry["module"]], entry["function"])
    params = dict(arguments)
    if identifier == "math.bisect_root":
        coefficients = params.pop("coefficients", None)
        if not isinstance(coefficients, list) or not 1 <= len(coefficients) <= 100:
            raise ValueError("bisection requires 1-100 polynomial coefficients")
        if any(isinstance(value, bool) or not isinstance(value, (int, float))
               or not math.isfinite(value) for value in coefficients):
            raise ValueError("polynomial coefficients must be finite numbers")

        def polynomial(point: float) -> float:
            total = 0.0
            for coefficient in coefficients:
                total = total * point + coefficient
            return total

        params["function"] = polynomial
    try:
        outcome = implementation(**params)
    except (TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError(f"invalid algorithm arguments: {exc}") from exc
    if is_dataclass(outcome) and not isinstance(outcome, type):
        outcome = asdict(outcome)
    return {
        "schema": "glaciereq.tower.algorithm-result.v1",
        "algorithm_id": identifier,
        "external_effects": False,
        "result": outcome,
    }
