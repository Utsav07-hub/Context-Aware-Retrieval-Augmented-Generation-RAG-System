"use client";

import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { cn, isSupportedDocument } from "@/lib/utils";
import { Button } from "@/components/ui/Button";

interface DocumentDropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function DocumentDropzone({
  onFileSelected,
  disabled,
}: DocumentDropzoneProps) {
  const [dragging, setDragging] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFiles(files: FileList | null) {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!isSupportedDocument(file)) {
      setLocalError(
        `"${file.name}" isn't supported. Please use PDF, DOCX, TXT or Markdown.`
      );
      return;
    }
    setLocalError(null);
    onFileSelected(file);
  }

  return (
    <div className="flex flex-col gap-2">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) handleFiles(e.dataTransfer.files);
        }}
        className={cn(
          "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed px-6 py-10 text-center transition-colors",
          dragging ? "border-accent bg-accent/5" : "border-border",
          disabled && "pointer-events-none opacity-50"
        )}
      >
        <div className="grid h-11 w-11 place-items-center rounded-full bg-bg-raised text-ink-muted">
          <UploadCloud className="h-5 w-5" />
        </div>
        <div>
          <p className="text-sm font-medium text-ink">Drop a file here</p>
          <p className="text-xs text-ink-faint">or</p>
        </div>
        <Button
          type="button"
          variant="secondary"
          onClick={() => inputRef.current?.click()}
          disabled={disabled}
        >
          Browse Files
        </Button>
        <p className="text-[11px] text-ink-faint">
          Supported: PDF · DOCX · TXT · MD
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </div>
      {localError && <p className="text-xs text-danger">{localError}</p>}
    </div>
  );
}
