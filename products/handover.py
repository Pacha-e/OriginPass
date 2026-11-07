"""The six-digit code that authorises handing a piece, or a batch, over in person.

Reading a QR identifies a piece; it gives no right over it. The right comes from
this code, which only the current holder sees on their phone and says aloud.

The code is never stored. It is an HMAC, under a key derived from SECRET_KEY, of
what it is for (a product or a batch and its id), who holds it now, how many
times it has changed hands, and the two-minute window it belongs to. So it
changes every two minutes on its own, and it stops working the moment the
handover happens, because the holder and the count it was made from change.

A code read in the last seconds of a window is still accepted for GRACE_SECONDS
into the next one, so a person typing it as it rolls over is not refused. Wrong
guesses are counted per piece or batch: MAX_FAILURES within LOCK_MINUTES lock it
for the rest of that span, which keeps a million combinations out of reach.
"""

import hmac
from datetime import timedelta

from django.conf import settings
from django.utils.crypto import salted_hmac

# ---- Constants ----

WINDOW_SECONDS = 120
GRACE_SECONDS = 15
MAX_FAILURES = 5
LOCK_MINUTES = 15
CODE_DIGITS = 6

#: Namespaces the derived key, so this HMAC can never be mistaken for a record
#: signature made with the same SECRET_KEY.
KEY_SALT = "originpass.handover.v1"
SEPARATOR = "\x1f"


# ---- Public API ----


def handover_code(subject, subject_id, holder_key, counter, at):
    """The code for `subject` ("product" or "batch") in the window holding `at`."""
    return _code(subject, subject_id, holder_key, counter, _window(at))


def seconds_left(at):
    """Seconds until the code shown at `at` changes, from WINDOW_SECONDS down to 1."""
    return WINDOW_SECONDS - int(at.timestamp()) % WINDOW_SECONDS


def normalise(typed):
    """Only the digits: people say and type codes as "482 913" or "482-913"."""
    return "".join(character for character in typed if character.isdigit())


def check_handover_code(subject, subject_id, holder_key, counter, typed, at):
    """Whether `typed` is the code now, or the previous one within the grace."""
    typed = normalise(typed)
    if len(typed) != CODE_DIGITS:
        return False
    window = _window(at)
    windows = [window]
    if int(at.timestamp()) % WINDOW_SECONDS <= GRACE_SECONDS:
        windows.append(window - 1)
    # Every candidate is compared, so the time taken says nothing about which matched.
    matches = [
        hmac.compare_digest(typed, _code(subject, subject_id, holder_key, counter, candidate))
        for candidate in windows
    ]
    return any(matches)


def is_locked(subject, subject_id, at):
    """Whether too many wrong codes were typed for this piece or batch lately."""
    from products.models import HandoverAttempt

    since = at - timedelta(minutes=LOCK_MINUTES)
    failures = HandoverAttempt.objects.filter(
        subject=subject, subject_id=subject_id, failed_at__gt=since, failed_at__lte=at
    ).count()
    return failures >= MAX_FAILURES


def record_failure(subject, subject_id, at):
    from products.models import HandoverAttempt

    HandoverAttempt.objects.create(subject=subject, subject_id=subject_id, failed_at=at)


# ---- Private helpers ----


def _window(at):
    return int(at.timestamp()) // WINDOW_SECONDS


def _code(subject, subject_id, holder_key, counter, window):
    payload = SEPARATOR.join(
        str(part) for part in (subject, subject_id, holder_key, counter, window)
    )
    digest = salted_hmac(KEY_SALT, payload, secret=settings.SECRET_KEY, algorithm="sha256").digest()
    number = int.from_bytes(digest[:8], "big") % 10**CODE_DIGITS
    return str(number).zfill(CODE_DIGITS)
