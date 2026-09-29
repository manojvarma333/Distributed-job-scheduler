"""Scheduling strategy: assign a queued job to a worker that is polling for work.

Strategy implemented: First Available Worker - the first healthy, idle worker
to ask for work receives the oldest, highest-priority QUEUED job.
"""
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.models.worker import Worker, WorkerStatus
from app.utils.logger import log_event


def assign_next_job(db: Session, worker: Worker) -> Job | None:
    if worker.status != WorkerStatus.ONLINE.value or worker.current_job:
        return None

    query = (
        db.query(Job)
        .filter(Job.status == JobStatus.QUEUED.value)
        .order_by(Job.priority.desc(), Job.created_at.asc())
    )
    # Multiple workers poll concurrently; without a row lock two requests can both SELECT the
    # same QUEUED job before either commits, double-assigning it. FOR UPDATE SKIP LOCKED makes
    # the read-then-assign atomic across concurrent worker requests (Postgres only; SQLite,
    # used in tests, has no concurrent pollers so the plain query there is safe).
    if db.bind.dialect.name == "postgresql":
        query = query.with_for_update(skip_locked=True)
    job = query.first()
    if not job:
        return None

    job.status = JobStatus.ASSIGNED.value
    job.assigned_worker = worker.worker_id
    worker.current_job = job.job_id
    db.commit()
    log_event(db, "JOB_ASSIGNED", f"Job {job.job_id} assigned to {worker.worker_id}",
              job_id=job.job_id, worker_id=worker.worker_id)
    return job
