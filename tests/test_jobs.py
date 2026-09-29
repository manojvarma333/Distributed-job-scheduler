"""Job lifecycle tests: creation, start, completion, failure, and retry counting."""


def _submit_job(client, task_type="CPU_TEST", max_retries=3):
    response = client.post("/jobs", json={
        "job_name": "Test Job",
        "task_type": task_type,
        "priority": 5,
        "max_retries": max_retries,
    })
    assert response.status_code == 200
    return response.json()


def test_job_creation_defaults_to_queued(client):
    job = _submit_job(client)
    assert job["status"] == "QUEUED"
    assert job["retry_count"] == 0
    assert job["job_id"].startswith("JOB-")


def test_get_job_returns_404_for_unknown_job(client):
    response = client.get("/jobs/JOB-9999")
    assert response.status_code == 404


def test_job_start_sets_running(client):
    job = _submit_job(client)
    client.post("/workers/register", json={"worker_id": "worker-001", "hostname": "h", "ip_address": "1.2.3.4"})
    client.get("/workers/worker-001/next-job")  # assigns the job

    response = client.post(f"/jobs/{job['job_id']}/start")
    assert response.status_code == 200
    assert response.json()["status"] == "RUNNING"


def test_job_completion(client):
    job = _submit_job(client)
    client.post("/workers/register", json={"worker_id": "worker-001"})
    client.get("/workers/worker-001/next-job")
    client.post(f"/jobs/{job['job_id']}/start")

    response = client.post(f"/jobs/{job['job_id']}/result", json={
        "status": "COMPLETED", "exit_code": 0, "output": "done", "execution_time": 1.5,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "COMPLETED"
    assert body["execution_time"] == 1.5


def test_job_failure_increments_retry_and_requeues(client):
    job = _submit_job(client, max_retries=3)
    client.post("/workers/register", json={"worker_id": "worker-001"})
    client.get("/workers/worker-001/next-job")
    client.post(f"/jobs/{job['job_id']}/start")

    response = client.post(f"/jobs/{job['job_id']}/result", json={
        "status": "FAILED", "exit_code": 1, "error": "boom",
    })
    body = response.json()
    assert body["status"] == "QUEUED"
    assert body["retry_count"] == 1


def test_job_reaches_max_retries(client):
    job = _submit_job(client, max_retries=1)
    for _ in range(2):  # first failure retries once, second failure exhausts retries
        client.post("/workers/register", json={"worker_id": "worker-001"})
        client.get("/workers/worker-001/next-job")
        client.post(f"/jobs/{job['job_id']}/start")
        response = client.post(f"/jobs/{job['job_id']}/result", json={
            "status": "FAILED", "exit_code": 1, "error": "boom",
        })

    assert response.json()["status"] == "MAX_RETRIES_REACHED"
