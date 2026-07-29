#!/usr/bin/env python3
"""Generate every derived Tower of Babel artifact from registry/languages.json.

Usage:
    python tools/generate.py
    python tools/generate.py --check
    python tools/generate.py --skip-file-validation
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "registry" / "languages.json"
README_PATH = ROOT / "README.md"

MATRIX_BEGIN = "<!-- BEGIN GENERATED:LANGUAGE_MATRIX -->"
MATRIX_END = "<!-- END GENERATED:LANGUAGE_MATRIX -->"
LINKS_BEGIN = "<!-- BEGIN GENERATED:LINK_LIBRARY -->"
LINKS_END = "<!-- END GENERATED:LINK_LIBRARY -->"


class ManifestError(ValueError):
    pass


def load_manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def validate_manifest(data: dict[str, Any], *, validate_files: bool = True) -> None:
    languages = data.get("languages")
    if not isinstance(languages, list) or not languages:
        raise ManifestError("languages must be a non-empty list")

    ids: set[str] = set()
    capability_ids: set[str] = set()
    required_w4h = {"what", "where", "when", "why", "how"}
    required_build = {"toolchain", "check", "run_easy", "run_advanced", "ci_tier"}

    for index, item in enumerate(languages, start=1):
        prefix = f"languages[{index}]"
        language_id = item.get("id")
        if not language_id or language_id in ids:
            raise ManifestError(f"{prefix}.id is missing or duplicated: {language_id!r}")
        ids.add(language_id)

        if set(item.get("w4h", {})) != required_w4h:
            raise ManifestError(f"{prefix}.w4h must contain exactly {sorted(required_w4h)}")
        if not required_build.issubset(item.get("build", {})):
            raise ManifestError(f"{prefix}.build is incomplete")
        if not item.get("interfaces"):
            raise ManifestError(f"{prefix}.interfaces must not be empty")

        links = item.get("links", [])
        if len(links) < 2:
            raise ManifestError(f"{prefix}.links must contain at least two references")
        for link in links:
            url = link.get("url", "")
            if not url.startswith("https://"):
                raise ManifestError(f"{prefix} contains a non-HTTPS link: {url}")

        smithery = item.get("smithery", {})
        if smithery.get("registration_status") not in {
            "declared-not-published", "published", "not-applicable"
        }:
            raise ManifestError(f"{prefix}.smithery.registration_status is invalid")

        spiral = item.get("spiral_engine", {})
        capability_id = spiral.get("capability_id")
        if not capability_id or capability_id in capability_ids:
            raise ManifestError(f"{prefix}.spiral_engine.capability_id is missing or duplicated")
        capability_ids.add(capability_id)

        maturity = item.get("maturity", {})
        allowed = set(data["policies"]["maturity_levels"])
        if maturity.get("level") not in allowed:
            raise ManifestError(f"{prefix}.maturity.level is invalid")
        if maturity.get("level") == "production" and len(maturity.get("promotion_gates", [])) < 5:
            raise ManifestError(f"{prefix} claims production without complete promotion gates")

        if validate_files:
            for kind in ("easy", "advanced"):
                path = ROOT / item["examples"][kind]
                if not path.is_file():
                    raise ManifestError(f"{prefix}.examples.{kind} does not exist: {path}")


def markdown_escape(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ")


def render_matrix(data: dict[str, Any]) -> str:
    header = [
        "| # | Language | Exact role | Maturity | Interfaces | Easy | Advanced | Primary docs |",
        "|---:|---|---|---|---|---|---|---|",
    ]
    rows = []
    for number, item in enumerate(data["languages"], start=1):
        interfaces = ", ".join(f"`{value}`" for value in item["interfaces"][:4])
        if len(item["interfaces"]) > 4:
            interfaces += f" +{len(item['interfaces']) - 4}"
        docs = item["links"][0]
        rows.append(
            "| {number} | **{name}** (`{extension}`) | {role} | `{maturity}` / {status} | "
            "{interfaces} | [easy]({easy}) | [advanced]({advanced}) | [{label}]({url}) |".format(
                number=number,
                name=markdown_escape(item["name"]),
                extension=item["extension"],
                role=markdown_escape(item["primary_domain"]),
                maturity=item["maturity"]["level"],
                status=markdown_escape(item["maturity"]["status"]),
                interfaces=interfaces,
                easy=item["examples"]["easy"],
                advanced=item["examples"]["advanced"],
                label=markdown_escape(docs["label"]),
                url=docs["url"],
            )
        )
    return "\n".join(header + rows)


def render_link_library(data: dict[str, Any]) -> str:
    blocks = [
        "## Generated per-language link library",
        "",
        "> Authored in `registry/languages.json`; regenerated by `tools/generate.py`.",
        "",
    ]
    for item in data["languages"]:
        blocks.append(f"### {item['name']} (`{item['id']}`)")
        blocks.append("")
        for link in item["links"]:
            blocks.append(f"- [{link['label']}]({link['url']}) — `{link['kind']}`")
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def render_python_registry(data: dict[str, Any]) -> str:
    payload_literal = repr(json.dumps(data["languages"], indent=2, ensure_ascii=False))
    template = """# GENERATED FILE — DO NOT EDIT.
# Source: registry/languages.json
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

_RAW_LANGUAGES = json.loads(__PAYLOAD_LITERAL__)


@dataclass(frozen=True)
class BabelLanguageSpec:
    id: str
    name: str
    extension: str
    category: str
    primary_domain: str
    what: str
    where: str
    when: str
    why: str
    how: str
    examples: dict[str, str]
    build: dict[str, str]
    interfaces: tuple[str, ...]
    maturity: dict[str, Any]
    links: tuple[dict[str, str], ...]
    smithery: dict[str, Any]
    spiral_engine: dict[str, Any]


def _to_spec(item: dict[str, Any]) -> BabelLanguageSpec:
    w4h = item["w4h"]
    return BabelLanguageSpec(
        id=item["id"],
        name=item["name"],
        extension=item["extension"],
        category=item["category"],
        primary_domain=item["primary_domain"],
        what=w4h["what"],
        where=w4h["where"],
        when=w4h["when"],
        why=w4h["why"],
        how=w4h["how"],
        examples=dict(item["examples"]),
        build=dict(item["build"]),
        interfaces=tuple(item["interfaces"]),
        maturity=dict(item["maturity"]),
        links=tuple(dict(link) for link in item["links"]),
        smithery=dict(item["smithery"]),
        spiral_engine=dict(item["spiral_engine"]),
    )


BABEL_REGISTRY: dict[str, BabelLanguageSpec] = {
    item["id"]: _to_spec(item) for item in _RAW_LANGUAGES
}
EXPECTED_LANGUAGE_IDS: tuple[str, ...] = tuple(BABEL_REGISTRY)


class BabelRegistryEngine:
    def get_spec(self, lang_key: str) -> dict[str, Any]:
        spec = BABEL_REGISTRY.get(lang_key.lower())
        if spec is None:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {
            "id": spec.id,
            "name": spec.name,
            "extension": spec.extension,
            "category": spec.category,
            "primary_domain": spec.primary_domain,
            "what": spec.what,
            "where": spec.where,
            "when": spec.when,
            "why": spec.why,
            "how": spec.how,
            "examples": dict(spec.examples),
            "build": dict(spec.build),
            "interfaces": list(spec.interfaces),
            "maturity": dict(spec.maturity),
            "links": [dict(link) for link in spec.links],
            "smithery": dict(spec.smithery),
            "spiral_engine": dict(spec.spiral_engine),
            "status": "VALIDATED_W4H_SPEC",
            "ok": True,
        }


if __name__ == "__main__":
    print(
        f"Tower of Babel Registry Initialized: {len(BABEL_REGISTRY)} "
        "manifest-governed languages registered."
    )
"""
    return template.replace("__PAYLOAD_LITERAL__", payload_literal)


def public_language(item: dict[str, Any], *keys: str) -> dict[str, Any]:
    return {"id": item["id"], "name": item["name"], **{key: item[key] for key in keys}}


def render_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def replace_section(document: str, begin: str, end: str, body: str) -> str:
    if document.count(begin) != 1 or document.count(end) != 1:
        raise ManifestError(f"README markers are missing or duplicated: {begin} / {end}")
    prefix, remainder = document.split(begin, 1)
    _, suffix = remainder.split(end, 1)
    return f"{prefix}{begin}\n{body.rstrip()}\n{end}{suffix}"


def generated_outputs(data: dict[str, Any]) -> dict[Path, str]:
    outputs: dict[Path, str] = {
        ROOT / "src" / "babel_registry.py": render_python_registry(data),
        ROOT / "generated" / "build_commands.json": render_json({
            "schema_version": data["schema_version"],
            "source": "registry/languages.json",
            "languages": [public_language(item, "build", "examples") for item in data["languages"]],
        }),
        ROOT / "generated" / "interfaces.json": render_json({
            "schema_version": data["schema_version"],
            "source": "registry/languages.json",
            "languages": [public_language(item, "interfaces") for item in data["languages"]],
        }),
        ROOT / "generated" / "maturity.json": render_json({
            "schema_version": data["schema_version"],
            "source": "registry/languages.json",
            "claim_rule": data["policies"]["claim_rule"],
            "languages": [public_language(item, "maturity") for item in data["languages"]],
        }),
        ROOT / "generated" / "smithery.registry.json": render_json({
            "schema_version": data["schema_version"],
            "source": "registry/languages.json",
            "publication_rule": data["policies"]["smithery_rule"],
            "capabilities": [
                {
                    "language_id": item["id"],
                    "language": item["name"],
                    **item["smithery"],
                    "interfaces": item["interfaces"],
                    "build_check": item["build"]["check"],
                }
                for item in data["languages"]
            ],
        }),
        ROOT / "generated" / "spiral-engine.registry.json": render_json({
            "schema_version": data["schema_version"],
            "source": "registry/languages.json",
            "activation_rule": data["policies"]["spiral_rule"],
            "capabilities": [
                {
                    "language_id": item["id"],
                    "language": item["name"],
                    **item["spiral_engine"],
                    "interfaces": item["interfaces"],
                    "maturity": item["maturity"]["level"],
                }
                for item in data["languages"]
            ],
        }),
        ROOT / "generated" / "link_library.md": render_link_library(data),
    }

    readme = README_PATH.read_text(encoding="utf-8")
    readme = replace_section(readme, MATRIX_BEGIN, MATRIX_END, render_matrix(data))
    readme = replace_section(
        readme,
        LINKS_BEGIN,
        LINKS_END,
        "The complete generated library lives at "
        "[`generated/link_library.md`](generated/link_library.md). "
        f"It contains {sum(len(item['links']) for item in data['languages'])} "
        "language-owned references.",
    )
    outputs[README_PATH] = readme
    return outputs


def write_outputs(outputs: dict[Path, str], *, check: bool) -> int:
    drift: list[str] = []
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            if check:
                drift.append(str(path.relative_to(ROOT)))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(expected, encoding="utf-8")
                print(f"generated {path.relative_to(ROOT)}")
    if drift:
        print("Generated artifacts are stale:", file=sys.stderr)
        for path in drift:
            print(f"  - {path}", file=sys.stderr)
        print("Run: python tools/generate.py", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail instead of writing drifted outputs.")
    parser.add_argument(
        "--skip-file-validation",
        action="store_true",
        help="Validate manifest structure without requiring example files (bootstrap only).",
    )
    args = parser.parse_args()

    data = load_manifest()
    validate_manifest(data, validate_files=not args.skip_file_validation)
    return write_outputs(generated_outputs(data), check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
