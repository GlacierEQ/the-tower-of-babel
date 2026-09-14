# Supply Chain and Protection

The Tower's permanent automation uses immutable action pins, hash-locked dependencies, exact-head evidence, and provider-native readback. Repository protection must preserve both executable integrity and source-bearing lineage.

## Main ruleset authority

Install or update the ruleset using an administration-scoped token:

```bash
RULESET_ADMIN_TOKEN=... python scripts/apply_main_ruleset.py
python scripts/verify_main_ruleset.py
```

The `Main Ruleset Contract` workflow can perform the same operation after a repository secret named `RULESET_ADMIN_TOKEN` is configured with **Administration: write** permission. A scheduled strict verification reports future platform drift.

## Branch lineage authority

`Branch Lineage Audit` runs after a same-repository PR merges. It is intentionally read-only and performs provider readback of the merged PR head so the repository can preserve an explicit lineage receipt.

A merge establishes `MERGED_WITH` overlap. It does **not** establish whole-donor `UNIQUE_CONTRIBUTION=0`, and it never independently authorizes remote-ref deletion. The receipt distinguishes an extant donor at the merged SHA, a donor that moved after merge, and a provider-confirmed absent ref. Provider readback errors fail closed rather than being converted into a false absence claim.

A donor remains `ACTIVE_IN_MESH` while any unique source, event, edge, contradiction, provenance, mechanism, unresolved dependency, receipt, or authority-domain fact remains. Fully drained derivative donors require independent provider-read-back `UNIQUE_CONTRIBUTION=0` plus explicit Operator authorization and transition to `PRESERVE_DRAINED_LINEAGE` or an equivalent durable pointer state.

## Semantic claim authority

`registry/advanced-claim-contracts.json` owns the Advanced Exhibit Atlas claims. Every floor declares source assertions, expected failure cases, required receipt fields, and forbidden positive overclaims. The audit verifies those contracts against checked-in source while allowing explicit disclaimers and claim-boundary language.
