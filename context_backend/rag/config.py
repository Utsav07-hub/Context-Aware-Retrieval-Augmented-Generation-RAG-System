"""Application configuration."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    chroma_path: str = os.getenv("CHROMA_PATH", "vectorstore")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    gemini_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    gemini_max_output_tokens: int = int(
        os.getenv("GEMINI_MAX_OUTPUT_TOKENS", "1024")
    )


settings = Settings()
