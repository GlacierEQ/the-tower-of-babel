# Tower Agent Doctrine — APEX

## Authority model

Casey Barton's intended GlacierEQ architecture is the sole human authority over project direction. The Tower does not acquire project authority. Its job is narrower and harder: **select and prove the strongest technology for each engineering boundary**.

`registry/tower.yml` is the APEX technology source registry for:

- technology observation and admission;
- W4H+How placement;
- easy and advanced exhibit paths;
- evidence state and proof class;
- toolchain and build commands;
- hardware and service blockers;
- cross-language interfaces;
- Megamind agent and piston ownership.

The registry records Tower state. It does not redefine Casey's intended system into a smaller projection.

Do not add a language, format, compiler, HDL, proof system, runtime, database, or accelerator by editing generated surfaces directly.

## APEX objective

The Tower optimizes **boundary fitness and whole-system coherent power**, not language count, minimum scope, or architectural uniformity.

For every real boundary:

1. identify what the boundary must accomplish;
2. identify the strongest credible current technologies for it;
3. compose candidates when one technology cannot dominate the whole boundary;
4. build the strongest justified reversible experiment;
5. measure function, performance, reliability, interface cost, resource behavior, observability, and failure isolation;
6. preserve every unique prior gain;
7. select the non-dominated winner or preserve multiple frontier candidates when the tradeoff is real;
8. repeat as the frontier changes.

A six-language repository is correct when six languages each own a boundary they are unusually good at. A one-language repository is correct when one language actually dominates all its boundaries. Uniformity itself has zero score.

## Required workflow

1. Start from Casey's APEX intent and the actual system bottleneck.
2. Inspect the APEX technology registry and fresh frontier sources.
3. Change the registry index or a declared fragment when the technology map changes.
4. Add or update exhibits that demonstrate the real boundary.
5. Add or update proof appropriate to the claim.
6. Run `tower validate`.
7. Run `tower generate`.
8. Run repository tests and the relevant native/toolchain/hardware path.
9. Compare against the incumbent boundary, not against an empty baseline.
10. Generate and verify integrity and deterministic receipts.
11. Preserve the winner, rollback path, prior unique gains, and next frontier cursor.

## Truth classes

A file name containing `advanced` does not establish production maturity. Use the declared evidence state:

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

Evidence limits claims. It does not prohibit an ambitious reversible experiment.

## Language-diversification law

New technology is admitted when its What, Where, When, Why, How, interoperability boundary, owner, and proof are explicit **and it strengthens the APEX architecture vector for that boundary**.

Do not refactor merely to add another language. Do not refuse a better language merely to reduce language count. Existing working components are preserved until the replacement proves it retains or exceeds their unique value.

## Generated files

Generated surfaces must not be hand-edited. They are overwritten by `python3 -m tower.generate`.

Historical files and receipts may contain the retired term `canonical`. That term is historical metadata only and has no governing force over APEX intent or current engineering direction.

## Working-directory supplement

For agents operating in this project, see `@/root/.agents/skills/tower-of-babel/SKILL.md`
for the operator-routing skill (project layout, CLI cheat sheet, evidence/proof
quick reference, sharp edges). That skill defers to this file on doctrine.

## Continuous-orientation invariant

The orientation engine emits routing telemetry, not authorization. Its machine result must preserve:

- `execution_permission: NOT_EVALUATED_BY_ORIENTATION`;
- `stop_condition_created: false`;
- a certainty level that can fall without reducing execution effort by itself;
- explicit route hints for resource recovery, continuity sourcing, contested-memory reconciliation, current-state acquisition, checkpoint establishment, committed-delta verification, and working-tree reconciliation;
- `CONTINUE` or `CONTINUE_WITH_GAPS` as the continuation state.

A gap is work to route, not a reason to manufacture a global stop. Disputed, invalidated, or superseded memory never becomes current positive continuity merely because parsing succeeded. Local orientation I/O failure is surfaced as degraded JSON telemetry, and output protection must reject same-path, symlink-resolved, or hard-linked attempts to overwrite operator memory.

## External-effect risk law

External effect is a location/boundary fact, not automatically a reason to stop.

Classify consequential action by reversibility:

- `reversible`: execute within the current Operator-directed mission when the technical execution boundary is satisfied; no redundant exact-scope receipt is required;
- `materially-irreversible`: require exact Operator-scoped authorization before crossing the effect boundary;
- `unclassified`: preserve the conservative legacy authorization requirement until the effect is classified.

Legacy `--external-effects` without `--effect-risk` remains `unclassified`, so existing callers do not silently become less protected.

Operator scope never bypasses toolchain, interface, execution, evidence, or proof requirements. Those requirements control what the system can truthfully do or claim; they do not acquire project-direction authority.
