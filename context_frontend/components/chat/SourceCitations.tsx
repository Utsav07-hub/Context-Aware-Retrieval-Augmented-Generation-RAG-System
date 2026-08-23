"use client";

import { FileText, Youtube } from "lucide-react";
import type { ChatSourceCitation } from "@/lib/types";
import { formatTimestamp, youtubeTimestampUrl } from "@/lib/utils";
import { RetrievalDetails } from "./RetrievalDetails";

export function SourceCitations({
  sources,
}: {
  sources: ChatSourceCitation[];
}) {
  if (sources.length === 0) return null;

  // Group citations by video/document so each source shows once with all
  // of its timestamps, mirroring how the backend returns per-chunk hits.
  const groups = new Map<string, ChatSourceCitation[]>();
  for (const s of sources) {
    const key = s.video_id ?? s.source;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(s);
  }

  return (
    <div className="mt-3">
      <p className="mb-2 text-xs font-medium text-ink-faint">Sources</p>
      <div className="space-y-2">
        {[...groups.entries()].map(([key, group]) => {
          const first = group[0];
          const isYoutube = Boolean(first.video_id);

          return (
            <div
              key={key}
              className="rounded-lg border border-border bg-bg-raised p-3"
            >
              <div className="mb-1.5 flex items-center gap-2 text-sm font-medium text-ink">
                {isYoutube ? (
                  <Youtube className="h-3.5 w-3.5 shrink-0 text-red-400" />
                ) : (
                  <FileText className="h-3.5 w-3.5 shrink-0 text-blue-400" />
                )}
                <span className="truncate">
                  {first.video_title ?? first.source}
                </span>
              </div>

              {isYoutube ? (
                <div className="flex flex-col gap-1">
                  {group
                    .filter((g) => g.start_time !== null)
                    .map((g) => (
                      <a
                        key={g.chunk_id}
                        href={youtubeTimestampUrl(
                          g.video_id as string,
                          g.start_time as number
                        )}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 rounded-md px-1.5 py-1 text-xs text-ink-muted transition-colors hover:bg-bg-hover hover:text-accent"
                      >
                        <span className="w-10 shrink-0 font-mono text-accent">
                          {formatTimestamp(g.start_time as number)}
                        </span>
                        <span className="truncate">
                          Source {g.source_number}
                        </span>
                      </a>
                    ))}
                </div>
              ) : (
                <p className="text-xs text-ink-faint">{first.source}</p>
              )}
            </div>
          );
        })}
      </div>

      <RetrievalDetails sources={sources} />
    </div>
  );
}
