#!/usr/bin/env python3
"""Audit and expose every Tower advanced exhibit."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from tower.registry import REPO_ROOT, load_registry, validate_registry

PROFILES = {
    "c": ("Lock-free SPSC telemetry handoff", "bounded queue, atomics, FIFO and backpressure receipt"),
    "cpp": ("Entropy-aware KV cache policy", "deterministic utility scoring, pinned retention and decision fingerprint"),
    "rust": ("Typed side-effect safety governor", "fail-closed path, payload, depth and approval policy"),
    "zig": ("Mission-scoped allocator discipline", "arena lifetime, deduplication and hard sample ceiling"),
    "odin": ("Data-oriented thermal integration", "explicit physical bounds, ablation and mission diagnostics"),
    "python": ("Drainable priority agent runtime", "bounded queues, FIFO ties, futures, retries and graceful shutdown"),
    "go": ("Versioned telemetry trust boundary", "CRC, frame bounds, sequence continuity, cancellation and metrics"),
    "typescript": ("Governed MCP/JSON-RPC gateway", "runtime validation, mutation approval, rate limiting and hashed receipts"),
    "swift": ("Metal affine-clamp engine", "GPU dispatch with CPU reference and an explicit no-ANE claim boundary"),
    "elixir": ("Supervised idempotent mission worker", "duplicate rejection and observed process replacement after failure"),
    "haskell": ("Pure capability-policy AST validation", "algebraic decisions, lexical path safety and deterministic receipt"),
    "r": ("Exact Beta-Binomial decision analysis", "ROPE, HDI and expected loss without MCMC or Bayes-factor overclaim"),
    "julia": ("Energy-audited orbital integration", "velocity-Verlet propagation with conservation drift diagnostics"),
    "sql": ("Tenant-isolated vector evidence store", "HNSW retrieval, RLS, constraints and bounded search function"),
    "cuda": ("Audited reference attention kernel", "stable softmax and GPU validation without a FlashAttention claim"),
    "triton": ("Bounded fused single-query attention", "one-program fusion, Torch oracle and latency benchmark"),
    "mojo": ("SIMD affine-clamp tensor kernel", "explicit pointers and vector width without unsupported TPU branding"),
    "onnx": ("Portable top-k MoE router graph", "model checking, reference execution and deterministic expert ordering"),
    "mlir": ("Destination-style attention score lowering", "SSA tensor contract prepared for canonicalization and loop/vector passes"),
    "webassembly": ("Capability- and fuel-bounded tool sandbox", "memory bounds, denied-operation immutability and audit counters"),
    "protobuf": ("Cooling command and receipt contract", "schema evolution, oneof authority, deterministic serialization and hashes"),
    "flatbuffers": ("Hash-linked zero-copy telemetry frame", "typed samples, file identity and prior-frame integrity field"),
    "capnproto": ("Capability-oriented agent mesh RPC", "authority-bearing specialist references and typed receipts"),
    "verilog": ("Weight-stationary dot-product datapath", "registered coefficients, widened signed accumulation and valid timing"),
    "systemverilog": ("Assertion-bearing 2x2 MAC mesh", "explicit systolic dataflow and temporal accumulator invariants"),
    "vhdl": ("Triple-modular-redundancy voter", "majority result, mismatch signal and all-lanes-disagree assertion"),
    "chisel": ("Parameterized NoC router generator", "destination routing, round-robin arbitration and Decoupled backpressure"),
    "lean4": ("Monotone authority and receipt proofs", "kernel-checked action ordering and non-regressing sequence property"),
    "coq": ("Linked receipt-chain ordering proof", "constructive chain-step and ordered-list invariants"),
    "agda": ("Dependent capability lattice", "total transitivity proof and impossible destructive downgrade case"),
}

PLACEHOLDERS = [
    re.compile(r"^\s*pass\s*$", re.MULTILINE),
    re.compile(r"\bTODO\b|\bFIXME\b", re.IGNORECASE),
    re.compile(r"return\s+s\s*end"),
    re.compile(r"public\s+class\s+\w+\s*\{\s*public\s+init\(\)\s*\{\s*\}\s*\}"),
]


def classify(tech: dict) -> str:
    state = tech["evidence_state"]
    if state in {"tested", "formally_verified", "production_reference", "integrated"}:
        return "proof-grade"
    if state in {"compiles", "benchmark"}:
        return "verified-reference"
    return "explicitly-gated-reference"


def audit() -> tuple[list[str], dict]:
    registry = load_registry()
    errors = validate_registry(registry)
    rows = []
    ids = {tech["id"] for tech in registry.technologies}
    if set(PROFILES) != ids:
        errors.append("advanced exhibit profile coverage does not match canonical registry")

    for tech in registry.technologies:
        tech_id = tech["id"]
        path = REPO_ROOT / tech["advanced_example"]
        easy = REPO_ROOT / tech["easy_example"]
        if not path.is_file():
            errors.append(f"{tech_id}: advanced exhibit missing: {tech['advanced_example']}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        substantive = [
            line for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith(("//", "#", ";;", "--"))
        ]
        if len(substantive) < 8:
            errors.append(f"{tech_id}: advanced exhibit has only {len(substantive)} substantive lines")
        if easy.is_file() and easy.read_bytes() == path.read_bytes():
            errors.append(f"{tech_id}: easy and advanced exhibits are identical")
        for pattern in PLACEHOLDERS:
            if pattern.search(text):
                errors.append(f"{tech_id}: advanced exhibit contains placeholder pattern {pattern.pattern!r}")
        if not Path(tech["advanced_example"]).name.startswith("advanced_"):
            errors.append(f"{tech_id}: advanced exhibit filename must start with advanced_")

        toolchain = tech["toolchain"]
        state = tech["evidence_state"]
        if state == "tested" and not toolchain.get("test"):
            errors.append(f"{tech_id}: tested evidence requires a test command")
        if state in {"compiles", "formally_verified"} and not toolchain.get("build"):
            errors.append(f"{tech_id}: {state} evidence requires a build/proof command")
        if state in {"hardware_gated", "toolchain_gated", "service_gated"}:
            if not (tech["execution"].get("hardware_gate") or toolchain.get("tool")):
                errors.append(f"{tech_id}: gated exhibit lacks an exact blocker surface")

        innovation, proof_surface = PROFILES[tech_id]
        rows.append({
            "id": tech_id,
            "technology": tech["name"],
            "advanced_exhibit": tech["advanced_example"],
            "architectural_role": tech["where"],
            "activation_condition": tech["when"],
            "signature_innovation": innovation,
            "proof_surface": proof_surface,
            "evidence_state": state,
            "proof_class": tech["proof_class"],
            "maturity_tier": classify(tech),
            "interfaces": tech["interfaces"],
            "claim_boundary": "Distinctive repository synthesis; no unsupported claim of first invention or production readiness.",
        })

    atlas = {
        "schema_version": 1,
        "authority": "registry/tower.yml",
        "generated_by": "tools/audit_advanced_exhibits.py",
        "advanced_exhibit_count": len(rows),
        "all_profiles_present": len(rows) == len(PROFILES),
        "exhibits": rows,
    }
    return errors, atlas


def markdown(atlas: dict) -> str:
    lines = [
        "# Advanced Exhibit Atlas",
        "",
        "> A generated map of the engineering boundary, proof surface, and truthful claim limit for every advanced Tower exhibit.",
        "",
        "The Atlas exposes distinctive implementation choices without converting them into unsupported novelty or production claims. The canonical technology authority remains `registry/tower.yml`.",
        "",
        "| Technology | Signature engineering move | Evidence | Advanced exhibit |",
        "|---|---|---|---|",
    ]
    for row in atlas["exhibits"]:
        lines.append(
            f"| **{row['technology']}** | {row['signature_innovation']} — {row['proof_surface']} | "
            f"`{row['evidence_state']}` / `{row['proof_class']}` | "
            f"[`{Path(row['advanced_exhibit']).name}`]({row['advanced_exhibit']}) |"
        )
    lines.extend([
        "",
        "## Promotion standard",
        "",
        "An exhibit is advanced only when it owns a meaningful boundary, rejects invalid or unsafe states, exposes an observable result, and carries a proof command or exact environmental blocker. File size, exotic syntax, and dramatic naming are not evidence.",
        "",
        "## Originality boundary",
        "",
        "The Tower highlights **distinctive synthesis**: original combinations of governance, receipts, bounded execution, cross-language interfaces, and proof surfaces. It does not claim that a standard algorithm, language feature, or architecture was invented here unless independently documented evidence supports that claim.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors, atlas = audit()
    json_path = REPO_ROOT / "quality" / "advanced_exhibit_atlas.json"
    md_path = REPO_ROOT / "ADVANCED_EXHIBITS.md"
    json_content = json.dumps(atlas, indent=2, sort_keys=True) + "\n"
    md_content = markdown(atlas)
    if args.write:
        json_path.write_text(json_content, encoding="utf-8")
        md_path.write_text(md_content, encoding="utf-8")
    if args.check:
        if not json_path.is_file() or json_path.read_text(encoding="utf-8") != json_content:
            errors.append("quality/advanced_exhibit_atlas.json is missing or stale")
        if not md_path.is_file() or md_path.read_text(encoding="utf-8") != md_content:
            errors.append("ADVANCED_EXHIBITS.md is missing or stale")
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Advanced exhibit audit verified {atlas['advanced_exhibit_count']} exhibits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
