"""Executable entrypoint for Tower's real local activation path."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from .activation import activate_execution
from .registry import load_registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tower-activate")
    parser.add_argument("technology", help="registered technology id or name")
    parser.add_argument("--external-effects", action="store_true", help="request an external-effects run; remains separately blocked")
    args = parser.parse_args(argv)

    registry = load_registry()
    technology = registry.by_id(args.technology)
    if technology is None:
        print(json.dumps({"status": "INVALID_MANIFEST", "blocker": f"Unknown technology: {args.technology}"}, indent=2, sort_keys=True))
        return 1

    result: dict[str, Any] = activate_execution(technology, external_effects=args.external_effects)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    status = result.get("status")
    return 0 if status == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
