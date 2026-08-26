import { ChangeEvent, DragEvent, useEffect, useState } from "react";
import { api } from "../api";
import type { DocInfo } from "../types";

export default function DocumentsView() {
  const [docs, setDocs] = useState<DocInfo[]>([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      const res = await api.documents();
      setDocs(res.documents);
      setTotalChunks(res.total_chunks);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  const upload = async (file: File) => {
    if (!file) return;
    setBusy(true);
    setMessage(`Ingesting ${file.name} — chunking + embedding…`);
    setError("");
    try {
      const res = await api.upload(file);
      setMessage(`✓ ${res.source} indexed as ${res.chunks_added} chunks`);
      await refresh();
    } catch (err) {
      setMessage("");
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  };

  const onPick = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) upload(file);
    e.target.value = "";
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) upload(file);
  };

  const remove = async (source: string) => {
    if (!window.confirm(`Remove "${source}" and all its chunks from the index?`))
      return;
    setBusy(true);
    try {
      const res = await api.deleteDocument(source);
      setMessage(`Removed ${res.source} (${res.chunks_removed} chunks)`);
      setError("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="documents">
      <h1>Knowledge Base</h1>
      <p className="muted">
        {docs.length} document{docs.length !== 1 ? "s" : ""} · {totalChunks}{" "}
        chunks in the vector store
      </p>

      <label
        className={`dropzone ${dragOver ? "over" : ""} ${busy ? "busy" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
      >
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={onPick}
          disabled={busy}
          hidden
        />
        <div className="dropzone-icon">{busy ? "⏳" : "📤"}</div>
        <div>
          {busy
            ? "Working…"
            : "Drop a PDF or TXT here, or click to browse"}
        </div>
        <div className="dropzone-hint">
          Files are chunked, embedded and stored in ChromaDB
        </div>
      </label>

      {message && <div className="banner ok">{message}</div>}
      {error && <div className="banner error">{error}</div>}

      <div className="doc-list">
        {docs.map((d) => (
          <div key={d.source} className="doc-row">
            <span className="doc-icon">📄</span>
            <div className="doc-info">
              <div className="doc-name">{d.source}</div>
              <div className="doc-chunks">{d.chunks} chunks</div>
            </div>
            <button
              className="doc-delete"
              disabled={busy}
              onClick={() => remove(d.source)}
              title="Remove from index"
            >
              ✕
            </button>
          </div>
        ))}
        {docs.length === 0 && !error && (
          <p className="muted">No documents indexed yet.</p>
        )}
      </div>
    </div>
  );
}
