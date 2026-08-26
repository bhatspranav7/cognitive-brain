import type {
  AgentMetric,
  ConfidenceMetrics,
  DocumentsResponse,
  FeedbackMetrics,
  Health,
  QueryResponse,
} from "./types";

const BASE =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/+$/, "") ||
  "http://127.0.0.1:8000";

const API_KEY = (import.meta.env.VITE_API_KEY as string | undefined) || "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    ...((init?.headers as Record<string, string>) || {}),
  };
  if (API_KEY) headers["X-API-Key"] = API_KEY;

  const res = await fetch(`${BASE}${path}`, { ...init, headers });

  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = await res.json();
      if (body?.detail) {
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch {
      /* keep status text */
    }
    throw new Error(detail);
  }

  return res.json() as Promise<T>;
}

function postJson<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export const api = {
  base: BASE,

  health: () => request<Health>("/health"),

  query: (query: string) => postJson<QueryResponse>("/query", { query }),

  feedback: (query: string, answer: string, rating: number) =>
    postJson<{ ok: boolean; average_rating: number }>("/feedback", {
      query,
      answer,
      rating,
    }),

  documents: () => request<DocumentsResponse>("/documents"),

  upload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<{ source: string; chunks_added: number }>(
      "/documents/upload",
      { method: "POST", body: form },
    );
  },

  deleteDocument: (source: string) =>
    request<{ source: string; chunks_removed: number }>(
      `/documents/${encodeURIComponent(source)}`,
      { method: "DELETE" },
    ),

  metricsAgents: () => request<Record<string, AgentMetric>>("/metrics/agents"),
  metricsFeedback: () => request<FeedbackMetrics>("/metrics/feedback"),
  metricsConfidence: () => request<ConfidenceMetrics>("/metrics/confidence"),
  metricsHistory: () => request<string[]>("/metrics/history"),
  metricsSources: () => request<Record<string, number>>("/metrics/sources"),
};
