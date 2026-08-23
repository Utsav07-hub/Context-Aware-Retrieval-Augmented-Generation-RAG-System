import os

from dotenv import load_dotenv
from langchain_core.documents import Document

from rag.chunking.chunker import TranscriptChunker
from rag.generation.llm import GeminiLLM
from rag.pipeline.generation import GenerationPipeline

load_dotenv()


def main():
    # --------------------------------------------------
    # 1. Synthetic YouTube transcript
    # --------------------------------------------------

    transcript = [
        {
            "text": (
                "Retrieval Augmented Generation, or RAG, "
                "combines information retrieval with text generation."
            ),
            "start": 0,
            "duration": 12,
        },
        {
            "text": (
                "RAG first retrieves relevant information from "
                "an external knowledge source before asking the "
                "language model to generate an answer."
            ),
            "start": 12,
            "duration": 15,
        },
        {
            "text": (
                "Embeddings represent text as numerical vectors. "
                "These vectors allow semantically similar information "
                "to be retrieved from a vector database."
            ),
            "start": 27,
            "duration": 18,
        },
        {
            "text": (
                "RAG is especially useful when information changes "
                "frequently because the knowledge source can be "
                "updated without retraining the language model."
            ),
            "start": 45,
            "duration": 20,
        },
    ]

    # --------------------------------------------------
    # 2. Convert transcript into Documents
    # --------------------------------------------------

    documents = []

    for i, item in enumerate(transcript):

        documents.append(
            Document(
                page_content=item["text"],
                metadata={
                    "video_id": "synthetic-rag-video",
                    "video_title": "Synthetic RAG Lecture",
                    "source": "synthetic",
                    "start_time": item["start"],
                    "end_time": item["start"] + item["duration"],
                    "chunk_id": f"synthetic-rag-video:{i}",
                },
            )
        )

    print("\n=== TRANSCRIPT ===")
    print(f"Transcript snippets: {len(documents)}")

    # --------------------------------------------------
    # 3. Create chunks
    # --------------------------------------------------

    # We already have small transcript snippets,
    # so for this validation we use them directly.
    chunks = documents

    print(f"Chunks: {len(chunks)}")

    # --------------------------------------------------
    # 4. Show retrieved-context simulation
    #
    # IMPORTANT:
    # We are NOT testing retrieval implementation here.
    # Retrieval was already validated by your 28+ tests.
    #
    # We are testing the connection:
    # retrieved docs -> context -> Gemini
    # --------------------------------------------------

    relevant_documents = [
        chunks[1],
        chunks[3],
    ]

    print(f"Retrieved documents: {len(relevant_documents)}")

    # --------------------------------------------------
    # 5. Real Gemini
    # --------------------------------------------------

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError(
            "GEMINI_API_KEY is not available"
        )

    llm = GeminiLLM(
        max_output_tokens=128
    )

    # --------------------------------------------------
    # 6. Generation pipeline
    # --------------------------------------------------

    pipeline = GenerationPipeline(
        llm=llm
    )

    question = (
        "Why is RAG useful when information changes frequently?"
    )

    result = pipeline.generate(
        question,
        relevant_documents
    )

    # --------------------------------------------------
    # 7. Display result
    # --------------------------------------------------

    print("\n=== QUESTION ===")
    print(question)

    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== SOURCES ===")

    for source in result["sources"]:

        print(
            f"Source {source['source_number']}: "
            f"{source['start_time']}s - "
            f"{source['end_time']}s"
        )

    # --------------------------------------------------
    # 8. Basic validation
    # --------------------------------------------------

    assert result["answer"]

    assert len(result["sources"]) == 2

    assert result["sources"][0]["video_id"] == (
        "synthetic-rag-video"
    )

    assert result["sources"][1]["video_id"] == (
        "synthetic-rag-video"
    )

    assert (
        result["sources"][0]["start_time"]
        < result["sources"][0]["end_time"]
    )

    assert (
        result["sources"][1]["start_time"]
        < result["sources"][1]["end_time"]
    )

    print("\n=== RESULT ===")
    print("REAL GEMINI + RAG GENERATION TEST PASSED")


if __name__ == "__main__":
    main()