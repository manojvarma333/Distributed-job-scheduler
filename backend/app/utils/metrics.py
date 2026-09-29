"""Aggregation helpers backing the /metrics endpoint."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.job import Job, JobStatus
from app.models.worker import Worker, WorkerStatus


def compute_system_metrics(db: Session) -> dict:
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    running_jobs = db.query(func.count(Job.id)).filter(Job.status == JobStatus.RUNNING.value).scalar() or 0
    completed_jobs = db.query(func.count(Job.id)).filter(Job.status == JobStatus.COMPLETED.value).scalar() or 0
    failed_jobs = db.query(func.count(Job.id)).filter(
        Job.status.in_([JobStatus.FAILED.value, JobStatus.MAX_RETRIES_REACHED.value])
    ).scalar() or 0
    queued_jobs = db.query(func.count(Job.id)).filter(
        Job.status.in_([JobStatus.QUEUED.value, JobStatus.RETRYING.value])
    ).scalar() or 0

    active_workers = db.query(func.count(Worker.id)).filter(Worker.status == WorkerStatus.ONLINE.value).scalar() or 0
    offline_workers = db.query(func.count(Worker.id)).filter(Worker.status == WorkerStatus.OFFLINE.value).scalar() or 0

    avg_execution_time = db.query(func.avg(Job.execution_time)).filter(
        Job.execution_time.isnot(None)
    ).scalar()
    total_retries = db.query(func.sum(Job.retry_count)).scalar() or 0

    return {
        "total_jobs": total_jobs,
        "queued_jobs": queued_jobs,
        "running_jobs": running_jobs,
        "completed_jobs": completed_jobs,
        "failed_jobs": failed_jobs,
        "active_workers": active_workers,
        "offline_workers": offline_workers,
        "average_execution_time": round(avg_execution_time, 2) if avg_execution_time else 0,
        "total_retries": int(total_retries),
    }
