"""Execution history and system event log ORM models."""
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.database.connection import Base


class JobExecution(Base):
    """One row per attempt of a job (so retries show full history)."""
    __tablename__ = "job_executions"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(String(64), unique=True, index=True, nullable=False)
    job_id = Column(String(32), index=True, nullable=False)
    worker_id = Column(String(64), index=True, nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(32), nullable=False)
    execution_time = Column(Float, nullable=True)
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    retry_number = Column(Integer, default=0, nullable=False)


class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(64), nullable=False)
    worker_id = Column(String(64), nullable=True)
    job_id = Column(String(32), nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String(16), default="INFO", nullable=False)
