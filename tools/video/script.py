"""Which script the video pipeline reads.

`script.py` has always been the single source the stages import. Rather than
fork every stage, the module stays and picks the edition from the
VIDEO_SCRIPT environment variable, defaulting to the current deliverable:

    VIDEO_SCRIPT=d1 python tools/video/build.py   # the Deliverable 1 edition
    python tools/video/build.py                    # Deliverable 3 (default)

This file is the only place that knows both editions exist.
"""

import os

_edition = os.environ.get("VIDEO_SCRIPT", "d3").lower()

if _edition == "d1":
    from script_d1 import GAP, RATE, SECTIONS, VOICE  # noqa: F401
elif _edition == "d3":
    from script_d3 import GAP, RATE, SECTIONS, VOICE  # noqa: F401
else:
    raise SystemExit(
        f"VIDEO_SCRIPT={_edition!r} is not an edition. Use 'd1' or 'd3'."
    )
