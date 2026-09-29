"""Memory-bound task: allocates and touches a moderate chunk of memory."""


def run():
    chunk_mb = 1
    chunk_count = 50
    chunks = [bytearray(chunk_mb * 1024 * 1024) for _ in range(chunk_count)]
    for chunk in chunks:
        chunk[0] = 1  # touch each page so it's actually resident
    total_mb = sum(len(c) for c in chunks) / (1024 * 1024)
    return f"Memory task allocated and touched {total_mb:.0f}MB"
