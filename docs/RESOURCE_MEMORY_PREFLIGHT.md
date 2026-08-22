# Tower Resource + Memory Preflight

Tower-governed work begins by reconstructing what already exists before changing technology placement, proof state, interfaces, or architecture lanes.

## Boundary

Tower remains the technology-placement and capability-proof authority. It does **not** become the owner of operator memory.

Memory arrives as an external continuity input. Tower analyzes it, preserves status and source pointers, and refuses to convert recalled material into proof merely because it was remembered.

## Required sequence

```text
MISSION
  -> RESOURCE INVENTORY
    -> EXTERNAL MEMORY / CONTINUITY ANALYSIS
      -> LAST VERIFIED CHECKPOINT
        -> PRIOR LANE / CLAIM / EXHIBIT / PROOF STATE
          -> DUPLICATE COLLAPSE
            -> CURRENT DELTA
              -> BOUNDARY ANALYSIS
                -> TECHNOLOGY COMPARISON
                  -> EXPERIMENT / PROOF GATE
                    -> PROMOTE / RETAIN / HYBRIDIZE / RETIRE
```

This is continuation, not restart.

## Executable command

```bash
tower preflight \
  --mission "evaluate the strongest technology for this boundary" \
  --memory /path/to/external-memory.json \
  --require-memory \
  --output artifacts/resource-memory-preflight.json
```

Without `--require-memory`, Tower can still inventory local resources and explicitly records memory as unavailable or not supplied. With `--require-memory`, absence of analyzable memory returns exit code `2`.

## Memory snapshot contract

Tower accepts either a JSON list of findings or an object containing `findings` / `memory_findings`.

```json
{
  "findings": [
    {
      "finding": "The current Rust lane previously beat the Go candidate on tail latency.",
      "status": "VERIFIED_WITH_SOURCE",
      "source_pointer": "artifacts/benchmarks/latency-2026-08-18.json"
    },
    {
      "finding": "A CUDA path was discussed but never exercised on qualifying hardware.",
      "status": "RECALLED_NEEDS_SOURCE"
    }
  ]
}
```

Allowed memory states:

- `VERIFIED_WITH_SOURCE`
- `RECALLED_NEEDS_SOURCE`
- `DISPUTED`
- `INVALIDATED`

A memory finding without a source pointer cannot be promoted to proof.

## Resource analysis

The preflight inventories the current repository state, records SHA-256 identity, assigns resource roles, and groups identical bytes as duplicate content.

Important consequence:

```text
same underlying bytes in five locations != five corroborating sources
```

Duplicate copies remain one evidence lineage.

Resource roles include:

- `REGISTRY_SOURCE`
- `REGISTRY_CONTRACT`
- `EXECUTABLE_CORE`
- `PROOF_TEST`
- `FRONTIER_SOURCE`
- `GENERATED_PROJECTION`
- `EXECUTION_ARTIFACT`
- `INTEGRITY_CONTROL`
- `AUTOMATION_CONTROL`
- `DOCUMENTATION`
- `REPOSITORY_RESOURCE`

## Checkpoint and delta

The receipt records the current Git commit/tree when available and the working-tree delta. The governing equation is:

```text
CURRENT_DECISION = LAST_VERIFIED_STATE + NEW_VERIFIED_DELTA
```

Prior working capability is reused. A new language, runtime, proof system, or architecture pattern must beat or complement the incumbent at the actual boundary rather than winning because the prior state was forgotten.

## Promotion gates

The preflight receipt permanently states:

- memory cannot become proof without a source;
- duplicates do not become independent corroboration;
- prior verified state must be reused rather than silently restarted;
- material contradictions must be resolved or explicitly preserved;
- absence from a current search is not evidence that a prior implementation never existed.

## Receipt

Default output:

`artifacts/resource-memory-preflight.json`

Schema identity:

`glaciereq.tower.resource-memory-preflight.v1`

The receipt is an input to Tower decision-making. It does not replace the technology registry, build proof, benchmark result, integrity result, or final deterministic receipt.