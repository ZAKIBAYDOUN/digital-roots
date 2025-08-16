import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not found. Please set before ingestion.")

VS_DIR = Path(__file__).resolve().parent / "vectorstore"


def _vs():
    """Load the persisted FAISS vector store using OpenAI embeddings."""
    return FAISS.load_local(
        str(VS_DIR),
        OpenAIEmbeddings(model="text-embedding-3-small"),
        allow_dangerous_deserialization=True,
    )

@tool
def ghc_docs(query: str) -> str:
    """Search Green Hill docs; return short cited snippets."""
    vs = _vs()
    hits = vs.similarity_search(query, k=4)
    out = []
    for h in hits:
        meta = h.metadata
        src = meta.get("source", "doc")
        page = meta.get("page")
        cite = f"{src}" + (f", p.{page}" if page else "")
        out.append(f"- {h.page_content.strip()}\n  [Source: {cite}]")
    return "\n".join(out)
