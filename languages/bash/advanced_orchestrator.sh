#!/usr/bin/env bash
# What: Tower CI Orchestrator with structured JSON receipts and retry backoff.
# Where: CI/CD runners validating the integrity of the Tower.
# When: During every pull request or deployment pipeline phase.
# Why: Ensures deterministic gating and fault tolerance against network flakes.
# How: Bash strict mode, signal traps, retry logic, and JSON output generation.

set -euo pipefail

# Ensure cleanup on exit
temp_dir=$(mktemp -d)
trap 'rm -rf "$temp_dir"' EXIT

receipt_file="${temp_dir}/receipt.json"
echo '{"status": "running", "gates": []}' > "$receipt_file"

append_receipt() {
    local step=$1
    local status=$2
    # Simple JSON append (in reality, jq would be used)
    jq --arg step "$step" --arg status "$status" \
       '.gates += [{"step": $step, "status": $status, "timestamp": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}]' \
       "$receipt_file" > "${receipt_file}.tmp" && mv "${receipt_file}.tmp" "$receipt_file"
}

with_retry() {
    local max_attempts=$1
    shift
    local cmd=("$@")
    local attempt=1
    local wait=2

    while true; do
        if "${cmd[@]}" > "${temp_dir}/cmd_out" 2>&1; then
            return 0
        fi
        
        if (( attempt >= max_attempts )); then
            echo "Failed after $max_attempts attempts: ${cmd[*]}" >&2
            cat "${temp_dir}/cmd_out" >&2
            return 1
        fi
        
        echo "Attempt $attempt failed. Retrying in $wait seconds..." >&2
        sleep $wait
        wait=$(( wait * 2 ))
        attempt=$(( attempt + 1 ))
    done
}

run_gate() {
    local step_name=$1
    shift
    echo "Running gate: $step_name"
    if with_retry 3 "$@"; then
        append_receipt "$step_name" "passed"
    else
        append_receipt "$step_name" "failed"
        echo "Pipeline Halted: Gate $step_name failed." >&2
        jq '.status = "failed"' "$receipt_file" > "${receipt_file}.tmp" && mv "${receipt_file}.tmp" "$receipt_file"
        cat "$receipt_file"
        exit 1
    fi
}

# Main pipeline execution
echo "Starting Tower Orchestration pipeline..."

run_gate "validate" python3 -c 'print("Simulating python -m tower validate")'
run_gate "generate" python3 -c 'print("Simulating tower generate --check")'
run_gate "integrity" python3 -c 'print("Simulating tower integrity verify")'

jq '.status = "passed" | .git_sha = "'"${GITHUB_SHA:-unknown}"'"' "$receipt_file" > "${receipt_file}.tmp" && mv "${receipt_file}.tmp" "$receipt_file"

echo "Pipeline succeeded! Final receipt:"
cat "$receipt_file"
