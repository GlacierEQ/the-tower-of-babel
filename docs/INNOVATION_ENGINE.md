# Tower of Babel Innovation Engine

## What the Tower actually is

The Tower of Babel is a **semantic architecture optimizer**.

It does not choose one language for an entire repository and it does not add
languages for polyglot spectacle. It evaluates *what work each boundary is
doing* and places the strongest available language/runtime there.

A representative decomposition is:

| Boundary | What matters | Typical candidates |
|---|---|---|
| Memory | layout, allocators, locality, determinism, ownership | Odin, Rust, Zig, C/C++ |
| Logic | invariants, policy, correctness, concurrency, failure semantics | Rust, Haskell, typed JVM languages |
| Action | async I/O, tools, connectors, effects, runtime reach | TypeScript, Go, Python |
| Interface | RPC, MCP, schemas, browser/API contracts | TypeScript, Protobuf, Go |
| Persistence | transactions, durable state, constraints | SQL + host runtime |
| Orchestration | agents, workflows, routing, composition | Python, TypeScript, Go |
| Telemetry | events, metrics, streaming, operational simplicity | Go, Rust, TypeScript |
| Security | memory safety, sandboxing, crypto, policy boundaries | Rust, WebAssembly, formal tools |
| Proof | machine-checked invariants | Lean, Coq, Agda |

These are **candidate priors, not commandments**. The engine combines them with
the current Tower registry, repository evidence, existing integration,
interoperability cost, migration cost, toolchain evidence, and the repository's
actual semantic demand.

### Example: Odin + Rust + TypeScript

A repo may become *more stable and more capable* by dividing responsibility:

```text
Memory / data layout
        ↓
       Odin
 explicit allocator + layout ownership
        │ C ABI / versioned contract
        ▼
Logic / policy / safety
        ↓
       Rust
 invariants + ownership + concurrency safety
        │ typed RPC / protobuf / JSON contract
        ▼
Action / connectors / UI / MCP
        ↓
   TypeScript
 async effects + external system reach
```

The Tower evaluates that split against alternatives. If adding Odin creates less
value than its interface/migration cost, it does not add Odin. If Rust already
owns memory safely enough, it may preserve Rust. If TypeScript has absorbed
logic that would be safer in Rust, the engine can propose a measured extraction.

## Spiral behavior

The Innovation Engine runs a feedback loop:

```text
inspect real repository
    ↓
classify files by semantic role
    ↓
rank languages per role
    ↓
measure quality + placement + interface cost
    ↓
evaluate near-term and far-term impact
    ↓
choose highest coherent intervention
    ↓
apply through an executor
    ↓
re-inspect actual repository
    ↓
accept improvement / revise / stop on regression
    ↺
```

The default completion target is **9.0/10**, but the average cannot hide a weak
critical axis. Purpose focus, correctness, testing, security, and semantic
placement must each remain at least **8.5**.

## Always evaluate everything

This engine operationalizes the rule by evaluating each proposed change across:

- present semantic demand;
- current language ownership;
- language-role fit;
- registry evidence;
- interoperability cost;
- migration cost;
- near-term benefit;
- far-term benefit;
- capability gain;
- stability gain;
- reversibility;
- implementation risk;
- implementation effort;
- complexity delta;
- critical-quality regressions after execution.

No single factor controls every situation. The controller re-evaluates after
each revolution because the correct next move changes as the repository changes.

## Python API

```python
from tower.innovation import BabelSpiralEngine
from tower.registry import load_registry

engine = BabelSpiralEngine(load_registry(), target=9.0, max_revolutions=12)

# Without an executor it performs a full evaluation and emits the highest-value
# next interventions.
report = engine.run("/path/to/repository")

# A coding agent can provide a controlled executor. Returning True means state
# actually changed; the Tower then re-inspects instead of trusting the claim.
def executor(intervention, repo_root):
    ...
    return True

report = engine.run("/path/to/repository", executor=executor)
```

Planning is not mutation. Mutation is not completion. A revolution counts only
after the changed repository is re-evaluated.


## Runtime evidence weighting

Semantic demand is evidence-weighted. Implementation files carry full weight,
schemas/formal contracts nearly full weight, tests support the runtime picture,
configuration contributes moderately, and documentation is advisory. This
prevents a large README/docs surface from outvoting the code that actually runs.

A language that is not already present and whose Tower evidence state is
toolchain-, service-, or hardware-gated is not treated as deployment-ready.
The engine can still identify its architectural advantage, but the next move is
to prove availability and run a reversible experiment before migration.


## Stable owner and frontier specialist

Capability and stability are optimized together by keeping two separate
language decisions for each semantic boundary:

- **Stable owner** — the strongest currently integrated, executable language for
  the boundary. It remains responsible for production behavior unless a change
  earns promotion.
- **Frontier specialist** — the language with the strongest intrinsic semantic
  fit for the boundary. It may be stronger in principle but still require
  toolchain proof, an explicit interface, benchmarks, or a reversible experiment.

For example, a mature repository may keep a tested C++ or Rust memory owner
while identifying Odin as the memory-layout frontier. The Spiral first proves
Odin's toolchain and measures the boundary in isolation. It does not destabilize
the current owner merely because Odin has stronger intrinsic memory semantics.

Promotion therefore follows:

```text
stable owner
    + frontier specialist
    + explicit interface
    + executable proof
    + measured capability gain
    + measured stability gain
    - migration cost
    - interface cost
    - long-term complexity
            ↓
      promote / preserve
```

This allows the Tower to expand capability without converting architectural
experimentation into production instability.
