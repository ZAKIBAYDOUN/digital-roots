#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cloud Twin Bootstrap Verification Script
Tests all DoD requirements for LangGraph Cloud deployment
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any

# Set test environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "test-key-for-structure-validation")
os.environ["VECTOR_STORE_DIR"] = "vector_store"
os.environ["ALLOWED_ORIGINS"] = "https://zakibaydoun.github.io,https://zakibaydoun.github.io/GHC-DT"
os.environ["INGEST_AUTH_TOKEN"] = "test-token"

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

SENTINEL = "GHC-SENTINEL :: digital-roots ? twin ? 2025-08-27"
TWIN_API_URL = "https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app"

class TwinBootstrapValidator:
    """Validates LangGraph Cloud deployment readiness"""
    
    def __init__(self):
        self.results = {}
        self.errors = []
    
    def verify_file_structure(self) -> bool:
        """Verify all required files exist"""
        print("?? Verifying File Structure...")
        
        required_files = {
            "app/__init__.py": "App package initialization",
            "app/ghc_twin.py": "LangGraph StateGraph entry point", 
            "app/document_store.py": "DocumentStore with add_texts method",
            "app/api.py": "FastAPI server with required endpoints",
            "langgraph.json": "LangGraph Cloud configuration",
            "requirements.txt": "Python dependencies"
        }
        
        missing = []
        for file_path, description in required_files.items():
            if not Path(file_path).exists():
                missing.append(f"{file_path} ({description})")
        
        if missing:
            self.errors.extend([f"Missing file: {f}" for f in missing])
            print(f"? Missing files: {missing}")
            return False
        
        print("? All required files present")
        return True
    
    def verify_langgraph_config(self) -> bool:
        """Verify langgraph.json configuration"""
        print("?? Verifying LangGraph Configuration...")
        
        try:
            with open("langgraph.json", "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Check entry points
            graphs = config.get("graphs", {})
            server = config.get("server", {})
            
            expected_graph = "./app/ghc_twin.py:app"
            expected_server = "./app/api.py:app"
            
            issues = []
            
            if graphs.get("agent") != expected_graph:
                issues.append(f"Graph entry should be {expected_graph}, got {graphs.get('agent')}")
            
            if server.get("app") != expected_server:
                issues.append(f"Server app should be {expected_server}, got {server.get('app')}")
            
            # Check environment variables
            env_vars = config.get("env", [])
            required_env = ["OPENAI_API_KEY", "VECTOR_STORE_DIR", "ALLOWED_ORIGINS"]
            missing_env = [var for var in required_env if var not in env_vars]
            
            if missing_env:
                issues.append(f"Missing env vars: {missing_env}")
            
            if issues:
                self.errors.extend(issues)
                print(f"? Configuration issues: {issues}")
                return False
            
            print("? LangGraph configuration valid")
            return True
            
        except Exception as e:
            error = f"Failed to validate langgraph.json: {e}"
            self.errors.append(error)
            print(f"? {error}")
            return False
    
    def verify_api_structure(self) -> bool:
        """Verify API endpoints are properly defined"""
        print("?? Verifying API Structure...")
        
        try:
            # Import and check API
            from app.api import api
            
            routes = [route.path for route in api.routes]
            
            required_endpoints = [
                "/health",
                "/api/twin/query", 
                "/api/twin/ingest_texts"
            ]
            
            missing_endpoints = [ep for ep in required_endpoints if ep not in routes]
            
            if missing_endpoints:
                error = f"Missing API endpoints: {missing_endpoints}"
                self.errors.append(error)
                print(f"? {error}")
                return False
            
            print("? All required API endpoints present")
            return True
            
        except Exception as e:
            error = f"Failed to verify API structure: {e}"
            self.errors.append(error)
            print(f"? {error}")
            return False
    
    async def verify_langgraph_app(self) -> bool:
        """Verify LangGraph app can be imported and invoked"""
        print("?? Verifying LangGraph App...")
        
        try:
            from app.ghc_twin import app
            
            # Test basic invocation structure (without real API calls)
            test_state = {
                "question": "Test question",
                "source_type": "public",
                "context": [],
                "answer": "",
                "final_answer": ""
            }
            
            # Just verify the app structure without actual execution
            # (since we don't have real API keys in CI)
            assert hasattr(app, 'invoke'), "App missing invoke method"
            assert hasattr(app, 'ainvoke'), "App missing ainvoke method"
            
            print("? LangGraph app structure valid")
            return True
            
        except Exception as e:
            error = f"Failed to verify LangGraph app: {e}"
            self.errors.append(error)
            print(f"? {error}")
            return False
    
    def verify_document_store(self) -> bool:
        """Verify DocumentStore has required methods"""
        print("?? Verifying DocumentStore...")
        
        try:
            from app.document_store import DocumentStore
            
            # Verify class and methods exist
            store_methods = dir(DocumentStore)
            
            required_methods = ["add_texts", "search_documents", "get_collection_stats"]
            missing_methods = [m for m in required_methods if m not in store_methods]
            
            if missing_methods:
                error = f"DocumentStore missing methods: {missing_methods}"
                self.errors.append(error)
                print(f"? {error}")
                return False
            
            print("? DocumentStore structure valid")
            return True
            
        except Exception as e:
            error = f"Failed to verify DocumentStore: {e}"
            self.errors.append(error)
            print(f"? {error}")
            return False
    
    def verify_requirements(self) -> bool:
        """Verify requirements.txt has all needed packages"""
        print("?? Verifying Requirements...")
        
        try:
            with open("requirements.txt", "r") as f:
                requirements_text = f.read().lower()
            
            required_packages = [
                "fastapi", "uvicorn", "chromadb", "langgraph",
                "langchain", "langchain-openai", "langchain-community",
                "pydantic", "tiktoken", "python-dotenv"
            ]
            
            missing_packages = []
            for package in required_packages:
                if package not in requirements_text:
                    missing_packages.append(package)
            
            if missing_packages:
                error = f"Missing packages in requirements.txt: {missing_packages}"
                self.errors.append(error)
                print(f"? {error}")
                return False
            
            print("? All required packages present")
            return True
            
        except Exception as e:
            error = f"Failed to verify requirements: {e}"
            self.errors.append(error)
            print(f"? {error}")
            return False
    
    def verify_ingest_workflow(self) -> bool:
        """Verify ingest workflow exists"""
        print("?? Verifying Ingest Workflow...")
        
        ingest_file = Path(".github/workflows/ingest.yml")
        if not ingest_file.exists():
            error = "Missing .github/workflows/ingest.yml"
            self.errors.append(error)
            print(f"? {error}")
            return False
        
        try:
            content = ingest_file.read_text()
            
            # Check for key workflow elements
            required_elements = [
                "TWIN_API_URL",
                "/api/twin/ingest_texts",
                "X-INGEST-TOKEN"
            ]
            
            missing_elements = []
            for element in required_elements:
                if element not in content:
                    missing_elements.append(element)
            
            if missing_elements:
                error = f"Ingest workflow missing elements: {missing_elements}"
                self.errors.append(error)
                print(f"? {error}")
                return False
            
            print("? Ingest workflow properly configured")
            return True
            
        except Exception as e:
            error = f"Failed to verify ingest workflow: {e}"
            self.errors.append(error)
            print(f"? {error}")
            return False
    
    def generate_deployment_commands(self) -> Dict[str, str]:
        """Generate deployment commands and test payloads"""
        return {
            "health_check": f"curl {TWIN_API_URL}/health",
            "sentinel_ingest": f"""curl -X POST "{TWIN_API_URL}/api/twin/ingest_texts" \\
  -H "Content-Type: application/json" \\
  -H "X-INGEST-TOKEN: ${{INGEST_AUTH_TOKEN}}" \\
  -d '{{"texts":["{SENTINEL}"],"metadatas":[{{"source_type":"public","path":"manual/sentinel.txt"}}]}}'""",
            "sentinel_query": f"""curl -X POST "{TWIN_API_URL}/api/twin/query" \\
  -H "Content-Type: application/json" \\
  -d '{{"question":"What sentinel did I just ingest?","source_type":"public"}}'""",
            "env_setup": """# Set these environment variables in LangGraph Cloud:
OPENAI_API_KEY=your_openai_key
VECTOR_STORE_DIR=vector_store
ALLOWED_ORIGINS=https://zakibaydoun.github.io,https://zakibaydoun.github.io/GHC-DT
INGEST_AUTH_TOKEN=your_secure_token"""
        }
    
    async def run_all_verifications(self) -> bool:
        """Run all verification checks"""
        print("?? Twin Cloud Bootstrap Verification")
        print("=" * 60)
        
        checks = [
            ("File Structure", self.verify_file_structure),
            ("LangGraph Config", self.verify_langgraph_config),
            ("API Structure", self.verify_api_structure),
            ("Requirements", self.verify_requirements),
            ("DocumentStore", self.verify_document_store),
            ("LangGraph App", self.verify_langgraph_app),
            ("Ingest Workflow", self.verify_ingest_workflow)
        ]
        
        results = {}
        for name, check_func in checks:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            results[name] = result
        
        # Generate report
        print("\n" + "=" * 60)
        print("?? VERIFICATION RESULTS")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for name, result in results.items():
            status = "? PASS" if result else "? FAIL"
            print(f"  {status} {name}")
        
        print(f"\nSummary: {passed}/{total} checks passed")
        
        if self.errors:
            print("\n? ERRORS FOUND:")
            for error in self.errors:
                print(f"  • {error}")
        
        if passed == total:
            print(f"\n?? ALL VERIFICATIONS PASSED!")
            print("Ready for LangGraph Cloud deployment!")
            
            # Generate deployment info
            commands = self.generate_deployment_commands()
            print("\n?? DEPLOYMENT COMMANDS:")
            print("=" * 40)
            
            print("\n1. Environment Setup:")
            print(commands["env_setup"])
            
            print("\n2. Health Check:")
            print(commands["health_check"])
            
            print("\n3. Sentinel Ingest:")
            print(commands["sentinel_ingest"])
            
            print("\n4. Sentinel Query:")
            print(commands["sentinel_query"])
            
            return True
        else:
            print(f"\n?? {total - passed} verification(s) failed")
            print("Please fix the issues before deployment.")
            return False

async def main():
    validator = TwinBootstrapValidator()
    success = await validator.run_all_verifications()
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)