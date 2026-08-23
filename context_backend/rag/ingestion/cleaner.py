import re


class TranscriptCleaner:

    def clean_text(self, text: str) -> str:
        """
        Clean an individual transcript snippet.
        """

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def clean(self, snippets: list[dict]) -> list[dict]:
        """
        Clean transcript snippets while preserving timestamps.
        """

        cleaned = []

        for snippet in snippets:

            text = self.clean_text(snippet["text"])

            # Ignore empty snippets
            if not text:
                continue

            cleaned.append({
                "text": text,
                "start": snippet["start"],
                "duration": snippet["duration"],
                "end": snippet["start"] + snippet["duration"]
            })

        return cleaned