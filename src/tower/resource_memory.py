"""Resource and external-memory reconstruction for Tower-governed work.

Tower does not own operator memory. It consumes an externally supplied memory
snapshot as continuity input, inventories the repository's current resource
state, collapses duplicate evidence by content hash, and emits a deterministic
preflight receipt before architecture placement or technology promotion.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

from .registry import REPO_ROOT

DEFAULT_OUTPUT = REPO_ROOT / "artifacts" / "resource-memory-preflight.json"

_EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str | None:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def _iter_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in _EXCLUDED_PARTS for part in rel.parts):
            continue
        yield path


def _resource_role(relative: str) -> str:
    if relative == "registry/tower.yml" or relative.startswith("registry/tower.d/"):
        return "REGISTRY_SOURCE"
    if relative.startswith("registry/"):
        return "REGISTRY_CONTRACT"
    if relative.startswith("src/tower/"):
        return "EXECUTABLE_CORE"
    if relative.startswith("tests/"):
        return "PROOF_TEST"
    if relative.startswith("frontier/"):
        return "FRONTIER_SOURCE"
    if relative.startswith("generated/"):
        return "GENERATED_PROJECTION"
    if relative.startswith("artifacts/"):
        return "EXECUTION_ARTIFACT"
    if relative.startswith(".integrity/"):
        return "INTEGRITY_CONTROL"
    if relative.startswith(".github/"):
        return "AUTOMATION_CONTROL"
    if relative.startswith("docs/") or relative.endswith(".md"):
        return "DOCUMENTATION"
    return "REPOSITORY_RESOURCE"


def inventory_resources(root: Path = REPO_ROOT) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Inventory resources and collapse same-byte copies into one lineage."""
    root = root.resolve()
    resources: list[dict[str, Any]] = []
    by_hash: dict[str, list[str]] = {}
    for path in _iter_files(root):
        rel = path.relative_to(root).as_posix()
        digest = _sha256(path)
        resources.append(
            {
                "resource_id": f"sha256:{digest}",
                "locator": rel,
                "resource_type": _resource_role(rel),
                "size_bytes": path.stat().st_size,
                "sha256": digest,
            }
        )
        by_hash.setdefault(digest, []).append(rel)

    duplicates = [
        {"sha256": digest, "locators": sorted(paths), "independent_sources": 1}
        for digest, paths in sorted(by_hash.items())
        if len(paths) > 1
    ]
    return resources, duplicates


def _read_memory_snapshot(path: Path | None) -> tuple[str, list[dict[str, Any]], list[str]]:
    if path is None:
        return "NOT_PROVIDED", [], ["external memory snapshot not supplied"]
    if not path.is_file():
        return "UNAVAILABLE", [], [f"external memory snapshot not found: {path}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "INVALID", [], [f"external memory snapshot unreadable: {exc}"]

    if isinstance(payload, dict):
        raw_findings = payload.get("findings", payload.get("memory_findings", []))
    elif isinstance(payload, list):
        raw_findings = payload
    else:
        return "INVALID", [], ["external memory snapshot must be an object or list"]

    if not isinstance(raw_findings, list):
        return "INVALID", [], ["external memory findings must be a list"]

    findings: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_findings):
        if isinstance(raw, str):
            findings.append(
                {
                    "finding": raw,
                    "status": "RECALLED_NEEDS_SOURCE",
                    "source_pointer": None,
                    "ordinal": index,
                }
            )
            continue
        if not isinstance(raw, dict):
            continue
        finding = raw.get("finding") or raw.get("text") or raw.get("claim")
        if not isinstance(finding, str) or not finding.strip():
            continue
        source_pointer = raw.get("source_pointer") or raw.get("source")
        if not isinstance(source_pointer, str) or not source_pointer.strip():
            source_pointer = None
        requested_status = raw.get("status")
        allowed = {
            "VERIFIED_WITH_SOURCE",
            "RECALLED_NEEDS_SOURCE",
            "DISPUTED",
            "INVALIDATED",
        }
        status = requested_status if requested_status in allowed else (
            "VERIFIED_WITH_SOURCE" if source_pointer else "RECALLED_NEEDS_SOURCE"
        )
        findings.append(
            {
                "finding": finding.strip(),
                "status": status,
                "source_pointer": source_pointer,
                "ordinal": index,
            }
        )

    gaps = [
        f"memory finding lacks source pointer: {row['finding']}"
        for row in findings
        if row["status"] == "RECALLED_NEEDS_SOURCE"
    ]
    return "ANALYZED", findings, gaps


def build_preflight(
    mission: str,
    *,
    root: Path = REPO_ROOT,
    memory_path: Path | None = None,
) -> dict[str, Any]:
    """Build a deterministic resource + memory reconstruction receipt."""
    mission = mission.strip()
    if not mission:
        raise ValueError("mission must be a non-empty string")

    root = root.resolve()
    resources, duplicates = inventory_resources(root)
    memory_status, memory_findings, memory_gaps = _read_memory_snapshot(memory_path)
    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    porcelain = _git(root, "status", "--porcelain=v1")
    changed = sorted(line[3:] for line in porcelain.splitlines() if len(line) >= 4) if porcelain else []

    resource_gaps: list[str] = []
    expected = [
        "registry/tower.yml",
        "ARCHITECTURE_LAW.md",
        "NERVOUS_SYSTEM.md",
        "src/tower/registry.py",
        "src/tower/proofs.py",
        "src/tower/integrity.py",
    ]
    locators = {row["locator"] for row in resources}
    for required in expected:
        if required not in locators:
            resource_gaps.append(f"required Tower resource missing: {required}")

    status = "COMPLETE" if not resource_gaps and memory_status == "ANALYZED" else "PARTIAL"
    return {
        "schema": "glaciereq.tower.resource-memory-preflight.v1",
        "mission": mission,
        "state": "RESOURCE_RECONSTRUCTED",
        "status": status,
        "tower_boundary": {
            "owns_operator_memory": False,
            "memory_role": "EXTERNAL_CONTINUITY_INPUT",
            "resource_role": "LOCAL_TECHNOLOGY_AND_PROOF_STATE",
        },
        "last_verified_checkpoint": {
            "commit_sha": head,
            "tree_sha": tree,
        },
        "resource_analysis": {
            "resource_count": len(resources),
            "resources": resources,
            "duplicate_content_groups": duplicates,
            "resource_gaps": resource_gaps,
        },
        "memory_analysis": {
            "status": memory_status,
            "source": str(memory_path) if memory_path else None,
            "findings": memory_findings,
            "gaps": memory_gaps,
            "evidence_rule": "memory requires a source pointer before promotion to proof",
        },
        "delta": {
            "working_tree_changed_paths": changed,
            "rule": "last verified state plus new verified delta",
        },
        "promotion_gate": {
            "may_use_memory_as_proof_without_source": False,
            "duplicates_count_as_independent_corroboration": False,
            "must_reuse_prior_verified_state": True,
            "must_resolve_or_preserve_material_contradictions": True,
        },
    }


def write_preflight(
    output: Path,
    mission: str,
    *,
    root: Path = REPO_ROOT,
    memory_path: Path | None = None,
) -> dict[str, Any]:
    payload = build_preflight(mission, root=root, memory_path=memory_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
