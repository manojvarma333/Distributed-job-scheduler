import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";
import StatusBadge from "../components/StatusBadge.jsx";

function duration(job) {
  if (job.execution_time != null) return `${job.execution_time}s`;
  if (job.started_at && !job.completed_at) return "running...";
  return "--";
}

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => api.getJobs().then(setJobs).catch((e) => setError(e.message));
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Jobs</h1>
      {error && <div className="error-banner">{error}</div>}
      <table className="data-table">
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Job Name</th>
            <th>Status</th>
            <th>Worker</th>
            <th>Created</th>
            <th>Duration</th>
            <th>Retries</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.job_id}>
              <td>
                <Link to={`/jobs/${job.job_id}`}>{job.job_id}</Link>
              </td>
              <td>{job.job_name}</td>
              <td>
                <StatusBadge status={job.status} />
              </td>
              <td>{job.assigned_worker || "--"}</td>
              <td>{job.created_at ? new Date(job.created_at).toLocaleTimeString() : "--"}</td>
              <td>{duration(job)}</td>
              <td>
                {job.retry_count}/{job.max_retries}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
