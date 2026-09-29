const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status} ${response.statusText}: ${body}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  getMetrics: () => request("/metrics"),
  getJobs: () => request("/jobs"),
  getJob: (jobId) => request(`/jobs/${jobId}`),
  submitJob: (payload) => request("/jobs", { method: "POST", body: JSON.stringify(payload) }),
  cancelJob: (jobId) => request(`/jobs/${jobId}/cancel`, { method: "POST" }),
  getWorkers: () => request("/workers"),
  getExecutions: (jobId) => request(jobId ? `/executions?job_id=${jobId}` : "/executions"),
  getEvents: () => request("/events"),
};

export const TASK_TYPES = [
  "CPU_TEST",
  "MEMORY_TEST",
  "SLEEP_TEST",
  "FILE_PROCESSING",
  "NETWORK_CHECK",
  "RANDOM_FAILURE",
];
