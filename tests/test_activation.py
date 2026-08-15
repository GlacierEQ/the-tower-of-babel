from tower.activation import ActivationMode, activate_execution, activation_surface, resolve_activation


def technology(**overrides):
    row = {
        "id": "python",
        "interfaces": ["stdout-json"],
        "toolchain": {"tool": "python3", "reference_pin": "system"},
        "execution": {"ci_tier": "portable"},
        "evidence_state": "tested",
        "proof_class": "behavioral",
    }
    row.update(overrides)
    return row


def test_declared_boundaries_restore_local_execution():
    decision = resolve_activation(technology(), ActivationMode.EXECUTE)
    assert decision.allowed is True
    assert decision.effective_mode is ActivationMode.EXECUTE


def test_activation_is_real_not_planning_only(monkeypatch):
    observed = {}

    def fake_build_floor(row):
        observed.update(row)
        return {"technology_id": row["id"], "status": "VERIFIED"}

    import tower.build
    monkeypatch.setattr(tower.build, "build_floor", fake_build_floor)
    result = activate_execution(technology())
    assert result["status"] == "VERIFIED"
    assert observed["id"] == "python"
    assert result["activation"]["governance"] == "shaping-and-audit"


def test_governance_still_controls_promotion():
    decision = resolve_activation(technology(evidence_state="illustrative"), ActivationMode.PROMOTE)
    assert decision.allowed is False
    assert decision.effective_mode is ActivationMode.EXECUTE
    assert "earned-evidence" in decision.reason


def test_external_effects_are_never_implicit():
    decision = resolve_activation(technology(), ActivationMode.EXECUTE, external_effects=True)
    assert decision.allowed is False
    assert "external-effects" in decision.blocked_capabilities
    assert activate_execution(technology(), external_effects=True)["status"] == "ACTIVATION_BLOCKED"


def test_surface_exposes_power_and_blockers():
    surface = activation_surface(technology())
    assert set(surface["available"]) == {"inspect", "compose", "execute", "promote"}
    assert all("reason" in item for item in surface["decisions"])
