"""Easy Tower exhibit: Genius-Mastery naming contract.

Canonical implementation: GlacierEQ/Genius-Mastery src/genius/naming.py
`genius name "Distributed Systems"` → Genius-Distributed-Systems
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_UNSAFE = re.compile(r"[^A-Za-z0-9._\s-]+")
_SPACES = re.compile(r"[\s_]+")


def _canonical_genius_name():
    roots = [
        Path("/Users/kcbflux/APEX_SYSTEM/INFRASTRUCTURE/Genius-Mastery/src"),
        Path.home() / "work" / "Genius-Mastery" / "src",
    ]
    for root in roots:
        naming = root / "genius" / "naming.py"
        if naming.is_file():
            sys.path.insert(0, str(root))
            from genius.naming import genius_name as gn  # type: ignore

            return gn
    return None


def genius_name(purpose: str) -> str:
    canonical = _canonical_genius_name()
    if canonical is not None:
        return canonical(purpose)
    s = purpose.strip()
    if not s:
        raise ValueError("purpose must be non-empty")
    s = _UNSAFE.sub("", s)
    s = _SPACES.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    parts = [p[:1].upper() + p[1:] if p else p for p in s.split("-")]
    return "Genius-" + "-".join(parts)


if __name__ == "__main__":
    got = genius_name("Distributed Systems")
    assert got == "Genius-Distributed-Systems", got
    print(got)
    print("kernel", "yes" if _canonical_genius_name() else "exhibit-fallback")
