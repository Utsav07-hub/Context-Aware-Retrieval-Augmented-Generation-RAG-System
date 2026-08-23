"use client";

import { useEffect, useRef, useState } from "react";
import { CheckCircle2, FileText, X, Youtube } from "lucide-react";
import type { Source } from "@/lib/types";
import { addYouTubeSource, ApiError, uploadSource } from "@/lib/api";
import { cn } from "@/lib/utils";
import { IndexingProgress } from "./IndexingProgress";
import { DocumentDropzone } from "./DocumentDropzone";
import { YoutubeForm } from "./YoutubeForm";
import { Button } from "@/components/ui/Button";

type Tab = "youtube" | "document";
type Stage = "form" | "working" | "done" | "error";

interface AddSourceModalProps {
  onClose: () => void;
  onAdded: (source: Source) => void;
}

export function AddSourceModal({ onClose, onAdded }: AddSourceModalProps) {
  const [tab, setTab] = useState<Tab>("youtube");
  const [stage, setStage] = useState<Stage>("form");
  const [step, setStep] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Source | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  function startProgress() {
    setStep(0);
    intervalRef.current = setInterval(() => {
      setStep((s) => (s < 2 ? s + 1 : s));
    }, 900);
  }

  function stopProgress() {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  async function handleYoutube(url: string) {
    setStage("working");
    setError(null);
    startProgress();
    try {
      const source = await addYouTubeSource(url);
      setStep(3);
      stopProgress();
      setResult(source);
      setStage("done");
      onAdded(source);
    } catch (e) {
      stopProgress();
      setStage("error");
      setError(
        e instanceof ApiError
          ? e.message
          : "Something went wrong while adding this video."
      );
    }
  }

  async function handleFile(file: File) {
    setStage("working");
    setError(null);
    startProgress();
    try {
      const source = await uploadSource(file);
      setStep(3);
      stopProgress();
      setResult(source);
      setStage("done");
      onAdded(source);
    } catch (e) {
      stopProgress();
      setStage("error");
      setError(
        e instanceof ApiError
          ? e.message
          : `Something went wrong while adding "${file.name}".`
      );
    }
  }

  function reset() {
    setStage("form");
    setError(null);
    setResult(null);
    setStep(0);
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-md rounded-2xl border border-border bg-bg-panel p-6 shadow-2xl"
      >
        <div className="mb-1 flex items-start justify-between">
          <div>
            <h2 className="text-base font-semibold text-ink">Add Knowledge</h2>
            <p className="mt-0.5 text-sm text-ink-muted">
              Choose a source to add to your knowledge base.
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-ink-faint transition-colors hover:bg-bg-hover hover:text-ink"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {stage === "form" && (
          <>
            <div className="mt-5 grid grid-cols-2 gap-2">
              <button
                onClick={() => setTab("youtube")}
                className={cn(
                  "flex flex-col items-start gap-1 rounded-xl border p-3.5 text-left transition-colors",
                  tab === "youtube"
                    ? "border-accent/60 bg-accent/5"
                    : "border-border hover:bg-bg-hover"
                )}
              >
                <Youtube className="h-4 w-4 text-red-400" />
                <span className="text-sm font-medium text-ink">YouTube</span>
                <span className="text-xs text-ink-faint">
                  Paste a video URL
                </span>
              </button>
              <button
                onClick={() => setTab("document")}
                className={cn(
                  "flex flex-col items-start gap-1 rounded-xl border p-3.5 text-left transition-colors",
                  tab === "document"
                    ? "border-accent/60 bg-accent/5"
                    : "border-border hover:bg-bg-hover"
                )}
              >
                <FileText className="h-4 w-4 text-blue-400" />
                <span className="text-sm font-medium text-ink">Document</span>
                <span className="text-xs text-ink-faint">
                  PDF, DOCX, TXT or Markdown
                </span>
              </button>
            </div>

            <div className="mt-5">
              {tab === "youtube" ? (
                <YoutubeForm onSubmit={handleYoutube} />
              ) : (
                <DocumentDropzone onFileSelected={handleFile} />
              )}
            </div>
          </>
        )}

        {stage === "working" && <IndexingProgress activeStep={step} />}

        {stage === "done" && result && (
          <div className="flex flex-col items-center gap-3 py-4 text-center">
            <div className="grid h-12 w-12 place-items-center rounded-full bg-success/15 text-success">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-ink">
                Knowledge indexed
              </p>
              <p className="text-sm text-ink-muted">
                {result.chunk_count} chunks added
              </p>
            </div>
            <Button onClick={onClose} className="mt-2 w-full">
              Done
            </Button>
          </div>
        )}

        {stage === "error" && (
          <div className="flex flex-col gap-3 py-2">
            <div className="rounded-lg border border-danger/25 bg-danger/10 px-3.5 py-3 text-sm text-danger">
              {error}
            </div>
            <Button variant="secondary" onClick={reset}>
              Try again
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
