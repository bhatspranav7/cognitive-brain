import { useEffect, useState } from "react";
import { api } from "./api";
import type { Health } from "./types";
import ChatView from "./components/ChatView";
import DashboardView from "./components/DashboardView";
import DocumentsView from "./components/DocumentsView";

type Tab = "chat" | "dashboard" | "documents";

const NAV: { id: Tab; label: string; icon: string }[] = [
  { id: "chat", label: "Chat", icon: "💬" },
  { id: "dashboard", label: "Dashboard", icon: "📊" },
  { id: "documents", label: "Documents", icon: "📄" },
];

export default function App() {
  const [tab, setTab] = useState<Tab>("chat");
  const [health, setHealth] = useState<Health | null>(null);
  const [healthError, setHealthError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      try {
        const h = await api.health();
        if (!cancelled) {
          setHealth(h);
          setHealthError(false);
        }
      } catch {
        if (!cancelled) setHealthError(true);
      }
    };

    check();
    const timer = setInterval(check, 15000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const online = !healthError && !!health;

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">🧠</span>
          <div>
            <div className="brand-name">CortexRAG</div>
            <div className="brand-sub">cognitive multi-agent RAG</div>
          </div>
        </div>

        <nav className="nav">
          {NAV.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${tab === item.id ? "active" : ""}`}
              onClick={() => setTab(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className={`status-pill ${online ? "ok" : "down"}`}>
            <span className="dot" />
            {online ? "API online" : "API offline"}
          </div>
          {health && (
            <div className="health-details">
              <div>
                LLM: {health.llm_provider}{" "}
                {health.llm_ok ? "✓" : "✗"}
              </div>
              <div>Embeddings: {health.embedding_provider}</div>
              <div>{health.documents_indexed} chunks indexed</div>
            </div>
          )}
          <div className="api-url" title={api.base}>
            {api.base.replace(/^https?:\/\//, "")}
          </div>
        </div>
      </aside>

      <main className="main">
        {tab === "chat" && <ChatView apiOnline={online} />}
        {tab === "dashboard" && <DashboardView />}
        {tab === "documents" && <DocumentsView />}
      </main>
    </div>
  );
}
