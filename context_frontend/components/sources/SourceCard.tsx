"use client";

import { Check, CheckCircle2 } from "lucide-react";
import type { Source } from "@/lib/types";
import { cn, relativeTime, sourceTypeLabel } from "@/lib/utils";
import { SourceIcon } from "@/components/ui/SourceIcon";
import { Badge } from "@/components/ui/Badge";

interface SourceCardProps {
  source: Source;
  active: boolean;
  addedAt?: number;
  onSelect: (source: Source) => void;
}

export function SourceCard({ source, active, addedAt, onSelect }: SourceCardProps) {
  const indexed = source.status === "indexed";

  return (
    <button
      onClick={() => onSelect(source)}
      className={cn(
        "group relative flex flex-col gap-3 rounded-xl border bg-bg-panel p-4 text-left transition-all duration-150",
        active
          ? "border-accent/60 ring-1 ring-accent/40"
          : "border-border hover:border-border hover:bg-bg-hover"
      )}
    >
      {active && (
        <div className="absolute right-3 top-3 grid h-5 w-5 place-items-center rounded-full bg-accent text-white">
          <Check className="h-3 w-3" strokeWidth={3} />
        </div>
      )}

      <div className="flex items-start gap-3 pr-6">
        <SourceIcon type={source.source_type} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-ink">
            {source.title}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Badge>{sourceTypeLabel(source.source_type)}</Badge>
        {indexed ? (
          <Badge variant="success">
            <CheckCircle2 className="h-3 w-3" /> Indexed
          </Badge>
        ) : (
          <Badge variant="neutral">{source.status}</Badge>
        )}
      </div>

      <div className="flex items-center justify-between text-xs text-ink-faint">
        <span>{source.chunk_count} chunks</span>
        {addedAt && <span>{relativeTime(addedAt)}</span>}
      </div>
    </button>
  );
}
