#!/usr/bin/env python3
"""Validate Tower against the current GlacierEQ APEX nervous-system v2 mesh."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / ".glaciereq" / "nervous-system.node.json"
README_PATH = ROOT / "README.md"
APEX_URL = "https://raw.githubusercontent.com/GlacierEQ/AKOS/main/governance/glaciereq.nervous-system.v2.json"
USER_AGENT = "GlacierEQ-Tower-APEX-Nervous-System-Validator/2.0"
EXPECTED_SEQUENCE = ["context", "discover", "compare", "cure", "innovate", "execute", "verify", "persist", "evolve"]


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} not found: {path}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} cannot be loaded: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be an object")
    return payload


def _fetch(url: str, attempts: int = 3, timeout: int = 20) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"unable to fetch {url}: {last_error}")


def _validate(contract: dict[str, Any], manifest: dict[str, Any], repository: str) -> list[str]:
    errors: list[str] = []
    node = manifest.get("nodes", {}).get(repository)
    apex = manifest.get("apex_logic", {})
    if not isinstance(node, dict):
        return [f"{repository} is not registered"]
    if manifest.get("schema_id") != "glaciereq.nervous-system.v2":
        errors.append("APEX nervous-system schema drift")
    if apex.get("selection_mode") != "CURRENT_BEST_REVISABLE":
        errors.append("selection mode drift")
    if apex.get("challengeable") is not True:
        errors.append("mesh selections must remain challengeable")
    if apex.get("capability_donor_preservation") is not True:
        errors.append("capability donor preservation drift")
    if apex.get("operator_objective_precedence") is not True:
        errors.append("operator objective precedence drift")

    expected = {
        "schema_id": "glaciereq.nervous-system-node.v2",
        "nervous_system_schema_id": manifest.get("schema_id"),
        "repository": repository,
        "role": node.get("role"),
        "apex_role": node.get("apex_role"),
        "apex_manifest": APEX_URL,
        "selection_mode": apex.get("selection_mode"),
        "challengeable": True,
        "capability_donor_preservation": True,
        "operating_sequence": EXPECTED_SEQUENCE,
    }
    for field, value in expected.items():
        if contract.get(field) != value:
            errors.append(f"{field} drift")

    readme = README_PATH.read_text(encoding="utf-8").lower()
    for term in node.get("required_terms", []):
        if not isinstance(term, str) or term.lower() not in readme:
            errors.append(f"README missing term: {term}")
    for link in node.get("required_links", []):
        if not isinstance(link, str) or link.lower() not in readme:
            errors.append(f"README missing link: {link}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--freshness",
        action="store_true",
        help="Emit the SHA-256 of the current APEX mesh observed during validation.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    contract = _read_json(CONTRACT_PATH, "local nervous-system contract")
    try:
        manifest_bytes = _fetch(APEX_URL)
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (RuntimeError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        errors.append(f"current APEX mesh cannot be loaded: {exc}")
        manifest_bytes = b""
        manifest = {}

    repository = os.environ.get("GITHUB_REPOSITORY", contract.get("repository", ""))
    if not isinstance(repository, str) or not repository:
        errors.append("repository identity is missing")
    elif isinstance(manifest, dict):
        errors.extend(_validate(contract, manifest, repository))

    for warning in warnings:
        print(f"::warning::{warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1

    observed_sha = hashlib.sha256(manifest_bytes).hexdigest()
    apex = manifest["apex_logic"]
    payload = {
        "schema": "glaciereq.nervous-system.validation.v2",
        "status": "verified",
        "repository": repository,
        "role": manifest["nodes"][repository]["role"],
        "apex_role": manifest["nodes"][repository]["apex_role"],
        "manifest_version": manifest["version"],
        "manifest_sha256": observed_sha,
        "selection_mode": apex["selection_mode"],
        "source": "current_apex_mesh",
    }
    if args.freshness:
        payload["freshness_status"] = "current_fetch"
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
