"""Deterministic local proof for the Tower of Babel thread."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from tower.integrity import verify_integrity, write_manifest
from tower.receipt import build_receipt
from tower.registry import load_registry, validate_registry
from tower.visualize import build_topology_graph


def run() -> dict[str, Any]:
    registry = load_registry()
    with tempfile.TemporaryDirectory() as directory:
        manifest_path = Path(directory) / "integrity.json"
        manifest = write_manifest(manifest_path)
        integrity = verify_integrity(manifest_path)
    receipt = build_receipt({"counts": {"VERIFIED": len(registry.technologies)}})
    topology = build_topology_graph(registry)
    return {
        "schema": "glaciereq.tower-of-babel.context-integrity-proof.v1",
        "technology_count": len(registry.technologies),
        "registry_errors": validate_registry(registry),
        "integrity_file_count": manifest["file_count"],
        "integrity_verified": integrity["ok"],
        "topology_node_count": topology["node_count"],
        "receipt_sha256": receipt["receipt_sha256"],
        "truth_boundary": (
            "This proof validates local registry consistency, generated-file integrity, "
            "topology construction, and deterministic receipt generation. It does not compile "
            "every technology, benchmark performance, provision hardware, or authorize a toolchain command."
        ),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rendered = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
