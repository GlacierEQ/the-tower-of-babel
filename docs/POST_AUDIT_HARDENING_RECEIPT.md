# Post-Audit Hardening Receipt

This tranche records repository-controlled hardening and preserves the external platform dependency that cannot be truthfully completed without repository-administration credentials. Historical deletion-era branch semantics are superseded only for their destructive disposition; their provenance remains part of repository history.

## Implemented

- immutable commit pins for every action in permanent Tower, Quality, Spiral, Advanced, Nervous System, Branch Lineage, and ruleset workflows;
- hash-locked Python 3.12 CI environment with exact wheel SHA-256 digests;
- registry-owned semantic claim contracts for all 30 advanced exhibits;
- source-pattern, failure-case, receipt-field, and forbidden-overclaim auditing;
- OIDC-bound Sigstore/SLSA attestations for Tower build, benchmark, proof, and release receipts on `main`;
- stable required status contexts suitable for a GitHub main-branch ruleset;
- exact-head, same-repository PR **read-only branch-lineage readback** with a retained `MERGED_WITH` receipt; merged status does not establish `UNIQUE_CONTRIBUTION=0` or deletion authority;
- provider-readback uncertainty fails closed rather than being recorded as branch absence;
- fully drained derivative donors preserve lineage as `PRESERVE_DRAINED_LINEAGE` after provider-read-back zero-unique-contribution proof and explicit Operator authorization;
- policy-as-code, installer, verifier, tests, and scheduled drift detection for the required `main` ruleset;
- Dependabot review lanes for GitHub Actions and Python dependency updates.

## External activation boundary

GitHub currently reports no active repository ruleset through the public rulesets endpoint. Applying the checked-in policy requires a repository secret named `RULESET_ADMIN_TOKEN` with Administration: write permission, followed by manual dispatch of `Main Ruleset Contract` in `apply` mode. The scheduled verifier will then fail closed if the live platform configuration drifts.

No completion claim is made for live branch protection until the verifier returns `status: verified` against GitHub's authenticated administration API.
