"""Runner failure paths; no Modelica compiler or scientific results required."""
from pathlib import Path
import json
import os
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts/oxygen'))
from run_support import accept_runtime, confined_new_output, diagnostics, own_session, run_process
from run_cell import environment

class RunnerTests(unittest.TestCase):
    def setUp(self):
        (ROOT/'build').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=ROOT/'build',prefix='runner-tests-')
        self.path=Path(self.temp.name).resolve()
    def tearDown(self):
        self.assertTrue(self.path.is_relative_to((ROOT/'build').resolve()))
        self.temp.cleanup()
    def test_output_boundaries(self):
        for path in [ROOT/'outside', ROOT/'build']:
            with self.assertRaises(ValueError):confined_new_output(ROOT,path)
        with self.assertRaises(FileExistsError):confined_new_output(ROOT,self.path)
        self.assertEqual(confined_new_output(ROOT,self.path/'new'),self.path/'new')
    def test_exclusive_lock_cleanup(self):
        path=self.path/'owner.lock'
        with self.assertRaisesRegex(RuntimeError,'test failure'):
            with own_session(path,{'owner':'test'}):
                with self.assertRaises(FileExistsError):
                    with own_session(path,{'owner':'second'}):self.fail('second owner entered')
                raise RuntimeError('test failure')
        self.assertFalse(path.exists())
    def test_wrong_tool_rejected(self):
        (self.path/'fake.exe').write_bytes(b'wrong')
        with self.assertRaisesRegex(ValueError,'tool identity'):
            environment(self.path,self.path,{'tools':[{'path':'fake.exe','sha256':'0'*64}]})
    def test_wrong_library_rejected(self):
        (self.path/'package.mo').write_text('wrong')
        with self.assertRaisesRegex(ValueError,'library entry'):
            environment(self.path,self.path,{'tools':[],'libraries':[{'path':'package.mo','sha256':'0'*64}]})
    def test_failed_process_retains_evidence(self):
        with self.assertRaisesRegex(RuntimeError,'failed'):
            run_process([sys.executable,'-c','print("failure evidence"); raise SystemExit(7)'],self.path,'failure',10,os.environ.copy())
        r=json.loads((self.path/'failure-process.json').read_text())
        self.assertEqual(r['exit_code'],7);self.assertFalse(r['accepted'])
        self.assertIn('failure evidence',(self.path/'failure-stdout.log').read_text())
        with self.assertRaises(FileExistsError):
            run_process([sys.executable,'-c','pass'],self.path,'failure',10,os.environ.copy())
    def test_timeout_terminates_owned_process(self):
        with self.assertRaisesRegex(RuntimeError,'failed'):
            run_process([sys.executable,'-c','import time; time.sleep(30)'],self.path,'timeout',.2,os.environ.copy())
        r=json.loads((self.path/'timeout-process.json').read_text())
        self.assertTrue(r['timeout']);self.assertFalse(r['accepted'])
        self.assertEqual(r['ownedTermination']['exit_code'],0);self.assertEqual(r['state'],'terminal')
    def test_compiler_error_not_warning(self):
        with self.assertRaises(ValueError):diagnostics('true\nError: failed model')
        self.assertEqual(diagnostics('true\nWarning: retained'),['Warning: retained'])
    def test_success_marker_cannot_hide_warning(self):
        (self.path/'simulate-stdout.log').write_text('solver: ida\nLOG_WARNING | warning | unexpected\nThe simulation finished successfully.')
        (self.path/'simulate-stderr.log').write_text('')
        with self.assertRaisesRegex(ValueError,'Unreviewed runtime warning'):accept_runtime(self.path)
    def test_reviewed_initialization_fallbacks(self):
        warning = 'LOG_STDOUT        | warning | The default linear solver fails, the fallback solver with total pivoting is started at time 0.000000. That might raise performance issues, for more information use -lv LOG_LS.\n'
        (self.path/'simulate-stderr.log').write_text('')
        log = self.path/'simulate-stdout.log'
        log.write_text(warning*72+'solver: ida\nThe simulation finished successfully.')
        self.assertEqual(accept_runtime(self.path)['initializationLinearSolverFallbacks'],72)
        log.write_text(warning+'solver: ida\nThe simulation finished successfully.')
        with self.assertRaisesRegex(ValueError,'Unexpected count'):accept_runtime(self.path)
    def test_later_linear_solver_fallback_rejected(self):
        (self.path/'simulate-stderr.log').write_text('')
        (self.path/'simulate-stdout.log').write_text('LOG_STDOUT | warning | The default linear solver fails, the fallback solver with total pivoting is started at time 1.000000. That might raise performance issues, for more information use -lv LOG_LS.\nsolver: ida\nThe simulation finished successfully.')
        with self.assertRaisesRegex(ValueError,'Unreviewed runtime warning'):accept_runtime(self.path)

if __name__=='__main__':unittest.main()
