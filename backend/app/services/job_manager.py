"""Job CRUD, submission, and result-handling (retry/completion) logic."""
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.execution import JobExecution
from app.models.job import Job, JobStatus
from app.models.schemas import JobCreate, JobResultReport
from app.models.worker import Worker
from app.utils.logger import log_event


def create_job(db: Session, payload: JobCreate) -> Job:
    job = Job(
        job_id="PENDING",  # replaced below once we know the primary key
        job_name=payload.job_name,
        task_type=payload.task_type.value,
        priority=payload.priority,
        max_retries=payload.max_retries,
        status=JobStatus.QUEUED.value,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    job.job_id = f"JOB-{job.id:04d}"
    db.commit()
    db.refresh(job)

    log_event(db, "JOB_SUBMITTED", f"Job {job.job_id} ({job.job_name}) submitted", job_id=job.job_id)
    return job


def list_jobs(db: Session, status: str | None = None):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    return query.order_by(Job.created_at.desc()).all()


def get_job(db: Session, job_id: str) -> Job | None:
    return db.query(Job).filter(Job.job_id == job_id).first()


def get_job_executions(db: Session, job_id: str):
    return db.query(JobExecution).filter(JobExecution.job_id == job_id).order_by(JobExecution.started_at.asc()).all()


def cancel_job(db: Session, job: Job) -> bool:
    if job.status not in (JobStatus.QUEUED.value, JobStatus.RETRYING.value):
        return False
    job.status = JobStatus.CANCELLED.value
    db.commit()
    log_event(db, "JOB_CANCELLED", f"Job {job.job_id} cancelled by user", job_id=job.job_id)
    return True


def start_job(db: Session, job: Job) -> Job:
    job.status = JobStatus.RUNNING.value
    job.started_at = datetime.now(timezone.utc)
    db.commit()
    log_event(db, "JOB_STARTED", f"Job {job.job_id} started on {job.assigned_worker}",
              job_id=job.job_id, worker_id=job.assigned_worker)
    return job


def report_result(db: Session, job: Job, result: JobResultReport) -> Job:
    """Record the execution attempt and decide whether to complete, retry, or give up."""
    worker = db.query(Worker).filter(Worker.worker_id == job.assigned_worker).first()

    execution = JobExecution(
        execution_id=str(uuid.uuid4()),
        job_id=job.job_id,
        worker_id=job.assigned_worker,
        started_at=job.started_at,
        completed_at=datetime.now(timezone.utc),
        status=result.status,
        execution_time=result.execution_time,
        output=result.output,
        error=result.error,
        retry_number=job.retry_count,
    )
    db.add(execution)

    job.exit_code = result.exit_code
    job.execution_time = result.execution_time
    job.output = result.output
    job.error = result.error

    if result.status == JobStatus.COMPLETED.value:
        job.status = JobStatus.COMPLETED.value
        job.completed_at = datetime.now(timezone.utc)
        if worker:
            worker.jobs_completed += 1
            worker.current_job = None
        db.commit()
        log_event(db, "JOB_COMPLETED", f"Job {job.job_id} completed on {job.assigned_worker}",
                   job_id=job.job_id, worker_id=job.assigned_worker)
        return job

    # failure path
    if worker:
        worker.jobs_failed += 1
        worker.current_job = None

    if job.retry_count < job.max_retries:
        job.retry_count += 1
        job.status = JobStatus.QUEUED.value
        job.assigned_worker = None
        db.commit()
        log_event(db, "JOB_RETRY", f"Job {job.job_id} failed, retry {job.retry_count}/{job.max_retries} queued",
                   severity="WARNING", job_id=job.job_id)
    else:
        job.status = JobStatus.MAX_RETRIES_REACHED.value
        db.commit()
        log_event(db, "JOB_MAX_RETRIES", f"Job {job.job_id} reached max retries ({job.max_retries}), giving up",
                   severity="ERROR", job_id=job.job_id)

    return job
