import math
import re
from collections import Counter

from langchain_core.documents import Document


class BM25Retriever:
    def __init__(
        self,
        documents: list[Document],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        self.documents = documents 
        
        self.k1 = k1
        self.b = b
        self.document_tokens = [
            self._tokenize(document.page_content)
            for document in documents
        ]
        self.document_lengths = [
            len(tokens)
            for tokens in self.document_tokens
        ]
        self.average_length = (
            sum(self.document_lengths) / len(self.document_lengths)
            if self.document_lengths
            else 0.0
        )
        self.document_frequencies = self._document_frequencies()

    def retrieve(
        self, query: str, k: int = 5, source_id: str | None = None
    ) -> list[Document]:
        query_tokens = self._tokenize(query)

        if not query_tokens or not self.documents:
            return []

        document_indices = [
            index
            for index, document in enumerate(self.documents)
            if source_id is None
            or document.metadata.get("source_id") == source_id
        ]

        scored = [
            (
                self.documents[index],
                self._score(query_tokens, index),
            )
            for index in document_indices
        ]

        scored = [
            item
            for item in scored
            if item[1] > 0
        ]

        scored.sort(
            key=lambda item: (
                -item[1],
                self.documents.index(item[0]),
            )
        )

        return [document for document, _score in scored[:k]]

    def _score(self, query_tokens: list[str], document_index: int) -> float:
        tokens = self.document_tokens[document_index]
        term_counts = Counter(tokens)
        doc_length = self.document_lengths[document_index]
        score = 0.0

        for token in query_tokens:
            frequency = term_counts[token]
            if frequency == 0:
                continue

            idf = self._idf(token)
            denominator = frequency + self.k1 * (
                1 - self.b + self.b * doc_length / (self.average_length or 1)
            )
            score += idf * (frequency * (self.k1 + 1)) / denominator

        return score

    def _document_frequencies(self) -> dict[str, int]:
        frequencies: dict[str, int] = {}

        for tokens in self.document_tokens:
            for token in set(tokens):
                frequencies[token] = frequencies.get(token, 0) + 1

        return frequencies

    def _idf(self, token: str) -> float:
        document_count = len(self.documents)
        frequency = self.document_frequencies.get(token, 0)
        return math.log(1 + (document_count - frequency + 0.5) / (frequency + 0.5))

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\b\w+\b", text.lower())
