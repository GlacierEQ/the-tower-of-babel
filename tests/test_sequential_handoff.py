import pytest
from tower.sequential_handoff import build_handoff

def test_deterministic_evidence_bound_handoff():
    steps = [{"stage": "recover", "status": "passed", "evidence": "commit abc"},
             {"stage": "implement", "status": "pending"}]
    assert build_handoff("M-1", "abc", steps) == build_handoff("M-1", "abc", steps)
    assert build_handoff("M-1", "abc", steps)["steps"][1]["evidence"] == ""

@pytest.mark.parametrize("steps", [
    [{"stage": "test", "status": "passed"}],
    [{"stage": "test", "status": "passed", "evidence": "x"}, {"stage": "recover", "status": "pending"}],
    [{"stage": "recover", "status": "pending"}, {"stage": "recover", "status": "pending"}],
    [{"stage": "recover", "status": "done"}],
])
def test_invalid_steps_rejected(steps):
    with pytest.raises(ValueError):
        build_handoff("M-1", "abc", steps)
