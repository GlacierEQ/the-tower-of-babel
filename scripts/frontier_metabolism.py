#!/usr/bin/env python3
"""Fetch registered frontier sources and emit deterministic observation receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch(url: str, timeout: int) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": "GlacierEQ-Tower-Frontier/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            return {
                "status": "ok",
                "http_status": getattr(response, "status", 200),
                "sha256": hashlib.sha256(body).hexdigest(),
                "bytes": len(body),
                "etag": response.headers.get("ETag"),
                "last_modified": response.headers.get("Last-Modified"),
            }
    except (HTTPError, URLError, TimeoutError) as exc:
        return {"status": "error", "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", default="frontier/sources.json")
    parser.add_argument("--previous")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    config = json.loads(Path(args.sources).read_text(encoding="utf-8"))
    previous: dict[str, object] = {}
    if args.previous and Path(args.previous).is_file():
        previous = json.loads(Path(args.previous).read_text(encoding="utf-8"))
    previous_by_id = {
        row.get("id"): row
        for row in previous.get("observations", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }

    observations: list[dict[str, object]] = []
    changed: list[str] = []
    successful = 0
    for source in config["sources"]:
        result = fetch(source["url"], args.timeout)
        row = {**source, **result}
        prior = previous_by_id.get(source["id"])
        if result.get("status") == "ok":
            successful += 1
            prior_hash = prior.get("sha256") if isinstance(prior, dict) else None
            row["change"] = "first_observation" if prior_hash is None else (
                "changed" if prior_hash != result.get("sha256") else "unchanged"
            )
            if row["change"] != "unchanged":
                changed.append(source["id"])
        else:
            row["change"] = "unavailable"
        observations.append(row)

    payload = {
        "schema": "glaciereq.frontier-observation.v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "source_registry": args.sources,
        "successful_sources": successful,
        "changed_sources": changed,
        "observations": observations,
    }
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"successful": successful, "changed": len(changed)}))
    return 0 if successful else 2


if __name__ == "__main__":
    raise SystemExit(main())
