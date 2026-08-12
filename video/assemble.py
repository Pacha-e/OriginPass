"""Put the slides, the walkthrough and the narration together into one MP4.

Each section lasts exactly as long as its own narration plus a short gap, so
nothing has to be timed by hand. The walkthrough is stretched or compressed to
the length of the narration that plays over it, which keeps what is being said
lined up with what is on screen.
"""

import json
import sys
from datetime import timedelta
from pathlib import Path

from moviepy import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)

sys.path.insert(0, str(Path(__file__).parent))
from script import GAP, SECTIONS  # noqa: E402

BUILD = Path(__file__).parent / "build"
SLIDES = BUILD / "slides"
AUDIO = BUILD / "audio"
DEMO = BUILD / "demo.webm"
OUT = BUILD / "OriginPass-Entrega-1.mp4"
SRT_OUT = BUILD / "OriginPass-Entrega-1.srt"

WIDTH, HEIGHT = 1920, 1080
FPS = 30


def srt_time(seconds):
    delta = timedelta(seconds=seconds)
    hours, rest = divmod(delta.seconds, 3600)
    minutes, secs = divmod(rest, 60)
    millis = delta.microseconds // 1000
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def shift_srt(text, offset, start_index):
    """Move one section's subtitles onto the timeline of the whole video."""
    blocks, index = [], start_index
    for raw in text.strip().split("\n\n"):
        lines = raw.splitlines()
        if len(lines) < 3:
            continue
        start, end = lines[1].split(" --> ")

        def parse(stamp):
            clock, millis = stamp.strip().split(",")
            hours, minutes, secs = clock.split(":")
            return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(millis) / 1000

        blocks.append(
            f"{index}\n"
            f"{srt_time(parse(start) + offset)} --> {srt_time(parse(end) + offset)}\n"
            + "\n".join(lines[2:])
        )
        index += 1
    return blocks, index


def demo_clip(duration):
    """The walkthrough, fitted to the narration that plays over it."""
    clip = VideoFileClip(str(DEMO))
    factor = clip.duration / duration
    fitted = clip.with_speed_scaled(factor)

    # Recorded at 1600x900; centred on the 1920x1080 canvas against the same
    # background the slides use, so the change of scene is not a jolt.
    scaled = fitted.resized(width=WIDTH)
    if scaled.h > HEIGHT:
        scaled = fitted.resized(height=HEIGHT)

    return CompositeVideoClip(
        [scaled.with_position("center")], size=(WIDTH, HEIGHT), bg_color=(246, 247, 249)
    ).with_duration(duration)


def main():
    manifest = json.loads((BUILD / "narration.json").read_text(encoding="utf-8"))
    durations = {entry["id"]: entry["duration"] for entry in manifest["sections"]}

    clips, srt_blocks, index, offset = [], [], 1, 0.0

    for section in SECTIONS:
        section_id = section["id"]
        narration = AudioFileClip(str(AUDIO / f"{section_id}.mp3"))
        length = durations[section_id] + GAP

        if section["kind"] == "slide":
            visual = ImageClip(str(SLIDES / f"{section_id}.png")).with_duration(length)
        else:
            visual = demo_clip(length)

        clips.append(visual.with_audio(narration).with_fps(FPS))

        blocks, index = shift_srt(
            (AUDIO / f"{section_id}.srt").read_text(encoding="utf-8"), offset, index
        )
        srt_blocks += blocks
        offset += length

        print(f"  {section_id:22} {length:6.2f} s   ends {offset:7.2f} s")

    video = concatenate_videoclips(clips, method="compose")

    print(f"\nwriting {OUT.name} — {video.duration:.1f} s ({video.duration / 60:.2f} min)")
    video.write_videofile(
        str(OUT),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        threads=4,
        logger=None,
    )

    SRT_OUT.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

    print(f"video:     {OUT}  ({OUT.stat().st_size / 1_048_576:.1f} MB)")
    print(f"subtitles: {SRT_OUT.name}  ({len(srt_blocks)} cues)")


if __name__ == "__main__":
    main()
