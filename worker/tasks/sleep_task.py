"""Simple sleep task, useful for observing QUEUED/RUNNING transitions."""
import time


def run():
    time.sleep(5)
    return "Sleep task completed after 5 seconds"
