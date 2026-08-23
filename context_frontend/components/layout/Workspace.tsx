"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, Menu, MessageSquare, X } from "lucide-react";
import type { Source, SourceFilter } from "@/lib/types";
import { getSources, healthCheck } from "@/lib/api";
import { Sidebar } from "./Sidebar";
import { SourcePanel } from "@/components/sources/SourcePanel";
import { ChatPanel } from "@/components/chat/ChatPanel";
import { AddSourceModal } from "@/components/upload/AddSourceModal";

type MobilePanel = "sources" | "chat";

export function Workspace() {
  const [sources, setSources] = useState<Source[]>([]);
  const [addedAt, setAddedAt] = useState<Record<string, number>>({});
  const [filter, setFilter] = useState<SourceFilter>("all");
  const [selectedSourceId, setSelectedSourceId] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [mobilePanel, setMobilePanel] = useState<MobilePanel>("sources");

  useEffect(() => {
    let cancelled = false;
    healthCheck()
      .then(() => !cancelled && setBackendOnline(true))
      .catch(() => !cancelled && setBackendOnline(false));
    return () => {
      cancelled = true;
    };
  }, []);

  const handleAdded = useCallback((source: Source) => {
    setSources((prev) => [...prev, source]);
    setAddedAt((prev) => ({ ...prev, [source.source_id]: Date.now() }));
    setSelectedSourceId(source.source_id);
    setBackendOnline(true);
  }, []);

  const selectedSource =
    sources.find((s) => s.source_id === selectedSourceId) ?? null;

  function selectSource(source: Source) {
    setSelectedSourceId(source.source_id);
    setMobilePanel("chat");
  }

  function selectRecent(id: string) {
    setSelectedSourceId(id);
    setSidebarOpen(false);
    setMobilePanel("chat");
  }

  useEffect(() => {
  let cancelled = false;
  healthCheck()
    .then(() => !cancelled && setBackendOnline(true))
    .catch(() => !cancelled && setBackendOnline(false));

  getSources()
    .then((restored) => {
      if (cancelled || restored.length === 0) return;
      setSources(restored);
    })
    .catch(() => {
      // No persistence endpoint yet, or it errored — degrade silently.
    });

  return () => {
    cancelled = true;
  };
  }, []);

  return (
    <div className="flex h-dvh flex-col overflow-hidden bg-bg">
      {backendOnline === false && (
        <div className="flex shrink-0 items-center gap-2 border-b border-danger/25 bg-danger/10 px-4 py-2 text-xs text-danger">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
          Couldn&apos;t connect to the RAG backend. Make sure the FastAPI
          server is running at http://127.0.0.1:8000.
        </div>
      )}

      {/* Top bar shown below lg, where the sidebar collapses into a drawer */}
      <div className="flex h-14 w-full shrink-0 items-center justify-between border-b border-border bg-bg-panel px-4 lg:hidden">
        <button onClick={() => setSidebarOpen(true)} className="text-ink-muted">
          <Menu className="h-5 w-5" />
        </button>
        <span className="text-sm font-semibold text-ink">Context</span>
        <div className="w-5" />
      </div>

      <div className="flex min-h-0 flex-1">
        {/* Sidebar: static on desktop, drawer below lg (tablet + mobile) */}
        <div className="hidden lg:block">
          <Sidebar
            sources={sources}
            filter={filter}
            onFilterChange={(f) => {
              setFilter(f);
              setMobilePanel("sources");
            }}
            onAddSource={() => setModalOpen(true)}
            onSelectRecent={selectRecent}
          />
        </div>

        {sidebarOpen && (
          <div
            className="fixed inset-0 z-40 flex bg-black/60 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <div onClick={(e) => e.stopPropagation()} className="relative">
              <Sidebar
                sources={sources}
                filter={filter}
                onFilterChange={(f) => {
                  setFilter(f);
                  setSidebarOpen(false);
                  setMobilePanel("sources");
                }}
                onAddSource={() => {
                  setModalOpen(true);
                  setSidebarOpen(false);
                }}
                onSelectRecent={selectRecent}
              />
              <button
                onClick={() => setSidebarOpen(false)}
                className="absolute right-3 top-4 text-ink-faint"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Sources panel: two-panel on tablet (md+), single column below md */}
        <div
          className={`min-w-0 flex-1 ${
            mobilePanel === "sources" ? "flex" : "hidden"
          } md:flex`}
        >
          <SourcePanel
            sources={sources}
            filter={filter}
            selectedSourceId={selectedSourceId}
            addedAt={addedAt}
            backendOnline={backendOnline}
            onSelectSource={selectSource}
            onAddSource={() => setModalOpen(true)}
          />
        </div>

        <div
          className={`${
            mobilePanel === "chat" ? "flex" : "hidden"
          } w-full md:flex md:w-auto`}
        >
          <ChatPanel
            selectedSource={selectedSource}
            onClearSource={() => setSelectedSourceId(null)}
          />
        </div>
      </div>

      {/* Mobile bottom nav (single-column breakpoint only) */}
      <div className="grid shrink-0 grid-cols-2 border-t border-border bg-bg-panel md:hidden">
        <button
          onClick={() => setMobilePanel("sources")}
          className={`flex flex-col items-center gap-0.5 py-2.5 text-xs ${
            mobilePanel === "sources" ? "text-accent" : "text-ink-faint"
          }`}
        >
          <Menu className="h-4 w-4" />
          Sources
        </button>
        <button
          onClick={() => setMobilePanel("chat")}
          className={`flex flex-col items-center gap-0.5 py-2.5 text-xs ${
            mobilePanel === "chat" ? "text-accent" : "text-ink-faint"
          }`}
        >
          <MessageSquare className="h-4 w-4" />
          Chat
        </button>
      </div>

      {modalOpen && (
        <AddSourceModal
          onClose={() => setModalOpen(false)}
          onAdded={handleAdded}
        />
      )}
    </div>
  );
}
