import json
from pathlib import Path

TEST_COMMANDS = [
    ["build/go_easy"],
    [
        "go",
        "test",
        "languages/go/advanced_telemetry_decoder.go",
        "languages/go/advanced_telemetry_decoder_test.go",
        "-v",
    ],
]

for path in (
    Path("registry/tower.d/orchestration-runtime.json"),
    Path("src/tower/data/tower.d/orchestration-runtime.json"),
):
    payload = json.loads(path.read_text(encoding="utf-8"))
    technology = next(
        item for item in payload["technologies"] if item["id"] == "go"
    )
    technology["toolchain"]["test"] = TEST_COMMANDS
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
