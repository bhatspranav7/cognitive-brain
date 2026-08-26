import { useEffect, useState } from "react";
import { api } from "../api";
import type {
  AgentMetric,
  ConfidenceMetrics,
  FeedbackMetrics,
} from "../types";

export default function DashboardView() {
  const [agents, setAgents] = useState<Record<string, AgentMetric>>({});
  const [feedback, setFeedback] = useState<FeedbackMetrics | null>(null);
  const [confidence, setConfidence] = useState<ConfidenceMetrics | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [sources, setSources] = useState<Record<string, number>>({});
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      try {
        const [a, f, c, h, s] = await Promise.all([
          api.metricsAgents(),
          api.metricsFeedback(),
          api.metricsConfidence(),
          api.metricsHistory(),
          api.metricsSources(),
        ]);
        if (cancelled) return;
        setAgents(a);
        setFeedback(f);
        setConfidence(c);
        setHistory(h);
        setSources(s);
        setError("");
      } catch (err) {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load");
      }
    };

    load();
    const timer = setInterval(load, 10000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const totalQueries = agents.retriever?.count ?? 0;
  const maxSource = Math.max(1, ...Object.values(sources));
  const topSource =
    Object.entries(sources).sort((a, b) => b[1] - a[1])[0]?.[0] || "—";

  return (
    <div className="dashboard">
      <h1>Observability Dashboard</h1>
      {error && <div className="banner error">{error}</div>}

      <div className="stat-grid">
        <div className="stat-card">
          <div className="stat-value">{totalQueries}</div>
          <div className="stat-label">Queries traced</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {confidence ? (confidence.average_confidence * 100).toFixed(0) : 0}%
          </div>
          <div className="stat-label">Avg confidence</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {feedback?.average_rating ?? 0}
            <span className="stat-unit">/5</span>
          </div>
          <div className="stat-label">
            Avg rating · {feedback?.total_feedback ?? 0} votes
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-value stat-small">{topSource}</div>
          <div className="stat-label">Top source</div>
        </div>
      </div>

      <div className="panel-grid">
        <div className="panel">
          <h2>Agent performance</h2>
          {Object.keys(agents).length === 0 ? (
            <p className="muted">No traces yet — ask something in Chat.</p>
          ) : (
            <table className="agent-table">
              <thead>
                <tr>
                  <th>Agent</th>
                  <th>Runs</th>
                  <th>Avg</th>
                  <th>Min</th>
                  <th>Max</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(agents).map(([name, m]) => (
                  <tr key={name}>
                    <td className="agent-name">{name}</td>
                    <td>{m.count}</td>
                    <td>{m.avg_latency.toFixed(2)}s</td>
                    <td>{m.min_latency.toFixed(2)}s</td>
                    <td>{m.max_latency.toFixed(2)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="panel">
          <h2>Source usage</h2>
          {Object.keys(sources).length === 0 ? (
            <p className="muted">No retrievals recorded yet.</p>
          ) : (
            <div className="bars">
              {Object.entries(sources)
                .sort((a, b) => b[1] - a[1])
                .map(([name, n]) => (
                  <div key={name} className="bar-row">
                    <div className="bar-label" title={name}>
                      {name}
                    </div>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{ width: `${(n / maxSource) * 100}%` }}
                      />
                    </div>
                    <div className="bar-value">{n}</div>
                  </div>
                ))}
            </div>
          )}
        </div>

        <div className="panel wide">
          <h2>Recent queries</h2>
          {history.length === 0 ? (
            <p className="muted">Nothing asked yet.</p>
          ) : (
            <ul className="history">
              {[...history].reverse().map((q, i) => (
                <li key={i}>{q}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
