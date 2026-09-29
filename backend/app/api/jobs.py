"""Job submission, status, cancellation, and worker-facing start/result callbacks."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schemas import JobCreate, JobResponse, JobResultReport
from app.services import job_manager

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
def submit_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = job_manager.create_job(db, payload)
    return job


@router.get("", response_model=list[JobResponse])
def list_jobs(status: str | None = None, db: Session = Depends(get_db)):
    return job_manager.list_jobs(db, status)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = job_manager.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    job = job_manager.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if not job_manager.cancel_job(db, job):
        raise HTTPException(status_code=400, detail="Job cannot be cancelled in its current state")
    return job


@router.post("/{job_id}/start", response_model=JobResponse)
def start_job(job_id: str, db: Session = Depends(get_db)):
    """Called by a worker right before it begins executing an assigned job."""
    job = job_manager.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_manager.start_job(db, job)


@router.post("/{job_id}/result", response_model=JobResponse)
def report_result(job_id: str, result: JobResultReport, db: Session = Depends(get_db)):
    """Called by a worker once execution finishes (success or failure)."""
    job = job_manager.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_manager.report_result(db, job, result)
