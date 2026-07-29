#!/usr/bin/env python3
"""Plan a mission through the canonical Tower-to-Megamind adapter."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from integrations.megamind.adapter import TechnologyRequest, select_technologies


def main() -> int:
    input_path, output_path = map(Path, sys.argv[1:3])
    mission = json.loads(input_path.read_text(encoding="utf-8"))
    plan = select_technologies(
        TechnologyRequest(
            mission_id=mission["mission_id"],
            capabilities=tuple(mission["required_capabilities"]),
            interfaces=tuple(mission["preferred_interfaces"]),
            minimum_proof_class="compile",
        )
    )
    output_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"stage": "planner", "technologies": plan["technology_ids"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
