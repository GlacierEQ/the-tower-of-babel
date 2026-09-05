from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

from tower.registry import REPO_ROOT, load_registry


# --- Unit-level checks of the vendored Genius Logic engine -------------------

def _engine_module():
    import importlib.util

    path = REPO_ROOT / "flagship" / "python" / "genius_logic.py"
    spec = importlib.util.spec_from_file_location("flagship_genius_logic", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["flagship_genius_logic"] = module  # required for frozen __future__ dataclasses
    spec.loader.exec_module(module)
    return module


def test_genius_logic_adversary_refutes_contradictory_claim():
    gl = _engine_module()
    engine = gl.LogicEngine()
    # `coherent` is the claim under test; `coverage_violation` is an established
    # TRUE fact that contradicts it, so the adversary must refute the claim.
    engine.add(gl.Proposition("coherent", "plan is coherent", "unknown", contradicts=["coverage_violation"]))
    engine.add(gl.Proposition("coverage_violation", "a capability is uncovered", "true", contradicts=["coherent"]))
    verdict = engine.adversary("coherent")
    assert verdict.refuted is True
    assert "coverage_violation" in verdict.challengers


def test_genius_logic_fixpoint_propagates_true():
    gl = _engine_module()
    engine = gl.LogicEngine()
    engine.add(gl.Proposition("base", "root fact", "true"))
    engine.add(gl.Proposition("derived", "consequence", "unknown"))
    engine.add(gl.Proposition("level2", "second consequence", "unknown"))
    engine.add_rule("base", "derived")
    engine.add_rule("derived", "level2")
    engine.derive()
    assert engine.props["base"].truth == "true"
    assert engine.props["derived"].truth == "true"
    assert engine.props["level2"].truth == "true"


def test_genius_logic_contradiction_detector_catches_both_true():
    gl = _engine_module()
    engine = gl.LogicEngine()
    engine.add(gl.Proposition("a", "a is true", "true", contradicts=["b"]))
    engine.add(gl.Proposition("b", "b is true", "true", contradicts=["a"]))
    hits = engine.contradictions()
    assert ("a", "b") in hits or ("b", "a") in hits


# --- Integration-level check of the Genius Mastery stage ---------------------

def _run_planner(tmp_path: Path) -> Path:
    source = REPO_ROOT / "flagship" / "mission.input.json"
    mission = tmp_path / "mission.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["input_sha256"] = "0" * 64
    mission.write_text(json.dumps(payload), encoding="utf-8")
    plan = tmp_path / "plan.json"
    completed = subprocess.run(
        [sys.executable, str(REPO_ROOT / "flagship/python/planner.py"), str(mission), str(plan)],
        cwd=REPO_ROOT, text=True, capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return plan


def test_genius_mastery_verdicts_on_canonical_mission(tmp_path, monkeypatch):
    monkeypatch.delenv("APEX_MEGA_ENABLED", raising=False)
    plan = _run_planner(tmp_path)
    report = tmp_path / "genius_report.json"
    mission = REPO_ROOT / "flagship" / "mission.input.json"

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "flagship/python/genius_mastery.py"),
            str(plan), str(report), "--mission", str(mission),
        ],
        cwd=REPO_ROOT, text=True, capture_output=True, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    parsed = json.loads(completed.stdout)
    assert parsed["stage"] == "genius_mastery"
    assert parsed["status"] == "VERIFIED", parsed
    assert parsed["coherent"] is True
    assert parsed["capability_coverage"] == "true"
    assert parsed["proof_floor"] == "true"
    assert parsed["interface_composition"] == "true"
    assert parsed["no_gated_selection"] == "true"
    assert set(parsed["preferred_interfaces_covered"]) >= {"protobuf", "jsonrpc"}
    assert parsed["adversary"]["refuted"] is False
    assert parsed["contradictions"] == []
    assert parsed["mega_skills"]["enabled"] is False
    assert parsed["mega_skills"]["status"] == "SKIPPED"
    assert report.is_file()
    on_disk = json.loads(report.read_text(encoding="utf-8"))
    assert on_disk["status"] == "VERIFIED"
    assert on_disk["tower_registry_sha256"] == json.loads(plan.read_text(encoding="utf-8"))["tower_registry_sha256"]


def test_genius_mastery_detects_gated_selection_incoherence(tmp_path, monkeypatch):
    monkeypatch.delenv("APEX_MEGA_ENABLED", raising=False)
    plan = _run_planner(tmp_path)
    plan_obj = json.loads(plan.read_text(encoding="utf-8"))
    # Inject a gated technology as a false "selected" entry to force the
    # no_gated_selection failure mode, which must refute coherence.
    gated_id = next(iter(plan_obj["gated_candidates"]), None)
    if gated_id is None:
        pytest.skip("canonical mission has no gated candidates to inject")
    plan_obj["technology_ids"].append(gated_id)
    bad_plan = tmp_path / "bad_plan.json"
    bad_plan.write_text(json.dumps(plan_obj), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "flagship/python/genius_mastery.py"),
            str(bad_plan), str(tmp_path / "genius_report.json"),
        ],
        cwd=REPO_ROOT, text=True, capture_output=True, check=False,
    )
    parsed = json.loads(completed.stdout)
    assert parsed["status"] == "FAILED", parsed
    assert parsed["coherent"] is False
    assert parsed["no_gated_selection"] == "false"
    assert parsed["adversary"]["refuted"] is True
    assert completed.returncode == 1
