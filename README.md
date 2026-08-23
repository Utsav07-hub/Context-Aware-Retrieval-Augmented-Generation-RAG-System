# Context-Aware Retrieval-Augmented Generation (RAG) System

A multi-source Retrieval-Augmented Generation (RAG) platform that allows users to ingest YouTube videos and documents, index their content using embeddings, retrieve relevant context, and ask questions through a conversational interface.

The system is designed to provide answers grounded in the selected source rather than relying only on the language model's general knowledge.

---

## Features

- YouTube video ingestion
- PDF document ingestion
- DOCX document ingestion
- TXT document ingestion
- Markdown document ingestion
- Automatic document chunking
- Semantic embeddings
- Persistent vector storage using Chroma
- Source-aware retrieval
- Conversational question answering
- Source citations with retrieved chunks
- Source persistence across frontend refreshes
- FastAPI backend
- Next.js frontend
- API health monitoring
- One-command local startup
- Automated backend tests

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      User            │
                         │  Web Application     │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Next.js Frontend   │
                         │                      │
                         │  • Source Manager    │
                         │  • Chat Interface    │
                         │  • Upload Interface  │
                         └──────────┬───────────┘
                                    │
                              HTTP / REST API
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         │                      │
                         │  /api/health         │
                         │  /api/sources        │
                         │  /api/chat           │
                         └──────────┬───────────┘
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
        ┌──────────────────┐                ┌──────────────────┐
        │ Source Ingestion │                │ Retrieval System │
        └────────┬─────────┘                └────────┬─────────┘
                 │                                   │
        ┌────────┼────────┐                          │
        ▼        ▼        ▼                          │
     YouTube    PDF     DOCX                         │
        │        │        │                          │
        └────────┼────────┘                          │
                 │                                   │
              TXT / MD                               │
                 │                                   │
                 ▼                                   │
           Document Loader                           │
                 │                                   │
                 ▼                                   │
             Chunking                                │
                 │                                   │
                 ▼                                   │
             Embeddings                              │
                 │                                   │
                 ▼                                   │
          ┌──────────────┐                           │
          │    Chroma    │◄──────────────────────────┘
          │ Vector Store │
          └──────────────┘
                 │
                 ▼
          Relevant Context
                 │
                 ▼
                LLM
                 │
                 ▼
          Answer + Sources
````

---

## RAG Pipeline

### Indexing

```text
Source
  │
  ├── YouTube
  ├── PDF
  ├── DOCX
  ├── TXT
  └── Markdown
        │
        ▼
      Loader
        │
        ▼
   Text Extraction
        │
        ▼
      Chunking
        │
        ▼
    Embeddings
        │
        ▼
      Chroma
```

### Question Answering

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
Vector Search
      │
      ▼
Relevant Chunks
      │
      ▼
Context Construction
      │
      ▼
Language Model
      │
      ▼
Answer
      │
      ▼
Source Citations
```

---

## Supported Sources

| Source   | Supported |
| -------- | --------- |
| YouTube  | ✅         |
| PDF      | ✅         |
| DOCX     | ✅         |
| TXT      | ✅         |
| Markdown | ✅         |

The system converts each supported source into chunks before generating embeddings and storing them in the vector database.

---

## Project Structure

```text
Context-Aware Retrieval-Augmented Generation (RAG) System/
│
├── context_backend/
│   │
│   ├── api/
│   │   ├── main.py
│   │   │
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   └── sources.py
│   │   │
│   │   └── schemas/
│   │       ├── sources.py
│   │       └── ...
│   │
│   ├── rag/
│   │   │
│   │   ├── ingestion/
│   │   │   ├── pdf_loader.py
│   │   │   ├── docx_loader.py
│   │   │   └── text_loader.py
│   │   │
│   │   ├── pipeline/
│   │   │   └── indexing.py
│   │   │
│   │   ├── vectorstore/
│   │   │   └── chroma_store.py
│   │   │
│   │   ├── embeddings/
│   │   └── ...
│   │
│   ├── tests/
│   │
│   ├── requirements.txt
│   └── ...
│
├── context_frontend/
│   │
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── start.bat
├── .gitignore
└── README.md
```

> The exact contents may evolve as the project continues to develop.

---

# Backend

The backend is built using **FastAPI**.

## Main API Endpoints

### Health Check

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok",
  "service": "youtube-rag-api"
}
```

---

### Add YouTube Source

```http
POST /api/sources/youtube
```

Example request:

```json
{
  "url": "[text](https://youtu.be/EFx9rugyRGE)"
}
```

Example response:

```json
{
  "source_id": "source-uuid",
  "source_type": "youtube",
  "title": "Example Video",
  "source": "[text](https://youtu.be/EFx9rugyRGE)",
  "video_id": "example",
  "chunk_count": 420,
  "status": "indexed"
}
```

---

### Upload Document

```http
POST /api/sources/upload
```

Supported formats:

```text
.pdf
.docx
.txt
.md
```

The backend:

1. Receives the uploaded file.
2. Determines the appropriate loader.
3. Extracts text.
4. Splits the content into chunks.
5. Generates embeddings.
6. Stores the chunks in Chroma.
7. Returns source metadata.

---

### List Indexed Sources

```http
GET /api/sources
```

Returns the indexed sources available in the vector store.

---

### Ask a Question

```http
POST /api/chat
```

Example:

```json
{
  "source_id": "source-uuid",
  "question": "What is the main concept explained in this document?"
}
```

The system retrieves relevant chunks from the selected source and generates an answer based on the retrieved context.

---

# Frontend

The frontend is built with:

* Next.js
* TypeScript
* Tailwind CSS

The interface provides:

* Source management
* YouTube URL ingestion
* Document upload
* Source selection
* Conversational chat
* Retrieved source citations
* Backend status indicator
* Source persistence

---

# Local Development

## Requirements

Make sure you have:

* Python 3.10+
* Node.js
* npm
* Git

---

## Backend Setup

Navigate to the backend:

```bash
cd context_backend
```

Create/activate your Python environment.

Then install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```text
.env
```

Add the required environment variables.

Never commit `.env` to GitHub.

---

## Frontend Setup

Navigate to:

```bash
cd context_frontend
```

Install dependencies:

```bash
npm install
```

Create:

```text
.env.local
```

Example:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

# Running the Application

The project includes a root-level startup script.

From the project root:

```bash
start.bat
```

This starts:

```text
FastAPI Backend
      ↓
http://127.0.0.1:8000

Next.js Frontend
      ↓
http://localhost:3000
```

The launcher starts both services and waits for the backend health endpoint before opening the frontend.

You can also run the services manually.

### Backend

```bash
cd context_backend

python -m uvicorn api.main:app --reload
```

### Frontend

```bash
cd context_frontend

npm run dev
```

---

# Testing

The backend includes automated tests.

Run:

```bash
cd context_backend
python -m pytest -q
```

Current test status:

```text
35 passed
1 skipped
```

The test suite covers the implemented backend functionality and regression behavior.

---

# Important Engineering Detail: Chunk IDs

During development, multi-page PDFs exposed an issue with duplicate Chroma document IDs.

The original indexing logic could preserve page-local chunk IDs generated during separate chunker calls:

```text
page 1 → source_id:0
page 2 → source_id:0
page 3 → source_id:0
```

Chroma requires IDs to be unique within an upsert operation.

The indexing pipeline now assigns a global chunk ID based on the source UUID and the global chunk position:

```text
source_id:0
source_id:1
source_id:2
source_id:3
...
```

This guarantees unique IDs across all chunks generated during a document upload.

The change is applied to the document indexing path without changing the YouTube indexing path.

---

# Design Principles

The project follows several principles:

### Source-aware retrieval

Questions are associated with a selected source so that retrieval can be restricted to the relevant knowledge base.

### Grounded generation

The language model receives retrieved context instead of being expected to answer entirely from its pretrained knowledge.

### Persistent source metadata

Indexed sources can be restored after refreshing the frontend.

### Modular ingestion

Different source types use separate loaders while sharing the downstream indexing pipeline.

```text
Source
  ↓
Loader
  ↓
Documents
  ↓
Chunking
  ↓
Embeddings
  ↓
Vector Store
```

### Separation of concerns

```text
Frontend
   ↓
API
   ↓
RAG Pipeline
   ↓
Vector Store
```

The frontend does not directly interact with the vector database.

---

# Current Status

## Completed

* [x] FastAPI backend
* [x] Next.js frontend
* [x] YouTube ingestion
* [x] PDF ingestion
* [x] DOCX ingestion
* [x] TXT ingestion
* [x] Markdown ingestion
* [x] Document chunking
* [x] Embedding generation
* [x] Chroma vector storage
* [x] Source metadata persistence
* [x] Source-aware chat
* [x] Retrieval citations
* [x] Frontend/backend health status
* [x] One-command local startup
* [x] Automated backend tests
* [x] Multi-page PDF duplicate-ID fix

## In Progress / Future Work

* [ ] Improve retrieval quality
* [ ] Retrieval evaluation dataset
* [ ] Answer faithfulness evaluation
* [ ] Better conversational memory
* [ ] Query rewriting
* [ ] Retrieval reranking
* [ ] Improved document metadata
* [ ] Production deployment
* [ ] Dockerization
* [ ] Production vector database
* [ ] Authentication
* [ ] Monitoring and logging

---

# Future Architecture

The current system is designed so that the local architecture can later evolve into a production deployment:

```text
                    User
                     │
                     ▼
              Next.js Frontend
                     │
                     ▼
               FastAPI API
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
     RAG Pipeline          LLM Provider
          │
          ▼
     Vector Database
```

The local Chroma-based setup is intended for development and experimentation. Production deployment can use a managed vector database and containerized services.

---

# Why This Project?

Traditional language models can answer questions from their training data, but they do not automatically know the contents of a user's private documents or newly provided information.

RAG addresses this by separating:

```text
Knowledge Storage
       +
Information Retrieval
       +
Language Generation
```

This project demonstrates that complete workflow with multiple real-world source types.

Instead of asking an LLM:

```text
"What do you know about this?"
```

the system performs:

```text
"What information exists in my selected source?"
              ↓
         Retrieve it
              ↓
       Give it to the LLM
              ↓
       Generate grounded answer
```

---
