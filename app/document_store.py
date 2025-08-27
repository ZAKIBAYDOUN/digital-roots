"""Document Store with Chroma integration for GHC Digital Twin"""

import os
import logging
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class DocumentStore:
    """Canonical document storage and retrieval using ChromaDB"""
    
    def __init__(self):
        """Initialize the document store with ChromaDB"""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize vector store
        vector_store_dir = os.getenv("VECTOR_STORE_DIR", "vector_store")
        self.vector_store = Chroma(
            persist_directory=vector_store_dir,
            embedding_function=self.embeddings,
            collection_name="ghc_digital_twin"
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        logger.info(f"DocumentStore initialized with vector store at {vector_store_dir}")
    
    def add_texts(
        self, 
        texts: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        source_type: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Canonical method for ingesting texts into the vector store
        
        Args:
            texts: List of text strings to ingest
            metadatas: Optional list of metadata dicts for each text
            source_type: Type of source (e.g., "public", "private", "docs")
            
        Returns:
            Dict with status and ingestion count
        """
        if not texts:
            logger.warning("No texts provided for ingestion")
            return {"status": "error", "message": "No texts provided", "ingested_count": 0}
        
        documents = []
        
        try:
            for i, text in enumerate(texts):
                if not text or not text.strip():
                    continue
                
                # Get metadata for this text
                metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
                metadata.update({
                    "source_type": source_type,
                    "text_index": i
                })
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                
                for j, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                        
                    # Add chunk metadata
                    chunk_metadata = {
                        **metadata,
                        "chunk_index": j,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk)
                    }
                    
                    documents.append(Document(
                        page_content=chunk, 
                        metadata=chunk_metadata
                    ))
            
            if documents:
                # Add documents to vector store
                self.vector_store.add_documents(documents)
                self.vector_store.persist()
                
                logger.info(f"Successfully ingested {len(documents)} document chunks")
                
                return {
                    "status": "success",
                    "ingested_count": len(documents),
                    "message": f"Ingested {len(documents)} chunks from {len(texts)} texts"
                }
            else:
                logger.warning("No valid document chunks created from provided texts")
                return {
                    "status": "warning", 
                    "message": "No valid chunks created",
                    "ingested_count": 0
                }
                
        except Exception as e:
            logger.error(f"Error during text ingestion: {str(e)}")
            return {
                "status": "error",
                "message": f"Ingestion failed: {str(e)}",
                "ingested_count": 0
            }
    
    def search_documents(
        self, 
        query: str, 
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Search for relevant documents in the vector store
        
        Args:
            query: Search query string
            k: Number of documents to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of relevant documents
        """
        try:
            if filter_dict:
                docs = self.vector_store.similarity_search(
                    query, 
                    k=k, 
                    filter=filter_dict
                )
            else:
                docs = self.vector_store.similarity_search(query, k=k)
                
            logger.debug(f"Found {len(docs)} relevant documents for query: {query[:100]}...")
            return docs
            
        except Exception as e:
            logger.error(f"Error during document search: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the document collection"""
        try:
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "document_count": count,
                "collection_name": collection.name,
                "status": "healthy" if count > 0 else "empty"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {
                "document_count": 0,
                "collection_name": "unknown",
                "status": "error",
                "error": str(e)
            }
    
    def clear_collection(self) -> Dict[str, Any]:
        """Clear all documents from the collection (use with caution)"""
        try:
            collection = self.vector_store._collection
            collection.delete()
            logger.warning("Document collection cleared")
            
            return {
                "status": "success",
                "message": "Collection cleared successfully"
            }
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to clear collection: {str(e)}"
            }