"""Document store wrapper and ingestion helpers for the app namespace.

Self-contained: no imports from root-level modules.
"""
import os
import uuid
from typing import List, Optional, Dict, Any

from langchain.text_splitter import RecursiveCharacterTextSplitter


def _get_embeddings():
    backend = os.getenv("EMBEDDING_BACKEND", "hf").lower()
    if backend == "openai":
        from langchain_openai import OpenAIEmbeddings
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
        return OpenAIEmbeddings(model=model)
    # Default to HuggingFace
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        model_name = os.getenv("HUGGINGFACE_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
        return HuggingFaceEmbeddings(model_name=model_name)
    except Exception:
        from langchain_openai import OpenAIEmbeddings
        model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-large")
        return OpenAIEmbeddings(model=model)


class DocumentStore:
    """Thin wrapper over Chroma vector store with a simple query() API.

    Parameters
    ----------
    persist_dir: Optional[str]
        Directory to persist the vector store. If not provided, the
        ``VECTORSTORE_DIR`` environment variable is used. As a final
        fallback, ``"vector_store"`` is chosen. This allows the document
        store to be instantiated without explicit configuration which is
        useful in tests and simple deployments.
    """

    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = (
            persist_dir
            or os.getenv("VECTORSTORE_DIR")
            or os.getenv("VECTOR_STORE_DIR")
            or "vector_store"
        )
        self.vectordb = None
        self._try_load()

    def _try_load(self):
        try:
            from langchain_chroma import Chroma
            embeddings = _get_embeddings()
            if os.path.exists(self.persist_dir):
                self.vectordb = Chroma(
                    persist_directory=self.persist_dir,
                    embedding_function=embeddings,
                )
        except Exception as e:
            print(f"Vector store load failed: {e}")
            self.vectordb = None

    def is_available(self) -> bool:
        return self.vectordb is not None

    def query(self, text: str, k: int = 5) -> str:
        if not self.vectordb:
            return "No vector store available"
        try:
            docs = self.vectordb.similarity_search(text, k=k)
            return "\n\n".join(d.page_content for d in docs)
        except Exception as e:
            return f"Vector store query failed: {e}"

    # --- Write APIs ---
    def _ensure_store(self):
        if self.vectordb:
            return self.vectordb
        try:
            from langchain_chroma import Chroma
            os.makedirs(self.persist_dir, exist_ok=True)
            embeddings = _get_embeddings()
            self.vectordb = Chroma(
                persist_directory=self.persist_dir,
                embedding_function=embeddings,
            )
            return self.vectordb
        except Exception as e:
            print(f"Error creating vector store for upsert: {e}")
            return None

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> bool:
        store = self._ensure_store()
        if not store:
            return False
        try:
            store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            return True
        except Exception as e:
            print(f"Error adding texts: {e}")
            return False

    def add_agent_outputs(self, state: Any) -> bool:
        items: List[tuple[str, Dict[str, Any]]] = []

        def _pack(name: str, data: Optional[Dict[str, Any]]):
            if not data:
                return
            summary = data.get("analysis") or str(data)
            items.append(
                (
                    summary,
                    {
                        "source": "agent_output",
                        "agent": name,
                        "origin": getattr(state, "origin", None),
                        "source_id": getattr(state, "source_id", None),
                        "question": getattr(state, "question", None),
                        "timestamp": getattr(state, "timestamp", None),
                    },
                )
            )

        _pack("strategy", getattr(state, "strategy_output", None))
        _pack("finance", getattr(state, "finance_output", None))
        _pack("operations", getattr(state, "operations_output", None))
        _pack("market", getattr(state, "market_output", None))
        _pack("risk", getattr(state, "risk_output", None))
        _pack("compliance", getattr(state, "compliance_output", None))
        _pack("innovation", getattr(state, "innovation_output", None))
        gh = getattr(state, "green_hill_response", None) or {}
        if gh.get("memo"):
            items.append(
                (
                    gh["memo"],
                    {
                        "source": "agent_output",
                        "agent": "GreenHillGPT",
                        "question": getattr(state, "question", None),
                    },
                )
            )

        if not items:
            return True

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts: List[str] = []
        metas: List[Dict[str, Any]] = []
        ids: List[str] = []
        for text, meta in items:
            chunks = splitter.split_text(text)
            base_id = str(uuid.uuid4())
            for i, ch in enumerate(chunks):
                texts.append(ch)
                metas.append({**meta, "chunk": i})
                ids.append(f"agent:{base_id}:{i}")

        return self.add_texts(texts, metas, ids)


def ingest_canonical_docs(doc_paths: List[str], persist_dir: str):
    """Ingest explicit file paths into a Chroma vector store."""
    try:
        from langchain_community.document_loaders import (
            PyPDFLoader,
            Docx2txtLoader,
            UnstructuredExcelLoader,
            TextLoader,
        )
        from langchain_chroma import Chroma
    except Exception as e:
        print(f"Missing ingestion deps: {e}")
        return None

    docs = []
    for p in doc_paths:
        if not os.path.exists(p):
            print(f"skip missing: {p}")
            continue
        try:
            if p.lower().endswith(".pdf"):
                docs.extend(PyPDFLoader(p).load())
            elif p.lower().endswith(".docx"):
                docs.extend(Docx2txtLoader(p).load())
            elif p.lower().endswith((".xlsx", ".xls")):
                docs.extend(UnstructuredExcelLoader(p).load())
            elif p.lower().endswith(".txt"):
                docs.extend(TextLoader(p).load())
        except Exception as e:
            print(f"failed to load {p}: {e}")

    if not docs:
        print("no documents loaded")
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    embeddings = _get_embeddings()
    os.makedirs(persist_dir, exist_ok=True)
    try:
        db = Chroma.from_documents(chunks, embeddings, persist_directory=persist_dir)
        print(f"persisted {len(chunks)} chunks -> {persist_dir}")
        return db
    except Exception as e:
        print(f"vector store creation failed: {e}")
        return None


def get_document_store(persist_dir: str) -> Optional[DocumentStore]:
    return DocumentStore(persist_dir)


def bootstrap_store(persist_dir: str):
    """Optionally download and extract a vector store archive at startup.

    Set VECTOR_STORE_URL to a .zip or .tar.gz file containing the Chroma dir.
    If persist_dir already exists with files, this is a no-op.
    """
    if os.path.isdir(persist_dir) and any(os.scandir(persist_dir)):
        return
    url = os.getenv("VECTOR_STORE_URL")
    if not url:
        return
    os.makedirs(persist_dir, exist_ok=True)
    tmp_path = "/tmp/vector_store_asset"
    try:
        import urllib.request
        print(f"Downloading vector store from {url}...")
        urllib.request.urlretrieve(url, tmp_path)
        if url.endswith(".zip"):
            import zipfile
            with zipfile.ZipFile(tmp_path, "r") as zf:
                zf.extractall(persist_dir)
        elif url.endswith((".tar.gz", ".tgz")):
            import tarfile
            with tarfile.open(tmp_path, "r:gz") as tf:
                tf.extractall(persist_dir)
        else:
            print("Unsupported archive type for VECTOR_STORE_URL (use .zip or .tar.gz)")
            return
        print(f"Vector store extracted to {persist_dir}")
    except Exception as e:
        print(f"Vector store bootstrap failed: {e}")
