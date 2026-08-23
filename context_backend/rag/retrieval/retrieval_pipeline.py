from rag.retrieval.hybrid_retriever import HybridRetriever
from rag.retrieval.reranker import Reranker


class RetrievalPipeline:

    def __init__(
        self,
        documents,
        candidate_k: int = 20,
        final_k: int = 5,
        retriever=None,
        reranker=None,
        compressor=None,
        source_id: str | None = None,
    ):

        self.retriever = retriever or HybridRetriever(
            documents=documents,
            k=candidate_k,
            source_id=source_id,
        )

        self.reranker = reranker or Reranker()
        self.compressor = compressor

        self.final_k = final_k

    def retrieve(self, query: str):

        candidates = self.retriever.retrieve(query)

        results = self.reranker.rerank(
            query=query,
            documents=candidates,
            top_k=self.final_k,
        )

        if self.compressor is not None:
            results = self.compressor.compress(
                query,
                results,
            )

        return results
