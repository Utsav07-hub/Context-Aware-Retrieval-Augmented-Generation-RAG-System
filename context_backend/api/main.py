from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.sources import router as sources_router
from api.routes.health import router as health_router
from api.routes.chat import router as chat_router


app = FastAPI(
    title="YT-RAG API",
    description="Backend API for the YouTube RAG platform",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
    prefix="/api",
)


app.include_router(
    sources_router,
    prefix="/api/sources",
    tags=["sources"],
)


app.include_router(
    chat_router,
    prefix="/api/chat",
    tags=["chat"],
)


@app.get("/")
def root():
    return {
        "service": "youtube-rag-api",
        "status": "running",
    }