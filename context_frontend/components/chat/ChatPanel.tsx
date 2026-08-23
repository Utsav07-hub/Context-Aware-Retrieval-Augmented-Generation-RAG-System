"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Info, Paperclip, SendHorizontal, Sparkles, Trash2 } from "lucide-react";
import type { ChatMessage, Source } from "@/lib/types";
import { askQuestion, ApiError } from "@/lib/api";
import { SelectedSourceBar } from "./SelectedSourceBar";
import { ChatMessageBubble } from "./ChatMessageBubble";

const SUGGESTIONS = [
  "What is the main idea?",
  "Explain this simply",
  "What are the key concepts?",
  "Summarize this source",
];

type LoadingPhase = null | "searching" | "generating";

interface ChatPanelProps {
  selectedSource: Source | null;
  onClearSource: () => void;
}

export function ChatPanel({ selectedSource, onClearSource }: ChatPanelProps) {
  const [messagesBySource, setMessagesBySource] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [input, setInput] = useState("");
  const [phase, setPhase] = useState<LoadingPhase>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const sourceId = selectedSource?.source_id ?? null;
  const messages = useMemo(
    () => (sourceId ? messagesBySource[sourceId] ?? [] : []),
    [sourceId, messagesBySource]
  );

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, phase]);

  function appendMessage(id: string, message: ChatMessage) {
    setMessagesBySource((prev) => ({
      ...prev,
      [id]: [...(prev[id] ?? []), message],
    }));
  }

  async function handleAsk(question: string) {
    const trimmed = question.trim();
    if (!trimmed) {
      setFormError("Type a question before sending.");
      return;
    }
    if (!selectedSource) {
      setFormError("Select a source to start asking questions.");
      return;
    }
    setFormError(null);

    const activeId = selectedSource.source_id;
    appendMessage(activeId, {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
      createdAt: Date.now(),
    });
    setInput("");
    setPhase("searching");

    const generatingTimeout = setTimeout(() => setPhase("generating"), 700);

    try {
      const res = await askQuestion(activeId, trimmed);
      appendMessage(activeId, {
        id: crypto.randomUUID(),
        role: "assistant",
        content: res.answer,
        sources: res.sources,
        createdAt: Date.now(),
      });
    } catch (e) {
      appendMessage(activeId, {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          e instanceof ApiError
            ? e.message
            : "Something went wrong answering that question. Please try again.",
        createdAt: Date.now(),
        error: true,
      });
    } finally {
      clearTimeout(generatingTimeout);
      setPhase(null);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    handleAsk(input);
  }

  function clearConversation() {
    if (!sourceId) return;
    setMessagesBySource((prev) => ({ ...prev, [sourceId]: [] }));
  }

  return (
    <section className="flex h-full w-full shrink-0 flex-col border-l border-border bg-bg-panel md:w-[340px] lg:w-[400px]">
      <header className="flex shrink-0 items-center justify-between border-b border-border px-5 py-5">
        <div>
          <h2 className="text-base font-semibold text-ink">AI Assistant</h2>
          <span className="mt-0.5 inline-flex items-center gap-1.5 text-xs font-medium text-success">
            <span className="h-1.5 w-1.5 rounded-full bg-success" />
            RAG Active
          </span>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button
              onClick={clearConversation}
              title="Clear conversation"
              className="rounded-md p-1.5 text-ink-faint transition-colors hover:bg-bg-hover hover:text-ink"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          )}
          <button
            title="RAG combines hybrid retrieval with Gemini to ground answers in your sources."
            className="rounded-md p-1.5 text-ink-faint transition-colors hover:bg-bg-hover hover:text-ink"
          >
            <Info className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      <div className="shrink-0 border-b border-border px-5 py-3.5">
        <SelectedSourceBar source={selectedSource} onClear={onClearSource} />
      </div>

      <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto px-5 py-5">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-5 text-center">
            <div className="grid h-11 w-11 place-items-center rounded-full bg-accent/10 text-accent">
              <Sparkles className="h-5 w-5" />
            </div>
            <p className="max-w-[240px] text-sm text-ink-muted">
              Ask questions about your selected knowledge.
            </p>
            <div className="flex w-full flex-col gap-1.5">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => handleAsk(s)}
                  disabled={!selectedSource || phase !== null}
                  className="rounded-lg border border-border bg-bg-raised px-3 py-2 text-left text-sm text-ink-muted transition-colors hover:border-accent/40 hover:text-ink disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((m) => (
              <ChatMessageBubble key={m.id} message={m} />
            ))}
            {phase && (
              <div className="flex items-center gap-2 text-sm text-ink-faint">
                <span className="flex gap-1">
                  <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-accent [animation-delay:0ms]" />
                  <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-accent [animation-delay:150ms]" />
                  <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-accent [animation-delay:300ms]" />
                </span>
                {phase === "searching"
                  ? "Searching knowledge..."
                  : "Generating answer..."}
              </div>
            )}
          </>
        )}
      </div>

      <form onSubmit={handleSubmit} className="shrink-0 border-t border-border p-4">
        {formError && (
          <p className="mb-2 text-xs text-danger">{formError}</p>
        )}
        <div className="flex items-end gap-2 rounded-xl border border-border bg-bg-raised p-1.5 pl-3.5 focus-within:border-accent/50">
          <button
            type="button"
            className="mb-1.5 shrink-0 text-ink-faint transition-colors hover:text-ink"
            title="Attachments aren't part of chat — add sources from the workspace"
          >
            <Paperclip className="h-4 w-4" />
          </button>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            placeholder="Ask anything about your knowledge..."
            className="max-h-32 flex-1 resize-none bg-transparent py-2 text-sm text-ink placeholder:text-ink-faint focus:outline-none"
          />
          <button
            type="submit"
            disabled={phase !== null}
            className="mb-1 grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-accent text-white transition-colors hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            <SendHorizontal className="h-4 w-4" />
          </button>
        </div>
        <p className="mt-1.5 text-[11px] text-ink-faint">Press Enter to send</p>
      </form>
    </section>
  );
}
