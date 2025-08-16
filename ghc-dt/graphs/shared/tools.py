import os, pathlib
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import tool

VS_DIR = os.getenv("VECTORSTORE_DIR", "vectorstore")

_FRIENDLY = {
    "Strategic_Plan-GreenHill_v10-pre-FINAL.pdf": "Strategic Plan v10 pre-FINAL",
    "Strategic_Plan-GreenHill_v10-pre-FINAL.docx": "Strategic Plan v10 pre-FINAL",
    "appendex.docx": "Appendix A",
    "ex sum implementation plan final.docx": "Implementation Plan",
    "ex sum market overview final.docx": "Market Overview",
    "ex sum company despcription final.docx": "Company Description",
    "ex sum financial projections final.docx": "Financial Projections",
    "ex sum risk analysis final.docx": "Risk Analysis",
    "ex sum conclusion final.docx": "Conclusion",
    "240726_SHA_Grren_Hill_1.pdf": "SHA 2024",
}

def _pretty_cite(meta: dict) -> str:
    import os as _os
    src = meta.get("source", "document")
    page = meta.get("page")
    name = _FRIENDLY.get(_os.path.basename(src), _os.path.basename(src))
    return f"{name}, p.{page}" if page is not None else name

def _load_vs():
    if not os.path.isdir(VS_DIR):
        raise RuntimeError(f"Vectorstore missing: {VS_DIR}/  (Run: python ingest/index_plan.py)")
    return FAISS.load_local(VS_DIR, OpenAIEmbeddings(), allow_dangerous_deserialization=True)

@tool
def ghc_docs(query: str) -> str:
    """Search Green Hill plan & Appendix A; return 3–5 short, cited snippets."""
    vs = _load_vs()
    hits = vs.similarity_search(query, k=4)
    if not hits:
        return "No KB match. Refine query or rebuild vectorstore from data/."
    out: List[str] = []
    for h in hits:
        meta = getattr(h, "metadata", {}) or {}
        out.append(f"- {h.page_content.strip().replace('\\n',' ')}\n  — {_pretty_cite(meta)}")
    return "\n".join(out)
