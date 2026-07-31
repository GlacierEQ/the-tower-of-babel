#!/usr/bin/env python3
"""One-time enrichment of generated README authority surfaces."""
from __future__ import annotations

from pathlib import Path

path = Path("src/tower/generate.py")
text = path.read_text(encoding="utf-8")
replacements = {
    "`registry/tower.yml` is the root authority. It indexes governed `registry/tower.d/*.json` fragments; the README and every machine-readable projection are derived from that source.":
        "`registry/tower.yml` is the root authority. It indexes governed `registry/tower.d/*.json` technology fragments and `registry/advanced-claim-contracts.json`; the README, Atlas, and every machine-readable projection are derived from that combined authority.",
    "registry/tower.yml + tower.d fragments":
        "registry/tower.yml + tower.d fragments + advanced claim contracts",
    "- an evidence state and proof class matching checked-in verification.\n":
        "- an evidence state and proof class matching checked-in verification;\n- a registry-owned semantic claim contract with source assertions, failure cases, receipt fields, and prohibited overclaims.\n",
    "| [`registry/tower.yml`](registry/tower.yml) | Canonical index and governance root | **Authored authority** |\n":
        "| [`registry/tower.yml`](registry/tower.yml) | Canonical index and governance root | **Authored authority** |\n| [`registry/advanced-claim-contracts.json`](registry/advanced-claim-contracts.json) | Source assertions, failure obligations, receipt fields, and truthful claim boundaries | **Authored authority** |\n",
    "| [`.integrity/file_hashes.json`](.integrity/file_hashes.json) | SHA-256 ledger for governed artifacts | Sealed surface |\n":
        "| [`.integrity/file_hashes.json`](.integrity/file_hashes.json) | SHA-256 ledger for governed artifacts | Sealed surface |\n| [`docs/SUPPLY_CHAIN_AND_PROTECTION.md`](docs/SUPPLY_CHAIN_AND_PROTECTION.md) | Hash-locked CI, OIDC attestations, ruleset verification, and deletion receipts | Operational contract |\n",
    "- Every claim carries an evidence state and proof class.\n":
        "- Every claim carries an evidence state, proof class, and registry-owned semantic claim contract.\n",
    "- Integrity, build evidence, proof reports, and receipts remain deterministic review surfaces.\n":
        "- Integrity, build evidence, proof reports, and receipts remain deterministic review surfaces; `main` receipts additionally receive OIDC-bound Sigstore provenance.\n",
}
for old, new in replacements.items():
    if old not in text:
        raise SystemExit(f"README generation anchor missing: {old[:80]!r}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
