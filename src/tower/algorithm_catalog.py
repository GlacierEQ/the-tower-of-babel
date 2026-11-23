"""Governed discovery and validation for executable numerical/market functions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import market_algorithms, numerics
from .registry import REPO_ROOT, TowerRegistry

CATALOG_PATH = REPO_ROOT / "registry" / "algorithm_catalog.json"
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
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            errors.append(f"algorithm[{index}] missing or duplicate id")
        else:
            seen.add(identifier)
        module = _MODULES.get(row.get("module"))
        function = row.get("function")
        if module is None or not isinstance(function, str) or not callable(getattr(module, function, None)):
            errors.append(f"algorithm[{index}] has no approved executable implementation")
        proof = row.get("proof")
        if (
            not isinstance(proof, str)
            or not proof.startswith("tests/")
            or ".." in Path(proof).parts
            or not (REPO_ROOT / proof).is_file()
        ):
            errors.append(f"algorithm[{index}] has no contained executable proof path")
        if row.get("domain") not in {
            "mathematics", "market_research", "market_risk", "market_simulation",
            "market_microstructure", "derivatives_research",
        }:
            errors.append(f"algorithm[{index}] has an unknown domain")
    return errors


def list_algorithms() -> dict[str, Any]:
    catalog = load_algorithm_catalog()
    return {
        "schema": catalog["schema"],
        "owner_technology_id": catalog["owner_technology_id"],
        "external_effects": False,
        "benchmark_status": "NOT_BENCHMARKED_AGAINST_ALTERNATIVES",
        "count": len(catalog["algorithms"]),
        "algorithms": catalog["algorithms"],
    }
