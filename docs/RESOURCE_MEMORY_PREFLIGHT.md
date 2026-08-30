# Tower Resource + Memory Orientation

Tower uses resource and memory reconstruction to orient technology placement, proof state, interfaces, and architecture work. Reconstruction improves continuity, certainty, and route selection; it is not permission machinery.

## Boundary

Tower remains the technology-placement and capability-proof authority. It does **not** become the owner of operator memory.

Memory arrives as an external continuity input. Tower analyzes it, preserves status and source pointers, and refuses to convert recalled material into proof merely because it was remembered.

## Required sequence

```text
MISSION
  -> RESOLVE ACTIVE TOWER CHECKOUT
    -> RESOURCE INVENTORY
      -> EXTERNAL MEMORY / CONTINUITY ANALYSIS
        -> PROOF-BOUND LAST VERIFIED CHECKPOINT
          -> PRIOR LANE / CLAIM / EXHIBIT / PROOF STATE
            -> DUPLICATE COLLAPSE
              -> COMMITTED + WORKING DELTA
                -> BOUNDARY ANALYSIS
                  -> TECHNOLOGY COMPARISON
                    -> EXPERIMENT / PROOF CHECK
                      -> PROMOTE / RETAIN / HYBRIDIZE / RETIRE
```

This is continuation, not restart.

## Executable command

```bash
tower preflight \
  --mission "evaluate the strongest technology for this boundary" \
  --memory /path/to/external-memory.json \
  --checkpoint-receipt artifacts/tower_receipt.json \
  --output artifacts/resource-memory-preflight.json
```

`--checkpoint-receipt` is optional because Tower automatically checks `artifacts/tower_receipt.json`. A checkpoint is accepted only when the v2 Tower release receipt has valid registry, integrity, and build states, a valid deterministic body hash, and a commit/tree pair available in the checkout.

`--require-memory` remains accepted only for compatibility. It does not grant or deny execution permission and does not convert missing, invalid, empty, or malformed continuity memory into a global stop condition. Those states remain explicit telemetry that lowers certainty and changes routing.

Preflight intentionally executes before registry loading. A damaged or missing `registry/tower.yml` therefore becomes a resource gap inside the receipt instead of preventing recovery analysis.

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
    },
    {
      "finding": "The former placement was replaced by a stronger verified lane.",
      "status": "SUPERSEDED",
      "source_pointer": "history/placement-change.json"
    }
  ]
}
```

Allowed memory states:

- `VERIFIED_WITH_SOURCE`
- `RECALLED_NEEDS_SOURCE`
- `DISPUTED`
- `INVALIDATED`
- `SUPERSEDED`

A caller cannot manufacture proof by writing `VERIFIED_WITH_SOURCE`: without a non-empty `source_pointer`, Tower downgrades the finding to `RECALLED_NEEDS_SOURCE` and records a gap. `SUPERSEDED` is preserved rather than resurrected as current evidence.

Tower rejects a supplied snapshot that contains entries but no analyzable findings. An explicitly empty findings list is reported as `NO_PRIOR_STATE_FOUND`, not as successful memory recovery.

The preflight output may never overwrite its memory input.

## Resource analysis

The preflight resolves the active checkout from the current working directory before considering the Python package location. This keeps an installed `tower` CLI from accidentally inventorying `site-packages`.

The preflight inventories repository state, records SHA-256 identity, assigns resource roles, and groups identical bytes as duplicate content.

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

The selected preflight output path is excluded from inventory so repeated preflight runs over unchanged inputs do not hash their own previous receipt.

## Checkpoint and delta

Tower does **not** label the current Git HEAD as the last verified checkpoint merely because it exists.

`last_verified_checkpoint` is populated only from a valid Tower v2 release receipt. If no valid receipt is available, the field is `null`, `checkpoint_gaps` explains why, and continuation controls report `has_verified_checkpoint: false` without converting that absence into an execution veto.

The current commit/tree is recorded separately as:

`CURRENT_COMMITTED_BASE_NOT_AUTOMATICALLY_VERIFIED`

When a proof-bound checkpoint exists, Tower computes committed file changes from that checkpoint commit through current HEAD, then separately records working-tree changes. Without a proof-bound checkpoint, committed-delta status is explicitly `UNKNOWN_NO_VERIFIED_CHECKPOINT` rather than silently treating newer commits as previously verified.

The governing equation remains:

```text
CURRENT_DECISION = LAST_VERIFIED_STATE + NEW_VERIFIED_DELTA
```

Prior working capability is reused. A new language, runtime, proof system, or architecture pattern must beat or complement the incumbent at the actual boundary rather than winning because the prior state was forgotten.

## Continuation controls

The orientation receipt permanently states:

- orientation is not execution permission;
- the default is to continue while a meaningful truthful route exists;
- memory cannot become proof without a source;
- duplicates do not become independent corroboration;
- prior verified state is reused when available rather than silently restarting;
- absence of a verified checkpoint is explicit uncertainty, not a mission veto;
- material contradictions are resolved or explicitly preserved;
- absence from a current search is not evidence that a prior implementation never existed;
- operator memory is read-only input to this process.

## Receipt

Default output:

`artifacts/resource-memory-preflight.json`

Schema identity:

`glaciereq.tower.resource-memory-preflight.v3`

Version 3 intentionally changes the top-level control shape from the former
`promotion_gate` object to `continuation_controls`, so consumers can distinguish
nonblocking orientation semantics without mistaking the payload for the older v2 contract.

The receipt is orientation input to Tower decision-making. It does not replace the technology registry, build proof, benchmark result, integrity result, or final deterministic release receipt, and it never becomes a permission gate over execution.