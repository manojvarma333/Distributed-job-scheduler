import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, TASK_TYPES } from "../services/api.js";

export default function SubmitJob() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    job_name: "",
    task_type: TASK_TYPES[0],
    priority: 5,
    max_retries: 3,
  });
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const update = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const job = await api.submitJob({
        job_name: form.job_name,
        task_type: form.task_type,
        priority: Number(form.priority),
        max_retries: Number(form.max_retries),
      });
      navigate(`/jobs/${job.job_id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Submit Job</h1>
      <p className="muted">
        Jobs run predefined, safe tasks only. Arbitrary shell commands are not accepted.
      </p>
      {error && <div className="error-banner">{error}</div>}
      <form className="form-card" onSubmit={handleSubmit}>
        <label>
          Job Name
          <input required value={form.job_name} onChange={update("job_name")} placeholder="e.g. CPU Test Run" />
        </label>

        <label>
          Task Type
          <select value={form.task_type} onChange={update("task_type")}>
            {TASK_TYPES.map((type) => (
              <option key={type} value={type}>
                {type.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </label>

        <label>
          Priority (1-10)
          <input type="number" min="1" max="10" value={form.priority} onChange={update("priority")} />
        </label>

        <label>
          Maximum Retries
          <input type="number" min="0" max="10" value={form.max_retries} onChange={update("max_retries")} />
        </label>

        <button type="submit" disabled={submitting}>
          {submitting ? "Submitting..." : "Submit Job"}
        </button>
      </form>
    </div>
  );
}
