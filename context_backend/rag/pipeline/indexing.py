"""Index YouTube transcripts and uploaded files into the vector store."""

from pathlib import Path
from uuid import uuid4

from rag.chunking.chunker import TranscriptChunker
from rag.config import settings
from rag.embeddings.embedder import EmbeddingModel
from rag.ingestion.cleaner import TranscriptCleaner
from rag.ingestion.transcript_loader import TranscriptLoader
from rag.ingestion.pdf_loader import PDFLoader
from rag.ingestion.docx_loader import DOCXLoader
from rag.ingestion.text_loader import TextFileLoader
from rag.vectorstore.chroma_store import ChromaVectorStore


class IndexingPipeline:
    def __init__(
        self,
        loader=None,
        cleaner=None,
        chunker=None,
        embedding_model=None,
        vector_store=None,
        persist_directory=None,
        collection_name: str = "youtube_transcripts",
    ):
        self.loader = loader or TranscriptLoader()
        self.cleaner = cleaner or TranscriptCleaner()
        self.chunker = chunker or TranscriptChunker()

        self.embedding_model = embedding_model
        self.vector_store = vector_store

        if self.vector_store is None:
            self.embedding_model = self.embedding_model or EmbeddingModel(
                model_name=settings.embedding_model,
            )
            self.vector_store = ChromaVectorStore(
                embedding_function=self.embedding_model.get_model(),
                persist_directory=persist_directory or settings.chroma_path,
                collection_name=collection_name,
            )

    def index_video(self, video_url: str) -> dict:
        transcript = self.loader.load(video_url)

        video_id = transcript["video_id"]
        raw_snippets = transcript.get("snippets", [])

        cleaned_snippets = self.cleaner.clean(raw_snippets)

        chunks = self.chunker.split(
            cleaned_snippets,
            video_id=video_id,
        )

        source = transcript.get("source", video_url)
        video_title = transcript.get("title") or transcript.get("video_title")

        source_id = transcript.get("source_id") or str(uuid4())

        for chunk in chunks:
            chunk.metadata["video_id"] = video_id
            chunk.metadata["source"] = source
            chunk.metadata["source_id"] = source_id
            chunk.metadata["source_type"] = "youtube"

            if video_title:
                chunk.metadata["video_title"] = video_title

        assert self.vector_store is not None
        indexed_chunk_ids = self.vector_store.add_documents(chunks)

        return {
            "source_id": source_id,
            "source_type": "youtube",
            "video_id": video_id,
            "video_title": video_title,
            "source": source,
            "transcript_snippet_count": len(raw_snippets),
            "cleaned_snippet_count": len(cleaned_snippets),
            "chunk_count": len(chunks),
            "indexed_chunk_ids": indexed_chunk_ids,
        }

    def index_file(
        self,
        file_path: str | Path,
        source_type: str | None = None,
        original_filename: str | None = None,
    ) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        extension = path.suffix.lower()

        loader_map = {
            ".pdf": PDFLoader(),
            ".docx": DOCXLoader(),
            ".txt": TextFileLoader(),
            ".md": TextFileLoader(),
        }

        if extension not in loader_map:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                "Supported types: .pdf, .docx, .txt, .md"
            )

        source_id = str(uuid4())

        loader = loader_map[extension]

        documents = loader.load(
            path,
            source_id=source_id,
            file_name=original_filename or path.name,
        )

        if not documents:
            return {
                "source_id": source_id,
                "source_type": source_type or self._source_type(extension),
                "title": original_filename or path.name,
                "source": original_filename or path.name,
                "file_name": original_filename or path.name,
                "chunk_count": 0,
                "indexed_chunk_ids": [],
                "status": "indexed",
            }

        chunks = self._chunk_documents(
            documents,
            source_id=source_id,
        )

        assert self.vector_store is not None
        indexed_chunk_ids = self.vector_store.add_documents(chunks)

        resolved_source_type = (
            source_type or self._source_type(extension)
        )

        return {
            "source_id": source_id,
            "source_type": resolved_source_type,
            "title": original_filename or path.name,
            "source": original_filename or path.name,
            "file_name": original_filename or path.name,
            "chunk_count": len(chunks),
            "indexed_chunk_ids": indexed_chunk_ids,
            "status": "indexed",
        }

    def _chunk_documents(
        self,
        documents,
        source_id: str,
    ):
        chunks = []

        for document in documents:
            metadata = dict(document.metadata)

            text = document.page_content

            # Reuse the existing chunker while preserving
            # file-specific metadata.
            split_documents = self.chunker.split(
                [
                    {
                        "text": text,
                        "start": metadata.get("start", 0),
                        "end": metadata.get(
                            "end",
                            metadata.get("end_time", 0),
                        ),
                        **metadata,
                    }
                ],
                video_id=source_id,
            )

            for chunk in split_documents:
                chunk.metadata.update(metadata)
                chunk.metadata["source_id"] = source_id

                chunk.metadata["chunk_id"] = f"{source_id}:{len(chunks)}"

                chunks.append(chunk)

        return chunks

    @staticmethod
    def _source_type(extension: str) -> str:
        return {
            ".pdf": "pdf",
            ".docx": "docx",
            ".txt": "txt",
            ".md": "markdown",
        }[extension]


def index_transcript(transcript: str) -> list[str]:
    """Deprecated compatibility shim for older tests/imports."""
    return [transcript]