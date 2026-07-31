#!/usr/bin/env python3
"""One-time assertion that advanced exhibits and nervous-system files converged."""
from pathlib import Path

required = [
    Path(".github/workflows/nervous-system-contract.yml"),
    Path(".glaciereq/nervous-system.node.json"),
    Path("scripts/validate_nervous_system.py"),
    Path("ADVANCED_EXHIBITS.md"),
    Path("quality/advanced_exhibit_atlas.json"),
    Path("tools/audit_advanced_exhibits.py"),
]
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise SystemExit("canonical convergence missing: " + ", ".join(missing))
print("Advanced exhibit and nervous-system surfaces converged.")
