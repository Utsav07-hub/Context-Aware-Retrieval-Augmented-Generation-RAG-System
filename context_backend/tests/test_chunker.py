from rag.chunking.chunker import TranscriptChunker


def test_transcript_chunking():

    snippets = [
        {
            "text": "RAG is Retrieval Augmented Generation.",
            "start": 0.0,
            "duration": 5.0,
            "end": 5.0,
        },
        {
            "text": "It combines retrieval with generation.",
            "start": 5.0,
            "duration": 5.0,
            "end": 10.0,
        },
        {
            "text": "The retrieved information is given to the language model.",
            "start": 10.0,
            "duration": 6.0,
            "end": 16.0,
        },
    ]

    chunker = TranscriptChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.split(
        snippets,
        video_id="test_video"
    )

    assert len(chunks) > 0

    for chunk in chunks:

        assert chunk.page_content

        assert chunk.metadata["video_id"] == "test_video"

        assert "start_time" in chunk.metadata
        assert "end_time" in chunk.metadata