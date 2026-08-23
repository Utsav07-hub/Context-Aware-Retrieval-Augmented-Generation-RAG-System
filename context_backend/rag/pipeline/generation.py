"""Generate grounded answers from retrieved documents."""

from rag.generation.context_builder import ContextBuilder
from rag.generation.llm import GeminiLLM
from rag.generation.prompt import RAGPrompt


class GenerationPipeline:
    def __init__(
        self,
        context_builder=None,
        prompt=None,
        llm=None,
    ):
        self.context_builder = context_builder or ContextBuilder()
        self.prompt = prompt or RAGPrompt().get_prompt()
        self.llm = llm or GeminiLLM()

    def generate(self, question: str, documents: list) -> dict:
        context = self.context_builder.build(documents)
        prompt_value = self.prompt.invoke(
            {
                "context": context,
                "question": question,
            }
        )
        rendered_prompt = self._render_prompt(prompt_value)
        answer = self.llm.generate(rendered_prompt)

        return {
            "answer": answer,
            "sources": [
                self._source_from_document(index, document)
                for index, document in enumerate(documents, start=1)
            ],
        }

    @staticmethod
    def _render_prompt(prompt_value) -> str:
        if hasattr(prompt_value, "to_string"):
            return prompt_value.to_string()

        if hasattr(prompt_value, "to_messages"):
            return "\n".join(
                message.content
                for message in prompt_value.to_messages()
            )

        return str(prompt_value)

    @staticmethod
    def _source_from_document(index, document) -> dict:
        metadata = document.metadata or {}
        return {
            "source_number": index,
            "video_id": metadata.get("video_id"),
            "video_title": metadata.get("video_title"),
            "start_time": metadata.get("start_time"),
            "end_time": metadata.get("end_time"),
            "source": metadata.get("source"),
            "chunk_id": metadata.get("chunk_id"),
        }
