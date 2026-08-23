from rag.embeddings.embedder import EmbeddingModel
from rag.vectorstore.chroma_store import ChromaVectorStore


class YouTubeRetriever:

    def __init__(
        self,
        k: int = 5,
        search_type: str = "similarity",
        fetch_k: int = 20,
        embedding_model=None,
        vector_store=None,
        source_id: str | None = None,
    ):
        self.embedding_model = embedding_model or EmbeddingModel()

        self.vector_store = vector_store or ChromaVectorStore(
            embedding_function=self.embedding_model.get_model()
        )

        self.retriever = self.vector_store.get_retriever(
            search_type=search_type,
            k=k,
            fetch_k=fetch_k,
            source_id=source_id,
        )

    def retrieve(self, query: str):
        return self.retriever.invoke(query)

    def get_retriever(
        self,
        search_type: str = "similarity",
        k: int = 5,
        fetch_k: int = 20,
        source_id: str | None = None,
    ):
        return self.vector_store.get_retriever(
            search_type=search_type,
            k=k,
            fetch_k=fetch_k,
            source_id=source_id,
        )