import type { ChatMessage } from "@/lib/types";
import { cn } from "@/lib/utils";
import { SourceCitations } from "./SourceCitations";

export function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] rounded-2xl rounded-br-md bg-accent px-4 py-2.5 text-sm text-white">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-start">
      <div
        className={cn(
          "max-w-[92%] rounded-2xl rounded-bl-md border px-4 py-3 text-sm leading-relaxed",
          message.error
            ? "border-danger/25 bg-danger/10 text-danger"
            : "border-border bg-bg-panel text-ink"
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {!message.error && message.sources && message.sources.length > 0 && (
          <SourceCitations sources={message.sources} />
        )}
      </div>
    </div>
  );
}
