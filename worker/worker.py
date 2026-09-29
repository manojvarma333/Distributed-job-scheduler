"""Worker process entrypoint: registers with the backend, sends heartbeats, and polls for jobs."""
import os
import socket
import time

import requests
from dotenv import load_dotenv

import executor
from heartbeat import HeartbeatSender

load_dotenv()

WORKER_ID = os.getenv("WORKER_ID", "worker-001")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
POLL_INTERVAL = float(os.getenv("POLL_INTERVAL", "2"))

_current_job = None


def _get_current_job():
    return _current_job


def register():
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
    except socket.gaierror:
        ip_address = "unknown"

    # the backend may not be accepting connections yet (container start order isn't readiness),
    # so retry with backoff instead of crashing on the first attempt.
    while True:
        try:
            requests.post(
                f"{BACKEND_URL}/workers/register",
                json={"worker_id": WORKER_ID, "hostname": socket.gethostname(), "ip_address": ip_address},
                timeout=10,
            )
            print(f"[{WORKER_ID}] registered with backend at {BACKEND_URL}")
            return
        except requests.RequestException as exc:
            print(f"[{WORKER_ID}] backend not reachable yet ({exc}), retrying in {POLL_INTERVAL}s")
            time.sleep(POLL_INTERVAL)


def run_job(job: dict):
    global _current_job
    job_id = job["job_id"]
    _current_job = job_id
    print(f"[{WORKER_ID}] starting job {job_id} ({job['task_type']})")

    requests.post(f"{BACKEND_URL}/jobs/{job_id}/start", timeout=10)
    result = executor.execute(job["task_type"])
    requests.post(f"{BACKEND_URL}/jobs/{job_id}/result", json=result, timeout=10)

    print(f"[{WORKER_ID}] finished job {job_id} -> {result['status']}")
    _current_job = None


def main():
    register()
    heartbeat = HeartbeatSender(WORKER_ID, BACKEND_URL, _get_current_job)
    heartbeat.start()

    print(f"[{WORKER_ID}] polling for jobs every {POLL_INTERVAL}s")
    while True:
        try:
            response = requests.get(f"{BACKEND_URL}/workers/{WORKER_ID}/next-job", timeout=10)
            if response.status_code == 200 and response.json():
                run_job(response.json())
            else:
                time.sleep(POLL_INTERVAL)
        except requests.RequestException as exc:
            print(f"[{WORKER_ID}] connection error: {exc}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
