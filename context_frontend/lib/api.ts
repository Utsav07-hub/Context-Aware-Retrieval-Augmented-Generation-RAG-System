import type {
  ChatRequest,
  ChatResponse,
  HealthResponse,
  Source,
} from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Wraps fetch so that network failures (backend not running) and non-2xx
 * responses both surface as a friendly ApiError instead of a raw stack trace.
 */
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, init);
  } catch {
    throw new ApiError(
      "Couldn't connect to the RAG backend. Make sure the FastAPI server is running at " +
        API_BASE_URL +
        "."
    );
  }

  if (!res.ok) {
    let detail = "";
    try {
      const body = await res.json();
      detail =
        typeof body?.detail === "string"
          ? body.detail
          : JSON.stringify(body?.detail ?? body);
    } catch {
      // response wasn't JSON, ignore
    }
    throw new ApiError(
      detail || `Request failed (${res.status}). Please try again.`,
      res.status
    );
  }

  return res.json() as Promise<T>;
}

export function healthCheck(): Promise<HealthResponse> {
  return request<HealthResponse>("/api/health");
}

export function addYouTubeSource(url: string): Promise<Source> {
  return request<Source>("/api/sources/youtube", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
}

export function uploadSource(file: File): Promise<Source> {
  const formData = new FormData();
  formData.append("file", file);
  return request<Source>("/api/sources/upload", {
    method: "POST",
    body: formData,
  });
}

export function askQuestion(
  sourceId: string,
  question: string
): Promise<ChatResponse> {
  const payload: ChatRequest = { source_id: sourceId, question };
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export async function getSources(): Promise<Source[]> {
  const data = await request<Source[] | { sources: Source[] }>("/api/sources");
  return Array.isArray(data) ? data : data.sources ?? [];
}
