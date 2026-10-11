'''Generate all derived Tower surfaces from the APEX technology registry.'''
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .registry import REPO_ROOT, TowerRegistry, load_registry, validate_registry

GENERATED_DIR = REPO_ROOT / "generated"

EVIDENCE_TIERS = {
    "illustrative": "concept_only",
    "toolchain_gated": "gated_reference",
    "service_gated": "gated_reference",
    "hardware_gated": "gated_reference",
    "compiles": "runnable_reference",
    "tested": "tested_implementation",
    "benchmark": "benchmarked_implementation",
    "formally_verified": "tested_implementation",
    "integrated": "integrated_capability",
    "production_reference": "production_reference",
}


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
    exhibit_count = count * 2
    behavioral_count = sum(1 for tech in registry.technologies if tech["proof_class"] == "behavioral")
    formal_count = sum(1 for tech in registry.technologies if tech["proof_class"] == "formal")
    gated_count = sum(
        1 for tech in registry.technologies
        if tech["evidence_state"] in {"hardware_gated", "toolchain_gated", "service_gated"}
    )
    categories: dict[str, list[str]] = {}
    for tech in registry.technologies:
        categories.setdefault(tech["category"], []).append(tech["name"])
    coverage = "\n".join(
        f"- **{category.replace('_', ' ').title()}** — {', '.join(names)}"
        for category, names in sorted(categories.items())
    )
    return f"""# The Tower of Babel — APEX

> **Executable polyglot architecture selection for maximum coherent advance.**

[![Tower Verification](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml)
[![Quality Gate](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml)
[![Spiral Engine](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml)

The Tower decides **which technology belongs at which engineering boundary, why it belongs there, how it interoperates with adjacent lanes, how it fails, and what evidence would justify replacing it**.

It is not a language museum, a monoculture generator, or an authority over Casey Barton's intended system. Casey's project intent controls direction. The Tower supplies boundary analysis, executable comparison, interoperability, proof, and a continuously revisable frontier.

## APEX law

```text
INTENDED SYSTEM + CURRENT SOURCE STATE + VERIFIED PRIOR GAINS
→ identify real boundaries and bottlenecks
→ observe current frontier technology
→ generate multiple strong candidates
→ compose best-fit technologies by lane
→ build the strongest justified reversible experiment
→ measure + adversarially break + operate
→ preserve all unique gains
→ keep the non-dominated winner(s)
→ expand again
```

**Smallness and uniformity have zero intrinsic score.** A one-language repository is correct when one technology actually dominates its boundaries. A six-language repository is correct when six technologies each materially outperform alternatives in their lane and their interfaces are explicit.

## The system in one minute

| Capability | What the Tower does |
|---|---|
| **Boundary decomposition** | Turns a mission into explicit runtime, memory, compute, proof, interface, policy, and presentation concerns. |
| **Technology placement** | Records What, Where, When, Why, and How for every admitted language, format, compiler layer, database, HDL, and proof system. |
| **Frontier metabolism** | Ingests fresh primary-source technology signals and maps credible advances to real GlacierEQ bottlenecks. |
| **Executable learning** | Pairs each technology with an approachable exhibit and a substantive advanced implementation. |
| **Truthful verification** | Compiles, tests, benchmarks, integrates, or formally verifies claims; missing requirements become exact blockers. |
| **Cross-language composition** | Publishes versioned interfaces so specialized components cooperate without ambiguous ownership. |
| **Deterministic evidence** | Seals source state and emits reproducible build, proof, integrity, and release receipts. |

| APEX surface | Count |
|---|---:|
| Technology floors | **{count}** |
| Easy + advanced exhibits | **{exhibit_count}** |
| Behavioral proof floors | **{behavioral_count}** |
| Formal proof floors | **{formal_count}** |
| Explicitly gated floors | **{gated_count}** |

## From mission to APEX receipt

```text
human objective / agent mission / system requirement
                         │
                         ▼
              Spiral or Megamind request
                         │
                         ▼
             APEX Tower source registry
       placement · interfaces · owners · proof gate
                         │
                         ▼
        candidate composition / bounded experiment
                         │
                         ▼
         build / test / benchmark / formal check
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   stronger proven lane            exact blocker
          │                    toolchain · hardware
          ▼                       service · evidence
  cross-language execution
          │
          ▼
 deterministic evidence receipt + next frontier cursor
```

## Start the Tower

```bash
python -m pip install -e .[dev]

tower validate
tower generate --check
tower integrity verify

tower spec rust
tower build rust
tower benchmark rust
tower megamind-map

tower spiral question \\
  --seed tower-demo \\
  --prompt-hint "maximum coherent multi-agent architecture"

python flagship/run_pipeline.py
```

Run a complete portable proof pass:

```bash
tower build --all --allow-blocked --output artifacts/build-report.json
tower benchmark python c cpp rust go typescript webassembly \\
  --output artifacts/benchmarks.json
tower proof-report \\
  --build-report artifacts/build-report.json \\
  --benchmark-report artifacts/benchmarks.json \\
  --allow-blocked \\
  --output artifacts/proof-report.json
tower receipt \\
  --build-report artifacts/build-report.json \\
  --output artifacts/tower_receipt.json
```

## APEX source state

`registry/tower.yml` is the authored APEX technology source index. It names contained `registry/tower.d/*.json` technology fragments and `registry/advanced-claim-contracts.json`. Generated projections derive from that source state.

The source registry proves what the Tower currently knows and what evidence is attached. It does **not** redefine the intended system downward when implementation lags the target.

```text
registry/tower.yml + tower.d fragments + advanced claim contracts
                  │
                  ▼
        validation and path containment
                  │
                  ▼
        deterministic surface generation
                  │
        ┌─────────┼─────────┬──────────┬───────────┐
        ▼         ▼         ▼          ▼           ▼
     README   build map  interfaces  maturity  agent maps
        │         │         │          │           │
        └─────────┴─────────┴──────────┴───────────┘
                  │
                  ▼
       build · benchmark · proof · receipt · evolve
```

### Tower of Babel lane law

A technology earns a lane when the registry establishes:

- a unique responsibility and explicit boundary;
- activation conditions and measurable reason it beats alternatives there;
- easy and advanced exhibits;
- pinned toolchain references and execution commands;
- hardware, service, and dependency constraints;
- explicit interfaces and owners;
- evidence state and proof class matching checked-in verification;
- replacement criteria if a stronger technology appears;
- preservation accounting for any prior capability it supersedes.

No language receives estate-wide privilege. Python, TypeScript, Rust, Go, SQL, Julia, Fortran, Triton, CUDA, Zig, C/C++, Elixir/Erlang, Datalog, Lean, Coq, TLA+, Rego, WebAssembly, and future technologies compete at the boundaries they are actually good at.

### Flagship polyglot mission

```text
TypeScript ingress
    → mission contract
Python planner
    → capability plan
Rust authority boundary
    → allow / block decision
Go telemetry
    → execution event
SQL durable state
    → persisted mission
WebAssembly sandbox
    → constrained tool boundary
Lean 4
    → receipt-chain invariant
Tower APEX receipt
```

See [`flagship/README.md`](flagship/README.md) and run `python flagship/run_pipeline.py`.

### Proof before activation

| Evidence state | Meaning |
|---|---|
| `illustrative` | Teaches syntax or the central concept; no stronger runtime claim is made. |
| `compiles` | A pinned compiler or schema tool accepts the exhibit. |
| `tested` | Automated behavioral checks pass. |
| `benchmark` | A reproducible performance measurement exists. |
| `hardware_gated` | The implementation is present but requires declared hardware. |
| `toolchain_gated` | The implementation is present but its compiler is absent from portable CI. |
| `service_gated` | A declared external service is required. |
| `formally_verified` | A proof kernel accepts the theorem. |
| `integrated` | The floor participates in the flagship multi-language system. |
| `production_reference` | Operational failure handling, observability, and deployment evidence exist. |

Evidence limits what may be claimed. It does not prohibit a reversible ambitious experiment.

## Advanced Exhibit Atlas

The easy exhibit teaches the technology. The advanced exhibit owns a real engineering boundary, exposes failure behavior, and terminates in proof or an exact blocker. [`ADVANCED_EXHIBITS.md`](ADVANCED_EXHIBITS.md) publishes signature engineering moves and claim boundaries; [`quality/advanced_exhibit_atlas.json`](quality/advanced_exhibit_atlas.json) provides the same map to agents and automation.

## Complete APEX technology map

The matrix is generated from the APEX source registry. Change source state and exhibits, not the generated README.

<details>
<summary><strong>Open the complete placement, proof, and exhibit matrix</strong></summary>

{_markdown_table(registry)}

</details>

### Domain coverage

{coverage}

## Machine entrypoint

An AI system should use Tower source state as evidence and selection input, not as authority to shrink intent.

1. **Initialize** from `registry/tower.yml` or generated technology maps.
2. **Resolve** a mission into explicit architecture concerns and interfaces.
3. **Generate candidates** from incumbent and frontier technologies.
4. **Select or compose** technologies whose boundary advantages are measurable.
5. **Reject** ambiguous ownership, missing evidence, undeclared interfaces, and capability loss.
6. **Execute** through generated build contracts or typed adapters.
7. **Preserve** blockers, hashes, proof state, prior gains, rollback, and receipts.
8. **Advance** only when evidence shows the resulting boundary is stronger.
9. **Repeat** when the frontier moves.

### Generated contract library

| Surface | Role | Status |
|---|---|---|
| [`registry/tower.yml`](registry/tower.yml) | APEX technology source index | **Authored source state** |
| [`registry/advanced-claim-contracts.json`](registry/advanced-claim-contracts.json) | Claim boundaries and proof obligations | **Authored source state** |
| [`generated/build_commands.json`](generated/build_commands.json) | Toolchains, pins, build/test commands, execution tiers | Generated |
| [`generated/interfaces.json`](generated/interfaces.json) | Cross-language interface graph | Generated |
| [`generated/maturity.json`](generated/maturity.json) | Evidence state, proof class, exhibit locations | Generated |
| [`generated/megamind.technology-map.json`](generated/megamind.technology-map.json) | Agent/piston ownership and activation map | Active export |
| [`generated/spiral-engine.registry.json`](generated/spiral-engine.registry.json) | Spiral APEX frontier metadata | Generated |
| [`generated/smithery.registry.json`](generated/smithery.registry.json) | Smithery capability and publication contract | Declared, not published |
| [`.integrity/file_hashes.json`](.integrity/file_hashes.json) | Immutable base integrity ledger | Sealed base |
| [`.integrity/approved_delta.json`](.integrity/approved_delta.json) | Reviewed APEX evolution delta | Reviewed evolution |

## Portfolio mesh

The Tower owns technology placement and proof within its boundary. Connected repositories retain their own responsibilities and consume Tower exports through explicit interfaces.

| Repository | Relationship | Boundary |
|---|---|---|
| [`GlacierEQ/AKOS`](https://github.com/GlacierEQ/AKOS) | Authority/evidence and orchestration peer | Execution authority, evidence law, completion semantics, operating sequence. |
| [`GlacierEQ/aspen-grove-core`](https://github.com/GlacierEQ/aspen-grove-core) | Memory peer | Durable context, memory specialization, continuity. |
| [`GlacierEQ/apex-boot-core`](https://github.com/GlacierEQ/apex-boot-core) | Initialization peer | Identity and initialization contracts. |
| [`GlacierEQ/Pro_Code`](https://github.com/GlacierEQ/Pro_Code) | Engineering doctrine peer | Standards, doctrine, playbooks. |
| [`GlacierEQ/pro-code`](https://github.com/GlacierEQ/pro-code) | Engineering execution peer | Implements and verifies engineering changes. |
| [`GlacierEQ/job-app-helix`](https://github.com/GlacierEQ/job-app-helix) | Evidence/projection peer | Projects verified capabilities without redefining source intent. |
| [`GlacierEQ/apex-control-plane`](https://github.com/GlacierEQ/apex-control-plane) | Control-plane peer | Automation and execution surface. |
| [`GlacierEQ/apex-cli`](https://github.com/GlacierEQ/apex-cli) | Operator peer | Command surface for downstream workflows. |
| [`flagship/`](flagship/) | In-repository integration proof | Executes the strict polyglot mission contract. |

## APEX discipline that survives automation

- Generated surfaces are never hand-edited; `tower generate --check` rejects drift.
- Every claim carries evidence state, proof class, and a semantic claim contract.
- Blocked hardware, tools, dependencies, and services remain visible and machine-readable.
- Cross-language interfaces are explicit and versioned.
- Integrity distinguishes undeclared drift from reviewed evolution.
- Every replacement must account for prior unique capability.
- A passing proof is a checkpoint, not a reason to stop evolving.
- Merge state and generated projections are evidence of system state, not authority over project intent.

```text
edit APEX source fragment
    → update easy + advanced exhibits
    → compare against incumbent boundary
    → strengthen proof
    → tower validate
    → tower generate
    → pytest
    → tower build --all --allow-blocked
    → bind reviewed integrity delta
    → emit APEX receipt
    → review exact-head CI
    → pursue next frontier
```

## Truth boundary

The Tower is an **operational-alpha polyglot innovation engine**. It makes strong claims only where checked-in evidence supports them. Unproven records remain references or experiments. Missing hardware, services, toolchains, or evidence remain explicit blockers. The system is expected to become stronger continuously without laundering aspiration into proof or proof into authority over intent.

## License

MIT — see [`LICENSE`](LICENSE).
"""


def render_runtime_registry(registry: TowerRegistry) -> str:
    return '''#!/usr/bin/env python3
"""Operational facade for the APEX Tower technology registry.

The facade refuses to turn a technology name into an execution choice without an
evidence threshold, capability match, and deterministic selection receipt.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

from tower.registry import load_registry, validate_registry

_EVIDENCE_RANK = {
    "illustrative": 0,
    "toolchain_gated": 1,
    "service_gated": 1,
    "hardware_gated": 1,
    "compiles": 2,
    "tested": 3,
    "benchmark": 4,
    "formally_verified": 4,
    "integrated": 5,
    "production_reference": 6,
}


def _validated_registry(repo_root=None):
    if repo_root is not None:
        target = Path(repo_root) / "registry" / "tower.yml"
        registry = load_registry(target)
    else:
        registry = load_registry()
    errors = validate_registry(registry)
    if errors:
        raise RuntimeError("Invalid Tower APEX registry: " + "; ".join(errors))
    return registry


def _tokens(row: dict) -> set[str]:
    values = [row.get("id", ""), row.get("name", ""), row.get("category", "")]
    values.extend(row.get("interfaces", []))
    return {str(value).casefold() for value in values if value}


class BabelRegistryEngine:
    def __init__(self, repo_root=None):
        self.registry = _validated_registry(repo_root=repo_root)

    def get_spec(self, lang_key: str):
        row = self.registry.by_id(lang_key)
        if row is None:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {**row, "status": "VALIDATED_W4H_SPEC", "ok": True}

    def select(
        self,
        required_capabilities: Iterable[str],
        preferred_interfaces: Iterable[str] = (),
        *,
        minimum_evidence_state: str = "tested",
        available_hardware: Iterable[str] = (),
    ) -> dict:
        required = tuple(sorted({str(x).strip().casefold() for x in required_capabilities if str(x).strip()}))
        preferred = tuple(sorted({str(x).strip().casefold() for x in preferred_interfaces if str(x).strip()}))
        if minimum_evidence_state not in _EVIDENCE_RANK:
            raise ValueError(f"unknown evidence state: {minimum_evidence_state}")
        minimum_rank = _EVIDENCE_RANK[minimum_evidence_state]
        hardware = {str(x).strip().casefold() for x in available_hardware if str(x).strip()}
        candidates = []
        excluded = []
        for row in sorted(self.registry.technologies, key=lambda item: item["id"]):
            state = row["evidence_state"]
            rank = _EVIDENCE_RANK.get(state, -1)
            tokens = _tokens(row)
            missing = [cap for cap in required if not any(cap in token for token in tokens)]
            if missing:
                excluded.append({"id": row["id"], "reason": "missing_capabilities", "missing": missing})
                continue
            if rank < minimum_rank:
                excluded.append({"id": row["id"], "reason": "insufficient_evidence", "evidence_state": state})
                continue
            gate = str(row.get("execution", {}).get("hardware_gate", ""))
            if gate and state in {"hardware_gated", "toolchain_gated", "service_gated"} and not hardware:
                excluded.append({"id": row["id"], "reason": "runtime_gate_unmet", "gate": gate})
                continue
            interface_hits = sum(1 for item in preferred if any(item in token for token in tokens))
            score = (rank * 100) + (interface_hits * 10) - len(row["id"])
            candidates.append({
                "id": row["id"],
                "name": row["name"],
                "evidence_state": state,
                "score": score,
                "interface_hits": interface_hits,
                "reason": "capabilities_and_evidence_match",
            })
        candidates.sort(key=lambda item: (-item["score"], item["id"]))
        registry_sha256 = hashlib.sha256(self.registry.apex_bytes()).hexdigest()
        if not candidates:
            return {
                "ok": False,
                "status": "NO_VERIFIED_MATCH",
                "required_capabilities": list(required),
                "minimum_evidence_state": minimum_evidence_state,
                "registry_sha256": registry_sha256,
                "candidates": [],
                "excluded": excluded,
            }
        selected = candidates[0]
        return {
            "ok": True,
            "status": "SELECTED_VERIFIED_TECHNOLOGY",
            "selected": selected,
            "required_capabilities": list(required),
            "preferred_interfaces": list(preferred),
            "minimum_evidence_state": minimum_evidence_state,
            "registry_sha256": registry_sha256,
            "candidates": candidates,
            "excluded": excluded,
        }


_REGISTRY = _validated_registry()
BABEL_REGISTRY = {row["id"]: row for row in _REGISTRY.technologies}


if __name__ == "__main__":
    print(f"Tower of Babel APEX Registry Initialized: {len(_REGISTRY.technologies)} Technologies Registered.")
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
        "engineering_mode": "APEX",
        "status": "OPERATIONAL" if integrity["ok"] else "DEGRADED",
        "timestamp": time.time(),
        "integrity": integrity,
        "total_technologies": len(technologies),
        "total_exhibits": len(technologies) * 2,
        "evidence_states": sorted({row["evidence_state"] for row in technologies}),
        "version": "1.2.0",
    }


if __name__ == "__main__":
    print(json.dumps(get_telemetry(), indent=2, sort_keys=True))
'''


def build_surfaces(registry: TowerRegistry) -> dict[Path, bytes]:
    commands = {}
    interfaces: dict[str, list[str]] = {}
    maturity = {}
    megamind = {"tower_id": registry.payload["tower_id"], "engineering_mode": "APEX", "technologies": {}}
    for tech in registry.technologies:
        tech_id = tech["id"]
        commands[tech_id] = {"toolchain": tech["toolchain"], "execution": tech["execution"]}
        interfaces[tech_id] = list(tech["interfaces"])
        maturity[tech_id] = {
            "evidence_state": tech["evidence_state"],
            "evidence_tier": EVIDENCE_TIERS[tech["evidence_state"]],
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
        "version": "1.2.0",
        "engineering_mode": "APEX",
        "publication_status": "declared-not-published",
        "publication_rule": "Publication requires an MCP package plus an external registry receipt.",
        "capabilities": [f"technology:{row['id']}" for row in registry.technologies],
        "commands": ["validate", "build", "benchmark", "proof-report", "spec", "receipt", "megamind-map"],
        "source": "registry/tower.yml",
    }
    spiral = {
        "family": "tower-of-babel",
        "role": "apex-technology-frontier",
        "engineering_mode": "APEX",
        "activation_status": "declared",
        "activation_rule": "A capability becomes active only after evidence supports its declared boundary and it strengthens the APEX frontier.",
        "nodes": [row["id"] for row in registry.technologies],
        "edges": [
            {"from": tech_id, "to": interface, "type": "exposes_interface"}
            for tech_id, values in interfaces.items()
            for interface in values
        ],
    }
    links = ["# Tower APEX Link Library", ""]
    for tech in registry.technologies:
        links.append(f"## {tech['name']}")
        links.extend(f"- {uri}" for uri in tech["primary_evidence"])
        links.append("")

    from .visualize import build_topology_graph, render_dot_graph

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
        GENERATED_DIR / "tower_topology.json": _json_bytes(build_topology_graph(registry)),
        GENERATED_DIR / "tower_interface_graph.dot": render_dot_graph(registry).encode(),
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
    print("Tower APEX generated surfaces are current." if args.check else "Tower APEX generated surfaces written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
