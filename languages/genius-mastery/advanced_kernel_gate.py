"""Advanced Tower exhibit: Genius-Mastery kernel gate.

Fails closed if GENIUS.yaml is missing kernel:true / purpose Mastery.
Prefers the live kernel tree; otherwise uses the bundled fragment.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

LIVE = [
    Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/Genius-Mastery/GENIUS.yaml"),
    Path.home() / "work" / "Genius-Mastery" / "GENIUS.yaml",
]
FRAGMENT = Path(__file__).with_name("GENIUS.fragment.yaml")


def _load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise SystemExit(f"not a mapping: {path}")
        return data
    # Minimal fallback: require the two load-bearing lines.
    required = {"kernel: true": False, "purpose: Mastery": False, "doctrine: mastery-not-skills": False}
    for line in text.splitlines():
        key = line.strip()
        if key in required:
            required[key] = True
    if not all(required.values()):
        raise SystemExit(f"fragment missing kernel markers: {path}")
    return {"kernel": True, "purpose": "Mastery", "doctrine": "mastery-not-skills"}


def main() -> int:
    source = next((p for p in LIVE if p.is_file()), FRAGMENT)
    if not source.is_file():
        print("GENIUS.yaml missing", file=sys.stderr)
        return 1
    data = _load(source)
    if data.get("kernel") is not True:
        print("kernel is not true", file=sys.stderr)
        return 1
    if str(data.get("purpose")) != "Mastery":
        print("purpose is not Mastery", file=sys.stderr)
        return 1
    print("kernel", source, data.get("package_version") or data.get("schema_version"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
