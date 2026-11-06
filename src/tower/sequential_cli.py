"""Create a Tower-to-Aspen handoff from local recorded outcomes; no remote effects."""
from __future__ import annotations
import argparse
import json
import sys
from .sequential_handoff import build_handoff

MAX_INPUT_BYTES = 1_048_576

def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON input file, or - for stdin')
    args = parser.parse_args(argv)
    try:
        if args.input == '-':
            raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
        else:
            with open(args.input, 'rb') as stream:
                raw = stream.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise ValueError('input exceeds 1 MiB')
        data = json.loads(raw, object_pairs_hook=_unique_object)
        if not isinstance(data, dict) or set(data) != {'mission_id', 'source_revision', 'steps'}:
            raise ValueError('expected mission_id, source_revision, and steps')
        if not isinstance(data['steps'], list):
            raise ValueError('steps must be an array')
        for step in data['steps']:
            if not isinstance(step, dict) or set(step) - {'stage', 'status', 'evidence'}:
                raise ValueError('invalid step fields')
            if not isinstance(step.get('stage'), str) or not isinstance(step.get('status'), str):
                raise ValueError('stage and status must be strings')
        handoff = build_handoff(data['mission_id'], data['source_revision'], data['steps'])
        serialized = json.dumps(handoff, sort_keys=True, ensure_ascii=True) + "\n"
        if len(serialized.encode("utf-8")) > MAX_INPUT_BYTES:
            raise ValueError("serialized handoff exceeds consumer limit")
        sys.stdout.write(serialized)
        return 0
    except (ValueError, TypeError, OSError, UnicodeError, RecursionError) as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
