#!/usr/bin/env python3
"""Canonical Tower registry, generator, integrity engine, and CLI.

The registry source is ``registry/tower.yml``. The file is JSON-formatted YAML so
the Tower has a dependency-free parser while remaining compatible with YAML
tooling.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "registry" / "tower.yml"
INTEGRITY_PATH = REPO_ROOT / ".integrity" / "file_hashes.json"
GENERATED_DIR = REPO_ROOT / "generated"

EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
}
EXCLUDED_FILES = {
    ".integrity/file_hashes.json",
    "generated/integrity_receipt.json",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".swp"}


@dataclass(frozen=True)
class TowerValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


class TowerRegistry:
    def __init__(self, root: Path | str = REPO_ROOT) -> None:
        self.root = Path(root).resolve()
        self.registry_path = self.root / "registry" / "tower.yml"
        self.data = self._load_registry()
        self.technologies = self.data["technologies"]

    def _load_registry(self) -> dict[str, Any]:
        raw = self.registry_path.read_text(encoding="utf-8")
        return json.loads(raw)

    @property
    def expected_count(self) -> int:
        return int(self.data["tower"]["expected_technologies"])

    @property
    def actual_count(self) -> int:
        return len(self.technologies)

    @property
    def total_exhibits(self) -> int:
        return sum(len(tech.get("examples", {})) for tech in self.technologies)

    def technology_ids(self) -> list[str]:
        return [tech["id"] for tech in self.technologies]

    def get(self, tech_id: str) -> dict[str, Any] | None:
        needle = tech_id.lower()
        for tech in self.technologies:
            if tech["id"].lower() == needle or tech["name"].lower() == needle:
                return tech
        return None

    def validate(self, *, require_files: bool = True) -> TowerValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        if self.data.get("schema_version") != "tower-registry/1":
            errors.append("registry schema_version must be tower-registry/1")

        if self.actual_count != self.expected_count:
            errors.append(f"expected {self.expected_count} technologies, found {self.actual_count}")

        seen_ids: set[str] = set()
        seen_paths: set[str] = set()
        allowed_states = set(self.data["evidence_states"].keys())
        allowed_types = set(self.data["technology_types"])

        for tech in self.technologies:
            tech_id = tech.get("id", "")
            if tech_id in seen_ids:
                errors.append(f"duplicate technology id: {tech_id}")
            seen_ids.add(tech_id)

            if tech.get("technology_type") not in allowed_types:
                errors.append(f"{tech_id}: unknown technology_type {tech.get('technology_type')!r}")

            for kind in ("easy", "advanced"):
                example = tech.get("examples", {}).get(kind)
                if not example:
                    errors.append(f"{tech_id}: missing {kind} example")
                    continue

                state = example.get("evidence_state")
                if state not in allowed_states:
                    errors.append(f"{tech_id}: {kind} example has unknown evidence_state {state!r}")

                rel = example.get("path")
                if not rel:
                    errors.append(f"{tech_id}: {kind} example missing path")
                    continue
                if rel in seen_paths:
                    warnings.append(f"example path reused: {rel}")
                seen_paths.add(rel)

                if require_files and not (self.root / rel).is_file():
                    errors.append(f"{tech_id}: missing {kind} example file {rel}")

            toolchain = tech.get("toolchain", {})
            if toolchain.get("version") == "unpinned":
                warnings.append(f"{tech_id}: toolchain version is not pinned yet")

        return TowerValidationResult(ok=not errors, errors=errors, warnings=warnings)

    def readme_matrix(self) -> str:
        lines = [
            "| # | Technology | Type | Category / Paradigm | Primary Domain | Easy Example | Advanced Exhibit | Evidence |",
            "| :--: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
        for tech in self.technologies:
            easy = tech["examples"]["easy"]
            advanced = tech["examples"]["advanced"]
            lines.append(
                f"| {tech['ordinal']} | **{tech['name']} (`{tech['extension']}`)** | "
                f"{tech['technology_type']} | {tech['category']} | {tech['primary_domain']} | "
                f"[{Path(easy['path']).name}]({easy['path']}) | "
                f"[{Path(advanced['path']).name}]({advanced['path']}) | "
                f"{advanced['evidence_state']} |"
            )
        return "\n".join(lines) + "\n"

    def runtime_registry_module(self) -> str:
        payload = {
            tech["id"]: {
                "name": tech["name"],
                "extension": tech["extension"],
                "what": tech["w4h"]["what"],
                "where": tech["w4h"]["where"],
                "when": tech["w4h"]["when"],
                "why": tech["w4h"]["why"],
                "how": tech["w4h"]["how"],
                "technology_type": tech["technology_type"],
                "advanced_evidence_state": tech["examples"]["advanced"]["evidence_state"],
            }
            for tech in self.technologies
        }
        return (
            "# Auto-generated from registry/tower.yml by src/tower_registry.py.\n"
            "# Do not hand-edit counts here.\n"
            "BABEL_REGISTRY_DATA = "
            + json.dumps(payload, indent=2, sort_keys=True)
            + "\n"
        )

    def release_artifact(self) -> dict[str, Any]:
        validation = self.validate(require_files=False)
        return {
            "schema_version": "tower-release/1",
            "generated_at": "deterministic-from-registry",
            "repository": self.data["repository"],
            "registry_sha256": sha256_path(self.registry_path),
            "technology_count": self.actual_count,
            "exhibit_count": self.total_exhibits,
            "technology_ids": self.technology_ids(),
            "evidence_state_counts": evidence_state_counts(self.technologies),
            "validation": {
                "ok": validation.ok,
                "errors": validation.errors,
                "warnings": validation.warnings,
            },
        }

    def megamind_graph(self) -> dict[str, Any]:
        nodes = []
        edges = []
        for tech in self.technologies:
            nodes.append({
                "id": tech["id"],
                "label": tech["name"],
                "type": tech["technology_type"],
                "domain": tech["primary_domain"],
                "evidence_state": tech["examples"]["advanced"]["evidence_state"],
            })
            for contract in tech.get("interop_contracts", []):
                edges.append({"from": tech["id"], **contract})
        return {
            "schema_version": "tower-megamind-technology-graph/1",
            "source_registry": str(self.registry_path.relative_to(self.root)),
            "nodes": nodes,
            "edges": edges,
        }


def evidence_state_counts(technologies: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for tech in technologies:
        state = tech["examples"]["advanced"]["evidence_state"]
        counts[state] = counts.get(state, 0) + 1
    return dict(sorted(counts.items()))


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_repo_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        parts = set(Path(rel).parts)
        if parts & EXCLUDED_DIRS:
            continue
        if rel in EXCLUDED_FILES:
            continue
        if path.suffix in EXCLUDED_SUFFIXES:
            continue
        yield path


def generate_integrity_manifest(root: Path = REPO_ROOT) -> dict[str, Any]:
    registry_path = root / "registry" / "tower.yml"
    hashes = {
        path.relative_to(root).as_posix(): sha256_path(path)
        for path in iter_repo_files(root)
    }
    return {
        "schema_version": "tower-integrity/1",
        "generated_by": "tower integrity generate",
        "registry_source": "registry/tower.yml",
        "registry_sha256": sha256_path(registry_path) if registry_path.exists() else None,
        "file_count": len(hashes),
        "hashes": hashes,
    }


def verify_integrity(root: Path = REPO_ROOT) -> dict[str, Any]:
    integrity_path = root / ".integrity" / "file_hashes.json"
    if not integrity_path.exists():
        return {"ok": False, "errors": ["missing .integrity/file_hashes.json"], "missing": [], "changed": [], "extra": []}

    manifest = json.loads(integrity_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    missing: list[str] = []
    changed: list[str] = []
    hashes = manifest.get("hashes", {})

    for rel, expected in sorted(hashes.items()):
        path = root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        actual = sha256_path(path)
        if actual != expected:
            changed.append(rel)

    current = set(generate_integrity_manifest(root)["hashes"].keys())
    listed = set(hashes.keys())
    extra = sorted(current - listed)

    if manifest.get("schema_version") != "tower-integrity/1":
        errors.append("integrity manifest schema_version must be tower-integrity/1")
    if manifest.get("file_count") != len(hashes):
        errors.append("integrity manifest file_count does not match hashes length")

    return {
        "ok": not errors and not missing and not changed,
        "errors": errors,
        "missing": missing,
        "changed": changed,
        "extra": extra,
        "checked": len(hashes),
    }


def write_generated_outputs(root: Path = REPO_ROOT) -> list[str]:
    registry = TowerRegistry(root)
    generated = root / "generated"
    generated.mkdir(exist_ok=True)

    outputs = {
        "generated/tower_matrix.md": registry.readme_matrix(),
        "src/generated_babel_registry.py": registry.runtime_registry_module(),
        "generated/tower_release.json": json.dumps(registry.release_artifact(), indent=2, sort_keys=True) + "\n",
        "generated/megamind_technology_graph.json": json.dumps(registry.megamind_graph(), indent=2, sort_keys=True) + "\n",
    }

    written: list[str] = []
    for rel, content in outputs.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(rel)
    return written


def git_commit_sha(root: Path = REPO_ROOT) -> str | None:
    env_sha = os.environ.get("GITHUB_SHA")
    if env_sha:
        return env_sha
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        return None


def make_receipt(root: Path = REPO_ROOT) -> dict[str, Any]:
    registry = TowerRegistry(root)
    verification = verify_integrity(root)
    validation = registry.validate()
    return {
        "schema_version": "tower-receipt/1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "commit_sha": git_commit_sha(root),
        "registry_sha256": sha256_path(registry.registry_path),
        "technology_count": registry.actual_count,
        "exhibit_count": registry.total_exhibits,
        "validation_ok": validation.ok,
        "integrity_ok": verification["ok"],
        "validation": {"errors": validation.errors, "warnings": validation.warnings},
        "integrity": verification,
    }


def command_validate(args: argparse.Namespace) -> int:
    result = TowerRegistry().validate(require_files=not args.no_files)
    print(json.dumps(result.__dict__, indent=2, sort_keys=True))
    return 0 if result.ok else 2


def command_report(_: argparse.Namespace) -> int:
    registry = TowerRegistry()
    print(json.dumps(registry.release_artifact(), indent=2, sort_keys=True))
    return 0


def command_generate(_: argparse.Namespace) -> int:
    written = write_generated_outputs()
    print(json.dumps({"written": written}, indent=2, sort_keys=True))
    return 0


def command_integrity(args: argparse.Namespace) -> int:
    if args.action == "generate":
        manifest = generate_integrity_manifest()
        INTEGRITY_PATH.parent.mkdir(exist_ok=True)
        INTEGRITY_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"written": str(INTEGRITY_PATH), "file_count": manifest["file_count"]}, indent=2))
        return 0
    if args.action == "verify":
        result = verify_integrity()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["ok"] else 2
    if args.action == "diff":
        current = json.dumps(generate_integrity_manifest(), indent=2, sort_keys=True).splitlines()
        committed = INTEGRITY_PATH.read_text(encoding="utf-8").splitlines() if INTEGRITY_PATH.exists() else []
        print("\n".join(difflib.unified_diff(committed, current, fromfile="committed", tofile="current", lineterm="")))
        return 0
    if args.action == "receipt":
        receipt = make_receipt()
        target = GENERATED_DIR / "integrity_receipt.json"
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        return 0 if receipt["validation_ok"] and receipt["integrity_ok"] else 2
    raise AssertionError(args.action)


def command_build(args: argparse.Namespace) -> int:
    registry = TowerRegistry()
    rows = []
    for tech in registry.technologies:
        cmd = tech["toolchain"].get("build_command")
        rows.append({
            "technology": tech["id"],
            "state": "configured" if cmd else "hardware_unavailable" if tech["toolchain"].get("expected_hardware") != "none" else "not_configured",
            "command": cmd,
            "reason": "P0 registry created; P1 pins toolchains and enables per-floor builds." if not cmd else None,
        })
    print(json.dumps({"mode": args.target, "results": rows}, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tower", description="Tower of Babel governance CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate")
    validate.add_argument("--no-files", action="store_true")
    validate.set_defaults(func=command_validate)

    report = sub.add_parser("report")
    report.set_defaults(func=command_report)

    generate = sub.add_parser("generate")
    generate.set_defaults(func=command_generate)

    integrity = sub.add_parser("integrity")
    integrity.add_argument("action", choices=["generate", "verify", "diff", "receipt"])
    integrity.set_defaults(func=command_integrity)

    build = sub.add_parser("build")
    build.add_argument("--all", dest="target", action="store_const", const="all", default="all")
    build.set_defaults(func=command_build)

    test = sub.add_parser("test")
    test.add_argument("--all", dest="target", action="store_const", const="all", default="all")
    test.set_defaults(func=command_build)

    benchmark = sub.add_parser("benchmark")
    benchmark.add_argument("--available", dest="target", action="store_const", const="available", default="available")
    benchmark.set_defaults(func=command_build)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
