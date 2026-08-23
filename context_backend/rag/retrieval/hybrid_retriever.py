from rag.retrieval.bm25_retriever import BM25Retriever
from rag.retrieval.retriever import YouTubeRetriever
from .fusion import ReciprocalRankFusion


class HybridRetriever:

    def __init__(
        self,
        documents,
        k=5,
        fetch_k=20,
        vector_retriever=None,
        source_id: str | None = None,
    ):
        self.source_id = source_id

        self.vector_retriever = (
            vector_retriever
            if vector_retriever is not None
            else YouTubeRetriever(
                k=k,
                fetch_k=fetch_k,
                source_id=source_id,
            )
        )

        self.keyword_retriever = BM25Retriever(
            documents
        )

        self.fusion = ReciprocalRankFusion()

        self.k = k

    def retrieve(self, query):

        vector_results = (
            self.vector_retriever.retrieve(query)
        )

        keyword_results = (
            self.keyword_retriever.retrieve(
                query,
                k=self.k,
                source_id=self.source_id,
            )
        )

        return self.fusion.fuse(
            [
                vector_results,
                keyword_results,
            ],
            top_k=self.k,
        )