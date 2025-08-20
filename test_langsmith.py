#!/usr/bin/env python3
"""
Test LangSmith connection for Digital Roots
"""
import os
import requests
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_langsmith():
    api_key = os.getenv("LANGSMITH_API_KEY")
    api_url = os.getenv("LANGGRAPH_API_URL")
    
    print("🔍 Testing LangSmith Connection")
    print(f"API Key: {api_key[:20]}..." if api_key else "❌ No API Key")
    print(f"API URL: {api_url}")
    
    if not api_key:
        print("❌ LANGSMITH_API_KEY not found!")
        return False
    
    if not api_url:
        print("❌ LANGGRAPH_API_URL not found!")
        return False
    
    # Test connection
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        # Test health endpoint
        response = requests.get(f"{api_url}/health", headers=headers, timeout=10)
        print(f"Health check: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ LangSmith connection WORKING!")
            return True
        elif response.status_code == 403:
            print("❌ 403 Forbidden - Check API key permissions")
        elif response.status_code == 404:
            print("❌ 404 Not Found - Check deployment URL")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
    
    return False

if __name__ == "__main__":
    test_langsmith()
