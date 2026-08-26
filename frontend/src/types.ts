export interface SourceRef {
  source: string;
  chunk?: number;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  is_valid: boolean;
  boost: string;
  retries: number;
  latency: number;
  citations: string[];
  sources: SourceRef[];
  retrieved_docs: string[];
  distances: number[];
}

export interface Health {
  status: string;
  version: string;
  llm_provider: string;
  llm_ok: boolean;
  embedding_provider: string;
  documents_indexed: number;
}

export interface AgentMetric {
  count: number;
  avg_latency: number;
  max_latency: number;
  min_latency: number;
}

export interface FeedbackMetrics {
  total_feedback: number;
  average_rating: number;
  highest_rating: number;
  lowest_rating: number;
}

export interface ConfidenceMetrics {
  average_confidence: number;
  highest_confidence: number;
  lowest_confidence: number;
}

export interface DocInfo {
  source: string;
  chunks: number;
}

export interface DocumentsResponse {
  documents: DocInfo[];
  total_chunks: number;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant" | "error";
  text: string;
  meta?: QueryResponse;
  rated?: number;
}
