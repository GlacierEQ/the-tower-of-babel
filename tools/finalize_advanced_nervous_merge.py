#!/usr/bin/env python3
"""One-time convergence of advanced exhibits with the portfolio nervous system."""
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

generator = Path("src/tower/generate.py")
source = generator.read_text(encoding="utf-8")
akos_row = "| [`GlacierEQ/AKOS`](https://github.com/GlacierEQ/AKOS) | Governance and agent-orchestration peer | Portfolio doctrine and execution governance; integration is contract-driven. |"
mesh_rows = """| [`GlacierEQ/AKOS`](https://github.com/GlacierEQ/AKOS) | Governance and agent-orchestration authority | Canonical governance, evidence, completion, and operating-sequence contract. |
| [`GlacierEQ/aspen-grove-core`](https://github.com/GlacierEQ/aspen-grove-core) | Memory and context-continuity peer | Preserves durable context and continuity without competing with Tower placement authority. |
| [`GlacierEQ/apex-boot-core`](https://github.com/GlacierEQ/apex-boot-core) | Identity and initialization peer | Activates identity, capability, and initialization contracts before governed execution. |
| [`GlacierEQ/Pro_Code`](https://github.com/GlacierEQ/Pro_Code) | Engineering doctrine peer | Publishes standards, doctrine, and playbooks consumed by implementation systems. |
| [`GlacierEQ/pro-code`](https://github.com/GlacierEQ/pro-code) | Governed engineering-execution peer | Executes, verifies, cures, and persists engineering changes under shared governance. |"""
if "GlacierEQ/aspen-grove-core" not in source:
    if akos_row not in source:
        raise SystemExit("portfolio mesh insertion point missing")
    source = source.replace(akos_row, mesh_rows)
    generator.write_text(source, encoding="utf-8")

print("Advanced exhibit and nervous-system surfaces converged.")
