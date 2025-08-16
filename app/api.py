from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from typing import Any, Dict, List, Optional

from app.ghc_twin import app as graph_app
from app.models import TwinState
from app.document_store import DocumentStore


api = FastAPI(title="Green Hill Canarias Digital Twin API")

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: Optional[str] = None
    source_type: Optional[str] = "public"
    origin: Optional[str] = None
    source_id: Optional[str] = None
    priority: Optional[str] = "normal"
    timestamp: Optional[str] = None


class IngestTextsRequest(BaseModel):
    texts: List[str]
    metadatas: Optional[List[Dict[str, Any]]] = None
    ids: Optional[List[str]] = None


@api.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@api.post("/api/twin/query")
def query(req: QueryRequest):
    try:
        state = TwinState(
            question=req.question,
            source_type=(req.source_type or "public"),
            origin=req.origin,
            source_id=req.source_id,
            priority=(req.priority or "normal"),
            timestamp=req.timestamp,
        )
        result = graph_app.invoke(state)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api.post("/api/twin/ingest_texts")
def ingest_texts(req: IngestTextsRequest):
    persist_dir = (
        os.getenv("VECTORSTORE_DIR")
        or os.getenv("VECTOR_STORE_DIR")
        or "vector_store"
    )
    store = DocumentStore(persist_dir)
    ok = store.add_texts(texts=req.texts, metadatas=req.metadatas, ids=req.ids)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to add texts")
    return {"ok": True, "count": len(req.texts)}


# Serve a tiny static UI if web/ exists
web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
web_dir = os.path.abspath(web_dir)
if os.path.isdir(web_dir):
    api.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
