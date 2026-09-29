"""Worker registration, heartbeats, listing, and the job-polling endpoint."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schemas import JobResponse, WorkerHeartbeat, WorkerRegister, WorkerResponse
from app.services import scheduler, worker_manager

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("/register", response_model=WorkerResponse)
def register_worker(payload: WorkerRegister, db: Session = Depends(get_db)):
    return worker_manager.register_worker(db, payload)


@router.get("", response_model=list[WorkerResponse])
def list_workers(db: Session = Depends(get_db)):
    return worker_manager.list_workers(db)


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(worker_id: str, db: Session = Depends(get_db)):
    worker = worker_manager.get_worker(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


@router.post("/{worker_id}/heartbeat", response_model=WorkerResponse)
def heartbeat(worker_id: str, payload: WorkerHeartbeat, db: Session = Depends(get_db)):
    worker = worker_manager.get_worker(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not registered")
    return worker_manager.record_heartbeat(db, worker, payload)


@router.get("/{worker_id}/next-job", response_model=JobResponse | None)
def next_job(worker_id: str, db: Session = Depends(get_db)):
    """Pull-based assignment: an idle worker polls this to receive its next job, if any."""
    worker = worker_manager.get_worker(db, worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not registered")
    return scheduler.assign_next_job(db, worker)
