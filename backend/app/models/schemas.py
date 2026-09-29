"""Pydantic request/response schemas shared by the API routers."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.job import TaskType


class JobCreate(BaseModel):
    job_name: str = Field(..., min_length=1, max_length=255)
    task_type: TaskType
    priority: int = Field(default=5, ge=1, le=10)
    max_retries: int = Field(default=3, ge=0, le=10)


class JobResultReport(BaseModel):
    status: str  # "COMPLETED" or "FAILED"
    exit_code: int = 0
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None


class JobResponse(BaseModel):
    job_id: str
    job_name: str
    task_type: str
    priority: int
    status: str
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_worker: Optional[str] = None
    retry_count: int
    max_retries: int
    exit_code: Optional[int] = None
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

    model_config = {"from_attributes": True}


class WorkerRegister(BaseModel):
    worker_id: str = Field(..., min_length=1, max_length=64)
    hostname: Optional[str] = None
    ip_address: Optional[str] = None


class WorkerHeartbeat(BaseModel):
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    current_job: Optional[str] = None


class WorkerResponse(BaseModel):
    worker_id: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    status: str
    cpu_usage: float
    memory_usage: float
    current_job: Optional[str] = None
    last_heartbeat: Optional[datetime] = None
    jobs_completed: int
    jobs_failed: int
    registered_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ExecutionResponse(BaseModel):
    execution_id: str
    job_id: str
    worker_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str
    execution_time: Optional[float] = None
    output: Optional[str] = None
    error: Optional[str] = None
    retry_number: int

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    event_type: str
    worker_id: Optional[str] = None
    job_id: Optional[str] = None
    message: str
    timestamp: Optional[datetime] = None
    severity: str

    model_config = {"from_attributes": True}
