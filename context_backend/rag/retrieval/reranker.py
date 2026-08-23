from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        query: str,
        documents: list,
        top_k: int = 5,
    ):

        if not documents:
            return []

        pairs = [
            [query, document.page_content]
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, scores),
            key=lambda item: item[1],
            reverse=True,
        )

        results = []

        for document, score in ranked[:top_k]:

            document.metadata["reranker_score"] = float(score)

            results.append(document)

        return results