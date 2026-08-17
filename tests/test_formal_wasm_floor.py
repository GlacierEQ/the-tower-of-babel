from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tower.formal_wasm_floor import (  # noqa: E402
    inventory_formal_wasm_floor,
    refuse_empty_formal_claim,
    write_receipt,
)


def test_inventory_complete() -> None:
    floor = inventory_formal_wasm_floor(ROOT)
    assert floor.lean_complete, floor.missing
    assert floor.wat_complete, floor.missing
    assert floor.complete
    assert floor.plane == "IMPLEMENTED"


def test_refuse_verified_without_harness() -> None:
    ok, reason = refuse_empty_formal_claim(ROOT, claimed_verified=True)
    assert ok is False
    assert reason == "verified_requires_external_proof_harness"


def test_refuse_amputated_floor(tmp_path: Path) -> None:
    ok, reason = refuse_empty_formal_claim(tmp_path)
    assert ok is False
    assert reason and reason.startswith("formal_wasm_floor_incomplete")


def test_receipt_writes() -> None:
    path = write_receipt(ROOT)
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert "formal_wasm_floor" in text or "engineered_first_class" in text
    assert "lean4" in text
    assert "wat" in text
