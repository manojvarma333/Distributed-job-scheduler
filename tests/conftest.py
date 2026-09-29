"""Shared pytest fixtures: points the app at a throwaway SQLite DB instead of Postgres."""
import os
import sys

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, BACKEND_DIR)

os.environ["DATABASE_URL"] = "sqlite:///./test_scheduler.db"
os.environ["RECOVERY_CHECK_INTERVAL_SECONDS"] = "1"
os.environ["HEARTBEAT_TIMEOUT_SECONDS"] = "2"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database.connection import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
