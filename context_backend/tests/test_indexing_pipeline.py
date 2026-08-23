from rag.pipeline.indexing import IndexingPipeline
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
            float(terms.count("embeddings")),
            float(len(text) % 10),
        ]


class FakeLoader:
    def __init__(self, transcript):
        self.transcript = transcript
        self.loaded_urls = []

    def load(self, video_url):
        self.loaded_urls.append(video_url)
        return self.transcript


class RecordingVectorStore:
    def __init__(self):
        self.added_documents = []

    def add_documents(self, documents):
        self.added_documents.extend(documents)
        return [
            document.metadata["chunk_id"]
            for document in documents
        ]


def transcript(snippets=None):
    return {
        "video_id": "abc123",
        "title": "RAG Lecture",
        "language": "English",
        "language_code": "en",
        "is_generated": False,
        "snippets": snippets
        if snippets is not None
        else [
            {
                "text": " RAG stands for Retrieval Augmented Generation. ",
                "start": 120,
                "duration": 15,
            },
            {
                "text": "Embeddings convert text into vectors.",
                "start": 135,
                "duration": 10,
            },
        ],
    }


def test_index_video_with_mocked_transcript_returns_summary():
    loader = FakeLoader(transcript())
    vector_store = RecordingVectorStore()
    pipeline = IndexingPipeline(
        loader=loader,
        vector_store=vector_store,
    )

    summary = pipeline.index_video("https://www.youtube.com/watch?v=abc123")

    assert loader.loaded_urls == ["https://www.youtube.com/watch?v=abc123"]
    assert summary["video_id"] == "abc123"
    assert summary["video_title"] == "RAG Lecture"
    assert summary["source"] == "https://www.youtube.com/watch?v=abc123"
    assert summary["transcript_snippet_count"] == 2
    assert summary["cleaned_snippet_count"] == 2
    assert summary["chunk_count"] == 2
    assert summary["indexed_chunk_ids"] == ["abc123:0", "abc123:1"]
    assert summary["source_id"]
    assert summary["source_type"] == "youtube"


def test_index_video_handles_empty_transcript():
    vector_store = RecordingVectorStore()
    pipeline = IndexingPipeline(
        loader=FakeLoader(transcript(snippets=[])),
        vector_store=vector_store,
    )

    summary = pipeline.index_video("https://youtu.be/abc123")

    assert vector_store.added_documents == []
    assert summary["transcript_snippet_count"] == 0
    assert summary["cleaned_snippet_count"] == 0
    assert summary["chunk_count"] == 0
    assert summary["indexed_chunk_ids"] == []


def test_index_video_preserves_metadata_on_inserted_documents():
    vector_store = RecordingVectorStore()
    pipeline = IndexingPipeline(
        loader=FakeLoader(transcript()),
        vector_store=vector_store,
    )

    pipeline.index_video("https://youtu.be/abc123")

    assert vector_store.added_documents
    for index, document in enumerate(vector_store.added_documents):
        assert document.metadata["video_id"] == "abc123"
        assert document.metadata["video_title"] == "RAG Lecture"
        assert document.metadata["source"] == "https://youtu.be/abc123"
        assert document.metadata["chunk_id"] == f"abc123:{index}"
        assert "start_time" in document.metadata
        assert "end_time" in document.metadata


def test_index_video_inserts_documents_into_vector_store(tmp_path):
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="indexing_insert",
    )
    pipeline = IndexingPipeline(
        loader=FakeLoader(transcript()),
        vector_store=store,
    )

    summary = pipeline.index_video("https://youtu.be/abc123")
    results = store.similarity_search("What is RAG?", k=1)

    assert summary["chunk_count"] == 2
    assert results
    assert results[0].metadata["video_id"] == "abc123"
    assert results[0].metadata["source"] == "https://youtu.be/abc123"


def test_index_video_duplicate_indexing_uses_stable_chunk_ids(tmp_path):
    store = ChromaVectorStore(
        embedding_function=FakeEmbeddings(),
        persist_directory=str(tmp_path),
        collection_name="indexing_duplicates",
    )
    pipeline = IndexingPipeline(
        loader=FakeLoader(transcript()),
        vector_store=store,
    )

    first = pipeline.index_video("https://youtu.be/abc123")
    second = pipeline.index_video("https://youtu.be/abc123")

    assert first["indexed_chunk_ids"] == ["abc123:0", "abc123:1"]
    assert second["indexed_chunk_ids"] == ["abc123:0", "abc123:1"]
    assert store.vectorstore._collection.count() == 2
