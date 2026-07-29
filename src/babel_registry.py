#!/usr/bin/env python3
"""Compatibility facade generated from registry/tower.yml."""
from tower.registry import load_registry, validate_registry


class BabelRegistryEngine:
    def __init__(self):
        self.registry = load_registry()

    def get_spec(self, lang_key: str):
        row = self.registry.by_id(lang_key)
        if row is None:
            return {"status": "UNKNOWN_SPEC", "ok": False}
        return {**row, "status": "VALIDATED_W4H_SPEC", "ok": True}


BABEL_REGISTRY = {row["id"]: row for row in load_registry().technologies}


if __name__ == "__main__":
    registry = load_registry()
    errors = validate_registry(registry)
    print(f"Tower of Babel Registry Initialized: {len(registry.technologies)} Technologies Registered.")
    if errors:
        raise SystemExit("\n".join(errors))
