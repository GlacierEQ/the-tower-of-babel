#!/usr/bin/env python3
"""One-time isolation of the easy Go command from package-level tests."""
from pathlib import Path

path = Path("languages/go/easy_ping.go")
source = path.read_text(encoding="utf-8")
marker = "//go:build ignore\n\n"
if source.startswith(marker):
    print("Easy Go command is already isolated from package discovery.")
else:
    if not source.startswith("package main\n"):
        raise SystemExit("unexpected easy Go command header")
    path.write_text(marker + source, encoding="utf-8")
    print("Isolated easy Go command while preserving explicit file builds.")
