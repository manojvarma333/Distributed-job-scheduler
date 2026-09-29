import { useEffect, useState } from "react";
import { api } from "../services/api.js";
import StatusBadge from "../components/StatusBadge.jsx";

export default function Executions() {
  const [executions, setExecutions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => api.getExecutions().then(setExecutions).catch((e) => setError(e.message));
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Executions</h1>
      {error && <div className="error-banner">{error}</div>}
      <table className="data-table">
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Worker</th>
            <th>Status</th>
            <th>Attempt</th>
            <th>Started</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          {executions.map((execution) => (
            <tr key={execution.execution_id}>
              <td>{execution.job_id}</td>
              <td>{execution.worker_id || "--"}</td>
              <td>
                <StatusBadge status={execution.status} />
              </td>
              <td>{execution.retry_number + 1}</td>
              <td>{execution.started_at ? new Date(execution.started_at).toLocaleTimeString() : "--"}</td>
              <td>{execution.execution_time != null ? `${execution.execution_time}s` : "--"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
