#!/usr/bin/env python3
"""One-time exact-head reseal marker after workflow-order correction."""
from pathlib import Path

required = [
    Path("README.md"),
    Path("src/tower/generate.py"),
    Path(".github/workflows/advanced-exhibits.yml"),
    Path(".github/workflows/nervous-system-contract.yml"),
    Path(".glaciereq/nervous-system.node.json"),
    Path("scripts/validate_nervous_system.py"),
]
missing = [str(path) for path in required if not path.is_file()]
if missing:
    raise SystemExit("final reseal missing governed surfaces: " + ", ".join(missing))

readme = Path("README.md").read_text(encoding="utf-8")
for repository in (
    "GlacierEQ/aspen-grove-core",
    "GlacierEQ/apex-boot-core",
    "GlacierEQ/Pro_Code",
    "GlacierEQ/pro-code",
):
    if repository not in readme:
        raise SystemExit(f"final reseal missing README mesh link: {repository}")

print("Final advanced-exhibit and nervous-system tree is ready for canonical reseal.")
