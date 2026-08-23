"""LLM provider abstractions and Gemini implementation."""

from abc import ABC, abstractmethod
import os
from typing import Any

from rag.config import settings


class LLMGenerationError(RuntimeError):
    """Raised when an LLM provider cannot return a usable response."""


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a fully rendered prompt."""


class GeminiLLM(LLMProvider):

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        temperature: float | None = None,
        max_output_tokens: int | None = None,
        client=None,
    ):

        if api_key is None:
            api_key = settings.gemini_api_key or os.getenv(
                "GEMINI_API_KEY"
            )

        if not api_key:
            raise LLMGenerationError(
                "GEMINI_API_KEY is required"
            )

        self.api_key = api_key

        self.model_name = (
            model_name or settings.gemini_model
        )

        self.temperature = (
            settings.gemini_temperature
            if temperature is None
            else temperature
        )

        self.max_output_tokens = (
            settings.gemini_max_output_tokens
            if max_output_tokens is None
            else max_output_tokens
        )

        self.client = client or self._create_client()

    def generate(self, prompt: str) -> str:

        if not prompt.strip():
            raise LLMGenerationError(
                "Prompt cannot be empty"
            )

        try:

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

        except Exception as exc:

            raise LLMGenerationError(
                "Gemini generation request failed"
            ) from exc

        text = getattr(response, "text", None)

        if not text:
            text = self._extract_text_from_candidates(
                response
            )

        text = (text or "").strip()

        if not text:
            raise LLMGenerationError(
                "Gemini returned an empty response"
            )

        return text

    def _create_client(self):

        try:
            from google import genai

        except ImportError as exc:

            raise LLMGenerationError(
                "google-genai is required for Gemini generation"
            ) from exc

        return genai.Client(
            api_key=self.api_key
        )

    @staticmethod
    def _extract_text_from_candidates(response):

        candidates = (
            getattr(response, "candidates", None)
            or []
        )

        parts = []

        for candidate in candidates:

            content = getattr(
                candidate,
                "content",
                None
            )

            if content is None:
                continue

            candidate_parts = (
                getattr(content, "parts", None)
                or []
            )

            for part in candidate_parts:

                part_text = getattr(
                    part,
                    "text",
                    None
                )

                if part_text:
                    parts.append(part_text)

        return "\n".join(parts)


def generate(prompt: str) -> str:
    """Generate text with the default Gemini provider."""

    return GeminiLLM().generate(prompt)