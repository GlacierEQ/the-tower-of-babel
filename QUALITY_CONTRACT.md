# Tower of Babel APEX Quality Contract

The Tower is a polyglot innovation system. Its quality target is not static conformance. Its quality target is **the strongest truthful, functional, evolvable technology composition for each boundary and for the system as a whole**.

## APEX source state

`registry/tower.yml` and its contained `registry/tower.d/*.json` fragments are the authored Tower technology source state. Generated maturity, interface, build, Smithery, Spiral, and Megamind surfaces derive from that source state.

The source state records what the Tower currently knows and proves. It does not outrank Casey Barton's intended architecture and it may not shrink that intent. When current implementation lags the APEX target, the gap becomes development work rather than justification for lowering the target.

## Exhibit levels

### Easy

An easy exhibit teaches one technology-specific concept with minimal ceremony. It must:

- parse, compile, or execute with its documented toolchain when available;
- be deterministic and safe for the demonstrated input;
- contain enough context to run or inspect independently;
- avoid claiming operational maturity it has not earned.

### Advanced

An advanced exhibit demonstrates a credible engineering boundary. It must include:

1. **W4H+How rationale** — what, where, when, why, and how.
2. **Typed or explicit inputs and outputs.**
3. **Validation and failure behavior** for malformed, missing, or unsafe input.
4. **A meaningful invariant or policy boundary.**
5. **Observability** through metrics, receipts, diagnostics, or a structured report.
6. **A runnable demonstration, proof, benchmark, or test vector.**
7. **No placeholders** such as empty bodies, unconditional success, `pass`, or identity stubs.
8. **Bounded resource behavior** where concurrency, memory, network, hardware, or untrusted input is involved.
9. **Boundary comparison** against the strongest incumbent when the exhibit proposes replacement or migration.
10. **Preservation accounting** proving which prior capabilities are retained, exceeded, composed, or deliberately retired.

An advanced exhibit need not be a complete product. It must be honest evidence of a real capability and a useful step toward the APEX target.

## APEX comparison rule

Smallness, uniformity, fewer dependencies, fewer languages, or fewer components are not quality dimensions by themselves.

A candidate should be preferred when it moves the system onto a stronger non-dominated frontier across relevant dimensions such as:

- capability;
- intelligence;
- reliability;
- leverage;
- composability;
- reach;
- frontier fitness;
- latency/throughput/resource efficiency where relevant;
- failure isolation and recovery.

Tradeoffs must remain visible. Policy may not manufacture a winner by deleting dimensions that favor a more capable architecture.

## Evidence and blockers

- `tested`, `compiles`, `benchmark`, `formally_verified`, and stronger states require corresponding execution evidence.
- Missing toolchains, services, dependencies, or hardware produce exact blockers, never false success.
- Structural presence is not compiler proof, and compiler proof is not operational proof.
- Evidence constrains claims, not reversible experimentation.
- A failed ambitious experiment is useful evidence when its failure mode is preserved and fed back into the next design.

## Repository invariants

CI fails when:

- the Tower source registry is invalid or its fragments escape their declared boundary;
- generated surfaces drift from authored Tower state;
- an easy or advanced exhibit is missing or malformed;
- native portable checks fail;
- a declared proof state conflicts with execution evidence;
- the integrity ledger cannot explain the governed tree;
- a replacement claims success while dropping an unaccounted prior capability.

CI must not fail merely because a justified experiment expands language count or architecture breadth.

## APEX activation rule

A capability becomes active when the evidence appropriate to its declared boundary succeeds, integration preserves required prior gains, and the resulting system is stronger on the relevant APEX frontier.

Branch completion alone proves nothing. Exact-head verification and integration proof are required. Merge state is evidence of repository history, not authority over project intent.

Historical files may contain the retired term `canonical`. Treat it as historical metadata only, never as a governing engineering concept.
