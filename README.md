# The Tower of Babel

> **A polyglot systems-engineering Rosetta Stone and capability registry.**  
> Twenty-one technologies, one W4H decision framework, one canonical manifest, and generated integration metadata for Smithery and Spiral Engine.

[![Languages](https://img.shields.io/badge/Languages-21-brightgreen)]()
[![Manifest](https://img.shields.io/badge/Source-registry%2Flanguages.json-blue)]()
[![License](https://img.shields.io/badge/License-MIT-blue)]()
[![GlacierEQ](https://img.shields.io/badge/GlacierEQ-Portfolio-purple)]()

---

## I/O front door — recruiters, builders, and curious humans

The Tower of Babel answers a practical question:

> **Which language belongs here, why does it belong here, and how does it connect to the rest of the system without becoming decorative polyglot sprawl?**

Every entry has:

- **What** it is best at.
- **Where** it belongs.
- **When** to select it.
- **Why** it beats the nearby alternatives for that role.
- **How** it executes that responsibility.
- An approachable exhibit and an advanced exhibit.
- Real build/check commands, supported interfaces, maturity, source links, and mesh registration metadata.

### Quick start

```bash
git clone https://github.com/GlacierEQ/the-tower-of-babel.git
cd the-tower-of-babel

python tools/generate.py --check
python -m unittest discover -s tests -v
python src/babel_registry.py
```

To change language metadata, edit **only** `registry/languages.json`, then regenerate:

```bash
python tools/generate.py
```

---

## Master of the trade — W4H placement matrix

This matrix is generated. Manual edits inside the markers will be rejected by CI.

<!-- BEGIN GENERATED:LANGUAGE_MATRIX -->
| # | Language | Exact role | Maturity | Interfaces | Easy | Advanced | Primary docs |
|---:|---|---|---|---|---|---|---|
| 1 | **Python** (`.py`) | AI/ML pipelines, document intelligence, automation | `exhibit` / seeded | `cli`, `stdio`, `http`, `mcp` +2 | [easy](languages/python/easy_fibonacci.py) | [advanced](languages/python/advanced_async_orchestrator.py) | [Official documentation](https://docs.python.org/3/) |
| 2 | **C** (`.c`) | Kernels, firmware, embedded and ABI foundations | `exhibit` / seeded | `cli`, `ffi`, `shared-library`, `embedded` | [easy](languages/c/easy_linked_list.c) | [advanced](languages/c/advanced_lockfree_spsc_ring.c) | [WG14 C standards group](https://www.open-std.org/jtc1/sc22/wg14/) |
| 3 | **C++** (`.cpp`) | Low-latency compute, engines, inference and numerical kernels | `exhibit` / seeded | `cli`, `ffi`, `shared-library`, `grpc` +1 | [easy](languages/cpp/easy_vector.cpp) | [advanced](languages/cpp/advanced_kv_entropy.cpp) | [ISO C++](https://isocpp.org/) |
| 4 | **Rust** (`.rs`) | Integrity cores, policy engines, concurrency and cryptographic tooling | `exhibit` / seeded | `cli`, `ffi`, `wasm`, `grpc` +2 | [easy](languages/rust/easy_counter.rs) | [advanced](languages/rust/advanced_safety_governor.rs) | [Learn Rust](https://www.rust-lang.org/learn) |
| 5 | **Go** (`.go`) | Network services, daemons, telemetry and control-plane edges | `exhibit` / seeded | `cli`, `http`, `grpc`, `protobuf` +2 | [easy](languages/go/easy_ping.go) | [advanced](languages/go/advanced_telemetry_decoder.go) | [Go documentation](https://go.dev/doc/) |
| 6 | **TypeScript** (`.ts`) | MCP gateways, web interfaces, browser automation and control planes | `exhibit` / seeded | `cli`, `stdio`, `http`, `websocket` +2 | [easy](languages/typescript/easy_greet.ts) | [advanced](languages/typescript/advanced_mcp_gateway.ts) | [TypeScript documentation](https://www.typescriptlang.org/docs/) |
| 7 | **CUDA** (`.cu`) | NVIDIA kernels, tensor operations and accelerator extensions | `exhibit` / specialized-toolchain | `gpu-kernel`, `ffi`, `pytorch-extension`, `cuda-graph` | [easy](languages/cuda/easy_vector_add.cu) | [advanced](languages/cuda/advanced_flash_attn_kernel.cu) | [CUDA Toolkit documentation](https://docs.nvidia.com/cuda/) |
| 8 | **SystemVerilog / Verilog** (`.v`) | FPGA, ASIC, digital logic and accelerator datapaths | `exhibit` / specialized-toolchain | `rtl`, `axi-stream`, `pcie`, `testbench` +1 | [easy](languages/verilog/easy_counter.v) | [advanced](languages/verilog/advanced_systolic_matmul.v) | [IEEE 1800 SystemVerilog standard](https://standards.ieee.org/ieee/1800/7743/) |
| 9 | **R** (`.R`) | Statistical inference, experimentation, reporting and biostatistics | `exhibit` / seeded | `cli`, `notebook`, `report`, `http` | [easy](languages/r/easy_statistics.R) | [advanced](languages/r/advanced_bayesian_ab_test.R) | [R documentation](https://www.r-project.org/other-docs.html) |
| 10 | **Julia** (`.jl`) | Differential equations, numerical methods and high-performance research | `exhibit` / specialized-toolchain | `cli`, `notebook`, `ffi`, `distributed` | [easy](languages/julia/easy_matrix.jl) | [advanced](languages/julia/advanced_orbital_differential.jl) | [Julia documentation](https://docs.julialang.org/) |
| 11 | **Swift** (`.swift`) | macOS/iOS applications, Metal compute and Apple platform integration | `exhibit` / specialized-toolchain | `cli`, `swift-package`, `metal`, `ffi` +1 | [easy](languages/swift/easy_array.swift) | [advanced](languages/swift/advanced_metal_ane_engine.swift) | [Swift documentation](https://www.swift.org/documentation/) |
| 12 | **Zig** (`.zig`) | Static utilities, C integration, cross-compilation and constrained runtimes | `exhibit` / specialized-toolchain | `cli`, `ffi`, `static-library`, `wasm` +1 | [easy](languages/zig/easy_hello.zig) | [advanced](languages/zig/advanced_arena_allocator.zig) | [Zig language reference](https://ziglang.org/documentation/master/) |
| 13 | **Odin** (`.odin`) | Real-time simulation, visualization, game-style engines and explicit data pipelines | `exhibit` / specialized-toolchain | `cli`, `ffi`, `static-library`, `visualization` | [easy](languages/odin/easy_math.odin) | [advanced](languages/odin/advanced_reentry_thermal.odin) | [Odin documentation](https://odin-lang.org/docs/) |
| 14 | **Mojo** (`.mojo`) | ML kernels, Python-interoperable acceleration and MLIR-oriented compute | `exhibit` / experimental-toolchain | `cli`, `python-interop`, `mlir`, `accelerator-kernel` | [easy](languages/mojo/easy_simd.mojo) | [advanced](languages/mojo/advanced_tpu_tensor_kernel.mojo) | [Mojo documentation](https://mojolang.org/) |
| 15 | **Elixir** (`.ex`) | Supervision trees, messaging systems and highly concurrent services | `exhibit` / specialized-toolchain | `cli`, `otp`, `http`, `websocket` +1 | [easy](languages/elixir/easy_actor.ex) | [advanced](languages/elixir/advanced_fault_tolerant_beam.ex) | [Elixir documentation](https://elixir-lang.org/docs.html) |
| 16 | **Haskell** (`.hs`) | Compilers, DSLs, transformations and high-assurance logic | `exhibit` / specialized-toolchain | `cli`, `ffi`, `grpc`, `compiler-plugin` | [easy](languages/haskell/easy_tree.hs) | [advanced](languages/haskell/advanced_ast_validator.hs) | [Haskell documentation](https://www.haskell.org/documentation/) |
| 17 | **Lean 4** (`.lean`) | Proof-carrying invariants, state machines and mathematical truth gates | `exhibit` / specialized-toolchain | `proof-artifact`, `cli`, `codegen`, `specification` | [easy](languages/lean4/easy_logic.lean) | [advanced](languages/lean4/advanced_truth_gate_proof.lean) | [Lean learning resources](https://lean-lang.org/documentation/) |
| 18 | **Triton** (`.py`) | Fused tensor kernels and model-specific GPU optimization | `exhibit` / specialized-toolchain | `python-api`, `gpu-kernel`, `pytorch-extension` | [easy](languages/triton/easy_vector_add.py) | [advanced](languages/triton/advanced_fused_attention.py) | [Triton documentation](https://triton-lang.org/main/index.html) |
| 19 | **Protocol Buffers** (`.proto`) | Canonical cross-language contracts, RPC messages and durable event schemas | `exhibit` / seeded | `idl`, `grpc`, `codegen`, `event-schema` | [easy](languages/protobuf/easy_user.proto) | [advanced](languages/protobuf/advanced_colossus_cooling.proto) | [Protocol Buffers documentation](https://protobuf.dev/) |
| 20 | **SQL / PostgreSQL** (`.sql`) | Canonical state, constraints, audit queries and vector retrieval | `exhibit` / seeded | `sql`, `postgres`, `vector-store`, `audit-log` | [easy](languages/sql/easy_table.sql) | [advanced](languages/sql/advanced_pgvector_hnsw.sql) | [PostgreSQL documentation](https://www.postgresql.org/docs/current/) |
| 21 | **WebAssembly** (`.wat`) | Zero-trust tools, portable plugins and host-constrained execution | `exhibit` / specialized-toolchain | `wasm`, `wasi`, `component-model`, `plugin` | [easy](languages/wat/easy_add.wat) | [advanced](languages/wat/advanced_wasm_sandbox.wat) | [WebAssembly project](https://webassembly.org/) |
<!-- END GENERATED:LANGUAGE_MATRIX -->

---

## Deep AI/ML and programmatic integration

The repository is deliberately layered:

```text
human decision guide
        ↓
registry/languages.json                 canonical authored truth
        ↓
tools/generate.py                       deterministic compiler
        ├── README matrix
        ├── Python runtime registry
        ├── build command catalog
        ├── supported interface catalog
        ├── maturity and promotion gates
        ├── Smithery capability declarations
        └── Spiral Engine pillar/piston declarations
        ↓
tests + CI                              drift and evidence gates
```

The AI/ML path is not “use Python for everything.” It is a pipeline:

```text
Python / Julia / R      research, evaluation, analysis
ONNX / Protobuf        portable model and message contracts
Triton / CUDA / Mojo   profiled accelerator kernels
C++ / Rust / Zig       native runtime, integrity, and deployment
SQL                    canonical state and vector retrieval
Lean 4                 selected machine-checked invariants
WASM                   capability-limited plugin execution
TypeScript / Go        MCP, web, service, and control-plane edges
```

The current advanced files are **exhibits**, not automatically production-certified components. The manifest makes that truth explicit and defines the gates required to promote any language piston to production.

---

## Linked mesh — Smithery, Spiral Engine, Pillars & Pistons

### Smithery

`generated/smithery.registry.json` declares which languages can host MCP servers, which serve as tool backends or contract providers, their intended transports, and their publication state.

A declaration is not a fake registry success. `declared-not-published` remains the status until a real MCP package is published and a registry receipt exists.

### Spiral Engine

`generated/spiral-engine.registry.json` maps every technology to:

- a **pillar** — the durable capability domain;
- a **piston** — the executable mechanism;
- a unique capability ID;
- required build, test, and digest evidence.

A declared piston is not active until Spiral Engine returns an actual registration receipt.

### Link library

<!-- BEGIN GENERATED:LINK_LIBRARY -->
The complete generated library lives at [`generated/link_library.md`](generated/link_library.md). It contains 63 language-owned references.
<!-- END GENERATED:LINK_LIBRARY -->

---

## Generated artifacts

| Artifact | Purpose |
|---|---|
| `src/babel_registry.py` | Python-readable runtime registry generated from the manifest |
| `generated/build_commands.json` | Toolchain, check, and example execution commands |
| `generated/interfaces.json` | Supported interfaces and integration surfaces |
| `generated/maturity.json` | Claim scope, maturity, and promotion gates |
| `generated/link_library.md` | Official, source, standards, and ecosystem links owned by each language |
| `generated/smithery.registry.json` | Smithery-oriented capability and transport declarations |
| `generated/spiral-engine.registry.json` | Pillar/piston registration declarations |

---

## Truth contract

The repository fails validation when:

- README, registry, or generated metadata drifts from the manifest;
- a language ID or Spiral capability ID is duplicated;
- an easy or advanced exhibit is missing;
- a language lacks build commands, interfaces, or link references;
- a link is not HTTPS;
- Smithery metadata implies publication without an explicit published status;
- a production maturity claim lacks the full promotion-gate set.

See [`docs/MANIFEST_CONTRACT.md`](docs/MANIFEST_CONTRACT.md).

---

## License

MIT License — see [`LICENSE`](LICENSE).

**Built by [GlacierEQ](https://github.com/GlacierEQ).**
