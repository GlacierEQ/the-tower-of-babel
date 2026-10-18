# Rust boundary fitness — Tower source assessment (2026-10-17)

**Owning architecture:** GlacierEQ/the-tower-of-babel `ARCHITECTURE_LAW.md` and `NERVOUS_SYSTEM.md`. This assessment does not supersede them, nominate an estate-wide default language, or create a new orchestration framework.

## Findings from current main and native tests

- Rust is already represented by `languages/rust/advanced_safety_governor.rs` (typed policy decisions), `flagship/rust/src/main.rs` (`tower-governor`, mission/registry/input hash and capability coverage), `registry/tower.d/systems.json` (portable behavioral proof), and declared Rust `tower spec/build/benchmark` lanes.
- The original Rust exhibit passed 5/5 native embedded tests on rustc 1.90.0 in the existing GlacierEQ Sprite.
- An adversarial test then reproduced a real **lexical-only path boundary**: an allowlisted evidence path could contain a symlink pointing outside the allowed root. The test failed with the original code, rather than being declared resolved from inspection.
- The repaired exhibit performs an additional **best-effort existing symlink resolution preflight** beneath the deepest matching declared root, rejecting escapes and dangling links while preserving symlinks pointing inside that root. Native `rustc --edition=2021 --deny warnings --test` and all 8 embedded tests passed.
- This does **NOT** establish secure filesystem-level authorization. Preflight checks remain subject to filesystem mutation/TOCTOU. A production file-effect owner must use a correctly scoped `openat2`, directory handle or equivalent descriptor/capability API, authorize the real effect, and independently read back provider state. `approved_mutation` and `approved_elevated_action` in this example are caller-supplied booleans; they are **not signed or authenticated approvals**. Do not promote the exhibit to `production_reference` on this patch.

## Placement decision

| Boundary | Rust value | Ownership decision |
|---|---|---|
| Deterministic policy/state machines, typed evidence & receipt validators | High; rich enums, explicit errors, no GC, safe concurrency by construction | **Prototype/expand Rust alongside existing owners and interfaces** |
| Durable mission persistence | Rust useful as execution client, but PostgreSQL/SQL owns transactions | **Retain database ownership** |
| High-concurrency worker scheduling | Rust is credible; benchmark real mission workloads against current Go/Python/TypeScript executor with identical request/schema and failure semantics | **Experiment, do not blindly replace** |
| AI orchestration and model experimentation | Python currently has major ecosystem leverage | **Keep Python unless measured boundary benefit beats migration and interface costs** |
| Web/MCP UI & provider reach | TypeScript and the existing MCP connector ecosystem remain fit | **Keep where strongest, pass versioned contract to Rust** |
| Formal invariants and proofs | Lean/TLA+/Coq can complement Rust; Rust typing is not a formal proof of business correctness | **Keep specialist proof lane** |

The existing `generated/benchmarks.json` compares different C, Python, and Rust exhibit workloads. Its raw runtimes are **not an apples-to-apples Rust-vs-Go-vs-Python speed ranking**. A genuine replacement decision needs source-equivalent workload, warmup and tail latency, peak RSS, failure recovery, cancellation, dependency-locked build, and interface cost.

## Next proof frontier

Run the actual flagship Rust governor `cargo test` and cross-language mission pipeline under a complete toolchain, generate provider-owned receipts, and compare a reversible real high-assurance worker or evidence-validator boundary against its incumbent. Preserve all existing unique capabilities; promote only source-bound gains and keep cold-ChatGPT auto-activation as a separate unverified outcome.
