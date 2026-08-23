"use client";

import { useState } from "react";
import { isValidYoutubeUrl } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

interface YoutubeFormProps {
  onSubmit: (url: string) => void;
  disabled?: boolean;
}

export function YoutubeForm({ onSubmit, disabled }: YoutubeFormProps) {
  const [url, setUrl] = useState("");
  const [touched, setTouched] = useState(false);

  const valid = isValidYoutubeUrl(url);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTouched(true);
    if (!valid) return;
    onSubmit(url.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-2">
      <label className="text-xs font-medium text-ink-muted">
        Paste URL
      </label>
      <input
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onBlur={() => setTouched(true)}
        placeholder="https://youtu.be/VIDEO_ID"
        disabled={disabled}
        className="w-full rounded-lg border border-border bg-bg-raised px-3 py-2.5 text-sm text-ink placeholder:text-ink-faint focus:border-accent/50"
      />
      {touched && url.length > 0 && !valid && (
        <p className="text-xs text-danger">
          That doesn&apos;t look like a valid YouTube URL.
        </p>
      )}
      <Button
        type="submit"
        disabled={disabled || url.length === 0}
        loading={disabled}
        className="mt-2 w-full"
      >
        Add to Knowledge
      </Button>
    </form>
  );
}
