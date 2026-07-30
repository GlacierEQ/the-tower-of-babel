#!/usr/bin/env python3
"""Canonical Tower of Babel language registry and repository validator.

The registry is the machine-readable source of truth behind the README matrix,
telemetry sidecar, tests, and future MCP exposure. Counts are never duplicated
in code: they are derived from ``BABEL_REGISTRY`` and the repository layout.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class BabelLanguageSpec:
    """Why a language exists in the mesh and which exhibits prove the claim."""

    name: str
    extension: str
    what: str
    where: str
    when: str
    why: str
    how: str
    easy_exhibit: str
    advanced_exhibit: str
    verification_tier: str


BABEL_REGISTRY: dict[str, BabelLanguageSpec] = {
    "python": BabelLanguageSpec(
        "Python", ".py", "Dynamic automation and AI language",
        "AI pipelines, orchestration, document intelligence",
        "Rapid integration and ecosystem breadth matter most",
        "Asyncio, typing, and mature libraries compress delivery time",
        "Structured concurrency, dataclasses, validation, and adapters",
        "languages/python/easy_fibonacci.py",
        "languages/python/advanced_async_orchestrator.py",
        "native-ci",
    ),
    "c": BabelLanguageSpec(
        "C", ".c", "Bare-metal systems language",
        "Firmware, embedded systems, real-time telemetry",
        "Deterministic memory layout and minimal runtime overhead are required",
        "C exposes atomics, cache alignment, and hardware-level control",
        "C11 atomics, explicit allocation, and memory-order semantics",
        "languages/c/easy_linked_list.c",
        "languages/c/advanced_lockfree_spsc_ring.c",
        "native-ci",
    ),
    "cpp": BabelLanguageSpec(
        "C++", ".cpp", "High-performance systems and numerical language",
        "Inference runtimes, cache management, simulation",
        "Zero-cost abstractions and tight memory control are needed",
        "RAII and the STL combine performance with maintainable structure",
        "Templates, contiguous storage, vectorization, and deterministic ownership",
        "languages/cpp/easy_vector.cpp",
        "languages/cpp/advanced_kv_entropy.cpp",
        "native-ci",
    ),
    "rust": BabelLanguageSpec(
        "Rust", ".rs", "Memory-safe systems language without a garbage collector",
        "Safety governors, evidence hashing, trusted CLIs",
        "Concurrency and untrusted input require compile-time safety",
        "Ownership prevents data races and memory corruption",
        "Typed policies, exhaustive enums, bounded resources, and auditable results",
        "languages/rust/easy_counter.rs",
        "languages/rust/advanced_safety_governor.rs",
        "native-ci",
    ),
    "go": BabelLanguageSpec(
        "Go", ".go", "Concurrent network and service language",
        "Telemetry decoders, daemons, connector services",
        "Large numbers of I/O-bound tasks need simple operational behavior",
        "Goroutines, channels, and static binaries simplify service delivery",
        "Bounded workers, binary decoding, context cancellation, and metrics",
        "languages/go/easy_ping.go",
        "languages/go/advanced_telemetry_decoder.go",
        "native-ci",
    ),
    "typescript": BabelLanguageSpec(
        "TypeScript", ".ts", "Typed asynchronous JavaScript",
        "MCP gateways, control planes, browser and web integrations",
        "Schema-rich asynchronous I/O must run across Node and edge runtimes",
        "Static types constrain dynamic protocol and API surfaces",
        "Discriminated unions, runtime validation, policy gates, and receipts",
        "languages/typescript/easy_greet.ts",
        "languages/typescript/advanced_mcp_gateway.ts",
        "native-ci",
    ),
    "cuda": BabelLanguageSpec(
        "CUDA", ".cu", "NVIDIA parallel GPU programming",
        "Attention, tensor kernels, high-throughput numerical workloads",
        "General-purpose kernels cannot meet accelerator throughput targets",
        "CUDA exposes thread blocks, shared memory, and Tensor Core execution",
        "Tiled kernels, bounds checks, synchronization, and host verification",
        "languages/cuda/easy_vector_add.cu",
        "languages/cuda/advanced_flash_attn_kernel.cu",
        "specialized-toolchain",
    ),
    "verilog": BabelLanguageSpec(
        "Verilog", ".v", "Register-transfer-level hardware description",
        "FPGA and ASIC accelerator datapaths",
        "Compute behavior must be synthesized directly into hardware",
        "RTL describes deterministic parallel circuits rather than software steps",
        "Pipelined processing elements, reset logic, and simulation testbenches",
        "languages/verilog/easy_counter.v",
        "languages/verilog/advanced_systolic_matmul.v",
        "specialized-toolchain",
    ),
    "r": BabelLanguageSpec(
        "R", ".R", "Statistical computing language",
        "Bayesian experiments, clinical analysis, statistical reporting",
        "Inference quality and statistical diagnostics dominate runtime concerns",
        "R provides first-class vectorized statistics and reproducible analysis",
        "Posterior simulation, credible intervals, decision thresholds, and reports",
        "languages/r/easy_statistics.R",
        "languages/r/advanced_bayesian_ab_test.R",
        "optional-ci",
    ),
    "julia": BabelLanguageSpec(
        "Julia", ".jl", "JIT-compiled scientific computing language",
        "Orbital mechanics and differential-equation simulation",
        "Interactive mathematical code must approach compiled performance",
        "Multiple dispatch and LLVM JIT preserve mathematical clarity and speed",
        "Typed state vectors, stable integration, invariants, and simulation reports",
        "languages/julia/easy_matrix.jl",
        "languages/julia/advanced_orbital_differential.jl",
        "specialized-toolchain",
    ),
    "swift": BabelLanguageSpec(
        "Swift", ".swift", "Apple-native systems language",
        "macOS and iOS compute, Metal integration, operator applications",
        "Apple-platform security and hardware APIs are required",
        "Swift combines native framework access with memory-safe value semantics",
        "Metal capability discovery, resource lifetimes, validation, and fallbacks",
        "languages/swift/easy_array.swift",
        "languages/swift/advanced_metal_ane_engine.swift",
        "specialized-toolchain",
    ),
    "zig": BabelLanguageSpec(
        "Zig", ".zig", "Explicit low-level systems language",
        "Resource-bounded kernels and allocator-controlled runtimes",
        "Hidden allocation and runtime behavior are unacceptable",
        "Zig makes allocators and error paths explicit",
        "Arena ownership, bounded lifetimes, error unions, and deterministic cleanup",
        "languages/zig/easy_hello.zig",
        "languages/zig/advanced_arena_allocator.zig",
        "specialized-toolchain",
    ),
    "odin": BabelLanguageSpec(
        "Odin", ".odin", "Data-oriented systems language",
        "Physics simulation and explicit-layout numerical systems",
        "Predictable control flow and data layout are primary requirements",
        "Odin avoids hidden control flow and encourages data-oriented design",
        "Explicit structures, validated timesteps, and stable numerical integration",
        "languages/odin/easy_math.odin",
        "languages/odin/advanced_reentry_thermal.odin",
        "specialized-toolchain",
    ),
    "mojo": BabelLanguageSpec(
        "Mojo", ".mojo", "AI systems language built on MLIR",
        "SIMD tensor transforms and emerging accelerator workloads",
        "Python-like ergonomics must coexist with low-level vector performance",
        "Mojo exposes value semantics, SIMD, and compiler-specialized kernels",
        "Typed tensor views, vectorized loops, bounds handling, and reference checks",
        "languages/mojo/easy_simd.mojo",
        "languages/mojo/advanced_tpu_tensor_kernel.mojo",
        "specialized-toolchain",
    ),
    "elixir": BabelLanguageSpec(
        "Elixir", ".ex", "BEAM actor-model language",
        "Fault-tolerant distributed supervision and event processing",
        "Many isolated processes must recover independently from failure",
        "OTP supervision and process isolation are built into the runtime",
        "GenServers, supervisors, backoff, monitoring, and explicit state transitions",
        "languages/elixir/easy_actor.ex",
        "languages/elixir/advanced_fault_tolerant_beam.ex",
        "specialized-toolchain",
    ),
    "haskell": BabelLanguageSpec(
        "Haskell", ".hs", "Pure functional language",
        "AST validation, transformation, and policy reasoning",
        "Complex transformations must remain deterministic and composable",
        "Algebraic data types and purity make invalid states visible",
        "Typed ASTs, accumulated validation errors, pure transformations, and tests",
        "languages/haskell/easy_tree.hs",
        "languages/haskell/advanced_ast_validator.hs",
        "specialized-toolchain",
    ),
    "lean4": BabelLanguageSpec(
        "Lean 4", ".lean", "Dependent-type theorem prover",
        "Machine-checked safety properties and operator truth gates",
        "A safety claim must be proven rather than inferred from tests",
        "Lean checks proofs against a small trusted kernel",
        "Definitions, invariants, decidable predicates, and machine-checked theorems",
        "languages/lean4/easy_logic.lean",
        "languages/lean4/advanced_truth_gate_proof.lean",
        "specialized-toolchain",
    ),
    "triton": BabelLanguageSpec(
        "Triton", ".py", "Pythonic GPU kernel language",
        "Fused LLM and tensor kernels",
        "A custom kernel needs GPU-level optimization without handwritten CUDA",
        "Triton compiles block-level programs to optimized GPU code",
        "Masked loads, numerically stable reductions, tiling, and reference checks",
        "languages/triton/easy_vector_add.py",
        "languages/triton/advanced_fused_attention.py",
        "specialized-toolchain",
    ),
    "protobuf": BabelLanguageSpec(
        "Protocol Buffers", ".proto", "Language-neutral binary interface definition",
        "Typed telemetry and cross-language RPC contracts",
        "Services require compact schemas with generated clients",
        "Protobuf provides versionable contracts and efficient binary encoding",
        "Explicit units, reserved fields, streaming RPCs, and evolution guidance",
        "languages/protobuf/easy_user.proto",
        "languages/protobuf/advanced_colossus_cooling.proto",
        "optional-ci",
    ),
    "sql": BabelLanguageSpec(
        "SQL/pgvector", ".sql", "Declarative relational and vector query language",
        "Canonical state, evidence ledgers, and semantic retrieval",
        "Consistency, constraints, and indexed retrieval belong near the data",
        "PostgreSQL combines transactions, policy, and vector indexes",
        "Schema constraints, metadata, HNSW indexes, parameterized search, and maintenance",
        "languages/sql/easy_table.sql",
        "languages/sql/advanced_pgvector_hnsw.sql",
        "optional-ci",
    ),
    "wat": BabelLanguageSpec(
        "WebAssembly Text", ".wat", "Portable sandboxed bytecode representation",
        "Capability-restricted plugins and deterministic tool execution",
        "Untrusted logic needs a narrow, portable execution boundary",
        "WebAssembly isolates linear memory and explicit imports/exports",
        "Bounded memory, validated inputs, explicit exports, and host-side capability control",
        "languages/wat/easy_add.wat",
        "languages/wat/advanced_wasm_sandbox.wat",
        "specialized-toolchain",
    ),
}


class BabelRegistryEngine:
    """Query language rationale and verify that repository claims match reality."""

    def __init__(self, repo_root: Path | str | None = None) -> None:
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[1]

    def get_spec(self, lang_key: str) -> dict[str, Any]:
        spec = BABEL_REGISTRY.get(lang_key.lower())
        if spec is None:
            return {"status": "UNKNOWN_SPEC", "ok": False, "language": lang_key}
        return {**asdict(spec), "key": lang_key.lower(), "status": "VALIDATED_W4H_SPEC", "ok": True}

    def list_specs(self) -> list[dict[str, Any]]:
        return [self.get_spec(key) for key in BABEL_REGISTRY]

    def validate_layout(self) -> dict[str, Any]:
        languages_root = self.repo_root / "languages"
        expected_directories = set(BABEL_REGISTRY)
        actual_directories = {
            path.name for path in languages_root.iterdir() if path.is_dir()
        } if languages_root.is_dir() else set()

        missing_files: list[str] = []
        invalid_extensions: list[str] = []
        empty_files: list[str] = []
        for spec in BABEL_REGISTRY.values():
            for relative_path in (spec.easy_exhibit, spec.advanced_exhibit):
                path = self.repo_root / relative_path
                if not path.is_file():
                    missing_files.append(relative_path)
                    continue
                if path.suffix != spec.extension:
                    invalid_extensions.append(relative_path)
                if path.stat().st_size == 0:
                    empty_files.append(relative_path)

        report = {
            "language_count": len(BABEL_REGISTRY),
            "exhibit_count": len(BABEL_REGISTRY) * 2,
            "missing_directories": sorted(expected_directories - actual_directories),
            "unexpected_directories": sorted(actual_directories - expected_directories),
            "missing_files": missing_files,
            "invalid_extensions": invalid_extensions,
            "empty_files": empty_files,
        }
        report["ok"] = not any(
            report[key]
            for key in (
                "missing_directories",
                "unexpected_directories",
                "missing_files",
                "invalid_extensions",
                "empty_files",
            )
        )
        report["status"] = "LAYOUT_VALID" if report["ok"] else "LAYOUT_INVALID"
        return report


def query_babel_registry(lang_key: str | None = None) -> dict[str, Any]:
    """Stable programmatic entry point for agents, CLIs, and MCP adapters."""

    engine = BabelRegistryEngine()
    if lang_key:
        return engine.get_spec(lang_key)
    return {
        "ok": True,
        "status": "BABEL_REGISTRY_READY",
        "languages": engine.list_specs(),
        "layout": engine.validate_layout(),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(query_babel_registry(), indent=2, sort_keys=True))
