import { cn } from "@/lib/utils";

export function Badge({
  children,
  variant = "neutral",
  className,
}: {
  children: React.ReactNode;
  variant?: "neutral" | "success" | "accent" | "danger";
  className?: string;
}) {
  const variants: Record<string, string> = {
    neutral: "bg-bg-raised text-ink-muted border-border",
    success: "bg-success/10 text-success border-success/20",
    accent: "bg-accent/10 text-accent border-accent/25",
    danger: "bg-danger/10 text-danger border-danger/20",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
