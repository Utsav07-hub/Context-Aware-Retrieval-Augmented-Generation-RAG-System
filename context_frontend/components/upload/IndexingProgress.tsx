"use client";

import { Check, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

const STEPS = ["Uploading", "Processing", "Creating embeddings", "Indexing"];

export function IndexingProgress({ activeStep }: { activeStep: number }) {
  return (
    <div className="flex flex-col gap-4 py-2">
      <p className="text-sm font-medium text-ink">Adding knowledge...</p>
      <div className="flex flex-col gap-2.5">
        {STEPS.map((label, i) => {
          const done = i < activeStep;
          const current = i === activeStep;
          return (
            <div key={label} className="flex items-center gap-2.5 text-sm">
              <span
                className={cn(
                  "grid h-4 w-4 shrink-0 place-items-center rounded-full border",
                  done && "border-success bg-success/20 text-success",
                  current && "border-accent bg-accent/20 text-accent",
                  !done && !current && "border-border text-ink-faint"
                )}
              >
                {done ? (
                  <Check className="h-2.5 w-2.5" strokeWidth={3} />
                ) : current ? (
                  <Loader2 className="h-2.5 w-2.5 animate-spin" />
                ) : (
                  <span className="h-1 w-1 rounded-full bg-current" />
                )}
              </span>
              <span
                className={cn(
                  done && "text-ink-muted",
                  current && "text-ink font-medium",
                  !done && !current && "text-ink-faint"
                )}
              >
                {label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
