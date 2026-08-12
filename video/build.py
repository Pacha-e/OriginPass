"""Build the deliverable video from end to end.

    python video/build.py

Runs the four stages in order. Each writes into `video/build/`, which is not
tracked, so the whole video can be rebuilt from the scripts alone.

The walkthrough stage needs the application running:

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

STAGES = [
    ("narrate.py", "narration", False),
    ("slides.py", "slides", False),
    ("record_demo.py", "walkthrough", True),
    ("assemble.py", "final video", False),
]


def server_is_up():
    try:
        urllib.request.urlopen(BASE, timeout=4)
        return True
    except urllib.error.HTTPError:
        return True
    except Exception:
        return False


def main():
    for filename, label, needs_server in STAGES:
        if needs_server and not server_is_up():
            print(f"\n{label}: no server answering at {BASE}.")
            print("Start it with:  python manage.py runserver 8765")
            return 1

        print(f"\n=== {label} ===")
        started = time.perf_counter()
        result = subprocess.run([sys.executable, str(HERE / filename)])
        if result.returncode != 0:
            print(f"{label} failed")
            return result.returncode
        print(f"{label} took {time.perf_counter() - started:.0f} s")

    print("\nDone. video/build/OriginPass-Entrega-1.mp4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
