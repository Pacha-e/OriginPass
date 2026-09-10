"""Put the slides, the walkthrough and the narration together into one MP4.

Each section lasts exactly as long as its own narration plus a short gap, so
nothing has to be timed by hand. The walkthrough is stretched or compressed to
the length of the narration that plays over it, which keeps what is being said
lined up with what is on screen.

    python tools/video/assemble.py            uses the recordings in tools/video/voice/
    python tools/video/assemble.py --silent   builds a preview with no audio, timed
                                        to the reference pace, for checking the
                                        visuals before recording anything
"""

import json
import re
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
DEMO = BUILD / "demo.webm"

WIDTH, HEIGHT = 1920, 1080
FPS = 30


def srt_time(seconds):
    delta = timedelta(seconds=seconds)
    hours, rest = divmod(delta.seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02}:{minutes:02}:{secs:02},{delta.microseconds // 1000:03}"


def cues_for(text, start, duration, index):
    """Split a section's text into sentence cues across its own duration.

    Each sentence gets a share of the time proportional to its length. It is an
    approximation of where the words fall, which is enough for subtitles and
    needs no speech recognition.
    """
    sentences = [s.strip() for s in re.split(r"(?<=[.:?!])\s+", text.strip()) if s.strip()]
    total_chars = sum(len(s) for s in sentences) or 1

    blocks, offset = [], start
    for sentence in sentences:
        span = duration * len(sentence) / total_chars
        blocks.append(f"{index}\n{srt_time(offset)} --> {srt_time(offset + span)}\n{sentence}")
        offset += span
        index += 1
    return blocks, index


def demo_clip(duration):
    """The walkthrough, fitted to the narration that plays over it."""
    clip = VideoFileClip(str(DEMO))
    fitted = clip.with_speed_scaled(clip.duration / duration)

    scaled = fitted.resized(width=WIDTH)
    if scaled.h > HEIGHT:
        scaled = fitted.resized(height=HEIGHT)

    return CompositeVideoClip(
        [scaled.with_position("center")], size=(WIDTH, HEIGHT), bg_color=(246, 247, 249)
    ).with_duration(duration)


def load_timing(silent):
    """Where the durations come from: the recordings, or the reference pace."""
    if silent:
        path = BUILD / "reference.json"
        if not path.exists():
            raise SystemExit("No reference.json. Run `python tools/video/reference.py` first.")
        data = json.loads(path.read_text(encoding="utf-8"))
        return {entry["id"]: (entry["duration"], None) for entry in data["sections"]}

    path = BUILD / "narration.json"
    if not path.exists():
        raise SystemExit("No narration.json. Run `python tools/video/voiceover.py` first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {entry["id"]: (entry["duration"], entry["path"]) for entry in data["sections"]}


def main():
    silent = "--silent" in sys.argv
    timing = load_timing(silent)

    suffix = "-preview" if silent else ""
    out = BUILD / f"OriginPass-Entrega-1{suffix}.mp4"
    srt_out = BUILD / f"OriginPass-Entrega-1{suffix}.srt"

    clips, srt_blocks, index, offset = [], [], 1, 0.0

    for section in SECTIONS:
        duration, audio_path = timing[section["id"]]
        length = duration + GAP

        if section["kind"] == "slide":
            visual = ImageClip(str(SLIDES / f"{section['id']}.png")).with_duration(length)
        else:
            visual = demo_clip(length)

        if audio_path:
            visual = visual.with_audio(AudioFileClip(audio_path))

        clips.append(visual.with_fps(FPS))

        blocks, index = cues_for(section["text"], offset, duration, index)
        srt_blocks += blocks
        offset += length

        print(f"  {section['id']:22} {length:6.2f} s   ends {offset:7.2f} s")

    video = concatenate_videoclips(clips, method="compose")

    print(f"\nwriting {out.name} — {video.duration:.1f} s ({video.duration / 60:.2f} min)")
    video.write_videofile(
        str(out),
        fps=FPS,
        codec="libx264",
        audio_codec="aac" if not silent else None,
        audio=not silent,
        preset="medium",
        threads=4,
        temp_audiofile=str(BUILD / "temp-audio.m4a"),
        logger=None,
    )

    srt_out.write_text("\n\n".join(srt_blocks) + "\n", encoding="utf-8")

    print(f"video:     {out}  ({out.stat().st_size / 1_048_576:.1f} MB)")
    print(f"subtitles: {srt_out.name}  ({len(srt_blocks)} cues)")
    if silent:
        print("\nThis is the silent preview. Record the narration, then run the build again.")


if __name__ == "__main__":
    main()
