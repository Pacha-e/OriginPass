"""Turn each section's text into spoken Spanish, and record how long it took.

Every later stage reads the durations written here: a slide stays on screen for
as long as its narration lasts, so the video never drifts out of sync with what
is being said.
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
AUDIO = BUILD / "audio"


async def speak(section):
    """Write one section's mp3 and its sentence-level subtitles."""
    mp3 = AUDIO / f"{section['id']}.mp3"
    srt = AUDIO / f"{section['id']}.srt"

    communicate = edge_tts.Communicate(
        section["text"], VOICE, rate=RATE, boundary="SentenceBoundary"
    )
    submaker = edge_tts.SubMaker()

    with open(mp3, "wb") as handle:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                handle.write(chunk["data"])
            else:
                submaker.feed(chunk)

    srt.write_text(submaker.get_srt(), encoding="utf-8")

    clip = AudioFileClip(str(mp3))
    duration = clip.duration
    clip.close()

    return {
        "id": section["id"],
        "kind": section["kind"],
        "mp3": mp3.name,
        "srt": srt.name,
        "duration": duration,
    }


async def main():
    AUDIO.mkdir(parents=True, exist_ok=True)

    entries = []
    for section in SECTIONS:
        entry = await speak(section)
        entries.append(entry)
        print(f"  {entry['id']:22} {entry['duration']:6.2f} s")

    total = sum(entry["duration"] for entry in entries)
    manifest = {"voice": VOICE, "rate": RATE, "total_narration": total, "sections": entries}
    (BUILD / "narration.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"\nnarration: {total:.1f} s ({total / 60:.1f} min) across {len(entries)} sections")


if __name__ == "__main__":
    asyncio.run(main())
