import json
import hashlib
import os
import subprocess
import sys
import unittest
from pathlib import Path

class HandoffCLITests(unittest.TestCase):
    def invoke(self, data):
        env=os.environ.copy(); env['PYTHONPATH']=str(Path(__file__).resolve().parents[1]/'src')
        return subprocess.run([sys.executable, '-m', 'tower.sequential_cli', '-'], input=data, capture_output=True, env=env)

    def test_build_and_reject_invalid(self):
        request={'mission_id':'M-1','source_revision':'abc','steps':[{'stage':'recover','status':'passed','evidence':'commit abc'}]}
        result=self.invoke(json.dumps(request).encode())
        self.assertEqual(result.returncode,0,result.stderr)
        handoff=json.loads(result.stdout)
        self.assertEqual(set(handoff), {'schema', 'producer', 'consumer', 'mission_id', 'source_revision', 'steps', 'sha256'})
        self.assertEqual(handoff['steps'], request['steps'])
        unsigned={k:v for k,v in handoff.items() if k != 'sha256'}
        expected=hashlib.sha256(json.dumps(unsigned,sort_keys=True,separators=(',', ':'),ensure_ascii=True,allow_nan=False).encode()).hexdigest()
        self.assertEqual(handoff['sha256'], expected)
        self.assertEqual(handoff['source_revision'],'abc')
        request['steps'][0].pop('evidence')
        self.assertEqual(self.invoke(json.dumps(request).encode()).returncode,2)

    def test_reject_expanded_handoff(self):
        request={"mission_id":"M", "source_revision":"abc", "steps":[{"stage":"recover", "status":"passed", "evidence":"é"*200000}]}
        self.assertEqual(self.invoke(json.dumps(request,ensure_ascii=False).encode()).returncode,2)

    def test_reject_duplicate_and_oversized(self):
        self.assertEqual(self.invoke(b'{"x":1,"x":2}').returncode,2)
        valid=b'{"mission_id":"M","source_revision":"abc","steps":[]}'
        oversized=self.invoke(valid + b' '*(1_048_577-len(valid)))
        self.assertEqual(oversized.returncode,2)
        self.assertIn(b'exceeds 1 MiB',oversized.stderr)
        self.assertEqual(self.invoke(b'['*2000+b']'*2000).returncode,2)

if __name__ == '__main__': unittest.main()
