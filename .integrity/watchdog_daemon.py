#!/usr/bin/env python3
"""Integrity watchdog backed by the real Tower hash engine."""
import json

from tower.integrity import verify_integrity


def check_integrity():
    return verify_integrity()


if __name__ == "__main__":
    result = check_integrity()
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if result["ok"] else 1)
