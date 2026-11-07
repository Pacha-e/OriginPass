"""The six-digit handover code: rotates every two minutes, dies with the handover."""

from datetime import UTC, datetime, timedelta

from django.test import TestCase

from products.handover import (
    GRACE_SECONDS,
    WINDOW_SECONDS,
    check_handover_code,
    handover_code,
    is_locked,
    normalise,
    record_failure,
    seconds_left,
)

# The start of a two-minute window, so offsets below are easy to read.
START = datetime.fromtimestamp(WINDOW_SECONDS * 15_000_000, tz=UTC)
ARGS = ("product", 7, "12", 0)


class HandoverCodeTests(TestCase):
    def test_same_code_within_window(self):
        self.assertEqual(
            handover_code(*ARGS, START), handover_code(*ARGS, START + timedelta(seconds=119))
        )

    def test_code_changes_next_window(self):
        self.assertNotEqual(
            handover_code(*ARGS, START), handover_code(*ARGS, START + timedelta(seconds=120))
        )

    def test_accepts_previous_code_within_15_seconds(self):
        code = handover_code(*ARGS, START - timedelta(seconds=1))
        at = START + timedelta(seconds=GRACE_SECONDS)
        self.assertTrue(check_handover_code(*ARGS, code, at))

    def test_refuses_previous_code_after_15_seconds(self):
        code = handover_code(*ARGS, START - timedelta(seconds=1))
        at = START + timedelta(seconds=GRACE_SECONDS + 1)
        self.assertFalse(check_handover_code(*ARGS, code, at))

    def test_code_dies_when_holder_or_counter_changes(self):
        code = handover_code(*ARGS, START)
        self.assertFalse(check_handover_code("product", 7, "13", 0, code, START))
        self.assertFalse(check_handover_code("product", 7, "12", 1, code, START))
        self.assertFalse(check_handover_code("batch", 7, "12", 0, code, START))

    def test_normalises_spaces_and_hyphen(self):
        code = handover_code(*ARGS, START)
        spaced = f"{code[:3]} {code[3:]}"
        hyphened = f"{code[:3]}-{code[3:]}"
        self.assertEqual(normalise(spaced), code)
        self.assertTrue(check_handover_code(*ARGS, spaced, START))
        self.assertTrue(check_handover_code(*ARGS, hyphened, START))

    def test_code_is_six_digits_with_leading_zeros(self):
        codes = {handover_code("product", pk, "12", 0, START) for pk in range(400)}
        self.assertTrue(all(len(code) == 6 and code.isdigit() for code in codes))
        self.assertTrue(any(code.startswith("0") for code in codes))

    def test_wrong_length_or_empty_is_refused(self):
        self.assertFalse(check_handover_code(*ARGS, "", START))
        self.assertFalse(check_handover_code(*ARGS, "12345", START))

    def test_seconds_left_counts_down_the_window(self):
        self.assertEqual(seconds_left(START), 120)
        self.assertEqual(seconds_left(START + timedelta(seconds=119)), 1)


class HandoverLockTests(TestCase):
    def test_five_failures_lock_for_fifteen_minutes(self):
        for minute in range(5):
            self.assertFalse(is_locked("product", 7, START + timedelta(minutes=minute)))
            record_failure("product", 7, START + timedelta(minutes=minute))

        self.assertTrue(is_locked("product", 7, START + timedelta(minutes=5)))
        self.assertFalse(is_locked("product", 8, START + timedelta(minutes=5)))
        self.assertFalse(is_locked("batch", 7, START + timedelta(minutes=5)))
        self.assertFalse(is_locked("product", 7, START + timedelta(minutes=20)))
