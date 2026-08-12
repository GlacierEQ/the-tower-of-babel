"""Regression tests for the Tower's canonical function-to-technology authority."""
from __future__ import annotations

from integrations.megamind.adapter import select_technologies as adapter_select
from tower.selector import TechnologyRequest, select_technologies


def test_cross_language_contract_selects_protobuf_as_proven_owner() -> None:
    result = select_technologies(
        TechnologyRequest(
            mission_id="contract-boundary",
            capabilities=("cross-language contract",),
            minimum_proof_class="behavioral",
        )
    )
    assert result["authority"] == "tower.selector"
    assert result["technology_ids"][0] == "protobuf", result
    assert result["placements"]["protobuf"]["evidence_state"] == "tested"
    assert "function:cross-language contract" in result["reasons"]["protobuf"]


def test_portable_model_graph_selects_onnx_not_general_config_format() -> None:
    result = select_technologies(
        TechnologyRequest(
            mission_id="model-runtime-boundary",
            capabilities=("portable model graph",),
            minimum_proof_class="behavioral",
        )
    )
    assert result["technology_ids"][0] == "onnx", result
    placement = result["placements"]["onnx"]
    assert placement["evidence_state"] == "tested"
    assert "model" in placement["what"].casefold()


def test_data_oriented_request_exposes_odin_as_gated_not_selected() -> None:
    result = select_technologies(
        TechnologyRequest(
            mission_id="data-layout-boundary",
            capabilities=("data-oriented memory",),
            minimum_proof_class="compile",
        )
    )
    assert result["gated_candidates"].get("odin") == "toolchain_gated"
    assert "odin" not in result["technology_ids"]


def test_quantization_request_does_not_promote_unbenchmarked_rhl_quant() -> None:
    result = select_technologies(
        TechnologyRequest(
            mission_id="compression-boundary",
            capabilities=("quantization compression",),
            minimum_proof_class="benchmark",
        )
    )
    assert result["under_proven_candidates"].get("rhl_quant") == "illustrative"
    assert "rhl_quant" not in result["technology_ids"]


def test_selection_returns_w4h_for_machine_auditability() -> None:
    result = select_technologies(
        TechnologyRequest(
            mission_id="native-security-boundary",
            capabilities=("memory-safe native",),
            minimum_proof_class="behavioral",
        )
    )
    rust = result["placements"]["rust"]
    assert all(rust[field] for field in ("what", "where", "when", "why", "how"))


def test_megamind_adapter_is_only_a_compatibility_consumer() -> None:
    request = TechnologyRequest(
        mission_id="compatibility",
        capabilities=("cross-language contract",),
        minimum_proof_class="behavioral",
    )
    assert adapter_select(request) == select_technologies(request)
