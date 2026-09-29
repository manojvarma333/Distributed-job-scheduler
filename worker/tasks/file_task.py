"""File processing task: writes, reads, and cleans up a temp file."""
import os
import tempfile
import uuid


def run():
    path = os.path.join(tempfile.gettempdir(), f"job_scheduler_{uuid.uuid4().hex}.txt")
    line_count = 2000
    with open(path, "w", encoding="utf-8") as f:
        for i in range(line_count):
            f.write(f"line {i}\n")

    with open(path, encoding="utf-8") as f:
        counted = sum(1 for _ in f)

    os.remove(path)
    return f"File task processed {counted} lines"
