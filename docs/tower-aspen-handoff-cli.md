# Offline Tower → Aspen coding handoff

The producer records operator-supplied steps; it does not execute coding, activate an AI reasoning model, or validate that evidence claims are true. The consumer verifies structure, digest and an independently supplied expected revision. A digest or revision match does not authenticate the producer or prove deployment. No network, credentials or writes occur unless the caller redirects stdout.

On local checkouts of these feature branches, from the Tower root:

```sh
PYTHONPATH=src python -m tower.sequential_cli mission.json > handoff.json
```

From the Aspen Core root, provide the absolute path and independently verified revision:

```sh
python -m src.tower_handoff_cli /path/to/handoff.json --expected-revision "$TRUSTED_REVISION"
```

Input to the producer is a JSON object with exactly `mission_id`, `source_revision`, and `steps`; steps contain `stage`, `status`, and optional `evidence`. Both commands support `-` for stdin, reject duplicate keys and inputs above 1 MiB, and return exit 2 for invalid input. The consumer explicitly reports `source_authenticated: false` and `provider_verified: false`. Treat the handoff as untrusted until source authenticity and relevant claims are verified independently.
