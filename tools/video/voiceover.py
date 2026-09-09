"""Read Emmanuel's recordings and time the video to them.

Put one file per section in `tools/video/voice/`, named after the section id. Any
format ffmpeg reads will do: mp3, m4a, wav, ogg. This measures each one and
writes the manifest that the assembly stage times everything from, so each
slide is held for exactly as long as the sentence spoken over it.

If a recording is missing this says which one, and how long the reference pace
suggests it should be, rather than failing on an obscure path error.
"""

import json
import sys
from pathlib import Path

from moviepy import AudioFileClip

sys.path.insert(0, str(Path(__file__).parent))
from script import SECTIONS  # noqa: E402

VOICE = Path(__file__).parent / "voice"
BUILD = Path(__file__).parent / "build"

EXTENSIONS = [".mp3", ".m4a", ".wav", ".ogg", ".flac"]


def recording_for(section_id):
    for extension in EXTENSIONS:
        candidate = VOICE / f"{section_id}{extension}"
        if candidate.exists():
            return candidate
    return None


def reference_durations():
    path = BUILD / "reference.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {entry["id"]: entry["duration"] for entry in data["sections"]}


def main():
    VOICE.mkdir(parents=True, exist_ok=True)
    hints = reference_durations()

    found, missing = [], []
    for section in SECTIONS:
        path = recording_for(section["id"])
        if path is None:
            missing.append(section["id"])
            continue

        clip = AudioFileClip(str(path))
        duration = clip.duration
        clip.close()

        found.append(
            {
                "id": section["id"],
                "kind": section["kind"],
                "path": str(path),
                "duration": duration,
            }
        )
        print(f"  {section['id']:22} {duration:6.2f} s   {path.name}")

    if missing:
        print(f"\n{len(missing)} recording(s) missing from {VOICE}:\n")
        for section_id in missing:
            hint = hints.get(section_id)
            target = f"about {hint:.0f} s" if hint else "see the recording guide"
            print(f"  {section_id}.mp3    ({target})")
        print("\nRun `python tools/video/reference.py` for the guide with the text to read.")
        return 1

    total = sum(entry["duration"] for entry in found)
    (BUILD / "narration.json").write_text(
        json.dumps({"source": "voice", "total_narration": total, "sections": found}, indent=2),
        encoding="utf-8",
    )

    print(f"\nnarration: {total:.1f} s ({total / 60:.1f} min) across {len(found)} sections")
    if not 300 <= total <= 420:
        print("note: the deliverable asks for five to seven minutes of finished video.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
