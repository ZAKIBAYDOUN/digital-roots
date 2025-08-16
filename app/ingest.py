# app/ingest.py
import os
import glob
from typing import List, Optional

def ingest_docs(source_dir: str, persist_dir: str, embed_model: str = None):
    """Ingest documents from source directory into vector store"""
    
    try:
        # Import dependencies
        from langchain_community.document_loaders import (
            PyPDFLoader, Docx2txtLoader, UnstructuredExcelLoader
        )
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma
        from langchain_huggingface import HuggingFaceEmbeddings
        
    except ImportError as e:
        print(f"Missing dependencies for ingestion: {e}")
        print("Install with: pip install langchain-community unstructured python-docx")
        return False
    
    # Collect documents
    loaders = []
    supported_extensions = {
        "*.pdf": PyPDFLoader,
        "*.docx": Docx2txtLoader, 
        "*.xlsx": UnstructuredExcelLoader,
        "*.xls": UnstructuredExcelLoader
    }
    
    for pattern, loader_class in supported_extensions.items():
        for file_path in glob.glob(os.path.join(source_dir, pattern)):
            try:
                loaders.append(loader_class(file_path))
                print(f"Found: {file_path}")
            except Exception as e:
                print(f"Failed to load {file_path}: {e}")
    
    if not loaders:
        print(f"No supported documents found in {source_dir}")
        return False
    
    # Load and split documents
    docs = []
    for loader in loaders:
        try:
            docs.extend(loader.load())
        except Exception as e:
            print(f"Failed to process {loader}: {e}")
    
    if not docs:
        print("No documents successfully loaded")
        return False
    
    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    texts = splitter.split_documents(docs)
    print(f"Split into {len(texts)} chunks")
    
    # Create embeddings and vector store
    model_name = embed_model or "sentence-transformers/all-MiniLM-L6-v2"
    embed_func = HuggingFaceEmbeddings(model_name=model_name)
    
    # Create persist directory
    os.makedirs(persist_dir, exist_ok=True)
    
    # Build vector store
    db = Chroma.from_documents(
        texts, 
        embed_func, 
        persist_directory=persist_dir
    )
    
    print(f"✅ Ingested {len(texts)} chunks into {persist_dir}")
    print(f"Vector store ready for deployment")
    
    return True

def list_documents(source_dir: str) -> List[str]:
    """List supported documents in source directory"""
    patterns = ["*.pdf", "*.docx", "*.xlsx", "*.xls"]
    files = []
    
    for pattern in patterns:
        files.extend(glob.glob(os.path.join(source_dir, pattern)))
    
    return sorted(files)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into vector store")
    parser.add_argument("--source", type=str, required=True, 
                       help="Directory containing documents")
    parser.add_argument("--out", type=str, required=True,
                       help="Output directory for vector store") 
    parser.add_argument("--model", type=str, default=None,
                       help="Embedding model name")
    parser.add_argument("--list", action="store_true",
                       help="List documents without ingesting")
    
    args = parser.parse_args()
    
    if args.list:
        files = list_documents(args.source)
        print(f"Found {len(files)} documents:")
        for f in files:
            print(f"  {f}")
    else:
        success = ingest_docs(args.source, args.out, args.model)
        if success:
            print("\n🎯 Next steps:")
            print(f"1. Set VECTORSTORE_DIR={args.out}")
            print("2. Deploy with vector store available")
            print("3. Test document queries")
        else:
            print("❌ Ingestion failed")
            exit(1)
