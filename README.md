# Distributed Job Scheduler & Execution Monitor

A lightweight distributed job scheduling and execution platform. Users submit jobs
through a REST API / React dashboard, a central FastAPI scheduler queues and assigns
them to worker processes, and workers execute predefined tasks while reporting status,
resource usage, and failures back to the scheduler. Failed jobs and failed workers are
automatically detected and recovered.

## Problem Statement

Running many computational jobs manually on a single machine doesn't scale. This project
simulates a small distributed computing environment (multiple worker processes/containers)
that queues jobs, assigns them to available workers, monitors execution and worker health,
and automatically retries failed work — without needing Kubernetes, Kafka, or cloud services.

## Solution

- **FastAPI backend** exposes REST endpoints for job submission, worker registration,
  execution history, metrics, and events, backed by **PostgreSQL**.
- **Workers** are independent Python processes (or Docker containers) that register with
  the backend, send heartbeats every 5 seconds, poll for work, execute predefined safe
  tasks, and report results.
- The scheduler uses a **First Available Worker** strategy: an idle worker polling for
  work receives the oldest, highest-priority queued job.
- A **recovery loop** runs in the backend every 5 seconds. If a worker's heartbeat is more
  than 15 seconds old, it's marked `OFFLINE`, its in-flight job is marked interrupted, and
  the job is requeued (and retried) on another worker.
- A **React + Vite dashboard** visualizes jobs, workers, executions, events, and metrics.

## Architecture

```
                    USER
                     |
                     v
              WEB DASHBOARD (React)
                     |
                     v
              FASTAPI SERVER
                     |
          +----------+----------+
          |                     |
          v                     v
    JOB SCHEDULER          POSTGRESQL
          ^
          | poll / register / heartbeat / result
    +-----+-----+-----+
    |           |     |
    v           v     v
 WORKER-1    WORKER-2 WORKER-3
    |           |     |
    +-----------+-----+
                |
                v
         JOB EXECUTION (predefined tasks)
```

Workers use a **pull model**: they poll `GET /workers/{id}/next-job` for assignments,
call `POST /jobs/{id}/start` when they begin, and `POST /jobs/{id}/result` when done.
This keeps the networking simple (workers only need outbound HTTP to the backend) while
still letting the backend's scheduler make all assignment decisions.

## Features

- Job submission restricted to predefined safe task types (no arbitrary shell commands)
- Job states: `QUEUED → ASSIGNED → RUNNING → COMPLETED`, with `FAILED → RETRYING → QUEUED`
  and `MAX_RETRIES_REACHED` failure paths
- Worker registration, heartbeats (CPU/RAM/current job), and offline detection
- Automatic job reassignment when a worker goes offline
- Full execution history per job (every retry attempt recorded)
- Structured logging + persisted system event log
- Dashboard: Overview, Jobs, Workers, Executions, Events, Metrics pages
- Docker Compose stack: Postgres + backend + 3 workers + frontend

## Technology Stack

**Backend:** Python 3.11+, FastAPI, Uvicorn, Pydantic, SQLAlchemy, psycopg2
**Frontend:** React, Vite, JavaScript, CSS
**Database:** PostgreSQL
**Infra:** Docker, Docker Compose, Linux/WSL2
**Monitoring:** psutil, Python logging, heartbeat mechanism
**Testing:** pytest

## Project Structure

```
distributed-job-scheduler/
├── backend/app/            FastAPI app: api/, models/, services/, database/, utils/
├── worker/                 worker.py, heartbeat.py, executor.py, tasks/
├── frontend/                React + Vite dashboard
├── tests/                   pytest suite (jobs, scheduler, workers, recovery)
├── docker/                   Dockerfile.backend / .worker / .frontend
├── docker-compose.yml
├── start.sh / stop.sh / health_check.sh
└── .env.example
```

## Installation (local, without Docker)

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp ../.env.example .env     # edit DATABASE_URL to point at your Postgres instance
uvicorn app.main:app --reload

# Worker (in another terminal, from worker/)
cd worker
pip install -r requirements.txt
WORKER_ID=worker-001 BACKEND_URL=http://localhost:8000 python worker.py

# Frontend (in another terminal, from frontend/)
cd frontend
npm install
npm run dev
```

## Docker Setup & Running

```bash
cp .env.example .env
./start.sh              # docker compose up --build -d
./health_check.sh        # verify backend, postgres, workers, network
./stop.sh                # docker compose down
```

Once running:
- Backend Swagger docs: http://localhost:8000/docs
- Frontend dashboard: http://localhost:4173

## API Documentation

Interactive OpenAPI/Swagger docs are auto-generated by FastAPI at `/docs`. Key endpoints:

```
POST   /jobs                        submit a job (predefined task types only)
GET    /jobs                        list jobs
GET    /jobs/{job_id}                job detail
POST   /jobs/{job_id}/cancel         cancel a queued job
POST   /jobs/{job_id}/start          [worker] mark job RUNNING
POST   /jobs/{job_id}/result         [worker] report COMPLETED/FAILED result

POST   /workers/register             [worker] register with the scheduler
POST   /workers/{worker_id}/heartbeat [worker] report CPU/RAM/current job
GET    /workers                      list workers
GET    /workers/{worker_id}          worker detail
GET    /workers/{worker_id}/next-job [worker] poll for next assigned job

GET    /executions                   execution history (optionally filter by job_id)
GET    /events                       system event log
GET    /metrics                      aggregated system metrics
GET    /health                       liveness check
GET    /network-test                 connectivity test endpoint
```

## Failure Recovery Demonstration

1. Submit a `Random Failure` job — watch it go `FAILED → RETRYING → QUEUED → RUNNING → COMPLETED`.
2. Stop a worker container: `docker stop worker-1`.
3. Within 15s the backend marks it `OFFLINE`, interrupts its running job, and requeues it.
4. Another worker picks up the job automatically.
5. Restart the worker: `docker start worker-1` — it re-registers and becomes available again.

All of this is visible live in the **Events** page and the **Job Details** execution history.

## Testing

```bash
pip install -r tests/requirements.txt
pytest -v
```

Tests use an isolated SQLite database (no Postgres required) and cover job lifecycle,
scheduler assignment logic, worker registration/heartbeats, and recovery/retry behavior.

## Future Improvements

- Least-loaded worker scheduling strategy
- Redis-backed job queue
- Authentication and role-based access control
- Prometheus + Grafana monitoring
- Kubernetes deployment and worker autoscaling
- Job dependencies and resource-aware scheduling
