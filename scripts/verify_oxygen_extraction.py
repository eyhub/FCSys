"""Verify the recorded source assembly; no compiler or scientific checks."""
from pathlib import Path
import argparse
import hashlib
import json


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_serialized(root, record):
    data = (root / record["path"]).read_bytes()
    if record["normalization"] == "crlf-to-lf":
        data = data.replace(b"\r\n", b"\n")
    else:
        assert record["normalization"] == "none", record["path"]
    assert hashlib.sha256(data).hexdigest() == record["sha256"], record["path"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", action="store_true",
                        help="Also verify original local source files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "qualification/oxygen-20260929/EXTRACTION.json")
                          .read_text(encoding="utf-8"))
    overlays = {f["proposedDestination"]: f for f in manifest["files"]}
    adaptations = {f["path"]: f for f in manifest["adaptations"]}
    serialized_path = root / "qualification/oxygen-20260929/SERIALIZATION.json"
    serialized = (json.loads(serialized_path.read_text(encoding="utf-8"))
                  if serialized_path.exists() else None)
    if serialized:
        for record in serialized["files"]:
            verify_serialized(root, record)
    checked = set()
    for f in manifest["inheritedFiles"]:
        path = f["path"]
        expected = (adaptations[path]["afterSha256"] if path in adaptations
                    else overlays[path]["sha256"] if path in overlays
                    else f["sha256"])
        if not serialized:
            assert digest(root / path) == expected, path
        checked.add(path)
        if args.sources:
            assert digest(Path(manifest["sourceForkCheckout"]) / path) == f["sha256"], path
    for f in manifest["files"]:
        path = f["proposedDestination"]
        assert digest(root / path) == f["sha256"], path
        assert (root / path).stat().st_size == f["bytes"], path
        checked.add(path)
        if args.sources:
            assert digest(Path(manifest["sourceResearchRoot"]) / f["source"]) == f["sha256"], f["source"]
    for f in manifest["rootLibraryComparison"]:
        if not serialized:
            assert digest(root / "FCSys 0.2.6" / f["file"]) == f["sha256"], f["file"]
    if serialized:
        assert checked <= {f["path"] for f in serialized["files"]}
    print(json.dumps({"passed": True, "assembledFiles": len(checked),
                      "selectedFiles": len(overlays),
                      "libraryRootFiles": len(manifest["rootLibraryComparison"]),
                      "serializedFiles": len(serialized["files"]) if serialized else 0,
                      "originalSourcesChecked": args.sources,
                      "runtimeExecuted": False}))


if __name__ == "__main__":
    main()
