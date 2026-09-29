"""FastAPI application entrypoint: wires up routers, DB init, and the recovery background thread."""
import socket
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import events, executions, jobs, metrics, workers
from app.config import settings
from app.database.connection import SessionLocal, init_db
from app.services.recovery import check_worker_timeouts


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    thread = threading.Thread(target=_recovery_loop, daemon=True)
    thread.start()
    yield


app = FastAPI(
    title="Distributed Job Scheduler & Execution Monitor",
    description="Central scheduler API for submitting jobs, tracking workers, and monitoring execution.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(workers.router)
app.include_router(metrics.router)
app.include_router(executions.router)
app.include_router(events.router)


def _recovery_loop():
    """Runs forever in a background thread, periodically requeuing jobs from dead workers."""
    while True:
        try:
            db = SessionLocal()
            try:
                check_worker_timeouts(db)
            finally:
                db.close()
        except Exception as exc:  # keep the loop alive even if a single pass errors out
            print(f"[recovery] error: {exc}")
        time.sleep(settings.recovery_check_interval_seconds)


@app.get("/health")
def health():
    return {"status": "ok", "hostname": socket.gethostname()}


@app.get("/network-test")
def network_test():
    """Lets workers/frontend verify they can reach the backend over the Docker network."""
    return {
        "status": "reachable",
        "hostname": socket.gethostname(),
        "ip_address": socket.gethostbyname(socket.gethostname()),
    }
