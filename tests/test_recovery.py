"""Recovery tests: heartbeat timeout detection, job reassignment, and retry-limit handling."""
import time
from datetime import datetime, timedelta, timezone

from app.database.connection import SessionLocal
from app.models.job import Job, JobStatus
from app.models.worker import Worker, WorkerStatus
from app.services.recovery import check_worker_timeouts


def test_heartbeat_timeout_marks_worker_offline(client):
    client.post("/workers/register", json={"worker_id": "worker-001"})

    db = SessionLocal()
    worker = db.query(Worker).filter(Worker.worker_id == "worker-001").first()
    worker.last_heartbeat = datetime.now(timezone.utc) - timedelta(seconds=100)
    db.commit()
    db.close()

    db = SessionLocal()
    check_worker_timeouts(db)
    db.close()

    response = client.get("/workers/worker-001")
    assert response.json()["status"] == "OFFLINE"


def test_offline_worker_job_is_requeued(client):
    job = client.post("/jobs", json={
        "job_name": "j", "task_type": "SLEEP_TEST", "priority": 5, "max_retries": 3,
    }).json()
    client.post("/workers/register", json={"worker_id": "worker-001"})
    client.get("/workers/worker-001/next-job")
    client.post(f"/jobs/{job['job_id']}/start")

    db = SessionLocal()
    worker = db.query(Worker).filter(Worker.worker_id == "worker-001").first()
    worker.last_heartbeat = datetime.now(timezone.utc) - timedelta(seconds=100)
    db.commit()
    check_worker_timeouts(db)
    db.close()

    response = client.get(f"/jobs/{job['job_id']}")
    body = response.json()
    assert body["status"] == "QUEUED"
    assert body["retry_count"] == 1
    assert body["assigned_worker"] is None


def test_offline_worker_job_hits_max_retries(client):
    job = client.post("/jobs", json={
        "job_name": "j", "task_type": "SLEEP_TEST", "priority": 5, "max_retries": 0,
    }).json()
    client.post("/workers/register", json={"worker_id": "worker-001"})
    client.get("/workers/worker-001/next-job")
    client.post(f"/jobs/{job['job_id']}/start")

    db = SessionLocal()
    worker = db.query(Worker).filter(Worker.worker_id == "worker-001").first()
    worker.last_heartbeat = datetime.now(timezone.utc) - timedelta(seconds=100)
    db.commit()
    check_worker_timeouts(db)
    db.close()

    response = client.get(f"/jobs/{job['job_id']}")
    assert response.json()["status"] == "MAX_RETRIES_REACHED"
