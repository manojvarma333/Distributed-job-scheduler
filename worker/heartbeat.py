"""Background thread that sends periodic heartbeats (CPU/RAM/current job) to the scheduler."""
import threading
import time

import requests

from metrics import get_cpu_usage, get_memory_usage


class HeartbeatSender(threading.Thread):
    def __init__(self, worker_id: str, backend_url: str, get_current_job, interval: int = 5):
        super().__init__(daemon=True)
        self.worker_id = worker_id
        self.backend_url = backend_url
        self.get_current_job = get_current_job
        self.interval = interval
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            try:
                requests.post(
                    f"{self.backend_url}/workers/{self.worker_id}/heartbeat",
                    json={
                        "cpu_usage": get_cpu_usage(),
                        "memory_usage": get_memory_usage(),
                        "current_job": self.get_current_job(),
                    },
                    timeout=10,
                )
            except requests.RequestException as exc:
                print(f"[{self.worker_id}] heartbeat failed: {exc}")
            self._stop_event.wait(self.interval)
