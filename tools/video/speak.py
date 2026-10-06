
"""Generate the Spanish narration for the Deliverable 3 video with edge-tts.

A stopgap so the video can be assembled and reviewed end to end today:
the pipeline is designed for Emmanuel's own recordings in
`tools/video/voice/`, and replacing any mp3 there with his voice drops
straight into the same assembly.

Run:  python tools/video/speak.py
"""

import asyncio
import sys
from pathlib import Path

import edge_tts

sys.path.insert(0, str(Path(__file__).parent))
from script import RATE, SECTIONS, VOICE  # noqa: E402

VOICE_DIR = Path(__file__).parent / "voice"


async def main():
    VOICE_DIR.mkdir(parents=True, exist_ok=True)
    for section in SECTIONS:
        mp3 = VOICE_DIR / f"{section['id']}.mp3"
        communicate = edge_tts.Communicate(section["text"], VOICE, rate=RATE)
        with open(mp3, "wb") as handle:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    handle.write(chunk["data"])
        print(f"  {section['id']:22} {mp3.stat().st_size / 1024:7.1f} KB")


if __name__ == "__main__":
    asyncio.run(main())
