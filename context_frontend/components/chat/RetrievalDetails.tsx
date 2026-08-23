"use client";

import { useState } from "react";
import { ChevronRight } from "lucide-react";
import type { ChatSourceCitation } from "@/lib/types";
import { cn } from "@/lib/utils";

export function RetrievalDetails({
  sources,
}: {
  sources: ChatSourceCitation[];
}) {
  const [open, setOpen] = useState(false);

  return (
    <div className="mt-3 border-t border-border pt-2.5">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 text-xs font-medium text-ink-muted transition-colors hover:text-ink"
      >
        <ChevronRight
          className={cn(
            "h-3 w-3 transition-transform",
            open && "rotate-90"
          )}
        />
        Retrieval details
      </button>

      {open && (
        <div className="mt-2.5 space-y-2 rounded-lg border border-border bg-bg-raised p-3 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-ink-faint">Retrieved sources</span>
            <span className="font-mono text-ink">{sources.length}</span>
          </div>
          <div className="space-y-1.5 border-t border-border pt-2">
            {sources.map((s) => (
              <div
                key={s.chunk_id}
                className="flex items-center justify-between gap-3"
              >
                <span className="truncate text-ink-faint">
                  #{s.source_number} · {s.video_title ?? s.source}
                </span>
                <span className="shrink-0 font-mono text-ink-muted">
                  {s.chunk_id}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
