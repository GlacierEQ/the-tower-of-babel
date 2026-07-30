# Tower of Babel Quality Contract

This repository is a portfolio system, not a file-extension collection. Every exhibit must be truthful about what it proves.

## Two exhibit levels

### Easy

An easy exhibit teaches one language-specific concept with minimal ceremony. It must:

- parse or compile with the documented toolchain;
- be deterministic and safe for its demonstrated input;
- contain enough context to run or inspect independently;
- avoid claiming production readiness.

### Advanced

An advanced exhibit demonstrates a credible production boundary. It must include:

1. **W4H rationale** — what, where, when, why, and how.
2. **Typed or explicit inputs and outputs.**
3. **Validation and failure behavior** for malformed, missing, or unsafe input.
4. **A meaningful invariant or policy boundary.**
5. **Observability** through metrics, receipts, diagnostics, or a structured report.
6. **A runnable demonstration or test vector.**
7. **No placeholders** such as empty bodies, unconditional success, `pass`, or identity stubs.
8. **Bounded resource behavior** where concurrency, memory, network, or untrusted input is involved.

An advanced exhibit does not need to be a complete product. It must, however, be honest evidence of the language capability named in the README.

## Validation tiers

- **native-ci** — validated on every GitHub Actions run with a compiler, interpreter, or repository test.
- **optional-ci** — validated when a commonly available optional toolchain is present.
- **specialized-toolchain** — structure and contract are validated in baseline CI; full compilation requires specialized hardware or language tooling.

## Repository invariants

The canonical registry at `src/babel_registry.py` is the source of truth. CI fails when:

- the registry does not contain exactly 21 languages;
- a language directory is missing or unexpected;
- an easy or advanced exhibit is missing, empty, duplicated, or has the wrong extension;
- the programmatic registry contract stops returning machine-readable results;
- the Python registry, sidecar, or tests fail to execute.

Compiler coverage is reported separately from structural coverage. A file is never described as compiler-validated unless the corresponding toolchain actually ran successfully.

## Promotion rule

A placeholder or concept sketch may remain in the repository only while it is clearly labeled as such. It must not be called an advanced production exhibit until it satisfies this contract.
