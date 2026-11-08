#!/usr/bin/env python3
"""Audit and expose every Tower advanced exhibit from registry-owned claims."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tower.registry import REPO_ROOT, load_registry, validate_registry

PLACEHOLDERS = [
    re.compile(r"^\s*pass\s*$", re.MULTILINE),
    re.compile(r"\bTODO\b|\bFIXME\b", re.IGNORECASE),
    re.compile(r"return\s+s\s*end"),
    re.compile(r"public\s+class\s+\w+\s*\{\s*public\s+init\(\)\s*\{\s*\}\s*\}"),
]
DISCLAIMER_MARKERS = (
    "no ",
    "no-",
    "not ",
    "without ",
    "unsupported",
    "does not",
    "do not",
    "claim boundary",
    "overclaim",
)


EVIDENCE_RANK = {
    "illustrative": 0,
    "toolchain_gated": 1,
    "service_gated": 1,
    "hardware_gated": 1,
    "compiles": 2,
    "tested": 3,
    "benchmark": 4,
    "formally_verified": 4,
    "integrated": 5,
    "production_reference": 6,
}

EVIDENCE_TIERS = {
    "illustrative": "concept_only",
    "toolchain_gated": "gated_reference",
    "service_gated": "gated_reference",
    "hardware_gated": "gated_reference",
    "compiles": "runnable_reference",
    "tested": "tested_implementation",
    "benchmark": "benchmarked_implementation",
    "formally_verified": "tested_implementation",
    "integrated": "integrated_capability",
    "production_reference": "production_reference",
}


def classify(tech: dict) -> str:
    return EVIDENCE_TIERS[tech["evidence_state"]]


def _forbidden_positive_claim(text: str, pattern: str) -> bool:
    compiled = re.compile(pattern, re.IGNORECASE)
    for line in text.splitlines():
        if not compiled.search(line):
            continue
        normalized = line.casefold()
        if any(marker in normalized for marker in DISCLAIMER_MARKERS):
            continue
        return True
    return False


def audit() -> tuple[list[str], dict]:
    registry = load_registry()
    errors = validate_registry(registry)
    rows = []
    ids = {tech["id"] for tech in registry.technologies}
    contracts = registry.claim_contracts
    if set(contracts) != ids:
        errors.append(
            "advanced claim contract coverage does not match canonical registry"
        )

    for tech in registry.technologies:
        tech_id = tech["id"]
        contract = contracts.get(tech_id)
        if not isinstance(contract, dict):
            errors.append(f"{tech_id}: advanced claim contract missing")
            continue
        path = REPO_ROOT / tech["advanced_example"]
        easy = REPO_ROOT / tech["easy_example"]
        if not path.is_file():
            errors.append(
                f"{tech_id}: advanced exhibit missing: {tech['advanced_example']}"
            )
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        # A reference exhibit must not emit a success receipt that downstream
        # systems could mistake for execution proof.
        if tech["evidence_state"] == "illustrative" and re.search(
            r"[\"']status[\"']\s*:\s*[\"']VERIFIED", text, re.IGNORECASE
        ):
            errors.append(f"{tech_id}: illustrative exhibit emits VERIFIED status")

        promotion = contract.get("promotion_requirements", {})
        if promotion:
            minimum = promotion.get("minimum_evidence_state")
            required_runtime = promotion.get("required_source_patterns", [])
            if minimum not in EVIDENCE_RANK:
                errors.append(
                    f"{tech_id}: promotion gate has unknown minimum evidence state"
                )
            elif (
                EVIDENCE_RANK.get(tech["evidence_state"], -1) >= EVIDENCE_RANK[minimum]
            ):
                for pattern in required_runtime:
                    if not re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
                        errors.append(
                            f"{tech_id}: promotion gate missing runtime proof {pattern!r}"
                        )

        substantive = [
            line
            for line in text.splitlines()
            if line.strip() and not line.lstrip().startswith(("//", "#", ";;", "--"))
        ]
        if len(substantive) < 8:
            errors.append(
                f"{tech_id}: advanced exhibit has only {len(substantive)} substantive lines"
            )
        if easy.is_file() and easy.read_bytes() == path.read_bytes():
            errors.append(f"{tech_id}: easy and advanced exhibits are identical")
        for pattern in PLACEHOLDERS:
            if pattern.search(text):
                errors.append(
                    f"{tech_id}: advanced exhibit contains placeholder pattern {pattern.pattern!r}"
                )
        if not Path(tech["advanced_example"]).name.startswith("advanced_"):
            errors.append(
                f"{tech_id}: advanced exhibit filename must start with advanced_"
            )

        for source_pattern in contract["required_source_patterns"]:
            if not re.search(source_pattern, text, re.IGNORECASE | re.MULTILINE):
                errors.append(
                    f"{tech_id}: advanced exhibit does not satisfy required source pattern {source_pattern!r}"
                )
        for forbidden_pattern in contract["forbidden_claim_patterns"]:
            if _forbidden_positive_claim(text, forbidden_pattern):
                errors.append(
                    f"{tech_id}: advanced exhibit makes forbidden positive claim {forbidden_pattern!r}"
                )

        toolchain = tech["toolchain"]
        state = tech["evidence_state"]
        if state == "tested" and not toolchain.get("test"):
            errors.append(f"{tech_id}: tested evidence requires a test command")
        if state in {"compiles", "formally_verified"} and not toolchain.get("build"):
            errors.append(f"{tech_id}: {state} evidence requires a build/proof command")
        if state in {"hardware_gated", "toolchain_gated", "service_gated"}:
            if not (tech["execution"].get("hardware_gate") or toolchain.get("tool")):
                errors.append(
                    f"{tech_id}: gated exhibit lacks an exact blocker surface"
                )

        rows.append(
            {
                "id": tech_id,
                "technology": tech["name"],
                "advanced_exhibit": tech["advanced_example"],
                "architectural_role": tech["where"],
                "activation_condition": tech["when"],
                "signature_innovation": contract["signature_innovation"],
                "proof_surface": contract["proof_surface"],
                "source_assertions": contract["required_source_patterns"],
                "expected_failure_cases": contract["expected_failure_cases"],
                "required_receipt_fields": contract["required_receipt_fields"],
                "forbidden_claim_patterns": contract["forbidden_claim_patterns"],
                "evidence_state": state,
                "proof_class": tech["proof_class"],
                "maturity_tier": classify(tech),
                "evidence_tier": classify(tech),
                "promotion_gate": contract.get("promotion_requirements", {}),
                "interfaces": tech["interfaces"],
                "claim_boundary": registry.claim_contract_metadata[
                    "global_claim_boundary"
                ],
            }
        )

    atlas = {
        "schema_version": 2,
        "authority": [
            "registry/tower.yml",
            "registry/advanced-claim-contracts.json",
        ],
        "generated_by": "tools/audit_advanced_exhibits.py",
        "advanced_exhibit_count": len(rows),
        "all_profiles_present": len(rows) == len(contracts),
        "all_claim_contracts_present": len(rows) == len(contracts),
        "claim_contract_schema": registry.claim_contract_metadata.get("schema_version"),
        "exhibits": rows,
    }
    return errors, atlas


def markdown(atlas: dict) -> str:
    lines = [
        "# Advanced Exhibit Atlas",
        "",
        "> A generated map of the engineering boundary, source assertions, failure cases, proof surface, and truthful claim limit for every advanced Tower exhibit.",
        "",
        "The Atlas is generated from `registry/tower.yml` and `registry/advanced-claim-contracts.json`. It exposes operational implementation choices without converting simulations into execution proof or unsupported novelty claims.",
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
    lines.extend(
        [
            "",
            "## Machine-enforced claim contract",
            "",
            "Every row is backed by registry-owned source patterns, expected failure cases, required receipt fields, and forbidden positive claims. The audit checks the source patterns and rejects unsupported positive claims while permitting explicit disclaimers and claim boundaries.",
            "",
            "## Promotion standard",
            "",
            "An exhibit is admitted to operations only when it owns a meaningful boundary, rejects invalid or unsafe states, exposes an observable result, and carries executable proof or an exact environmental blocker. Concept-only references are never eligible for runtime selection. File size, exotic syntax, and dramatic naming are not evidence.",
            "",
            "## Originality boundary",
            "",
            "The Tower highlights **distinctive synthesis**: original combinations of governance, receipts, bounded execution, cross-language interfaces, and proof surfaces. It does not claim that a standard algorithm, language feature, or architecture was invented here unless independently documented evidence supports that claim.",
            "",
        ]
    )
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
        if (
            not json_path.is_file()
            or json_path.read_text(encoding="utf-8") != json_content
        ):
            errors.append("quality/advanced_exhibit_atlas.json is missing or stale")
        if not md_path.is_file() or md_path.read_text(encoding="utf-8") != md_content:
            errors.append("ADVANCED_EXHIBITS.md is missing or stale")
    if errors:
        print("\n".join(errors))
        return 1
    print(
        f"Advanced exhibit audit verified {atlas['advanced_exhibit_count']} exhibits."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
