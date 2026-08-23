import re
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from rag.chunking.chunker import TranscriptChunker
from rag.embeddings.embedder import EmbeddingModel
from rag.generation.context_builder import ContextBuilder
from rag.generation.prompt import RAGPrompt
from rag.ingestion.cleaner import TranscriptCleaner
from rag.ingestion.transcript_loader import TranscriptLoader
from rag.pipeline.indexing import index_transcript
from rag.retrieval.bm25_retriever import BM25Retriever
from rag.retrieval.compressor import ContextCompressor
from rag.retrieval.fusion import ReciprocalRankFusion
from rag.retrieval.hybrid_retriever import HybridRetriever
from rag.retrieval.reranker import Reranker
from rag.retrieval.retrieval_pipeline import RetrievalPipeline
from rag.vectorstore.chroma_store import ChromaVectorStore


class FakeEmbeddings:
    def embed_documents(self, texts):
        return [self._embed(text) for text in texts]

    def embed_query(self, text):
        return self._embed(text)

    def _embed(self, text):
        terms = text.lower().split()
        return [
            float(terms.count("rag")),
            float(terms.count("embeddings") + terms.count("vectors")),
            float(terms.count("database") + terms.count("databases")),
            float(len(text) % 10),
        ]


class FakeVectorRetriever:
    def __init__(self, documents):
        self.documents = documents

    def retrieve(self, query):
        query_terms = set(tokenize(query))
        return sorted(
            self.documents,
            key=lambda document: len(
                query_terms.intersection(tokenize(document.page_content))
            ),
            reverse=True,
        )


class FakeRankerModel:
    def predict(self, pairs):
        scores = []
        for query, content in pairs:
            query_terms = set(tokenize(query))
            scores.append(
                float(len(query_terms.intersection(tokenize(content))))
            )
        return scores


class FakeCompressorBackend:
    def __init__(self):
        self.query = None

    def compress_documents(self, documents, query):
        self.query = query
        return [
            Document(
                page_content=document.page_content[:80],
                metadata=dict(document.metadata),
            )
            for document in documents
        ]


def docs():
    return [
        Document(
            page_content="RAG stands for Retrieval Augmented Generation.",
            metadata={
                "video_id": "test123",
                "start_time": 120,
                "end_time": 135,
                "chunk_id": "test123:0",
            },
        ),
        Document(
            page_content="Embeddings convert text into vectors.",
            metadata={
                "video_id": "test123",
                "start_time": 136,
                "end_time": 145,
                "chunk_id": "test123:1",
            },
        ),
        Document(
            page_content="Vector databases store embeddings.",
            metadata={
                "video_id": "test123",
                "start_time": 146,
                "end_time": 155,
                "chunk_id": "test123:2",
            },
        ),
    ]


def tokenize(text):
    return re.findall(r"\b\w+\b", text.lower())


def test_transcript_loader_extracts_valid_youtube_ids():
    loader = TranscriptLoader()

    assert (
        loader.extract_video_id("https://www.youtube.com/watch?v=VIDEO_ID")
        == "VIDEO_ID"
    )
    assert loader.extract_video_id("https://youtu.be/VIDEO_ID") == "VIDEO_ID"


def test_transcript_loader_rejects_invalid_urls():
    loader = TranscriptLoader()

    with pytest.raises(ValueError, match="Invalid YouTube URL"):
        loader.extract_video_id("https://example.com/watch?v=VIDEO_ID")

    with pytest.raises(ValueError, match="Invalid YouTube URL"):
        loader.extract_video_id("https://www.youtube.com/watch")


def test_transcript_loader_uses_transcript_api_without_network(monkeypatch):
    transcript = Mock(
        language="English",
        language_code="en",
        is_generated=False,
    )
    transcript.to_raw_data.return_value = [
        {"text": "RAG", "start": 0.0, "duration": 1.0}
    ]
    api = Mock()
    api.fetch.return_value = transcript
    monkeypatch.setattr(
        "rag.ingestion.transcript_loader.YouTubeTranscriptApi",
        Mock(return_value=api),
    )

    result = TranscriptLoader(languages=["en"]).load(
        "https://www.youtube.com/watch?v=abc123"
    )

    api.fetch.assert_called_once_with("abc123", languages=["en"])
    assert result["video_id"] == "abc123"
    assert result["snippets"][0]["text"] == "RAG"


def test_transcript_cleaning_preserves_timestamps_and_meaning():
    cleaner = TranscriptCleaner()
    cleaned = cleaner.clean(
        [
            {
                "text": "   RAG    is retrieval   augmented generation.   ",
                "start": 12.0,
                "duration": 3.5,
            },
            {"text": "   ", "start": 20.0, "duration": 1.0},
        ]
    )

    assert cleaned == [
        {
            "text": "RAG is retrieval augmented generation.",
            "start": 12.0,
            "duration": 3.5,
            "end": 15.5,
        }
    ]


def test_chunker_preserves_source_metadata_and_handles_empty_text():
    chunker = TranscriptChunker(chunk_size=30, chunk_overlap=10)
    chunks = chunker.split(
        [
            {
                "text": "RAG retrieves context. RAG answers with context.",
                "start": 1.0,
                "duration": 5.0,
                "end": 6.0,
            },
            {"text": "", "start": 6.0, "duration": 1.0, "end": 7.0},
        ],
        video_id="video42",
    )

    assert chunks
    assert all(len(chunk.page_content) <= 30 for chunk in chunks)
    assert all(chunk.metadata["video_id"] == "video42" for chunk in chunks)
    assert all(chunk.metadata["start_time"] == 1.0 for chunk in chunks)
    assert all(chunk.metadata["end_time"] == 6.0 for chunk in chunks)
    assert all(chunk.metadata["chunk_id"].startswith("video42:") for chunk in chunks)


def test_embedding_model_wraps_consistent_huggingface_model(monkeypatch):
    fake_model = Mock()
    factory = Mock(return_value=fake_model)
    monkeypatch.setattr("rag.embeddings.embedder.HuggingFaceEmbeddings", factory)

    model = EmbeddingModel(model_name="local-test-model")

    factory.assert_called_once_with(model_name="local-test-model")
    assert model.get_model() is fake_model


def test_fake_embeddings_return_numerical_vectors_and_handle_empty_input():
    embeddings = FakeEmbeddings()

    assert embeddings.embed_documents([]) == []
    vector = embeddings.embed_query("RAG embeddings")
    assert vector
    assert all(isinstance(value, float) for value in vector)
    assert embeddings.embed_query("RAG") == embeddings.embed_query("RAG")


def test_chroma_vector_store_insert_retrieve_persist_and_similarity(tmp_path):
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="test_collection",
    )
    document_ids = store.add_documents(docs())

    assert document_ids == ["test123:0", "test123:1", "test123:2"]
    results = store.similarity_search("What is RAG?", k=1)
    assert len(results) == 1
    assert results[0].metadata["video_id"] == "test123"

    reloaded = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="test_collection",
    )
    persisted = reloaded.similarity_search("What is RAG?", k=1)

    assert persisted[0].page_content == results[0].page_content


def test_duplicate_chroma_indexing_uses_stable_chunk_ids(tmp_path):
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="duplicates",
    )

    store.add_documents(docs())
    store.add_documents(docs())

    assert store.vectorstore._collection.count() == 3


def test_basic_and_mmr_retrieval_modes(tmp_path):
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="retrieval_modes",
    )
    store.add_documents(docs())

    similarity = store.get_retriever(search_type="similarity", k=2).invoke("RAG")
    mmr = store.get_retriever(search_type="mmr", k=2, fetch_k=3).invoke("RAG")

    assert len(similarity) == 2
    assert len(mmr) == 2
    assert all(isinstance(document, Document) for document in similarity + mmr)
    assert all(document.metadata["video_id"] == "test123" for document in similarity + mmr)
    assert store.similarity_search("", k=2) == []


def test_bm25_retrieves_exact_terms_case_insensitively():
    retriever = BM25Retriever(
        [
            Document(page_content="MMR diversifies retrieved chunks."),
            Document(page_content="RAG retrieves context."),
        ]
    )

    assert retriever.retrieve("mmr", k=1)[0].page_content.startswith("MMR")
    assert retriever.retrieve("", k=5) == []
    assert BM25Retriever([]).retrieve("MMR") == []


def test_rrf_fusion_merges_duplicates_and_is_deterministic():
    a = Document(page_content="A", metadata={"chunk_id": "A"})
    b = Document(page_content="B", metadata={"chunk_id": "B"})
    c = Document(page_content="C", metadata={"chunk_id": "C"})
    d = Document(page_content="D", metadata={"chunk_id": "D"})
    e = Document(page_content="E", metadata={"chunk_id": "E"})
    fusion = ReciprocalRankFusion()

    first = fusion.fuse([[a, b, c, d], [c, a, e, b]], top_k=3)
    second = fusion.fuse([[a, b, c, d], [c, a, e, b]], top_k=3)

    assert [document.page_content for document in first] == ["A", "C", "B"]
    assert [document.page_content for document in first] == [
        document.page_content for document in second
    ]
    assert fusion.fuse([[], []]) == []


def test_hybrid_retrieval_combines_vector_and_keyword_results():
    source_docs = docs()
    hybrid = HybridRetriever(
        documents=source_docs,
        k=3,
        vector_retriever=FakeVectorRetriever(source_docs[:2]),
    )

    results = hybrid.retrieve("Vector databases")

    assert any("RAG stands" in document.page_content for document in results)
    assert any("Vector databases" in document.page_content for document in results)
    assert len({document.metadata["chunk_id"] for document in results}) == len(results)
    assert all(document.metadata["video_id"] == "test123" for document in results)


def test_reranker_reorders_candidates_and_stores_scores(monkeypatch):
    monkeypatch.setattr(
        "rag.retrieval.reranker.CrossEncoder",
        Mock(return_value=FakeRankerModel()),
    )
    reranker = Reranker(model_name="fake")
    candidates = [
        Document(page_content="Unrelated text", metadata={}),
        Document(page_content="RAG retrieves context", metadata={}),
    ]

    results = reranker.rerank("RAG context", candidates, top_k=1)

    assert results[0].page_content == "RAG retrieves context"
    assert isinstance(results[0].metadata["reranker_score"], float)
    assert reranker.rerank("RAG", [], top_k=5) == []
    assert len(reranker.rerank("RAG", [candidates[1]], top_k=5)) == 1


def test_contextual_compression_preserves_metadata_and_query():
    backend = FakeCompressorBackend()
    compressor = ContextCompressor(compressor=backend)

    results = compressor.compress("What is RAG?", docs())

    assert backend.query == "What is RAG?"
    assert all(len(document.page_content) <= 80 for document in results)
    assert all(document.metadata["video_id"] == "test123" for document in results)
    assert all("start_time" in document.metadata for document in results)
    assert compressor.compress("anything", []) == []


def test_context_builder_formats_sources_timestamps_and_limits_chars():
    context = ContextBuilder(max_chars=500).build(docs()[:2])

    assert "[SOURCE 1]" in context
    assert "[SOURCE 2]" in context
    assert "Timestamp: 02:00 - 02:15" in context
    assert context.index("[SOURCE 1]") < context.index("[SOURCE 2]")
    assert ContextBuilder().build([]) == ""

    missing = ContextBuilder().build([Document(page_content="No metadata")])
    assert "Video ID: unknown" in missing
    assert "Timestamp: 00:00 - 00:00" in missing

    limited = ContextBuilder(max_chars=10).build(docs())
    assert limited == ""


def test_context_builder_formats_requested_youtube_timestamp():
    document = Document(
        page_content="Timestamp check",
        metadata={"video_id": "abc123", "start_time": 754, "end_time": 801},
    )

    context = ContextBuilder().build([document])

    assert "Timestamp: 12:34 - 13:21" in context


def test_prompt_template_inserts_context_question_and_instructions():
    prompt = RAGPrompt().get_prompt()
    messages = prompt.invoke(
        {
            "context": "[SOURCE 1]\nTimestamp: 00:00 - 00:05\nRAG info",
            "question": "What is RAG?",
        }
    ).to_messages()
    rendered = "\n".join(message.content for message in messages)

    assert "RAG info" in rendered
    assert "What is RAG?" in rendered
    assert "Use only the supplied lecture context" in rendered
    assert "Do not invent information" in rendered
    assert "timestamp" in rendered.lower()


def test_indexing_placeholder_does_not_destroy_input():
    assert index_transcript("raw transcript") == ["raw transcript"]


def test_retrieval_pipeline_preserves_metadata_through_rerank_and_compression():
    backend = FakeCompressorBackend()
    pipeline = RetrievalPipeline(
        documents=docs(),
        retriever=Mock(retrieve=Mock(return_value=docs())),
        reranker=Mock(rerank=Mock(return_value=docs()[:2])),
        compressor=ContextCompressor(compressor=backend),
        final_k=2,
    )

    results = pipeline.retrieve("What is RAG?")

    assert len(results) == 2
    assert all(document.page_content for document in results)
    assert all(document.metadata["video_id"] == "test123" for document in results)
    assert all("start_time" in document.metadata for document in results)
    assert all("end_time" in document.metadata for document in results)


def test_non_llm_end_to_end_rag_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rag.retrieval.reranker.CrossEncoder",
        Mock(return_value=FakeRankerModel()),
    )
    snippets = [
        {"text": "RAG stands for Retrieval Augmented Generation.", "start": 0, "duration": 5},
        {"text": "RAG retrieves relevant external information.", "start": 5, "duration": 5},
        {"text": "Embeddings convert text into vectors.", "start": 10, "duration": 5},
        {"text": "Vector databases store embeddings.", "start": 15, "duration": 5},
    ]
    cleaned = TranscriptCleaner().clean(snippets)
    chunks = TranscriptChunker(chunk_size=80, chunk_overlap=10).split(
        cleaned,
        video_id="test123",
    )
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="e2e",
    )
    store.add_documents(chunks)
    vector_results = store.similarity_search("What is RAG?", k=4)
    hybrid = HybridRetriever(
        documents=chunks,
        k=4,
        vector_retriever=FakeVectorRetriever(vector_results),
    )
    retrieved = hybrid.retrieve("What is RAG?")
    reranked = Reranker(model_name="fake").rerank(
        "What is RAG?",
        retrieved,
        top_k=3,
    )
    compressed = ContextCompressor(compressor=FakeCompressorBackend()).compress(
        "What is RAG?",
        reranked,
    )
    context = ContextBuilder().build(compressed)
    prompt = RAGPrompt().get_prompt().invoke(
        {"context": context, "question": "What is RAG?"}
    )
    rendered = "\n".join(message.content for message in prompt.to_messages())

    assert "RAG stands for Retrieval Augmented Generation" in rendered
    assert "Video ID: test123" in rendered
    assert "[SOURCE 1]" in rendered
    assert "What is RAG?" in rendered


def test_metadata_preservation_end_to_end(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "rag.retrieval.reranker.CrossEncoder",
        Mock(return_value=FakeRankerModel()),
    )
    cleaned = TranscriptCleaner().clean(
        [
            {
                "text": "RAG retrieves relevant context.",
                "start": 120,
                "duration": 15,
            }
        ]
    )
    chunks = TranscriptChunker(chunk_size=80, chunk_overlap=5).split(
        cleaned,
        video_id="test123",
    )
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="metadata",
    )
    store.add_documents(chunks)
    retrieved = store.similarity_search("RAG", k=1)
    reranked = Reranker(model_name="fake").rerank("RAG", retrieved, top_k=1)
    compressed = ContextCompressor(compressor=FakeCompressorBackend()).compress(
        "RAG",
        reranked,
    )
    context = ContextBuilder().build(compressed)

    assert compressed[0].metadata["video_id"] == "test123"
    assert compressed[0].metadata["start_time"] == 120
    assert compressed[0].metadata["end_time"] == 135
    assert "Video ID: test123" in context
    assert "Timestamp: 02:00 - 02:15" in context
