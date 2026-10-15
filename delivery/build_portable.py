"""Rebuild the Windows presentation ZIP from the current working tree (no secrets)."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "delivery"
WIKI = ROOT.parent / "OriginPass-wiki"
#: What is presented besides the application: the deck, its script and the
#: silent walkthrough of the new features. All three are built, not committed.
PRESENTATION = {
    "OriginPass-Entrega-3-presentacion.pdf": ROOT / "tools/presentation/build",
    "OriginPass-Entrega-3-guion.md": ROOT / "tools/presentation/build",
    "OriginPass-Entrega-3-recorrido.mp4": ROOT / "tools/video/build",
}
ZIP = DELIVERY / "OriginPass-Portatil.zip"
DEMO_PHOTOS = ("bolso-textil-demo", "estuche-demo", "cesteria-demo")


def main() -> int:
    presentation = [folder / name for name, folder in PRESENTATION.items()]
    for required in (WIKI / "Deliverable-3.md", WIKI / "Daily-Log.md", *presentation):
        if not required.is_file():
            print(f"Missing required source: {required}", file=sys.stderr)
            return 1
    raw = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    tracked = [Path(name.decode()) for name in raw.split(b"\0") if name]
    # Files selected explicitly before their first commit; never sweep all untracked files.
    extra = [Path("companies/migrations/0002_company_evidence_notes_company_publish_consent.py")]
    for prefix in ("companies/management/commands/demo_photos", "static/img/demo"):
        extra.extend(Path(prefix) / f"{name}.jpg" for name in DEMO_PHOTOS)
    sources: dict[str, Path] = {}
    for relative in tracked + extra:
        parts = relative.parts
        if not parts or parts[0] == "delivery":
            continue  # no recursion; setup scripts are added separately
        if any(part in {".venv", "node_modules", "__pycache__", ".git", "media"} for part in parts):
            continue
        if relative.suffix.lower() in {".key", ".pem", ".p12"}:
            continue
        if relative.name.startswith(".env") and relative.name != ".env.example":
            continue
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        sources[f"app/{relative.as_posix()}"] = path
    for name in ("Setup-Portatil.ps1", "Start-OriginPass.ps1", "LEEME-PORTATIL.md"):
        sources[name] = DELIVERY / name
    for page in WIKI.glob("*.md"):
        sources[f"wiki/{page.name}"] = page
    for name, folder in PRESENTATION.items():
        sources[f"presentacion/{name}"] = folder / name
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for target, source in sorted(sources.items()):
            bundle.write(source, target)
    with zipfile.ZipFile(ZIP) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
        for target, source in sources.items():
            if bundle.read(target) != source.read_bytes():
                raise RuntimeError(f"Archive mismatch: {target}")
    digest = hashlib.sha256(ZIP.read_bytes()).hexdigest()
    (DELIVERY / "SHA256SUMS.txt").write_text(
        f"{digest}  OriginPass-Portatil.zip\n", encoding="utf-8"
    )
    print(f"{ZIP} ({ZIP.stat().st_size} bytes, {len(sources)} entries) SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
