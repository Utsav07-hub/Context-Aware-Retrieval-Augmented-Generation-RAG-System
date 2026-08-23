from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


class PDFLoader:
    """Load a PDF into LangChain Documents, one document per page."""

    def load(
        self,
        file_path: str | Path,
        source_id: str,
        file_name: str | None = None,
    ) -> list[Document]:

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError("PDFLoader requires a .pdf file")

        reader = PdfReader(str(path))

        documents = []

        display_name = file_name or path.name

        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()

            if not text:
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source_id": source_id,
                        "source_type": "pdf",
                        "file_name": display_name,
                        "page": page_number,
                    },
                )
            )

        return documents