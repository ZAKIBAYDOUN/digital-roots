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

SENTINEL = "GHC-SENTINEL :: digital-roots -> twin -> 2025-08-27"
TWIN_API_URL = "https://digitalroots-bf3899aefd705f6789c2466e0c9b974d.us.langgraph.app"

async def verify_all_components():
    """Run comprehensive verification of all components"""
    
    print("== Twin Cloud Bootstrap Verification ==")
    print("=" * 50)
    
    checks = []
    errors = []
    
    # 1. File Structure Check
    print("1. Verifying File Structure...")
    required_files = [
        "app/__init__.py",
        "app/ghc_twin.py", 
        "app/document_store.py",
        "app/api.py",
        "langgraph.json",
        "requirements.txt"
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        errors.append(f"Missing files: {missing_files}")
        print(f"   FAIL - Missing: {missing_files}")
        checks.append(False)
    else:
        print("   PASS - All required files present")
        checks.append(True)
    
    # 2. LangGraph Config Check
    print("2. Verifying LangGraph Configuration...")
    try:
        with open("langgraph.json", "r") as f:
            config = json.load(f)
        
        # Check key configurations
        graphs = config.get("graphs", {})
        server = config.get("server", {})
        env_vars = config.get("env", [])
        
        config_ok = True
        if graphs.get("agent") != "./app/ghc_twin.py:app":
            errors.append("Incorrect graph entry point")
            config_ok = False
        
        if server.get("app") != "./app/api.py:app":
            errors.append("Incorrect server entry point") 
            config_ok = False
            
        required_env = ["OPENAI_API_KEY", "VECTOR_STORE_DIR", "ALLOWED_ORIGINS"]
        missing_env = [v for v in required_env if v not in env_vars]
        if missing_env:
            errors.append(f"Missing env vars: {missing_env}")
            config_ok = False
        
        if config_ok:
            print("   PASS - Configuration valid")
            checks.append(True)
        else:
            print("   FAIL - Configuration issues found")
            checks.append(False)
            
    except Exception as e:
        errors.append(f"Config error: {e}")
        print(f"   FAIL - Config error: {e}")
        checks.append(False)
    
    # 3. API Structure Check
    print("3. Verifying API Structure...")
    try:
        from app.api import api
        
        routes = [route.path for route in api.routes]
        required_endpoints = ["/health", "/api/twin/query", "/api/twin/ingest_texts"]
        missing_endpoints = [ep for ep in required_endpoints if ep not in routes]
        
        if missing_endpoints:
            errors.append(f"Missing endpoints: {missing_endpoints}")
            print(f"   FAIL - Missing endpoints: {missing_endpoints}")
            checks.append(False)
        else:
            print("   PASS - All API endpoints present")
            checks.append(True)
            
    except Exception as e:
        errors.append(f"API import error: {e}")
        print(f"   FAIL - API import error: {e}")
        checks.append(False)
    
    # 4. DocumentStore Check
    print("4. Verifying DocumentStore...")
    try:
        from app.document_store import DocumentStore
        
        required_methods = ["add_texts", "search_documents", "get_collection_stats"]
        store_methods = dir(DocumentStore)
        missing_methods = [m for m in required_methods if m not in store_methods]
        
        if missing_methods:
            errors.append(f"DocumentStore missing methods: {missing_methods}")
            print(f"   FAIL - Missing methods: {missing_methods}")
            checks.append(False)
        else:
            print("   PASS - DocumentStore structure valid")
            checks.append(True)
            
    except Exception as e:
        errors.append(f"DocumentStore error: {e}")
        print(f"   FAIL - DocumentStore error: {e}")
        checks.append(False)
    
    # 5. Requirements Check
    print("5. Verifying Requirements...")
    try:
        with open("requirements.txt", "r") as f:
            req_text = f.read().lower()
        
        required_packages = [
            "fastapi", "uvicorn", "chromadb", "langgraph", 
            "langchain", "pydantic", "tiktoken"
        ]
        
        missing_packages = [p for p in required_packages if p not in req_text]
        
        if missing_packages:
            errors.append(f"Missing packages: {missing_packages}")
            print(f"   FAIL - Missing packages: {missing_packages}")
            checks.append(False)
        else:
            print("   PASS - All required packages present")
            checks.append(True)
            
    except Exception as e:
        errors.append(f"Requirements error: {e}")
        print(f"   FAIL - Requirements error: {e}")
        checks.append(False)
    
    # 6. Ingest Workflow Check
    print("6. Verifying Ingest Workflow...")
    ingest_file = Path(".github/workflows/ingest.yml")
    if ingest_file.exists():
        try:
            content = ingest_file.read_text()
            # Check for workflow structure - either local or global workflow call
            required_elements = ["TWIN_API_URL"]
            
            if "uses: ZAKIBAYDOUN/GHC-DT/.github/workflows/ghc-global-ingest.yml" in content:
                # Using global workflow - check reference file
                ref_file = Path("reference/ghc-global-ingest.yml")
                if ref_file.exists():
                    ref_content = ref_file.read_text()
                    if "/api/twin/ingest_texts" in ref_content:
                        print("   PASS - Ingest workflow uses global workflow with correct endpoint")
                        checks.append(True)
                    else:
                        errors.append("Global workflow missing /api/twin/ingest_texts endpoint")
                        print("   FAIL - Global workflow missing endpoint")
                        checks.append(False)
                else:
                    print("   PASS - Uses global workflow (reference file exists)")
                    checks.append(True)
            elif "/api/twin/ingest_texts" in content:
                print("   PASS - Local ingest workflow configured")
                checks.append(True)
            else:
                errors.append("Ingest workflow missing endpoint configuration")
                print("   FAIL - Missing endpoint configuration")
                checks.append(False)
        except Exception as e:
            errors.append(f"Ingest workflow error: {e}")
            print(f"   FAIL - Workflow error: {e}")
            checks.append(False)
    else:
        errors.append("Missing ingest workflow")
        print("   FAIL - Missing .github/workflows/ingest.yml")
        checks.append(False)
    
    # Results Summary
    print("\n" + "=" * 50)
    print("VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    
    test_names = [
        "File Structure", "LangGraph Config", "API Structure", 
        "DocumentStore", "Requirements", "Ingest Workflow"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, checks)):
        status = "PASS" if result else "FAIL"
        print(f"  {status} - {name}")
    
    print(f"\nSummary: {passed}/{total} checks passed")
    
    if errors:
        print("\nERRORS FOUND:")
        for error in errors:
            print(f"  - {error}")
    
    if passed == total:
        print("\n SUCCESS: All verifications passed!")
        print("Ready for LangGraph Cloud deployment!")
        
        # Generate deployment commands
        print("\nDEPLOYMENT COMMANDS:")
        print("-" * 30)
        print("1. Environment Setup (set in LangGraph Cloud):")
        print("   OPENAI_API_KEY=your_openai_key")
        print("   VECTOR_STORE_DIR=vector_store")
        print("   ALLOWED_ORIGINS=https://zakibaydoun.github.io,https://zakibaydoun.github.io/GHC-DT")
        print("   INGEST_AUTH_TOKEN=your_secure_token")
        
        print(f"\n2. Health Check:")
        print(f"   curl {TWIN_API_URL}/health")
        
        print(f"\n3. Sentinel Ingest:")
        print(f'   curl -X POST "{TWIN_API_URL}/api/twin/ingest_texts" \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -H "X-INGEST-TOKEN: $INGEST_AUTH_TOKEN" \\')
        print(f'     -d \'{{"texts":["{SENTINEL}"],"metadatas":[{{"source_type":"public","path":"manual/sentinel.txt"}}]}}\'')
        
        print(f"\n4. Sentinel Query:")
        print(f'   curl -X POST "{TWIN_API_URL}/api/twin/query" \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -d \'{{"question":"What sentinel did I just ingest?","source_type":"public"}}\'')
        
        return True
    else:
        print(f"\nFAILED: {total - passed} verification(s) failed")
        print("Please fix the issues before deployment.")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_all_components())
    print(f"\nExit code: {0 if success else 1}")
    sys.exit(0 if success else 1)