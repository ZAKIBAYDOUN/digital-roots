import os
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .document_store import DocumentStore

class TwinState(TypedDict):
    """State for the digital twin graph"""
    question: str
    source_type: Optional[str]
    context: List[str]
    answer: str
    final_answer: str

class DigitalTwin:
    """GHC Digital Twin with RAG capabilities"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize document store
        self.document_store = DocumentStore()
        
        # Add sentinel document for testing
        self._ensure_sentinel_document()
    
    def _ensure_sentinel_document(self):
        """Ensure sentinel document exists for testing"""
        sentinel = "GHC-SENTINEL :: digital-roots ? twin ? 2025-08-27"
        sentinel_text = f"""
        Digital Roots Sentinel Document
        
        This document contains the sentinel phrase: {sentinel}
        
        Digital Roots is a cannabis cultivation management platform with AI agents that provides:
        - CEO Digital Twin orchestration
        - 9 specialized AI agents (strategy, finance, operations, market, compliance, code, innovation, risk)
        - Multi-language support (EN, ES, IS, FR)
        - RAG-enabled document retrieval
        - Automated content ingestion
        
        This sentinel document confirms end-to-end retrieval functionality.
        """
        
        # Add sentinel document
        self.document_store.add_texts(
            texts=[sentinel_text],
            metadatas=[{"source": "sentinel", "type": "test", "sentinel": sentinel}],
            source_type="system"
        )
    
    def search_knowledge_base(self, state: TwinState) -> Dict[str, Any]:
        """Search the vector store for relevant context"""
        question = state["question"]
        source_type = state.get("source_type", "public")
        
        # Search for relevant documents
        filter_dict = {"source_type": source_type} if source_type != "public" else None
        docs = self.document_store.search_documents(question, k=5, filter_dict=filter_dict)
        context = [doc.page_content for doc in docs]
        
        return {"context": context}
    
    def generate_answer(self, state: TwinState) -> Dict[str, Any]:
        """Generate answer based on context"""
        question = state["question"]
        context = state.get("context", [])
        
        # Prepare the context
        if context:
            context_str = "\n\n".join(context)
        else:
            context_str = "No specific context available in the knowledge base."
        
        # Generate answer with system prompt
        system_prompt = """You are the CEO Digital Twin for Green Hill Canarias (GHC) and Digital Roots platform.

You are an AI-powered executive assistant that helps manage cannabis cultivation operations through:
- Strategic planning and business analysis
- Financial oversight and budgeting  
- Operational planning and logistics
- Market analysis and competitive intelligence
- Regulatory compliance guidance
- Risk assessment and mitigation
- Innovation and R&D insights
- Technical engineering support

Answer questions based on the provided context from our knowledge base. If you find relevant information, use it to provide detailed, actionable responses. If the context doesn't contain sufficient information, clearly state this and provide general guidance based on your training.

Always maintain a professional, executive-level tone focused on practical business outcomes."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Knowledge Base Context:\n{context_str}\n\nQuestion: {question}")
        ]
        
        response = self.llm.invoke(messages)
        answer = response.content
        
        return {"answer": answer, "final_answer": answer}

# Create the state graph
def create_app():
    """Create and return the LangGraph application"""
    twin = DigitalTwin()
    
    # Define the graph
    workflow = StateGraph(TwinState)
    
    # Add nodes
    workflow.add_node("search", twin.search_knowledge_base)
    workflow.add_node("generate", twin.generate_answer)
    
    # Add edges
    workflow.add_edge("search", "generate")
    workflow.add_edge("generate", END)
    
    # Set entry point
    workflow.set_entry_point("search")
    
    # Compile the graph
    app = workflow.compile()
    
    # Add the twin and document store instances to the app for API access
    app.twin = twin
    app.document_store = twin.document_store
    
    return app

# Create the app instance
app = create_app()