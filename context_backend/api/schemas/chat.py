from pydantic import BaseModel


class ChatRequest(BaseModel):
    source_id: str
    question: str


class ChatSource(BaseModel):
    source_number: int
    video_id: str | None = None
    video_title: str | None = None
    start_time: float | None = None
    end_time: float | None = None
    source: str | None = None
    chunk_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    
from fastapi import APIRouter, HTTPException

from api.schemas.chat import (
    ChatRequest,
    ChatResponse,
)
from api.services.rag_service import RAGService


router = APIRouter()

rag_service = RAGService()


@router.post("", response_model=ChatResponse)
def chat(request: ChatRequest):

    try:
        result = rag_service.answer(
            question=request.question,
            source_id=request.source_id,
        )

        return ChatResponse(**result)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="RAG generation failed.",
        ) from exc