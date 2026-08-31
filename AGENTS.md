# Tower Agent Doctrine

## Operator authority and Tower evidence scope

The Operator has absolute project-direction authority. The Tower does not acquire
project authority from a registry, receipt, promotion state, generated surface,
test result, model judgment, or automation layer.

The registry rooted at `registry/tower.yml` is the Tower's technical
technology-evidence source for:

- technology admission recommendations;
- W4H+How placement analysis;
- easy and advanced exhibit paths;
- evidence state and proof class;
- toolchain and build commands;
- hardware and service blockers;
- cross-language interfaces;
- Megamind agent and piston ownership metadata.

Tower may challenge a factual or technical claim with evidence. It may not
silently replace the Operator's objective, reduce scope, require canonical
positioning before material work, or convert a recommendation into a veto.

Do not add a language, format, compiler, HDL, proof system, or runtime by editing
the README, sidecar, generated files, or Megamind maps directly.

## Resource + memory orientation

Use resource and memory reconstruction to orient consequential work, improve routing, and preserve continuity. It is not permission machinery and does not hold the mission at a stop sign.

1. recover the relevant external memory / continuity context when available;
2. inventory current Tower resources and prior work;
3. identify the last verified checkpoint when one exists;
4. collapse duplicates so repeated copies are not counted as corroboration;
5. identify prior accepted, disputed, superseded, and invalidated conclusions;
6. compute the new delta rather than restarting the analysis;
7. preserve material contradictions and source gaps;
8. select and execute the strongest truthful next route.

Missing memory, a partial reconstruction, an absent checkpoint, or an unresolved source gap changes certainty and route selection. None of those facts becomes a generic execution veto.

Run:

```bash
tower orient --mission "<exact engineering objective>" --memory external-memory.json
```

The primary orientation receipt is written to `artifacts/resource-memory-orientation.json` by default. `tower preflight` remains a compatibility alias for older callers and retains nonblocking semantics.

Tower analyzes memory but does not own operator memory. Memory is continuity input, not proof. A remembered fact must retain or recover a source pointer before promotion to evidence.

## Required workflow

1. Orient from resource + memory state and inspect its certainty, checkpoint, duplicate groups, gaps, delta, and recommended next route without treating the report as permission to act.
2. Reuse or extend the strongest prior verified lane when available instead of restarting it; if unavailable, continue from the strongest observed state with exact uncertainty.
3. Change the registry index or one of its declared fragments.
4. Add or update both exhibits.
5. Add or update the proof gate.
6. Run `tower validate`.
7. Run `tower generate`.
8. Run `pytest`.
9. Run `tower build --all --allow-blocked`.
10. Generate and verify integrity.
11. Generate the deterministic receipt.
12. Review generated drift before commit.

A missing Tower receipt, incomplete memory, absent checkpoint, failed search, or
unresolved contradiction does not by itself stop the mission. Continue through the
strongest meaningful truthful route and record uncertainty, blockers, and conflicts
as telemetry for the next action.

## Truth classes

A file name containing `advanced` does not establish production maturity.
Use the declared evidence state:

- illustrative
- compiles
- tested
- benchmark
- hardware_gated
- toolchain_gated
- service_gated
- formally_verified
- integrated
- production_reference

Never promote a floor without corresponding evidence.

## Continuity and duplication rules

- `LAST_VERIFIED_STATE + NEW_VERIFIED_DELTA` is the default evolution model.
- A failed search does not prove prior work never existed.
- Repeated repository copies of the same bytes remain one evidentiary lineage.
- A generated summary, README statement, or recalled memory cannot promote itself into executable proof.
- Older derivative summaries do not override newer source-backed state.
- A counterexample or contradiction is preserved until resolved; it is not deleted to make a technology look stronger.
- Proof or projection demotion does not authorize implementation deletion.
- Existing unique capability may retire only through proven equivalence/superset replacement or explicit Operator direction.

## Language-diversification rule

New technology is admitted only when its What, Where, When, Why, How,
interoperability boundary, owner, and proof gate are explicit. Existing working
components are preserved; no refactor is permitted merely to introduce another
language.

## Generated files

Generated surfaces must not be hand-edited. They are overwritten by
`python3 -m tower.generate`.


## Continuous-orientation invariant

The orientation engine emits routing telemetry, not authorization. Its machine result must preserve:

- `execution_permission: NOT_EVALUATED_BY_ORIENTATION`;
- `stop_condition_created: false`;
- a certainty level that can fall without reducing execution effort by itself;
- explicit route hints for resource recovery, continuity sourcing, contested-memory reconciliation, current-state acquisition, checkpoint establishment, committed-delta verification, and working-tree reconciliation;
- `CONTINUE` or `CONTINUE_WITH_GAPS` as the continuation state.

A gap is work to route, not a reason to manufacture a global stop. Disputed, invalidated, or superseded memory never becomes current positive continuity merely because parsing succeeded. Local orientation I/O failure is surfaced as degraded JSON telemetry, and output protection must reject same-path, symlink-resolved, or hard-linked attempts to overwrite operator memory.
