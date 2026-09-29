const COLORS = {
  COMPLETED: "green",
  RUNNING: "blue",
  ASSIGNED: "blue",
  FAILED: "red",
  MAX_RETRIES_REACHED: "red",
  QUEUED: "yellow",
  RETRYING: "yellow",
  CANCELLED: "gray",
  OFFLINE: "red",
  ONLINE: "green",
};

export default function StatusBadge({ status }) {
  const color = COLORS[status] || "gray";
  return <span className={`badge badge-${color}`}>{status}</span>;
}
