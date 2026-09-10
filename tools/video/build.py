"""Build the deliverable video from end to end.

    python tools/video/build.py             the finished video, narrated by you
    python tools/video/build.py --preview   a silent preview, to check the visuals
                                      before recording anything

Stages write into `tools/video/build/`, which is not tracked, so the whole video can
be rebuilt from the scripts alone.

The walkthrough stage drives the real application, so it needs the server up:

    docker compose up -d db
    python manage.py migrate
    python manage.py seed_demo
    python manage.py runserver 8765
"""

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
BASE = "http://127.0.0.1:8765"


def server_is_up():
    try:
        urllib.request.urlopen(BASE, timeout=4)
        return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False


def run(filename, label, args=()):
    print(f"\n=== {label} ===")
    started = time.perf_counter()
    result = subprocess.run([sys.executable, str(HERE / filename), *args])
    if result.returncode != 0:
        return result.returncode
    print(f"{label} took {time.perf_counter() - started:.0f} s")
    return 0


def main():
    preview = "--preview" in sys.argv

    stages = [("slides.py", "slides", (), False)]

    if preview:
        stages.append(("reference.py", "reference pace and recording guide", (), False))
    else:
        stages.append(("voiceover.py", "your recordings", (), False))

    stages.append(("record_demo.py", "walkthrough", (), True))
    stages.append(("assemble.py", "final video", ("--silent",) if preview else (), False))

    for filename, label, args, needs_server in stages:
        if needs_server and not server_is_up():
            print(f"\n{label}: no server answering at {BASE}.")
            print("Start it with:  python manage.py runserver 8765")
            return 1

        code = run(filename, label, args)
        if code != 0:
            print(f"\n{label} failed")
            return code

    name = "OriginPass-Entrega-1-preview.mp4" if preview else "OriginPass-Entrega-1.mp4"
    print(f"\nDone. tools/video/build/{name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
