import { useEffect, useState } from "react";
import { api } from "../services/api.js";
import StatusBadge from "../components/StatusBadge.jsx";

function timeAgo(timestamp) {
  if (!timestamp) return "never";
  const seconds = Math.floor((Date.now() - new Date(timestamp).getTime()) / 1000);
  if (seconds < 60) return `${seconds}s ago`;
  return `${Math.floor(seconds / 60)}m ago`;
}

export default function Workers() {
  const [workers, setWorkers] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => api.getWorkers().then(setWorkers).catch((e) => setError(e.message));
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Workers</h1>
      {error && <div className="error-banner">{error}</div>}
      <div className="worker-grid">
        {workers.map((worker) => (
          <div className="worker-card" key={worker.worker_id}>
            <div className="worker-card-header">
              <strong>{worker.worker_id}</strong>
              <StatusBadge status={worker.status} />
            </div>
            <div className="worker-metric">
              <span>CPU</span>
              <div className="meter">
                <div className="meter-fill" style={{ width: `${worker.cpu_usage}%` }} />
              </div>
              <span>{worker.cpu_usage.toFixed(0)}%</span>
            </div>
            <div className="worker-metric">
              <span>Memory</span>
              <div className="meter">
                <div className="meter-fill" style={{ width: `${worker.memory_usage}%` }} />
              </div>
              <span>{worker.memory_usage.toFixed(0)}%</span>
            </div>
            <div>Current Job: {worker.current_job || "idle"}</div>
            <div>
              Completed: {worker.jobs_completed} &nbsp; Failed: {worker.jobs_failed}
            </div>
            <div className="muted">Last Heartbeat: {timeAgo(worker.last_heartbeat)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
