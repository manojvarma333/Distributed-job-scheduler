"""Worker ORM model."""
import enum

from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func

from app.database.connection import Base


class WorkerStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(String(64), unique=True, index=True, nullable=False)
    hostname = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)
    status = Column(String(16), default=WorkerStatus.ONLINE.value, nullable=False)

    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    # job_id of the job currently executing on this worker, if any
    current_job = Column(String(32), nullable=True)

    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())
    jobs_completed = Column(Integer, default=0, nullable=False)
    jobs_failed = Column(Integer, default=0, nullable=False)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
