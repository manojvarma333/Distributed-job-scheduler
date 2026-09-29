"""Execution history endpoints (per-job attempt log used by the Executions page)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.execution import JobExecution
from app.models.schemas import ExecutionResponse
from app.services.job_manager import get_job_executions

router = APIRouter(prefix="/executions", tags=["executions"])


@router.get("", response_model=list[ExecutionResponse])
def list_executions(job_id: str | None = None, db: Session = Depends(get_db)):
    if job_id:
        return get_job_executions(db, job_id)
    return db.query(JobExecution).order_by(JobExecution.started_at.desc()).limit(200).all()
