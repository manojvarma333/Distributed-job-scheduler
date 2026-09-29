"""Worker + general API tests: registration, heartbeat, listing, and metrics."""


def test_register_worker(client):
    response = client.post("/workers/register", json={
        "worker_id": "worker-001", "hostname": "host1", "ip_address": "10.0.0.2",
    })
    assert response.status_code == 200
    body = response.json()
    assert body["worker_id"] == "worker-001"
    assert body["status"] == "ONLINE"


def test_heartbeat_updates_usage(client):
    client.post("/workers/register", json={"worker_id": "worker-001"})
    response = client.post("/workers/worker-001/heartbeat", json={
        "cpu_usage": 42.5, "memory_usage": 60.1, "current_job": None,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["cpu_usage"] == 42.5
    assert body["memory_usage"] == 60.1


def test_heartbeat_for_unknown_worker_returns_404(client):
    response = client.post("/workers/ghost/heartbeat", json={"cpu_usage": 1.0, "memory_usage": 1.0})
    assert response.status_code == 404


def test_list_workers(client):
    client.post("/workers/register", json={"worker_id": "worker-001"})
    client.post("/workers/register", json={"worker_id": "worker-002"})
    response = client.get("/workers")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_metrics(client):
    client.post("/jobs", json={"job_name": "j", "task_type": "SLEEP_TEST", "priority": 5, "max_retries": 3})
    response = client.get("/metrics")
    assert response.status_code == 200
    body = response.json()
    assert body["total_jobs"] == 1
    assert "active_workers" in body


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
