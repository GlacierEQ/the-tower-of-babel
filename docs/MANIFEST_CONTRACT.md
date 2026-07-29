# Canonical Language Manifest Contract

`registry/languages.json` is the only hand-authored source of language placement truth.

## Generated surfaces

Running `python tools/generate.py` deterministically updates:

- the README language matrix and link-library summary;
- `src/babel_registry.py`;
- build commands;
- supported interfaces;
- maturity and promotion gates;
- Smithery declarations;
- Spiral Engine pillar/piston declarations;
- the per-language link library.

CI runs `python tools/generate.py --check`. Any hand-edited generated artifact fails.

## Required language record

Every language must define:

1. identity and file extension;
2. category and primary domain;
3. complete W4H;
4. easy and advanced exhibit paths;
5. toolchain, check, and execution commands;
6. supported interfaces;
7. maturity, claim scope, and promotion gates;
8. at least two HTTPS references;
9. Smithery role, transports, and publication truth;
10. Spiral Engine pillar, piston, capability ID, and evidence requirements.

## Maturity meanings

- `concept`: placement is defined but executable evidence is absent.
- `exhibit`: representative code exists; production behavior is not certified.
- `integration-candidate`: native tests and at least one real interface contract pass.
- `production`: build, native tests, cross-language contracts, benchmark evidence, and artifact digests all exist.

No filename may be labeled “production-grade” merely because it is located in an advanced example path.

## Smithery truth

`declared-not-published` means the metadata exists locally but no registry publication receipt has been observed.

`published` requires:

- a real MCP server or package;
- declared transports;
- package/version identity;
- Smithery registry receipt or resolvable listing;
- conformance evidence.

## Spiral Engine truth

`declared` means Babel has assigned a pillar, piston, and capability ID.

Activation requires a Spiral Engine registration receipt containing:

- capability ID;
- implementation artifact digest;
- interfaces;
- build and test receipts;
- activation state.
