"""Measuring the response, for the requirements that state a time bound.

Several requirements are written as "within N seconds", so the test that covers
one of them has to measure rather than assert a shape. This keeps that
measurement in one place instead of restarting a stopwatch in each module.
"""

import time


def measure(call):
    """Run `call` and return what it returned, together with the seconds it took."""
    started = time.perf_counter()
    result = call()
    return result, time.perf_counter() - started
