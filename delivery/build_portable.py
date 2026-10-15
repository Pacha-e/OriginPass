"""Rebuild the Windows presentation ZIP from the current working tree (no secrets)."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELIVERY = ROOT / "delivery"
WIKI = ROOT / "docs/wiki"
#: What is presented besides the application: the deck, its script and the
#: silent walkthrough of the new features. These are built, not committed.
PRESENTATION = {
    "OriginPass-Entrega-3-presentacion.pdf": ROOT / "tools/presentation/build",
    "OriginPass-Entrega-3-guion.md": ROOT / "tools/presentation/build",
    "OriginPass-Entrega-3-presentacion.html": ROOT / "tools/presentation/build",
    "OriginPass-Entrega-3-recorrido.mp4": ROOT / "tools/video/build",
}
ZIP = DELIVERY / "OriginPass-Portatil.zip"
MEDIA = DELIVERY / "build/videos"


def sha256(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch-videos", action="store_true")
    options = parser.parse_args()
    media = json.loads((DELIVERY / "media-manifest.json").read_text(encoding="utf-8"))
    MEDIA.mkdir(parents=True, exist_ok=True)
    for asset in media["assets"] + media.get("support_assets", []):
        destination = ROOT / asset.get("directory", "delivery/build/videos")
        destination.mkdir(parents=True, exist_ok=True)
        path = destination / asset["name"]
        if not path.is_file() and options.fetch_videos:
            subprocess.run(
                [
                    "gh",
                    "release",
                    "download",
                    asset.get("release", media["release"]),
                    "--repo",
                    "Pacha-e/OriginPass",
                    "--pattern",
                    asset["name"],
                    "--dir",
                    str(destination),
                    "--skip-existing",
                ],
                check=True,
            )
        if not path.is_file():
            raise FileNotFoundError(f"{path}: run this builder with --fetch-videos")
        if path.stat().st_size != asset["size"] or sha256(path) != asset["sha256"]:
            raise ValueError(f"Published video checksum mismatch: {asset['name']}")
    presentation = [folder / name for name, folder in PRESENTATION.items()]
    for required in (
        WIKI / "Deliverable-3.md",
        WIKI / "Daily-Log.md",
        *presentation,
    ):
        if not required.is_file():
            print(f"Missing required source: {required}", file=sys.stderr)
            return 1
    raw = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True
    ).stdout
    tracked = [Path(name.decode()) for name in raw.split(b"\0") if name]
    # Files selected explicitly before their first commit; never sweep all untracked files.
    extra = [Path("tools/presentation/render_diagrams.py")]
    for stem in (
        "deployment-model-Deployment-model",
        "components-model-Component-model",
        "data-model-Data-model",
    ):
        extra.extend(Path("docs/diagrams/export") / f"{stem}.{ext}" for ext in ("pdf", "svg"))
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
    for name in (
        "Setup-Portatil.ps1",
        "Start-OriginPass.ps1",
        "LEEME-PORTATIL.md",
        "ABRIR-KIT.html",
        "Verificar-Kit.ps1",
        "verify_kit.py",
        "demo_links.py",
        "CREDITOS-VIDEOS.md",
        "media-manifest.json",
        "docker-compose.kit.yml",
    ):
        sources[name] = DELIVERY / name
    for page in WIKI.glob("*.md"):
        sources[f"wiki/{page.name}"] = page
    for name, folder in PRESENTATION.items():
        sources[f"presentacion/{name}"] = folder / name
    diagrams = ROOT / "tools/presentation/build/diagramas"
    for name in (
        "index.html",
        *(
            f"{stem}.{ext}"
            for stem in (
                "deployment-model-Deployment-model",
                "components-model-Component-model",
                "data-model-Data-model",
            )
            for ext in ("pdf", "svg", "png")
        ),
        "deployment-model.drawio",
        "components-model.drawio",
        "data-model.drawio",
    ):
        source = diagrams / name
        if not source.is_file():
            raise FileNotFoundError(source)
        sources[f"presentacion/diagramas/{name}"] = source
    captures = ROOT / "tools/presentation/build/capturas"
    for source in [captures / "index.html", *sorted(captures.glob("*.png"))]:
        sources[f"presentacion/capturas/{source.name}"] = source
    for asset in media["assets"]:
        sources[f"videos/{asset['name']}"] = MEDIA / asset["name"]
    build = DELIVERY / "build"
    placeholder = build / "ABRIR-DEMO.html"
    placeholder.write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<h1>Prepara la demostración</h1><p>Ejecuta Setup-Portatil.ps1. "
        "Creará aquí los enlaces con los pasaportes de este equipo.</p></html>",
        encoding="utf-8",
    )
    sources[placeholder.name] = placeholder
    manifest = {
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
        ).strip(),
        "built_at": datetime.now(UTC).isoformat(),
        "files": {
            name: {"size": source.stat().st_size, "sha256": sha256(source)}
            for name, source in sorted(sources.items())
            if name != "ABRIR-DEMO.html"  # Rebuilt by setup for the local demo database.
        },
    }
    manifest_path = build / "KIT-MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    sources[manifest_path.name] = manifest_path
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for target, source in sorted(sources.items()):
            bundle.write(source, target)
    with zipfile.ZipFile(ZIP) as bundle:
        if bundle.testzip() is not None:
            raise RuntimeError("ZIP CRC verification failed")
        for target, source in sources.items():
            if bundle.read(target) != source.read_bytes():
                raise RuntimeError(f"Archive mismatch: {target}")
    digest = sha256(ZIP)
    (DELIVERY / "SHA256SUMS.txt").write_text(
        f"{digest}  OriginPass-Portatil.zip\n", encoding="utf-8"
    )
    print(f"{ZIP} ({ZIP.stat().st_size} bytes, {len(sources)} entries) SHA-256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
