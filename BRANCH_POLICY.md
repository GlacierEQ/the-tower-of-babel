# Branch Policy — `main` Is the Worker, the Mesh Preserves Lineage

`main` is the living integration branch and the routing cursor for where new Tower work normally compounds. It is not global replacement authority over older source-bearing branches.

## Operating rules

1. **Completed implementation belongs on `main`.** A function is not integrated while it exists only on a side branch.
2. **Branches are source-bearing mesh nodes, not disposable workspaces.** Start new implementation from current `main` when appropriate, but a merge establishes overlap only; it does not prove donor exhaustion.
3. **Preserve non-superseded unique contribution before retirement.** A donor remains `ACTIVE_IN_MESH` while it contains any non-superseded unique source, event, edge, contradiction, mechanism, unresolved dependency, or authority-domain fact. Provenance and lineage receipts are preserved as durable pointers; once they merely describe already-transcribed state they are not themselves unique contribution that blocks retirement.
4. **Partial overlap is explicit.** Record relationships such as `MERGED_WITH`, `SUPERSEDES_ONLY`, `CONTRADICTS`, `DUPLICATE_OF`, or `DERIVED_FROM` rather than flattening one branch into another.
5. **Retirement requires proof, not an invented approval gate.** Only provider-read-back `UNIQUE_CONTRIBUTION=0` can establish that a derivative donor is fully drained. Do not substitute merged/closed state, age, patch equivalence, current-main containment, CI success, replay, synthesis, or a generic approval ritual for that proof. Where the Operator has given a controlling instruction for the work, routine forward repair proceeds under that instruction rather than introducing a new per-retirement approval requirement.
6. **Retirement preserves lineage.** A fully drained donor transitions to `PRESERVE_DRAINED_LINEAGE` or an equivalent durable pointer state; remote-ref deletion is not the normal terminal action.
7. **Exact-head evidence remains mandatory for mutation claims.** Registry validation, generated-surface checks, tests, integrity verification, and relevant build gates must apply to the precise commit being acted on.
8. **`main` must remain usable.** Broken or incomplete integration is repaired immediately or reverted; it is never hidden indefinitely behind another branch.

## Lifecycle

```text
current main routing cursor
    → source-bearing work branch
    → exact-head verification
    → merge/transcribe/compound into main
    → provider readback
    → MERGED_WITH / DERIVED_FROM / other explicit relationship
    → ACTIVE_IN_MESH while non-superseded unique contribution remains
    → provider-read-back UNIQUE_CONTRIBUTION=0
    → PRESERVE_DRAINED_LINEAGE
```

`latest`, merged/closed PR state, patch equivalence, age, stale-dependency status, CI success, current-main containment, successful replay, or successful synthesis are evidence about overlap or execution state only. They do not independently or jointly authorize remote-ref deletion.
