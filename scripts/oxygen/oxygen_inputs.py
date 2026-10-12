"""Explicit inputs/output for the retained oxygen numerical checks."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests/oxygen/reference-fixtures.json"


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def new_output(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / "build").resolve()):
        raise ValueError("Output must be inside this repository's build directory")
    if path.exists():
        raise FileExistsError(path)
    return path


def verification_inputs(family):
    if not __debug__:
        raise RuntimeError("Do not use python -O: retained numerical assertions are required")
    choices = {"cell": ["native0", "native1"],
               "controls": ["scale05", "scale1", "scale2"],
               "polarization": [p["tag"] for p in json.loads(
                   (ROOT / "tests/oxygen/polarization-points.json").read_text())]}
    parser = argparse.ArgumentParser(description=f"Verify {family}; does not run a simulation")
    parser.add_argument("--case", required=True, choices=choices[family])
    parser.add_argument("--mat", required=True, type=Path)
    parser.add_argument("--mat-sha256", required=True)
    parser.add_argument("--process-record", required=True, type=Path)
    parser.add_argument("--fixtures", type=Path, help="Explicit local fixture path map")
    parser.add_argument("--evidence-kind", required=True, choices=["retained-replay", "new-run"])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output = new_output(args.output)
    args.mat = args.mat.resolve(strict=True)
    args.process_record = args.process_record.resolve(strict=True)
    actual = sha256(args.mat)
    if actual != args.mat_sha256.lower():
        raise ValueError("MAT SHA-256 does not match the declared input")
    receipt = json.loads(args.process_record.read_text(encoding="utf-8"))
    if not (receipt.get("accepted") is True and receipt.get("exit_code") == 0
            and receipt.get("timeout") is False):
        raise ValueError("Process record must report accepted, exit_code=0, timeout=false")
    if receipt.get("stage") is not None and receipt["stage"] != args.case:
        raise ValueError("Process record stage does not match selected case")
    if Path(receipt.get("artifact", "").replace("\\", "/")).name != args.mat.name:
        raise ValueError("Process record artifact name does not match MAT input")
    if receipt.get("mat_sha256") and receipt["mat_sha256"] != actual:
        raise ValueError("Process record MAT identity differs from the supplied result")
    args.context = {"evidence_kind": args.evidence_kind,
                    "case": args.case, "family": family,
                    "mat": str(args.mat), "mat_sha256": actual,
                    "process_record": str(args.process_record),
                    "process_record_sha256": sha256(args.process_record),
                    "process_receipt_has_mat_hash": bool(receipt.get("mat_sha256")),
                    "verified_utc": datetime.now(timezone.utc).isoformat(),
                    "dependencies": {name: version(name) for name in ("numpy", "scipy")},
                    "fixtures": {}, "simulation_launched_by_verifier": False}
    provenance_files = [Path(sys.argv[0]).resolve(), Path(__file__).resolve(), FIXTURES,
                        ROOT / "tests/oxygen/polarization-points.json"]
    args.context["verification_sources"] = [
        {"path": str(p), "sha256": sha256(p)} for p in provenance_files]
    git = lambda *a: subprocess.check_output(["git", "-C", str(ROOT), *a]).decode().strip()
    args.context["repository"] = {"head": git("rev-parse", "HEAD"),
                                  "working_tree_status": git("status", "--porcelain=v1")}
    return args


def reference(args, key):
    if args.fixtures is None:
        raise ValueError(f"--fixtures is required for reference {key}")
    definitions = json.loads(FIXTURES.read_text(encoding="utf-8"))["files"]
    definition = next(f for f in definitions if f["id"] == key)
    map_path = args.fixtures.resolve(strict=True)
    mapping = json.loads(map_path.read_text(encoding="utf-8"))
    path = Path(mapping["files"][key])
    if not path.is_absolute():
        path = map_path.parent / path
    path = path.resolve(strict=True)
    if sha256(path) != definition["sha256"]:
        raise ValueError(f"Reference fixture hash mismatch: {key}")
    args.context["fixtures"][key] = {"path": str(path), "sha256": definition["sha256"]}
    return path, definition["sha256"]


def write_result(out, args):
    out["verification_context"] = args.context
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(out, stream, indent=2)
        stream.write("\n")
