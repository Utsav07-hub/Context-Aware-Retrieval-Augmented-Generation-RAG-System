from langchain_core.documents import Document


class ReciprocalRankFusion:
    def __init__(self, rank_constant: int = 60):
        self.rank_constant = rank_constant

    def fuse(
        self,
        ranked_lists: list[list[Document]],
        top_k: int = 5,
    ) -> list[Document]:
        scores: dict[str, float] = {}
        documents: dict[str, Document] = {}
        first_seen: dict[str, int] = {}
        seen_counter = 0

        for results in ranked_lists:
            for rank, document in enumerate(results, start=1):
                document_id = self._document_id(document)

                if document_id not in documents:
                    documents[document_id] = document
                    first_seen[document_id] = seen_counter
                    seen_counter += 1

                scores[document_id] = scores.get(document_id, 0.0) + (
                    1.0 / (self.rank_constant + rank)
                )

        ranked_ids = sorted(
            scores,
            key=lambda document_id: (
                -scores[document_id],
                first_seen[document_id],
                document_id,
            ),
        )

        return [documents[document_id] for document_id in ranked_ids[:top_k]]

    @staticmethod
    def _document_id(document: Document) -> str:
        metadata = document.metadata or {}
        return (
            metadata.get("chunk_id")
            or "|".join(
                str(metadata.get(key, ""))
                for key in ("video_id", "start_time", "end_time")
            )
            or document.page_content
        )
