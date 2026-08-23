from rag.embeddings.embedder import EmbeddingModel
from rag.vectorstore.chroma_store import ChromaVectorStore
from rag.retrieval.retrieval_pipeline import RetrievalPipeline
from rag.pipeline.generation import GenerationPipeline
class RAGService:

    def __init__(self):
        self.embedding_model = EmbeddingModel()

        self.vector_store = ChromaVectorStore(
            embedding_function=self.embedding_model.get_model()
        )

        self.generation = GenerationPipeline()

    def answer(
        self,
        question: str,
        source_id: str,
    ) -> dict:

        documents = self.vector_store.get_documents_by_source(
            source_id
        )

        if not documents:
            raise ValueError(
                "No indexed documents found for this source."
            )

        retrieval = RetrievalPipeline(
            documents=documents,
            source_id=source_id,
        )

        relevant_documents = retrieval.retrieve(
            question
        )

        if not relevant_documents:
            raise ValueError(
                "No relevant context found for this question."
            )

        return self.generation.generate(
            question,
            relevant_documents,
        )