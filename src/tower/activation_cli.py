"""Executable entrypoint for Tower capability activation."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .activation import activate_execution
from .operator_scope import verify_operator_scope_receipt
from .registry import load_registry


def _scope_receipt_path(argument: str | None) -> Path | None:
    candidate = argument or os.environ.get("TOWER_OPERATOR_SCOPE_RECEIPT")
    return Path(candidate).expanduser() if candidate else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tower-activate")
    parser.add_argument("technology")
    parser.add_argument(
        "--external-effects",
        action="store_true",
        help="Declare that the requested execution may cross an external-effect boundary.",
    )
    parser.add_argument(
        "--operator-scope-receipt",
        help=(
            "Path to an exact-scoped glaciereq.operator-scope.v1 receipt. "
            "May also be supplied through TOWER_OPERATOR_SCOPE_RECEIPT."
        ),
    )
    args = parser.parse_args(argv)

    technology = load_registry().by_id(args.technology)
    if technology is None:
        print(
            json.dumps(
                {
                    "status": "INVALID_MANIFEST",
                    "blocker": f"Unknown technology: {args.technology}",
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    operator_scope_authorized = False
    scope_verification: dict[str, Any] | None = None
    if args.external_effects:
        receipt_path = _scope_receipt_path(args.operator_scope_receipt)
        if receipt_path is None:
            scope_verification = {
                "authorized": False,
                "errors": ["external effects require an exact-scoped Operator receipt"],
                "assurance": "missing",
            }
        else:
            verification = verify_operator_scope_receipt(
                receipt_path,
                technology_id=args.technology,
                mode="execute",
                external_effects=True,
            )
            scope_verification = verification.to_dict()
            operator_scope_authorized = verification.authorized

    result: dict[str, Any] = activate_execution(
        technology,
        external_effects=args.external_effects,
        operator_scope_authorized=operator_scope_authorized,
    )
    if scope_verification is not None:
        result["operator_scope"] = scope_verification

    print(json.dumps(result, indent=2, sort_keys=True, default=str))
    return 0 if result.get("status") == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
