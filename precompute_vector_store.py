#!/usr/bin/env python3
"""
CLI to precompute the vector store from a list of canonical document paths.
Delegates ingestion to app/ingest.py functionality.

Usage:
    python precompute_vector_store.py --persist vector_store docs/file1.pdf docs/file2.docx

Env:
    EMBEDDING_BACKEND=hf|openai
    OPENAI_API_KEY=...
    OPENAI_EMBED_MODEL=text-embedding-3-large
"""
import argparse
import os
from typing import List

from app.document_store import ingest_canonical_docs


def main(argv: List[str] | None = None):
        parser = argparse.ArgumentParser()
        parser.add_argument("paths", nargs="+", help="Document paths to ingest")
        parser.add_argument(
            "--persist",
            default=os.getenv("VECTORSTORE_DIR")
            or os.getenv("VECTOR_STORE_DIR")
            or "vector_store",
            help="Persist dir",
        )
        args = parser.parse_args(argv)

        os.makedirs(args.persist, exist_ok=True)
        vectordb = ingest_canonical_docs(args.paths, args.persist)
        if vectordb is None:
                print("Ingestion failed or no documents were processed.")
                raise SystemExit(1)
        print(f"Done. Persisted at {args.persist}")


if __name__ == "__main__":
        main()
