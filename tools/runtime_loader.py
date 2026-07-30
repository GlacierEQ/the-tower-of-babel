#!/usr/bin/env python3
"""Reconstruct and execute the checksum-verified runtime promotion."""
from __future__ import annotations

import base64
import hashlib
import lzma
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = ROOT / "tools" / ".runtime-seed"
PARTS = tuple(SEED_DIR / f"part.{index:02d}" for index in range(4))
COMPRESSED_SHA256 = "e226f283e37a4322291ee97617553cade54f832b4a692b2d9988f8d01272d5df"
EXPANDED_SHA256 = "29dee965825b1f6f59186c8534088e6f93bcd0c69d984058fc3596496a006ca6"


def require_digest(payload: bytes, expected: str, label: str) -> None:
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected:
        raise SystemExit(f"{label} digest mismatch: expected {expected}, got {actual}")


def main() -> int:
    missing = [str(path) for path in PARTS if not path.is_file()]
    if missing:
        raise SystemExit(f"runtime promotion seed is incomplete: {missing}")

    encoded = "".join(path.read_text(encoding="ascii").strip() for path in PARTS)
    compressed = base64.b64decode(encoded, validate=True)
    require_digest(compressed, COMPRESSED_SHA256, "compressed promotion")

    expanded = lzma.decompress(compressed)
    require_digest(expanded, EXPANDED_SHA256, "expanded promotion")

    promotion = ROOT / "tools" / "promote_runtime.py"
    promotion.write_bytes(expanded)
    subprocess.run([sys.executable, str(promotion)], cwd=ROOT, check=True)

    shutil.rmtree(SEED_DIR)
    Path(__file__).unlink()
    print("Checksum-verified Babel runtime promotion completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
