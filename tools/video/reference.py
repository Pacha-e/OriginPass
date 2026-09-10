"""Produce a pacing reference and a recording guide. Never part of the video.

The final video is narrated by Emmanuel. This module only helps him record it:
it speaks each section with a synthetic voice so there is something to listen to
for pacing, and it writes a guide with the text to read and how long each
section should take.

Nothing here is used by `assemble.py`. The audio it writes goes to
`build/reference/`, which the assembly stage never reads.
"""

import asyncio
import json
import sys
from pathlib import Path

import edge_tts
from moviepy import AudioFileClip

sys.path.insert(0, str(Path(__file__).parent))
from script import RATE, SECTIONS, VOICE  # noqa: E402

BUILD = Path(__file__).parent / "build"
REFERENCE = BUILD / "reference"
GUIDE = BUILD / "recording-guide.md"


async def speak(section):
    mp3 = REFERENCE / f"{section['id']}.mp3"

    communicate = edge_tts.Communicate(section["text"], VOICE, rate=RATE)
    with open(mp3, "wb") as handle:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                handle.write(chunk["data"])

    clip = AudioFileClip(str(mp3))
    duration = clip.duration
    clip.close()
    return duration


def write_guide(entries):
    lines = [
        "# Recording guide",
        "",
        "Read one section per file. Save each as `tools/video/voice/<id>.mp3` using the",
        "names in the table, then run `python tools/video/build.py`.",
        "",
        "The target time is what a synthetic voice took at a natural pace. Treat it as a",
        "guide, not a limit: every slide is held for exactly as long as your own",
        "recording, so going over or under only changes the length of the video.",
        "",
        "| File to save | Target | Words |",
        "|---|---|---|",
    ]
    for entry in entries:
        recording = f"`tools/video/voice/{entry['id']}.mp3`"
        lines.append(f"| {recording} | {entry['duration']:.0f} s | {entry['words']} |")

    total = sum(entry["duration"] for entry in entries)
    lines += [
        "",
        f"Total at the reference pace: **{total / 60:.1f} minutes**. "
        "The deliverable asks for five to seven.",
        "",
        "---",
        "",
        "## What to read",
        "",
    ]

    for section in SECTIONS:
        entry = next(e for e in entries if e["id"] == section["id"])
        lines += [
            f"### `{section['id']}.mp3` — {entry['duration']:.0f} s",
            "",
            section["text"],
            "",
        ]
        if section["kind"] == "demo":
            lines += [
                "> This one plays over the recorded walkthrough of the application. "
                "The walkthrough is fitted to however long your recording is, so the "
                "two stay together whatever pace you take.",
                "",
            ]

    GUIDE.write_text("\n".join(lines), encoding="utf-8")


async def main():
    REFERENCE.mkdir(parents=True, exist_ok=True)

    entries = []
    for section in SECTIONS:
        duration = await speak(section)
        entries.append(
            {
                "id": section["id"],
                "kind": section["kind"],
                "duration": duration,
                "words": len(section["text"].split()),
            }
        )
        print(f"  {section['id']:22} {duration:6.2f} s")

    (BUILD / "reference.json").write_text(
        json.dumps({"sections": entries}, indent=2), encoding="utf-8"
    )
    write_guide(entries)

    total = sum(entry["duration"] for entry in entries)
    print(f"\nreference pace: {total / 60:.1f} min")
    print(f"guide written to {GUIDE}")
    print("\nThis audio is a pacing reference only. It is never used in the video.")


if __name__ == "__main__":
    asyncio.run(main())
