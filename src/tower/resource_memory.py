"""Resource and external-memory reconstruction for Tower-governed work.

Tower does not own operator memory. It consumes an externally supplied memory
snapshot as continuity input, inventories the active Tower checkout, collapses
duplicate evidence by content hash, binds continuity to a valid release receipt
when one is available, and emits deterministic orientation state for architecture placement and
technology decisions. Orientation informs routing and certainty; it is never
an execution-permission gate.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable

from .registry import REPO_ROOT

DEFAULT_OUTPUT = Path("artifacts/resource-memory-preflight.json")
DEFAULT_RELEASE_RECEIPT = Path("artifacts/tower_receipt.json")

_EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


def resolve_repo_root(root: Path | None = None) -> Path:
    """Resolve the active Tower checkout, not the Python installation prefix."""
    if root is not None:
        return Path(root).resolve()

    cwd = Path.cwd().resolve()
    candidates = [cwd, *cwd.parents]
    packaged = REPO_ROOT.resolve()
    if packaged not in candidates:
        candidates.append(packaged)

    for candidate in candidates:
        markers = sum(
            path.exists()
            for path in (
                candidate / "ARCHITECTURE_LAW.md",
                candidate / "NERVOUS_SYSTEM.md",
                candidate / "pyproject.toml",
                candidate / ".git",
            )
        )
        if markers >= 2:
            return candidate
    return cwd


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable_sha256(value: Any) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def _iter_files(root: Path, excluded: set[Path] | None = None) -> Iterable[Path]:
    excluded = {path.resolve() for path in (excluded or set())}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if path.resolve() in excluded:
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


def inventory_resources(
    root: Path | None = None,
    *,
    exclude_paths: Iterable[Path] = (),
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Inventory resources and collapse same-byte copies into one lineage."""
    root = resolve_repo_root(root)
    excluded = {Path(path).resolve() for path in exclude_paths}
    resources: list[dict[str, Any]] = []
    by_hash: dict[str, list[str]] = {}
    for path in _iter_files(root, excluded):
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


def _memory_locator(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return f"external:{resolved.name}"


def _validate_source_pointer(pointer: str, root: Path) -> tuple[bool, str]:
    """Verify a source pointer against local files or Git history.

    External pointers remain continuity hints until an authenticated connector
    or a local checkpoint projects them into this checkout.
    """
    if pointer.startswith("commit:"):
        _, separator, remainder = pointer.partition(":")
        commit_sha, separator, relative = remainder.partition(":")
        if (
            not separator
            or len(commit_sha) != 40
            or any(char not in "0123456789abcdef" for char in commit_sha)
            or not relative
        ):
            return False, "commit source pointer must be commit:<40hex>:<path>"
        resolved = _git(root, "cat-file", "-e", f"{commit_sha}:{relative}")
        if resolved is None:
            return False, "commit source pointer is not available in this Git history"
        return True, "GIT_OBJECT_RESOLVED"

    if (
        pointer.startswith("http://")
        or pointer.startswith("https://")
        or pointer.startswith("external:")
        or pointer.startswith("GlacierEQ/")
    ):
        return False, "external source pointer requires an authenticated local checkpoint"

    candidate = (root / pointer).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return False, "local source pointer escapes repository root"
    if not candidate.is_file():
        return False, "local source pointer does not resolve to a file"
    return True, "LOCAL_FILE_RESOLVED"


def _read_memory_snapshot(
    path: Path | None,
    root: Path,
) -> tuple[str, list[dict[str, Any]], list[str], str | None]:
    if path is None:
        return "NOT_PROVIDED", [], ["external memory snapshot not supplied"], None
    if not path.is_file():
        return "UNAVAILABLE", [], [f"external memory snapshot not found: {path}"], None
    try:
        snapshot_sha256 = _sha256(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return "INVALID", [], [f"external memory snapshot unreadable: {exc}"], None

    if isinstance(payload, dict):
        raw_findings = payload.get("findings", payload.get("memory_findings", []))
    elif isinstance(payload, list):
        raw_findings = payload
    else:
        return "INVALID", [], ["external memory snapshot must be an object or list"], snapshot_sha256

    if not isinstance(raw_findings, list):
        return "INVALID", [], ["external memory findings must be a list"], snapshot_sha256
    if not raw_findings:
        return "NO_PRIOR_STATE_FOUND", [], ["external memory snapshot contains no findings"], snapshot_sha256

    findings: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_findings):
        if isinstance(raw, str) and raw.strip():
            findings.append(
                {
                    "finding": raw.strip(),
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
            "SUPERSEDED",
        }

        source_valid = False
        source_validation = "NO_SOURCE_POINTER"
        if source_pointer is not None:
            source_valid, source_validation = _validate_source_pointer(source_pointer, root)

        if requested_status in {"DISPUTED", "INVALIDATED", "SUPERSEDED"}:
            status = requested_status
        elif requested_status == "RECALLED_NEEDS_SOURCE":
            status = requested_status
        elif source_pointer is not None and source_valid:
            status = "VERIFIED_WITH_SOURCE"
        else:
            status = "RECALLED_NEEDS_SOURCE"

        findings.append(
            {
                "finding": finding.strip(),
                "status": status,
                "source_pointer": source_pointer,
                "source_pointer_valid": source_valid,
                "source_validation": source_validation,
                "ordinal": index,
            }
        )

    if not findings:
        return "INVALID", [], ["external memory snapshot contains no analyzable findings"], snapshot_sha256

    gaps = []
    for row in findings:
        if row["status"] != "RECALLED_NEEDS_SOURCE":
            continue
        if row.get("source_pointer") is None:
            gaps.append(f"memory finding lacks source pointer: {row['finding']}")
        else:
            gaps.append(
                "memory source pointer is not verified: "
                f"{row['source_pointer']} ({row.get('source_validation', 'UNKNOWN')})"
            )
    return "ANALYZED", findings, gaps, snapshot_sha256


def _load_verified_checkpoint(root: Path, receipt_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    """Load a proof-bound release receipt without inventing verification state."""
    if not receipt_path.is_file():
        return None, [f"verified release receipt not found: {receipt_path}"]
    try:
        payload = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"verified release receipt unreadable: {exc}"]
    if not isinstance(payload, dict):
        return None, ["verified release receipt root must be an object"]

    errors: list[str] = []
    if payload.get("schema_version") != "2.0.0":
        errors.append("verified release receipt schema_version must be 2.0.0")
    for flag in ("registry_valid", "integrity_valid", "build_report_valid"):
        if payload.get(flag) is not True:
            errors.append(f"verified release receipt requires {flag}=true")

    commit_sha = payload.get("integrity_commit_sha")
    tree_sha = payload.get("integrity_tree_sha")
    if not isinstance(commit_sha, str) or len(commit_sha) != 40:
        errors.append("verified release receipt commit SHA is invalid")
    if not isinstance(tree_sha, str) or len(tree_sha) != 40:
        errors.append("verified release receipt tree SHA is invalid")

    body = {
        key: value
        for key, value in payload.items()
        if key not in {"receipt_id", "body_sha256", "receipt_sha256"}
    }
    body_sha = _stable_sha256(body)
    if payload.get("body_sha256") != body_sha or payload.get("receipt_sha256") != body_sha:
        errors.append("verified release receipt body hash is invalid")

    if isinstance(commit_sha, str) and len(commit_sha) == 40:
        resolved_tree = _git(root, "rev-parse", f"{commit_sha}^{{tree}}")
        if resolved_tree is None:
            errors.append("verified release receipt commit is not available in this checkout")
        elif isinstance(tree_sha, str) and resolved_tree != tree_sha:
            errors.append("verified release receipt tree does not match commit")

    if errors:
        return None, errors
    return {
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "receipt_sha256": body_sha,
        "receipt_locator": receipt_path.relative_to(root).as_posix()
        if receipt_path.is_relative_to(root)
        else f"external:{receipt_path.name}",
        "verification_basis": "TOWER_RELEASE_RECEIPT_V2",
    }, []


def _git_state(root: Path, checkpoint: dict[str, Any] | None) -> dict[str, Any]:
    head = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    porcelain = _git(root, "status", "--porcelain=v1")
    working_changes = sorted(line[3:] for line in porcelain.splitlines() if len(line) >= 4) if porcelain else []

    committed_changes: list[str] = []
    committed_status = "UNKNOWN_NO_VERIFIED_CHECKPOINT"
    if checkpoint is not None and head is not None:
        base_commit = str(checkpoint["commit_sha"])
        diff = _git(root, "diff", "--name-only", f"{base_commit}..{head}", "--")
        if diff is not None:
            committed_changes = sorted(line for line in diff.splitlines() if line)
            committed_status = "COMPUTED_FROM_VERIFIED_CHECKPOINT"

    return {
        "current_git_base": {
            "commit_sha": head,
            "tree_sha": tree,
            "proof_status": "CURRENT_COMMITTED_BASE_NOT_AUTOMATICALLY_VERIFIED",
        },
        "committed_delta_status": committed_status,
        "committed_changed_paths": committed_changes,
        "working_tree_changed_paths": working_changes,
        "rule": "last verified state plus new verified delta",
    }


def build_preflight(
    mission: str,
    *,
    root: Path | None = None,
    memory_path: Path | None = None,
    checkpoint_receipt: Path | None = None,
    exclude_paths: Iterable[Path] = (),
) -> dict[str, Any]:
    """Build a deterministic resource + memory reconstruction receipt."""
    mission = mission.strip()
    if not mission:
        raise ValueError("mission must be a non-empty string")

    root = resolve_repo_root(root)
    memory_path = memory_path.resolve() if memory_path is not None else None
    receipt_path = (
        checkpoint_receipt.resolve()
        if checkpoint_receipt is not None
        else (root / DEFAULT_RELEASE_RECEIPT).resolve()
    )

    resources, duplicates = inventory_resources(root, exclude_paths=exclude_paths)
    memory_status, memory_findings, memory_gaps, memory_sha256 = _read_memory_snapshot(memory_path, root)
    checkpoint, checkpoint_gaps = _load_verified_checkpoint(root, receipt_path)
    git_state = _git_state(root, checkpoint)

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

    status = (
        "COMPLETE"
        if not resource_gaps
        and memory_status == "ANALYZED"
        and not memory_gaps
        and checkpoint is not None
        else "PARTIAL"
    )
    return {
        "schema": "glaciereq.tower.resource-memory-preflight.v3",
        "mission": mission,
        "state": "RESOURCE_RECONSTRUCTED",
        "status": status,
        "tower_boundary": {
            "owns_operator_memory": False,
            "memory_role": "EXTERNAL_CONTINUITY_INPUT",
            "resource_role": "LOCAL_TECHNOLOGY_AND_PROOF_STATE",
        },
        "repository_root": root.as_posix(),
        "last_verified_checkpoint": checkpoint,
        "checkpoint_gaps": checkpoint_gaps,
        "resource_analysis": {
            "resource_count": len(resources),
            "resources": resources,
            "duplicate_content_groups": duplicates,
            "resource_gaps": resource_gaps,
        },
        "memory_analysis": {
            "status": memory_status,
            "source_locator": _memory_locator(memory_path, root) if memory_path else None,
            "source_sha256": memory_sha256,
            "findings": memory_findings,
            "gaps": memory_gaps,
            "evidence_rule": "memory requires a source pointer before VERIFIED_WITH_SOURCE promotion",
        },
        "delta": git_state,
        "continuation_controls": {
            "mode": "ORIENTATION_NOT_PERMISSION",
            "default_behavior": "CONTINUE_WHILE_MEANINGFUL_ROUTE_EXISTS",
            "memory_changes_certainty_not_permission": True,
            "resource_gaps_change_routing_not_global_execution_permission": True,
            "checkpoint_absence_is_not_execution_veto": True,
            "may_use_memory_as_proof_without_source": False,
            "duplicates_count_as_independent_corroboration": False,
            "reuse_prior_verified_state_when_available": True,
            "has_verified_checkpoint": checkpoint is not None,
            "resolve_or_preserve_material_contradictions": True,
        },
    }


def write_preflight(
    output: Path,
    mission: str,
    *,
    root: Path | None = None,
    memory_path: Path | None = None,
    checkpoint_receipt: Path | None = None,
) -> dict[str, Any]:
    root = resolve_repo_root(root)
    output = output if output.is_absolute() else root / output
    output = output.resolve()
    resolved_memory = memory_path.resolve() if memory_path is not None else None
    if resolved_memory is not None and resolved_memory == output:
        raise ValueError("preflight output must not overwrite the external memory snapshot")

    payload = build_preflight(
        mission,
        root=root,
        memory_path=resolved_memory,
        checkpoint_receipt=checkpoint_receipt,
        exclude_paths=(output,),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload
