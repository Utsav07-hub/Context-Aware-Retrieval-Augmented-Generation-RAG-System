from langchain_chroma import Chroma
from langchain_core.documents import Document

class ChromaVectorStore:

    def __init__(
        self,
        embedding_function,
        persist_directory="vectorstore/chroma",
        collection_name="youtube_transcripts",
    ):

        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=persist_directory,
        )

    def add_documents(self, documents):
        if not documents:
            return []

        document_ids = [
            document.metadata.get("chunk_id")
            for document in documents
        ]

        ids = self.vectorstore.add_documents(
            documents,
            ids=document_ids if all(document_ids) else None,
        )

        return ids

    def similarity_search(self, query, k=5):
        if not query.strip():
            return []

        return self.vectorstore.similarity_search(
            query,
            k=k,
        )

    def get_retriever(
        self,
        search_type="similarity",
        k=5,
        fetch_k=20,
        source_id=None,
    ):
        search_kwargs: dict[str, object] = {
            "k": k,
        }

        if search_type == "mmr":
            search_kwargs["fetch_k"] = max(fetch_k, k)

        if source_id is not None:
            search_kwargs["filter"] = {
                "source_id": source_id,
            }

        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs,
        )
    def get_documents_by_source(self, source_id: str) -> list[Document]:
        result = self.vectorstore.get(
            where={"source_id": source_id}
        )

        documents = []

        for content, metadata in zip(
            result.get("documents", []),
            result.get("metadatas", []),
        ):
            documents.append(
                Document(
                    page_content=content,
                    metadata=metadata or {},
                )
            )

        return documents
    def list_sources(self) -> list[dict]:
        result = self.vectorstore.get()
        metadatas = result.get("metadatas", []) or []

        sources = {}

        for metadata in metadatas:
            if not metadata:
                continue

            source_id = metadata.get("source_id")

            if not source_id:
                continue

            if source_id not in sources:
                sources[source_id] = {
                    "source_id": source_id,
                    "source_type": metadata.get("source_type"),
                    "title": metadata.get("video_title") or metadata.get("title"),
                    "source": metadata.get("source"),
                    "video_id": metadata.get("video_id"),
                    "chunk_count": 0,
                }

            sources[source_id]["chunk_count"] += 1

        return list(sources.values())
