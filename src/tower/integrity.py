"""Deterministic integrity manifest and verification."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT

MANIFEST = REPO_ROOT / ".integrity" / "file_hashes.json"
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
    ".integrity/receipt.json",
    "artifacts/tower_receipt.json",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _eligible(path: Path) -> bool:
    """Return whether a path belongs to the governed source/evidence domain."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    return (
        path.is_file()
        and not any(part in _EXCLUDED_PARTS for part in path.parts)
        and not any(part.endswith(".egg-info") for part in path.parts)
        and rel not in _EXCLUDED_FILES
        and not rel.endswith((".pyc", ".pyo", ".coverage"))
    )


def hash_file(path: Path) -> str:
    """Hash one artifact without loading the entire file into memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_hashes() -> dict[str, str]:
    """Collect deterministic hashes for all governed repository artifacts."""
    return {
        path.relative_to(REPO_ROOT).as_posix(): hash_file(path)
        for path in sorted(REPO_ROOT.rglob("*"))
        if _eligible(path)
    }


def write_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    """Write the canonical integrity manifest."""
    hashes = collect_hashes()
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
        "unexpected": [],
    }


def verify_integrity(path: Path = MANIFEST) -> dict[str, Any]:
    """Verify one immutable manifest snapshot against governed artifacts."""
    if not path.is_file():
        return {
            "ok": False,
            "status": "MISSING_MANIFEST",
            "manifest_sha256": "",
            "missing": [],
            "changed": [],
            "unexpected": [],
        }
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
        if not isinstance(file_path, str) or not file_path or not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            return _invalid_manifest(f"invalid hash entry: {file_path!r}", manifest_sha256)

    current = collect_hashes()
    missing = sorted(set(expected_hashes) - set(current))
    unexpected = sorted(set(current) - set(expected_hashes))
    changed = sorted(
        file_path
        for file_path in set(expected_hashes) & set(current)
        if expected_hashes[file_path] != current[file_path]
    )
    ok = not missing and not unexpected and not changed
    return {
        "ok": ok,
        "status": "VERIFIED" if ok else "DRIFT",
        "manifest_sha256": manifest_sha256,
        "file_count": len(current),
        "missing": missing,
        "changed": changed,
        "unexpected": unexpected,
    }
