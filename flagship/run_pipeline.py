#!/usr/bin/env python3
"""Execute the flagship polyglot pipeline with exact toolchain blockers."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "build" / "flagship"


def run(argv: list[str], *, cwd: Path = ROOT) -> dict:
    try:
        completed = subprocess.run(
            argv, cwd=cwd, text=True, capture_output=True, timeout=180, check=False
        )
        return {
            "argv": argv,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-3000:],
            "stderr": completed.stderr[-3000:],
            "status": "VERIFIED" if completed.returncode == 0 else "FAILED",
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "argv": argv,
            "returncode": None,
            "stdout": (exc.stdout or "")[-3000:] if isinstance(exc.stdout, str) else "",
            "stderr": (exc.stderr or "")[-3000:] if isinstance(exc.stderr, str) else "",
            "status": "FAILED_TIMEOUT",
        }


def blocker(tool: str, stage: str) -> dict:
    return {
        "stage": stage,
        "status": "BLOCKED_TOOLCHAIN",
        "blocker": f"Required executable not found: {tool}",
    }


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    source = ROOT / "flagship" / "mission.input.json"
    mission = WORK / "mission.json"
    plan = WORK / "plan.json"
    decision = WORK / "decision.json"
    event = WORK / "event.json"

    if shutil.which("tsc") and shutil.which("node"):
        ts_out = WORK / "typescript"
        ts_out.mkdir(exist_ok=True)
        compile_result = run([
            "tsc", "--strict", "--target", "ES2022", "--module", "commonjs",
            "--outDir", str(ts_out), "flagship/typescript/ingress.ts",
        ])
        compile_result["stage"] = "typescript_compile"
        results.append(compile_result)
        if compile_result["status"] == "VERIFIED":
            ingress = run([
                "node", str(ts_out / "ingress.js"), str(source), str(mission),
            ])
            ingress["stage"] = "typescript_ingress"
            results.append(ingress)
    else:
        results.append(blocker("tsc/node", "typescript_ingress"))

    if not mission.is_file():
        payload = json.loads(source.read_text(encoding="utf-8"))
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        payload["input_sha256"] = hashlib.sha256(canonical).hexdigest()
        mission.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        results.append({"stage": "python_ingress_fallback", "status": "FALLBACK"})

    planner = run([sys.executable, "flagship/python/planner.py", str(mission), str(plan)])
    planner["stage"] = "python_planner"
    results.append(planner)

    if planner["status"] == "VERIFIED" and shutil.which("cargo"):
        authority = run([
            "cargo", "run", "--quiet", "--manifest-path", "flagship/rust/Cargo.toml",
            "--", str(plan), str(decision),
        ])
        authority["stage"] = "rust_authority"
        results.append(authority)
    elif planner["status"] == "VERIFIED":
        results.append(blocker("cargo", "rust_authority"))

    if decision.is_file() and shutil.which("go"):
        go_binary = WORK / "tower-telemetry"
        compile_go = run(["go", "build", "-o", str(go_binary), "flagship/go/telemetry.go"])
        compile_go["stage"] = "go_compile"
        results.append(compile_go)
        if compile_go["status"] == "VERIFIED":
            telemetry = run([str(go_binary), str(decision), str(event)])
            telemetry["stage"] = "go_telemetry"
            results.append(telemetry)
    elif decision.is_file():
        results.append(blocker("go", "go_telemetry"))

    if shutil.which("sqlite3"):
        db = WORK / "tower.db"
        sql_result = run(["sqlite3", str(db), ".read flagship/sql/state.sql"])
        sql_result["stage"] = "sql_state"
        results.append(sql_result)
    else:
        results.append(blocker("sqlite3", "sql_state"))

    if shutil.which("wat2wasm"):
        wasm = run([
            "wat2wasm", "flagship/wat/sandbox.wat", "-o", str(WORK / "sandbox.wasm")
        ])
        wasm["stage"] = "wasm_sandbox"
        results.append(wasm)
    else:
        results.append(blocker("wat2wasm", "wasm_sandbox"))

    if shutil.which("lake"):
        lean = run(["lake", "env", "lean", "flagship/lean4/invariant.lean"])
        lean["stage"] = "lean_invariant"
        results.append(lean)
    else:
        results.append(blocker("lake", "lean_invariant"))

    report = {
        "pipeline_id": "tower-polyglot-mission-v1",
        "mission_id": json.loads(mission.read_text(encoding="utf-8"))["mission_id"],
        "results": results,
    }
    report_bytes = json.dumps(report, indent=2, sort_keys=True).encode()
    report["report_sha256"] = hashlib.sha256(report_bytes).hexdigest()
    (WORK / "pipeline.report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    failed = [row for row in results if row["status"].startswith("FAILED")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
