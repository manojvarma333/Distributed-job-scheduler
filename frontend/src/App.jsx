import { Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Jobs from "./pages/Jobs.jsx";
import JobDetails from "./pages/JobDetails.jsx";
import SubmitJob from "./pages/SubmitJob.jsx";
import Workers from "./pages/Workers.jsx";
import Executions from "./pages/Executions.jsx";
import Events from "./pages/Events.jsx";
import Metrics from "./pages/Metrics.jsx";

export default function App() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/:jobId" element={<JobDetails />} />
          <Route path="/submit" element={<SubmitJob />} />
          <Route path="/workers" element={<Workers />} />
          <Route path="/executions" element={<Executions />} />
          <Route path="/events" element={<Events />} />
          <Route path="/metrics" element={<Metrics />} />
        </Routes>
      </main>
    </div>
  );
}
