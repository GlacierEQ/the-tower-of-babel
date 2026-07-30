# The Tower of Babel

> **A polyglot systems-engineering Rosetta Stone:** 21 languages, 42 focused exhibits, one machine-readable W4H decision framework.

[![Languages](https://img.shields.io/badge/languages-21-2ea44f)](src/babel_registry.py)
[![Exhibits](https://img.shields.io/badge/exhibits-42-2ea44f)](quality/exhibit_status.json)
[![Quality Contract](https://img.shields.io/badge/advanced%20contract-enforced-6f42c1)](QUALITY_CONTRACT.md)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

The Tower of Babel is not an argument that every problem needs another language. It demonstrates the opposite: **language choice should be deliberate, bounded, and provable.** Each language is placed where its runtime model, type system, hardware access, or ecosystem creates measurable value.

---

## 1. For recruiters and engineering leaders

This repository demonstrates three capabilities that are difficult to communicate through a conventional résumé:

### Systems judgment

The project explains **what, where, when, why, and how** each language belongs in a production architecture. Python handles orchestration; Rust guards privileged actions; Go decodes concurrent telemetry; TypeScript governs MCP and web protocol surfaces; C controls lock-free memory; SQL protects canonical state.

### Depth without theater

The repository distinguishes between:

- **production-depth exhibits** that satisfy the repository’s advanced engineering contract; and
- **promotion candidates** that are useful language demonstrations but are not yet represented as production-ready.

That distinction is tracked in [`quality/exhibit_status.json`](quality/exhibit_status.json). The current baseline contains **7 production-depth advanced exhibits** and **14 candidates with explicit gaps**. The repository does not hide incomplete depth behind badges or file counts.

### Architecture that can be inspected by humans and agents

The README serves the human reader. The canonical registry, maturity ledger, sidecar telemetry, tests, and CI serve machines. A hiring manager can understand the thesis quickly; a senior engineer can inspect the implementation; an AI agent can query the same source of truth programmatically.

---

## 2. For senior engineers and technical reviewers

### Canonical architecture

```text
README.md                         Human impact and navigation
QUALITY_CONTRACT.md               Definition of easy vs. advanced evidence
src/babel_registry.py             Canonical 21-language W4H registry
quality/exhibit_status.json       Machine-readable maturity and gaps
mastermind_sidecar.py             Derived operational telemetry
languages/<language>/             Easy and advanced exhibits
tests/test_tower_of_babel.py      Repository invariants
.github/workflows/ci.yml          Native compiler and contract validation
.integrity/file_hashes.json       Integrity inventory
```

Counts are derived from the registry. They are not independently hard-coded into the sidecar or tests.

### W4H language matrix

| Language | Production domain | Why this language | Easy exhibit | Advanced exhibit | Current maturity |
|---|---|---|---|---|---|
| Python | AI orchestration and document intelligence | Ecosystem breadth and structured async integration | [Fibonacci](languages/python/easy_fibonacci.py) | [Async multi-agent orchestrator](languages/python/advanced_async_orchestrator.py) | **Production-depth** |
| C | Firmware and real-time telemetry | Explicit memory ordering and minimal runtime overhead | [Linked list](languages/c/easy_linked_list.c) | [Lock-free SPSC ring](languages/c/advanced_lockfree_spsc_ring.c) | **Production-depth** |
| C++ | Inference runtimes and numerical systems | RAII, contiguous storage, and zero-cost abstractions | [Vector](languages/cpp/easy_vector.cpp) | [KV entropy](languages/cpp/advanced_kv_entropy.cpp) | Candidate |
| Rust | Safety governors and trusted CLIs | Compile-time memory safety and exhaustive policy modeling | [Counter](languages/rust/easy_counter.rs) | [Typed action governor](languages/rust/advanced_safety_governor.rs) | **Production-depth** |
| Go | Telemetry and connector daemons | Simple concurrency and static deployment | [Ping](languages/go/easy_ping.go) | [Verified telemetry decoder](languages/go/advanced_telemetry_decoder.go) | **Production-depth** |
| TypeScript | MCP gateways and web control planes | Typed asynchronous protocol surfaces | [Greeting](languages/typescript/easy_greet.ts) | [Governed MCP gateway](languages/typescript/advanced_mcp_gateway.ts) | **Production-depth** |
| CUDA | GPU attention kernels | Direct control of NVIDIA execution and memory hierarchy | [Vector add](languages/cuda/easy_vector_add.cu) | [Attention kernel](languages/cuda/advanced_flash_attn_kernel.cu) | Candidate |
| Verilog | FPGA and ASIC accelerators | Deterministic parallel circuits | [Counter](languages/verilog/easy_counter.v) | [4×4 systolic array](languages/verilog/advanced_systolic_matmul.v) | **Production-depth** |
| R | Bayesian experimentation | First-class statistical inference and reporting | [Statistics](languages/r/easy_statistics.R) | [Bayesian A/B engine](languages/r/advanced_bayesian_ab_test.R) | **Production-depth** |
| Julia | Orbital and differential-equation simulation | Mathematical clarity with LLVM JIT performance | [Matrix](languages/julia/easy_matrix.jl) | [Orbital integrator](languages/julia/advanced_orbital_differential.jl) | Candidate |
| Swift | Apple-native compute and operator applications | Safe native access to Metal and platform frameworks | [Array](languages/swift/easy_array.swift) | [Metal engine](languages/swift/advanced_metal_ane_engine.swift) | Candidate |
| Zig | Explicit resource-bounded kernels | Allocator visibility and deterministic cleanup | [Hello](languages/zig/easy_hello.zig) | [Arena allocator](languages/zig/advanced_arena_allocator.zig) | Candidate |
| Odin | Data-oriented physics systems | Predictable layout and low hidden runtime behavior | [Math](languages/odin/easy_math.odin) | [Reentry thermal model](languages/odin/advanced_reentry_thermal.odin) | Candidate |
| Mojo | Emerging SIMD AI systems | Python-like syntax with compiler-level vectorization | [SIMD](languages/mojo/easy_simd.mojo) | [Tensor kernel](languages/mojo/advanced_tpu_tensor_kernel.mojo) | Candidate |
| Elixir | Fault-tolerant distributed supervision | OTP process isolation and recovery | [Actor](languages/elixir/easy_actor.ex) | [Cluster supervisor](languages/elixir/advanced_fault_tolerant_beam.ex) | Candidate |
| Haskell | Pure AST and policy transformation | Algebraic data types and deterministic composition | [Tree](languages/haskell/easy_tree.hs) | [AST validator](languages/haskell/advanced_ast_validator.hs) | Candidate |
| Lean 4 | Machine-checked safety claims | Proof checking against a small trusted kernel | [Logic](languages/lean4/easy_logic.lean) | [Truth-gate proof](languages/lean4/advanced_truth_gate_proof.lean) | Candidate |
| Triton | Fused GPU kernels | Block-level GPU programming without handwritten CUDA | [Vector add](languages/triton/easy_vector_add.py) | [Fused attention](languages/triton/advanced_fused_attention.py) | Candidate |
| Protobuf | Typed cross-language telemetry | Compact, evolvable binary contracts | [User schema](languages/protobuf/easy_user.proto) | [Cooling telemetry](languages/protobuf/advanced_colossus_cooling.proto) | Candidate |
| SQL/pgvector | Canonical data and semantic retrieval | Transactions, constraints, policy, and vector indexing | [Table](languages/sql/easy_table.sql) | [HNSW vector store](languages/sql/advanced_pgvector_hnsw.sql) | Candidate |
| WebAssembly text | Capability-bounded plugins | Portable linear-memory sandbox boundary | [Add](languages/wat/easy_add.wat) | [Guard sandbox](languages/wat/advanced_wasm_sandbox.wat) | Candidate |

### What “advanced” means here

The full standard is defined in [`QUALITY_CONTRACT.md`](QUALITY_CONTRACT.md). An advanced exhibit must include meaningful validation, failure behavior, an invariant or policy boundary, observability, bounded resources where relevant, and a runnable demonstration or test vector. Empty bodies and unconditional-success stubs cannot be promoted.

### Validation

Baseline CI currently proves:

- the registry contains exactly 21 languages;
- the filesystem contains exactly the registered language directories and 42 registered exhibits;
- every W4H record is complete and queryable;
- the maturity ledger covers every language;
- Python registry, sidecar, and repository tests execute;
- C exhibits compile and run with warnings treated as errors;
- C++ exhibits compile with warnings treated as errors;
- Go exhibits are formatted and tested, including adversarial decoder cases;
- Rust exhibits compile and the safety-governor tests pass.

Specialized GPU, FPGA, theorem-prover, and emerging-language toolchains are tracked separately. The README does not describe those files as compiler-validated unless the corresponding toolchain actually ran.

---

## 3. For AI ingestion and system-mesh integration

### Stable query surface

```python
from src.babel_registry import query_babel_registry

all_languages = query_babel_registry()
rust = query_babel_registry("rust")
```

The response contains:

- language identity and extension;
- W4H selection rationale;
- exact easy and advanced exhibit paths;
- verification tier;
- repository layout validation.

Run it directly:

```bash
python3 src/babel_registry.py
python3 mastermind_sidecar.py
python3 -m unittest discover -s tests -v
```

### Mesh relationships

The repository is designed to inform—not replace—the surrounding system:

- **MCP and control planes:** TypeScript gateway patterns.
- **Evidence and privileged execution:** Rust policy governor and C integrity primitives.
- **Connector and telemetry services:** Go concurrency and binary validation.
- **AI/document intelligence:** Python orchestration.
- **Canonical state and retrieval:** PostgreSQL/pgvector patterns.
- **Future untrusted plugins:** WebAssembly capability boundaries.

The intended integration path is a small MCP adapter around `query_babel_registry()`, allowing agents to ask which language belongs at a system boundary and receive the rationale plus concrete exhibit evidence.

---

## Quick start

```bash
git clone https://github.com/GlacierEQ/the-tower-of-babel.git
cd the-tower-of-babel

python3 src/babel_registry.py
python3 mastermind_sidecar.py
python3 -m unittest discover -s tests -v
```

## License

MIT. See [`LICENSE`](LICENSE).
