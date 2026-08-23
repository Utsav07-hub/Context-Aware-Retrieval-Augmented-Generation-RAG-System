from pathlib import Path

from langchain_core.documents import Document


class TextFileLoader:
    """Load plain text or Markdown files into LangChain Documents."""

    SUPPORTED_EXTENSIONS = {".txt", ".md"}

    def load(
        self,
        file_path: str | Path,
        source_id: str,
        file_name: str | None = None,
    ) -> list[Document]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        extension = path.suffix.lower()

        if extension not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                "TextFileLoader supports only .txt and .md files"
            )

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

        if not text:
            return []

        source_type = "markdown" if extension == ".md" else "txt"
        display_name = file_name or path.name

        return [
            Document(
                page_content=text,
                metadata={
                    "source_id": source_id,
                    "source_type": source_type,
                    "file_name": display_name,
                },
            )
        ]