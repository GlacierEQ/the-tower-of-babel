"""Deterministic integrity manifest and reviewed evolution verification."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT

MANIFEST = REPO_ROOT / ".integrity" / "file_hashes.json"
DELTA_MANIFEST = REPO_ROOT / ".integrity" / "approved_delta.json"
_EXCLUDED_PARTS = {
    ".git",
    ".lake",
    "target",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    "build",
    "artifacts",
    "dist",
    "node_modules",
    ".venv",
}
_EXCLUDED_FILES = {
    ".integrity/file_hashes.json",
    ".integrity/approved_delta.json",
    ".integrity/receipt.json",
    ".integrity/ci-trigger.json",
    "artifacts/tower_receipt.json",
    "generated/benchmarks.json",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _eligible(path: Path, manifest_path: Path | None = None) -> bool:
    """Return whether a repository-contained path belongs to the governed domain."""
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError:
        return False
    rel = relative.as_posix()
    parts = relative.parts
    excluded_manifest = None
    if manifest_path is not None:
        try:
            excluded_manifest = manifest_path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            pass
    return (
        path.is_file()
        and not any(part in _EXCLUDED_PARTS for part in parts)
        and not any(part.endswith(".egg-info") for part in parts)
        and rel not in _EXCLUDED_FILES
        and (excluded_manifest is None or rel != excluded_manifest)
        and not rel.endswith((".pyc", ".pyo", ".coverage"))
    )


def hash_file(path: Path) -> str:
    """Hash one artifact without loading the entire file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_hashes(manifest_path: Path | None = None) -> dict[str, str]:
    """Collect deterministic hashes for all governed repository artifacts."""
    return {
        path.relative_to(REPO_ROOT).as_posix(): hash_file(path)
        for path in sorted(REPO_ROOT.rglob("*"))
        if _eligible(path, manifest_path=manifest_path)
    }


def write_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    """Write a new squashed full integrity snapshot."""
    hashes = collect_hashes(manifest_path=path)
    payload = {
        "schema_version": "1.0.0",
        "repo_name": "the-tower-of-babel",
        "hash_algorithm": "sha256",
        "file_count": len(hashes),
        "hashes": hashes,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _invalid_manifest(error: str, manifest_sha256: str = "") -> dict[str, Any]:
    return {
        "ok": False,
        "status": "INVALID_MANIFEST",
        "error": error,
        "manifest_sha256": manifest_sha256,
        "missing": [],
        "changed": [],
        "changed_details": {},
        "unexpected": [],
    }


def _load_delta(
    delta_path: Path,
    *,
    base_manifest_sha256: str,
    expected_hashes: dict[str, str],
) -> tuple[dict[str, str], dict[str, Any]]:
    """Apply one reviewed evolution delta to a full immutable base snapshot.

    The delta is deliberately excluded from the governed file set, just like the
    full manifest itself. Its trust anchor is the reviewed Git commit plus an
    exact SHA-256 binding to the immutable base manifest. Any undeclared drift
    still fails verification.
    """
    if not delta_path.is_file():
        return dict(expected_hashes), {"applied": False, "sha256": ""}

    delta_bytes = delta_path.read_bytes()
    delta_sha256 = hashlib.sha256(delta_bytes).hexdigest()
    try:
        delta = json.loads(delta_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid integrity delta: {exc}") from exc
    if not isinstance(delta, dict):
        raise ValueError("integrity delta root must be an object")
    if delta.get("schema") != "glaciereq.integrity-delta.v1":
        raise ValueError("integrity delta schema must be glaciereq.integrity-delta.v1")
    if delta.get("base_manifest_sha256") != base_manifest_sha256:
        raise ValueError("integrity delta is not bound to the current base manifest")

    changes = delta.get("changes")
    removals = delta.get("removals", [])
    if not isinstance(changes, dict) or not isinstance(removals, list):
        raise ValueError("integrity delta changes/removals have invalid types")

    resolved = dict(expected_hashes)
    for file_path, digest in changes.items():
        if (
            not isinstance(file_path, str)
            or not file_path
            or file_path in _EXCLUDED_FILES
            or not isinstance(digest, str)
            or not _SHA256_RE.fullmatch(digest)
        ):
            raise ValueError(f"invalid integrity delta change: {file_path!r}")
        resolved[file_path] = digest

    for file_path in removals:
        if not isinstance(file_path, str) or not file_path or file_path in _EXCLUDED_FILES:
            raise ValueError(f"invalid integrity delta removal: {file_path!r}")
        if file_path not in resolved:
            raise ValueError(f"integrity delta removes unknown path: {file_path}")
        del resolved[file_path]

    resulting_file_count = delta.get("resulting_file_count")
    if resulting_file_count != len(resolved):
        raise ValueError("integrity delta resulting_file_count does not match resolved hashes")

    return resolved, {
        "applied": True,
        "sha256": delta_sha256,
        "change_count": len(changes),
        "removal_count": len(removals),
    }


def _default_delta_for(path: Path) -> Path:
    """Use repository evolution approval only for the canonical repository manifest."""
    try:
        canonical = path.resolve() == MANIFEST.resolve()
    except OSError:
        canonical = path == MANIFEST
    if canonical:
        return DELTA_MANIFEST
    return path.parent / ".no-approved-delta"


def verify_integrity(
    path: Path = MANIFEST,
    *,
    delta_path: Path | None = None,
) -> dict[str, Any]:
    """Verify a manifest, applying reviewed evolution only to the repository one."""
    if not path.is_file():
        return {
            "ok": False,
            "status": "MISSING_MANIFEST",
            "manifest_sha256": "",
            "missing": [],
            "changed": [],
            "changed_details": {},
            "unexpected": [],
        }
    if delta_path is None:
        delta_path = _default_delta_for(path)
    try:
        manifest_bytes = path.read_bytes()
    except OSError as exc:
        return _invalid_manifest(str(exc))
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    try:
        expected = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _invalid_manifest(str(exc), manifest_sha256)
    if not isinstance(expected, dict):
        return _invalid_manifest("manifest root must be an object", manifest_sha256)
    if expected.get("schema_version") != "1.0.0":
        return _invalid_manifest("schema_version must be 1.0.0", manifest_sha256)
    if expected.get("repo_name") != "the-tower-of-babel":
        return _invalid_manifest("repo_name must be the-tower-of-babel", manifest_sha256)
    if expected.get("hash_algorithm") != "sha256":
        return _invalid_manifest("hash_algorithm must be sha256", manifest_sha256)
    expected_hashes = expected.get("hashes")
    if not isinstance(expected_hashes, dict):
        return _invalid_manifest("hashes must be an object", manifest_sha256)
    if expected.get("file_count") != len(expected_hashes):
        return _invalid_manifest("file_count does not match hashes", manifest_sha256)
    for file_path, digest in expected_hashes.items():
        if (
            not isinstance(file_path, str)
            or not file_path
            or not isinstance(digest, str)
            or not _SHA256_RE.fullmatch(digest)
        ):
            return _invalid_manifest(f"invalid hash entry: {file_path!r}", manifest_sha256)

    try:
        resolved_hashes, delta = _load_delta(
            delta_path,
            base_manifest_sha256=manifest_sha256,
            expected_hashes=expected_hashes,
        )
    except (OSError, ValueError) as exc:
        return _invalid_manifest(str(exc), manifest_sha256)

    current = collect_hashes()
    missing = sorted(set(resolved_hashes) - set(current))
    unexpected = sorted(set(current) - set(resolved_hashes))
    changed = sorted(
        file_path
        for file_path in set(resolved_hashes) & set(current)
        if resolved_hashes[file_path] != current[file_path]
    )
    changed_details = {
        file_path: {
            "expected_sha256": resolved_hashes[file_path],
            "actual_sha256": current[file_path],
        }
        for file_path in changed
    }
    ok = not missing and not unexpected and not changed
    return {
        "ok": ok,
        "status": "VERIFIED" if ok else "DRIFT",
        "manifest_sha256": manifest_sha256,
        "base_file_count": len(expected_hashes),
        "file_count": len(current),
        "integrity_delta": delta,
        "missing": missing,
        "changed": changed,
        "changed_details": changed_details,
        "unexpected": unexpected,
    }
