import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../services/api.js";
import StatCard from "../components/StatCard.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [recentJobs, setRecentJobs] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => {
      Promise.all([api.getMetrics(), api.getJobs()])
        .then(([m, jobs]) => {
          setMetrics(m);
          setRecentJobs(jobs.slice(0, 8));
          setError(null);
        })
        .catch((e) => setError(e.message));
    };
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Overview</h1>
      {error && <div className="error-banner">Could not reach backend: {error}</div>}
      {metrics && (
        <div className="stat-grid">
          <StatCard label="Total Jobs" value={metrics.total_jobs} />
          <StatCard label="Queued Jobs" value={metrics.queued_jobs} accent="yellow" />
          <StatCard label="Running Jobs" value={metrics.running_jobs} accent="blue" />
          <StatCard label="Completed" value={metrics.completed_jobs} accent="green" />
          <StatCard label="Failed" value={metrics.failed_jobs} accent="red" />
          <StatCard label="Active Workers" value={metrics.active_workers} accent="green" />
          <StatCard label="Offline Workers" value={metrics.offline_workers} accent="red" />
          <StatCard label="Total Retries" value={metrics.total_retries} />
        </div>
      )}

      <h2>Recent Jobs</h2>
      <table className="data-table">
        <thead>
          <tr>
            <th>Job ID</th>
            <th>Name</th>
            <th>Status</th>
            <th>Worker</th>
            <th>Retries</th>
          </tr>
        </thead>
        <tbody>
          {recentJobs.map((job) => (
            <tr key={job.job_id}>
              <td>
                <Link to={`/jobs/${job.job_id}`}>{job.job_id}</Link>
              </td>
              <td>{job.job_name}</td>
              <td>
                <StatusBadge status={job.status} />
              </td>
              <td>{job.assigned_worker || "--"}</td>
              <td>{job.retry_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
