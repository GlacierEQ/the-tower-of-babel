import json
import os
import subprocess
import sys
import unittest

class HandoffCLITests(unittest.TestCase):
    def invoke(self, data):
        return subprocess.run([sys.executable, '-m', 'tower.sequential_cli', '-'], input=data, capture_output=True, env=os.environ.copy())

    def test_build_and_reject_invalid(self):
        request={'mission_id':'M-1','source_revision':'abc','steps':[{'stage':'recover','status':'passed','evidence':'commit abc'}]}
        result=self.invoke(json.dumps(request).encode())
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['source_revision'],'abc')
        request['steps'][0].pop('evidence')
        self.assertEqual(self.invoke(json.dumps(request).encode()).returncode,2)

    def test_reject_duplicate_and_oversized(self):
        self.assertEqual(self.invoke(b'{"x":1,"x":2}').returncode,2)
        self.assertEqual(self.invoke(b'x'*(1_048_577)).returncode,2)

if __name__ == '__main__': unittest.main()
