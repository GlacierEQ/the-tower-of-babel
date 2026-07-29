#!/usr/bin/env python3
"""
Tower of Babel Registry & Rationale Engine (src/babel_registry.py).
Evaluates 17 languages across What, Where, When, Why, How (W4H) dimensions.
"""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class BabelLanguageSpec:
    name: str
    extension: str
    what: str
    where: str
    when: str
    why: str
    how: str

BABEL_REGISTRY: Dict[str, BabelLanguageSpec] = {
    "odin": BabelLanguageSpec("Odin", ".odin", "Data-oriented systems language", "Aerospace physics & reentry math", "Sub-microsecond physics integration required", "Zero hidden control flow and GC pauses", "Custom context allocators & explicit struct layouts"),
    "zig": BabelLanguageSpec("Zig", ".zig", "Bare-metal systems language without macros", "Bare-metal agent memory kernels", "Operating in memory-constrained environments", "Prevents runtime OOM and buffer allocation crashes", "Explicit std.mem.Allocator passed to functions"),
    "rust": BabelLanguageSpec("Rust", ".rs", "Memory-safe systems language without GC", "Safety governors & action boundary checkers", "Concurrent execution requires data race freedom", "Borrow checker enforces memory safety at compile time", "Ownership, RAII, and thread-safe channels"),
    "cpp": BabelLanguageSpec("C++", ".cpp", "High-performance OOP & STL language", "KV-cache entropy pruners & Kepler solvers", "Max throughput numerical computing required", "Direct memory pointers and SIMD auto-vectorization", "Template metaprogramming and RAII memory wrappers"),
    "cuda": BabelLanguageSpec("CUDA", ".cu", "NVIDIA parallel GPU programming language", "Tensor Core attention matrix kernels", "PetaFLOP matrix math operations are bottlenecked", "Executes directly on CUDA core SMs", "Kernel grids, thread blocks, and shared memory"),
    "protobuf": BabelLanguageSpec("Protobuf", ".proto", "Language-neutral binary serialization IDL", "100k GPU liquid cooling telemetry RPCs", "High-frequency IPC microservices demand low bandwidth", "Zero-copy binary encoding beats JSON by 10x", "Proto3 syntax compiling to C++/Go/Python stubs"),
    "lean4": BabelLanguageSpec("Lean 4", ".lean", "Dependent type formal theorem prover", "Operator truth gates and safety proofs", "Mathematical certainty of safety is mandatory", "Verifies correctness proofs statically before execution", "Dependent types, tactics, and inductive definitions"),
    "go": BabelLanguageSpec("Go", ".go", "Concurrent garbage-collected systems language", "Flight telemetry decoders & microservices", "High-concurrency networking with low latency", "Sub-millisecond concurrent GC and CSP goroutines", "Goroutines, channels, and binary packing"),
    "typescript": BabelLanguageSpec("TypeScript", ".ts", "Typed asynchronous JavaScript dialect", "Sovereign MCP stdio routers & web agents", "Building web I/O services and browser DOM bridges", "Strong typing prevents runtime undefined property errors", "Node.js V8 runtime, async/await, and interface types"),
    "triton": BabelLanguageSpec("Triton", ".py", "OpenAI GPU programming language", "Fused LLM attention kernels", "Custom CUDA kernels are too slow to write by hand", "Compiles Python-like code directly to optimized PTX", "Triton JIT decorator and block pointer math"),
    "mojo": BabelLanguageSpec("Mojo", ".mojo", "Modular AI systems language", "TPU SIMD tensor vectorization", "Combining Python syntax with C-speed vectorization", "Hardware-agnostic ML IR compilation", "fn declarations, struct types, and SIMD vectors"),
    "julia": BabelLanguageSpec("Julia", ".jl", "JIT-compiled scientific computing language", "Orbital differential equation solvers", "Solving high-dimensional non-linear differential equations", "Dynamic syntax with C-speed LLVM JIT compilation", "Multiple dispatch, LinearAlgebra, and ODE solvers"),
    "elixir": BabelLanguageSpec("Elixir", ".ex", "BEAM fault-tolerant functional language", "Supercomputer cluster supervision trees", "Building self-healing high-concurrency clusters", "Erlang BEAM actor model isolates process crashes", "GenServer, supervision trees, and pattern matching"),
    "swift": BabelLanguageSpec("Swift", ".swift", "Apple native systems language", "Metal GPU & Apple Neural Engine compute", "Optimizing LLMs for macOS/iOS Apple Silicon", "Zero-cost C/Obj-C interoperability with Metal API", "ARC memory management, Metal buffers, and SIMD"),
    "haskell": BabelLanguageSpec("Haskell", ".hs", "Purely functional lazy language", "Pure algebraic AST validation passes", "Validating complex state machines without side effects", "Immutability guarantees AST transformations are pure", "Pattern matching, monads, and algebraic data types"),
    "sql": BabelLanguageSpec("SQL/pgvector", ".sql", "Declarative database query language", "Vector similarity & relational knowledge bases", "Searching million-vector LLM embedding stores", "Native HNSW index search executes inside database engine", "PostgreSQL pgvector extension and cosine distance ops"),
    "wat": BabelLanguageSpec("WebAssembly", ".wat", "WebAssembly text format bytecode", "Zero-trust sandboxed agent tool execution", "Running untrusted user tools securely", "Capability-based sandboxing isolated from host OS", "WASM stack machine, export functions, and memory limits")
}

class BabelRegistryEngine:
    def get_spec(self, lang_key: str) -> Dict[str, Any]:
        spec = BABEL_REGISTRY.get(lang_key.lower())
        if not spec:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {
            "name": spec.name,
            "extension": spec.extension,
            "what": spec.what,
            "where": spec.where,
            "when": spec.when,
            "why": spec.why,
            "how": spec.how,
            "status": "VALIDATED_W4H_SPEC",
            "ok": True
        }

if __name__ == "__main__":
    engine = BabelRegistryEngine()
    print(f"Tower of Babel Registry Initialized: {len(BABEL_REGISTRY)} Languages Registered.")
