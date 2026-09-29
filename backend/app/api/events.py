"""System event log endpoint (worker registrations, job lifecycle, failures, recovery)."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.execution import SystemEvent
from app.models.schemas import EventResponse

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def list_events(limit: int = 200, db: Session = Depends(get_db)):
    return db.query(SystemEvent).order_by(SystemEvent.timestamp.desc()).limit(limit).all()
