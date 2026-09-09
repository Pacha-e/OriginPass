# Video production

Builds the Deliverable 1 presentation video from a script, without editing
software. **The narration is recorded by Emmanuel.** Nothing synthetic reaches
the finished video.

## What each file does

| File | What it produces |
|---|---|
| `script.py` | The narration text and the slide content, in one place. Nothing else holds copy. |
| `slides.py` | One 1920×1080 PNG per slide, built as HTML and rendered in a browser |
| `record_demo.py` | The application walkthrough, driven through a real browser and recorded to WebM |
| `reference.py` | A recording guide, and a synthetic read of each section **to hear the pace only** |
| `voiceover.py` | Measures your recordings and writes the timing everything else follows |
| `assemble.py` | The final MP4 and a subtitle file covering the whole video |
| `build.py` | Runs them in order |

## Recording the narration

```bash
python tools/video/reference.py
```

Writes `build/recording-guide.md`: a table of the twelve files to record, what to
read in each, and roughly how long each should take. It also writes a synthetic
read of every section into `build/reference/`, which exists so you can hear the
intended pace. **That audio is never used in the video.**

Record one file per section and save them in `tools/video/voice/`, named after the
section id:

```
tools/video/voice/01-title.mp3
tools/video/voice/02-problem.mp3
...
tools/video/voice/11-close.mp3
```

Any format ffmpeg reads works: mp3, m4a, wav, ogg, flac. Recording one file per
section rather than a single take means a section can be redone without
re-recording the rest.

The target times are guides, not limits. Every slide is held for exactly as long
as your own recording, so taking longer on a section simply makes the video
longer.

## Building it

The walkthrough drives the real application, so the database has to be up and
seeded first:

```bash
docker compose up -d db
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 8765
```

Then, in another terminal:

```bash
pip install edge-tts playwright moviepy imageio-ffmpeg
python -m playwright install chromium

python tools/video/build.py --preview   # silent, to check the visuals first
python tools/video/build.py             # the finished video, with your narration
```

Output lands in `tools/video/build/`, which is not tracked.

## How the timing works

No duration is written by hand. `voiceover.py` measures each of your recordings,
and every later stage reads those numbers. A slide is held for exactly as long as
the sentence spoken over it, and the walkthrough is stretched or compressed to
the length of the narration that plays over it. Re-record a section and the video
re-times itself on the next build.

Subtitles are produced by splitting each section's text into sentences and giving
each one a share of that section's time proportional to its length. It is an
approximation of where the words fall, which is enough for subtitles and needs no
speech recognition.

## Choices worth knowing about

**The slides borrow the application's palette** so the deck and the product look
like one thing. They are plain HTML and CSS rendered in a headless browser, which
means any layout a browser can draw is available and no presentation software is
involved.

**The narration is Spanish, the code and the documentation are English.** The
pedagogical agreement requires deliverables and artefacts to be written in
English; the video is presented in Spanish, which is the language of the class.

**The interface in the walkthrough is still English.** Rendering it in Spanish is
UR04, which belongs to Sprint 2. Once that ships, rebuilding picks up the
translated interface without the narration or the slides being touched.
