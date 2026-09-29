"""System-wide metrics endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.utils.metrics import compute_system_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return compute_system_metrics(db)
