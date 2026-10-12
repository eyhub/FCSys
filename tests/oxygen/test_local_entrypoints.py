"""Input-boundary checks; no compiler, simulator or large MAT dependency."""
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/oxygen"))
import oxygen_inputs as inputs
import prepare


class LocalEntrypoints(unittest.TestCase):
    def setUp(self):
        build = ROOT / "build"
        build.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="entrypoint-test-", dir=build)
        self.directory = Path(self.temp.name).resolve()
        assert self.directory.is_relative_to(build.resolve())

    def tearDown(self):
        assert self.directory.is_relative_to((ROOT / "build").resolve())
        self.temp.cleanup()

    def invocation(self, receipt=None, digest=None):
        mat = self.directory / "native0.mat"
        mat.write_bytes(b"input-boundary fixture, not scientific MAT data")
        process = self.directory / "process.json"
        process.write_text(json.dumps(receipt or {"accepted": True, "exit_code": 0,
                            "timeout": False, "stage": "native0", "artifact": mat.name}))
        return ["verify_cell.py", "--case", "native0", "--mat", str(mat),
                "--mat-sha256", digest or inputs.sha256(mat), "--process-record", str(process),
                "--evidence-kind", "retained-replay", "--output", str(self.directory / "out.json")]

    def test_hash_mismatch_rejected_without_output(self):
        with patch.object(sys, "argv", self.invocation(digest="0" * 64)):
            with self.assertRaisesRegex(ValueError, "MAT SHA-256"):
                inputs.verification_inputs("cell")
        self.assertFalse((self.directory / "out.json").exists())

    def test_failed_process_rejected(self):
        with patch.object(sys, "argv", self.invocation(receipt={"accepted": False,
                          "exit_code": 1, "timeout": False})):
            with self.assertRaisesRegex(ValueError, "Process record"):
                inputs.verification_inputs("cell")

    def test_wrong_case_rejected(self):
        receipt = {"accepted": True, "exit_code": 0, "timeout": False,
                   "stage": "native1", "artifact": "native0.mat"}
        with patch.object(sys, "argv", self.invocation(receipt=receipt)):
            with self.assertRaisesRegex(ValueError, "stage"):
                inputs.verification_inputs("cell")

    def test_outputs_preserved_and_confined(self):
        out = self.directory / "already.json"
        out.write_text("preserve")
        with self.assertRaises(FileExistsError):
            inputs.new_output(out)
        self.assertEqual(out.read_text(), "preserve")
        with self.assertRaises(ValueError):
            inputs.new_output(ROOT / "qualification/should-not-exist.json")

    def test_bad_reference_hash_rejected(self):
        corrupted = self.directory / "reference.mat"
        corrupted.write_bytes(b"incorrect reference bytes")
        mapping = self.directory / "fixtures.json"
        mapping.write_text(json.dumps({"files": {"oxygen-local-parent": str(corrupted)}}))
        with self.assertRaisesRegex(ValueError, "Reference fixture hash mismatch"):
            inputs.reference(SimpleNamespace(fixtures=mapping, context={"fixtures": {}}),
                             "oxygen-local-parent")

    def test_load_order_and_source_fingerprints(self):
        for profile, (model, harness) in prepare.PROFILES.items():
            out = self.directory / profile
            with patch.object(sys, "argv", ["prepare.py", "load", "--profile", profile,
                                             "--output-dir", str(out)]), redirect_stdout(io.StringIO()):
                prepare.main()
            record = json.loads((out / "preparation.json").read_text())
            self.assertEqual(record["model"], model)
            self.assertFalse(record["compilerExecuted"])
            expected = ([] if profile == "binding" else ["FCSys 0.2.6/package.mo"]) + harness
            self.assertEqual(record["loadOrder"], expected)
            load = (out / "Load.mos").read_text()
            positions = [load.index((ROOT / p).resolve().as_posix()) for p in expected]
            self.assertEqual(positions, sorted(positions))
            self.assertNotIn("C:/Thesis-cell", load)
            self.assertIn(f"translateModel({model})", (out / "Translate.mos").read_text())
            for f in record["sources"]:
                self.assertEqual(hashlib.sha256((ROOT / f["path"]).read_bytes()).hexdigest(), f["sha256"])


if __name__ == "__main__":
    unittest.main()
