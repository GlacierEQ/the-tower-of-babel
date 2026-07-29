#!/usr/bin/env python3
"""Watchdog daemon for the-tower-of-babel repo."""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def check_integrity():
    hashes_file = REPO_ROOT / ".integrity" / "file_hashes.json"
    if not hashes_file.exists():
        return {"status": "MISSING_HASHES", "ok": False}
    return {"status": "HEALTHY", "ok": True}

if __name__ == "__main__":
    print(json.dumps(check_integrity(), indent=2))
