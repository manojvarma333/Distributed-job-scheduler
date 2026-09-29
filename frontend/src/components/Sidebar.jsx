import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/jobs", label: "Jobs" },
  { to: "/submit", label: "Submit Job" },
  { to: "/workers", label: "Workers" },
  { to: "/executions", label: "Executions" },
  { to: "/events", label: "Events" },
  { to: "/metrics", label: "Metrics" },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-title">
        <span className="sidebar-dot" />
        Job Scheduler
      </div>
      <nav>
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.end}
            className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
