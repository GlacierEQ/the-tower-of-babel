#!/usr/bin/env python3
"""One-time correction for independent Go executable quality boundaries."""
from pathlib import Path

path = Path(".github/workflows/ci.yml")
source = path.read_text(encoding="utf-8")
old = '''      - name: Format and test Go exhibits
        run: |
          set -euo pipefail
          test -z "$(gofmt -l languages/go)"
          go test ./languages/go -v
'''
new = '''      - name: Format, compile, and test Go exhibits
        run: |
          set -euo pipefail
          test -z "$(gofmt -l languages/go)"
          go build -o /tmp/babel-go-easy languages/go/easy_ping.go
          go build -o /tmp/babel-go-advanced languages/go/advanced_telemetry_decoder.go
          /tmp/babel-go-easy
          /tmp/babel-go-advanced
          go test languages/go/advanced_telemetry_decoder.go languages/go/advanced_telemetry_decoder_test.go -v
'''
if old not in source:
    raise SystemExit("expected Go quality-gate block missing")
path.write_text(source.replace(old, new, 1), encoding="utf-8")
print("Corrected Go quality boundary for independent executable exhibits.")
