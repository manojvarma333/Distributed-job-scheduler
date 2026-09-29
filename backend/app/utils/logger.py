"""Structured logging: console logs plus persistence of important events to system_events."""
import logging
import sys

from sqlalchemy.orm import Session

from app.config import settings
from app.models.execution import SystemEvent

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("scheduler")


def log_event(db: Session, event_type: str, message: str, severity: str = "INFO",
               worker_id: str | None = None, job_id: str | None = None) -> None:
    """Log to console/stdout and persist the event row so the dashboard event log can show it."""
    getattr(logger, severity.lower(), logger.info)(message)
    event = SystemEvent(
        event_type=event_type,
        worker_id=worker_id,
        job_id=job_id,
        message=message,
        severity=severity,
    )
    db.add(event)
    db.commit()
