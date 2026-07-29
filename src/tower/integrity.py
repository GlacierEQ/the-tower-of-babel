"""Deterministic integrity manifest and verification."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT

MANIFEST = REPO_ROOT / ".integrity" / "file_hashes.json"
_EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", "build", "artifacts", "dist", "node_modules", ".venv"}
_EXCLUDED_FILES = {
    ".integrity/file_hashes.json",
    ".integrity/receipt.json",
    "artifacts/tower_receipt.json",
}


def _eligible(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return (
        path.is_file()
        and not any(part in _EXCLUDED_PARTS for part in path.parts)
        and rel not in _EXCLUDED_FILES
        and not rel.endswith((".pyc", ".pyo"))
    )


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_hashes() -> dict[str, str]:
    return {
        path.relative_to(REPO_ROOT).as_posix(): hash_file(path)
        for path in sorted(REPO_ROOT.rglob("*"))
        if _eligible(path)
    }


def write_manifest(path: Path = MANIFEST) -> dict[str, Any]:
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


def verify_integrity(path: Path = MANIFEST) -> dict[str, Any]:
    if not path.is_file():
        return {"ok": False, "status": "MISSING_MANIFEST", "missing": [], "changed": [], "unexpected": []}
    try:
        expected = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "status": "INVALID_MANIFEST", "error": str(exc), "missing": [], "changed": [], "unexpected": []}
    expected_hashes = expected.get("hashes", {})
    if not isinstance(expected_hashes, dict):
        return {"ok": False, "status": "INVALID_MANIFEST", "missing": [], "changed": [], "unexpected": []}
    current = collect_hashes()
    missing = sorted(set(expected_hashes) - set(current))
    unexpected = sorted(set(current) - set(expected_hashes))
    changed = sorted(
        path for path in set(expected_hashes) & set(current)
        if expected_hashes[path] != current[path]
    )
    ok = not missing and not unexpected and not changed
    return {
        "ok": ok,
        "status": "VERIFIED" if ok else "DRIFT",
        "file_count": len(current),
        "missing": missing,
        "changed": changed,
        "unexpected": unexpected,
    }
