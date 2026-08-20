# Tower of Babel Thread Charter

## Mission

`the-tower-of-babel` maintains a technology registry that makes multi-language capability surfaces inspectable: each floor carries its own evidence state, proof class, toolchain reference, and build constraints rather than being reduced to a generic language list.

## Runnable Context Integrity Proof Surface

Run the focused local contract with:

```bash
PYTHONPATH=src:. pytest -q tests/test_tower_of_babel.py tests/test_context_integrity_proof.py
PYTHONPATH=src:. python3 scripts/run_context_integrity_proof.py --output artifacts/tower_context_integrity_proof.json
```

The proof loads the registry, invokes `validate_registry()` for semantic validation, checks generated-file integrity in a temporary manifest, constructs a topology graph, and emits a deterministic receipt. A failed validation or internal proof step is serialized as a structured failure and exits nonzero. It does not invoke a technology-specific toolchain.

## Published Capability Surfaces

| Surface | Promise |
|---|---|
| `tower.registry.load_registry()` | Loads the complete 40-technology source registry and enforces source-file containment, fragment linkage, record-object shape, and duplicate identifiers. Consumers requiring semantic floor validation must also call `validate_registry()`. |
| `tower.integrity.write_manifest()` / `verify_integrity()` | Produces and verifies a local content-integrity manifest for registry-governed files. |
| `tower.visualize.build_topology_graph()` | Builds a queryable technology topology from the registry without changing a floor’s source or execution authority. |
| `tower.build.build_floor()` | Reports missing toolchains and hardware gates as explicit blocked statuses rather than presenting unavailable work as success. |

## Truth Boundary

This thread proves local registry and integrity behavior. It does **not** prove that every technology builds, benchmarks well, has hardware available, is secure, or is authorized to execute.

## Next Capability

Publish a query-only Context Integrity topology snapshot for other threads, preserving each technology floor’s own proof class and execution gates.
