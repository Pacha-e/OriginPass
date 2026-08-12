# Video production

Builds the Deliverable 1 presentation video from a script, without recording a
screen by hand and without editing software. Everything is reproducible: change
a sentence in `script.py`, run the build, and the video comes out with the new
narration and with every slide re-timed to fit it.

## What each file does

| File | What it produces |
|---|---|
| `script.py` | The narration and the slide content, in one place. Nothing else holds copy. |
| `narrate.py` | One MP3 and one SRT per section, spoken in Colombian Spanish, plus the durations everything else is timed from |
| `slides.py` | One 1920×1080 PNG per slide, built as HTML and rendered in a browser |
| `record_demo.py` | The application walkthrough, driven through a real browser and recorded to WebM |
| `assemble.py` | The final MP4 and a subtitle file covering the whole video |
| `build.py` | Runs the four in order |

## Running it

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
python video/build.py
```

Output lands in `video/build/`, which is not tracked.

## How the timing works

No duration is written by hand. `narrate.py` speaks each section and measures
how long the speech turned out to be; every later stage reads those numbers. A
slide is held for exactly as long as its own narration, and the walkthrough is
stretched or compressed to the length of the narration that plays over it. Edit
the script and the timing follows on its own.

## Choices worth knowing about

**The voice is `es-CO-GonzaloNeural`,** a Colombian Spanish neural voice from
Microsoft Edge's speech service. It needs no API key. The rate is set 8 per cent
below default, because the default lands around 200 words a minute, which is
faster than a person presenting.

**The narration is Spanish, the code and the documentation are English.** The
pedagogical agreement requires deliverables and artefacts to be written in
English; the video is presented in Spanish, which is the language of the class.

**To narrate it yourself instead,** record one audio file per section into
`video/build/audio/` using the same names, and run `slides.py` and `assemble.py`
without `narrate.py`. The rest of the pipeline does not care where the audio came
from, only how long it is — except that `assemble.py` reads durations from
`narration.json`, so that file has to be updated to match.

**The slides borrow the application's palette** so the deck and the product look
like one thing. They are plain HTML and CSS rendered in a headless browser,
which means any layout the browser can draw is available, and no presentation
software is involved.
