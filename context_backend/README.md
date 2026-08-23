# YouTube RAG

A modular Retrieval-Augmented Generation starter project for asking questions about YouTube transcripts.

## Structure

- `rag/ingestion`: load and clean transcripts
- `rag/chunking`: split transcripts into searchable chunks
- `rag/embeddings`: create vector embeddings
- `rag/vectorstore`: persist vectors with ChromaDB
- `rag/retrieval`: retrieve and rerank context
- `rag/generation`: build prompts and call an LLM
- `rag/pipeline`: compose indexing and query workflows
- `data/raw`: source transcripts
- `data/processed`: cleaned transcripts
- `vectorstore`: local ChromaDB data

## Setup

Create and activate a virtual environment, then install dependencies from `requirements.txt`.
Copy your API credentials into `.env` when enabling an LLM provider.

Run tests with `pytest` from this directory.
