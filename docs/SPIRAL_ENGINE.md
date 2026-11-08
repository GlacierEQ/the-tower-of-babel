# Spiral Engine — APEX Frontier Expansion

The Spiral Engine exists to make the Tower move, not to certify stagnation. It turns evidence, system pressure, and frontier technology into increasingly capable architectures while preserving truth and prior gains.

## What it does

The engine currently performs inspectable question-generation and admission operations. Under APEX those operations are interpreted as **frontier-expansion machinery**:

1. **Civilization question generation** — emits one `en-US` synthesis question spanning every declared civilization domain. A supplied seed makes the question replayable; omitting the seed creates a fresh seed and returns it with the question.
2. **Capability evaluation** — evaluates whole-system domain coverage, evidence, risk controls, observability, ownership, human override, and rollback readiness. The result is a deterministic receipt.
3. **APEX comparison** — admission is not the end state. A candidate must be compared against the incumbent and against other credible frontier candidates on capability, intelligence, reliability, leverage, composability, reach, frontier fitness, resource behavior, failure isolation, and preservation of unique prior gains.
4. **Next-turn generation** — every accepted or rejected candidate produces the next pressure/opportunity cursor. The engine must never treat a passing receipt as a reason to stop evolving.

It performs no network calls and requires no model for deterministic evaluation. Models, research agents, and frontier observers may propose candidates, but evidence remains ordinary inspectable data.

## Domains

The initial civilization taxonomy is:

`science`, `technology`, `health`, `environment`, `economics`, `law`, `governance`, `history`, `culture`, `art`, `education`, `ethics`, `infrastructure`, `security`, `information`, `psychology`, `demographics`, and `geopolitics`.

Civilization-scoped capabilities must account for every declared domain. Unknown or missing domains produce exact blockers rather than being silently ignored.

## Commands

```bash
tower spiral question --seed civilization
tower spiral question --output artifacts/civilization-question.json

tower spiral admit examples/spiral/civilization_capability.json \
  --output artifacts/spiral-admission-receipt.json

tower spiral verify artifacts/spiral-admission-receipt.json
```

`tower spiral admit` exits `0` for `ADMIT`, `2` for a declared rejection, and `1` for invalid input or execution failure.

## Evaluation contract

A civilization-scale candidate provides:

- `capability_id`
- a substantive `summary`
- `scope: civilization`
- `risk_level`
- all declared `affected_domains`
- at least three independently identified evidence records with SHA-256 digests
- controls for ownership, approval, human override, audit logging, rollback, and metrics

The current deterministic score remains deliberately reviewable:

| Dimension | Weight |
|---|---:|
| Domain coverage | 40% |
| Evidence | 30% |
| Controls | 30% |

This score is a **proof threshold**, not the APEX objective function. Passing it means a candidate has enough declared support to proceed. It does not mean the candidate is the strongest architecture.

## APEX selection after proof

Once a candidate passes its proof threshold, compare it against the incumbent and other viable candidates. Prefer the non-dominated design frontier. Do not select the smallest candidate merely because it is easier to describe or integrate.

A candidate that increases architecture breadth is valid when the added components create greater coherent power than their coordination cost. A candidate that simplifies architecture is valid when the simplification genuinely preserves or increases capability rather than merely deleting difficult boundaries.

## Receipt properties

Each receipt includes:

- engine and schema versions;
- candidate SHA-256;
- exact decision, score, controls, evidence count, coverage, and blockers;
- a stable receipt ID;
- a receipt SHA-256 over deterministic JSON.

The receipt intentionally excludes wall-clock time so identical inputs produce identical receipts. External systems may timestamp, sign, attest, or append the receipt without changing the deterministic decision.

A receipt proves an evaluation happened. It does not acquire authority over Casey Barton's intended system.

## APEX status

The Spiral Engine remains an evolving runtime component. Generated Tower state is evidence of the implemented frontier. When that state falls short of the APEX target, the correct response is to develop forward, compose stronger technology, and prove the next turn.

Historical material may contain the retired term `canonical`. It is provenance only and has no controlling engineering meaning under APEX.
