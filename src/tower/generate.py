'''Generate all derived Tower surfaces from the canonical registry.'''
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT, TowerRegistry, load_registry, validate_registry

GENERATED_DIR = REPO_ROOT / "generated"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n").encode("utf-8")


def _markdown_table(registry: TowerRegistry) -> str:
    rows = [
        "| # | Technology | Class | What | Where | When | Why | Evidence | Easy | Advanced |",
        "|---:|---|---|---|---|---|---|---|---|---|",
    ]
    for index, tech in enumerate(registry.technologies, 1):
        def esc(value: object) -> str:
            return str(value).replace("|", r"\|").replace("\n", " ")
        rows.append(
            f"| {index} | **{esc(tech['name'])}** `{esc(tech['extension'])}` | "
            f"{esc(tech['artifact_type'])} | {esc(tech['what'])} | {esc(tech['where'])} | "
            f"{esc(tech['when'])} | {esc(tech['why'])} | `{esc(tech['evidence_state'])}` / "
            f"`{esc(tech['proof_class'])}` | [{Path(tech['easy_example']).name}]({tech['easy_example']}) | "
            f"[{Path(tech['advanced_example']).name}]({tech['advanced_example']}) |"
        )
    return "\n".join(rows)


def render_readme(registry: TowerRegistry) -> str:
    count = len(registry.technologies)
    categories: dict[str, list[str]] = {}
    for tech in registry.technologies:
        categories.setdefault(tech["category"], []).append(tech["name"])
    coverage = "\n".join(
        f"- **{category.replace('_', ' ').title()}** — {', '.join(names)}"
        for category, names in sorted(categories.items())
    )
    return f'''# The Tower of Babel

> **A governed multi-language systems engineering Rosetta Stone**  
> **{count} technology floors · W4H+How placement · easy and advanced exhibits · executable proof classes**

The Tower of Babel is the canonical authority for language, format, compiler, hardware, serialization, and formal-verification boundaries across the GlacierEQ system family.

Every floor answers:

- **What** does this technology uniquely contribute?
- **Where** does it belong in the architecture?
- **When** should it be activated?
- **Why** is it the correct boundary?
- **How** does it achieve that result?
- What is the **easy example**?
- What is the **advanced example**?
- What proof currently supports the claim?

`registry/tower.yml` is the root authority. Its contained `tower.d/*.json` fragments and the index form one canonical registry. The README, runtime registry, sidecar counts, build manifests, interface graph, maturity report, Megamind map, mesh metadata, and integrity receipt are derived from it.

## Architecture

```text
Megamind mission and specialist selection
                ↓
Tower technology and proof contract
                ↓
Per-floor toolchain / build / blocker report
                ↓
Cross-language interface contract
                ↓
Execution evidence and deterministic receipt
```

## Canonical technology matrix

{_markdown_table(registry)}

## Domain coverage

{coverage}

## Evidence states

| State | Meaning |
|---|---|
| `illustrative` | Teaches syntax or the central concept. |
| `compiles` | A pinned compiler or schema tool accepts the exhibit. |
| `tested` | Automated behavior checks pass. |
| `benchmark` | A reproducible performance measurement exists. |
| `hardware_gated` | The exhibit is complete but requires declared hardware. |
| `toolchain_gated` | The exhibit is complete but its compiler is not in the portable CI image. |
| `service_gated` | A declared external service is required. |
| `formally_verified` | A proof kernel accepts the theorem. |
| `integrated` | The floor participates in the flagship polyglot system. |
| `production_reference` | Operational failure handling, observability, and deployment evidence exist. |

## Commands

```bash
python -m pip install -e .[dev]
tower validate
tower generate --check
tower build --all --allow-blocked
tower integrity verify
tower benchmark python c cpp rust go typescript webassembly
tower proof-report --build-report artifacts/build-report.json
tower receipt
tower spec rust
tower megamind-map
python flagship/run_pipeline.py
```

## Flagship polyglot mission pipeline

The flagship system traverses multiple floors:

```text
TypeScript ingress
    → ProtoJSON mission contract
Python planner
    → capability plan
Rust authority governor
    → allow/block decision
Go telemetry emitter
    → execution event
SQL canonical state
    → persisted mission
WebAssembly sandbox
    → constrained tool example
Lean 4
    → receipt-chain invariant
Tower receipt
```

See [`flagship/README.md`](flagship/README.md).

## Governance

- New technologies are added only through the canonical registry rooted at `registry/tower.yml`.
- Generated surfaces may not be hand-edited.
- Claims must carry an evidence state and proof class.
- Missing toolchains and hardware produce exact blockers, never false success.
- Cross-language contracts are versioned.
- Megamind consumes Tower exports; it does not maintain a competing technology registry.

## License

MIT — see [`LICENSE`](LICENSE).
'''


def render_runtime_registry(registry: TowerRegistry) -> str:
    return '''#!/usr/bin/env python3
"""Compatibility facade generated from registry/tower.yml."""
from tower.registry import load_registry, validate_registry


def _validated_registry():
    registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        raise RuntimeError("Invalid Tower registry: " + "; ".join(errors))
    return registry


class BabelRegistryEngine:
    def __init__(self):
        self.registry = _validated_registry()

    def get_spec(self, lang_key: str):
        row = self.registry.by_id(lang_key)
        if row is None:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {**row, "status": "VALIDATED_W4H_SPEC", "ok": True}


_REGISTRY = _validated_registry()
BABEL_REGISTRY = {row["id"]: row for row in _REGISTRY.technologies}


if __name__ == "__main__":
    print(f"Tower of Babel Registry Initialized: {len(_REGISTRY.technologies)} Technologies Registered.")
'''


def render_sidecar() -> str:
    return '''#!/usr/bin/env python3
"""Tower sidecar: derived telemetry, never hard-coded counts."""
import json
import time

from tower.integrity import verify_integrity
from tower.registry import load_registry


def get_telemetry():
    registry = load_registry()
    integrity = verify_integrity()
    technologies = registry.technologies
    return {
        "repo_name": "the-tower-of-babel",
        "status": "OPERATIONAL" if integrity["ok"] else "DEGRADED",
        "timestamp": time.time(),
        "integrity": integrity,
        "total_technologies": len(technologies),
        "total_exhibits": len(technologies) * 2,
        "evidence_states": sorted({row["evidence_state"] for row in technologies}),
        "version": "1.1.0",
    }


if __name__ == "__main__":
    print(json.dumps(get_telemetry(), indent=2, sort_keys=True))
'''


def build_surfaces(registry: TowerRegistry) -> dict[Path, bytes]:
    commands = {}
    interfaces: dict[str, list[str]] = {}
    maturity = {}
    megamind = {"tower_id": registry.payload["tower_id"], "technologies": {}}
    for tech in registry.technologies:
        tech_id = tech["id"]
        commands[tech_id] = {"toolchain": tech["toolchain"], "execution": tech["execution"]}
        interfaces[tech_id] = list(tech["interfaces"])
        maturity[tech_id] = {
            "evidence_state": tech["evidence_state"],
            "proof_class": tech["proof_class"],
            "easy_example": tech["easy_example"],
            "advanced_example": tech["advanced_example"],
        }
        megamind["technologies"][tech_id] = {
            "agents": tech["megamind"]["agents"],
            "pistons": tech["megamind"]["pistons"],
            "interfaces": tech["interfaces"],
            "activation_when": tech["when"],
            "proof_class": tech["proof_class"],
        }

    smithery = {
        "name": "tower-of-babel",
        "version": "1.1.0",
        "publication_status": "declared-not-published",
        "publication_rule": "Publication requires an MCP package plus an external registry receipt.",
        "capabilities": [f"technology:{row['id']}" for row in registry.technologies],
        "commands": ["validate", "build", "benchmark", "proof-report", "spec", "receipt", "megamind-map"],
        "source": "registry/tower.yml",
    }
    spiral = {
        "family": "tower-of-babel",
        "role": "canonical-technology-authority",
        "activation_status": "declared",
        "activation_rule": "A capability becomes active only after Spiral Engine returns an admission receipt.",
        "nodes": [row["id"] for row in registry.technologies],
        "edges": [
            {"from": tech_id, "to": interface, "type": "exposes_interface"}
            for tech_id, values in interfaces.items()
            for interface in values
        ],
    }
    links = ["# Tower Link Library", ""]
    for tech in registry.technologies:
        links.append(f"## {tech['name']}")
        links.extend(f"- {uri}" for uri in tech["primary_evidence"])
        links.append("")

    surfaces: dict[Path, bytes] = {
        REPO_ROOT / "README.md": render_readme(registry).encode(),
        REPO_ROOT / "src" / "babel_registry.py": render_runtime_registry(registry).encode(),
        REPO_ROOT / "mastermind_sidecar.py": render_sidecar().encode(),
        REPO_ROOT / "src" / "tower" / "data" / "tower.yml": registry.source.read_bytes(),
        GENERATED_DIR / "build_commands.json": _json_bytes(commands),
        GENERATED_DIR / "interfaces.json": _json_bytes(interfaces),
        GENERATED_DIR / "maturity.json": _json_bytes(maturity),
        GENERATED_DIR / "megamind.technology-map.json": _json_bytes(megamind),
        GENERATED_DIR / "smithery.registry.json": _json_bytes(smithery),
        GENERATED_DIR / "spiral-engine.registry.json": _json_bytes(spiral),
        GENERATED_DIR / "link_library.md": ("\n".join(links) + "\n").encode(),
    }
    for fragment in registry.fragment_files:
        relative = fragment.relative_to(registry.source.parent)
        surfaces[REPO_ROOT / "src" / "tower" / "data" / relative] = fragment.read_bytes()
    return surfaces


def generate(*, check: bool = False) -> list[str]:
    registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        return errors
    drift: list[str] = []
    for path, content in build_surfaces(registry).items():
        if check:
            if not path.is_file() or path.read_bytes() != content:
                drift.append(str(path.relative_to(REPO_ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return drift


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = generate(check=args.check)
    if errors:
        print("\n".join(errors))
        return 1
    print("Tower generated surfaces are current." if args.check else "Tower generated surfaces written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
