# Spaceflight Expansion Hub

## Purpose

This is the durable navigation layer for the Tower's SpaceX-adjacent / aerospace expansion work. It links the audit, machine-readable candidates, admission backlog, and implementation tasks without admitting any candidate floor prematurely.

The governing boundary remains strict:

- The Tower does **not** claim proprietary SpaceX-stack knowledge.
- Candidate floors are not active Tower floors until `registry/tower.yml` admits them through a governed fragment.
- No Tower count changes until examples, advanced claim contracts, proof gates, generated surfaces, and integrity receipts exist.
- Public aerospace/spaceflight signals are treated as transfer-domain evidence, not private-stack proof.

## Durable records

| Record | Role | Status |
|---|---|---|
| `docs/SPACEFLIGHT_EXPANSION_AUDIT.md` | Human audit and public-source posture | drafted |
| `registry/proposals/spaceflight-expansion.candidates.json` | Machine-readable candidate-floor proposal | drafted |
| `registry/proposals/spaceflight-admission-backlog.json` | Ordered implementation backlog with gates and receipts | drafted |
| GitHub tracking issue | Operational task surface for admission work | created after this doc |

## Candidate floors

| Priority | Candidate | Registry status | First durable action |
|---:|---|---|---|
| 1 | Embedded Linux / Yocto | candidate only | Define Linux capability probe and Yocto blocker receipt |
| 2 | C# / .NET | candidate only | Build first portable active-admission PR |
| 3 | MATLAB / Simulink | candidate only | Define model-based control exhibit and license/toolchain blocker |
| 4 | RTOS / RTEMS | candidate only | Define deterministic scheduler exhibit and RTEMS gate |
| 5 | AADL / AGREE | candidate only | Define avionics architecture contract proof surface |
| 6 | ROS 2 / DDS | candidate only | Define QoS telemetry pub/sub integration gate |
| 7 | Modelica / FMI | candidate only | Define physical-system co-simulation boundary |
| 8 | LabVIEW / test automation | candidate only | Keep historical/test-automation candidate until current proof improves |

## First active admission

The first floor to promote should be **C# / .NET** because it can be made portable and verifiable immediately:

- easy exhibit: typed records and validation for telemetry or mission status;
- advanced exhibit: minimal mission telemetry API or CLI pipeline with typed request/response contracts;
- evidence state: `tested`;
- proof class: `behavioral`;
- build gate: `dotnet build`;
- test gate: `dotnet test`;
- generated surfaces: README matrix, build map, agent map, maturity map, and release artifact;
- receipt: Tower integrity receipt plus floor-specific build/test output.

## Admission gates for every candidate

A candidate floor becomes active only when a PR includes all of the following:

1. `registry/tower.d/<domain>.json` record or update;
2. easy exhibit path;
3. advanced exhibit path;
4. advanced claim contract entry;
5. toolchain definition with exact command(s);
6. hardware/service/toolchain blocker semantics;
7. proof class and evidence state;
8. generated surfaces refreshed from the registry;
9. integrity manifest/receipt updated by the Tower engine;
10. CI or explicit gated-blocker result.

## Ownership boundary

The Tower owns:

- technology taxonomy;
- floor admission;
- W4H definitions;
- examples and advanced exhibits;
- toolchain/proof gates;
- interop contracts;
- evidence states and receipts.

Megamind or Spiral may consume this expansion pack, but they must query Tower contracts rather than copy prose into a separate authority.

## Next action

Open a focused C# / .NET active-admission PR that adds the floor, examples, advanced claim contract, generated surfaces, and a portable CI proof gate.