# Tower Agent Doctrine

## Authority

The registry rooted at `registry/tower.yml` is the technology-evidence authority for:

- technology admission;
- W4H+How placement;
- easy and advanced exhibit paths;
- evidence state and proof class;
- toolchain and build commands;
- hardware and service blockers;
- cross-language interfaces;
- Megamind agent and piston ownership.

Do not add a language, format, compiler, HDL, proof system, or runtime by editing
the README, sidecar, generated files, or Megamind maps directly.

## Mandatory resource + memory preflight

Before changing technology placement, proof state, exhibits, interfaces, architecture lanes, or admission status:

1. recover the relevant external memory / continuity context when available;
2. inventory current Tower resources and prior work;
3. identify the last verified checkpoint;
4. collapse duplicates so repeated copies are not counted as corroboration;
5. identify prior accepted, disputed, superseded, and invalidated conclusions;
6. compute the new delta rather than restarting the analysis;
7. preserve material contradictions and source gaps;
8. only then change the registry or implementation.

Run:

```bash
tower preflight --mission "<exact engineering objective>" --memory <external-memory.json> --require-memory
```

The preflight receipt is written to `artifacts/resource-memory-preflight.json` by default.

Tower analyzes memory but does not own operator memory. Memory is continuity input, not proof. A remembered fact must retain or recover a source pointer before promotion to evidence.

## Required workflow

1. Run the resource + memory preflight and inspect its checkpoint, duplicate groups, gaps, and delta.
2. Reuse or extend the strongest prior verified lane instead of restarting it.
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

## Language-diversification rule

New technology is admitted only when its What, Where, When, Why, How,
interoperability boundary, owner, and proof gate are explicit. Existing working
components are preserved; no refactor is permitted merely to introduce another
language.

## Generated files

Generated surfaces must not be hand-edited. They are overwritten by
`python3 -m tower.generate`.
