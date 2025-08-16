from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.tools import tool

VS_DIR = "vectorstore"

def _vs():
    embed = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(VS_DIR, embed, allow_dangerous_deserialization=True)

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
