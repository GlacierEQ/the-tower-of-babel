"""Wasm + Lean formal placement floor — W4H boundary inventory.

Does not claim every language builds or that Lean proofs are verified here.
It *does* inventory governed floors (Lean4 + WAT) and refuse empty formal floors
masquerading as VERIFIED.

Mechanism: engineered_first_class / formal floor for polyglot placement
(Library of Links: Wasm Core Spec + Lean 4 Manual).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Honest plane labels for this module's own claims
PLANE_IMPLEMENTED = "IMPLEMENTED"  # inventory + refuse paths exist
PLANE_VERIFIED = "VERIFIED"  # only when external proof harness says so (not this module)

LEAN_PATHS: tuple[str, ...] = (
    "languages/lean4/easy_logic.lean",
    "languages/lean4/advanced_truth_gate_proof.lean",
    "lakefile.lean",
    "lean-toolchain",
)

WAT_PATHS: tuple[str, ...] = (
    "languages/wat/easy_add.wat",
    "languages/wat/advanced_wasm_sandbox.wat",
)


@dataclass(frozen=True)
class FloorArtifact:
    path: str
    present: bool
    non_empty: bool
    bytes: int


@dataclass(frozen=True)
class FormalWasmFloor:
    lean: tuple[FloorArtifact, ...]
    wat: tuple[FloorArtifact, ...]
    lean_complete: bool
    wat_complete: bool
    complete: bool
    missing: tuple[str, ...]
    plane: str
    boundary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "lean": [a.__dict__ for a in self.lean],
            "wat": [a.__dict__ for a in self.wat],
            "lean_complete": self.lean_complete,
            "wat_complete": self.wat_complete,
            "complete": self.complete,
            "missing": list(self.missing),
            "plane": self.plane,
            "boundary": self.boundary,
            "claim": (
                "Formal/Wasm floors are present as placement exhibits; "
                "do not treat presence as machine-checked VERIFIED proof without harness."
            ),
        }


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _artifact(base: Path, rel: str) -> FloorArtifact:
    path = base / rel
    if not path.is_file():
        return FloorArtifact(path=rel, present=False, non_empty=False, bytes=0)
    data = path.read_bytes()
    return FloorArtifact(
        path=rel,
        present=True,
        non_empty=len(data.strip()) > 0,
        bytes=len(data),
    )


def inventory_formal_wasm_floor(root: Path | None = None) -> FormalWasmFloor:
    base = root or repository_root()
    lean = tuple(_artifact(base, p) for p in LEAN_PATHS)
    wat = tuple(_artifact(base, p) for p in WAT_PATHS)
    missing = [a.path for a in lean + wat if not a.present or not a.non_empty]
    lean_complete = all(a.present and a.non_empty for a in lean)
    wat_complete = all(a.present and a.non_empty for a in wat)
    complete = lean_complete and wat_complete
    return FormalWasmFloor(
        lean=lean,
        wat=wat,
        lean_complete=lean_complete,
        wat_complete=wat_complete,
        complete=complete,
        missing=tuple(missing),
        plane=PLANE_IMPLEMENTED if complete else "TARGET",
        boundary="placement_inventory_not_machine_checked_verification",
    )


def refuse_empty_formal_claim(
    root: Path | None = None,
    *,
    claimed_verified: bool = False,
) -> tuple[bool, str | None]:
    """Fail closed if formal floors missing, or if VERIFIED claimed without inventory."""
    floor = inventory_formal_wasm_floor(root)
    if not floor.complete:
        return False, f"formal_wasm_floor_incomplete:{','.join(floor.missing)}"
    if claimed_verified:
        # This module never grants VERIFIED — external harness required
        return False, "verified_requires_external_proof_harness"
    return True, None


def placement_contract_snippet() -> dict[str, Any]:
    """W4H-style placement note for Babel governance docs/tools."""
    return {
        "lanes": {
            "lean4": {
                "owns": "machine-checked invariants / formal floor exhibits",
                "proof_class": "formal",
                "paths": list(LEAN_PATHS),
            },
            "wat_wasm": {
                "owns": "sandboxed portable execution boundary exhibits",
                "proof_class": "build_or_validate",
                "paths": list(WAT_PATHS),
            },
        },
        "law": "Language earns place only with boundary + contract + proof path",
        "anti_pattern": "polyglot theater without floors",
    }


def write_receipt(root: Path | None = None, path: Path | None = None) -> Path:
    base = root or repository_root()
    floor = inventory_formal_wasm_floor(base)
    out = path or (base / "receipts" / "formal_wasm_floor_proof.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "glaciereq.babel.formal-wasm-floor.v1",
        "mechanism_id": "engineered_first_class",
        "companion": "wasm_lean_placement",
        "floor": floor.to_dict(),
        "placement": placement_contract_snippet(),
        "ok": floor.complete,
    }
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
