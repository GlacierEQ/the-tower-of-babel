import hashlib
import json
import unittest
from tower.sequential_handoff import build_handoff


class HandoffContractTests(unittest.TestCase):
    def test_preserves_evidence_and_binds_exact_bytes(self):
        steps = [{"stage": "recover", "status": "passed", "evidence": "  line one\nline two  "}]
        result = build_handoff(" M ", " abc ", steps, aspen_repository=" GlacierEQ/aspen-grove-core ")
        self.assertEqual(result["steps"], steps)
        self.assertEqual(result["consumer"], "GlacierEQ/aspen-grove-core")
        payload = {k: v for k, v in result.items() if k != "sha256"}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()
        self.assertEqual(result["sha256"], hashlib.sha256(canonical).hexdigest())
        changed = build_handoff("M", "abc", [{**steps[0], "evidence": steps[0]["evidence"].strip()}])
        self.assertNotEqual(result["sha256"], changed["sha256"])

    def test_invalid_direct_inputs_raise_value_error(self):
        invalid_steps = [None, "steps", {}, [None], [{"stage": "recover", "status": []}],
                         [{"stage": [], "status": "pending"}],
                         [{"stage": "recover", "status": "pending", "extra": "lost"}],
                         [{"stage": "recover", "status": "passed", "evidence": []}],
                         [{"stage": "recover", "status": "passed", "evidence": "  "}]]
        for steps in invalid_steps:
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                build_handoff("M", "abc", steps)
        for mission, revision, destination in [(" ", "abc", "x"), ("M", " ", "x"), ("M", "abc", " ")]:
            with self.subTest(mission=mission, revision=revision, destination=destination), self.assertRaises(ValueError):
                build_handoff(mission, revision, [], aspen_repository=destination)

if __name__ == "__main__":
    unittest.main()
