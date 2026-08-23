from pathlib import Path
from tempfile import NamedTemporaryFile
# import traceback
from fastapi import APIRouter, HTTPException, UploadFile, File

from api.schemas.sources import (
    SourceResponse,
    YouTubeSourceRequest,
)
from rag.pipeline.indexing import IndexingPipeline
from rag.config import settings
from rag.embeddings.embedder import EmbeddingModel
from rag.vectorstore.chroma_store import ChromaVectorStore

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@router.post("/youtube", response_model=SourceResponse)
def add_youtube_source(request: YouTubeSourceRequest):
    try:
        pipeline = IndexingPipeline()
        result = pipeline.index_video(str(request.url))

        return SourceResponse(
            source_id=result["source_id"],
            source_type=result["source_type"],
            title=result.get("video_title"),
            source=result["source"],
            video_id=result["video_id"],
            chunk_count=result["chunk_count"],
            status="indexed",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to index YouTube source.",
        ) from exc


@router.post("/upload", response_model=SourceResponse)
async def upload_source(file: UploadFile = File(...)):
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use PDF, DOCX, TXT, or Markdown.",
        )

    temp_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:
            temp_path = Path(temp_file.name)

            while chunk := await file.read(1024 * 1024):
                temp_file.write(chunk)

        pipeline = IndexingPipeline()

        result = pipeline.index_file(
            temp_path,
            original_filename=filename,
        )

        return SourceResponse(
            source_id=result["source_id"],
            source_type=result["source_type"],
            title=result.get("title"),
            source=result["source"],
            video_id="",
            chunk_count=result["chunk_count"],
            status=result["status"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Failed to index uploaded file.",
        ) from exc

    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()
            
@router.get("")
def list_sources():
    try:
        vector_store = _get_vector_store()
        return {"sources": vector_store.list_sources()}

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to load indexed sources.",
        ) from exc
            
def _get_vector_store() -> ChromaVectorStore:
    embedding_model = EmbeddingModel(
        model_name=settings.embedding_model
    )

    return ChromaVectorStore(
        embedding_function=embedding_model.get_model(),
        persist_directory=settings.chroma_path,
        collection_name="youtube_transcripts",
    )