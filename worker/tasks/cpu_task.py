"""CPU-bound task: keeps a core busy for a few seconds."""
import time


def run():
    duration_seconds = 5
    end = time.time() + duration_seconds
    total = 0
    while time.time() < end:
        total += sum(i * i for i in range(2000))
    return f"CPU task completed after {duration_seconds}s, computed checksum {total}"
