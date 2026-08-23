import { FileText, Youtube } from "lucide-react";
import type { SourceType } from "@/lib/types";
import { cn } from "@/lib/utils";

const STYLES: Record<SourceType, { bg: string; fg: string }> = {
  youtube: { bg: "bg-red-500/15", fg: "text-red-400" },
  pdf: { bg: "bg-red-500/15", fg: "text-red-400" },
  docx: { bg: "bg-blue-500/15", fg: "text-blue-400" },
  txt: { bg: "bg-zinc-500/15", fg: "text-zinc-300" },
  md: { bg: "bg-violet-500/15", fg: "text-violet-300" },
};

export function SourceIcon({
  type,
  size = "md",
}: {
  type: SourceType;
  size?: "sm" | "md";
}) {
  const style = STYLES[type] ?? STYLES.txt;
  const box = size === "sm" ? "h-7 w-7" : "h-9 w-9";
  const icon = size === "sm" ? "h-3.5 w-3.5" : "h-4 w-4";

  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center rounded-lg",
        box,
        style.bg,
        style.fg
      )}
    >
      {type === "youtube" ? (
        <Youtube className={icon} strokeWidth={2} />
      ) : (
        <FileText className={icon} strokeWidth={2} />
      )}
    </div>
  );
}
