import type { DocumentExtension, Source, SourceType } from "./types";

export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(" ");
}

/** Formats seconds as m:ss for YouTube timestamps, e.g. 84 -> "1:24". */
export function formatTimestamp(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export function youtubeTimestampUrl(videoId: string, seconds: number): string {
  return `https://www.youtube.com/watch?v=${videoId}&t=${Math.floor(
    seconds
  )}s`;
}

export function extensionFromFilename(name: string): DocumentExtension | null {
  const ext = name.split(".").pop()?.toLowerCase();
  if (ext === "pdf" || ext === "docx" || ext === "txt" || ext === "md") {
    return ext;
  }
  return null;
}

const ACCEPTED_EXTENSIONS: DocumentExtension[] = ["pdf", "docx", "txt", "md"];

export function isSupportedDocument(file: File): boolean {
  const ext = extensionFromFilename(file.name);
  return ext !== null && ACCEPTED_EXTENSIONS.includes(ext);
}

export function isValidYoutubeUrl(url: string): boolean {
  try {
    const u = new URL(url.trim());
    const host = u.hostname.replace(/^www\./, "");
    if (host === "youtu.be") {
      return u.pathname.length > 1;
    }
    if (host === "youtube.com" || host === "m.youtube.com") {
      return u.searchParams.has("v") || u.pathname.startsWith("/shorts/");
    }
    return false;
  } catch {
    return false;
  }
}

export function sourceTypeLabel(type: SourceType): string {
  switch (type) {
    case "youtube":
      return "YouTube";
    case "pdf":
      return "PDF";
    case "docx":
      return "DOCX";
    case "txt":
      return "TXT";
    case "md":
      return "Markdown";
    default:
      return type;
  }
}

export function isDocumentSource(source: Source): boolean {
  return source.source_type !== "youtube";
}

export function relativeTime(fromMs: number): string {
  const diff = Date.now() - fromMs;
  const min = Math.floor(diff / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min} minute${min === 1 ? "" : "s"} ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} hour${hr === 1 ? "" : "s"} ago`;
  const day = Math.floor(hr / 24);
  return `${day} day${day === 1 ? "" : "s"} ago`;
}
