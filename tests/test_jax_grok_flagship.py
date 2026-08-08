"""Reference test for the pure-Python mesh simulation; it does not prove JAX/XLA execution."""
from __future__ import annotations

import json
from languages.jax.advanced_grok_distributed_mesh import GrokJaxDistributedEngine


def test_grok_jax_engine_execution():
    engine = GrokJaxDistributedEngine(num_heads=4, head_dim=32, num_layers=16)
    report = engine.simulate_sharded_grok_step(prompt_tokens=4)
    assert report["status"] == "REFERENCE_ONLY"
    assert report["flagship_tier"] == "CONCEPTUAL_DISTRIBUTED_MESH"
    assert report["sharding"]["xla_devices"] == 8
    assert report["execution_metrics"]["tokens_processed"] == 4
    assert report["execution_metrics"]["kv_cache_length"] == 4


def test_rope_transform():
    engine = GrokJaxDistributedEngine(num_heads=2, head_dim=8, num_layers=4)
    vector = [1.0, 0.0, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]
    rotated = engine.apply_rope(vector, seq_idx=2)
    assert len(rotated) == len(vector)
    assert rotated != vector  # Positional shift applied
