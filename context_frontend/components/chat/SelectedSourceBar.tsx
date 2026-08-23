import { X } from "lucide-react";
import type { Source } from "@/lib/types";
import { SourceIcon } from "@/components/ui/SourceIcon";

export function SelectedSourceBar({
  source,
  onClear,
}: {
  source: Source | null;
  onClear: () => void;
}) {
  if (!source) {
    return (
      <p className="text-sm text-ink-faint">
        Select a source to start asking questions.
      </p>
    );
  }

  return (
    <div>
      <p className="mb-1.5 text-xs text-ink-faint">Using source</p>
      <div className="inline-flex items-center gap-2 rounded-full border border-border bg-bg-raised py-1 pl-1 pr-2.5">
        <SourceIcon type={source.source_type} size="sm" />
        <span className="max-w-[160px] truncate text-sm text-ink">
          {source.title}
        </span>
        <button
          onClick={onClear}
          className="text-ink-faint transition-colors hover:text-ink"
          aria-label="Clear selected source"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}
