"""Local resource metrics for heartbeat reporting."""
import psutil


def get_cpu_usage() -> float:
    return psutil.cpu_percent(interval=0.5)


def get_memory_usage() -> float:
    return psutil.virtual_memory().percent
