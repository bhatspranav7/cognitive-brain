import { FormEvent, useEffect, useRef, useState } from "react";
import { api } from "../api";
import type { ChatMessage } from "../types";
import StarRating from "./StarRating";

const THINKING_STAGES = [
  "Retriever agent — searching the vector store…",
  "Reasoner agent — writing a grounded answer…",
  "Validator agent — checking the answer against sources…",
];

const SUGGESTIONS = [
  "What skills does Pranav have?",
  "What projects has Pranav worked on?",
  "What is the pandemic simulation paper about?",
];

let nextId = 1;

export default function ChatView({ apiOnline }: { apiOnline: boolean }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!loading) return;
    setStage(0);
    const timer = setInterval(
      () => setStage((s) => Math.min(s + 1, THINKING_STAGES.length - 1)),
      3500,
    );
    return () => clearInterval(timer);
  }, [loading]);

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || loading) return;

    setInput("");
    setMessages((m) => [...m, { id: nextId++, role: "user", text: q }]);
    setLoading(true);

    try {
      const result = await api.query(q);
      setMessages((m) => [
        ...m,
        { id: nextId++, role: "assistant", text: result.answer, meta: result },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          id: nextId++,
          role: "error",
          text: err instanceof Error ? err.message : "Request failed",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const rate = async (msg: ChatMessage, rating: number) => {
    const question =
      [...messages].reverse().find((m) => m.role === "user" && m.id < msg.id)
        ?.text || "";
    setMessages((m) =>
      m.map((x) => (x.id === msg.id ? { ...x, rated: rating } : x)),
    );
    try {
      await api.feedback(question, msg.text, rating);
    } catch {
      /* rating is best-effort */
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    ask(input);
  };

  return (
    <div className="chat">
      <div className="chat-scroll">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🧠</div>
            <h2>Ask your documents anything</h2>
            <p>
              Questions run through a retriever → reasoner → validator agent
              pipeline, grounded in the PDFs you upload.
            </p>
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="suggestion" onClick={() => ask(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`bubble-row ${msg.role}`}>
            <div className={`bubble ${msg.role}`}>
              {msg.role === "error" && (
                <div className="bubble-error-label">Request failed</div>
              )}
              <div className="bubble-text">{msg.text}</div>

              {msg.meta && (
                <>
                  <div className="meta-row">
                    <span
                      className={`chip ${
                        msg.meta.confidence >= 0.5
                          ? "good"
                          : msg.meta.confidence >= 0.3
                            ? "mid"
                            : "bad"
                      }`}
                      title="Validator similarity score"
                    >
                      confidence {(msg.meta.confidence * 100).toFixed(0)}%
                    </span>
                    <span className={`chip boost-${msg.meta.boost}`}>
                      boost: {msg.meta.boost}
                    </span>
                    <span className="chip">
                      {msg.meta.is_valid ? "✓ grounded" : "⚠ weakly grounded"}
                    </span>
                    <span className="chip">{msg.meta.latency.toFixed(1)}s</span>
                    {msg.meta.retries > 0 && (
                      <span className="chip">
                        {msg.meta.retries} retr{msg.meta.retries > 1 ? "ies" : "y"}
                      </span>
                    )}
                  </div>

                  {msg.meta.retrieved_docs.length > 0 && (
                    <details className="sources">
                      <summary>
                        {msg.meta.citations.length} source
                        {msg.meta.citations.length !== 1 ? "s" : ""}
                      </summary>
                      {msg.meta.retrieved_docs.map((doc, i) => (
                        <div key={i} className="source-item">
                          <div className="source-name">
                            {msg.meta!.sources[i]?.source || "Unknown"}
                            {msg.meta!.sources[i]?.chunk !== undefined &&
                              ` · chunk ${msg.meta!.sources[i].chunk}`}
                            {msg.meta!.distances[i] !== undefined &&
                              ` · distance ${msg.meta!.distances[i].toFixed(1)}`}
                          </div>
                          <div className="source-text">
                            {doc.length > 400 ? doc.slice(0, 400) + "…" : doc}
                          </div>
                        </div>
                      ))}
                    </details>
                  )}

                  <StarRating
                    rated={msg.rated}
                    onRate={(r) => rate(msg, r)}
                  />
                </>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="bubble-row assistant">
            <div className="bubble assistant thinking">
              <span className="spinner" />
              {THINKING_STAGES[stage]}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={onSubmit}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            apiOnline
              ? "Ask a question about your documents…"
              : "API offline — start the backend first"
          }
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>
    </div>
  );
}
