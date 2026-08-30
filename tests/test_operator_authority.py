from tower.activation import ActivationMode, resolve_activation


def executable_technology() -> dict:
    return {
        "id": "python",
        "toolchain": {"tool": "python"},
        "execution": {"ci_tier": "portable"},
        "interfaces": ["mission-v1"],
        "evidence_state": "tested",
        "proof_class": "behavioral",
    }


def test_external_effects_require_operator_scope_not_secondary_approval():
    decision = resolve_activation(
        executable_technology(),
        ActivationMode.EXECUTE,
        external_effects=True,
    )
    assert decision.allowed is False
    assert decision.reason == "external-effects-require-operator-scope-authorization"
    assert decision.blocked_capabilities == ("external-effects",)


def test_operator_scope_authorizes_external_execution_boundary():
    decision = resolve_activation(
        executable_technology(),
        ActivationMode.EXECUTE,
        external_effects=True,
        operator_scope_authorized=True,
    )
    assert decision.allowed is True
    assert decision.effective_mode is ActivationMode.EXECUTE
    assert decision.reason == "operator-scoped-external-execution-boundary-present"


def test_operator_scope_does_not_bypass_technical_prerequisites():
    technology = executable_technology()
    technology["toolchain"] = {}
    decision = resolve_activation(
        technology,
        ActivationMode.EXECUTE,
        external_effects=True,
        operator_scope_authorized=True,
    )
    assert decision.allowed is False
    assert decision.reason == "execution-boundary-incomplete"
    assert "toolchain.tool" in decision.required_proof


def test_operator_scope_does_not_bypass_promotion_evidence():
    technology = executable_technology()
    technology["evidence_state"] = "illustrative"
    technology["proof_class"] = "illustrative"
    decision = resolve_activation(
        technology,
        ActivationMode.PROMOTE,
        external_effects=True,
        operator_scope_authorized=True,
    )
    assert decision.allowed is False
    assert decision.reason == "promotion-requires-earned-evidence"


def test_local_execution_stays_available_without_redundant_authorization():
    decision = resolve_activation(executable_technology(), ActivationMode.EXECUTE)
    assert decision.allowed is True
    assert decision.reason == "declared-execution-boundary-present"


def test_inspection_remains_available_even_with_external_effect_flag():
    decision = resolve_activation(
        executable_technology(),
        ActivationMode.INSPECT,
        external_effects=True,
    )
    assert decision.allowed is True
    assert decision.reason == "inspection-is-always-available"
