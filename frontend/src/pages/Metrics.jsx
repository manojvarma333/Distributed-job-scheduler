import { useEffect, useState } from "react";
import { api } from "../services/api.js";
import StatCard from "../components/StatCard.jsx";

export default function Metrics() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => api.getMetrics().then(setMetrics).catch((e) => setError(e.message));
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!metrics) return <div>Loading...</div>;

  return (
    <div>
      <h1>Metrics</h1>
      <div className="stat-grid">
        <StatCard label="Total Jobs" value={metrics.total_jobs} />
        <StatCard label="Successful Jobs" value={metrics.completed_jobs} accent="green" />
        <StatCard label="Failed Jobs" value={metrics.failed_jobs} accent="red" />
        <StatCard label="Running Jobs" value={metrics.running_jobs} accent="blue" />
        <StatCard label="Average Execution Time" value={`${metrics.average_execution_time}s`} />
        <StatCard label="Active Workers" value={metrics.active_workers} accent="green" />
        <StatCard label="Offline Workers" value={metrics.offline_workers} accent="red" />
        <StatCard label="Total Retries" value={metrics.total_retries} />
      </div>
    </div>
  );
}
