#!/usr/bin/env python3
"""
Test script for LangGraph Cloud deployment validation
Tests all DoD requirements including sentinel phrase retrieval
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add app to path for testing
sys.path.insert(0, str(Path(__file__).parent))

async def test_langgraph_app():
    """Test the LangGraph app directly"""
    print("?? Testing LangGraph App...")
    
    try:
        from app.ghc_twin import app
        
        # Test basic functionality
        test_state = {
            "question": "What is Digital Roots?",
            "source_type": "public",
            "context": [],
            "answer": "",
            "final_answer": ""
        }
        
        result = await app.ainvoke(test_state)
        
        assert "final_answer" in result, "Missing final_answer in response"
        assert result["final_answer"], "Empty final_answer"
        
        print("? LangGraph app test passed")
        return True
        
    except Exception as e:
        print(f"? LangGraph app test failed: {e}")
        return False

async def test_sentinel_retrieval():
    """Test sentinel phrase retrieval for end-to-end validation"""
    print("?? Testing Sentinel Phrase Retrieval...")
    
    try:
        from app.ghc_twin import app
        
        sentinel = "GHC-SENTINEL :: digital-roots ? twin ? 2025-08-27"
        
        # Test sentinel retrieval
        test_state = {
            "question": "What is the GHC sentinel phrase for digital-roots?",
            "source_type": "system",
            "context": [],
            "answer": "",
            "final_answer": ""
        }
        
        result = await app.ainvoke(test_state)
        final_answer = result.get("final_answer", "")
        
        contains_sentinel = sentinel in final_answer
        
        print(f"Final Answer: {final_answer[:200]}...")
        print(f"Contains Sentinel: {contains_sentinel}")
        
        if contains_sentinel:
            print("? Sentinel retrieval test passed")
            return True
        else:
            print("? Sentinel phrase not found in response")
            return False
            
    except Exception as e:
        print(f"? Sentinel retrieval test failed: {e}")
        return False

def test_document_store():
    """Test DocumentStore functionality"""
    print("?? Testing DocumentStore...")
    
    try:
        from app.document_store import DocumentStore
        
        store = DocumentStore()
        
        # Test adding documents
        result = store.add_texts(
            texts=["Test document for validation"],
            metadatas=[{"test": True, "source": "test"}],
            source_type="test"
        )
        
        assert result["status"] == "success", f"Failed to add texts: {result}"
        assert result["ingested_count"] > 0, "No documents were ingested"
        
        # Test searching
        docs = store.search_documents("Test document", k=1)
        assert len(docs) > 0, "Search returned no documents"
        
        # Test stats
        stats = store.get_collection_stats()
        assert stats["document_count"] > 0, "Collection appears empty"
        
        print("? DocumentStore test passed")
        return True
        
    except Exception as e:
        print(f"? DocumentStore test failed: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("?? Testing File Structure...")
    
    required_files = [
        "app/__init__.py",
        "app/ghc_twin.py", 
        "app/document_store.py",
        "app/api.py",
        "requirements.txt",
        "langgraph.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"? Missing files: {missing_files}")
        return False
    
    print("? File structure test passed")
    return True

def test_langgraph_config():
    """Test langgraph.json configuration"""
    print("?? Testing LangGraph Configuration...")
    
    try:
        with open("langgraph.json", "r") as f:
            config = json.load(f)
        
        # Check required fields
        assert "graphs" in config, "Missing graphs config"
        assert "server" in config, "Missing server config"
        assert "env" in config, "Missing env config"
        
        # Check graph entry point
        graphs = config["graphs"]
        assert "agent" in graphs, "Missing agent graph"
        assert graphs["agent"] == "./app/ghc_twin.py:app", "Incorrect agent path"
        
        # Check server entry point
        server = config["server"]
        assert "app" in server, "Missing server app"
        assert server["app"] == "./app/api.py:app", "Incorrect server app path"
        
        # Check environment variables
        env_vars = config["env"]
        required_env = ["OPENAI_API_KEY", "VECTOR_STORE_DIR", "ALLOWED_ORIGINS"]
        for var in required_env:
            assert var in env_vars, f"Missing env var: {var}"
        
        print("? LangGraph config test passed")
        return True
        
    except Exception as e:
        print(f"? LangGraph config test failed: {e}")
        return False

def test_requirements():
    """Test requirements.txt has all needed packages"""
    print("?? Testing Requirements...")
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read().lower()
        
        required_packages = [
            "fastapi", "uvicorn", "chromadb", "langgraph", 
            "langchain", "pydantic", "tiktoken", "streamlit", 
            "python-dotenv"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"? Missing packages: {missing_packages}")
            return False
        
        print("? Requirements test passed")
        return True
        
    except Exception as e:
        print(f"? Requirements test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("?? Digital Roots LangGraph Cloud Deployment Tests")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Requirements", test_requirements), 
        ("LangGraph Config", test_langgraph_config),
        ("DocumentStore", test_document_store),
        ("LangGraph App", test_langgraph_app),
        ("Sentinel Retrieval", test_sentinel_retrieval),
    ]
    
    results = []
    for name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("?? Test Results:")
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "? PASS" if result else "? FAIL"
        print(f"  {status} {name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n?? All tests passed! Ready for deployment.")
        return True
    else:
        print(f"\n?? {failed} test(s) failed. Please fix before deployment.")
        return False

if __name__ == "__main__":
    # Set environment variables for testing
    os.environ.setdefault("OPENAI_API_KEY", "test-key")
    os.environ.setdefault("VECTOR_STORE_DIR", "test_vector_store")
    os.environ.setdefault("ALLOWED_ORIGINS", "https://zakibaydoun.github.io,https://zakibaydoun.github.io/GHC-DT")
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)