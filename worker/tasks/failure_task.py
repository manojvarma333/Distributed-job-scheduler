"""Intentionally-flaky task used to demonstrate the retry/fault-tolerance mechanism."""
import random


def run():
    if random.random() < 0.6:
        raise RuntimeError("Simulated random failure")
    return "Random failure task succeeded this time"
