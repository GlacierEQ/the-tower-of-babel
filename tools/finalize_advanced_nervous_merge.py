#!/usr/bin/env python3
"""One-time exact-head reseal after total Haskell path validation."""
from pathlib import Path

path = Path("languages/haskell/advanced_ast_validator.hs")
source = path.read_text(encoding="utf-8")
required = (
    'safeRelativePath [] = Left (EmptyIdentifier "path")',
    "safeRelativePath path@('/' : _) = Left (UnsafeRelativePath path)",
)
for fragment in required:
    if fragment not in source:
        raise SystemExit(f"total Haskell validation fragment missing: {fragment}")
if "head path" in source:
    raise SystemExit("partial Haskell head operation remains")
print("Haskell path validation is total and ready for canonical reseal.")
