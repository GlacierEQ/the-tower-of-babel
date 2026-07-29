#!/usr/bin/env python3
"""Verify and install the canonical Tower of Babel manifest engine.

This one-shot installer exists only to atomically transfer the generated
repository tree. It verifies the compressed and expanded payloads before
writing any path, rejects path traversal, and removes all seed artifacts
when installation succeeds.
"""
from __future__ import annotations

import base64
import hashlib
import json
import lzma
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "tools" / ".seed-v4"
PARTS = [SEED_DIR / f"part.{index:02d}" for index in range(4)]
EXPECTED_COMPRESSED_SHA256 = "5aff7864872b0398e4105137a7125b7b9458216a1d846d6b8bbe73c47defbaaf"
EXPECTED_RAW_SHA256 = "2549e770727b2694fc0287c123a7f075d48955451aeb69328a003383236da221"


def safe_target(relative_path: str) -> Path:
    path = Path(relative_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"unsafe payload path: {relative_path}")
    target = (ROOT / path).resolve()
    if ROOT.resolve() not in target.parents and target != ROOT.resolve():
        raise ValueError(f"payload path escapes repository: {relative_path}")
    return target


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    missing = [str(path.relative_to(ROOT)) for path in PARTS if not path.is_file()]
    if missing:
        raise SystemExit(f"missing seed segments: {', '.join(missing)}")

    encoded = "".join(path.read_text(encoding="utf-8").strip() for path in PARTS)
    compressed = base64.b64decode(encoded, validate=True)
    compressed_digest = digest(compressed)
    if compressed_digest != EXPECTED_COMPRESSED_SHA256:
        raise SystemExit(
            "compressed payload digest mismatch: "
            f"expected {EXPECTED_COMPRESSED_SHA256}, got {compressed_digest}"
        )

    raw = lzma.decompress(compressed)
    raw_digest = digest(raw)
    if raw_digest != EXPECTED_RAW_SHA256:
        raise SystemExit(
            "expanded payload digest mismatch: "
            f"expected {EXPECTED_RAW_SHA256}, got {raw_digest}"
        )

    files = json.loads(raw.decode("utf-8"))
    if not isinstance(files, dict) or not files:
        raise SystemExit("canonical payload is not a non-empty file map")

    targets: list[tuple[Path, str]] = []
    for relative_path, content in files.items():
        if not isinstance(relative_path, str) or not isinstance(content, str):
            raise SystemExit("canonical payload contains a non-text file entry")
        targets.append((safe_target(relative_path), content))

    for target, content in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    shutil.rmtree(SEED_DIR)
    Path(__file__).unlink()
    bootstrap = ROOT / ".github" / "workflows" / "install-canonical-manifest.yml"
    if bootstrap.exists():
        bootstrap.unlink()

    print(
        json.dumps(
            {
                "status": "INSTALLED",
                "files_written": len(targets),
                "raw_sha256": raw_digest,
                "compressed_sha256": compressed_digest,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
