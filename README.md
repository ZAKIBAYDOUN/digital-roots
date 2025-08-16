# Green Hill Canarias – Digital Twin

A multi-agent LangGraph application with retrieval and memo synthesis. Use the Streamlit UI for an easy start, or call the API directly.

## Quick Start

1) Local dev – install and run a UI

- Install deps:
  - pip install -r requirements.txt
- Start Streamlit (UI):
  - streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501
  - Open the forwarded 8501 port in your browser

2) Optional: Start the API

- uvicorn app.api:api --host 0.0.0.0 --port 8000
- GET http://localhost:8000/health

3) Minimal environment (low-security)

- Temporary for shell: `export OPENAI_API_KEY='sk-...'`
- Persistent for app/Docker: add to `.env` in repo root:

```env
OPENAI_API_KEY=sk-...
EMBEDDING_BACKEND=openai
VECTOR_STORE_DIR=/data/vectorstore
ALLOWED_ORIGINS=*
```

4) Docker (VPS) quick deploy

```bash
cd docker
docker compose up -d --build
```

Open: http://SERVER_IP/health and http://SERVER_IP:8501

> Organization setup: see ORG_SETUP.md for Codespaces billing, policies, and secrets in the green-hill-canarias org.

## Streamlit UI Guide

- Run tab
  - Presets: one-click examples to get started
  - Mode: Question or Content-only (no question; provide a payload_ref and optional metadata)
  - Target agent (optional): force routing to a specific agent
  - Download: export the full resulting state as JSON

- Ingest tab
  - Paste text (one line per item) and ingest to the vector store
  - Uses VECTOR_STORE_DIR (default: vector_store)

- Status tab
  - Shows vector store availability and allows a quick search
  - Checks API /health and displays if OPENAI_API_KEY is set

## API Usage

- POST /api/twin/query
  - Body (question mode): { "question": "...", "source_type": "public" }
  - Body (content-only): { "source_type": "web_source", "payload_ref": "https://...", "metadata": { ... } }
  - Returns the full TwinState as JSON, including final_answer and agent outputs

- POST /api/twin/ingest_texts
  - Body: { "texts": ["...","..."], "metadatas": [{...},{...}] }
  - Adds content to the Chroma vector store for retrieval

## Documents & Retrieval

- One-off ingestion (files):
  - Place PDFs/DOCX/XLSX/TXT under docs/
  - python app/ingest.py --source docs --out vector_store
  - Set VECTOR_STORE_DIR=vector_store

- Runtime additions (programmatic):
  - app.document_store.DocumentStore.add_texts([...])
  - Agent outputs are auto-archived on finalize (disable with ARCHIVE_AGENT_OUTPUTS=0)

## Environment

- VECTOR_STORE_DIR=vector_store
- EMBEDDING_BACKEND=hf | openai (default: hf)
- HUGGINGFACE_EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
- OPENAI_EMBED_MODEL=text-embedding-3-small (if EMBEDDING_BACKEND=openai)
- OPENAI_API_KEY, OPENAI_CHAT_MODEL, GREEN_HILL_CHAT_MODEL
- ARCHIVE_AGENT_OUTPUTS=1

## Cloud Deployment (LangGraph)

- Entry: ./app/ghc_twin.py:app (see langgraph.json)
- env_files in langgraph.json auto-load .env and .env.multi_agent
- Provide either LANGSMITH_API_KEY (dev) or LANGGRAPH_CLOUD_LICENSE_KEY (prod) in the environment

## Troubleshooting

- “langgraph up” exits with license error:
  - Set LANGSMITH_API_KEY (dev) or LANGGRAPH_CLOUD_LICENSE_KEY (prod) in .env
- UI/health doesn’t load in a Codespace/container:
  - Ensure ports (8501 for Streamlit, 8000 for API) are forwarded and public
- Vector store says “No vector store available”:
  - Create it via the Ingest tab or run the ingester; confirm VECTOR_STORE_DIR points to the directory
- LLM calls fail:
  - Set OPENAI_API_KEY, and choose OPENAI_CHAT_MODEL (e.g., gpt-4o-mini)

