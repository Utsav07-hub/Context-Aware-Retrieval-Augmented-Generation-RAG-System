"use client";

import { useMemo, useState } from "react";
import { Library, Plus, Search, Wifi, WifiOff } from "lucide-react";
import type { Source, SourceFilter } from "@/lib/types";
import { SourceCard } from "./SourceCard";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

type SortOrder = "newest" | "oldest" | "chunks";

interface SourcePanelProps {
  sources: Source[];
  filter: SourceFilter;
  selectedSourceId: string | null;
  addedAt: Record<string, number>;
  backendOnline: boolean | null;
  onSelectSource: (source: Source) => void;
  onAddSource: () => void;
}

const FILTER_LABEL: Record<SourceFilter, string> = {
  all: "All Sources",
  youtube: "YouTube",
  documents: "Documents",
};

export function SourcePanel({
  sources,
  filter,
  selectedSourceId,
  addedAt,
  backendOnline,
  onSelectSource,
  onAddSource,
}: SourcePanelProps) {
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<SortOrder>("newest");

  const filtered = useMemo(() => {
    let list = sources.filter((s) =>
      filter === "all"
        ? true
        : filter === "youtube"
        ? s.source_type === "youtube"
        : s.source_type !== "youtube"
    );

    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter((s) => s.title.toLowerCase().includes(q));
    }

    list = [...list].sort((a, b) => {
      if (sort === "chunks") return b.chunk_count - a.chunk_count;
      const at = addedAt[a.source_id] ?? 0;
      const bt = addedAt[b.source_id] ?? 0;
      return sort === "newest" ? bt - at : at - bt;
    });

    return list;
  }, [sources, filter, query, sort, addedAt]);

  return (
    <section className="flex h-full min-w-0 flex-1 flex-col overflow-hidden">
      <header className="flex shrink-0 items-start justify-between gap-4 border-b border-border px-6 py-5">
        <div>
          <h1 className="text-lg font-semibold text-ink">
            {FILTER_LABEL[filter]}
          </h1>
          <p className="text-sm text-ink-muted">Your knowledge base</p>
        </div>
        <div className="flex items-center gap-3">
          {backendOnline !== null && (
            <span
              className="inline-flex items-center gap-1.5 rounded-full border border-border bg-bg-raised px-2.5 py-1 text-xs font-medium"
              title={
                backendOnline
                  ? "Connected to the FastAPI backend"
                  : "Backend unreachable"
              }
            >
              {backendOnline ? (
                <>
                  <span className="h-1.5 w-1.5 rounded-full bg-success" />
                  <span className="text-success">RAG ACTIVE</span>
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3 text-danger" />
                  <span className="text-danger">OFFLINE</span>
                </>
              )}
            </span>
          )}
        </div>
      </header>

      <div className="flex shrink-0 flex-wrap items-center gap-2 border-b border-border px-6 py-3">
        <div className="relative min-w-[200px] flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-faint" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search sources..."
            className="w-full rounded-lg border border-border bg-bg-raised py-2 pl-8 pr-3 text-sm text-ink placeholder:text-ink-faint focus:border-accent/50"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortOrder)}
          className="rounded-lg border border-border bg-bg-raised px-3 py-2 text-sm text-ink-muted focus:border-accent/50"
        >
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="chunks">Most Chunks</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto px-6 py-5">
        {sources.length === 0 ? (
          <EmptyState
            icon={<Library className="h-5 w-5" />}
            title="No knowledge yet"
            description="Add a YouTube video or a document to start building your knowledge base."
            action={
              <Button onClick={onAddSource} className="mt-1">
                <Plus className="h-4 w-4" />
                Add Source
              </Button>
            }
          />
        ) : filtered.length === 0 ? (
          <EmptyState
            icon={<Search className="h-5 w-5" />}
            title="No matching sources"
            description="Try a different search term or filter."
          />
        ) : (
          <>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-2">
              {filtered.map((s) => (
                <SourceCard
                  key={s.source_id}
                  source={s}
                  active={s.source_id === selectedSourceId}
                  addedAt={addedAt[s.source_id]}
                  onSelect={onSelectSource}
                />
              ))}
            </div>
            <p className="mt-6 text-center text-xs text-ink-faint">
              {filtered.length} source{filtered.length === 1 ? "" : "s"} total
            </p>
          </>
        )}
      </div>
    </section>
  );
}
