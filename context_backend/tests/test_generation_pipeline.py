import os
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from langchain_core.documents import Document

from rag.generation.llm import GeminiLLM, LLMGenerationError
from rag.generation.prompt import RAGPrompt
from rag.pipeline.generation import GenerationPipeline


class FakeLLM:
    def __init__(self, answer):
        self.answer = answer
        self.prompts = []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return self.answer


def test_gemini_provider_successful_generation():
    response = SimpleNamespace(text="  RAG retrieves context before generation.  ")
    client = Mock()
    client.models.generate_content.return_value = response
    llm = GeminiLLM(
        api_key="test-key",
        model_name="test-model",
        temperature=0.1,
        max_output_tokens=64,
        client=client,
    )

    answer = llm.generate("Grounded prompt")

    assert answer == "RAG retrieves context before generation."
    client.models.generate_content.assert_called_once()
    call = client.models.generate_content.call_args
    assert call.kwargs["model"] == "test-model"
    assert call.kwargs["contents"] == "Grounded prompt"


def test_gemini_provider_handles_empty_response():
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(text="   ")
    llm = GeminiLLM(api_key="test-key", client=client)

    with pytest.raises(LLMGenerationError, match="empty response"):
        llm.generate("Prompt")


def test_gemini_provider_wraps_api_failure():
    client = Mock()
    client.models.generate_content.side_effect = RuntimeError("sdk failure")
    llm = GeminiLLM(api_key="test-key", client=client)

    with pytest.raises(LLMGenerationError, match="request failed"):
        llm.generate("Prompt")


def test_gemini_provider_requires_api_key_without_injected_client():
    with pytest.raises(LLMGenerationError, match="GEMINI_API_KEY"):
        GeminiLLM(api_key="")


def test_gemini_provider_uses_model_configuration():
    client = Mock()
    client.models.generate_content.return_value = SimpleNamespace(text="Configured")
    llm = GeminiLLM(
        api_key="test-key",
        model_name="gemini-test-model",
        temperature=0.5,
        max_output_tokens=12,
        client=client,
    )

    assert llm.model_name == "gemini-test-model"
    assert llm.temperature == 0.5
    assert llm.max_output_tokens == 12
    assert llm.generate("Prompt") == "Configured"


def test_prompt_integration_keeps_question_context_and_grounding():
    prompt = RAGPrompt().get_prompt()
    messages = prompt.invoke(
        {
            "question": "What is RAG?",
            "context": "[SOURCE 1]\nTimestamp: 02:00 - 02:15\nRAG context",
        }
    ).to_messages()
    rendered = "\n".join(str(message.content) for message in messages)

    assert "What is RAG?" in rendered
    assert "RAG context" in rendered
    assert "Use only the supplied lecture context" in rendered
    assert "Do not invent information" in rendered
    assert "not supported by the context" in rendered


def test_generation_pipeline_returns_answer_and_sources():
    document = Document(
        page_content="RAG retrieves relevant external information before generation.",
        metadata={
            "video_id": "test123",
            "video_title": "RAG Lecture",
            "start_time": 120,
            "end_time": 135,
            "source": "https://youtu.be/test123",
            "chunk_id": "test123:0",
        },
    )
    llm = FakeLLM("RAG retrieves relevant external information before generation.")
    pipeline = GenerationPipeline(llm=llm)

    result = pipeline.generate("What is RAG?", [document])

    assert result["answer"] == (
        "RAG retrieves relevant external information before generation."
    )
    assert result["sources"] == [
        {
            "source_number": 1,
            "video_id": "test123",
            "video_title": "RAG Lecture",
            "start_time": 120,
            "end_time": 135,
            "source": "https://youtu.be/test123",
            "chunk_id": "test123:0",
        }
    ]
    assert "What is RAG?" in llm.prompts[0]
    assert "RAG retrieves relevant external information before generation." in (
        llm.prompts[0]
    )
    assert "Timestamp: 02:00 - 02:15" in llm.prompts[0]


@pytest.mark.skipif(
    os.getenv("RUN_GEMINI_INTEGRATION") != "1"
    or not os.getenv("GEMINI_API_KEY"),
    reason="Set RUN_GEMINI_INTEGRATION=1 and GEMINI_API_KEY to run Gemini integration",
)
def test_real_gemini_generation_integration():
    llm = GeminiLLM(max_output_tokens=32)

    answer = llm.generate(
        "Answer with exactly one short sentence: What does RAG stand for?"
    )

    assert answer
    assert isinstance(answer, str)
