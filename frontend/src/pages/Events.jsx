import { useEffect, useState } from "react";
import { api } from "../services/api.js";

const SEVERITY_CLASS = { INFO: "sev-info", WARNING: "sev-warning", ERROR: "sev-error" };

export default function Events() {
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = () => api.getEvents().then(setEvents).catch((e) => setError(e.message));
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h1>Event Log</h1>
      {error && <div className="error-banner">{error}</div>}
      <div className="event-log">
        {events.map((event, idx) => (
          <div className={`event-row ${SEVERITY_CLASS[event.severity] || ""}`} key={idx}>
            <span className="event-time">
              {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ""}
            </span>
            <span className="event-message">{event.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
