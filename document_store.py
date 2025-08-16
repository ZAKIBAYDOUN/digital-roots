"""Legacy shim for DocumentStore utilities."""
from app.document_store import (
    DocumentStore,
    ingest_canonical_docs,
    get_document_store,
    bootstrap_store,
)

__all__ = [
    "DocumentStore",
    "ingest_canonical_docs",
    "get_document_store",
    "bootstrap_store",
]
