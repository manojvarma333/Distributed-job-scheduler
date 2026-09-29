"""Worker registration, heartbeat handling, and lookups."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.schemas import WorkerHeartbeat, WorkerRegister
from app.models.worker import Worker, WorkerStatus
from app.utils.logger import log_event


def register_worker(db: Session, payload: WorkerRegister) -> Worker:
    worker = db.query(Worker).filter(Worker.worker_id == payload.worker_id).first()
    if worker:
        worker.hostname = payload.hostname
        worker.ip_address = payload.ip_address
        worker.status = WorkerStatus.ONLINE.value
        worker.last_heartbeat = datetime.now(timezone.utc)
        db.commit()
        log_event(db, "WORKER_REREGISTERED", f"Worker {worker.worker_id} re-registered", worker_id=worker.worker_id)
        return worker

    worker = Worker(
        worker_id=payload.worker_id,
        hostname=payload.hostname,
        ip_address=payload.ip_address,
        status=WorkerStatus.ONLINE.value,
        last_heartbeat=datetime.now(timezone.utc),
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    log_event(db, "WORKER_REGISTERED", f"Worker {worker.worker_id} registered", worker_id=worker.worker_id)
    return worker


def record_heartbeat(db: Session, worker: Worker, payload: WorkerHeartbeat) -> Worker:
    was_offline = worker.status == WorkerStatus.OFFLINE.value
    worker.cpu_usage = payload.cpu_usage
    worker.memory_usage = payload.memory_usage
    # current_job is NOT applied from the heartbeat: the scheduler/report_result flow is the
    # single source of truth for assignment. Applying a heartbeat's snapshot here can race with
    # a job completing in between the worker sampling it and the request arriving, re-marking a
    # worker as busy after it already went idle.
    worker.status = WorkerStatus.ONLINE.value
    worker.last_heartbeat = datetime.now(timezone.utc)
    db.commit()
    if was_offline:
        log_event(db, "WORKER_ONLINE", f"Worker {worker.worker_id} is back ONLINE", worker_id=worker.worker_id)
    return worker


def list_workers(db: Session):
    return db.query(Worker).order_by(Worker.worker_id.asc()).all()


def get_worker(db: Session, worker_id: str) -> Worker | None:
    return db.query(Worker).filter(Worker.worker_id == worker_id).first()
