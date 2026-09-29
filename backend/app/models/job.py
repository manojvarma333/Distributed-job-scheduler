"""Job ORM model and the enums that define allowed task types / job states."""
import enum

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.database.connection import Base


class TaskType(str, enum.Enum):
    """Predefined safe tasks. Arbitrary shell commands are never accepted from the API."""
    CPU_TEST = "CPU_TEST"
    MEMORY_TEST = "MEMORY_TEST"
    SLEEP_TEST = "SLEEP_TEST"
    FILE_PROCESSING = "FILE_PROCESSING"
    NETWORK_CHECK = "NETWORK_CHECK"
    RANDOM_FAILURE = "RANDOM_FAILURE"


class JobStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    ASSIGNED = "ASSIGNED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    MAX_RETRIES_REACHED = "MAX_RETRIES_REACHED"
    CANCELLED = "CANCELLED"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(32), unique=True, index=True, nullable=False)
    job_name = Column(String(255), nullable=False)
    task_type = Column(String(32), nullable=False)
    priority = Column(Integer, default=5, nullable=False)
    status = Column(String(32), default=JobStatus.QUEUED.value, index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    assigned_worker = Column(String(64), nullable=True, index=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)

    exit_code = Column(Integer, nullable=True)
    output = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)
