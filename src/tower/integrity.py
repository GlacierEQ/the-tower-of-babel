"""Evolvable repository integrity and explicit evidence snapshots."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT

LEGACY_MANIFEST = REPO_ROOT / ".integrity" / "file_hashes.json"
LEGACY_DELTA_MANIFEST = REPO_ROOT / ".integrity" / "approved_delta.json"
DEFAULT_SNAPSHOT = REPO_ROOT / "artifacts" / "integrity-snapshot.json"
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
    "receipts",
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


def _eligible_relative(relative: Path) -> bool:
    rel = relative.as_posix()
    return (
        not any(part in _EXCLUDED_PARTS for part in relative.parts)
        and not any(part.endswith(".egg-info") for part in relative.parts)
        and rel not in _EXCLUDED_FILES
        and not rel.endswith((".pyc", ".pyo", ".coverage"))
    )


def _eligible(path: Path, manifest_path: Path | None = None) -> bool:
    try:
        relative = path.relative_to(REPO_ROOT)
    except ValueError:
        return False
    excluded_manifest = None
    if manifest_path is not None:
        try:
            excluded_manifest = (
                manifest_path.resolve().relative_to(REPO_ROOT).as_posix()
            )
        except (OSError, ValueError):
            pass
    return (
        path.is_file()
        and _eligible_relative(relative)
        and (excluded_manifest is None or relative.as_posix() != excluded_manifest)
    )


def hash_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_hashes(manifest_path: Path | None = None) -> dict[str, str]:
    """Collect deterministic hashes for an explicit evidence snapshot."""
    return {
        path.relative_to(REPO_ROOT).as_posix(): hash_file(path)
        for path in sorted(REPO_ROOT.rglob("*"))
        if _eligible(path, manifest_path=manifest_path)
    }


def write_manifest(path: Path = DEFAULT_SNAPSHOT) -> dict[str, Any]:
    """Write an explicit point-in-time evidence snapshot.

    Snapshots are reproducibility artifacts. They are not the live mutation gate.
    """
    hashes = collect_hashes(manifest_path=path)
    payload = {
        "schema_version": "2.0.0",
        "mode": "EXPLICIT_EVIDENCE_SNAPSHOT",
        "repo_name": "the-tower-of-babel",
        "hash_algorithm": "sha256",
        "file_count": len(hashes),
        "hashes": hashes,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


def _invalid_snapshot(error: str, snapshot_sha256: str = "") -> dict[str, Any]:
    return {
        "ok": False,
        "status": "INVALID_SNAPSHOT",
        "error": error,
        "snapshot_sha256": snapshot_sha256,
        "missing": [],
        "changed": [],
        "unexpected": [],
    }


def _load_delta(
    delta_path: Path,
    *,
    base_manifest_sha256: str,
    expected_hashes: dict[str, str],
) -> tuple[dict[str, str], dict[str, Any]]:
    """Compatibility support for intentionally supplied historical snapshots."""
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
        raise ValueError("integrity delta is not bound to the supplied base snapshot")

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
        if (
            not isinstance(file_path, str)
            or not file_path
            or file_path in _EXCLUDED_FILES
        ):
            raise ValueError(f"invalid integrity delta removal: {file_path!r}")
        if file_path not in resolved:
            raise ValueError(f"integrity delta removes unknown path: {file_path}")
        del resolved[file_path]

    resulting_file_count = delta.get("resulting_file_count")
    if resulting_file_count != len(resolved):
        raise ValueError(
            "integrity delta resulting_file_count does not match resolved hashes"
        )

    return resolved, {
        "applied": True,
        "sha256": delta_sha256,
        "change_count": len(changes),
        "removal_count": len(removals),
    }


def _verify_snapshot(path: Path, *, delta_path: Path | None = None) -> dict[str, Any]:
    if not path.is_file():
        return {
            "ok": False,
            "status": "MISSING_SNAPSHOT",
            "snapshot_sha256": "",
            "missing": [],
            "changed": [],
            "unexpected": [],
        }
    try:
        snapshot_bytes = path.read_bytes()
    except OSError as exc:
        return _invalid_snapshot(str(exc))
    snapshot_sha256 = hashlib.sha256(snapshot_bytes).hexdigest()
    try:
        expected = json.loads(snapshot_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return _invalid_snapshot(str(exc), snapshot_sha256)
    if not isinstance(expected, dict):
        return _invalid_snapshot("snapshot root must be an object", snapshot_sha256)
    if expected.get("schema_version") not in {"1.0.0", "2.0.0"}:
        return _invalid_snapshot("unsupported snapshot schema_version", snapshot_sha256)
    if expected.get("repo_name") != "the-tower-of-babel":
        return _invalid_snapshot(
            "repo_name must be the-tower-of-babel", snapshot_sha256
        )
    if expected.get("hash_algorithm") != "sha256":
        return _invalid_snapshot("hash_algorithm must be sha256", snapshot_sha256)
    expected_hashes = expected.get("hashes")
    if not isinstance(expected_hashes, dict):
        return _invalid_snapshot("hashes must be an object", snapshot_sha256)
    if expected.get("file_count") != len(expected_hashes):
        return _invalid_snapshot("file_count does not match hashes", snapshot_sha256)
    for file_path, digest in expected_hashes.items():
        if (
            not isinstance(file_path, str)
            or not file_path
            or not isinstance(digest, str)
            or not _SHA256_RE.fullmatch(digest)
        ):
            return _invalid_snapshot(
                f"invalid hash entry: {file_path!r}", snapshot_sha256
            )

    resolved_hashes = dict(expected_hashes)
    delta = {"applied": False, "sha256": ""}
    if delta_path is not None:
        try:
            resolved_hashes, delta = _load_delta(
                delta_path,
                base_manifest_sha256=snapshot_sha256,
                expected_hashes=expected_hashes,
            )
        except (OSError, ValueError) as exc:
            return _invalid_snapshot(str(exc), snapshot_sha256)

    current = collect_hashes(manifest_path=path)
    missing = sorted(set(resolved_hashes) - set(current))
    unexpected = sorted(set(current) - set(resolved_hashes))
    changed = sorted(
        file_path
        for file_path in set(resolved_hashes) & set(current)
        if resolved_hashes[file_path] != current[file_path]
    )
    ok = not missing and not unexpected and not changed
    return {
        "ok": ok,
        "status": "VERIFIED" if ok else "DRIFT",
        "mode": "EXPLICIT_EVIDENCE_SNAPSHOT",
        "snapshot_sha256": snapshot_sha256,
        "file_count": len(current),
        "integrity_delta": delta,
        "missing": missing,
        "changed": changed,
        "unexpected": unexpected,
    }


def _git(*args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _git_index_integrity() -> dict[str, Any]:
    """Verify the working repository against its reviewed Git HEAD/index."""
    try:
        commit_sha = _git("rev-parse", "HEAD").strip()
        tree_sha = _git("rev-parse", "HEAD^{tree}").strip()
        tracked_raw = _git("ls-files", "-z")
        changed_raw = _git(
            "diff", "--name-only", "--diff-filter=ACDMRTUXB", "HEAD", "--"
        )
        untracked_raw = _git("ls-files", "--others", "--exclude-standard", "-z")
        tree_listing = _git("ls-tree", "-r", "--full-tree", "HEAD")
    except (OSError, subprocess.CalledProcessError) as exc:
        return {
            "ok": False,
            "status": "NOT_GIT_CHECKOUT",
            "mode": "GIT_INDEX_LIVE",
            "error": str(exc),
            "changed": [],
            "unexpected": [],
        }

    tracked = sorted(
        rel for rel in tracked_raw.split("\0") if rel and _eligible_relative(Path(rel))
    )
    changed = sorted(
        rel.strip()
        for rel in changed_raw.splitlines()
        if rel.strip() and _eligible_relative(Path(rel.strip()))
    )
    unexpected = sorted(
        rel
        for rel in untracked_raw.split("\0")
        if rel and _eligible_relative(Path(rel))
    )
    ok = not changed and not unexpected
    receipt_body = {
        "commit_sha": commit_sha,
        "tree_sha": tree_sha,
        "tracked_file_count": len(tracked),
        "tree_listing_sha256": hashlib.sha256(tree_listing.encode("utf-8")).hexdigest(),
    }
    receipt_sha256 = hashlib.sha256(
        json.dumps(receipt_body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "ok": ok,
        "status": "VERIFIED" if ok else "DRIFT",
        "mode": "GIT_INDEX_LIVE",
        **receipt_body,
        "receipt_sha256": receipt_sha256,
        "changed": changed,
        "unexpected": unexpected,
        "selection_mode": "CURRENT_HEAD_REVISABLE",
        "evolution_note": "Integrity verifies the reviewed current tree; stronger reviewed commits may replace it without rewriting a static baseline.",
    }


def verify_integrity(
    path: Path | None = None,
    *,
    delta_path: Path | None = None,
) -> dict[str, Any]:
    """Verify live Git state by default, or an explicit evidence snapshot by request."""
    if path is None:
        return _git_index_integrity()
    return _verify_snapshot(path, delta_path=delta_path)
