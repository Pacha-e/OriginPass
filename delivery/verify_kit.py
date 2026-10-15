"""Check a kit's file manifest without installing dependencies or opening the database."""

import hashlib
import json
import sys
from pathlib import Path


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def main():
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent
    manifest = json.loads((root / "KIT-MANIFEST.json").read_text(encoding="utf-8"))
    errors = []
    for name, expected in manifest["files"].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            errors.append(f"Missing or invalid path: {name}")
        elif path.stat().st_size != expected["size"] or digest(path) != expected["sha256"]:
            errors.append(f"Content mismatch: {name}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Kit OK: {len(manifest['files'])} files; source commit {manifest['source_commit']}")
    print("Application setup and a rehearsal on the presentation laptop are separate checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
