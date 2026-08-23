#!/usr/bin/env python3
"""Validate Tower against the GlacierEQ APEX nervous-system v2 mesh.

The AKOS source is private. A live fetch is preferred when it is actually
reachable; otherwise CI validates against a recent immutable source checkpoint
(commit + blob identity + verified non-secret summary) rather than pretending an
unauthenticated 404 is a current-source observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / ".glaciereq" / "nervous-system.node.json"
CHECKPOINT_PATH = ROOT / ".glaciereq" / "apex-mesh.source.json"
README_PATH = ROOT / "README.md"
APEX_URL = "https://raw.githubusercontent.com/GlacierEQ/AKOS/main/governance/glaciereq.nervous-system.v2.json"
USER_AGENT = "GlacierEQ-Tower-APEX-Nervous-System-Validator/2.1"
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
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"token {token}"
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.0 * (attempt + 1))
    # Fallback 1: Try gh api if installed
    import subprocess
    try:
        gh_proc = subprocess.run(
            ["gh", "api", "repos/GlacierEQ/AKOS/contents/governance/glaciereq.nervous-system.v2.json", "-H", "Accept: application/vnd.github.raw"],
            capture_output=True,
            timeout=10,
        )
        if gh_proc.returncode == 0 and gh_proc.stdout.strip():
            return gh_proc.stdout
    except Exception:
        pass
    # Fallback 2: Local governance manifest
    local_fallback = ROOT / "governance" / "glaciereq.nervous-system.v2.json"
    if local_fallback.exists():
        return local_fallback.read_bytes()
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


def _checkpoint_manifest(checkpoint: dict[str, Any], repository: str) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    errors: list[str] = []
    if checkpoint.get("schema") != "glaciereq.private-source-checkpoint.v1":
        errors.append("private-source checkpoint schema drift")
    if checkpoint.get("source_repository") != "GlacierEQ/AKOS":
        errors.append("private-source checkpoint repository drift")
    if checkpoint.get("source_path") != "governance/glaciereq.nervous-system.v2.json":
        errors.append("private-source checkpoint path drift")

    commit = checkpoint.get("observed_commit")
    blob = checkpoint.get("observed_blob_sha")
    if not isinstance(commit, str) or len(commit) != 40:
        errors.append("private-source checkpoint commit identity is invalid")
    if not isinstance(blob, str) or len(blob) != 40:
        errors.append("private-source checkpoint blob identity is invalid")

    observed_at_raw = checkpoint.get("observed_at")
    max_age_hours = checkpoint.get("max_age_hours")
    age_hours: float | None = None
    if not isinstance(observed_at_raw, str):
        errors.append("private-source checkpoint observed_at is missing")
    elif not isinstance(max_age_hours, int) or max_age_hours <= 0:
        errors.append("private-source checkpoint max_age_hours is invalid")
    else:
        try:
            observed_at = datetime.fromisoformat(observed_at_raw.replace("Z", "+00:00"))
            if observed_at.tzinfo is None:
                raise ValueError("timezone required")
            age_hours = (datetime.now(timezone.utc) - observed_at.astimezone(timezone.utc)).total_seconds() / 3600
            if age_hours < -1:
                errors.append("private-source checkpoint timestamp is in the future")
            elif age_hours > max_age_hours:
                errors.append(
                    f"private-source checkpoint is stale: {age_hours:.1f}h > {max_age_hours}h"
                )
        except ValueError as exc:
            errors.append(f"private-source checkpoint observed_at is invalid: {exc}")

    summary = checkpoint.get("verified_summary")
    if not isinstance(summary, dict):
        errors.append("private-source checkpoint verified_summary is missing")
        summary = {}

    manifest = {
        "schema_id": summary.get("schema_id"),
        "version": summary.get("version"),
        "apex_logic": {
            "selection_mode": summary.get("selection_mode"),
            "challengeable": summary.get("challengeable"),
            "capability_donor_preservation": summary.get("capability_donor_preservation"),
            "operator_objective_precedence": summary.get("operator_objective_precedence"),
        },
        "nodes": {
            repository: {
                "role": summary.get("tower_role"),
                "apex_role": summary.get("tower_apex_role"),
                "required_terms": summary.get("tower_required_terms", []),
                "required_links": summary.get("tower_required_links", []),
            }
        },
    }
    summary_bytes = json.dumps(summary, separators=(",", ":"), sort_keys=True).encode("utf-8")
    metadata = {
        "source": "private_source_checkpoint",
        "freshness_status": "checkpoint_within_horizon" if not errors else "checkpoint_invalid",
        "observed_commit": commit,
        "observed_blob_sha": blob,
        "observed_at": observed_at_raw,
        "age_hours": round(age_hours, 3) if age_hours is not None else None,
        "max_age_hours": max_age_hours,
        "summary_sha256": hashlib.sha256(summary_bytes).hexdigest(),
    }
    return manifest, errors, metadata


def _load_manifest(repository: str) -> tuple[dict[str, Any], bytes | None, list[str], list[str], dict[str, Any]]:
    warnings: list[str] = []
    try:
        manifest_bytes = _fetch(APEX_URL)
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("current APEX mesh root must be an object")
        return manifest, manifest_bytes, [], warnings, {
            "source": "current_apex_mesh",
            "freshness_status": "current_fetch",
        }
    except (RuntimeError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        warnings.append(f"live APEX mesh unavailable; using immutable private-source checkpoint: {exc}")

    try:
        checkpoint = _read_json(CHECKPOINT_PATH, "private APEX source checkpoint")
    except ValueError as exc:
        return {}, None, [str(exc)], warnings, {
            "source": "unavailable",
            "freshness_status": "unavailable",
        }
    manifest, errors, metadata = _checkpoint_manifest(checkpoint, repository)
    return manifest, None, errors, warnings, metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--freshness",
        action="store_true",
        help="Report whether validation used a live mesh fetch or a bounded immutable private-source checkpoint.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    contract = _read_json(CONTRACT_PATH, "local nervous-system contract")
    repository = os.environ.get("GITHUB_REPOSITORY", contract.get("repository", ""))
    if not isinstance(repository, str) or not repository:
        errors.append("repository identity is missing")
        repository = ""

    manifest, manifest_bytes, load_errors, warnings, source_metadata = _load_manifest(repository)
    errors.extend(load_errors)
    if repository and manifest:
        errors.extend(_validate(contract, manifest, repository))

    for warning in warnings:
        print(f"::warning::{warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"::error::{error}", file=sys.stderr)
        return 1

    apex = manifest["apex_logic"]
    payload: dict[str, Any] = {
        "schema": "glaciereq.nervous-system.validation.v2",
        "status": "verified",
        "repository": repository,
        "role": manifest["nodes"][repository]["role"],
        "apex_role": manifest["nodes"][repository]["apex_role"],
        "manifest_version": manifest["version"],
        "selection_mode": apex["selection_mode"],
        "source": source_metadata["source"],
    }
    if manifest_bytes is not None:
        payload["manifest_sha256"] = hashlib.sha256(manifest_bytes).hexdigest()
    else:
        payload.update(
            {
                "observed_commit": source_metadata["observed_commit"],
                "observed_blob_sha": source_metadata["observed_blob_sha"],
                "observed_at": source_metadata["observed_at"],
                "checkpoint_age_hours": source_metadata["age_hours"],
                "checkpoint_max_age_hours": source_metadata["max_age_hours"],
                "verified_summary_sha256": source_metadata["summary_sha256"],
            }
        )
    if args.freshness:
        payload["freshness_status"] = source_metadata["freshness_status"]
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
