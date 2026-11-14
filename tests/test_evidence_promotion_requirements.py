import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATHS = (
    ROOT / "registry" / "advanced-claim-contracts.json",
    ROOT / "src" / "tower" / "data" / "advanced-claim-contracts.json",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))["contracts"]


def test_runtime_claims_require_executable_promotion_evidence() -> None:
    sovereign = _load(CONTRACT_PATHS[0])
    mirrored = _load(CONTRACT_PATHS[1])
    assert sovereign == mirrored

    cuda = sovereign["cuda"]
    assert cuda["promotion_requirements"]["minimum_evidence_state"] == "tested"
    assert "__global__" in cuda["promotion_requirements"]["required_source_patterns"]
    assert "gpu_backend" in cuda["promotion_requirements"]["required_receipt_fields"]
    assert "real nvcc-built and GPU-executed" in cuda["proof_surface"]

    jax = sovereign["jax"]
    assert jax["promotion_requirements"]["minimum_evidence_state"] == "tested"
    assert "import\\s+jax" in jax["promotion_requirements"]["required_source_patterns"]
    assert "device_count" in jax["promotion_requirements"]["required_receipt_fields"]
    assert "JAX/XLA execution" in jax["proof_surface"]

    rhl = sovereign["rhl_quant"]
    assert rhl["promotion_requirements"]["minimum_evidence_state"] == "benchmark"
    assert "quality_delta" in rhl["promotion_requirements"]["required_receipt_fields"]
    assert "throughput" in rhl["promotion_requirements"]["required_receipt_fields"]
    assert "baseline quality/performance" in rhl["proof_surface"]
