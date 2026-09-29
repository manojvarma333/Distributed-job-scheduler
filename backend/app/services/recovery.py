"""Automated recovery: detect offline workers and reassign their interrupted jobs."""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.execution import JobExecution
from app.models.job import Job, JobStatus
from app.models.worker import Worker, WorkerStatus
from app.utils.logger import log_event


def check_worker_timeouts(db: Session) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.heartbeat_timeout_seconds)

    stale_workers = (
        db.query(Worker)
        .filter(Worker.status == WorkerStatus.ONLINE.value, Worker.last_heartbeat < cutoff)
        .all()
    )

    for worker in stale_workers:
        worker.status = WorkerStatus.OFFLINE.value
        log_event(db, "WORKER_TIMEOUT", f"Worker {worker.worker_id} heartbeat timeout, marked OFFLINE",
                   severity="WARNING", worker_id=worker.worker_id)

        if worker.current_job:
            job = db.query(Job).filter(Job.job_id == worker.current_job).first()
            if job and job.status in (JobStatus.ASSIGNED.value, JobStatus.RUNNING.value):
                _interrupt_and_requeue(db, job, worker)
            worker.current_job = None

        db.commit()


def _interrupt_and_requeue(db: Session, job: Job, worker: Worker) -> None:
    execution = JobExecution(
        execution_id=str(uuid.uuid4()),
        job_id=job.job_id,
        worker_id=worker.worker_id,
        started_at=job.started_at,
        completed_at=datetime.now(timezone.utc),
        status="INTERRUPTED",
        retry_number=job.retry_count,
        error=f"Worker {worker.worker_id} stopped responding",
    )
    db.add(execution)

    log_event(db, "JOB_INTERRUPTED", f"Job {job.job_id} interrupted, worker {worker.worker_id} offline",
              severity="ERROR", job_id=job.job_id, worker_id=worker.worker_id)

    if job.retry_count < job.max_retries:
        job.retry_count += 1
        job.status = JobStatus.QUEUED.value
        job.assigned_worker = None
        log_event(db, "JOB_REQUEUED", f"Job {job.job_id} returned to queue for retry {job.retry_count}/{job.max_retries}",
                   severity="WARNING", job_id=job.job_id)
    else:
        job.status = JobStatus.MAX_RETRIES_REACHED.value
        log_event(db, "JOB_MAX_RETRIES", f"Job {job.job_id} reached max retries after worker failure",
                   severity="ERROR", job_id=job.job_id)
