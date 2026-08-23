class ContextBuilder:

    def __init__(self, max_chars: int = 8000):
        self.max_chars = max_chars

    def build(self, documents):

        context_parts = []
        total_chars = 0

        for index, document in enumerate(
            documents,
            start=1
        ):

            metadata = document.metadata

            video_id = metadata.get(
                "video_id",
                "unknown"
            )

            start_time = metadata.get(
                "start_time",
                0
            )

            end_time = metadata.get(
                "end_time",
                0
            )

            text = document.page_content.strip()

            context = (
                f"[SOURCE {index}]\n"
                f"Video ID: {video_id}\n"
                f"Timestamp: "
                f"{self.format_time(start_time)}"
                f" - "
                f"{self.format_time(end_time)}\n"
                f"Content:\n"
                f"{text}\n"
            )

            if total_chars + len(context) > self.max_chars:
                break

            context_parts.append(context)
            total_chars += len(context)

        return "\n---\n".join(context_parts)

    @staticmethod
    def format_time(seconds):

        seconds = int(seconds)

        minutes = seconds // 60
        remaining_seconds = seconds % 60

        return f"{minutes:02d}:{remaining_seconds:02d}"