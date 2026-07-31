#!/usr/bin/env python3
"""One-time canonical gofmt alignment correction and reseal trigger."""
from pathlib import Path

path = Path("languages/go/advanced_telemetry_decoder.go")
source = path.read_text(encoding="utf-8")
replacements = {
    "\tSequence     uint32\n\tTimestampNS  uint64\n\tTemperature float32\n\tPressurePA   float32":
        "\tSequence    uint32\n\tTimestampNS uint64\n\tTemperature float32\n\tPressurePA  float32",
    "\t\tSequence:     binary.BigEndian.Uint32(buf[8:12]),\n\t\tTimestampNS:  binary.BigEndian.Uint64(buf[12:20]),":
        "\t\tSequence:    binary.BigEndian.Uint32(buf[8:12]),\n\t\tTimestampNS: binary.BigEndian.Uint64(buf[12:20]),",
    "\t\tPressurePA:   math.Float32frombits(binary.BigEndian.Uint32(buf[24:28])),":
        "\t\tPressurePA:  math.Float32frombits(binary.BigEndian.Uint32(buf[24:28])),",
    "\t\tSequence:     1,\n\t\tTimestampNS:  1_726_100_000_000_000_000,\n\t\tTemperature: 21.5,\n\t\tPressurePA:   101325,":
        "\t\tSequence:    1,\n\t\tTimestampNS: 1_726_100_000_000_000_000,\n\t\tTemperature: 21.5,\n\t\tPressurePA:  101325,",
}
for old, new in replacements.items():
    if old not in source:
        raise SystemExit(f"expected gofmt source fragment missing: {old!r}")
    source = source.replace(old, new, 1)
path.write_text(source, encoding="utf-8")
print("Applied canonical gofmt alignment to advanced telemetry decoder.")
