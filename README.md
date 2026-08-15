# The Tower of Babel — APEX

> **Executable polyglot architecture selection for maximum coherent advance.**

[![Tower Verification](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/tower.yml)
[![Quality Gate](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/ci.yml)
[![Spiral Engine](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml/badge.svg)](https://github.com/GlacierEQ/the-tower-of-babel/actions/workflows/spiral.yml)

The Tower decides **which technology belongs at which engineering boundary, why it belongs there, how it interoperates with adjacent lanes, how it fails, and what evidence would justify replacing it**.

It is not a language museum, a monoculture generator, or an authority over Casey Barton's intended system. Casey's project intent controls direction. The Tower supplies boundary analysis, executable comparison, interoperability, proof, and a continuously revisable frontier.

## APEX law

```text
INTENDED SYSTEM + CURRENT SOURCE STATE + VERIFIED PRIOR GAINS
→ identify real boundaries and bottlenecks
→ observe current frontier technology
→ generate multiple strong candidates
→ compose best-fit technologies by lane
→ build the strongest justified reversible experiment
→ measure + adversarially break + operate
→ preserve all unique gains
→ keep the non-dominated winner(s)
→ expand again
```

**Smallness and uniformity have zero intrinsic score.** A one-language repository is correct when one technology actually dominates its boundaries. A six-language repository is correct when six technologies each materially outperform alternatives in their lane and their interfaces are explicit.

## The system in one minute

| Capability | What the Tower does |
|---|---|
| **Boundary decomposition** | Turns a mission into explicit runtime, memory, compute, proof, interface, policy, and presentation concerns. |
| **Technology placement** | Records What, Where, When, Why, and How for every admitted language, format, compiler layer, database, HDL, and proof system. |
| **Frontier metabolism** | Ingests fresh primary-source technology signals and maps credible advances to real GlacierEQ bottlenecks. |
| **Executable learning** | Pairs each technology with an approachable exhibit and a substantive advanced implementation. |
| **Truthful verification** | Compiles, tests, benchmarks, integrates, or formally verifies claims; missing requirements become exact blockers. |
| **Cross-language composition** | Publishes versioned interfaces so specialized components cooperate without ambiguous ownership. |
| **Deterministic evidence** | Seals source state and emits reproducible build, proof, integrity, and release receipts. |

| APEX surface | Count |
|---|---:|
| Technology floors | **40** |
| Easy + advanced exhibits | **80** |
| Behavioral proof floors | **17** |
| Formal proof floors | **3** |
| Explicitly gated floors | **9** |

## From mission to APEX receipt

```text
human objective / agent mission / system requirement
                         │
                         ▼
              Spiral or Megamind request
                         │
                         ▼
             APEX Tower source registry
       placement · interfaces · owners · proof gate
                         │
                         ▼
        candidate composition / bounded experiment
                         │
                         ▼
         build / test / benchmark / formal check
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
   stronger proven lane            exact blocker
          │                    toolchain · hardware
          ▼                       service · evidence
  cross-language execution
          │
          ▼
 deterministic evidence receipt + next frontier cursor
```

## Start the Tower

```bash
python -m pip install -e .[dev]

tower validate
tower generate --check
tower integrity verify

tower spec rust
tower build rust
tower benchmark rust
tower megamind-map

tower spiral question \
  --seed tower-demo \
  --prompt-hint "maximum coherent multi-agent architecture"

python flagship/run_pipeline.py
```

Run a complete portable proof pass:

```bash
tower build --all --allow-blocked --output artifacts/build-report.json
tower benchmark python c cpp rust go typescript webassembly \
  --output artifacts/benchmarks.json
tower proof-report \
  --build-report artifacts/build-report.json \
  --benchmark-report artifacts/benchmarks.json \
  --allow-blocked \
  --output artifacts/proof-report.json
tower receipt \
  --build-report artifacts/build-report.json \
  --output artifacts/tower_receipt.json
```

## APEX source state

`registry/tower.yml` is the authored APEX technology source index. It names contained `registry/tower.d/*.json` technology fragments and `registry/advanced-claim-contracts.json`. Generated projections derive from that source state.

The source registry proves what the Tower currently knows and what evidence is attached. It does **not** redefine the intended system downward when implementation lags the target.

```text
registry/tower.yml + tower.d fragments + advanced claim contracts
                  │
                  ▼
        validation and path containment
                  │
                  ▼
        deterministic surface generation
                  │
        ┌─────────┼─────────┬──────────┬───────────┐
        ▼         ▼         ▼          ▼           ▼
     README   build map  interfaces  maturity  agent maps
        │         │         │          │           │
        └─────────┴─────────┴──────────┴───────────┘
                  │
                  ▼
       build · benchmark · proof · receipt · evolve
```

### Tower of Babel lane law

A technology earns a lane when the registry establishes:

- a unique responsibility and explicit boundary;
- activation conditions and measurable reason it beats alternatives there;
- easy and advanced exhibits;
- pinned toolchain references and execution commands;
- hardware, service, and dependency constraints;
- explicit interfaces and owners;
- evidence state and proof class matching checked-in verification;
- replacement criteria if a stronger technology appears;
- preservation accounting for any prior capability it supersedes.

No language receives estate-wide privilege. Python, TypeScript, Rust, Go, SQL, Julia, Fortran, Triton, CUDA, Zig, C/C++, Elixir/Erlang, Datalog, Lean, Coq, TLA+, Rego, WebAssembly, and future technologies compete at the boundaries they are actually good at.

### Flagship polyglot mission

```text
TypeScript ingress
    → mission contract
Python planner
    → capability plan
Rust authority boundary
    → allow / block decision
Go telemetry
    → execution event
SQL durable state
    → persisted mission
WebAssembly sandbox
    → constrained tool boundary
Lean 4
    → receipt-chain invariant
Tower APEX receipt
```

See [`flagship/README.md`](flagship/README.md) and run `python flagship/run_pipeline.py`.

### Proof before activation

| Evidence state | Meaning |
|---|---|
| `illustrative` | Teaches syntax or the central concept; no stronger runtime claim is made. |
| `compiles` | A pinned compiler or schema tool accepts the exhibit. |
| `tested` | Automated behavioral checks pass. |
| `benchmark` | A reproducible performance measurement exists. |
| `hardware_gated` | The implementation is present but requires declared hardware. |
| `toolchain_gated` | The implementation is present but its compiler is absent from portable CI. |
| `service_gated` | A declared external service is required. |
| `formally_verified` | A proof kernel accepts the theorem. |
| `integrated` | The floor participates in the flagship multi-language system. |
| `production_reference` | Operational failure handling, observability, and deployment evidence exist. |

Evidence limits what may be claimed. It does not prohibit a reversible ambitious experiment.

## Advanced Exhibit Atlas

The easy exhibit teaches the technology. The advanced exhibit owns a real engineering boundary, exposes failure behavior, and terminates in proof or an exact blocker. [`ADVANCED_EXHIBITS.md`](ADVANCED_EXHIBITS.md) publishes signature engineering moves and claim boundaries; [`quality/advanced_exhibit_atlas.json`](quality/advanced_exhibit_atlas.json) provides the same map to agents and automation.

## Complete APEX technology map

The matrix is generated from the APEX source registry. Change source state and exhibits, not the generated README.

<details>
<summary><strong>Open the complete placement, proof, and exhibit matrix</strong></summary>

| # | Technology | Class | What | Where | When | Why | Evidence | Easy | Advanced |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | **C** `.c` | language | Provides direct memory and hardware control with a minimal runtime. | Firmware, kernels, embedded loops, lock-free primitives, and portable system libraries. | Use when deterministic layout, ABI control, or near-zero runtime overhead is mandatory. | It is the universal systems interoperability layer and maps closely to machine execution. | `tested` / `behavioral` | [easy_linked_list.c](languages/c/easy_linked_list.c) | [advanced_lockfree_spsc_ring.c](languages/c/advanced_lockfree_spsc_ring.c) |
| 2 | **C++** `.cpp` | language | Combines low-level control with zero-cost abstractions and mature numerical libraries. | Engines, inference runtimes, cache systems, geometry, simulation, and latency-sensitive services. | Use when performance and complex abstractions must coexist in one native binary. | It provides deterministic ownership patterns, templates, SIMD access, and unmatched systems-library depth. | `tested` / `behavioral` | [easy_vector.cpp](languages/cpp/easy_vector.cpp) | [advanced_kv_entropy.cpp](languages/cpp/advanced_kv_entropy.cpp) |
| 3 | **Rust** `.rs` | language | Builds native systems with compile-time ownership, thread safety, and no garbage collector. | Evidence engines, action governors, cryptographic tooling, network services, and safe concurrency. | Use when native performance and strong memory/concurrency guarantees are both non-negotiable. | The borrow checker eliminates broad classes of memory corruption and data races before execution. | `tested` / `behavioral` | [easy_counter.rs](languages/rust/easy_counter.rs) | [advanced_safety_governor.rs](languages/rust/advanced_safety_governor.rs) |
| 4 | **Zig** `.zig` | language | Builds explicit, portable native software with compile-time metaprogramming and excellent C interop. | Portable CLIs, allocators, cross-compilation, embedded tools, and small runtime components. | Use when cross-target delivery, allocator control, or C integration dominates. | It provides explicit failure paths, no hidden allocation, and first-class cross-compilation. | `tested` / `behavioral` | [easy_hello.zig](languages/zig/easy_hello.zig) | [advanced_arena_allocator.zig](languages/zig/advanced_arena_allocator.zig) |
| 5 | **Odin** `.odin` | language | Prioritizes data-oriented native programming with explicit memory contexts and low hidden complexity. | Game engines, physics, visualization, and deterministic real-time loops. | Use when data layout, allocator visibility, and predictable control flow are central. | It presents a simpler C-like systems model with built-in data-oriented facilities. | `toolchain_gated` / `compile` | [easy_math.odin](languages/odin/easy_math.odin) | [advanced_reentry_thermal.odin](languages/odin/advanced_reentry_thermal.odin) |
| 6 | **Lua** `.lua` | language | Provides a tiny, portable embeddable scripting runtime for host-controlled extension. | Game engines, plugin hosts, config loaders, agent tool sandboxes, and embedded automation. | Use when untrusted or third-party logic must run under an explicit capability table. | Its small core and first-class environments make capability isolation practical without a heavyweight runtime. | `tested` / `behavioral` | [easy_hello.lua](languages/lua/easy_hello.lua) | [advanced_sandbox_capability_table.lua](languages/lua/advanced_sandbox_capability_table.lua) |
| 7 | **Python** `.py` | language | Rapidly composes AI, automation, analysis, and control-plane workflows. | Mission orchestration, model tooling, document pipelines, tests, and integration glue. | Use when iteration speed, ecosystem breadth, and readable coordination dominate the boundary. | It offers the strongest general AI ecosystem and the lowest friction for composing heterogeneous systems. | `tested` / `behavioral` | [easy_fibonacci.py](languages/python/easy_fibonacci.py) | [advanced_async_orchestrator.py](languages/python/advanced_async_orchestrator.py) |
| 8 | **Go** `.go` | language | Builds simple, deployable concurrent network services and telemetry processors. | Gateways, control-plane daemons, streaming telemetry, and cloud infrastructure. | Use when many I/O-bound tasks need straightforward concurrency and operational simplicity. | Goroutines, channels, static binaries, and a disciplined standard library reduce service complexity. | `tested` / `behavioral` | [easy_ping.go](languages/go/easy_ping.go) | [advanced_telemetry_decoder.go](languages/go/advanced_telemetry_decoder.go) |
| 9 | **TypeScript** `.ts` | language | Adds static contracts to JavaScript's browser, Node.js, and event-driven ecosystem. | MCP gateways, web applications, browser agents, connectors, and asynchronous control surfaces. | Use when the boundary is web-native, JSON/RPC-heavy, or shared between frontend and backend. | It catches interface drift before runtime while retaining JavaScript's deployment reach. | `tested` / `behavioral` | [easy_greet.ts](languages/typescript/easy_greet.ts) | [advanced_mcp_gateway.ts](languages/typescript/advanced_mcp_gateway.ts) |
| 10 | **Java** `.java` | language | Owns the JVM runtime baseline for enterprise services, Android, and portable bytecode deployment. | Application servers, batch gateways, Android runtimes, and cross-organization service boundaries. | Use when the operational contract is the JVM itself and long-lived enterprise ecosystems matter. | Java remains the universal JVM ABI and the language other JVM languages must interoperate with. | `tested` / `behavioral` | [easy_hello.java](languages/java/easy_hello.java) | [advanced_bounded_work_queue.java](languages/java/advanced_bounded_work_queue.java) |
| 11 | **Kotlin** `.kt` | language | Modern JVM and multiplatform language with null-safety and structured concurrency. | Android, server services, shared business logic, and agent runtimes on the JVM. | Use when new JVM work needs safer defaults, concise syntax, and optional multiplatform reach. | It is the practical successor language for most new JVM development while preserving full Java interop. | `tested` / `behavioral` | [easy_hello.kt](languages/kotlin/easy_hello.kt) | [advanced_coroutine_supervisor.kt](languages/kotlin/advanced_coroutine_supervisor.kt) |
| 12 | **Swift** `.swift` | language | Builds safe native software for Apple platforms and interoperates with Metal. | macOS/iOS applications, Apple Silicon inference, Metal compute, and device-native interfaces. | Use when the target is Apple's runtime, UI stack, or GPU/ANE ecosystem. | It combines native performance, safety features, and first-class Apple framework access. | `hardware_gated` / `hardware` | [easy_array.swift](languages/swift/easy_array.swift) | [advanced_metal_compute_engine.swift](languages/swift/advanced_metal_compute_engine.swift) |
| 13 | **Elixir** `.ex` | language | Runs massive numbers of isolated processes under supervision on the BEAM. | Realtime backends, event systems, self-healing clusters, and coordination services. | Use when fault isolation, uptime, and highly concurrent messaging dominate. | BEAM supervision and actor semantics make failure a managed lifecycle event. | `tested` / `behavioral` | [easy_actor.ex](languages/elixir/easy_actor.ex) | [advanced_fault_tolerant_beam.ex](languages/elixir/advanced_fault_tolerant_beam.ex) |
| 14 | **Haskell** `.hs` | language | Expresses pure transformations and rich type-level models with controlled effects. | Compilers, DSLs, formal models, financial logic, and correctness-sensitive transformations. | Use when algebraic structure and purity simplify reasoning about complex state. | Its type system and immutable semantics make invalid transformations harder to express. | `compiles` / `compile` | [easy_tree.hs](languages/haskell/easy_tree.hs) | [advanced_ast_validator.hs](languages/haskell/advanced_ast_validator.hs) |
| 15 | **R** `.R` | language | Provides expressive statistical modeling, inference, and visualization. | Experiments, Bayesian analysis, biostatistics, forecasting, and reproducible reports. | Use when statistical methodology and domain packages matter more than service deployment. | Its statistical ecosystem exposes mature, reviewable implementations of advanced methods. | `tested` / `behavioral` | [easy_statistics.R](languages/r/easy_statistics.R) | [advanced_bayesian_ab_test.R](languages/r/advanced_bayesian_ab_test.R) |
| 16 | **Julia** `.jl` | language | Combines high-level mathematical syntax with JIT-compiled numerical performance. | ODE/PDE solvers, optimization, scientific machine learning, and simulation. | Use when researchers need expressive mathematics without abandoning native-speed kernels. | Multiple dispatch and LLVM compilation unify interactive modeling with high-performance methods. | `tested` / `behavioral` | [easy_matrix.jl](languages/julia/easy_matrix.jl) | [advanced_orbital_differential.jl](languages/julia/advanced_orbital_differential.jl) |
| 17 | **Fortran** `.f90` | language | Delivers high-performance numerical and scientific kernels with mature array semantics. | Climate models, CFD, linear algebra, materials simulation, and legacy scientific stacks. | Use when dense numerical loops, long-lived scientific codes, or HPC libraries dominate. | It remains the performance and maintainability baseline for large-scale numerical computing. | `tested` / `behavioral` | [easy_hello.f90](languages/fortran/easy_hello.f90) | [advanced_heat_diffusion.f90](languages/fortran/advanced_heat_diffusion.f90) |
| 18 | **SQL / pgvector** `.sql` | query_language | Declares relational transformations, constraints, transactions, and vector retrieval. | Canonical state, analytics, audit records, knowledge graphs, and embedding search. | Use when durable data relationships and set-oriented operations belong inside the database. | The query planner, transactions, indexes, and constraints centralize data correctness and performance. | `service_gated` / `integration` | [easy_table.sql](languages/sql/easy_table.sql) | [advanced_pgvector_hnsw.sql](languages/sql/advanced_pgvector_hnsw.sql) |
| 19 | **CUDA C++ / PTX (gated kernel runtime)** `.cu` | gpu_kernel | NVIDIA GPU programming platform; this record is a reference-only host simulation until a real CUDA kernel is executed. | NVIDIA GPU services, inference kernels, and numerical workloads requiring measured device acceleration. | Select only after the target GPU, CUDA toolkit, kernel receipt, and baseline performance are verified. | Use for custom GPU kernels only when nvcc, a supported NVIDIA GPU, runtime launch evidence, and comparative measurements are available. | `illustrative` / `illustrative` | [easy_vector_add.cu](languages/cuda/easy_vector_add.cu) | [advanced_nvidia_flash_attention_kernel.cu](languages/cuda/advanced_nvidia_flash_attention_kernel.cu) |
| 20 | **Triton** `.py` | kernel_language | Defines high-throughput GPU kernels with Python syntax and compiler-managed block programming. | Fused attention, normalization, quantization, MoE routing, and custom inference operations. | Use after profiling shows framework kernels are inadequate and the target GPU is supported. | It exposes GPU performance without hand-authoring all CUDA indexing and scheduling details. | `hardware_gated` / `benchmark` | [easy_vector_add.py](languages/triton/easy_vector_add.py) | [advanced_fused_attention.py](languages/triton/advanced_fused_attention.py) |
| 21 | **Mojo** `.mojo` | language | Combines Python-like authoring with systems-level types, ownership, and accelerator-oriented compilation. | AI kernels, SIMD tensor code, model serving components, and MLIR-backed optimization. | Use when Python ergonomics must reach native or accelerator performance in one language. | Its compiler stack targets heterogeneous AI hardware while retaining familiar syntax. | `toolchain_gated` / `compile` | [easy_simd.mojo](languages/mojo/easy_simd.mojo) | [advanced_simd_tensor_kernel.mojo](languages/mojo/advanced_simd_tensor_kernel.mojo) |
| 22 | **ONNX** `.onnx` | model_format | Represents machine-learning computation as a portable typed graph independent of the training framework. | Model exchange, runtime deployment, graph inspection, optimization, and hardware-provider selection. | Use when a model must move between frameworks or run across multiple inference backends. | It separates learned graph semantics from any one training library and enables portable validation. | `tested` / `behavioral` | [easy_linear_model.py](languages/onnx/easy_linear_model.py) | [advanced_moe_router.py](languages/onnx/advanced_moe_router.py) |
| 23 | **MLIR** `.mlir` | intermediate_representation | Provides extensible intermediate representations and dialects across abstraction levels. | Compiler pipelines, tensor lowering, accelerator backends, DSLs, and hardware-specific optimization. | Use when one operation must be progressively transformed from domain semantics to machine code. | It makes compiler passes and hardware dialect boundaries explicit and reusable. | `toolchain_gated` / `compile` | [easy_add.mlir](languages/mlir/easy_add.mlir) | [advanced_attention_pipeline.mlir](languages/mlir/advanced_attention_pipeline.mlir) |
| 24 | **WebAssembly** `.wat` | binary_format | Provides a portable, capability-constrained bytecode target for sandboxed execution. | Browser modules, plugin systems, edge runtimes, and zero-trust agent tools. | Use when untrusted or portable code must run within explicit host capabilities. | Its validated bytecode and host-controlled imports create a small cross-platform isolation boundary. | `tested` / `behavioral` | [easy_add.wat](languages/wat/easy_add.wat) | [advanced_wasm_sandbox.wat](languages/wat/advanced_wasm_sandbox.wat) |
| 25 | **Protocol Buffers** `.proto` | idl | Defines language-neutral schemas for compact binary messages and RPC services. | Service contracts, telemetry, receipts, registries, and cross-language mission envelopes. | Use when multiple languages need one evolvable typed contract. | Field-numbered schemas preserve compatibility and generate implementations across ecosystems. | `tested` / `behavioral` | [easy_user.proto](languages/protobuf/easy_user.proto) | [advanced_colossus_cooling.proto](languages/protobuf/advanced_colossus_cooling.proto) |
| 26 | **FlatBuffers** `.fbs` | idl | Defines binary objects that can be read directly from a buffer without full unpacking. | Games, mobile state, telemetry, embedded inference, and latency-sensitive local IPC. | Use when read latency and allocation avoidance dominate and schema evolution remains required. | Generated accessors traverse the serialized buffer in place, reducing parsing and copying. | `compiles` / `compile` | [easy_user.fbs](languages/flatbuffers/easy_user.fbs) | [advanced_telemetry.fbs](languages/flatbuffers/advanced_telemetry.fbs) |
| 27 | **Cap'n Proto** `.capnp` | idl | Combines zero-copy serialization with capability-oriented RPC. | Low-latency distributed systems, secure object capabilities, storage engines, and agent IPC. | Use when serialized messages and authority-bearing RPC references must share one model. | It reads wire-format objects directly and encodes access through explicit capabilities. | `compiles` / `compile` | [easy_user.capnp](languages/capnproto/easy_user.capnp) | [advanced_agent_mesh.capnp](languages/capnproto/advanced_agent_mesh.capnp) |
| 28 | **Verilog** `.v` | hdl | Describes synthesizable digital logic at register-transfer level. | FPGA prototypes, ASIC blocks, counters, pipelines, and arithmetic units. | Use when the output must become gates, registers, and wires rather than software instructions. | It gives deterministic cycle-level hardware structure with broad tool support. | `compiles` / `compile` | [easy_counter.v](languages/verilog/easy_counter.v) | [advanced_weight_stationary_dot_array.v](languages/verilog/advanced_weight_stationary_dot_array.v) |
| 29 | **SystemVerilog** `.sv` | hdl | Extends Verilog with richer RTL, interfaces, assertions, and verification constructs. | ASIC/FPGA design, protocol interfaces, constrained verification, and accelerator pipelines. | Use when hardware design needs stronger typing, interfaces, or executable assertions. | It unifies synthesizable RTL with powerful verification semantics and industry tooling. | `compiles` / `compile` | [easy_counter.sv](languages/systemverilog/easy_counter.sv) | [advanced_systolic_array.sv](languages/systemverilog/advanced_systolic_array.sv) |
| 30 | **VHDL** `.vhd` | hdl | Describes strongly typed concurrent hardware with explicit packages and timing semantics. | Aerospace, defense, FPGA control logic, safety-critical digital systems, and reusable IP. | Use when hardware correctness, strong typing, and long-lived certification-oriented design dominate. | Its explicit type system and deterministic concurrency support highly reviewable RTL. | `compiles` / `compile` | [easy_counter.vhd](languages/vhdl/easy_counter.vhd) | [advanced_fault_tolerant_voter.vhd](languages/vhdl/advanced_fault_tolerant_voter.vhd) |
| 31 | **Chisel** `.scala` | hdl | Uses Scala to construct parameterized hardware generators that emit synthesizable RTL. | RISC-V processors, reusable accelerators, networks-on-chip, and parameterized hardware families. | Use when hardware should be generated from reusable abstractions rather than copied RTL. | It brings types, functions, testing libraries, and parameterization to hardware construction. | `toolchain_gated` / `compile` | [easy_counter.scala](languages/chisel/easy_counter.scala) | [advanced_noc_router.scala](languages/chisel/advanced_noc_router.scala) |
| 32 | **Lean 4** `.lean` | proof_language | Combines dependent types, executable functional programming, and machine-checked proofs. | Safety invariants, receipt-chain correctness, mathematics, and verified decision gates. | Use when a critical property must be proven rather than sampled by tests. | It produces kernel-checked proofs with explicit assumptions and reusable theorem libraries. | `formally_verified` / `formal` | [easy_logic.lean](languages/lean4/easy_logic.lean) | [advanced_truth_gate_proof.lean](languages/lean4/advanced_truth_gate_proof.lean) |
| 33 | **Coq** `.v` | proof_language | Defines programs and machine-checked proofs in the Calculus of Inductive Constructions. | Verified compilers, protocols, cryptography, semantics, and critical algorithms. | Use when constructive proofs, extraction, or mature proof libraries fit the assurance case. | It checks every proof term with a small trusted kernel and can extract verified programs. | `formally_verified` / `formal` | [easy_logic.v](languages/coq/easy_logic.v) | [advanced_receipt_chain.v](languages/coq/advanced_receipt_chain.v) |
| 34 | **Agda** `.agda` | proof_language | Uses dependent types for proofs and total functional programs. | Protocol models, type-safe DSLs, mathematical structures, and certified transformations. | Use when the implementation and proof should inhabit the same expressive dependent type system. | It makes invariants part of types and requires total, structurally valid definitions. | `formally_verified` / `formal` | [easy_logic.agda](languages/agda/easy_logic.agda) | [advanced_capability_lattice.agda](languages/agda/advanced_capability_lattice.agda) |
| 35 | **eBPF** `.bpf.c` | bytecode | Executes sandboxed bytecode inside the Linux kernel without modifying kernel source code. | Linux kernel tracing, Cilium networking, Falco security auditing, and socket performance profiling. | Use when kernel-level observability, network packet filtering, or syscall enforcement is required at line rate. | It enables programmable zero-overhead packet filtering, syscall tracing, and real-time security auditing. | `compiles` / `compile` | [easy_packet_filter.bpf.c](languages/ebpf/easy_packet_filter.bpf.c) | [advanced_syscall_sentinel.bpf.c](languages/ebpf/advanced_syscall_sentinel.bpf.c) |
| 36 | **OpenQASM 3.0** `.qasm` | circuit_description | Describes quantum circuits, entanglement gates, and classical feedback loops for QPUs. | IBM Quantum, AWS Braket, Rigetti, QPU simulators, and quantum error correction algorithms. | Use when constructing quantum circuits, Bell states, or hybrid quantum-classical algorithms. | It provides a hardware-agnostic intermediate representation for gate-based quantum compilation. | `toolchain_gated` / `compile` | [easy_bell_state.qasm](languages/openqasm/easy_bell_state.qasm) | [advanced_grover_oracle.qasm](languages/openqasm/advanced_grover_oracle.qasm) |
| 37 | **Cairo** `.cairo` | turing_complete_zk | A Turing-complete language for writing STARK-provable programs and zero-knowledge verification logic. | Starknet, STARK-based L2 rollups, verifiable AI inference, and privacy-preserving audit ledgers. | Use when off-chain state execution must produce cryptographically verifiable proof of correctness. | It allows complex off-chain execution to be mathematically proven on-chain via succinct cryptographic receipts. | `toolchain_gated` / `compile` | [easy_fib_proof.cairo](languages/cairo/easy_fib_proof.cairo) | [advanced_stark_governor.cairo](languages/cairo/advanced_stark_governor.cairo) |
| 38 | **JAX + XLA (gated autodiff runtime)** `.py` | tensor_autodiff | Python autodiff and XLA compilation framework; this record is a pure-Python shape simulation until JAX executes. | Verified JAX runtimes with a declared CPU/GPU/TPU backend and reproducible device tests. | Select only after JAX imports, jax.jit or pjit executes, and the requested sharding/backend receipt is captured. | Use when JAX/XLA provides a measured advantage for autodiff, compilation, or device parallelism. | `illustrative` / `illustrative` | [easy_grad_jit.py](languages/jax/easy_grad_jit.py) | [advanced_grok_distributed_mesh.py](languages/jax/advanced_grok_distributed_mesh.py) |
| 39 | **Soufflé Datalog** `.dl` | logic_rules | Declarative logic programming language for high-speed static code analysis and security verification. | Vulnerability scanning, compiler program analysis, access control evaluation, and static call graph analysis. | Use when declarative rule-based query evaluation across large code graphs is required. | It resolves complex graph reachability, pointer analysis, and security policy rules in parallel C++ code. | `compiles` / `compile` | [easy_reachability.dl](languages/datalog/easy_reachability.dl) | [advanced_vulnerability_scanner.dl](languages/datalog/advanced_vulnerability_scanner.dl) |
| 40 | **RHL-Quant reference quantizer (unbenchmarked)** `.py` | tensor_compression | Reference ternary/residual quantization experiment; no accelerator, model-scale, memory, or quality result is established here. | Benchmark harnesses for model compression after a backend, dataset, quality metric, and rollback path are defined. | Select only after a real backend implementation, baseline comparison, memory measurement, throughput measurement, and quality delta are verified. | A candidate compression path, not an operational choice, until numerical baselines and hardware measurements are reproduced. | `illustrative` / `illustrative` | [easy_ternary_scale.py](languages/rhl_quant/easy_ternary_scale.py) | [advanced_rhl_quant_engine.py](languages/rhl_quant/advanced_rhl_quant_engine.py) |

</details>

### Domain coverage

- **Ai Systems** — Mojo
- **Apple Native** — Swift
- **Bare Metal Systems** — C
- **Binary Contracts** — Protocol Buffers
- **Capability Rpc** — Cap'n Proto
- **Compiler Ir** — MLIR
- **Compute Graph** — ONNX
- **Concurrent Services** — Go
- **Data Oriented Systems** — Odin
- **Declarative Data** — SQL / pgvector
- **Declarative Static Analysis** — Soufflé Datalog
- **Dependent Programming** — Agda
- **Embeddable Scripting** — Lua
- **Fault Tolerant Distributed** — Elixir
- **Formal Verification** — Lean 4, Coq
- **Functional Ai Systems** — JAX + XLA (gated autodiff runtime)
- **Gpu Kernel Dsl** — Triton
- **Gpu Parallel Compute** — CUDA C++ / PTX (gated kernel runtime)
- **Hardware Construction** — Chisel
- **Hardware Description** — Verilog
- **Hardware Verification** — SystemVerilog
- **High Performance Systems** — C++
- **High Reliability Hardware** — VHDL
- **Hpc Numerical** — Fortran
- **Jvm Enterprise Services** — Java
- **Jvm Multiplatform** — Kotlin
- **Kernel Tracing And Security** — eBPF
- **Memory Safe Systems** — Rust
- **Orchestration And Ai** — Python
- **Portable Systems** — Zig
- **Pure Functional** — Haskell
- **Quantization And Compression** — RHL-Quant reference quantizer (unbenchmarked)
- **Quantum Compute** — OpenQASM 3.0
- **Sandbox Runtime** — WebAssembly
- **Scientific Computing** — Julia
- **Statistics** — R
- **Typed Async Interfaces** — TypeScript
- **Zero Copy Serialization** — FlatBuffers
- **Zero Knowledge Proofs** — Cairo

## Machine entrypoint

An AI system should use Tower source state as evidence and selection input, not as authority to shrink intent.

1. **Initialize** from `registry/tower.yml` or generated technology maps.
2. **Resolve** a mission into explicit architecture concerns and interfaces.
3. **Generate candidates** from incumbent and frontier technologies.
4. **Select or compose** technologies whose boundary advantages are measurable.
5. **Reject** ambiguous ownership, missing evidence, undeclared interfaces, and capability loss.
6. **Execute** through generated build contracts or typed adapters.
7. **Preserve** blockers, hashes, proof state, prior gains, rollback, and receipts.
8. **Advance** only when evidence shows the resulting boundary is stronger.
9. **Repeat** when the frontier moves.

### Generated contract library

| Surface | Role | Status |
|---|---|---|
| [`registry/tower.yml`](registry/tower.yml) | APEX technology source index | **Authored source state** |
| [`registry/advanced-claim-contracts.json`](registry/advanced-claim-contracts.json) | Claim boundaries and proof obligations | **Authored source state** |
| [`generated/build_commands.json`](generated/build_commands.json) | Toolchains, pins, build/test commands, execution tiers | Generated |
| [`generated/interfaces.json`](generated/interfaces.json) | Cross-language interface graph | Generated |
| [`generated/maturity.json`](generated/maturity.json) | Evidence state, proof class, exhibit locations | Generated |
| [`generated/megamind.technology-map.json`](generated/megamind.technology-map.json) | Agent/piston ownership and activation map | Active export |
| [`generated/spiral-engine.registry.json`](generated/spiral-engine.registry.json) | Spiral APEX frontier metadata | Generated |
| [`generated/smithery.registry.json`](generated/smithery.registry.json) | Smithery capability and publication contract | Declared, not published |
| [`.integrity/file_hashes.json`](.integrity/file_hashes.json) | Immutable base integrity ledger | Sealed base |
| [`.integrity/approved_delta.json`](.integrity/approved_delta.json) | Reviewed APEX evolution delta | Reviewed evolution |

## Portfolio mesh

The Tower owns technology placement and proof within its boundary. Connected repositories retain their own responsibilities and consume Tower exports through explicit interfaces.

| Repository | Relationship | Boundary |
|---|---|---|
| [`GlacierEQ/AKOS`](https://github.com/GlacierEQ/AKOS) | Authority/evidence and orchestration peer | Execution authority, evidence law, completion semantics, operating sequence. |
| [`GlacierEQ/aspen-grove-core`](https://github.com/GlacierEQ/aspen-grove-core) | Memory peer | Durable context, memory specialization, continuity. |
| [`GlacierEQ/apex-boot-core`](https://github.com/GlacierEQ/apex-boot-core) | Initialization peer | Identity and initialization contracts. |
| [`GlacierEQ/Pro_Code`](https://github.com/GlacierEQ/Pro_Code) | Engineering doctrine peer | Standards, doctrine, playbooks. |
| [`GlacierEQ/pro-code`](https://github.com/GlacierEQ/pro-code) | Engineering execution peer | Implements and verifies engineering changes. |
| [`GlacierEQ/job-app-helix`](https://github.com/GlacierEQ/job-app-helix) | Evidence/projection peer | Projects verified capabilities without redefining source intent. |
| [`GlacierEQ/apex-control-plane`](https://github.com/GlacierEQ/apex-control-plane) | Control-plane peer | Automation and execution surface. |
| [`GlacierEQ/apex-cli`](https://github.com/GlacierEQ/apex-cli) | Operator peer | Command surface for downstream workflows. |
| [`flagship/`](flagship/) | In-repository integration proof | Executes the strict polyglot mission contract. |

## APEX discipline that survives automation

- Generated surfaces are never hand-edited; `tower generate --check` rejects drift.
- Every claim carries evidence state, proof class, and a semantic claim contract.
- Blocked hardware, tools, dependencies, and services remain visible and machine-readable.
- Cross-language interfaces are explicit and versioned.
- Integrity distinguishes undeclared drift from reviewed evolution.
- Every replacement must account for prior unique capability.
- A passing proof is a checkpoint, not a reason to stop evolving.
- Merge state and generated projections are evidence of system state, not authority over project intent.

```text
edit APEX source fragment
    → update easy + advanced exhibits
    → compare against incumbent boundary
    → strengthen proof
    → tower validate
    → tower generate
    → pytest
    → tower build --all --allow-blocked
    → bind reviewed integrity delta
    → emit APEX receipt
    → review exact-head CI
    → pursue next frontier
```

## Truth boundary

The Tower is an **operational-alpha polyglot innovation engine**. It makes strong claims only where checked-in evidence supports them. Unproven records remain references or experiments. Missing hardware, services, toolchains, or evidence remain explicit blockers. The system is expected to become stronger continuously without laundering aspiration into proof or proof into authority over intent.

## License

MIT — see [`LICENSE`](LICENSE).
