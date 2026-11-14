# Spaceflight Expansion Audit

## Purpose

This audit checks whether the Tower has omitted technology floors that matter for a SpaceX-style aerospace, launch, satellite, ground-systems, simulation, telemetry, and verification stack.

The live Tower already covers many current SpaceX-adjacent primitives: C, C++, Rust, Python, Go, TypeScript, SQL, CUDA, Triton, ONNX, MLIR, Protobuf, FlatBuffers, Cap'n Proto, SystemVerilog, VHDL, Chisel, Coq, Agda, WebAssembly, and related compute/proof/interface layers. The gap is therefore not more generic languages first. The gap is aerospace-specific execution environments, test/plant/simulation tooling, and model/formal architecture layers.

## Public-source posture

This audit does not claim to know SpaceX proprietary internals. It only records public signals and converts them into Tower candidate floors.

Public current SpaceX job postings emphasize:

- C++/Rust or comparable systems languages for Starship flight software controlling and simulating flight systems.
- Linux-based C++ software for Starshield processors and microcontrollers.
- C/C++/Python development across Starlink flight and ground systems.
- Python/C#/data systems for mission-critical application software, analytics, pipelines, .NET APIs, PostgreSQL, dashboards, and ML tooling.
- GNC algorithms, simulation, Monte Carlo, HITL, dashboards, C++/Python, and vehicle-dynamics simulation for Starlink.

## Verdict

The Tower should not add a proprietary `SpaceX` floor. It should add a governed **spaceflight systems expansion pack** whose floors represent transferable public engineering domains.

## Recommended candidate floors

| Priority | Candidate floor | Class | Why it belongs | Admission status |
|---:|---|---|---|---|
| 1 | Embedded Linux / Yocto | runtime / operating surface | Public SpaceX postings repeatedly identify Linux-based flight, ground, and application software surfaces. | candidate only |
| 2 | C# / .NET | application platform | Public SpaceX postings identify C#/Python application software and .NET APIs for mission-critical data systems. | candidate only |
| 3 | MATLAB / Simulink | model-based control and simulation | GNC, state estimation, control theory, Monte Carlo, HITL, and vehicle-dynamics work need a model-based engineering floor even when SpaceX-specific tool choice is not asserted. | candidate only |
| 4 | LabVIEW / test automation | hardware test and instrumentation | Historical public SpaceX software-team disclosures mention LabVIEW in build/launch/monitor tooling; treat as legacy-public signal, not current proof. | candidate only |
| 5 | RTOS / RTEMS | real-time runtime | Aerospace and embedded control stacks often require deterministic scheduling and timing proofs distinct from Linux. | candidate only |
| 6 | ROS 2 / DDS | distributed robotics middleware | Useful for fault-tolerant publish/subscribe, telemetry, command, and autonomous subsystem coordination in space robotics and satellite architectures. | candidate only |
| 7 | AADL / AGREE | avionics architecture and contract proof | Avionics systems need model-level architecture contracts and assume-guarantee reasoning beyond general-purpose proof languages. | candidate only |
| 8 | Modelica / FMI | physical-system modeling and co-simulation | Propulsion, thermal, fluids, electrical, and vehicle simulations need exchangeable plant models and co-simulation boundaries. | candidate only |

## Why these are not admitted yet

The Tower governance rule is strict: a floor should not enter the active registry until it has:

1. a canonical registry record;
2. an easy exhibit;
3. an advanced exhibit;
4. an advanced claim contract;
5. a toolchain or blocker definition;
6. a proof class and evidence state;
7. generated surfaces updated from the registry;
8. an integrity receipt.

This audit therefore creates a machine-readable proposal instead of silently inflating the Tower count.

## Proposed admission order

1. **C# / .NET** — easiest portable build gate; directly supported by current public SpaceX application-software postings.
2. **Embedded Linux / Yocto** — add as an operating-surface floor with a portable Linux capability probe and a Yocto-gated advanced build.
3. **MATLAB / Simulink** — add as `service_gated` or `toolchain_gated` unless an open Octave/Scilab fallback is explicitly scoped as illustrative only.
4. **RTOS / RTEMS** — add a portable conceptual model and gated RTEMS build receipt.
5. **AADL / AGREE** — add as formal architecture floor with parser/model examples and proof blockers.
6. **ROS 2 / DDS** — add as integration-gated distributed robotics middleware.
7. **Modelica / FMI** — add as physical-system co-simulation floor.
8. **LabVIEW** — add only as historical/test-automation candidate unless current proof improves.

## Admission boundary

Do not write: `The Tower has SpaceX's stack.`

Allowed claim after this audit:

> The Tower has identified public SpaceX-adjacent software and aerospace-system domains not yet represented as active registry floors, and has preserved them as candidate floors pending exhibits, claim contracts, and verification gates.

## Immediate next implementation

The next active floor should be **C# / .NET** because it is current-public, portable, executable in CI, and fills a real application/data-platform gap without waiting on proprietary aerospace toolchains.
