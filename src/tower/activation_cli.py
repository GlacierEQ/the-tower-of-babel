"""Executable entrypoint for Tower's local activation path."""
from __future__ import annotations
import argparse
import json
from typing import Any
from .activation import activate_execution
from .registry import load_registry
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tower-activate")
    parser.add_argument("technology")
    parser.add_argument("--external-effects", action="store_true")
    args = parser.parse_args(argv)
    technology = load_registry().by_id(args.technology)
    if technology is None:
        print(json.dumps({"status": "INVALID_MANIFEST", "blocker": f"Unknown technology: {args.technology}"}, indent=2, sort_keys=True)); return 1
    result: dict[str, Any] = activate_execution(technology, external_effects=args.external_effects)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0 if result.get("status") == "VERIFIED" else 2
if __name__ == "__main__": raise SystemExit(main())
