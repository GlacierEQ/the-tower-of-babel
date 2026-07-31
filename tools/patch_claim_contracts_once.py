#!/usr/bin/env python3
"""One-time source-grounded corrections discovered by the semantic audit."""
from __future__ import annotations

import json
from pathlib import Path

path = Path("registry/advanced-claim-contracts.json")
payload = json.loads(path.read_text(encoding="utf-8"))
contracts = payload["contracts"]

contracts["swift"]["forbidden_claim_patterns"] = [
    "runs? (directly )?on (the )?ANE",
    "ANE backend",
    "production GPU",
]
contracts["cuda"]["required_source_patterns"] = ["expf", "reference_attention"]
contracts["cuda"]["forbidden_claim_patterns"] = [
    "implements? (the )?production FlashAttention",
    "FlashAttention compatible",
    "production kernel",
]
contracts["mojo"]["forbidden_claim_patterns"] = [
    "runs? on (a )?TPU",
    "TPU backend",
    "production kernel",
]
contracts["webassembly"]["required_source_patterns"] = [
    "capability",
    "last_status|attempts|successes",
]
contracts["flatbuffers"]["required_source_patterns"] = [
    "previous_frame_sha256",
    "file_identifier",
]

path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
