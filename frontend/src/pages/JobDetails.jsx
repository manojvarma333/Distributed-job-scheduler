import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../services/api.js";
import StatusBadge from "../components/StatusBadge.jsx";

export default function JobDetails() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [executions, setExecutions] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => {
      Promise.all([api.getJob(jobId), api.getExecutions(jobId)])
        .then(([j, execs]) => {
          setJob(j);
          setExecutions(execs);
          setError(null);
        })
        .catch((e) => setError(e.message));
    };
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, [jobId]);

  if (error) return <div className="error-banner">{error}</div>;
  if (!job) return <div>Loading...</div>;

  return (
    <div>
      <h1>{job.job_id}</h1>
      <div className="detail-grid">
        <div>
          <strong>Job Name:</strong> {job.job_name}
        </div>
        <div>
          <strong>Status:</strong> <StatusBadge status={job.status} />
        </div>
        <div>
          <strong>Task Type:</strong> {job.task_type}
        </div>
        <div>
          <strong>Worker:</strong> {job.assigned_worker || "--"}
        </div>
        <div>
          <strong>Created:</strong> {job.created_at ? new Date(job.created_at).toLocaleString() : "--"}
        </div>
        <div>
          <strong>Started:</strong> {job.started_at ? new Date(job.started_at).toLocaleString() : "--"}
        </div>
        <div>
          <strong>Completed:</strong> {job.completed_at ? new Date(job.completed_at).toLocaleString() : "--"}
        </div>
        <div>
          <strong>Execution Duration:</strong> {job.execution_time != null ? `${job.execution_time}s` : "--"}
        </div>
        <div>
          <strong>Retries:</strong> {job.retry_count}/{job.max_retries}
        </div>
      </div>

      <h2>Output / Error</h2>
      <pre className="output-block">{job.output || "(no output yet)"}</pre>
      {job.error && <pre className="output-block error-text">{job.error}</pre>}

      <h2>Execution History</h2>
      <table className="data-table">
        <thead>
          <tr>
            <th>Attempt</th>
            <th>Status</th>
            <th>Worker</th>
            <th>Duration</th>
            <th>Error</th>
          </tr>
        </thead>
        <tbody>
          {executions.map((execution) => (
            <tr key={execution.execution_id}>
              <td>{execution.retry_number + 1}</td>
              <td>
                <StatusBadge status={execution.status} />
              </td>
              <td>{execution.worker_id || "--"}</td>
              <td>{execution.execution_time != null ? `${execution.execution_time}s` : "--"}</td>
              <td>{execution.error || "--"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
