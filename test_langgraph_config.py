#!/usr/bin/env python3
"""
Test script to validate LangGraph configuration
"""
import json
import os
from pathlib import Path

def test_langgraph_config():
    """Test the langgraph.json configuration file"""
    config_path = Path("langgraph.json")
    
    if not config_path.exists():
        print("❌ langgraph.json not found!")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print("✅ langgraph.json loaded successfully")
        print(f"📦 Project: {config.get('project_name', 'Unknown')}")
        print(f"🔗 API URL: {config.get('api_url', 'Not configured')}")
        print(f"👥 Agents: {len(config.get('agents', {}))}")
        
        # Test agent configuration
        agents = config.get('agents', {})
        for agent_id, agent_config in agents.items():
            name = agent_config.get('name', 'Unknown')
            icon = agent_config.get('icon', '❓')
            print(f"   {icon} {name} ({agent_id})")
        
        # Test environment variables
        required_vars = config.get('environment', {}).get('required_env_vars', [])
        print(f"\n🔧 Required Environment Variables:")
        for var in required_vars:
            status = "✅" if os.getenv(var) else "❌"
            print(f"   {status} {var}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in langgraph.json: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading langgraph.json: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LangGraph Configuration")
    print("=" * 40)
    test_langgraph_config()