// Types mirroring the existing FastAPI backend contracts exactly.
// Do not add fields the backend does not return.

export type SourceType = "youtube" | "pdf" | "docx" | "txt" | "md";

export interface Source {
  source_id: string;
  source_type: SourceType;
  title: string;
  source: string;
  video_id: string | null;
  chunk_count: number;
  status: "indexed" | string;
}

export interface YoutubeSourceRequest {
  url: string;
}

export interface ChatRequest {
  source_id: string;
  question: string;
}

export interface ChatSourceCitation {
  source_number: number;
  video_id: string | null;
  video_title: string | null;
  start_time: number | null;
  end_time: number | null;
  source: string;
  chunk_id: string;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSourceCitation[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatSourceCitation[];
  createdAt: number;
  error?: boolean;
}

export interface HealthResponse {
  status?: string;
  [key: string]: unknown;
}

export type SourceFilter = "all" | "youtube" | "documents";

// Discriminates uploaded document sub-types by extension for display purposes only.
export const DOCUMENT_EXTENSIONS = ["pdf", "docx", "txt", "md"] as const;
export type DocumentExtension = (typeof DOCUMENT_EXTENSIONS)[number];
