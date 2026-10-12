"""Prepare concrete load scripts and fixture maps; never invoke a compiler."""
from pathlib import Path
import argparse
import json
import subprocess
from oxygen_inputs import ROOT, FIXTURES, new_output, sha256

PROFILES = {
    "cell": ("OxygenCoupled.Cell", ["experimental/oxygen-paperten/KulikovskyDistributed.mo",
             "experimental/oxygen-paperten/DCell.mo", "experimental/oxygen-paperten/OxygenCoupled.mo"]),
    "controls": ("OxygenControls.Matrix", ["tests/modelica/oxygen/OxygenLocal.mo",
                 "tests/modelica/oxygen/OxygenControls.mo"]),
    "binding": ("BindingProbe.Matrix", ["tests/modelica/oxygen/BindingProbe.mo"]),
}


def write_new(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    load = commands.add_parser("load", help="Write Load.mos, Translate.mos and source identity")
    load.add_argument("--profile", required=True, choices=PROFILES)
    load.add_argument("--output-dir", required=True, type=Path)
    fixtures = commands.add_parser("fixtures", help="Hash references and write a local path map")
    fixtures.add_argument("--source-root", required=True, type=Path)
    fixtures.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "fixtures":
        out = new_output(args.output)
        definitions = json.loads(FIXTURES.read_text(encoding="utf-8"))["files"]
        paths = {}
        for f in definitions:
            p = (args.source_root / f["sourceLocator"]).resolve(strict=True)
            if sha256(p) != f["sha256"]:
                raise ValueError(f"Fixture hash mismatch: {f['id']}")
            paths[f["id"]] = str(p)
        write_new(out, json.dumps({"formatVersion": 1, "files": paths}, indent=2) + "\n")
        print(json.dumps({"verifiedFixtures": len(paths), "output": str(out), "copiedData": False}))
        return
    out = args.output_dir.resolve()
    if out.exists():
        raise FileExistsError(f"Use a new preparation directory: {out}")
    targets = [new_output(out / name) for name in ("Load.mos", "Translate.mos", "preparation.json")]
    model, harness = PROFILES[args.profile]
    sources = ([] if args.profile == "binding" else ["FCSys 0.2.6/package.mo"]) + harness
    paths = [(ROOT / p).resolve(strict=True) for p in sources]
    lines = ['getVersion();', 'loadModel(Modelica,{"3.2.3"});getErrorString();',
             'getSourceFile(Modelica);']
    for p in paths:
        lines.append(f'loadFile({json.dumps(p.as_posix(), ensure_ascii=False)});getErrorString();')
    content = "\n".join(lines) + "\n"
    translation = content + 'print("BEGIN_STAGE=translate\\n");\n' + f'translateModel({model});getErrorString();\n' + 'print("END_STAGE=translate\\n");\n'
    identity_paths = set(paths)
    if args.profile != "binding":
        identity_paths.update((ROOT / "FCSys 0.2.6").glob("*.mo"))
        identity_paths.add(ROOT / "FCSys 0.2.6/package.order")
        identity_paths.update(p for p in (ROOT / "FCSys 0.2.6/Resources/Source/C").rglob("*") if p.is_file())
    git = lambda *a: subprocess.check_output(["git", "-C", str(ROOT), *a]).decode().strip()
    record = {"profile": args.profile, "model": model, "loadOrder": sources,
              "sourceCommit": git("rev-parse", "HEAD"),
              "workingTreeStatus": git("status", "--porcelain=v1"),
              "sources": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p)}
                          for p in sorted(identity_paths)],
              "compilerExecuted": False, "recordedCompiler": "OpenModelica 1.27.0 Windows 64-bit",
              "modelicaRequested": "3.2.3", "resolvedLibraries": "not observed; no compiler executed",
              "instructions": "Execute later in this output directory with explicit compiler bounds. Check every load result/error and actual resolved libraries before accepting translation."}
    for path, text in zip(targets, (content, translation, json.dumps(record, indent=2) + "\n")):
        write_new(path, text)
    print(json.dumps({"profile": args.profile, "model": model, "preparedFiles": [str(p) for p in targets], "compilerExecuted": False}))


if __name__ == "__main__":
    main()
