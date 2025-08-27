import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ghc_twin import app as langgraph_app

# Create FastAPI app
api = FastAPI(title="GHC Digital Twin API", version="1.0.0")

# Configure CORS with specified origins
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "https://zakibaydoun.github.io,https://zakibaydoun.github.io/GHC-DT")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

api.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    source_type: str = "public"

class QueryResponse(BaseModel):
    final_answer: str
    status: str = "success"

class IngestRequest(BaseModel):
    texts: List[str]
    metadatas: List[Dict[str, Any]] = None
    source_type: str = "public"

class IngestResponse(BaseModel):
    status: str
    ingested_count: int
    message: str

class HealthResponse(BaseModel):
    ok: bool
    service: str = "GHC Digital Twin"
    version: str = "1.0.0"

# Routes
@api.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - returns JSON with ok: true"""
    return HealthResponse(ok=True)

@api.post("/api/twin/query", response_model=QueryResponse)
async def query_twin(request: QueryRequest):
    """Process a question and return an answer from the digital twin"""
    try:
        # Prepare the input state using TwinState pattern
        input_state = {
            "question": request.question,
            "source_type": request.source_type,
            "context": [],
            "answer": "",
            "final_answer": ""
        }
        
        # Invoke the LangGraph app
        result = await langgraph_app.ainvoke(input_state)
        
        return QueryResponse(
            final_answer=result.get("final_answer", "Unable to generate answer"),
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.post("/api/twin/ingest_texts", response_model=IngestResponse)
async def ingest_texts(
    request: IngestRequest,
    x_ingest_token: str = Header(None, alias="X-INGEST-TOKEN")
):
    """Ingest new documents into the digital twin's knowledge base"""
    # Check for auth token if configured
    expected_token = os.getenv("INGEST_AUTH_TOKEN")
    if expected_token and x_ingest_token != expected_token:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or missing X-INGEST-TOKEN header"
        )
    
    try:
        # Use the canonical DocumentStore.add_texts() method
        result = langgraph_app.document_store.add_texts(
            texts=request.texts,
            metadatas=request.metadatas,
            source_type=request.source_type
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return IngestResponse(
            status=result["status"],
            ingested_count=result["ingested_count"],
            message=result.get("message", f"Ingested {result['ingested_count']} chunks")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/twin/status")
async def get_status():
    """Get the status of the digital twin"""
    try:
        # Get collection stats from document store
        stats = langgraph_app.document_store.get_collection_stats()
        
        return {
            "status": "operational",
            "document_count": stats["document_count"],
            "collection_status": stats["status"],
            "model": "gpt-4",
            "embedding_model": "text-embedding-ada-002",
            "vector_store_dir": os.getenv("VECTOR_STORE_DIR", "vector_store")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "document_count": 0
        }

@api.get("/api/twin/sentinel")
async def test_sentinel():
    """Test endpoint for sentinel phrase retrieval"""
    try:
        sentinel_question = "What is the GHC sentinel phrase for digital-roots?"
        
        input_state = {
            "question": sentinel_question,
            "source_type": "system",
            "context": [],
            "answer": "",
            "final_answer": ""
        }
        
        result = await langgraph_app.ainvoke(input_state)
        
        sentinel = "GHC-SENTINEL :: digital-roots ? twin ? 2025-08-27"
        contains_sentinel = sentinel in result.get("final_answer", "")
        
        return {
            "status": "success" if contains_sentinel else "failed",
            "contains_sentinel": contains_sentinel,
            "expected_sentinel": sentinel,
            "final_answer": result.get("final_answer", "")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Export the API as 'app' for LangGraph Cloud
app = api