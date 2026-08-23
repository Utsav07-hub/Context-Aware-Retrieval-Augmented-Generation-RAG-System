from pydantic import BaseModel, HttpUrl


class YouTubeSourceRequest(BaseModel):
    url: HttpUrl


class SourceResponse(BaseModel):
    source_id: str
    source_type: str
    title: str | None = None
    source: str
    video_id: str | None = None
    chunk_count: int
    status: str