"use client";

import { Layers, Plus, Settings, FileText, Youtube } from "lucide-react";
import type { Source, SourceFilter } from "@/lib/types";
import { cn } from "@/lib/utils";

interface SidebarProps {
  sources: Source[];
  filter: SourceFilter;
  onFilterChange: (filter: SourceFilter) => void;
  onAddSource: () => void;
  onSelectRecent: (sourceId: string) => void;
}

export function Sidebar({
  sources,
  filter,
  onFilterChange,
  onAddSource,
  onSelectRecent,
}: SidebarProps) {
  const youtubeCount = sources.filter((s) => s.source_type === "youtube").length;
  const docCount = sources.length - youtubeCount;
  const recent = [...sources].slice(-5).reverse();

  const navItem = (
    key: SourceFilter,
    label: string,
    count: number,
    icon: React.ReactNode
  ) => (
    <button
      onClick={() => onFilterChange(key)}
      className={cn(
        "flex w-full items-center justify-between rounded-lg px-2.5 py-1.5 text-sm transition-colors",
        filter === key
          ? "bg-bg-raised text-ink"
          : "text-ink-muted hover:bg-bg-hover hover:text-ink"
      )}
    >
      <span className="flex items-center gap-2">
        {icon}
        {label}
      </span>
      <span className="text-xs text-ink-faint">{count}</span>
    </button>
  );

  return (
    <aside className="flex h-full w-[248px] shrink-0 flex-col border-r border-border bg-bg-panel">
      <div className="flex items-center gap-2.5 px-4 pt-5 pb-4">
        <div className="grid h-8 w-8 place-items-center rounded-lg bg-accent/15 text-accent">
          <Layers className="h-4 w-4" strokeWidth={2.5} />
        </div>
        <div>
          <p className="text-sm font-semibold leading-tight text-ink">Context</p>
          <p className="text-[11px] leading-tight text-ink-faint">
            AI Knowledge Workspace
          </p>
        </div>
      </div>

      <div className="px-3">
        <button
          onClick={onAddSource}
          className="flex w-full items-center justify-center gap-1.5 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
        >
          <Plus className="h-4 w-4" strokeWidth={2.5} />
          Add Source
        </button>
      </div>

      <nav className="mt-6 flex flex-col gap-0.5 px-3">
        <p className="mb-1.5 px-2.5 text-[11px] font-semibold tracking-wide text-ink-faint">
          KNOWLEDGE
        </p>
        {navItem(
          "all",
          "All Sources",
          sources.length,
          <Layers className="h-3.5 w-3.5" />
        )}
        {navItem(
          "youtube",
          "YouTube",
          youtubeCount,
          <Youtube className="h-3.5 w-3.5" />
        )}
        {navItem(
          "documents",
          "Documents",
          docCount,
          <FileText className="h-3.5 w-3.5" />
        )}
      </nav>

      <div className="mt-6 flex-1 overflow-y-auto px-3">
        <p className="mb-1.5 px-2.5 text-[11px] font-semibold tracking-wide text-ink-faint">
          RECENT
        </p>
        {recent.length === 0 ? (
          <p className="px-2.5 text-xs text-ink-faint">
            Sources you add will show up here.
          </p>
        ) : (
          <div className="flex flex-col gap-0.5">
            {recent.map((s) => (
              <button
                key={s.source_id}
                onClick={() => onSelectRecent(s.source_id)}
                className="flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-left text-sm text-ink-muted transition-colors hover:bg-bg-hover hover:text-ink"
              >
                {s.source_type === "youtube" ? (
                  <Youtube className="h-3.5 w-3.5 shrink-0 text-red-400" />
                ) : (
                  <FileText className="h-3.5 w-3.5 shrink-0 text-ink-faint" />
                )}
                <span className="truncate">{s.title}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-border p-3">
        <button className="flex w-full items-center gap-2 rounded-lg px-2.5 py-2 text-sm text-ink-muted transition-colors hover:bg-bg-hover hover:text-ink">
          <Settings className="h-3.5 w-3.5" />
          Settings
        </button>
      </div>
    </aside>
  );
}
